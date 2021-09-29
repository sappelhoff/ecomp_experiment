"""Define stimuli for experiment."""

from psychopy import visual


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
    outer, inner, horz, vert : tuple of objects
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
