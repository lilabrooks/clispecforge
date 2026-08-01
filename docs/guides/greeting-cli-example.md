# Greeting CLI example

The repository includes one small standalone example under
[`examples/greeting-cli/`](../../examples/greeting-cli/). It corresponds to the
bundled [`example` spec](../../specs/cli/example.md) and stays separate from the
CliSpecForge package.

Validate the source spec:

```bash
clispecforge spec check example
```

Run the example tests from the repository root:

```bash
python -m pytest examples/greeting-cli/tests
```

Build its wheel and source archive:

```bash
python -m build examples/greeting-cli
```

Install it independently with pipx:

```bash
pipx install examples/greeting-cli
greet Lila
```

Expected output:

```text
Hello, Lila
```

The example uses only Python's standard library. Installing it does not install
or import CliSpecForge.
