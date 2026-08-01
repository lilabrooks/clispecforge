---
source: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
owner: Lila Brooks
deciders: [Lila Brooks]
---
# Python packaging for CLIs

## Purpose
Ask for conventional Python CLI packaging with explicit dependencies and an
installed command entry point.

## When to use
Use this when changing `pyproject.toml`, command entry points, dependencies, package layout, versioning, or install instructions.

## Rules
- Put importable code under `src/`.
- Expose terminal commands through `[project.scripts]`.
- Keep `requires-python` accurate for the code that is written.
- Put development-only tools in optional dependencies.
- Add runtime dependencies only when the CLI behavior requires them.
- Keep provider-specific dependencies optional when possible.
- Document install and run commands in `README.md` when the user-facing command changes.

## Verification
- Confirm `pyproject.toml` parses.
- Confirm the script entry point targets a callable that returns an exit code.
- Include the build, installation, and command smoke-test steps the developer
  should run after applying the files.
- Do not describe the scaffold as installable or runnable until those steps
  have actually passed outside CliSpecForge.
