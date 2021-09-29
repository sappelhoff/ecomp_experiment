"""Define trials for the experiment."""
import numpy as np


def gen_trial(rng):
    """Generate trials for a participant.

    Parameters
    ----------
    rng : np.random.Generator
        The random number generator object based on which to
        generate the trials.

    Returns
    -------
    color_samples : np.ndarray, shape(8,)
        Samples for this trial.

    """
    # Digits from 1 to 9
    digits = np.arange(1, 10)

    # 8 samples per trial
    n_samples = 8

    # 4 samples are of color1, 4 samples are of color2
    # all drawn from uniform distribution
    samples = rng.choice(digits, n_samples, replace=True)
    colors = rng.choice([-1, 1] * int(n_samples / 2), n_samples, replace=False)

    # Negative samples are color1, positive samples are color2
    color_samples = samples * colors
    return color_samples


def gen_trials(n_trials, prop_regen=0, seed=None):
    """Generate multiple trials."""
    assert prop_regen >= 0 and prop_regen <= 1, "`prop_regen` must be between 0 and 1."
    rng = np.random.default_rng(seed)

    # 8 samples per trial
    n_samples = 8

    trials = np.nan * np.zeros((n_trials, n_samples))
    for itrial in range(n_trials):
        trials[itrial, ...] = gen_trial(rng)

    # Re-generate a proportion of trials where difficulty difference
    # between single and dual stream tasks is highest
    difficulties_diffs = calc_trial_difficulty_diffs(trials)
    idxs_descending = np.argsort(difficulties_diffs)[::-1]
    n_regen = int(np.round(n_trials * prop_regen))
    idxs_regen = idxs_descending[0:n_regen]

    for idx in idxs_regen:
        trials[idx, ...] = gen_trial(rng)

    return trials


def calc_trial_difficulty_diffs(trials):
    """Calculate difficulty diffference of each trial between single and dual stream."""
    midpoint = 5
    difficulties_diffs = np.nan * np.zeros(trials.shape[0])
    for itrial, trial in enumerate(trials):

        digits = np.abs(trial)
        colors = np.sign(trial)

        # Calc difficulty of single/dual task by means of "expected value difference"
        ev_diff_single = np.abs(midpoint - digits.mean())
        ev_diff_dual = np.abs(digits[colors == -1].mean() - digits[colors == 1].mean())
        difficulties_diffs[itrial] = np.abs(ev_diff_single - ev_diff_dual)

    return difficulties_diffs
