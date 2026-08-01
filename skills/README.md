# Request skills

Skills are Markdown instructions attached to one provider request. They can
shape the proposed files and tests. They do not give CliSpecForge an execution
loop or establish that the response builds, installs, or passes its tests.

Use them with CLI specs:

```bash
clispecforge run --spec example --skill focused-implementation --skill stdlib-cli-ux "Implement this feature"
```

Recommended folders:

```text
skills/
├── agent/        # Skills attached to a provider request
└── templates/    # Reusable skill templates
```

These skills are inspired by `multica-ai/andrej-karpathy-skills`, adapted for this vendor-neutral Python CLI project. The sources checked when writing them are recorded in [docs/notes/skill-research.md](../docs/notes/skill-research.md).

## Skill selection

- `think-before-coding`: use when a spec is ambiguous or incomplete.
- `goal-driven-execution`: use to translate a spec into observable success criteria.
- `focused-implementation`: use for most code changes to keep scope tight.
- `stdlib-cli-ux`: use when commands, flags, help text, output, or errors change.
- `cli-test-coverage`: use when CLI behavior needs tests.
- `python-code-quality`: use when Python source changes.
- `python-packaging-cli`: use when packaging, dependencies, entry points, or install docs change.

Common stack for requesting a fuller CLI scaffold:

```bash
clispecforge run --spec example --skill goal-driven-execution --skill focused-implementation --skill stdlib-cli-ux --skill cli-test-coverage "Implement this feature"
```
