# Skill research notes

These project skills were added after checking current public documentation for Python CLI structure, clean Python, and CLI behavior.

## Sources checked

- Python `argparse` documentation: use parser libraries, subcommands, help text, error handling, and newer Python 3.14 options such as `suggest_on_error` and `color`.
- Command Line Interface Guidelines: stdout/stderr discipline, exit codes, examples in help text, useful errors, and script-friendly output.
- Ruff documentation: one tool for linting, formatting, import sorting, upgrade rules, and unused-import cleanup.
- mypy documentation: strict mode as a set of optional checks for catching type unsoundness.
- pytest documentation: capture stdout and stderr separately when testing CLI behavior.
- Python Packaging User Guide: use `[project.scripts]` for installed console commands and optional dependencies for feature groups.
- Typer documentation: useful reference for CLIs that need richer help and shell completion, but this project keeps the baseline CLI dependency-free.

## Skills added

- `python-code-quality`
- `stdlib-cli-ux`
- `cli-test-coverage`
- `python-packaging-cli`

These sit beside the Karpathy-inspired agent behavior skills. The intent is split cleanly: Karpathy-style skills guide how the agent works, while the new skills guide what good Python CLI output should look like.

## Consolidation

After review, `cli-ux-contracts` and `argparse-stdlib-cli` were merged into `stdlib-cli-ux` because this project intentionally uses the standard library for its baseline CLI surface. Keeping UX rules and parser rules together reduces prompt clutter and gives the agent one command-design contract.

`simplicity-first` and `surgical-changes` were merged into `focused-implementation`. They both guide scope control during edits, and agents are more likely to apply them correctly as one compact skill.
