import pandas as pd
import pytest

from nhanes_autoanalyst.nhanes_data import (
    NhanesDataError,
    append_cycles,
    build_xpt_url,
    file_code_from_stem,
    merge_on_seqn,
)


def test_file_code_from_stem():
    assert file_code_from_stem("DEMO", "2015-2016") == "DEMO_I"
    assert file_code_from_stem("DEMO_I", "2015-2016") == "DEMO_I"
    assert file_code_from_stem("DEMO", "1999-2000") == "DEMO"


def test_build_xpt_url():
    assert build_xpt_url("2015-2016", "DEMO_I") == "https://wwwn.cdc.gov/Nchs/Nhanes/2015-2016/DEMO_I.XPT"


def test_merge_on_seqn_outer():
    left = pd.DataFrame({"SEQN": [1, 2], "A": [10, 20]})
    right = pd.DataFrame({"SEQN": [2, 3], "B": [200, 300]})
    out = merge_on_seqn({"left": left, "right": right})
    assert set(out["SEQN"]) == {1, 2, 3}
    assert "A" in out.columns and "B" in out.columns


def test_merge_duplicate_seqn_fails():
    left = pd.DataFrame({"SEQN": [1, 1], "A": [10, 20]})
    with pytest.raises(NhanesDataError):
        merge_on_seqn({"left": left})


def test_append_cycles_adds_survey_cycle():
    a = pd.DataFrame({"SEQN": [1], "X": [1]})
    b = pd.DataFrame({"SEQN": [2], "X": [2]})
    out = append_cycles({"2015-2016": a, "2017-2018": b})
    assert list(out["survey_cycle"]) == ["2015-2016", "2017-2018"]
