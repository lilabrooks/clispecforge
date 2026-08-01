# Changelog

All notable changes to this project are documented here. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.7.0] - 2026-08-01

### Added

- `clispecforge plan RESPONSE` previews an existing provider-style response.
  It parses `FILE:` blocks, validates every target, rejects unsafe paths and
  duplicate targets, prints terminal-safe contents, reports the response
  SHA-256, and writes nothing.
- `clispecforge apply RESPONSE` writes the files in an existing response under
  `--out-dir`, with `--force` required for existing targets and an optional
  `--expect-sha256` that ties the write to the exact response that was
  previewed.
- Both commands accept `-` to read the response from standard input, and
  neither contacts OpenAI, Anthropic, or the echo provider. Agent hosts can
  supply the generation while CliSpecForge keeps parsing, validation, and
  writes.
- `clispecforge --version` reports the installed version from
  `agent_cli.__version__`.

## [0.6.0] - 2026-08-01

### Added

- Added a deterministic recorded-response smoke test that writes, builds,
  installs, and runs a generated greeting package outside the checkout.

### Changed

- Dry-run plans now print terminal-safe file contents for review before
  `--apply`.
- Consolidated test, coverage, lint, formatting, and typing CI into one quality
  workflow across Python 3.12 through 3.14.

### Fixed

- Preserve generated Markdown files containing fenced examples by matching
  variable-length opening and closing fences.
- Reject generated paths containing control or formatting characters and
  escape those characters in previewed file contents.

## [0.5.0] - 2026-08-01

### Added

- Added a standalone greeting CLI example with its own package metadata and tests.

### Changed

- Rewrote the README around the narrow product boundary and a verified, credential-free mechanics demo.
- Raised the enforced coverage floor to 90% with additional CLI boundary, provider-response, and installed-resource tests.
- Made `make check` enforce coverage as part of the everyday quality gate.
- Removed or qualified documentation and skill claims that implied CliSpecForge builds, installs, executes, or verifies model-generated artifacts.

### Removed

- Removed the embedded machine-details fixture from the CliSpecForge package.

### Fixed

- Allow strict mypy checks from a development install when the optional provider SDKs are absent.
- Keep `make check-all` isolated while enforcing the complete gate on every supported Python version.

## [0.4.0] - 2026-08-01

### Changed

- Reframed the repository as an independent, single-pass Python CLI scaffold generator.
- Replaced the kit-managed documentation and agent configuration with concise project-owned guidance.
- Renamed the distribution and executable to `clispecforge`, removed the fixture entry point, and aligned the public environment-variable prefix.
- Raised the provider output-token default to 4,096 and added `CLISPECFORGE_MAX_TOKENS` for explicit configuration.

### Removed

- Removed OKF maps, hooks, helpers, mirrored workflow skills, and their parity checks.

### Fixed

- Fail clearly when Anthropic or OpenAI reports a response truncated at the configured output-token limit.
- Reject generated paths that escape the output directory through symbolic links.
- Reject duplicate generated targets before writing any file.
- Ignore incomplete `FILE:` blocks with no closing fence.

## [0.3.0] - 2026-07-02

### Added

- `anthropic` provider adapter backed by the Claude Messages API (default model `claude-opus-4-8`), installed via the `anthropic` optional extra.
- `openai` provider adapter backed by the Chat Completions API (default model `gpt-4o-mini`), installed via the `openai` optional extra. Both adapters defer their SDK import to `complete()`, so the CLI keeps working with neither extra installed.
- `AGENT_CLI_MODEL` environment variable to override which model the active provider adapter calls.
- `agent build` command: runs the same spec/skill-aware prompt as `agent run` with the `file-output-contract` skill always attached, parses `FILE:` blocks from the reply (`core/fileset.py`), prints the write plan by default, writes files with `--apply`, and refuses to overwrite existing files unless `--force` is given. Generated paths are rejected if absolute or containing `..`.
- `--strict` flag on `agent build` to fail before the model call when the attached spec has validation errors; the default warns on stderr and continues.
- `skills/agent/file-output-contract.md` documenting the `FILE:` reply format the build parser consumes.

## [0.2.0] - 2026-07-02

### Added

- Default specs and skills are bundled inside the package, so `agent spec` and `agent skill` work from any directory after a pipx or pip install. A `specs/cli` or `skills/agent` folder in the working directory still takes precedence.
- `resources.py` resolves the active spec and skill roots: the working directory first, the bundled defaults as a fallback.
- `providers/registry.py` as the single source of truth for provider adapters. The factory, the unknown-provider error, and the `providers` command all read from it.
- Warning on stderr when `agent run --all-skills` finds no skills, instead of silently doing nothing.
- `Makefile` with `make check` (active interpreter) and `make check-all` (every supported Python via uv), plus `lint`, `format`, `typecheck`, `test`, and `coverage` targets.
- Configuration section in the README documenting `AGENT_CLI_PROVIDER` and `AGENT_CLI_SYSTEM_PROMPT` with usage examples.
- Tests covering the provider registry, spec and skill root resolution, the empty-skills warning, and the echo adapter ignoring the system prompt.

### Changed

- Provider selection is driven by the registry rather than a hardcoded `match` statement.
- Coverage enforces a 70% floor (`fail_under = 70`).
- CI runs against Python 3.12, 3.13, and 3.14.
- README reorganized: a dedicated Configuration section, the Flow diagram moved up, and duplicated check commands removed.
- `docs/architecture.md` points provider registration at `providers/registry.py`.

### Removed

- `.env.example`, which implied a `.env` auto-loading the project does not perform. The environment variables are documented in the README instead.

### Fixed

- Spec and skill commands failing when the CLI was installed and run outside a repo checkout. They relied on working-directory-relative paths that were not shipped in the package.
