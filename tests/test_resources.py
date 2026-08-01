from pathlib import Path

import pytest

from agent_cli import resources
from agent_cli.cli import main
from agent_cli.resources import default_skill_root, default_spec_root


def test_default_spec_root_prefers_cwd_specs() -> None:
    # Running from the repo root, the checked-in specs/cli should win.
    root = default_spec_root()

    assert root == Path("specs/cli")
    assert any(root.rglob("*.md"))


def test_default_skill_root_prefers_cwd_skills() -> None:
    root = default_skill_root()

    assert root == Path("skills/agent")
    assert any(root.rglob("*.md"))


def test_default_spec_root_uses_bundled_specs_outside_a_checkout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundled = tmp_path / "bundled-specs"
    bundled.mkdir()
    (bundled / "example.md").write_text("# Example\n", encoding="utf-8")
    monkeypatch.setattr(resources, "CWD_SPEC_ROOT", tmp_path / "missing-specs")
    monkeypatch.setattr(resources, "_bundled_root", lambda *_parts: bundled)

    assert default_spec_root() == bundled


def test_default_skill_root_uses_bundled_skills_outside_a_checkout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundled = tmp_path / "bundled-skills"
    bundled.mkdir()
    (bundled / "example.md").write_text("# Example\n", encoding="utf-8")
    monkeypatch.setattr(resources, "CWD_SKILL_ROOT", tmp_path / "missing-skills")
    monkeypatch.setattr(resources, "_bundled_root", lambda *_parts: bundled)

    assert default_skill_root() == bundled


def test_all_skills_warns_when_no_skills_found(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # An empty working directory has no specs/skills and no bundled fallback in
    # the source tree, so --all-skills must warn instead of silently no-opping.
    monkeypatch.chdir(tmp_path)

    exit_code = main(["run", "--all-skills", "build it"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "found no skills" in captured.err
    assert captured.out == "clispecforge: Echo provider received: build it\n"
