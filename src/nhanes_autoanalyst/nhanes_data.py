"""Download, read, merge, and append NHANES public-use XPT files.

This module is intentionally deterministic and conservative:
- it only targets public-use CDC/NCHS XPT URLs;
- it never redistributes downloaded data;
- it preserves SEQN as the required merge key;
- it adds survey_cycle metadata when appending cycles.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence
import hashlib
import re

import pandas as pd
import requests

CDC_NHANES_BASE_URL = "https://wwwn.cdc.gov/Nchs/Nhanes"
SEQN = "SEQN"

# Continuous NHANES public-use cycles. File suffixes are not fully uniform across
# every historical component, so callers may still pass explicit file_code.
CYCLE_SUFFIX: dict[str, str] = {
    "1999-2000": "",
    "2001-2002": "_B",
    "2003-2004": "_C",
    "2005-2006": "_D",
    "2007-2008": "_E",
    "2009-2010": "_F",
    "2011-2012": "_G",
    "2013-2014": "_H",
    "2015-2016": "_I",
    "2017-2018": "_J",
    "2017-March 2020 Pre-pandemic": "_P",
    "2021-2023": "_L",
}


class NhanesDataError(RuntimeError):
    """Raised when NHANES data operations fail with actionable context."""


@dataclass(frozen=True)
class XptRequest:
    """A single NHANES XPT file request."""

    cycle: str
    file_code: str
    component: str | None = None

    @property
    def normalized_file_code(self) -> str:
        code = self.file_code.strip().upper()
        if code.endswith(".XPT"):
            code = code[:-4]
        return code

    @property
    def url(self) -> str:
        return build_xpt_url(self.cycle, self.normalized_file_code)

    @property
    def cache_name(self) -> str:
        safe_cycle = re.sub(r"[^0-9A-Za-z]+", "_", self.cycle).strip("_")
        return f"{safe_cycle}__{self.normalized_file_code}.XPT"


def file_code_from_stem(stem: str, cycle: str) -> str:
    """Build a cycle-aware NHANES file code from a base stem.

    Examples
    --------
    >>> file_code_from_stem("DEMO", "2015-2016")
    'DEMO_I'
    >>> file_code_from_stem("DEMO_I", "2015-2016")
    'DEMO_I'
    """
    stem = stem.strip().upper().removesuffix(".XPT")
    suffix = CYCLE_SUFFIX.get(cycle)
    if suffix is None:
        raise NhanesDataError(
            f"Unsupported or misspelled cycle: {cycle!r}. "
            f"Known cycles: {', '.join(CYCLE_SUFFIX)}"
        )
    if suffix and stem.endswith(suffix):
        return stem
    if not suffix:
        return stem
    return f"{stem}{suffix}"


def build_xpt_url(cycle: str, file_code: str, base_url: str = CDC_NHANES_BASE_URL) -> str:
    """Return the official CDC/NCHS public-use XPT URL."""
    code = file_code.strip().upper().removesuffix(".XPT")
    return f"{base_url.rstrip('/')}/{cycle}/{code}.XPT"


def cache_path_for(request: XptRequest, cache_dir: str | Path = "data/raw/nhanes") -> Path:
    return Path(cache_dir) / request.cache_name


def download_xpt(
    request: XptRequest,
    cache_dir: str | Path = "data/raw/nhanes",
    *,
    overwrite: bool = False,
    timeout: int = 60,
) -> Path:
    """Download one NHANES XPT file to the local cache and return its path."""
    out = cache_path_for(request, cache_dir)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and not overwrite and out.stat().st_size > 0:
        return out

    response = requests.get(request.url, timeout=timeout)
    if response.status_code == 404:
        raise NhanesDataError(
            f"NHANES file not found: {request.url}. Check cycle/file_code."
        )
    response.raise_for_status()
    content = response.content
    if len(content) < 128:
        raise NhanesDataError(f"Downloaded file is unexpectedly small: {request.url}")
    out.write_bytes(content)
    return out


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_xpt(path: str | Path, *, columns: Sequence[str] | None = None) -> pd.DataFrame:
    """Read a SAS transport XPT file into a pandas DataFrame."""
    df = pd.read_sas(path, format="xport")
    df.columns = [str(c).upper() for c in df.columns]
    if columns is not None:
        requested = [c.upper() for c in columns]
        missing = sorted(set(requested) - set(df.columns))
        if missing:
            raise NhanesDataError(f"Missing requested columns in {path}: {missing}")
        df = df.loc[:, requested]
    if SEQN in df.columns:
        df[SEQN] = pd.to_numeric(df[SEQN], errors="raise").astype("Int64")
    return df


def require_seqn(df: pd.DataFrame, label: str = "dataframe") -> None:
    if SEQN not in df.columns:
        raise NhanesDataError(f"{label} has no {SEQN}; cannot merge NHANES components.")
    if df[SEQN].duplicated().any():
        n = int(df[SEQN].duplicated().sum())
        raise NhanesDataError(f"{label} has {n} duplicated {SEQN} values.")


def merge_on_seqn(frames: Mapping[str, pd.DataFrame], *, how: str = "outer") -> pd.DataFrame:
    """Merge component-level files within one NHANES cycle by SEQN."""
    if not frames:
        raise NhanesDataError("No frames supplied for merge.")
    items = list(frames.items())
    first_label, merged = items[0]
    require_seqn(merged, first_label)
    merged = merged.copy()
    for label, right in items[1:]:
        require_seqn(right, label)
        overlap = sorted((set(merged.columns) & set(right.columns)) - {SEQN})
        if overlap:
            right = right.rename(columns={c: f"{c}__{label}" for c in overlap})
        merged = merged.merge(right, on=SEQN, how=how, validate="one_to_one")
    return merged


def append_cycles(frames: Mapping[str, pd.DataFrame]) -> pd.DataFrame:
    """Append cycle-level analytic datasets and add survey_cycle."""
    if not frames:
        raise NhanesDataError("No cycle frames supplied for append.")
    out: list[pd.DataFrame] = []
    for cycle, df in frames.items():
        if SEQN not in df.columns:
            raise NhanesDataError(f"Cycle {cycle} has no {SEQN}.")
        tmp = df.copy()
        tmp.insert(0, "survey_cycle", cycle)
        out.append(tmp)
    return pd.concat(out, ignore_index=True, sort=False)


def missingness_report(df: pd.DataFrame) -> pd.DataFrame:
    """Return a compact missingness report for any analytic table."""
    n = len(df)
    miss = df.isna().sum().rename("n_missing").to_frame()
    miss["pct_missing"] = (miss["n_missing"] / n * 100).round(2) if n else 0
    miss.insert(0, "variable", miss.index)
    return miss.reset_index(drop=True)


def build_cycle_dataset(
    requests_for_cycle: Iterable[XptRequest],
    *,
    cache_dir: str | Path = "data/raw/nhanes",
    columns: Mapping[str, Sequence[str]] | None = None,
    overwrite: bool = False,
    how: str = "outer",
) -> pd.DataFrame:
    """Download/read/merge all requested files for one NHANES cycle."""
    frames: dict[str, pd.DataFrame] = {}
    for req in requests_for_cycle:
        path = download_xpt(req, cache_dir=cache_dir, overwrite=overwrite)
        cols = None
        if columns and req.normalized_file_code in columns:
            raw_cols = [SEQN, *columns[req.normalized_file_code]]
            cols = list(dict.fromkeys(c.upper() for c in raw_cols))
        frames[req.normalized_file_code] = read_xpt(path, columns=cols)
    return merge_on_seqn(frames, how=how)
