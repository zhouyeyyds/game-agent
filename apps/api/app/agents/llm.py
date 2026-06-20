import json
from dataclasses import dataclass
from time import perf_counter
from typing import Any

from openai import APITimeoutError, OpenAI

from app.core.config import get_settings


class LLMConfigurationError(RuntimeError):
    pass


class LLMRequestError(RuntimeError):
    pass


@dataclass(frozen=True)
class LLMUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass(frozen=True)
class LLMJsonResult:
    data: dict[str, Any]
    model: str
    usage: LLMUsage
    elapsed_ms: int


def _read_usage(response: Any) -> LLMUsage:
    usage = getattr(response, "usage", None)
    if usage is None:
        return LLMUsage()
    prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
    completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
    total_tokens = int(getattr(usage, "total_tokens", 0) or prompt_tokens + completion_tokens)
    return LLMUsage(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
    )


def _extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.removeprefix("```json").removeprefix("```").strip()
        stripped = stripped.removesuffix("```").strip()
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start < 0 or end < start:
            raise
        value = json.loads(stripped[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("LLM response must be a JSON object")
    return value


def generate_json(system_prompt: str, user_prompt: str) -> LLMJsonResult:
    settings = get_settings()
    if settings.llm_provider != "openai_compatible":
        raise LLMConfigurationError(f"Unsupported LLM provider: {settings.llm_provider}")
    if not settings.llm_api_key:
        raise LLMConfigurationError("LLM_API_KEY is required for openai_compatible provider")

    client = OpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        timeout=settings.llm_timeout_seconds,
        max_retries=settings.llm_max_retries,
    )
    started_at = perf_counter()
    try:
        response = client.chat.completions.create(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
    except APITimeoutError as exc:
        raise LLMRequestError(
            "LLM request timed out after "
            f"{settings.llm_timeout_seconds} seconds. Increase LLM_TIMEOUT_SECONDS, "
            "restart the backend, or use a faster model for code generation."
        ) from exc
    elapsed_ms = int((perf_counter() - started_at) * 1000)
    content = response.choices[0].message.content or "{}"
    return LLMJsonResult(
        data=_extract_json_object(content),
        model=settings.llm_model,
        usage=_read_usage(response),
        elapsed_ms=elapsed_ms,
    )
