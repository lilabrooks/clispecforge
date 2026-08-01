# Greeting CLI example

This standalone package is a compact example of the files described by
[`specs/cli/example.md`](../../specs/cli/example.md). It has no dependency on
CliSpecForge and is not included in the `clispecforge` wheel.

Run its tests from the repository root:

```bash
python -m pytest examples/greeting-cli/tests
```

Build and install it independently:

```bash
python -m build examples/greeting-cli
pipx install examples/greeting-cli
greet Lila
```

Expected output:

```text
Hello, Lila
```
