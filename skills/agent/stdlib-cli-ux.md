---
source: https://clig.dev/; https://docs.python.org/3/library/argparse.html
owner: Lila Brooks
deciders: [Lila Brooks]
---
# Standard-library CLI UX

## Purpose
Build dependency-free Python CLIs that are predictable for humans, scriptable for automation, and implemented cleanly with `argparse`.

## When to use
Use this for commands, subcommands, flags, arguments, help text, parser errors, stdout/stderr behavior, and exit codes.

## Rules
- Use `argparse.ArgumentParser` for the baseline CLI surface.
- Put command execution behind callable functions so tests can call behavior without shelling out.
- Use subparsers for command groups.
- Set `required=True` on subparsers when a command is required.
- Print primary command output to stdout.
- Print errors, warnings, progress, and diagnostic messages to stderr.
- Return exit code `0` for success and non-zero for failure.
- Make `-h` and `--help` useful for the main command and every subcommand.
- Lead help text with the command's job and at least one common example when the command is non-trivial.
- Use clear `metavar`, `choices`, and `help` text for arguments that users must understand.
- Prefer explicit long flags such as `--output` and `--format`; add short flags only for common actions.
- For Python 3.14+, enable `suggest_on_error` or set it as an attribute after parser creation so older supported Python versions can still run.
- Be intentional about color: keep help readable when output is redirected.
- Suggest likely fixes for invalid commands or arguments when it is safe.
- Do not silently run a guessed command after invalid input.

## Verification
- Test parser construction for new commands.
- Test a valid invocation through `main([...])`.
- Test stdout, stderr, and exit code for success.
- Test stdout, stderr, and exit code for at least one failure case.
- Include tests for `--help` at the command and subcommand level.
- Include assertions for required arguments, optional flags, and examples.
- Do not claim the help output was run; CliSpecForge does not execute it.
