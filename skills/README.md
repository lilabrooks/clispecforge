# Agent skills

Agent skills are Markdown instructions that shape how the agent works while it builds CLI features from specs.

Use them with CLI specs:

```bash
clispecforge run --spec example --skill focused-implementation --skill stdlib-cli-ux "Implement this feature"
```

Recommended folders:

```text
skills/
├── agent/        # Skills an agent can attach to a run
└── templates/    # Reusable skill templates
```

These skills are inspired by `multica-ai/andrej-karpathy-skills`, adapted for this vendor-neutral Python CLI project. The sources checked when writing them are recorded in [docs/notes/skill-research.md](../docs/notes/skill-research.md).

## Skill selection

- `think-before-coding`: use when a spec is ambiguous or incomplete.
- `goal-driven-execution`: use for multi-step work that needs a verification loop.
- `focused-implementation`: use for most code changes to keep scope tight.
- `stdlib-cli-ux`: use when commands, flags, help text, output, or errors change.
- `cli-test-coverage`: use when CLI behavior needs tests.
- `python-code-quality`: use when Python source changes.
- `python-packaging-cli`: use when packaging, dependencies, entry points, or install docs change.

Common stack for implementing a CLI feature:

```bash
clispecforge run --spec example --skill goal-driven-execution --skill focused-implementation --skill stdlib-cli-ux --skill cli-test-coverage "Implement this feature"
```
