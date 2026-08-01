# Specs

Write CLI specs as Markdown files. CliSpecForge reads them and adds their
contents to one provider request.

Recommended folders:

```text
specs/
├── cli/          # Specs for Python CLI scaffolds
└── templates/    # Reusable spec templates
```

Each spec should reduce what the model has to infer. Keep behavior, inputs,
outputs, and acceptance tests concrete. The spec guides a response; it does not
verify the returned implementation.

Run checks with:

```bash
clispecforge spec check
```
