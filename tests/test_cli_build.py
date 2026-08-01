from pathlib import Path

import pytest

from agent_cli.cli import build as build_agent_task
from agent_cli.cli import main

# The echo provider parrots the full agent prompt back verbatim, so embedding a
# FILE: block in the task text is enough to exercise the parse-and-write path
# without a real model provider.
_TASK_WITH_FILE = "\n".join(
    [
        "Please create a greeting script.",
        "FILE: hello.txt",
        "```",
        "hello world",
        "```",
    ]
)

_TASK_WITH_DUPLICATE_FILE = "\n".join(
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

_TASK_WITH_UNSAFE_FILE = "\n".join(
    [
        "FILE: ../outside.txt",
        "```",
        "escaped",
        "```",
    ]
)


def test_build_attaches_file_output_contract_skill() -> None:
    text, files = build_agent_task("say hi, no files needed")

    assert "# Agent skill: File output contract" in text
    assert files == []


def test_build_dry_run_prints_plan_without_writing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["build", "--out-dir", str(tmp_path), _TASK_WITH_FILE])

    captured = capsys.readouterr()
    target = tmp_path / "hello.txt"
    assert exit_code == 0
    assert "Plan: 1 file(s)" in captured.out
    assert str(target) in captured.out
    assert "Re-run with --apply" in captured.out
    assert not target.exists()


def test_build_apply_writes_the_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["build", "--out-dir", str(tmp_path), "--apply", _TASK_WITH_FILE])

    captured = capsys.readouterr()
    target = tmp_path / "hello.txt"
    assert exit_code == 0
    assert target.read_text(encoding="utf-8") == "hello world\n"
    assert f"Wrote {target}" in captured.out


def test_build_apply_refuses_to_overwrite_without_force(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    existing = tmp_path / "hello.txt"
    existing.write_text("original", encoding="utf-8")

    exit_code = main(["build", "--out-dir", str(tmp_path), "--apply", _TASK_WITH_FILE])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Error: Refusing to overwrite" in captured.err
    assert existing.read_text(encoding="utf-8") == "original"


def test_build_apply_overwrites_with_force(tmp_path: Path) -> None:
    existing = tmp_path / "hello.txt"
    existing.write_text("original", encoding="utf-8")

    exit_code = main(["build", "--out-dir", str(tmp_path), "--apply", "--force", _TASK_WITH_FILE])

    assert exit_code == 0
    assert existing.read_text(encoding="utf-8") == "hello world\n"


def test_build_apply_rejects_duplicate_targets(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["build", "--out-dir", str(tmp_path), "--apply", _TASK_WITH_DUPLICATE_FILE])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Error: Duplicate generated file target" in captured.err
    assert not (tmp_path / "same.txt").exists()


def test_build_rejects_unsafe_target_before_preview(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["build", "--out-dir", str(tmp_path), _TASK_WITH_UNSAFE_FILE])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "Error: Unsafe or invalid file path" in captured.err
    assert not (tmp_path.parent / "outside.txt").exists()


def test_build_warns_when_no_file_blocks_found(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["build", "--out-dir", str(tmp_path), "just answer in prose, no files"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "no 'FILE:' blocks found" in captured.err


_VALID_SPEC = "\n".join(
    [
        "# Example CLI",
        "",
        "## Purpose",
        "Do a thing.",
        "",
        "## Commands",
        "- `example run`",
        "",
        "## Inputs",
        "None.",
        "",
        "## Outputs",
        "A greeting.",
        "",
        "## Behavior",
        "Print a greeting.",
        "",
        "## Acceptance tests",
        "- Output includes a greeting.",
    ]
)

_INVALID_SPEC = "\n".join(
    [
        "# Incomplete CLI",
        "",
        "Just prose, no required sections.",
    ]
)


def test_build_accepts_a_spec_file_path_outside_specs_cli(tmp_path: Path) -> None:
    spec_path = tmp_path / "somewhere-else.md"
    spec_path.write_text(_VALID_SPEC, encoding="utf-8")

    text, _files = build_agent_task("describe it", spec=str(spec_path))

    assert "# CLI spec: Example CLI" in text


def test_build_warns_and_continues_on_invalid_spec_by_default(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    spec_path = tmp_path / "bad-spec.md"
    spec_path.write_text(_INVALID_SPEC, encoding="utf-8")

    exit_code = main(
        ["build", "--out-dir", str(tmp_path), "--spec", str(spec_path), "say hi, no files"]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Warning: spec" in captured.err
    assert "missing required section" in captured.err
    assert "Continuing without --strict" in captured.err


def test_build_strict_blocks_on_invalid_spec_before_calling_model(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    spec_path = tmp_path / "bad-spec.md"
    spec_path.write_text(_INVALID_SPEC, encoding="utf-8")

    exit_code = main(
        [
            "build",
            "--out-dir",
            str(tmp_path),
            "--spec",
            str(spec_path),
            "--strict",
            "say hi, no files",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "Error: Spec" in captured.err
    assert "failed validation" in captured.err
    assert f"clispecforge spec check {spec_path}" in captured.err


def test_build_strict_allows_a_valid_spec_through(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    spec_path = tmp_path / "good-spec.md"
    spec_path.write_text(_VALID_SPEC, encoding="utf-8")

    exit_code = main(
        [
            "build",
            "--out-dir",
            str(tmp_path),
            "--spec",
            str(spec_path),
            "--strict",
            "say hi, no files",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "failed validation" not in captured.err
