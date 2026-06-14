"""Manifest loader for NHANES AutoAnalyst v0.2 data builds."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .nhanes_data import XptRequest, file_code_from_stem


def load_manifest(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if "cycles" not in data or not data["cycles"]:
        raise ValueError("Manifest must define non-empty 'cycles'.")
    if "files" not in data or not data["files"]:
        raise ValueError("Manifest must define non-empty 'files'.")
    return data


def requests_from_manifest(manifest: dict[str, Any]) -> dict[str, list[XptRequest]]:
    out: dict[str, list[XptRequest]] = {}
    files = manifest["files"]
    for cycle in manifest["cycles"]:
        reqs: list[XptRequest] = []
        for item in files:
            if isinstance(item, str):
                reqs.append(XptRequest(cycle=cycle, file_code=file_code_from_stem(item, cycle)))
            else:
                stem = item.get("stem") or item.get("file_code")
                if not stem:
                    raise ValueError(f"Bad file entry: {item!r}")
                explicit = item.get("file_code")
                code = explicit if explicit else file_code_from_stem(stem, cycle)
                reqs.append(XptRequest(cycle=cycle, file_code=code, component=item.get("component")))
        out[cycle] = reqs
    return out


def column_map_from_manifest(manifest: dict[str, Any]) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for item in manifest.get("files", []):
        if isinstance(item, str):
            continue
        cols = item.get("columns")
        code = item.get("file_code") or item.get("stem")
        if cols and code:
            mapping[str(code).upper()] = [str(c).upper() for c in cols]
    return mapping
