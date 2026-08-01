# CliSpecForge

[![Tests](https://github.com/lilabrooks/clispecforge/actions/workflows/tests.yml/badge.svg)](https://github.com/lilabrooks/clispecforge/actions/workflows/tests.yml)
[![Coverage](https://github.com/lilabrooks/clispecforge/actions/workflows/coverage.yml/badge.svg)](https://github.com/lilabrooks/clispecforge/actions/workflows/coverage.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

CliSpecForge turns a Markdown specification for a small Python CLI into a
reviewable file plan. It sends one request to Anthropic or OpenAI, previews the
complete fenced file blocks returned by the model, and writes them only when
you pass `--apply`.

Its job ends after the write. Reviewing, running, testing, and revising the
scaffold remain normal development work.

## Install

Install the tagged release with [pipx](https://pipx.pypa.io/):

```bash
pipx install "git+https://github.com/lilabrooks/clispecforge.git@v0.5.0"
clispecforge providers
```

The base installation uses only the Python standard library. Python 3.12 or
newer is required.

## Quick mechanics demo

The default `echo` provider needs no credentials or network access. In Bash or
Zsh, use it to exercise preview and write behavior with a deterministic file
block:

```bash
demo_dir=$(mktemp -d)
demo_prompt=$'FILE: hello.py\n```python\nprint("Hello from CliSpecForge")\n```'

clispecforge build --out-dir "$demo_dir" "$demo_prompt"
clispecforge build --apply --out-dir "$demo_dir" "$demo_prompt"
python3 "$demo_dir/hello.py"
```

The first build prints a one-file plan. The second writes `hello.py`, and the
last command prints:

```text
Hello from CliSpecForge
```

This checks CliSpecForge's prompt, parser, preview, and guarded-write path. It
does not call a model or demonstrate generated code quality.

## Generate from a spec

Install one provider SDK into the pipx environment:

```bash
pipx inject clispecforge openai
```

Then select the provider, supply its credential through the environment, and
preview a generation:

```bash
export OPENAI_API_KEY="your-key"
export CLISPECFORGE_PROVIDER=openai

clispecforge build --spec example \
  "Implement this spec as a small installable Python package"
```

Add `--apply --out-dir ./greeting-project` after reviewing the plan. Anthropic
works the same way with `pipx inject clispecforge anthropic`,
`ANTHROPIC_API_KEY`, and `CLISPECFORGE_PROVIDER=anthropic`.

Model responses can vary. Treat every returned file as untrusted input and
review its contents before applying or running it.

## What happens on `build`

1. CliSpecForge loads and validates the optional Markdown spec.
2. It attaches any selected instruction skills and a plain-text file contract.
3. The configured provider receives one completion request.
4. Complete `FILE: relative/path` blocks become a proposed file set.
5. CliSpecForge validates every target and prints the plan.
6. `--apply` writes the files beneath the selected output directory.

The tool has no conversation loop, autonomous retry, code execution, test
runner, Git integration, or repository-aware patching. A response stopped at
the configured output-token limit fails instead of being treated as complete.

## Write safeguards

- Preview is the default. Writes require `--apply`.
- Existing targets detected during preflight require the explicit `--force`
  flag.
- Absolute paths, parent traversal, symbolic-link escapes, and duplicate
  resolved targets are rejected.
- An unfinished fenced block is ignored.
- Duplicate and existing-target checks happen before any file is written.

These checks reduce accidental writes and common path escapes. They are not a
filesystem sandbox against concurrent path changes, and they do not establish
that generated code is correct or safe to execute.

## Specs and optional skills

A spec is ordinary Markdown with these sections: `Purpose`, `Commands`,
`Inputs`, `Outputs`, `Behavior`, and `Acceptance tests`. Start from
[`specs/templates/cli-spec.md`](specs/templates/cli-spec.md), then validate it:

```bash
clispecforge spec check path/to/spec.md
```

`build` warns and continues when a spec is invalid. Pass `--strict` to fail
before the provider call.

Skills are small Markdown instructions that can shape a request without adding
runtime behavior to CliSpecForge:

```bash
clispecforge skill list
clispecforge build --spec path/to/spec.md \
  --skill python-packaging-cli \
  "Implement this spec"
```

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `CLISPECFORGE_PROVIDER` | `echo` | Select `echo`, `openai`, or `anthropic`. |
| `CLISPECFORGE_MODEL` | provider default | Override the provider adapter's model. |
| `CLISPECFORGE_MAX_TOKENS` | `4096` | Set the provider output-token limit to a positive integer. |
| `CLISPECFORGE_SYSTEM_PROMPT` | concise assistant prompt | Replace the system prompt sent to model providers. |
| `OPENAI_API_KEY` | unset | Credential read by the OpenAI SDK. |
| `ANTHROPIC_API_KEY` | unset | Credential read by the Anthropic SDK. |

Command-level `--provider` overrides `CLISPECFORGE_PROVIDER`. CliSpecForge does
not load `.env` files.

## Standalone example

[`examples/greeting-cli`](examples/greeting-cli) is a small, independently
packaged CLI that illustrates the sort of output this project targets. It
imports no CliSpecForge code and is excluded from the CliSpecForge wheel.

From a development checkout with `.[dev]` installed:

```bash
python -m pytest examples/greeting-cli/tests
python -m build examples/greeting-cli
```

The example is maintained as a readable sample. It is not evidence that an
arbitrary model response will pass its acceptance tests.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
make check
make coverage
```

`make check` runs Ruff, mypy, pytest, and branch coverage with a 90% floor.
`make coverage` runs the test-and-coverage portion by itself. CI covers Python
3.12, 3.13, and 3.14. See
[CONTRIBUTING.md](CONTRIBUTING.md) for the contribution workflow.

## More detail

- [Design and scope](docs/design.md)
- [Design decisions](docs/decisions.md)
- [Standalone example walkthrough](docs/guides/greeting-cli-example.md)
- [pipx and artifact guide](docs/guides/pipx-artifact-guide.md)
- [Changelog](CHANGELOG.md)

## Project status

CliSpecForge is a personal side project and public reference implementation. It
has no support SLA. Releases are tagged, and behavior changes are recorded in
the changelog.
