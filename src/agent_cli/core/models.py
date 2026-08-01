from dataclasses import dataclass, field

from agent_cli.core.messages import Message


class ResponseTruncatedError(RuntimeError):
    """Raised when a provider stops at the configured output-token limit."""

    def __init__(self, provider: str, max_tokens: int) -> None:
        super().__init__(
            f"{provider} response reached the configured {max_tokens}-token output limit."
        )


@dataclass(frozen=True, slots=True)
class CompletionRequest:
    messages: tuple[Message, ...]
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CompletionResponse:
    text: str
    model: str | None = None
    usage: dict[str, int] = field(default_factory=dict)
