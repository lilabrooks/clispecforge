from dataclasses import dataclass
from os import environ

DEFAULT_PROVIDER = "echo"
DEFAULT_SYSTEM_PROMPT = "You are a concise, practical assistant."
DEFAULT_MAX_TOKENS = 4096


class ConfigurationError(ValueError):
    """Raised when an environment setting cannot be used."""


def _read_max_tokens() -> int:
    raw_value = environ.get("CLISPECFORGE_MAX_TOKENS")
    if raw_value is None:
        return DEFAULT_MAX_TOKENS

    try:
        max_tokens = int(raw_value)
    except ValueError:
        max_tokens = 0

    if max_tokens <= 0:
        msg = "CLISPECFORGE_MAX_TOKENS must be a positive integer."
        raise ConfigurationError(msg)
    return max_tokens


@dataclass(frozen=True, slots=True)
class Settings:
    provider: str = DEFAULT_PROVIDER
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    model: str | None = None
    max_tokens: int = DEFAULT_MAX_TOKENS

    @classmethod
    def from_env(cls, provider_override: str | None = None) -> "Settings":
        provider = provider_override or environ.get("CLISPECFORGE_PROVIDER", DEFAULT_PROVIDER)
        system_prompt = environ.get("CLISPECFORGE_SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT)
        model = environ.get("CLISPECFORGE_MODEL")
        return cls(
            provider=provider,
            system_prompt=system_prompt,
            model=model,
            max_tokens=_read_max_tokens(),
        )
