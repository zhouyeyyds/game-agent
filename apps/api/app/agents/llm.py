import json
from typing import Any

from openai import OpenAI

from app.core.config import get_settings


class LLMConfigurationError(RuntimeError):
    pass


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


def generate_json(system_prompt: str, user_prompt: str) -> dict[str, Any]:
    settings = get_settings()
    if settings.llm_provider == "mock":
        raise LLMConfigurationError("mock provider does not call a remote LLM")
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
    response = client.chat.completions.create(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    content = response.choices[0].message.content or "{}"
    return _extract_json_object(content)

