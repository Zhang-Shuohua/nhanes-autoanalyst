# NHANES AutoAnalyst v0.2 patch

Copy these folders/files into the repository root:

- `src/nhanes_autoanalyst/nhanes_data.py`
- `src/nhanes_autoanalyst/manifest.py`
- `src/nhanes_autoanalyst/cli_data.py`
- merge `src/nhanes_autoanalyst/cli.py` if your existing CLI already has v0.1 commands
- `examples/v02_minimal_manifest.yaml`
- `tests/test_nhanes_data.py`
- `docs/v02_data_pipeline.md`

Then run:

```bash
pip install -e .[dev]
pytest
nhanes-auto download-xpt 2015-2016 DEMO
nhanes-auto build-dataset examples/v02_minimal_manifest.yaml --out outputs/v02_minimal_nhanes.csv
```

Recommended git workflow:

```bash
git checkout -b feat/v0.2-nhanes-xpt-pipeline
# copy files from this patch into repo
git add src examples tests docs
git commit -m "feat: add NHANES public-use XPT data pipeline"
git push origin feat/v0.2-nhanes-xpt-pipeline
```
