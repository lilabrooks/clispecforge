from pathlib import Path

import pytest

from agent_cli.cli import main

_VALID_SPEC = """---
status: draft
---
# Example CLI

## Purpose
Demonstrate the spec commands.

## Commands
- `example`

## Inputs
None.

## Outputs
Text.

## Behavior
Print text.

## Acceptance tests
- Output includes text.
"""

_VALID_SKILL = """---
source: test
---
# Example skill

## Purpose
Demonstrate the skill commands.

## When to use
During tests.

## Rules
- Stay focused.

## Verification
- Check the result.
"""


@pytest.mark.parametrize(
    ("kind", "valid_document", "context_heading"),
    [
        ("spec", _VALID_SPEC, "# CLI spec: Example CLI"),
        ("skill", _VALID_SKILL, "# Agent skill: Example skill"),
    ],
)
def test_document_commands_list_show_and_check_validation_boundaries(
    kind: str,
    valid_document: str,
    context_heading: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = tmp_path / kind
    root.mkdir()
    valid_path = root / "example.md"
    valid_path.write_text(valid_document, encoding="utf-8")

    assert main([kind, "list", "--root", str(root)]) == 0
    assert capsys.readouterr().out == f"{valid_path}\n"

    assert main([kind, "show", "example", "--root", str(root)]) == 0
    assert context_heading in capsys.readouterr().out

    assert main([kind, "check", "example", "--root", str(root)]) == 0
    assert capsys.readouterr().out == f"{valid_path}: ok\n"

    invalid_path = root / "incomplete.md"
    invalid_path.write_text("# Incomplete\n", encoding="utf-8")

    assert main([kind, "check", "--root", str(root)]) == 1
    captured = capsys.readouterr()
    assert f"{valid_path}: ok" in captured.out
    assert f"{invalid_path}: failed" in captured.out
    assert "missing required section" in captured.out


@pytest.mark.parametrize(("kind", "plural"), [("spec", "specs"), ("skill", "skills")])
def test_document_commands_report_an_empty_root(
    kind: str,
    plural: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = tmp_path / "missing"

    assert main([kind, "list", "--root", str(root)]) == 0
    assert capsys.readouterr().out == f"No {plural} found under {root}.\n"

    assert main([kind, "check", "--root", str(root)]) == 1
    assert capsys.readouterr().out == f"No {plural} found under {root}.\n"
