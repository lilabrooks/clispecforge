import argparse
import sys
from pathlib import Path

from agent_cli.config.settings import ConfigurationError, Settings
from agent_cli.core.fileset import (
    GeneratedFile,
    parse_generated_files,
    resolve_target_path,
    write_generated_files,
)
from agent_cli.core.models import ResponseTruncatedError
from agent_cli.core.parser import FriendlyArgumentParser
from agent_cli.providers.registry import available_providers
from agent_cli.resources import default_skill_root, default_spec_root
from agent_cli.runtime.factory import build_agent
from agent_cli.skills.loader import list_skills, load_skill, resolve_skill, validate_skill
from agent_cli.specs.loader import list_specs, load_spec, resolve_spec, validate_spec

FILE_OUTPUT_CONTRACT_SKILL = "file-output-contract"


class SpecValidationError(ValueError):
    """Raised when `clispecforge build --strict` finds spec validation errors."""


def _validate_spec_or_raise(spec_path: Path, *, strict: bool) -> None:
    result = validate_spec(load_spec(spec_path))
    if not result.errors:
        return

    if strict:
        msg = f"Spec {spec_path} failed validation:\n{result.format()}"
        raise SpecValidationError(msg)

    write_stderr_line(f"Warning: spec {spec_path} has validation errors:")
    write_stderr_line(result.format())
    write_stderr_line(
        "Continuing without --strict. Run 'clispecforge spec check' for the full report."
    )


def _gather_context_blocks(
    spec: str | None,
    skills: list[str] | None,
    all_skills: bool,
) -> list[str]:
    context_blocks: list[str] = []
    if spec is not None:
        spec_path = resolve_spec(spec, default_spec_root())
        context_blocks.append(load_spec(spec_path).to_agent_context())

    skill_root = default_skill_root()
    skill_paths = list_skills(skill_root) if all_skills else []
    if all_skills and not skill_paths:
        write_stderr_line(f"Warning: --all-skills found no skills under {skill_root}.")
    skill_paths.extend(resolve_skill(skill, skill_root) for skill in skills or [])
    for skill_path in skill_paths:
        context_blocks.append(load_skill(skill_path).to_agent_context())

    return context_blocks


def run(
    prompt: str,
    provider: str | None = None,
    spec: str | None = None,
    skills: list[str] | None = None,
    all_skills: bool = False,
) -> str:
    settings = Settings.from_env(provider_override=provider)
    agent = build_agent(settings)
    context_blocks = _gather_context_blocks(spec, skills, all_skills)
    agent_prompt = "\n\n".join([*context_blocks, f"Task:\n{prompt}"]) if context_blocks else prompt
    result = agent.run(agent_prompt)
    return f"{result.agent_name}: {result.text}"


def build(  # noqa: PLR0913 (one flag per --spec/--skill/--all-skills/--strict CLI option)
    prompt: str,
    *,
    provider: str | None = None,
    spec: str | None = None,
    skills: list[str] | None = None,
    all_skills: bool = False,
    strict: bool = False,
) -> tuple[str, list[GeneratedFile]]:
    """Run the agent with the file-output contract attached, then parse the reply."""
    if spec is not None:
        _validate_spec_or_raise(resolve_spec(spec, default_spec_root()), strict=strict)

    settings = Settings.from_env(provider_override=provider)
    agent = build_agent(settings)
    context_blocks = _gather_context_blocks(spec, skills, all_skills)

    contract_path = resolve_skill(FILE_OUTPUT_CONTRACT_SKILL, default_skill_root())
    context_blocks.append(load_skill(contract_path).to_agent_context())

    agent_prompt = "\n\n".join([*context_blocks, f"Task:\n{prompt}"])
    result = agent.run(agent_prompt)
    return result.text, parse_generated_files(result.text)


def build_parser() -> argparse.ArgumentParser:
    parser = FriendlyArgumentParser(
        prog="clispecforge",
        description="Generate reviewable Python CLI scaffolds from Markdown specifications.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        allow_abbrev=False,
    )
    parser.suggest_on_error = True  # type: ignore[attr-defined]
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        parser_class=FriendlyArgumentParser,
    )

    run_parser = subparsers.add_parser("run", help="Run one prompt through the configured agent.")
    run_parser.add_argument("prompt", help="Task or question for the agent.")
    run_parser.add_argument("--provider", "-p", help="Provider adapter to use.")
    run_parser.add_argument("--spec", help="Markdown CLI spec to attach to the agent prompt.")
    skill_modes = run_parser.add_mutually_exclusive_group()
    skill_modes.add_argument(
        "--skill",
        action="append",
        default=[],
        help="Markdown agent skill to attach. Repeat for multiple skills.",
    )
    skill_modes.add_argument(
        "--all-skills",
        action="store_true",
        help="Attach every Markdown agent skill from the default skill root.",
    )

    spec_parser = subparsers.add_parser("spec", help="Work with Markdown CLI specs.")
    spec_subparsers = spec_parser.add_subparsers(
        dest="spec_command",
        required=True,
        parser_class=FriendlyArgumentParser,
    )

    spec_list_parser = spec_subparsers.add_parser("list", help="List available CLI specs.")
    spec_list_parser.add_argument(
        "--root", default=str(default_spec_root()), help="Spec root folder."
    )

    spec_show_parser = spec_subparsers.add_parser(
        "show",
        help="Print the agent-ready context for a spec.",
    )
    spec_show_parser.add_argument("spec", help="Spec path or slug.")
    spec_show_parser.add_argument(
        "--root", default=str(default_spec_root()), help="Spec root folder."
    )

    spec_check_parser = spec_subparsers.add_parser("check", help="Validate one spec or all specs.")
    spec_check_parser.add_argument("spec", nargs="?", help="Spec path or slug.")
    spec_check_parser.add_argument(
        "--root", default=str(default_spec_root()), help="Spec root folder."
    )

    skill_parser = subparsers.add_parser("skill", help="Work with Markdown agent skills.")
    skill_subparsers = skill_parser.add_subparsers(
        dest="skill_command",
        required=True,
        parser_class=FriendlyArgumentParser,
    )

    skill_list_parser = skill_subparsers.add_parser("list", help="List available agent skills.")
    skill_list_parser.add_argument(
        "--root", default=str(default_skill_root()), help="Skill root folder."
    )

    skill_show_parser = skill_subparsers.add_parser(
        "show",
        help="Print the agent-ready context for a skill.",
    )
    skill_show_parser.add_argument("skill", help="Skill path or slug.")
    skill_show_parser.add_argument(
        "--root", default=str(default_skill_root()), help="Skill root folder."
    )

    skill_check_parser = skill_subparsers.add_parser(
        "check",
        help="Validate one skill or all skills.",
    )
    skill_check_parser.add_argument("skill", nargs="?", help="Skill path or slug.")
    skill_check_parser.add_argument(
        "--root", default=str(default_skill_root()), help="Skill root folder."
    )

    build_cmd_parser = subparsers.add_parser(
        "build",
        help="Run the agent under the file-output contract and write the files it returns.",
    )
    build_cmd_parser.add_argument("prompt", help="Feature or task to build.")
    build_cmd_parser.add_argument("--provider", "-p", help="Provider adapter to use.")
    build_cmd_parser.add_argument("--spec", help="Markdown CLI spec to attach to the agent prompt.")
    build_skill_modes = build_cmd_parser.add_mutually_exclusive_group()
    build_skill_modes.add_argument(
        "--skill",
        action="append",
        default=[],
        help="Markdown agent skill to attach. Repeat for multiple skills.",
    )
    build_skill_modes.add_argument(
        "--all-skills",
        action="store_true",
        help="Attach every Markdown agent skill from the default skill root.",
    )
    build_cmd_parser.add_argument(
        "--out-dir",
        default=".",
        help="Directory generated files are written under.",
    )
    build_cmd_parser.add_argument(
        "--apply",
        action="store_true",
        help="Write the generated files to disk. Without this flag, only print the plan.",
    )
    build_cmd_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files. Only takes effect together with --apply.",
    )
    build_cmd_parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Fail before calling the model if --spec has validation errors. "
            "Default is to warn on stderr and continue."
        ),
    )

    subparsers.add_parser("providers", help="Show installed provider adapters.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "run":
            write_stdout_line(
                run(
                    prompt=args.prompt,
                    provider=args.provider,
                    spec=args.spec,
                    skills=args.skill,
                    all_skills=args.all_skills,
                )
            )
            return 0

        if args.command == "build":
            return handle_build_command(args)

        if args.command == "spec":
            return handle_spec_command(args)

        if args.command == "skill":
            return handle_skill_command(args)

        if args.command == "providers":
            write_stdout_line("\n".join(available_providers()))
            return 0
    except FileNotFoundError as error:
        parser.exit(
            1,
            (
                f"Error: {error}\n"
                "Try 'clispecforge spec list' or 'clispecforge skill list' "
                "to see available files.\n"
            ),
        )
    except ConfigurationError as error:
        parser.exit(1, f"Error: {error}\n")
    except ResponseTruncatedError as error:
        parser.exit(
            1,
            f"Error: {error}\nIncrease CLISPECFORGE_MAX_TOKENS and try again.\n",
        )
    except ValueError as error:
        parser.exit(
            1,
            f"Error: {error}\nTry 'clispecforge providers' to see available providers.\n",
        )

    parser.error(f"Unknown command {args.command!r}")
    return 2


def write_stdout_line(value: object) -> None:
    sys.stdout.write(f"{value}\n")


def write_stderr_line(value: object) -> None:
    sys.stderr.write(f"{value}\n")


def handle_build_command(args: argparse.Namespace) -> int:
    try:
        text, files = build(
            prompt=args.prompt,
            provider=args.provider,
            spec=args.spec,
            skills=args.skill,
            all_skills=args.all_skills,
            strict=args.strict,
        )
    except SpecValidationError as error:
        write_stderr_line(f"Error: {error}")
        write_stderr_line(f"Try 'clispecforge spec check {args.spec}' to see the full report.")
        return 1

    if not files:
        write_stdout_line(text)
        write_stderr_line(
            "Warning: no 'FILE:' blocks found in the agent's response; nothing to write."
        )
        return 0

    out_dir = Path(args.out_dir)
    try:
        targets = [resolve_target_path(out_dir, generated) for generated in files]
    except ValueError as error:
        write_stderr_line(f"Error: {error}")
        return 1

    if not args.apply:
        write_stdout_line(f"Plan: {len(files)} file(s) under {out_dir}:")
        for target in targets:
            write_stdout_line(f"  {target}")
        write_stdout_line("Re-run with --apply to write these files.")
        return 0

    try:
        write_generated_files(files, targets, force=args.force)
    except (FileExistsError, ValueError) as error:
        write_stderr_line(f"Error: {error}")
        return 1

    for target in targets:
        write_stdout_line(f"Wrote {target}")
    return 0


def handle_spec_command(args: argparse.Namespace) -> int:
    root = Path(args.root)

    if args.spec_command == "list":
        paths = list_specs(root)
        if not paths:
            write_stdout_line(f"No specs found under {root}.")
            return 0
        for path in paths:
            write_stdout_line(path)
        return 0

    if args.spec_command == "show":
        path = resolve_spec(args.spec, root)
        write_stdout_line(load_spec(path).to_agent_context())
        return 0

    if args.spec_command == "check":
        paths = [resolve_spec(args.spec, root)] if args.spec else list_specs(root)
        if not paths:
            write_stdout_line(f"No specs found under {root}.")
            return 1

        results = [validate_spec(load_spec(path)) for path in paths]
        for result in results:
            write_stdout_line(result.format())
        return 0 if all(result.ok for result in results) else 1

    raise ValueError(f"Unknown spec command {args.spec_command!r}")


def handle_skill_command(args: argparse.Namespace) -> int:
    root = Path(args.root)

    if args.skill_command == "list":
        paths = list_skills(root)
        if not paths:
            write_stdout_line(f"No skills found under {root}.")
            return 0
        for path in paths:
            write_stdout_line(path)
        return 0

    if args.skill_command == "show":
        path = resolve_skill(args.skill, root)
        write_stdout_line(load_skill(path).to_agent_context())
        return 0

    if args.skill_command == "check":
        paths = [resolve_skill(args.skill, root)] if args.skill else list_skills(root)
        if not paths:
            write_stdout_line(f"No skills found under {root}.")
            return 1

        results = [validate_skill(load_skill(path)) for path in paths]
        for result in results:
            write_stdout_line(result.format())
        return 0 if all(result.ok for result in results) else 1

    raise ValueError(f"Unknown skill command {args.skill_command!r}")


if __name__ == "__main__":
    raise SystemExit(main())
