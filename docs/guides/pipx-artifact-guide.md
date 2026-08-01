---
title: pipx artifact guide
type: guide
status: current
date: 2026-07-04
owner: Lila Brooks
deciders: [Lila Brooks]
tags: [documentation, guide, pipx, packaging]
---

# pipx artifact guide

This guide shows how to install from GitHub, create an installable artifact, and test both paths with pipx.

## 1. Install directly from GitHub

Use this when someone wants to install the CLI without cloning the repo.

```bash
pipx install "git+https://github.com/lilabrooks/clispecforge.git"
```

Test the installed command:

```bash
clispecforge providers
```

Install from a specific branch:

```bash
pipx install "git+https://github.com/lilabrooks/clispecforge.git@main"
```

Install the tagged release:

```bash
pipx install "git+https://github.com/lilabrooks/clispecforge.git@v0.5.0"
```

Upgrade later:

```bash
pipx upgrade clispecforge
```

Uninstall:

```bash
pipx uninstall clispecforge
```

## 2. Enter the project for local artifact builds

```bash
# Skip the clone step if you already have a local checkout.
git clone https://github.com/lilabrooks/clispecforge.git
cd clispecforge
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## 3. Run quality checks

```bash
make check
```

Fix any failures before building.

## 4. Install the build tools

If you did not install the development extra, install the build frontend and backend:

```bash
python -m pip install build hatchling
```

## 5. Build the artifacts

```bash
python -m build
```

Expected output files:

```text
dist/clispecforge-0.5.0.tar.gz
dist/clispecforge-0.5.0-py3-none-any.whl
```

The artifact names use the `clispecforge` distribution name. The wheel installs the `clispecforge` command.

## 6. Install the wheel with pipx

```bash
pipx install dist/clispecforge-0.5.0-py3-none-any.whl
```

If `clispecforge` is already installed with pipx, reinstall it:

```bash
pipx reinstall clispecforge
```

For local development, install the project in editable mode:

```bash
pipx install -e .
```

## 7. Test the installed command

```bash
clispecforge providers
clispecforge spec check example
```

## 8. Move the artifact

The portable file to share is the wheel:

```text
dist/clispecforge-0.5.0-py3-none-any.whl
```

On another machine with Python and pipx installed:

```bash
pipx install /path/to/clispecforge-0.5.0-py3-none-any.whl
clispecforge providers
```

## 9. Uninstall

```bash
pipx uninstall clispecforge
```
