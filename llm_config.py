"""Configuration for an OpenAI-compatible LLM provider."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class LLMConfig:
    api_key: str
    base_url: str | None
    model: str
    temperature: float
    max_tokens: int


def load_llm_config() -> LLMConfig:
    load_dotenv()

    api_key = os.getenv("LLM_API_KEY", "").strip()
    model = os.getenv("LLM_MODEL", "").strip()
    base_url = os.getenv("LLM_BASE_URL", "").strip() or None

    if not api_key or api_key == "your_api_key_here":
        raise RuntimeError("LLM_API_KEY is not configured in the environment.")
    if not model or model == "your_model_name_here":
        raise RuntimeError("LLM_MODEL is not configured in the environment.")

    try:
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    except ValueError as exc:
        raise RuntimeError("LLM_TEMPERATURE must be a number.") from exc

    try:
        max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1000"))
    except ValueError as exc:
        raise RuntimeError("LLM_MAX_TOKENS must be an integer.") from exc

    if temperature < 0:
        raise RuntimeError("LLM_TEMPERATURE must be zero or greater.")
    if max_tokens <= 0:
        raise RuntimeError("LLM_MAX_TOKENS must be greater than zero.")

    return LLMConfig(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
