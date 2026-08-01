"""Parse and write files from an agent response following the file-output
contract (see `skills/agent/file-output-contract.md`): a `FILE: <path>` line
followed by one fenced code block holding that file's complete contents.
"""

from dataclasses import dataclass
from pathlib import Path

_FILE_MARKER_PREFIX = "FILE:"
_FENCE_PREFIX = "```"


@dataclass(frozen=True, slots=True)
class GeneratedFile:
    path: str
    content: str


def parse_generated_files(text: str) -> list[GeneratedFile]:
    lines = text.splitlines()
    files: list[GeneratedFile] = []
    index = 0

    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped.startswith(_FILE_MARKER_PREFIX):
            index += 1
            continue

        path = stripped.removeprefix(_FILE_MARKER_PREFIX).strip()
        index += 1
        while index < len(lines) and not lines[index].strip():
            index += 1

        if index >= len(lines) or not lines[index].strip().startswith(_FENCE_PREFIX):
            continue  # no fenced block follows; treat the marker as prose

        index += 1  # skip the opening fence
        content_lines: list[str] = []
        while index < len(lines) and lines[index].strip() != _FENCE_PREFIX:
            content_lines.append(lines[index])
            index += 1
        if index >= len(lines):
            continue  # an incomplete block is not a complete generated file
        index += 1  # skip the closing fence

        if path:
            files.append(GeneratedFile(path=path, content="\n".join(content_lines)))

    return files


def resolve_target_path(out_dir: Path, generated: GeneratedFile) -> Path:
    relative = Path(generated.path)
    if not generated.path.strip() or relative.is_absolute() or ".." in relative.parts:
        msg = f"Unsafe or invalid file path in agent output: {generated.path!r}"
        raise ValueError(msg)

    target = out_dir / relative
    if not target.resolve(strict=False).is_relative_to(out_dir.resolve(strict=False)):
        msg = f"Unsafe or invalid file path in agent output: {generated.path!r}"
        raise ValueError(msg)
    return target


def write_generated_files(
    files: list[GeneratedFile],
    targets: list[Path],
    *,
    force: bool = False,
) -> None:
    seen: set[Path] = set()
    duplicates: list[Path] = []
    for target in targets:
        resolved = target.resolve(strict=False)
        if resolved in seen and resolved not in duplicates:
            duplicates.append(resolved)
        seen.add(resolved)
    if duplicates:
        joined = ", ".join(str(path) for path in duplicates)
        msg = f"Duplicate generated file target(s): {joined}"
        raise ValueError(msg)

    if not force:
        existing = [target for target in targets if target.exists()]
        if existing:
            joined = ", ".join(str(path) for path in existing)
            msg = f"Refusing to overwrite existing file(s) without --force: {joined}"
            raise FileExistsError(msg)

    for generated, target in zip(files, targets, strict=True):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"{generated.content}\n", encoding="utf-8")
