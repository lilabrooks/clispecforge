"""Single source of truth for provider adapters.

The factory, the unknown-provider error, and the `providers` command all read
from `_PROVIDERS`. Add a real vendor by importing its adapter and adding one
entry here.
"""

from collections.abc import Callable

from agent_cli.core.ports import LanguageModel
from agent_cli.providers.anthropic import AnthropicLanguageModel
from agent_cli.providers.echo import EchoLanguageModel
from agent_cli.providers.openai import OpenAILanguageModel


def _create_echo(model: str | None, max_tokens: int | None) -> LanguageModel:
    del model, max_tokens  # echo has no underlying model or output-token limit
    return EchoLanguageModel()


def _create_anthropic(model: str | None, max_tokens: int | None) -> LanguageModel:
    return AnthropicLanguageModel(model=model, max_tokens=max_tokens)


def _create_openai(model: str | None, max_tokens: int | None) -> LanguageModel:
    return OpenAILanguageModel(model=model, max_tokens=max_tokens)


_PROVIDERS: dict[str, Callable[[str | None, int | None], LanguageModel]] = {
    "echo": _create_echo,
    "anthropic": _create_anthropic,
    "openai": _create_openai,
}


def available_providers() -> list[str]:
    return sorted(_PROVIDERS)


def create_provider(
    name: str,
    *,
    model: str | None = None,
    max_tokens: int | None = None,
) -> LanguageModel:
    try:
        factory = _PROVIDERS[name]
    except KeyError:
        supported = ", ".join(available_providers())
        msg = f"Unknown provider {name!r}. Supported providers: {supported}."
        raise ValueError(msg) from None
    return factory(model, max_tokens)
