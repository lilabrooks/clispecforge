import pytest

from agent_cli.config.settings import DEFAULT_MAX_TOKENS, ConfigurationError, Settings


def test_settings_allow_provider_override() -> None:
    settings = Settings.from_env(provider_override="echo")

    assert settings.provider == "echo"


def test_settings_reads_renamed_environment_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CLISPECFORGE_PROVIDER", "openai")
    monkeypatch.setenv("CLISPECFORGE_SYSTEM_PROMPT", "Be concise.")

    settings = Settings.from_env()

    assert settings.provider == "openai"
    assert settings.system_prompt == "Be concise."


def test_settings_model_defaults_to_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CLISPECFORGE_MODEL", raising=False)

    settings = Settings.from_env()

    assert settings.model is None


def test_settings_reads_model_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CLISPECFORGE_MODEL", "claude-sonnet-5")

    settings = Settings.from_env()

    assert settings.model == "claude-sonnet-5"


def test_settings_max_tokens_uses_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CLISPECFORGE_MAX_TOKENS", raising=False)

    settings = Settings.from_env()

    assert settings.max_tokens == DEFAULT_MAX_TOKENS


def test_settings_reads_max_tokens_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CLISPECFORGE_MAX_TOKENS", "8192")

    settings = Settings.from_env()

    assert settings.max_tokens == 8192


@pytest.mark.parametrize("value", ["0", "-1", "many"])
def test_settings_rejects_invalid_max_tokens(
    monkeypatch: pytest.MonkeyPatch,
    value: str,
) -> None:
    monkeypatch.setenv("CLISPECFORGE_MAX_TOKENS", value)

    with pytest.raises(ConfigurationError, match="must be a positive integer"):
        Settings.from_env()
