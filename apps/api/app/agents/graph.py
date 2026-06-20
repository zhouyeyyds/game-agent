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
        nodes.ensure_task_not_canceled(db, task)
        result = dict(node(db, task, state))
        nodes.ensure_task_not_canceled(db, task)
        return result

    return wrapped


def _route_after_scan(state: GenerationState) -> str:
    if not state.get("security_errors"):
        return "upload"
    if state.get("repair_attempts", 0) < get_settings().agent_max_repair_attempts:
        return "repair"
    return "failed"


def _fail_invalid_bundle(state: GenerationState) -> GenerationState:
    errors = state.get("security_errors", [])
    message = "Generated bundle failed validation after repair attempts"
    if errors:
        message = f"{message}: {errors[-1]}"
    raise RuntimeError(message)


def build_generation_graph(db: Session, task: GenerationTask):
    graph = StateGraph(GenerationState)
    graph.add_node("idea_analyzer", _bind(db, task, nodes.idea_analyzer))
    graph.add_node("asset_interpreter", _bind(db, task, nodes.asset_interpreter))
    graph.add_node("game_designer", _bind(db, task, nodes.game_designer))
    graph.add_node("code_generation_agent", _bind(db, task, nodes.code_generation_agent))
    graph.add_node("bundle_security_scan", _bind(db, task, nodes.bundle_security_scan))
    graph.add_node("repair_bundle", _bind(db, task, nodes.repair_bundle))
    graph.add_node("upload", _bind(db, task, nodes.upload_node))
    graph.add_node("finalizer", _bind(db, task, nodes.finalizer))
    graph.add_node("failed", _fail_invalid_bundle)

    graph.set_entry_point("idea_analyzer")
    graph.add_edge("idea_analyzer", "asset_interpreter")
    graph.add_edge("asset_interpreter", "game_designer")
    graph.add_edge("game_designer", "code_generation_agent")
    graph.add_edge("code_generation_agent", "bundle_security_scan")
    graph.add_conditional_edges(
        "bundle_security_scan",
        _route_after_scan,
        {"upload": "upload", "repair": "repair_bundle", "failed": "failed"},
    )
    graph.add_edge("repair_bundle", "bundle_security_scan")
    graph.add_edge("upload", "finalizer")
    graph.add_edge("finalizer", END)
    return graph.compile()
