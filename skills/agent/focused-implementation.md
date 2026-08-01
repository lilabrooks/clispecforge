---
source: https://github.com/multica-ai/andrej-karpathy-skills
owner: Lila Brooks
deciders: [Lila Brooks]
---
# Focused implementation

## Purpose
Keep generated Python CLI changes small, readable, and limited to the requested spec.

## When to use
Use this whenever implementing or changing Python files, tests, docs, specs, or provider adapters.

## Rules
- Build only what the current spec asks for.
- Touch only files needed for the requested CLI behavior.
- Prefer one clear function over a new abstraction when the code has one use.
- Delay configuration, plugins, registries, caching, and extensibility until a spec requires them.
- Match the current project style.
- Leave unrelated formatting, comments, names, and structure alone.
- Mention unrelated issues instead of fixing them during the current change.
- Remove imports, variables, functions, and files made unused by the current change.

## Verification
- Every changed line supports the requested spec or its tests.
- The change has no speculative features.
- New helpers have more than one real caller or make the code easier to read now.
- The diff contains no drive-by refactors.
- Identify the existing tests the developer should rerun after applying the files.
- Do not claim that tests passed; CliSpecForge does not execute them.
