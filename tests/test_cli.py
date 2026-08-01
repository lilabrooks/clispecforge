import pytest

from agent_cli.cli import main
from agent_cli.core.models import ResponseTruncatedError


class _TruncatedAgent:
    def run(self, prompt: str) -> None:
        del prompt
        raise ResponseTruncatedError("OpenAI", 2048)


def test_providers_command_writes_available_providers(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["providers"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "anthropic\necho\nopenai\n"
    assert captured.err == ""


def test_run_command_writes_agent_result(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["run", "hello"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "clispecforge: Echo provider received: hello\n"
    assert captured.err == ""


def test_run_command_can_attach_all_skills(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["run", "--spec", "example", "--all-skills", "build it"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "# Agent skill: CLI test coverage" in captured.out
    assert "# Agent skill: Focused implementation" in captured.out
    assert "# Agent skill: Goal-driven execution" in captured.out
    assert "# Agent skill: Python code quality" in captured.out
    assert "# Agent skill: Python packaging for CLIs" in captured.out
    assert "# Agent skill: Standard-library CLI UX" in captured.out
    assert "# Agent skill: Think before coding" in captured.out
    assert captured.err == ""


def test_run_command_rejects_all_skills_with_specific_skill(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as error:
        main(["run", "--all-skills", "--skill", "focused-implementation", "build it"])

    captured = capsys.readouterr()
    assert error.value.code == 2
    assert captured.out == ""
    assert "Error:" in captured.err
    assert "not allowed with argument" in captured.err
    assert "Try 'clispecforge run --help' for available options." in captured.err


def test_missing_command_explains_available_help(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main([])

    captured = capsys.readouterr()
    assert error.value.code == 2
    assert captured.out == ""
    assert "Error: the following arguments are required: command" in captured.err
    assert "Try 'clispecforge --help' for available options." in captured.err


def test_missing_spec_exits_with_clean_error(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main(["run", "--spec", "missing", "hello"])

    captured = capsys.readouterr()
    assert error.value.code == 1
    assert captured.out == ""
    assert captured.err == (
        "Error: Spec 'missing' was not found under specs/cli.\n"
        "Try 'clispecforge spec list' or 'clispecforge skill list' to see available files.\n"
    )


def test_unknown_provider_exits_with_clear_next_step(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main(["run", "--provider", "missing", "hello"])

    captured = capsys.readouterr()
    assert error.value.code == 1
    assert captured.out == ""
    assert captured.err == (
        "Error: Unknown provider 'missing'. Supported providers: anthropic, echo, openai.\n"
        "Try 'clispecforge providers' to see available providers.\n"
    )


def test_truncated_response_exits_with_clear_next_step(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr("agent_cli.cli.build_agent", lambda _settings: _TruncatedAgent())

    with pytest.raises(SystemExit) as error:
        main(["run", "hello"])

    captured = capsys.readouterr()
    assert error.value.code == 1
    assert captured.out == ""
    assert captured.err == (
        "Error: OpenAI response reached the configured 2048-token output limit.\n"
        "Increase CLISPECFORGE_MAX_TOKENS and try again.\n"
    )


def test_invalid_max_tokens_exits_without_provider_hint(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("CLISPECFORGE_MAX_TOKENS", "many")

    with pytest.raises(SystemExit) as error:
        main(["run", "hello"])

    captured = capsys.readouterr()
    assert error.value.code == 1
    assert captured.out == ""
    assert captured.err == "Error: CLISPECFORGE_MAX_TOKENS must be a positive integer.\n"
