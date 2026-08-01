"""Offline ingestion: `clispecforge plan` and `clispecforge apply`.

These commands consume an existing provider-style response. No provider adapter
may be reached, so every test installs guards that fail loudly if one is.
"""

import io
from pathlib import Path
from typing import Never

import pytest

import agent_cli
from agent_cli.cli import main, response_digest

_RESPONSE = "\n".join(
    [
        "Here is the scaffold.",
        "",
        "FILE: hello.txt",
        "```",
        "hello world",
        "```",
        "",
        "FILE: src/pkg/__init__.py",
        "```python",
        '__version__ = "0.1.0"',
        "```",
        "",
        "Review before running it.",
    ]
)

_RESPONSE_WITH_NESTED_FENCE = "\n".join(
    [
        "FILE: README.md",
        "````markdown",
        "# Title",
        "",
        "```bash",
        "echo hi",
        "```",
        "",
        "This sentence after the inner fence must survive parsing.",
        "````",
    ]
)

_RESPONSE_WITH_DUPLICATE = "\n".join(
    [
        "FILE: same.txt",
        "```",
        "first",
        "```",
        "FILE: same.txt",
        "```",
        "second",
        "```",
    ]
)

_RESPONSE_WITH_UNSAFE_PATH = "\n".join(
    [
        "FILE: ../outside.txt",
        "```",
        "escaped",
        "```",
    ]
)

_RESPONSE_WITH_CONTROL_CHARACTERS = "\n".join(
    [
        "FILE: message.txt",
        "```",
        "hello\x1b[2Jworld",
        "```",
    ]
)

_RESPONSE_WITHOUT_FILE_BLOCKS = "I built nothing. Here is some prose instead."

_RESPONSE_WITH_UNCLOSED_FENCE = "\n".join(
    [
        "FILE: truncated.txt",
        "```",
        "the closing fence never arrives",
    ]
)


@pytest.fixture(autouse=True)
def forbid_provider_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fail the test if anything in this module reaches a provider adapter."""

    def refuse(*args: object, **kwargs: object) -> Never:
        del args, kwargs
        msg = "offline ingestion must not build an agent or contact a provider"
        raise AssertionError(msg)

    monkeypatch.setattr("agent_cli.cli.build_agent", refuse)
    monkeypatch.setattr("agent_cli.runtime.factory.build_agent", refuse)
    monkeypatch.setattr("agent_cli.runtime.factory.build_model", refuse)
    monkeypatch.setattr("agent_cli.providers.registry.create_provider", refuse)


def write_response(tmp_path: Path, text: str, name: str = "response.txt") -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def out_dir(tmp_path: Path) -> Path:
    target = tmp_path / "generated"
    target.mkdir()
    return target


def test_version_reports_the_package_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main(["--version"])

    captured = capsys.readouterr()
    assert error.value.code == 0
    assert captured.out == f"clispecforge {agent_cli.__version__}\n"


def test_plan_prints_contents_and_digest_without_writing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    response = write_response(tmp_path, _RESPONSE)
    generated = out_dir(tmp_path)

    exit_code = main(["plan", str(response), "--out-dir", str(generated)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert f"Response SHA-256: {response_digest(_RESPONSE)}" in captured.out
    assert "Plan: 2 file(s)" in captured.out
    assert "hello world" in captured.out
    assert '__version__ = "0.1.0"' in captured.out
    assert f"--- end {generated / 'hello.txt'} ---" in captured.out
    assert "--expect-sha256" in captured.out
    assert list(generated.iterdir()) == []


def test_plan_reads_a_response_from_standard_input(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    generated = out_dir(tmp_path)
    monkeypatch.setattr("sys.stdin", io.StringIO(_RESPONSE))

    exit_code = main(["plan", "-", "--out-dir", str(generated)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert f"Response SHA-256: {response_digest(_RESPONSE)}" in captured.out
    assert "Plan: 2 file(s)" in captured.out
    assert list(generated.iterdir()) == []


def test_plan_preserves_a_file_holding_an_inner_markdown_fence(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    response = write_response(tmp_path, _RESPONSE_WITH_NESTED_FENCE)
    generated = out_dir(tmp_path)

    exit_code = main(["plan", str(response), "--out-dir", str(generated)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "```bash" in captured.out
    assert "This sentence after the inner fence must survive parsing." in captured.out


def test_plan_escapes_terminal_control_characters(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    response = write_response(tmp_path, _RESPONSE_WITH_CONTROL_CHARACTERS)

    exit_code = main(["plan", str(response), "--out-dir", str(out_dir(tmp_path))])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "hello\\x1b[2Jworld" in captured.out
    assert "\x1b" not in captured.out


def test_plan_rejects_an_unsafe_path(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    response = write_response(tmp_path, _RESPONSE_WITH_UNSAFE_PATH)
    generated = out_dir(tmp_path)

    exit_code = main(["plan", str(response), "--out-dir", str(generated)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "Error: Unsafe or invalid file path" in captured.err
    assert not (generated.parent / "outside.txt").exists()


def test_plan_rejects_duplicate_targets_before_approval(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    response = write_response(tmp_path, _RESPONSE_WITH_DUPLICATE)

    exit_code = main(["plan", str(response), "--out-dir", str(out_dir(tmp_path))])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "Error: Duplicate generated file target" in captured.err


def test_plan_rejects_a_response_with_no_file_blocks(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    response = write_response(tmp_path, _RESPONSE_WITHOUT_FILE_BLOCKS)

    exit_code = main(["plan", str(response), "--out-dir", str(out_dir(tmp_path))])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "Error: no complete 'FILE:' blocks found" in captured.err
    assert "file-output-contract" in captured.err


def test_plan_rejects_an_empty_response(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    response = write_response(tmp_path, "")

    exit_code = main(["plan", str(response), "--out-dir", str(out_dir(tmp_path))])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Error: no complete 'FILE:' blocks found" in captured.err


def test_plan_rejects_an_unclosed_fenced_block(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    response = write_response(tmp_path, _RESPONSE_WITH_UNCLOSED_FENCE)

    exit_code = main(["plan", str(response), "--out-dir", str(out_dir(tmp_path))])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Error: no complete 'FILE:' blocks found" in captured.err


def test_plan_reports_a_missing_response_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "absent.txt"

    exit_code = main(["plan", str(missing), "--out-dir", str(out_dir(tmp_path))])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert f"Error: cannot read response from {missing}" in captured.err


def test_apply_writes_every_file_under_the_output_directory(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    response = write_response(tmp_path, _RESPONSE)
    generated = out_dir(tmp_path)

    exit_code = main(["apply", str(response), "--out-dir", str(generated)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert (generated / "hello.txt").read_text(encoding="utf-8") == "hello world\n"
    assert (generated / "src/pkg/__init__.py").read_text(encoding="utf-8") == (
        '__version__ = "0.1.0"\n'
    )
    assert f"Wrote {generated / 'hello.txt'}" in captured.out


def test_apply_reads_a_response_from_standard_input(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    generated = out_dir(tmp_path)
    monkeypatch.setattr("sys.stdin", io.StringIO(_RESPONSE))

    exit_code = main(["apply", "-", "--out-dir", str(generated)])

    assert exit_code == 0
    assert (generated / "hello.txt").read_text(encoding="utf-8") == "hello world\n"


def test_apply_rejects_a_response_with_no_file_blocks(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    response = write_response(tmp_path, _RESPONSE_WITHOUT_FILE_BLOCKS)
    generated = out_dir(tmp_path)

    exit_code = main(["apply", str(response), "--out-dir", str(generated)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "Error: no complete 'FILE:' blocks found" in captured.err
    assert list(generated.iterdir()) == []


def test_apply_reports_a_missing_response_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "absent.txt"

    exit_code = main(["apply", str(missing), "--out-dir", str(out_dir(tmp_path))])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert f"Error: cannot read response from {missing}" in captured.err


def test_apply_refuses_to_overwrite_without_force(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    response = write_response(tmp_path, _RESPONSE)
    generated = out_dir(tmp_path)
    existing = generated / "hello.txt"
    existing.write_text("original", encoding="utf-8")

    exit_code = main(["apply", str(response), "--out-dir", str(generated)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Error: Refusing to overwrite" in captured.err
    assert existing.read_text(encoding="utf-8") == "original"
    assert not (generated / "src/pkg/__init__.py").exists()


def test_apply_overwrites_with_force(tmp_path: Path) -> None:
    response = write_response(tmp_path, _RESPONSE)
    generated = out_dir(tmp_path)
    existing = generated / "hello.txt"
    existing.write_text("original", encoding="utf-8")

    exit_code = main(["apply", str(response), "--out-dir", str(generated), "--force"])

    assert exit_code == 0
    assert existing.read_text(encoding="utf-8") == "hello world\n"


def test_apply_rejects_duplicate_targets_before_writing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    response = write_response(tmp_path, _RESPONSE_WITH_DUPLICATE)
    generated = out_dir(tmp_path)

    exit_code = main(["apply", str(response), "--out-dir", str(generated)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Error: Duplicate generated file target" in captured.err
    assert not (generated / "same.txt").exists()


def test_apply_rejects_an_unsafe_path_before_writing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    response = write_response(tmp_path, _RESPONSE_WITH_UNSAFE_PATH)
    generated = out_dir(tmp_path)

    exit_code = main(["apply", str(response), "--out-dir", str(generated)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Error: Unsafe or invalid file path" in captured.err
    assert not (generated.parent / "outside.txt").exists()


def test_apply_accepts_the_digest_reported_by_plan(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    response = write_response(tmp_path, _RESPONSE)
    generated = out_dir(tmp_path)

    assert main(["plan", str(response), "--out-dir", str(generated)]) == 0
    planned = capsys.readouterr().out
    digest = planned.splitlines()[0].removeprefix("Response SHA-256: ")

    exit_code = main(
        ["apply", str(response), "--out-dir", str(generated), "--expect-sha256", digest]
    )

    assert exit_code == 0
    assert (generated / "hello.txt").read_text(encoding="utf-8") == "hello world\n"


def test_apply_rejects_a_response_that_changed_since_the_plan(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    response = write_response(tmp_path, _RESPONSE)
    generated = out_dir(tmp_path)
    approved = response_digest(_RESPONSE)

    response.write_text(_RESPONSE.replace("hello world", "rm -rf /"), encoding="utf-8")
    exit_code = main(
        ["apply", str(response), "--out-dir", str(generated), "--expect-sha256", approved]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "Error: response digest mismatch" in captured.err
    assert approved in captured.err
    assert list(generated.iterdir()) == []


def test_apply_accepts_an_uppercase_expected_digest(tmp_path: Path) -> None:
    response = write_response(tmp_path, _RESPONSE)
    generated = out_dir(tmp_path)

    exit_code = main(
        [
            "apply",
            str(response),
            "--out-dir",
            str(generated),
            "--expect-sha256",
            response_digest(_RESPONSE).upper(),
        ]
    )

    assert exit_code == 0


def test_digest_is_stable_across_a_file_and_standard_input(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    response = write_response(tmp_path, _RESPONSE)
    generated = out_dir(tmp_path)

    assert main(["plan", str(response), "--out-dir", str(generated)]) == 0
    from_file = capsys.readouterr().out.splitlines()[0]

    monkeypatch.setattr("sys.stdin", io.StringIO(_RESPONSE))
    assert main(["plan", "-", "--out-dir", str(generated)]) == 0
    from_stdin = capsys.readouterr().out.splitlines()[0]

    assert from_file == from_stdin
