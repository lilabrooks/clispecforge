---
source: https://github.com/multica-ai/andrej-karpathy-skills
owner: Lila Brooks
deciders: [Lila Brooks]
---
# Goal-driven execution

## Purpose
Convert a CLI spec into observable implementation goals for a single response.

## When to use
Use this for multi-step CLI work, bug fixes, validation rules, and any change that needs tests.

## Rules
- Define success criteria before implementation.
- Turn vague requests into observable behavior, such as stdout, stderr, exit code, files written, or tests passing.
- Map each proposed file to a success criterion from the spec.
- Include a regression test when the request describes a reproducible bug.
- State any blocker or assumption in the response instead of inventing missing details.
- Keep the response single-pass. Do not imply that commands or repair loops ran.

## Verification
- The proposed files include tests for the behavior in the spec.
- The response names the commands the developer should run after applying the files.
- No check is reported as passed unless its result was supplied in the prompt.
