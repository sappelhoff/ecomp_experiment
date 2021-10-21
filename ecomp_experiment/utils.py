"""Provide utility functions for the main experiment."""

import csv
import glob
import os
from pathlib import Path

import numpy as np
import pandas as pd
from psychopy import core

from ecomp_experiment.define_settings import KEYLIST_DICT


def calc_accuracy(logfile, blocksize):
    """Calculate accuracy as percent correct choices overall and of last block.

    Parameters
    ----------
    logfile : pathlib.Path
        Path object pointing to the logfile for this stream.
    blocksize : int
        How many trials fit into one block.

    Returns
    -------
    acc_overall, acc_block : int
        Accuracy as percentage correct choices overall so far, and in the last block.
    """
    df = pd.read_csv(logfile, sep="\t", usecols=["correct"])

    # "n/a" for "correct" means timeout, calculate as incorrect
    corrects = df["correct"].to_numpy()
    corrects = [False if np.isnan(i) else i for i in corrects]

    acc_overall = (np.sum(corrects) / len(corrects)) * 100
    acc_block = (np.sum(corrects[-blocksize:]) / blocksize) * 100

    # round up and turn into int
    acc_overall = int(np.ceil(acc_overall))
    acc_block = int(np.ceil(acc_block))

    return acc_overall, acc_block


def check_framerate(win, expected_fps):
    """Get and check fps of this window."""
    fps_counter = 0
    while True:
        fps = win.getActualFrameRate(nMaxFrames=1000)
        if fps is not None:
            fps = int(round(fps))
        if expected_fps == fps:
            return fps
        else:
            fps_counter += 1
            print(f"Found fps: {fps}, trying again.")
            core.wait(0.5)
        if fps_counter > 3:
            win.close()
            raise ValueError(f"Are you sure you are expecting {expected_fps} fps?")


def map_key_to_choice(key, state, stream):
    """Map a key to a choice, given a stream and stimulus state.

    Parameters
    ----------
    key : str
        The key that was pressed, see KEYLIST_DICT in define_settings.py.
    state : {0, 1}
        One of two states of the stimuli. Used for counterbalancing on
        which side (left/right) which answer option is displayed.
        state 0: left=red/higher, right=blue/lower
        state 1: left=blue/lower, right=red/higher
    stream : {"single", "dual"}
        The task (stream) where the key was pressed.

    Returns
    -------
    choice : {"lower", "higher", "blue", "red"}
        The choice the participant made. lower/higher relate to single stream, blue/red
        relate to dual stream.

    See Also
    --------
    define_stimuli.get_choice_stims
    define_settings.KEYLIST_DICT
    """
    left_key_pressed = key in KEYLIST_DICT["left"]
    right_key_pressed = key in KEYLIST_DICT["right"]
    if stream == "single":
        if state == 0:
            if left_key_pressed:
                choice = "higher"
            else:
                assert right_key_pressed
                choice = "lower"
        else:
            assert state == 1
            if left_key_pressed:
                choice = "lower"
            else:
                assert right_key_pressed
                choice = "higher"
        assert choice in ["lower", "higher"]
    else:
        assert stream == "dual"
        if state == 0:
            if left_key_pressed:
                choice = "red"
            else:
                assert right_key_pressed
                choice = "blue"
        else:
            assert state == 1
            if left_key_pressed:
                choice = "blue"
            else:
                assert right_key_pressed
                choice = "red"
        assert choice in ["red", "blue"]

    return choice


def save_dict(fname, savedict):
    """Write dict to file.

    Parameters
    ----------
    fname : pathlib.Path
        The file location to write to. Will be created if it doesn't
        exist yet; else, content is appended.
    savedict : dict
        The data to write.
    """
    if not fname.exists():
        with open(fname, "w", newline="") as fout:
            writer = csv.DictWriter(fout, savedict.keys(), delimiter="\t")
            writer.writeheader()
            writer.writerow(savedict)
    else:
        with open(fname, "a", newline="") as fout:
            writer = csv.DictWriter(fout, savedict.keys(), delimiter="\t")
            writer.writerow(savedict)


def calc_bonus(subj_id):
    """Calculate bonus money for a study participant.

    Bonus money is between 0 and 10 euro, based on overall % correct trials
    in single and dual stream tasks.

    Function must be run from the root of the repository.
    Run this function with (replace 'S' with the subject number):
    python -c "from ecomp_experiment.utils import calc_bonus; calc_bonus('S')"

    """
    if not isinstance(subj_id, int):
        raise ValueError("\n\n>>>>>> Supplied an integer for subj_id?")
    cwd = os.getcwd()
    ecomp_dir = Path(cwd).resolve()
    assert (ecomp_dir / "experiment_data").exists(), "\n\n>>>>>> Ran from root of repo?"
    assert (ecomp_dir / "LICENSE").exists(), "\n\n>>>>>> Ran from root of repo?"
    data_dir = ecomp_dir / "experiment_data"

    # Calculate accuracies for each stream
    accs = []
    for stream in ["single", "dual"]:
        search = str(data_dir / "sub-{:02}*".format(subj_id) / stream / "data.tsv")
        files = glob.glob(search)
        files_str = "\n".join(files) if len(files) > 0 else "[]"
        if len(files) != 1:
            msg = f"Found too few or too many file candidates:\n{files_str}"
            msg += f"\n\n(Was searching for:\n{search}\n)"
            raise RuntimeError(msg)
        logfile = files[0]
        acc_overall, _ = calc_accuracy(logfile, 1)  # blocksize irrelevant
        accs.append(acc_overall)
    accuracy = np.mean(accs)

    # map accuracy to money
    acc = int(np.ceil(accuracy))
    # smaller than 55 = 0 € (should not happen = chance level)
    if acc < 55:
        bonus_euro = 0

    # larger than 90 = 10 € (highly unlikely to happen)
    elif acc >= 90:
        bonus_euro = 10

    # Else, map accuracy from 55 to 90 % to 0 to 10 Euros
    else:
        cents_map = np.linspace(0, 1000, 90 - 55)
        bonus_cents = cents_map[acc - 55]
        bonus_euro = bonus_cents / 100

    # We round up to next euro
    bonus_euro = int(np.ceil(bonus_euro))
    print(f"Overall correct: {accuracy}%\nBonus money: {bonus_euro}€")
