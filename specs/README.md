# Specs

Write CLI specs as Markdown files. The Python app reads these files and turns them into agent context.

Recommended folders:

```text
specs/
├── cli/          # Specs for CLI features Python should build
└── templates/    # Reusable spec templates
```

Each spec should be specific enough that an agent can implement the CLI without guessing. Keep behavior, inputs, outputs, and acceptance tests concrete.

Run checks with:

```bash
clispecforge spec check
```
