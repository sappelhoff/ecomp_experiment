"""Test utility functions."""

import itertools

from ecomp_experiment.utils import map_key_to_choice


def test_map_key_to_choice():
    """Test mapping a key to a choice."""
    keys = ["left", "right"]
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
