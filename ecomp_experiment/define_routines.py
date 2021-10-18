"""Define routines for the experiment flow."""


import datetime
import json
import os
import shutil
from pathlib import Path

import numpy as np
from psychopy import core, event, gui

import ecomp_experiment
from ecomp_experiment.define_settings import BLOCKSIZE, MAXWAIT_RESPONSE_S, NSAMPLES
from ecomp_experiment.define_stimuli import get_central_text_stim
from ecomp_experiment.define_ttl import send_trigger
from ecomp_experiment.utils import calc_accuracy


def display_instructions(win, stream):
    """Display participant instructions.

    Parameters
    ----------
    win : psychopy.visual.Window
        The psychopy window on which to draw the stimuli.
    stream : {"single", "dual"}
        The stream to run in the experiment.
    """
    text_stim = get_central_text_stim(win=win, height=1, text="", color=(1, 1, 1))

    # prepare instructions
    common_instructions_start = [
        "In this study, we want to investigate how humans average numerical values "
        "when making decisions from rapid sequential samples.",
        "At the beginning of each trial you will see a gray fixation stimulus in "
        "the center of the screen.",
        "After some time, the trial will start and we will present "
        "a rapid sequence of digits, one after the other. "
        f"Specifically, you will always see {NSAMPLES} digits between 1 and 9. "
        "Half of them are in red color, the other half of them are in blue color.",
    ]
    single_instructions = [
        "We will then ask you if the average of the numbers was smaller "
        "or larger than five.",
        "You will see an upwards (larger), and a downwards (smaller) "
        "arrow on the left and right side of the screen. "
        "Please use your left and right hand to select the arrows that indicate "
        "whether the average of the shown numbers was smaller or larger than five.",
        "Please note that on each trial, the location of the upwards and "
        "downwards arrow changes. "
        "In other words, you have to check on each trial which key, left or right, "
        "means which answer, upwards arrow (larger) or downwards arrow (smaller).",
    ]
    dual_instructions = [
        "We will then ask you which color had the larger average. "
        "You will see a blue and a red upwards arrow on the left and "
        "right side of the screen. "
        "Please use your left and right hand to select the arrows that indicate "
        "whether the average of the blue or of the red numbers was larger.",
        "Please note that on each trial, the location of the blue and red upwards "
        "arrow changes. "
        "In other words, you have to check on each trial which key, left or right, "
        "means which answer, blue or red upwards arrow.",
    ]
    common_instructions_end = [
        f"You have {MAXWAIT_RESPONSE_S} seconds to answer. "
        "If you do not answer in time, there will be "
        "a timeout message and your answer is counted as wrong.\n"
        "The study will then automatically proceed to the next trial after a "
        "short time.",
        f"Every {BLOCKSIZE} trials you will receive information about how "
        "accurate your choices were. "
        "Remember that over the whole experiment you can earn a bonus of "
        "up to 10 Euros, depending on your accuracy.\n\n"
        "-> Pressing the right key will end the instructions. <-",
    ]

    if stream == "single":
        instructions = (
            common_instructions_start + single_instructions + common_instructions_end
        )
    else:
        assert stream == "dual"
        instructions = (
            common_instructions_start + dual_instructions + common_instructions_end
        )

    # Instructions presentation
    itext = 0
    while True:
        text_stim.text = instructions[itext]
        text_stim.draw()
        win.flip()
        keys = event.waitKeys(keyList=["left", "right", "escape"])
        if keys[0] == "escape":
            break
        elif keys[0] == "left":
            # can't go further back than 0
            itext = max(0, itext - 1)
        elif keys[0] == "right":
            itext += 1
            if itext >= len(instructions):
                break


def display_survey_gui():
    """Gather participant and experiment data.

    Creates a directory and writes data to it.

    Returns
    -------
    run_type : {"experiment", "training", "test", "instructions"}
        The type/mode that the experiment runs in. "experiment" should be
        used to run participants, "test" behaves equally, but saves data to
        "Test" subject folders (always overwritten), and "training" should
        only be used for training trials, because it will display additional
        feedback. "instructions" will just display participant instructions
        and then quit.
    streamdir : pathlib.Path | None
        Path object pointing to the directory where to save data for this
        participant. Will be None if `run_type` is "instructions".
    stream : {"single", "dual"}
        The stream to run in the experiment.
    substr : str
        The subject identifier string.
    """
    # Check for real experiment or just a test run
    survey_gui1 = gui.Dlg(title="eComp Experiment")
    survey_gui1.addField(
        "Type", choices=["experiment", "training", "test", "instructions"]
    )
    survey_gui1.addField("Stream", choices=["single", "dual"])
    survey_data1 = survey_gui1.show()

    if not survey_gui1.OK:
        # Cancel the program in case of "cancel"
        core.quit()

    run_type = survey_data1[0]
    stream = survey_data1[1]

    if run_type == "experiment":

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
    elif run_type == "instructions":
        return run_type, None, stream
    else:
        assert run_type in ["training", "test"]
        survey_data2 = ["test"]

    # Prepare directory for saving data
    ecomp_dir = Path("main.py").resolve().parent.parent
    data_dir = ecomp_dir / "experiment_data"
    assert data_dir.exists(), "Sure you are in the right directory?"

    # Create subj dir
    subid = survey_data2[0]
    substr = "{:02}".format(subid) if isinstance(subid, int) else subid
    subjdir = data_dir / f"sub-{substr}"
    streamdir = subjdir / stream

    # Do not risk overwriting experiment data
    if streamdir.exists():
        if run_type == "experiment":
            msg = f"Stream directory {stream} for subject ID {substr} already exists."
            raise RuntimeError(msg)
        else:
            assert run_type in ["training", "test"]
            print("Found previous test/training data. Removing it ...")
            shutil.rmtree(streamdir)

    os.makedirs(subjdir, exist_ok=True)
    os.makedirs(streamdir, exist_ok=True)

    # Save available participant data
    recording_datetime = datetime.datetime.today().isoformat()
    if len(survey_data2) > 1:
        kwargs = dict(zip(["ID", "Age", "Sex", "Handedness"], survey_data2))
    else:
        kwargs = dict(zip(["ID"], survey_data2))
    data = dict(
        experiment_version=ecomp_experiment.__version__,
        recording_datetime=recording_datetime,
        stream=stream,
    )
    data.update(kwargs)

    fname = f"experiment_info_stream-{stream}.json"
    fpath = subjdir / fname
    if fpath.exists() and run_type == "experiment":
        raise RuntimeError(f"File exists: {fpath}")
    with open(fpath, "w") as fout:
        json.dump(data, fout, indent=4, ensure_ascii=False, sort_keys=True)

    return run_type, streamdir, stream, substr


def display_iti(win, min_ms, max_ms, fps, rng, trigger_kwargs):
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
    trigger_kwargs : dict
        Contains keys ser, tk, and byte. To be passed to the send_trigger
        function.

    Returns
    -------
    iti_ms : int
        the inter-trial-interval in milliseconds.
    """
    low = int(np.floor(min_ms / 1000 * fps))
    high = int(np.ceil(max_ms / 1000 * fps))
    iti_frames = rng.integers(low, high + 1)

    win.callOnFlip(send_trigger, **trigger_kwargs)
    for frame in range(iti_frames):
        win.flip()

    iti_ms = (iti_frames / fps) * 1000
    return iti_ms


def display_trial(
    win, trial, digit_frames, fade_frames, digit_stims, trigger_kwargs_list
):
    """Display a trial on a window.

    Parameters
    ----------
    win : psychopy.visual.Window
        The psychopy window on which to draw the stimuli.
    trial : np.ndarray, shape(8,)
        The digit samples in this trial (from 1 to 9).
    digit_frames, fade_frames : int
        The number of frames (win flips) to show a digit, and to fade a digit.
    digit_stims : dict
        Contains the psychopy stimuli for the digits.
    trigger_kwargs_list : list of dicts
        Each entry in the list corresponds to a digit in the trial (in order!).
    """
    for idigit, digit in enumerate(trial):

        stim = digit_stims[digit]
        trigger_kwargs = trigger_kwargs_list[idigit]

        # Draw digit
        win.callOnFlip(send_trigger, **trigger_kwargs)
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


def display_block_break(
    win, logfile, itrial, ntrials, blocksize, block_counter, hard_break, trigger_kwargs
):
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
    block_counter : int
        A simple counter variable, that will be incremented by 1 and then returned.
    hard_break : int
        Used to determine whether to do a non-skippable block break. Done via
        ``block_counter % hard_break == 0``, that is, do a non-skippable block after
        every `hard_break` blocks. Hard breaks can only be skipped by pressing
        the escape key.
    trigger_kwargs : dict
        Contains keys ser, tk, and byte. To be passed to the send_trigger
        function.

    Returns
    -------
    block_counter : int
        A simple block counter, incremented by one compared to how it was passed
        into this function.
    """
    do_hard_break = block_counter % hard_break == 0
    acc_overall, acc_block = calc_accuracy(logfile, blocksize)

    height = 1
    color = (1, 1, 1)
    text = f"You have completed {itrial+1} of {ntrials} trials.\n\n"
    text += f"Your choices in the past {blocksize} trials "
    text += f"were {acc_block}% accurate.\n\n"
    text += f"Your overall accuracy in this task so far is {acc_overall}%.\n\n"

    if do_hard_break:
        text += "-> Please wait for the experimenter. <-"
    else:
        text += "Press any key to continue."

    text_stim = get_central_text_stim(win, height, text, color)
    text_stim.draw()
    win.callOnFlip(send_trigger, **trigger_kwargs)
    win.flip()
    if do_hard_break:
        # only pressing escape works
        event.waitKeys(keyList=["escape"])
    else:
        event.waitKeys()

    return block_counter + 1
