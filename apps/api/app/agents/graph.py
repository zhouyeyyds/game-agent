from collections.abc import Callable
from typing import Any

from langgraph.graph import END, StateGraph
from sqlalchemy.orm import Session

from app.agents import nodes
from app.agents.state import GenerationState
from app.core.config import get_settings
from app.models import GenerationTask

NodeFn = Callable[[Session, GenerationTask, GenerationState], GenerationState]


def _bind(
    db: Session,
    task: GenerationTask,
    node: NodeFn,
) -> Callable[[GenerationState], dict[str, Any]]:
    def wrapped(state: GenerationState) -> dict[str, Any]:
        return dict(node(db, task, state))

    return wrapped


def _route_after_review(state: GenerationState) -> str:
    if not state.get("validation_errors"):
        return "render"
    if state.get("repair_attempts", 0) < get_settings().agent_max_repair_attempts:
        return "repair"
    return "failed"


def _fail_invalid_spec(state: GenerationState) -> GenerationState:
    errors = state.get("validation_errors", [])
    message = "GameSpec validation failed after repair attempts"
    if errors:
        message = f"{message}: {errors[-1]}"
    raise RuntimeError(message)


def build_generation_graph(db: Session, task: GenerationTask):
    graph = StateGraph(GenerationState)
    graph.add_node("idea_analyzer", _bind(db, task, nodes.idea_analyzer))
    graph.add_node("asset_interpreter", _bind(db, task, nodes.asset_interpreter))
    graph.add_node("game_designer", _bind(db, task, nodes.game_designer))
    graph.add_node("spec_writer", _bind(db, task, nodes.spec_writer))
    graph.add_node("spec_reviewer", _bind(db, task, nodes.spec_reviewer))
    graph.add_node("repair_spec", _bind(db, task, nodes.repair_spec))
    graph.add_node("render", _bind(db, task, nodes.render_node))
    graph.add_node("upload", _bind(db, task, nodes.upload_node))
    graph.add_node("finalizer", _bind(db, task, nodes.finalizer))
    graph.add_node("failed", _fail_invalid_spec)

    graph.set_entry_point("idea_analyzer")
    graph.add_edge("idea_analyzer", "asset_interpreter")
    graph.add_edge("asset_interpreter", "game_designer")
    graph.add_edge("game_designer", "spec_writer")
    graph.add_edge("spec_writer", "spec_reviewer")
    graph.add_conditional_edges(
        "spec_reviewer",
        _route_after_review,
        {"render": "render", "repair": "repair_spec", "failed": "failed"},
    )
    graph.add_edge("repair_spec", "spec_reviewer")
    graph.add_edge("render", "upload")
    graph.add_edge("upload", "finalizer")
    graph.add_edge("finalizer", END)
    return graph.compile()
