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
fenced code blocks. The format is easy to inspect and works across providers.
A block is accepted only after its closing fence is found. Model output remains
untrusted and must pass parser and path checks before any write.

## Guarded writes by default

`clispecforge build` previews a plan unless `--apply` is supplied. Targets that
exist during preflight require `--force`. Targets are resolved and checked
against the selected output directory, including through symbolic links.
Duplicate resolved targets fail the batch before any file is written. These
checks reduce accidental writes and common path escapes; they are not a
filesystem sandbox against concurrent path changes.

## Single-pass generation

Each command makes at most one model request. Execution, testing, repair loops,
conversation state, and repository automation remain the developer's job. This
boundary keeps the program small and its behavior easy to inspect.

## Explicit output limits

Anthropic and OpenAI requests use a configurable output-token limit, with a
4,096-token default. The adapters reject responses stopped by that limit rather
than passing partial output to the file parser. Raising the limit remains a
manual setting; the CLI does not retry requests.
