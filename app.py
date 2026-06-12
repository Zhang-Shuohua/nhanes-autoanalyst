"""Optional Streamlit prototype for NHANES AutoAnalyst.

Run with:
    streamlit run app.py

This UI only creates a draft YAML-like configuration. It does not run real NHANES analyses yet.
"""

try:
    import streamlit as st
except ImportError:  # pragma: no cover
    raise SystemExit("Streamlit is not installed. Install with: pip install -e .[ui]")

import yaml

st.set_page_config(page_title="NHANES AutoAnalyst", layout="wide")
st.title("NHANES AutoAnalyst")
st.caption("Teaching-oriented NHANES reproducible analysis scaffold")

project = st.text_input("Project name", "lead_hypertension_analysis")
cycles = st.multiselect(
    "NHANES cycles",
    ["2005-2006", "2007-2008", "2009-2010", "2011-2012", "2013-2014", "2015-2016", "2017-2018"],
    default=["2011-2012", "2013-2014"],
)
outcome = st.selectbox("Outcome recipe", ["hypertension_guideline", "nafld_usfli_ge30", "ckd_egfr_albuminuria", "diabetes_ada"])
exposure = st.selectbox("Exposure", ["blood_lead", "blood_cadmium", "hei_2015", "dii_28_parameter", "bmi"])
covariates = st.multiselect(
    "Covariates",
    ["age", "sex", "race_ethnicity", "education", "bmi", "smoking_status", "diabetes_ada", "hypertension_guideline", "physical_activity_met"],
    default=["age", "sex", "race_ethnicity", "bmi"],
)
analysis = {
    "table1": st.checkbox("Table 1", value=True),
    "survey_weighted_logistic": st.checkbox("Survey-weighted logistic regression", value=True),
    "rcs": st.checkbox("Restricted cubic spline", value=False),
}

config = {
    "project": project,
    "cycles": cycles,
    "outcome": {"recipe": outcome},
    "exposures": [{"raw_variable" if exposure.startswith("blood_") else "recipe": exposure}],
    "covariates": covariates,
    "analysis": analysis,
}

st.subheader("Generated YAML draft")
st.code(yaml.safe_dump(config, allow_unicode=True, sort_keys=False), language="yaml")
st.warning("This is a configuration draft. Researchers must confirm variables, cycles, weights, exclusions, and formulas before analysis.")
