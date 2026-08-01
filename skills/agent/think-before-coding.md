---
source: https://github.com/multica-ai/andrej-karpathy-skills
owner: Lila Brooks
deciders: [Lila Brooks]
---
# Think before coding

## Purpose
Prevent the agent from making hidden assumptions while turning a Markdown CLI spec into Python code.

## When to use
Use this when a spec is incomplete, ambiguous, internally inconsistent, or has more than one reasonable implementation path.

## Rules
- State assumptions before editing code.
- If a command, flag, input file, output format, or error behavior is unclear, ask for clarification.
- If there are multiple reasonable interpretations, list the choices and their tradeoffs.
- Push back when the requested design is heavier than the current problem needs.
- Keep uncertainty visible in the agent response.

## Verification
- The proposed files trace back to explicit spec text or named assumptions.
- Ambiguous requirements are clarified before code changes.
- The response names unresolved risks instead of pretending they are solved.
