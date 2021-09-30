"""Provide utility functions for the main experiment."""

import csv

from psychopy import core


def set_fixstim_color(stim, color):
    """Set the fill and line color of a stim."""
    stim.setFillColor(color)
    stim.setLineColor(color)
    return stim


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
    key : {"left", "right"}
        The key that was pressed.
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
    """
    if stream == "single":
        if state == 0:
            if key == "left":
                choice = "higher"
            else:
                assert key == "right"
                choice = "lower"
        else:
            assert state == 1
            if key == "left":
                choice = "lower"
            else:
                assert key == "right"
                choice = "higher"
        assert choice in ["lower", "higher"]
    else:
        assert stream == "dual"
        if state == 0:
            if key == "left":
                choice = "red"
            else:
                assert key == "right"
                choice = "blue"
        else:
            assert state == 1
            if key == "left":
                choice = "blue"
            else:
                assert key == "right"
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
        with open(fname, "w") as fout:
            writer = csv.DictWriter(fout, savedict.keys(), delimiter="\t")
            writer.writeheader()
            writer.writerow(savedict)
    else:
        with open(fname, "a") as fout:
            writer = csv.DictWriter(fout, savedict.keys(), delimiter="\t")
            writer.writerow(savedict)
