---
title: my-cli generator test
type: guide
status: current
date: 2026-07-04
owner: Lila Brooks
deciders: [Lila Brooks]
tags: [documentation, guide, testing, my-cli]
---

# my-cli generator test

This guide shows how to test the `my-cli` generated CLI fixture in this repo.

## 1. Enter the project

```bash
# Skip the clone step if you already have a local checkout.
git clone https://github.com/lilabrooks/clispecforge.git
cd clispecforge
source .venv/bin/activate
```

## 2. Validate the my-cli spec

```bash
clispecforge spec check my-cli-details
```

Expected result:

```text
specs/cli/my-cli-details.md: ok
```

If `clispecforge` fails with `ModuleNotFoundError: No module named 'agent_cli'`, reinstall the project into the virtualenv:

```bash
python -m pip install -e ".[dev]"
```

On macOS, if the error persists, clear hidden flags on the virtualenv and retry:

```bash
chflags -R nohidden .venv
source .venv/bin/activate
clispecforge spec check my-cli-details
```

## 3. Run the implemented my-cli app

Basic mode:

```bash
python -m agent_cli.commands.my_cli --basic
```

Expected shape:

```text
hostname: ...
system: ...
machine: ...
```

Detailed mode:

```bash
python -m agent_cli.commands.my_cli --detailed
```

Expected shape:

```text
hostname: ...
system: ...
machine: ...
release: ...
version: ...
platform: ...
processor: ...
python_version: ...
```

## 4. Test the spec-to-agent prompt path

```bash
clispecforge run --spec my-cli-details \
  --skill goal-driven-execution \
  --skill focused-implementation \
  --skill stdlib-cli-ux \
  --skill cli-test-coverage \
  "Implement this CLI feature"
```

The default provider is `echo`, so this command proves that the Markdown spec and skills are loaded into the agent prompt. It does not call a real AI model yet.

To attach every available skill instead of selecting them one by one:

```bash
clispecforge run --spec my-cli-details --all-skills "Implement this CLI feature"
```

## 5. Run quality checks

```bash
pytest
ruff check .
ruff format --check .
mypy
```

All checks should pass before committing changes.

## 6. Understand build artifact names

If you build the project:

```bash
python -m build
```

The files in `dist/` use the `clispecforge` distribution name:

```text
clispecforge-0.4.0.tar.gz
clispecforge-0.4.0-py3-none-any.whl
```

The wheel installs only the project command:

```bash
clispecforge providers
```

The generated fixture stays available from the repository checkout through
`python -m agent_cli.commands.my_cli`; it is not a second installed command.

For the full artifact build and pipx install flow, see [pipx-artifact-guide.md](pipx-artifact-guide.md).
