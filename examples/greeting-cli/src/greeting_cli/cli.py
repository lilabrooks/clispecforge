import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="greet",
        description="Print a greeting for one name.",
        allow_abbrev=False,
    )
    parser.add_argument("name", help="Name to greet.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    sys.stdout.write(f"Hello, {args.name}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
