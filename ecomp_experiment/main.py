"""Try this."""

# %%

import datetime
import json
import os
from pathlib import Path

import numpy as np
from psychopy import core, event, gui, monitors, visual

import ecomp_experiment
from ecomp_experiment.define_settings import EXPECTED_FPS
from ecomp_experiment.define_stimuli import (
    get_choice_stims,
    get_digit_stims,
    get_fixation_stim,
)
from ecomp_experiment.define_trials import gen_trials
from ecomp_experiment.utils import check_framerate

# %%

trials = gen_trials(2)

my_monitor = monitors.Monitor(name="benq")
width, height = my_monitor.getSizePix()


win = visual.Window(
    color=(0, 0, 0),  # Background color: RGB [-1,1]
    fullscr=True,  # Fullscreen for better timing
    monitor=my_monitor,
    units="deg",
    winType="pyglet",
    size=(width, height),
)

fps = check_framerate(win, EXPECTED_FPS)


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


# get digits
digit_stims = get_digit_stims(win, height=5)

# Get the objects for the fixation stim
outer, inner, horz, vert = get_fixation_stim(win)
fixation_stim_parts = [outer, horz, vert, inner]

rt_clock = core.Clock()
iti_rng = np.random.default_rng()
for trial in trials:

    # Show fixstim
    for stim in fixation_stim_parts:
        stim.setAutoDraw(True)

    # jittered inter-trial-interval
    iti_ms = display_iti(win, 500, 1000, fps, iti_rng)

    # 500ms before first sample onset,remove fixstim
    for stim in fixation_stim_parts:
        stim.setAutoDraw(False)
    for frame in range(int(np.ceil(fps / 2))):
        win.flip()

    # show samples
    display_trial(
        win,
        trial,
        digit_frames=int(fps / 2.75),
        fade_frames=int(fps / 12),
        digit_stims=digit_stims,
    )

    # wait briefly after offset of last sample
    for frame in range(int(fps / 2.75) + int(fps / 12)):
        win.flip()

    # get choice from participant
    choice_stims = get_choice_stims(win, stream="dual", participant_id=1, height=2)
    for stim in choice_stims:
        stim.draw()

    rt_clock.reset()
    win.flip()
    key_rt = event.waitKeys(maxWait=3, keyList=["left", "right"], timeStamped=rt_clock)
    print(key_rt)

    # display participant choice

    print(np.abs(trial).mean())

win.close()


# %%
win.close()
# %%


def display_survey_gui():
    """Gather participant and experiment data."""
    # Check for real experiment or just a test run
    survey_gui = gui.Dlg(title="eComp Experiment")
    survey_gui.addField("Type", choices=["Experiment", "Test"])
    survey_data = survey_gui.show()

    if survey_gui.OK and survey_data[0] == "Experiment":

        # We want to run the experiment, gather some data
        survey_gui = gui.Dlg(title="eComp Experiment")
        survey_gui.addField("ID:", choices=list(range(1, 100)))
        survey_gui.addField("Age:", choices=list(range(18, 60)))
        survey_gui.addField("Sex:", choices=["Male", "Female", "Other"])
        survey_gui.addField("Handedness:", choices=["Right", "Left", "Ambidextrous"])
        survey_data = survey_gui.show()

    elif survey_gui.OK:
        assert len(survey_data) == 1 and survey_data[0] == "Test"
    else:
        core.quit()

    # Prepare directory for saving data
    ecomp_dir = Path("main.py").resolve().parent.parent
    data_dir = ecomp_dir / "experiment_data"
    assert data_dir.exists()
    recording_datetime = datetime.datetime.today().isoformat()
    substr = (
        "{:02}".format(survey_data[0])
        if isinstance(survey_data[0], int)
        else survey_data[0]
    )
    dirname = data_dir / f"sub-{substr}_{recording_datetime}"
    os.makedirs(dirname)

    # Save available participant data
    if len(survey_data) > 1:
        survey_data_kwargs = dict(zip(["ID", "Age", "Sex", "Handedness"], survey_data))
    else:
        survey_data_kwargs = dict(zip(["ID"], survey_data))
    data = dict(
        experiment_version=ecomp_experiment.__version__,
        recording_datetime=recording_datetime,
    )
    data.update(survey_data_kwargs)

    fname = "experiment_info.json"
    with open(dirname / fname, "w") as fout:
        json.dump(data, fout, indent=4, sort_keys=True)

    print(data)


# %%
display_survey_gui()
# %%
