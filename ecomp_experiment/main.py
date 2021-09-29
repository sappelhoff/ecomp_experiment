"""Try this."""

# %%

import numpy as np
from psychopy import monitors, visual

from ecomp_experiment.define_settings import EXPECTED_FPS
from ecomp_experiment.define_stimuli import get_digit_stims, get_fixation_stim
from ecomp_experiment.define_trials import gen_trials
from ecomp_experiment.utils import check_framerate

# %%


trials = gen_trials(5)

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


def display_trial(win, trial, digit_frames, blank_frames, digit_stims):
    """Display a trial on a window."""
    for digit in trial:

        # Draw digit
        digit_stims[digit].draw()
        for frame in range(digit_frames):
            win.flip()

        # Blank screen before next digit
        for frame in range(blank_frames):
            win.flip()


# get digits
digit_stims = get_digit_stims(win, height=5)

# Get the objects for the fixation stim
outer, inner, horz, vert = get_fixation_stim(win)
fixation_stim_parts = [outer, horz, vert, inner]


trial = trials[2, ...]
for trial in trials:
    display_trial(win, trial, int(fps / 3), int(fps / 12), digit_stims)
    for frame in range(fps):
        win.flip()

    print(np.abs(trial).mean())

win.close()


# %%
win.close()
# %%
