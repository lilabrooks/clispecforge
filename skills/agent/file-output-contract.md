---
source: internal
owner: Lila Brooks
deciders: [Lila Brooks]
---
# File output contract

## Purpose
Define the exact reply format for tasks that create or change files, so `clispecforge build` can parse the response and write real files to disk.

## When to use
Use this whenever the task asks you to implement, generate, scaffold, or otherwise produce files, not just to explain, review, or describe something.

## Rules
- For every file you create or change, emit a line containing only `FILE: <relative/path>`.
- Paths are relative to the project root. Never emit an absolute path or a path containing `..`.
- Immediately after the `FILE:` line, emit exactly one fenced code block with the file's complete contents. Do not truncate, and do not use `...` or "rest unchanged" placeholders.
- Use an opening fence of at least three backticks and close it with exactly the same number of backticks. The outer fence must be longer than every run of backticks inside the file. For example, wrap a Markdown file containing triple-backtick examples in four backticks.
- Add a language tag on the opening fence when one applies (for example ` ```python `); a bare ` ``` ` is fine otherwise.
- Emit one `FILE:` line and one fenced block per file. Do not combine multiple files into a single fenced block.
- Keep explanatory prose outside the fenced blocks, either before the first `FILE:` line or after the last fenced block.
- If the task does not require writing files, skip this format and answer normally.

## Verification
- Every fenced code block that represents a file is immediately preceded by a `FILE:` line naming its path.
- No `FILE:` path is absolute or contains `..`.
- Each fenced block contains the complete file content, not a diff, excerpt, or placeholder.
- Each closing fence has exactly the same number of backticks as its opening fence.
