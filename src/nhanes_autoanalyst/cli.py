"""NHANES AutoAnalyst command line interface.

If your existing repository already has cli.py, merge the add_data_subcommands()
call into its parser instead of replacing project-specific commands.
"""

from __future__ import annotations

import argparse

from .cli_data import add_data_subcommands


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nhanes-auto")
    subparsers = parser.add_subparsers(dest="command", required=True)
    add_data_subcommands(subparsers)
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
