"""Define routines for the experiment flow."""


import datetime
import json
import os
from pathlib import Path

import numpy as np
from psychopy import core, event, gui

import ecomp_experiment
from ecomp_experiment.define_stimuli import get_central_text_stim
from ecomp_experiment.utils import calc_accuracy


def display_survey_gui():
    """Gather participant and experiment data.

    Creates a directory and writes data to it.

    Returns
    -------
    streamdir : pathlib.Path
        Path object pointing to the directory where to save data
        for this participant.
    stream : {"single", "dual"}
        The stream to run in the experiment.
    """
    # Check for real experiment or just a test run
    survey_gui1 = gui.Dlg(title="eComp Experiment")
    survey_gui1.addField("Type", choices=["Experiment", "Test"])
    survey_gui1.addField("Stream", choices=["single", "dual"])
    survey_data1 = survey_gui1.show()

    if not survey_gui1.OK:
        # Cancel the program in case of "cancel"
        core.quit()

    run_type = survey_data1[0]
    stream = survey_data1[1]

    if run_type == "Experiment":

        # We want to run the experiment, gather some data
        survey_gui2 = gui.Dlg(title="eComp Experiment")
        survey_gui2.addField("ID:", choices=list(range(1, 100)))
        survey_gui2.addField("Age:", choices=list(range(18, 60)))
        survey_gui2.addField("Sex:", choices=["Male", "Female", "Other"])
        survey_gui2.addField("Handedness:", choices=["Right", "Left", "Ambidextrous"])
        survey_data2 = survey_gui2.show()

        if not survey_gui2.OK:
            # Cancel the program in case of "cancel"
            core.quit()
    else:
        survey_data2 = ["Test"]

    # Prepare directory for saving data
    ecomp_dir = Path("main.py").resolve().parent.parent
    data_dir = ecomp_dir / "experiment_data"
    assert data_dir.exists()
    recording_datetime = datetime.datetime.today().isoformat()
    substr = (
        "{:02}".format(survey_data2[0])
        if isinstance(survey_data2[0], int)
        else survey_data2[0]
    )
    subjdir = data_dir / f"sub-{substr}_{recording_datetime}"
    streamdir = subjdir / stream
    os.makedirs(subjdir, exist_ok=True)
    os.makedirs(streamdir, exist_ok=True)

    # Save available participant data
    if len(survey_data2) > 1:
        kwargs = dict(zip(["ID", "Age", "Sex", "Handedness"], survey_data2))
    else:
        kwargs = dict(zip(["ID"], survey_data2))
    data = dict(
        experiment_version=ecomp_experiment.__version__,
        recording_datetime=recording_datetime,
    )
    data.update(kwargs)

    fname = "experiment_info.json"
    with open(subjdir / fname, "w") as fout:
        json.dump(data, fout, indent=4, ensure_ascii=False, sort_keys=True)

    return streamdir, stream


def display_iti(win, min_ms, max_ms, fps, rng):
    """Display and return an inter-trial-interval.

    Parameters
    ----------
    win : psychopy.visual.Window
        The psychopy window on which to draw the stimuli.
    min_ms, max_ms :  int
        The minimum and maximum inter-trial-interval time in milliseconds.
    fps : int
        Refreshrate of the screen.
    rng : np.random.Generator
        The random number generator object based on which to
        generate the inter-trial-intervals.

    Returns
    -------
    iti_ms : int
        the inter-trial-interval in milliseconds.

    """
    low = int(np.floor(min_ms / 1000 * fps))
    high = int(np.ceil(max_ms / 1000 * fps))
    iti_frames = rng.integers(low, high + 1)

    for frame in range(iti_frames):
        win.flip()

    iti_ms = (iti_frames / fps) * 1000
    return iti_ms


def display_trial(win, trial, digit_frames, fade_frames, digit_stims):
    """Display a trial on a window."""
    for digit in trial:

        stim = digit_stims[digit]

        # Draw digit
        for frame in range(digit_frames):
            stim.draw()
            win.flip()

        # Fade stim to blank within fade_frames
        orig_opacity = stim.opacity
        opacities = np.linspace(1, 0, fade_frames)
        for opacity in opacities:
            stim.setOpacity(opacity)
            stim.draw()
            win.flip()

        # Reset stim opacity
        stim.setOpacity(orig_opacity)


def display_block_break(win, logfile, itrial, ntrials, blocksize):
    """Display a break screen, including feedback.

    Parameters
    ----------
    win : psychopy.visual.Window
        The psychopy window on which to draw the stimuli.
    logfile : pathlib.Path
        Path object pointing to the logfile for this stream.
    itrial : int
        The current trial number
    ntrials : int
        The overall number of trials.
    blocksize : int
        How many trials fit into one block.
    """
    acc_overall, acc_block = calc_accuracy(logfile, blocksize)

    height = 1
    color = (1, 1, 1)
    text = f"You have completed {itrial+1} of {ntrials} trials.\n\n"
    text += f"Your choices in the past {blocksize} trials "
    text += f"were {acc_block}% accurate.\n\n"
    text += f"Your overall accuracy in this task so far is {acc_overall}%.\n\n"
    text += "Press any key to continue"

    text_stim = get_central_text_stim(win, height, text, color)
    text_stim.draw()
    win.flip()
    event.waitKeys()
