"""Repository-level consistency checks."""

import re
import shutil
import subprocess
import tomllib
from importlib.metadata import version
from pathlib import Path

import pytest

import agent_cli
from agent_cli.skills.loader import list_skills, load_skill, validate_skill
from agent_cli.specs.loader import list_specs, load_spec, validate_spec

REPO_ROOT = Path(__file__).resolve().parent.parent

ARTIFACT_VERSION = re.compile(r"clispecforge-(\d+\.\d+\.\d+)")
TAG_VERSION = re.compile(r"@v(\d+\.\d+\.\d+)")
PINNED_REQUIREMENT = re.compile(r"^[A-Za-z0-9_.-]+(?:\[[A-Za-z0-9_,.-]+\])?==")


def project_configuration() -> dict[str, object]:
    return tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def project_metadata() -> dict[str, object]:
    data = project_configuration()
    project = data["project"]
    assert isinstance(project, dict)
    return project


def test_project_exposes_one_named_command() -> None:
    assert project_metadata()["scripts"] == {"clispecforge": "agent_cli.cli:main"}


def scanner_requirements() -> list[str]:
    return [
        line.strip()
        for line in (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]


def test_project_derives_versions_from_git() -> None:
    configuration = project_configuration()
    project = project_metadata()
    build_system = configuration["build-system"]
    tool = configuration["tool"]
    assert isinstance(build_system, dict)
    assert isinstance(tool, dict)
    assert "version" not in project
    assert project["dynamic"] == ["version"]
    assert "hatch-vcs>=0.5.0" in build_system["requires"]
    assert tool["hatch"]["version"] == {"source": "vcs"}


def test_package_version_matches_installed_metadata() -> None:
    assert agent_cli.__version__ == version("clispecforge")


def released_version() -> str:
    changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    match = re.search(r"^## \[(\d+\.\d+\.\d+)\]", changelog, flags=re.MULTILINE)
    assert match is not None, "CHANGELOG.md has no '## [x.y.z]' release heading"
    return match.group(1)


def test_docs_reference_latest_release() -> None:
    expected_version = released_version()
    docs = [REPO_ROOT / "README.md", *sorted((REPO_ROOT / "docs").rglob("*.md"))]
    stale: list[str] = []
    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        for pattern in (ARTIFACT_VERSION, TAG_VERSION):
            stale.extend(
                f"{doc.relative_to(REPO_ROOT)}: {found}"
                for found in pattern.findall(text)
                if found != expected_version
            )
    assert not stale, f"stale version references (expected {expected_version}): {stale}"


def test_scanner_requirements_mirror_optional_dependencies() -> None:
    optional_dependencies = project_metadata()["optional-dependencies"]
    assert isinstance(optional_dependencies, dict)
    expected = sorted(
        dependency for dependencies in optional_dependencies.values() for dependency in dependencies
    )
    actual = sorted(scanner_requirements())
    missing = sorted(set(expected) - set(actual))
    assert not missing, f"requirements.txt is missing optional dependencies: {missing}"


def test_scanner_requirements_avoid_exact_pins() -> None:
    pinned = [line for line in scanner_requirements() if PINNED_REQUIREMENT.match(line)]
    assert not pinned, f"requirements.txt should use lower bounds, not exact pins: {pinned}"


def test_no_tracked_files_match_gitignore() -> None:
    if shutil.which("git") is None or not (REPO_ROOT / ".git").exists():
        pytest.skip("not a git checkout")
    result = subprocess.run(
        ["git", "ls-files", "-i", "-c", "--exclude-standard"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    tracked_but_ignored = result.stdout.split()
    assert not tracked_but_ignored, (
        f"tracked files match .gitignore (untrack with 'git rm --cached'): {tracked_but_ignored}"
    )


def test_bundled_specs_pass_validation() -> None:
    root = REPO_ROOT / "specs" / "cli"
    paths = list_specs(root)
    assert paths, f"no specs found under {root}"
    failures = [
        result.format()
        for result in (validate_spec(load_spec(path)) for path in paths)
        if not result.ok
    ]
    assert not failures, "\n".join(failures)


def test_bundled_skills_pass_validation() -> None:
    root = REPO_ROOT / "skills" / "agent"
    paths = list_skills(root)
    assert paths, f"no skills found under {root}"
    failures = [
        result.format()
        for result in (validate_skill(load_skill(path)) for path in paths)
        if not result.ok
    ]
    assert not failures, "\n".join(failures)
