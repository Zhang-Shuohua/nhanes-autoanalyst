# v0.2 data pipeline

This patch adds the first deterministic NHANES public-use data layer:

1. Build official CDC/NCHS XPT URLs.
2. Download and cache XPT files locally.
3. Read XPT files with `pandas.read_sas(..., format="xport")`.
4. Merge files within one cycle by `SEQN`.
5. Append multiple cycles and add `survey_cycle`.
6. Export a missingness report.

## Commands

```bash
pip install -e .[dev]

nhanes-auto download-xpt 2015-2016 DEMO --cache-dir data/raw/nhanes
nhanes-auto inspect-xpt data/raw/nhanes/2015_2016__DEMO_I.XPT

nhanes-auto build-dataset examples/v02_minimal_manifest.yaml \
  --cache-dir data/raw/nhanes \
  --out outputs/v02_minimal_nhanes.csv
```

## Design notes

- `SEQN` is required for merges.
- Duplicate `SEQN` values fail fast because NHANES component merges should be one-to-one at participant level.
- Overlapping non-`SEQN` columns are preserved with suffixes instead of silently overwritten.
- The package does not redistribute NHANES data. It downloads public-use files from CDC/NCHS.
