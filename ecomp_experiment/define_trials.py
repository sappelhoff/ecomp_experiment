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
        ev_diff_dual = np.abs(digits[colors < 0].mean() - digits[colors > 0].mean())
        difficulties_diffs[itrial] = np.abs(ev_diff_single - ev_diff_dual)

    return difficulties_diffs


def evaluate_trial_correct(trial, choice, stream):
    """Evaluate whether a choice was correct for a trial, given a task type (stream).

    In case the trial does not have an objectively correct choice (ambiguous trials),
    the correctness will be determined randomly with a draw from a uniform distribution.
    If the choice is "n/a", the correctness will be "n/a" as well; but the ambiguity
    of the trial (True/False) will still be determined.

    Parameters
    ----------
    trial : np.ndarray
        The samples in this trial, negative 1 to 9 and positive 1 to 9. the sign
        of each sample determines which of two "colors" in the stream it belonged to.
        Negative samples are red, positive samples are blue.
    choice : {"lower", "higher", "blue", "red", "n/a"}
        The choice the participant made. lower/higher relate to single stream, blue/red
        relate to dual stream. Choices that are "n/a" are due to a slow response of
        participants and will result in a correctness of "n/a".
    stream : {"single", "dual"}
        The task (stream) that the trial and choice are from.

    Returns
    -------
    correct : bool | "n/a"
        Whether or not the choice in this trial was correct, given the stream.
        (Determined randomly if ambiguous is True)
    ambiguous : bool
        Whether or not the trial was ambiguous (not possible to objectively determine
        correctness).
    """
    set_correct_na = False
    if choice == "n/a":
        # Set choice to an arbitrary but valid value to evaluate `ambiguous` variable
        # but set `correct` to "n/a" later
        set_correct_na = True
        choice = {"single": "left", "dual": "red"}[stream]  # arbitrary

    digits = np.abs(trial)
    rng = np.random.default_rng()
    correct = rng.choice([True, False])
    ambiguous = True

    if stream == "single":
        assert choice in ["lower", "higher"]
        midpoint = 5

        # Can only evaluate correctness for non-ambiguous trials
        if digits.mean() != midpoint:
            ambiguous = False
            correct = False
            correct_higher = (digits.mean() > midpoint) and (choice == "higher")
            correct_lower = (digits.mean() < midpoint) and (choice == "lower")
            if correct_higher or correct_lower:
                correct = True

    else:
        assert stream == "dual"
        assert choice in ["blue", "red"]
        colors = np.sign(trial)
        mean_red = digits[colors < 0].mean()
        mean_blue = digits[colors > 0].mean()

        # Can only evaluate correctness for non-ambiguous trials
        if mean_red != mean_blue:
            ambiguous = False
            correct = False
            correct_red = (mean_red > mean_blue) and (choice == "red")
            correct_blue = (mean_red < mean_blue) and (choice == "blue")
            if correct_red or correct_blue:
                correct = True

    if set_correct_na:
        correct = "n/a"

    return correct, ambiguous
