# CliSpecForge

[![Quality](https://github.com/lilabrooks/clispecforge/actions/workflows/quality.yml/badge.svg)](https://github.com/lilabrooks/clispecforge/actions/workflows/quality.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

CliSpecForge turns a Markdown specification for a small Python CLI into a
reviewable file set. It sends one request to Anthropic or OpenAI, prints the
complete file contents with terminal control characters escaped, and writes
them only when you pass `--apply`. It can also take a response you already
have, so an agent host supplies the generation while the parsing, path checks,
preview, and guarded writes stay here.

Its job ends after the write. Reviewing, running, testing, and revising the
scaffold remain normal development work.

## Where CliSpecForge fits

A skill gives an agent reusable instructions. A coding agent can inspect a
repository, edit files, run tools, diagnose failures, and revise its work.
CliSpecForge owns a smaller boundary around one model request: it turns a
Markdown contract into a checked file proposal and requires a separate decision
before writing it.

| Layer | Main job | Best fit |
| --- | --- | --- |
| Agent skill | Tell an agent how to approach recurring work. | Conventions, checklists, and reusable workflows inside an agent host. |
| Coding agent | Work interactively with repository context and tools. | Existing projects, patches, tests, diagnosis, and repair. |
| CliSpecForge | Enforce a provider-neutral, single-pass spec-to-files handoff. | Small greenfield Python CLI scaffolds that should be reviewed before they reach disk. |

These roles can be combined. The
[`clispecforge-scaffold`](https://github.com/lilabrooks/lila-agent-skills/tree/main/skills/clispecforge-scaffold)
skill drives the offline handoff from Codex or Claude Code: it checks the
request against its scope, validates the spec, has the host model produce the
complete file blocks, previews them with `plan`, and waits for explicit approval
before `apply`.

The skill defines the procedure and asks for approval; CliSpecForge enforces
the mechanical handoff checks. Skill instructions depend on the agent and its
host following them. CliSpecForge independently parses the response, rejects
unsafe or duplicate targets, escapes terminal control characters, requires a
separate `apply` command, refuses an existing target without `--force`, and,
when `apply` receives the digest `plan` reported, refuses a response that
changed after approval. Use the skill when you want that path followed
consistently, or call `plan` and `apply` directly when you are managing the
handoff yourself. Pass `--expect-sha256` yourself in that case; without it
`apply` writes whatever the response currently contains.

This narrow scope also keeps the mechanics easy to inspect and test. The same
spec, optional instruction skills, file contract, and guarded-write path work
through the supported Anthropic and OpenAI adapters. Model output still varies,
and CliSpecForge does not test or repair the generated project.

Use CliSpecForge when the CLI contract is settled and you want a bounded,
review-first scaffold step. Use a coding agent for substantive repository work
that needs discovery, patching, execution, feedback, or Git. Skills complement
both approaches by carrying reusable guidance.

## Install

Install the current `main` branch with [pipx](https://pipx.pypa.io/):

```bash
pipx install "git+https://github.com/lilabrooks/clispecforge.git@main"
clispecforge providers
```

Refresh an existing installation from the newest `main` commit with
`pipx upgrade clispecforge`.

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

The first build prints a one-file plan and its contents. The second writes
`hello.py`, and the last command prints:

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

Model responses can vary. Treat every returned file as untrusted input. The
preview escapes terminal control characters and prints each file's contents for
review before applying or running it.

## What happens on `build`

1. CliSpecForge loads and validates the optional Markdown spec.
2. It attaches any selected instruction skills and a plain-text file contract.
3. The configured provider receives one completion request.
4. Complete `FILE: relative/path` blocks become a proposed file set.
5. CliSpecForge validates every target and prints the terminal-safe plan and
   file contents.
6. `--apply` writes the files beneath the selected output directory.

The tool has no conversation loop, autonomous retry, code execution, test
runner, Git integration, or repository-aware patching. A response stopped at
the configured output-token limit fails instead of being treated as complete.

## Apply a response you already have

`plan` and `apply` take a response that already exists, in the same `FILE:`
format `build` consumes. Neither contacts a provider, so an agent host, a saved
transcript, or a recorded fixture can supply the generation while CliSpecForge
keeps the parsing, path checks, preview, and guarded writes:

```bash
clispecforge plan response.txt --out-dir ./generated
clispecforge apply response.txt --out-dir ./generated
clispecforge apply response.txt --out-dir ./generated --force
```

Pass `-` instead of a filename to read the response from standard input.

`plan` prints the response SHA-256 on its first line and writes nothing. Pass
that digest back to tie the write to the response you actually reviewed:

```bash
clispecforge apply response.txt --out-dir ./generated --expect-sha256 <digest-from-plan>
```

`apply` fails without writing if the response changed since the preview. The
digest is an integrity check against drift between approval and write, not a
signature or a statement that the generated code is correct.

A response with no complete `FILE:` block is an error for both commands, and
`plan` rejects duplicate targets so an approved plan is one `apply` can carry
out.

Report the installed version with:

```bash
clispecforge --version
```

## Write safeguards

These apply to `build`, `plan`, and `apply` alike; the checks are shared code,
not repeated per command.

- Preview is the default. Writes require `build --apply` or the separate
  `apply` command.
- Existing targets detected during preflight require the explicit `--force`
  flag.
- Absolute paths, parent traversal, symbolic-link escapes, and duplicate
  resolved targets are rejected.
- An unfinished fenced block is ignored.
- Opening and closing fences must have the same number of backticks. Longer
  outer fences preserve Markdown files containing ordinary fenced examples.
- Control and formatting characters are escaped in previews, and rejected in
  generated paths.
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

## Deterministic replay smoke test

[`examples/replay/greeting-package-response.txt`](examples/replay/greeting-package-response.txt)
records one complete provider-style response. Its generated README contains an
inner fenced console example, exercising the variable-length outer fence.

Run the complete local handoff:

```bash
make smoke-replay
```

The smoke test parses the recorded response, writes all proposed files under a
temporary directory containing spaces and brackets, builds a wheel, installs it
in a fresh environment, and runs `greet Lila` outside the checkout. It is
deterministic evidence for the file handoff and packaging path. It does not call
a model or measure model-generated code quality.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
make check
make coverage
```

`make check` runs Ruff, mypy, pytest, and branch coverage with a 90% floor.
`make coverage` runs the test-and-coverage portion by itself. `make
smoke-replay` exercises the recorded-response package handoff. CI runs the
everyday gate on Python 3.12, 3.13, and 3.14, then runs the replay smoke test on
Python 3.14. See
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
