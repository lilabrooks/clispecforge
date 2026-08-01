---
source: https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html
owner: Lila Brooks
deciders: [Lila Brooks]
---
# CLI test coverage

## Purpose
Make CLI behavior verifiable through tests instead of manual terminal checks.

## When to use
Use this when adding or changing commands, output formats, errors, file IO, environment variable handling, or provider selection.

## Rules
- Test behavior through callable functions first.
- Test `main([...])` for command parsing and exit codes.
- Use pytest-style function tests.
- Capture stdout and stderr separately with `capsys` or `capfd`.
- Use `tmp_path` for file-writing behavior.
- Use `monkeypatch` for environment variables.
- Keep tests deterministic: no network calls, real credentials, current time, or machine-specific paths unless injected.
- Add failure-path tests for missing files, invalid flags, bad formats, and unknown providers when relevant.
- Keep fixtures small and named after the behavior they support.

## Verification
- New CLI behavior has at least one success test.
- New error behavior has at least one failure test.
- File-writing commands assert both file content and terminal output.
- Name the pytest command the developer should run after applying the files.
- Do not claim that tests passed; CliSpecForge does not execute them.
