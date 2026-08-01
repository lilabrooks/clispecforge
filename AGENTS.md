# Repository instructions

## Purpose

This repository contains a small, single-pass Python CLI scaffold generator.
It validates Markdown specifications, adds optional instruction skills, sends
one request to a selected model provider, previews the returned file plan, and
writes approved files.

## Scope

- Keep the tool understandable and dependency-light.
- Preserve the one-request workflow. Conversation state, autonomous repair,
  tool execution, repository orchestration, and Git automation stay outside the
  product.
- Treat model output as untrusted input. Generated paths and overwrite behavior
  are security-sensitive.
- Keep required runtime dependencies empty. Provider SDKs remain optional
  extras with deferred imports.

Read `docs/design.md` before changing architecture or public behavior. Read
`docs/decisions.md` before changing dependencies, provider boundaries, the
file-output contract, or write safety.

## Working rules

- Preserve unrelated user changes.
- Update tests and user-facing documentation with behavior changes.
- Never read `.env` files or commit credentials.
- Do not publish, release, push, or create tags without explicit instruction.
- Keep changes focused. Add abstractions only when current behavior requires
  them.

## Verification

- Everyday gate: `make check`
- Coverage: `make coverage`
- All supported Pythons, 3.12 through 3.14: `make check-all`
- Package smoke test for packaging changes: build a wheel, install it in a
  fresh environment, and run `clispecforge providers` outside the checkout.
