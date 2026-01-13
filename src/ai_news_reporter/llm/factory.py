"""Factory for creating LLM instances."""

from ..core.exceptions import LLMError
from .base import BaseLLM
from .claude import ClaudeLLM
from .openai_llm import OpenAILLM


def create_llm(
    provider: str,
    api_key: str,
    model: str | None = None,
    max_tokens: int = 4096,
    temperature: float = 0.3,
) -> BaseLLM:
    """Create an LLM instance based on provider.

    Args:
        provider: LLM provider name (claude, openai).
        api_key: API key for the provider.
        model: Optional model override.
        max_tokens: Maximum tokens in response.
        temperature: Sampling temperature.

    Returns:
        LLM instance.

    Raises:
        LLMError: If provider is unknown.
    """
    provider = provider.lower()

    if provider == "claude":
        return ClaudeLLM(
            api_key=api_key,
            model=model or "claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            temperature=temperature,
        )
    elif provider == "openai":
        return OpenAILLM(
            api_key=api_key,
            model=model or "gpt-4.1-mini",
            max_tokens=max_tokens,
            temperature=temperature,
        )
    else:
        raise LLMError(f"Unknown LLM provider: {provider}. Supported: claude, openai")
