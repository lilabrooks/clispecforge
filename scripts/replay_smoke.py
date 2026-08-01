"""Exercise one recorded response through parse, write, build, install, and run."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import venv
from pathlib import Path

from agent_cli.core.fileset import parse_generated_files, resolve_target_path, write_generated_files

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "replay" / "greeting-package-response.txt"
EXPECTED_PATHS = {
    "README.md",
    "pyproject.toml",
    "src/greeting_cli/__init__.py",
    "src/greeting_cli/cli.py",
}


def run_checked(*arguments: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        arguments,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        command = " ".join(arguments)
        msg = f"Command failed ({result.returncode}): {command}\n{result.stdout}{result.stderr}"
        raise RuntimeError(msg)
    return result


def environment_command(environment: Path, name: str) -> Path:
    scripts = environment / ("Scripts" if sys.platform == "win32" else "bin")
    suffix = ".exe" if sys.platform == "win32" else ""
    return scripts / f"{name}{suffix}"


def main() -> int:
    files = parse_generated_files(FIXTURE.read_text(encoding="utf-8"))
    paths = {generated.path for generated in files}
    if paths != EXPECTED_PATHS:
        msg = f"Replay paths differ: expected {sorted(EXPECTED_PATHS)}, got {sorted(paths)}"
        raise RuntimeError(msg)

    readme = next(generated for generated in files if generated.path == "README.md")
    if "This sentence after the inner fence must survive parsing." not in readme.content:
        raise RuntimeError("The replay README was truncated at its inner Markdown fence.")

    with tempfile.TemporaryDirectory(prefix="clispecforge-replay-") as temporary:
        temporary_root = Path(temporary)
        project = temporary_root / "generated project [replay]"
        targets = [resolve_target_path(project, generated) for generated in files]
        write_generated_files(files, targets)

        artifacts = temporary_root / "artifacts"
        run_checked(
            sys.executable,
            "-m",
            "build",
            "--wheel",
            "--no-isolation",
            "--outdir",
            str(artifacts),
            str(project),
        )
        wheels = list(artifacts.glob("*.whl"))
        if len(wheels) != 1:
            raise RuntimeError(f"Expected one replay wheel, found {len(wheels)}.")

        environment = temporary_root / "installed environment"
        venv.EnvBuilder(with_pip=True).create(environment)
        python = environment_command(environment, "python")
        run_checked(str(python), "-m", "pip", "install", "--no-deps", str(wheels[0]))
        result = run_checked(str(environment_command(environment, "greet")), "Lila")
        if result.stdout != "Hello, Lila\n":
            raise RuntimeError(f"Unexpected replay output: {result.stdout!r}")

    sys.stdout.write("Replay smoke passed: parsed, wrote, built, installed, and ran greet Lila.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
