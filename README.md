# NHANES AutoAnalyst

**NHANES AutoAnalyst** is an early-stage, teaching-oriented open-source toolkit for reproducible analysis of **NHANES public-use data**.

中文定位：**NHANES 可复现分析与衍生变量 recipe 平台**。

It is designed for public health, clinical epidemiology, and nutrition epidemiology learners who repeatedly face the same NHANES workflow problems:

- finding the right public-use XPT files;
- merging tables by `SEQN`;
- combining survey cycles;
- documenting derived variables such as NAFLD, CKD, diabetes, hypertension, dietary scores, and exposure panels;
- checking missingness before modeling;
- preparing Table 1, survey-weighted regression, subgroup analysis, and reproducible reports.

> This project is **not** an automatic paper-writing tool. It is a reproducible workflow scaffold. The researcher must still define the research question, exposure, outcome, covariates, inclusion/exclusion criteria, and interpretation.

## Current status

`v0.1-alpha` is a project scaffold and teaching MVP. It can:

- load a study YAML configuration;
- normalize common user aliases such as `covariate` -> `covariates`, `gender` -> `sex`;
- validate recipe names with fuzzy suggestions;
- read a local recipe registry;
- generate an analysis plan, variable dictionary, and derivation report;
- run a small synthetic demo for missingness reporting;
- provide documentation for a NAFLD + dietary pattern example inspired by a real undergraduate thesis workflow.

It does **not yet** guarantee validated reproduction of HEI/DASH/MED/DII/USFLI calculations across all NHANES cycles. These recipes are currently documented and structured for future validation.

## Why recipe-based?

NHANES raw files do not directly provide many research variables. A user may need to derive:

- `NAFLD` from `USFLI >= 30`;
- `CKD` from eGFR and albuminuria;
- `hypertension` from BP measurements and medication questionnaire;
- `HEI`, `DASH`, `MED`, `DII` from dietary variables;
- smoking, alcohol, physical activity, and metabolic status from questionnaire and lab files.

This project treats those derived variables as **recipes**: transparent, versioned, inspectable files that describe inputs, formulas, exclusions, outputs, and citations.

## Quickstart

```bash
pip install -e .[dev]

# Check a study configuration
nhanes-auto check examples/nafld_diet_analysis.yaml

# Generate a reproducible analysis plan and derivation report
nhanes-auto plan examples/nafld_diet_analysis.yaml --outdir outputs/nafld_diet_plan

# Run a small local demo without downloading NHANES data
nhanes-auto demo --outdir outputs/demo
```

Outputs include:

```text
outputs/
├── analysis_plan.md
├── variable_dictionary.csv
├── derivation_report.md
├── recipe_requirements.csv
└── missingness_report.csv
```

## Non-programmer workflow

The long-term goal is:

1. User fills a web form or chooses a template.
2. The system generates YAML.
3. The validator checks aliases, typos, unsupported recipes, and missing information.
4. User confirms the analysis plan.
5. Deterministic code downloads public-use NHANES data, merges by `SEQN`, derives variables, and runs analyses.
6. The system exports reproducibility reports and manuscript-ready tables.

## Data use and attribution

This project is not affiliated with CDC, NCHS, HHS, or the U.S. Government. It should only download and analyze **NHANES public-use data** from official CDC/NCHS sources. It does not redistribute restricted data and does not imply CDC endorsement.

See `docs/legal_and_data_use.md`.

## Built-in example: NAFLD + dietary patterns

The first example demonstrates how to organize a study similar to:

> NHANES 2005–2016; NAFLD defined by USFLI >= 30; exposures including HEI, DASH, MED, DII; covariates including age, sex, race/ethnicity, education, BMI, diabetes, hypertension, ALT, AST, HbA1c, physical activity; analyses including Table 1, survey-weighted logistic regression, subgroup analysis, and optional ML baselines.

See `examples/nafld_diet_analysis.yaml` and `docs/example_nafld_diet.md`.

## Commands

```bash
nhanes-auto check STUDY.yaml
nhanes-auto plan STUDY.yaml --outdir outputs/my_project
nhanes-auto demo --outdir outputs/demo
nhanes-auto list-recipes
```

## Repository layout

```text
nhanes-autoanalyst/
├── app.py                              # optional Streamlit UI prototype
├── examples/                           # study YAML examples
├── recipes/                            # transparent variable recipe registry
├── src/nhanes_autoanalyst/             # Python package
├── docs/                               # Chinese/English docs
├── tests/                              # basic tests
└── .github/                            # issue templates and CI
```

## Roadmap

- `v0.1`: project scaffold, recipes, config validator, derivation report.
- `v0.2`: public-use XPT download, `SEQN` merge, cycle-aware variable registry.
- `v0.3`: Table 1 and survey-weighted regression interface.
- `v0.5`: complete NAFLD + dietary pattern example with validated recipes.
- `v1.0`: stable open-source toolkit with several public-health examples.
- `v2.0`: optional AI-assisted natural-language-to-YAML configuration.

## License

MIT License.
