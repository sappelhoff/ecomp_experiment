"""Define stimuli for experiment."""

import numpy as np
from psychopy import visual


def get_choice_stims(win, stream, participant_id, height=1):
    """Get the stimuli used for inquiring participant choice.

    Parameters
    ----------
    win : psychopy.visual.Window
        The psychopy window on which to draw the stimuli.
    stream : {"single", "dual"}
        Whether the single or dual stream choice stim should be prepared.
    participant_id : int
        The participant ID, used for counterbalancing on which side (left/right)
        which answer option is displayed (using even versus odd IDs to distinguish).
    height : int | float
        The height of the stimuli in degrees visual angle.

    Returns
    -------
    choice_stims : list of psychopy.visual.text.TextStim
        Stimuli to be displayed during choice phase of a trial.

    """
    # Common arguments to all choice stimuli
    kwargs = dict(
        win=win,
        height=height,
        units="deg",
        font="Liberation Sans",
        anchorVert="center",
    )

    if stream == "single":
        left_text = ["↑a", "↓a"][int(participant_id % 2 == 0)]
        right_text = ["↓a", "↑a"][int(participant_id % 2 == 0)]
        center_text = "5"
        assert left_text != right_text
        left_color = (0, 0, 0)
        right_color = (0, 0, 0)

    else:
        assert stream == "dual"
        left_color = [(1, 0, 0), (0, 0, 1)][int(participant_id % 2 == 0)]
        right_color = [(0, 0, 1), (1, 0, 0)][int(participant_id % 2 == 0)]
        assert left_color != right_color
        left_text = "↑a"
        right_text = "↑a"
        center_text = "or"

    # Design one for left, one for center, and one for right
    left = visual.TextStim(
        **kwargs,
        text=left_text,
        pos=(-0.1, 0),
        alignText="left",
        anchorHoriz="left",
        color=left_color,
    )

    center = visual.TextStim(
        **kwargs,
        text=center_text,
        pos=(0, 0),
        alignText="left",
        anchorHoriz="left",
        color=(1, 1, 1),
    )

    right = visual.TextStim(
        **kwargs,
        text=right_text,
        pos=(0.1, 0),
        alignText="right",
        anchorHoriz="right",
        color=right_color,
    )

    choice_stims = [left, center, right]
    return choice_stims


def get_digit_stims(win, color1=(1, 0, 0), color2=(0, 0, 1), height=1):
    """Pre-generate all digit stimuli.

    Parameters
    ----------
    win : psychopy.visual.Window
        The psychopy window on which to draw the stimuli.
    color1 : tuple
        The first color that the stimuli may have.
    color2 : tuple
        The second color that the stimuli may have.
    height : int | float
        height of the stimuli in degrees visual angle.

    Returns
    -------
    digit_stims : dict of psychopy.visual.text.TextStim
        Contains keys 1 to 9 and negative 1 to negative 9. Corresponding
        to digits in color1 and color2, respectively.

    """
    digits = [-9, -8, -7, -6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    digit_stims = dict()
    for digit in digits:
        color = color1 if digit < 0 else color2
        stim = visual.TextStim(
            win,
            height=height,
            units="deg",
            color=color,
            text=f"{np.abs(digit)}",
            font="Liberation Sans",
            pos=(0, 0),
            alignText="center",
            anchorHoriz="center",
            anchorVert="center",
        )
        digit_stims[digit] = stim

    return digit_stims


def get_fixation_stim(win, back_color=(0, 0, 0), stim_color=(1, 1, 1)):
    """Provide objects to represent a fixation stimulus as in [1]_.

    Parameters
    ----------
    win : psychopy.visual.Window
        The psychopy window on which to draw the fixation stimulus.
    back_color : tuple
        Color of the background (-1=black, 0=gray, 1=white).
    stim_color : tuple
        Color of the stimulus (-1=black, 0=gray, 1=white).

    Returns
    -------
    outer, inner, horz, vert : tuple of psychopy Circle and Rect objects
        The objects that make up the fixation stimulus.

    References
    ----------
    .. [1] Thaler, L., Schütz, A. C., Goodale, M. A., & Gegenfurtner, K. R.
       (2013). What is the best fixation target? The effect of target shape on
       stability of fixational eye movements. Vision Research, 76, 31-42.
       https://www.doi.org/10.1016/j.visres.2012.10.012

    """
    # diameter outer circle = 0.6 degrees
    # diameter circle = 0.2 degrees
    outer = visual.Circle(
        win=win,
        radius=0.6 / 2,
        edges=32,
        units="deg",
        fillColor=stim_color,
        lineColor=back_color,
    )

    inner = visual.Circle(
        win=win,
        radius=0.2 / 2,
        edges=32,
        units="deg",
        fillColor=stim_color,
        lineColor=stim_color,
    )

    horz = visual.Rect(
        win=win,
        units="deg",
        width=0.6,
        height=0.2,
        fillColor=back_color,
        lineColor=back_color,
    )

    vert = visual.Rect(
        win=win,
        units="deg",
        width=0.2,
        height=0.6,
        fillColor=back_color,
        lineColor=back_color,
    )

    return (outer, inner, horz, vert)
