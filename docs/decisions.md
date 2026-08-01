# Design decisions

These choices define the intended shape of CliSpecForge.

## One provider protocol

Application code depends on a one-method `LanguageModel` protocol. Anthropic,
OpenAI, and echo implementations live behind a registry. This keeps prompt
assembly and file handling independent from vendor SDK types.

## One public name

The distribution and installed executable are both named `clispecforge`. The
standalone example has its own package metadata and console script without
adding another command to the CliSpecForge wheel. The internal `agent_cli`
import package remains unchanged; it is an implementation detail and renaming
it would not improve the command-line workflow.

## No required runtime dependencies

The base package uses the Python standard library. Provider SDKs are opt-in
extras and are imported only when selected. The credential-free echo path
continues to work with a base installation.

## Plain-text file output

`clispecforge build` asks providers for `FILE: relative/path` markers followed by
fenced code blocks. Opening and closing fences must use the same number of
backticks, with a three-backtick minimum. Longer outer fences allow Markdown
files to contain ordinary fenced examples without truncation. The format is
easy to inspect and works across providers. A block is accepted only after its
matching closing fence is found. Model output remains untrusted and must pass
parser and path checks before any write.

## Guarded writes by default

`clispecforge build` previews a plan and terminal-safe file contents unless
`--apply` is supplied. Control and formatting characters are escaped in the
preview so model output cannot send them directly to the terminal. Targets that
exist during preflight require `--force`. Targets are resolved and checked
against the selected output directory, including through symbolic links.
Duplicate resolved targets fail the batch before any file is written. These
checks reduce accidental writes and common path escapes; they are not a
filesystem sandbox against concurrent path changes.

## Generation is separable from the file handoff

`plan` and `apply` consume a response that already exists, so an agent host can
supply the generation while CliSpecForge still owns parsing, path validation,
preview, and guarded writes. They reuse `build`'s functions rather than
reimplementing them, which is what keeps the two entry points honest: a
response that `plan` rejects is a response `build` would also reject.

`plan` reports the SHA-256 of the decoded response text, and `apply
--expect-sha256` refuses anything else. That turns "the approved response is
the applied response" into a check instead of an assumption, which matters when
a host writes the response to a temporary file that something else could touch
between approval and write. The digest covers the response, not the files it
produces, and it is an integrity check against drift and mistakes rather than
an authenticity guarantee.

`plan` also rejects duplicate resolved targets, which `build`'s preview leaves
to write time. Approval is the point of `plan`, so it should not present a plan
that `apply` would refuse.

## Single-pass generation

Each command makes at most one model request. Execution, testing, repair loops,
conversation state, and repository automation remain the developer's job. This
boundary keeps the program small and its behavior easy to inspect.

## Explicit output limits

Anthropic and OpenAI requests use a configurable output-token limit, with a
4,096-token default. The adapters reject responses stopped by that limit rather
than passing partial output to the file parser. Raising the limit remains a
manual setting; the CLI does not retry requests.
