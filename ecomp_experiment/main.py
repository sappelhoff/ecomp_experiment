"""Try this."""

# %%

import datetime
import json
import os
from pathlib import Path

import numpy as np
from psychopy import core, event, gui, monitors, visual

import ecomp_experiment
from ecomp_experiment.define_settings import EXPECTED_FPS, MONITOR_NAME
from ecomp_experiment.define_stimuli import (
    get_central_text_stim,
    get_choice_stims,
    get_digit_stims,
    get_fixation_stim,
)
from ecomp_experiment.define_trials import evaluate_trial_correct, gen_trials
from ecomp_experiment.utils import (
    calc_perc_correct,
    check_framerate,
    map_key_to_choice,
    save_dict,
)


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


# Prepare logging
streamdir, stream = display_survey_gui()
logfile = streamdir / "data.tsv"

# prepare the trials
trials = gen_trials(2)

# prepare the window
my_monitor = monitors.Monitor(name=MONITOR_NAME)
width, height = my_monitor.getSizePix()


win = visual.Window(
    color=(-1, -1, -1),  # Background color: RGB [-1,1]
    fullscr=True,  # Fullscreen for better timing
    monitor=my_monitor,
    units="deg",
    winType="pyglet",
    size=(width, height),
)

fps = check_framerate(win, EXPECTED_FPS)

# get digits
digit_stims = get_digit_stims(win, height=5)

# Get the objects for the fixation stim
outer, inner, horz, vert = get_fixation_stim(win)
fixation_stim_parts = [outer, horz, vert, inner]

rt_clock = core.Clock()
iti_rng = np.random.default_rng()
for itrial, trial in enumerate(trials):

    # Show fixstim
    for stim in fixation_stim_parts:
        stim.setAutoDraw(True)

    # jittered inter-trial-interval
    iti_ms = display_iti(win, 500, 1500, fps, iti_rng)

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

    # get choice from participant
    state = 1
    choice_stims = get_choice_stims(win, stream=stream, state=state, height=2)
    for stim in choice_stims:
        stim.draw()

    rt_clock.reset()
    win.flip()
    key_rt = event.waitKeys(maxWait=3, keyList=["left", "right"], timeStamped=rt_clock)

    if key_rt is None:
        choice = "n/a"
        rt = "n/a"
        valid = False
    else:
        assert len(key_rt) == 1
        key = key_rt[0][0]
        choice = map_key_to_choice(key, state, stream)
        rt = key_rt[0][1]
        valid = True

    # evaluate correctness of choice
    correct, ambiguous = evaluate_trial_correct(trial, choice, stream)

    # Save stuff
    savedict = dict(
        trial=itrial,
        choice=choice,
        ambiguous=ambiguous,
        rt=rt,
        validity=valid,
        iti=iti_ms,
        correct=correct,
        stream=stream,
    )
    samples = dict(
        zip([f"sample{i}" for i in range(1, 9)], [sample for sample in trial])
    )
    savedict.update(samples)
    save_dict(logfile, savedict)

    # Do a block break and display feedback
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
        corr_overall, corr_block = calc_perc_correct(logfile, blocksize)

        height = 1
        color = (1, 1, 1)
        text = f"You have completed {itrial+1} of {ntrials} trials.\n\n"
        text += f"Your choices in the past {blocksize} trials "
        text += f"were {corr_block}% accurate.\n\n"
        text += f"Your overall accuracy in this task so far is {corr_overall}%.\n\n"
        text += "Press any key to continue"

        text_stim = get_central_text_stim(win, height, text, color)
        text_stim.draw()
        win.flip()
        event.waitKeys()

    display_block_break(win, logfile, itrial, 2, 1)


win.close()


# %%
win.close()
# %%
