"""CLI commands for NHANES public-use XPT data operations."""

from __future__ import annotations

import argparse
from pathlib import Path

from .manifest import column_map_from_manifest, load_manifest, requests_from_manifest
from .nhanes_data import (
    XptRequest,
    append_cycles,
    build_cycle_dataset,
    download_xpt,
    file_code_from_stem,
    missingness_report,
    read_xpt,
)


def add_data_subcommands(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("download-xpt", help="Download a CDC/NCHS NHANES public-use XPT file")
    p.add_argument("cycle", help="Example: 2015-2016")
    p.add_argument("file", help="File stem or code, e.g. DEMO or DEMO_I")
    p.add_argument("--cache-dir", default="data/raw/nhanes")
    p.add_argument("--overwrite", action="store_true")
    p.set_defaults(func=cmd_download_xpt)

    p = subparsers.add_parser("inspect-xpt", help="Inspect a cached/local XPT file")
    p.add_argument("path")
    p.add_argument("--head", type=int, default=5)
    p.set_defaults(func=cmd_inspect_xpt)

    p = subparsers.add_parser("build-dataset", help="Build merged/appended NHANES dataset from YAML manifest")
    p.add_argument("manifest")
    p.add_argument("--cache-dir", default="data/raw/nhanes")
    p.add_argument("--out", default="outputs/nhanes_dataset.csv")
    p.add_argument("--missingness-out", default=None)
    p.add_argument("--overwrite", action="store_true")
    p.set_defaults(func=cmd_build_dataset)


def cmd_download_xpt(args: argparse.Namespace) -> None:
    code = file_code_from_stem(args.file, args.cycle) if "_" not in args.file else args.file
    req = XptRequest(cycle=args.cycle, file_code=code)
    path = download_xpt(req, cache_dir=args.cache_dir, overwrite=args.overwrite)
    print(f"Downloaded/cached: {path}")
    print(f"URL: {req.url}")


def cmd_inspect_xpt(args: argparse.Namespace) -> None:
    df = read_xpt(args.path)
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")
    print(", ".join(df.columns[:80]))
    print(df.head(args.head).to_string(index=False))


def cmd_build_dataset(args: argparse.Namespace) -> None:
    manifest = load_manifest(args.manifest)
    reqs_by_cycle = requests_from_manifest(manifest)
    colmap = column_map_from_manifest(manifest)

    cycle_frames = {}
    for cycle, reqs in reqs_by_cycle.items():
        print(f"Building cycle {cycle} with {len(reqs)} XPT files...")
        cycle_frames[cycle] = build_cycle_dataset(
            reqs,
            cache_dir=args.cache_dir,
            columns=colmap,
            overwrite=args.overwrite,
        )
    dataset = append_cycles(cycle_frames)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(out, index=False)
    print(f"Saved dataset: {out} ({len(dataset):,} rows, {len(dataset.columns):,} columns)")

    miss_out = Path(args.missingness_out) if args.missingness_out else out.with_name(out.stem + "_missingness.csv")
    missingness_report(dataset).to_csv(miss_out, index=False)
    print(f"Saved missingness report: {miss_out}")
