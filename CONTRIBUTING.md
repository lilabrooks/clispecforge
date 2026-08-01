# Contributing

CliSpecForge is intentionally small. Changes should preserve the single-pass
workflow and keep required runtime dependencies empty.

## Setup

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,anthropic,openai]"
```

Python 3.12 through 3.14 is supported.

## Before submitting a change

Run the everyday gate:

```bash
make check
```

The everyday gate includes the enforced branch-coverage floor. Packaging
changes also need a wheel build and a fresh-environment smoke test from outside
the checkout. Changes under `examples/greeting-cli/` also require its
independent build and `greet Lila` smoke test.

Keep tests focused on observable behavior. Use `tmp_path`, `capsys`, and
`monkeypatch` for filesystem, terminal, and provider boundaries.

## Design constraints

- `cli.py` owns terminal parsing and output.
- `core/` owns provider-neutral types, Markdown parsing, and file handling.
- `providers/` maps the core request and response types to vendor SDKs.
- `runtime/` wires settings, providers, and the agent together.
- Provider SDK imports stay deferred so the echo workflow needs only Python.
- Generated paths and overwrite behavior are security-sensitive.

See [docs/design.md](docs/design.md) for the full flow and
[docs/decisions.md](docs/decisions.md) for the binding design choices.
