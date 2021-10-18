"""Test trial definition functions."""

import numpy as np

from ecomp_experiment.define_settings import NSAMPLES
from ecomp_experiment.define_trials import evaluate_trial_correct, gen_trials


def test_smoke():
    """Basic smoke test, generating trials, testing for difficulty and correctness."""
    seed = 42
    rng = np.random.default_rng(seed)
    choices = {"single": ["lower", "higher"], "dual": ["red", "blue"]}
    trials = gen_trials(100, NSAMPLES, 0.5, seed)
    for trial in trials:
        stream = rng.choice(["single", "dual"])
        choice_idx = rng.choice([0, 1, 2])
        choice = "n/a" if choice_idx == 2 else choices[stream][choice_idx]
        correct, ambiguous = evaluate_trial_correct(trial, choice, stream)


def test_evaluate_trial_correct():
    """Test that trials are correctly evaluated."""
    # Test a basic trial for all streams and choices
    trial = np.array([-1, -1, -1, -1, 2, 2, 2, 2])

    correct, ambiguous = evaluate_trial_correct(trial, choice="lower", stream="single")
    assert correct
    assert not ambiguous

    correct, ambiguous = evaluate_trial_correct(trial, choice="red", stream="dual")
    assert not correct
    assert not ambiguous

    correct, ambiguous = evaluate_trial_correct(trial, choice="n/a", stream="dual")
    assert correct == "n/a"
    assert not ambiguous

    correct, ambiguous = evaluate_trial_correct(trial, choice="higher", stream="single")
    assert not correct
    assert not ambiguous

    correct, ambiguous = evaluate_trial_correct(trial, choice="blue", stream="dual")
    assert correct
    assert not ambiguous

    correct, ambiguous = evaluate_trial_correct(trial, choice="n/a", stream="single")
    assert correct == "n/a"
    assert not ambiguous

    # Test ambiguous trials
    trial = np.array([-5, -5, -5, -5, 5, 5, 5, 5])

    correct, ambiguous = evaluate_trial_correct(trial, choice="lower", stream="single")
    assert correct in [True, False]  # random
    assert ambiguous

    correct, ambiguous = evaluate_trial_correct(trial, choice="red", stream="dual")
    assert correct in [True, False]  # random
    assert ambiguous

    correct, ambiguous = evaluate_trial_correct(trial, choice="n/a", stream="dual")
    assert correct == "n/a"
    assert ambiguous

    # check results are really random when trial is ambiguous:
    # Statistically there should be at least one of each, True and False
    corrects = []
    for i in range(100):
        correct, _ = evaluate_trial_correct(trial, choice="red", stream="dual")
        corrects.append(correct)
    assert True in corrects
    assert False in corrects
