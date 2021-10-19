"""Test utility functions."""
import itertools

import numpy as np
import pandas as pd
import pytest

from ecomp_experiment.define_settings import KEYLIST_DICT
from ecomp_experiment.utils import map_key_to_choice, save_dict


@pytest.mark.parametrize(
    "keys", list(itertools.product(KEYLIST_DICT["left"], KEYLIST_DICT["right"]))
)
def test_map_key_to_choice(keys):
    """Test mapping a key to a choice."""
    states = [0, 1]
    streams = ["single", "dual"]
    inputs = list(itertools.product(keys, states, streams))
    # inputs are:
    # [('left', 0, 'single'), -> higher
    #  ('left', 0, 'dual'),   -> red
    #  ('left', 1, 'single'), -> lower
    #  ('left', 1, 'dual'),   -> blue
    #  ('right', 0, 'single'), -> lower
    #  ('right', 0, 'dual'),   -> blue
    #  ('right', 1, 'single'), -> higher
    #  ('right', 1, 'dual')]   -> red
    # (note that left/right are defined in KEYLIST_DICT)
    expected_results = [
        "higher",
        "red",
        "lower",
        "blue",
        "lower",
        "blue",
        "higher",
        "red",
    ]
    for inp, res in zip(inputs, expected_results):
        choice = map_key_to_choice(*inp)
        assert choice == res


def test_save_dict(tmpdir):
    """Test saving dict to csv."""
    savedict = dict(a=55, b=22, c=33)
    fname = tmpdir / "try.csv"
    save_dict(fname, savedict)
    savedict.update(a=44, b=33, c=22)
    save_dict(fname, savedict)
    df = pd.read_csv(fname, sep="\t")
    assert df.columns.to_list() == ["a", "b", "c"]
    np.testing.assert_array_equal(df["a"].to_numpy(), [55, 44])
    np.testing.assert_array_equal(df["b"].to_numpy(), [22, 33])
    np.testing.assert_array_equal(df["c"].to_numpy(), [33, 22])
