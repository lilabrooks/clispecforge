# Design

CliSpecForge turns a Markdown CLI contract into a reviewable set of generated
files. It is a single-pass scaffold generator for small Python command-line
tools.

## Flow

`clispecforge build` runs the full path, from prompt assembly to writes:

1. Resolve and validate an optional specification.
2. Load any selected instruction skills.
3. Add the file-output contract for `clispecforge build`.
4. Send one completion request through the selected provider adapter.
5. Fail if the provider reports that the response hit the output-token limit.
6. Parse complete `FILE:` blocks from the response.
7. Reject unsafe paths and duplicate resolved targets.
8. Print the proposed targets and terminal-safe contents, or write them when
   `--apply` is present.

The default echo provider exercises prompt assembly without credentials or a
network call. Anthropic and OpenAI support is installed through optional extras.

## Offline ingestion

`clispecforge plan` and `clispecforge apply` enter the same flow at step 6 with
a response that already exists. They read it from a file or standard input,
contact no provider, and reuse the parsing, target resolution, preview, and
write functions that `build` uses. `plan` previews and reports the response
SHA-256; `apply` writes, and `--expect-sha256` refuses a response that differs
from the one previewed.

This lets an agent host own the generation while CliSpecForge keeps the parts
that must stay checked: parsing, path validation, preview, and guarded writes.
The host supplies text; it does not gain a way to bypass a check.

## Boundaries

- `cli.py` owns argument parsing, stdout, stderr, and exit codes.
- `agents/` creates provider-neutral completion requests.
- `core/` holds shared types, Markdown parsing, and generated-file handling.
- `providers/` contains vendor adapters behind the `LanguageModel` protocol.
- `specs/` and `skills/` load and validate Markdown documents.
- `runtime/` is the composition root.
- `examples/` contains a standalone output sample with its own package metadata
  and tests.

Core modules do not import providers. Provider SDK imports happen only when
their adapter receives a request.

The example package does not import CliSpecForge and is not included in its
wheel.

## Scope

The tool validates inputs, assembles context, requests one response or accepts
an existing one, previews the returned files, and applies approved writes.
Developers remain responsible for reviewing, running, and testing the generated
scaffold.

Conversation state, autonomous retries, tool execution, repository management,
Git operations, hosted execution, and IDE integration stay outside the product.
