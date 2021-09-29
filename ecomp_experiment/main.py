"""Try this."""

# %%

import numpy as np
from psychopy import core, monitors, visual

from ecomp_experiment.define_settings import EXPECTED_FPS
from ecomp_experiment.define_stimuli import get_fixation_stim
from ecomp_experiment.utils import set_fixstim_color

# %%
win = visual.Window()

# %%
win.close()
# %%


my_monitor = monitors.Monitor(name="benq")
width, height = my_monitor.getSizePix()
# %%


win = visual.Window(
    color=(0, 0, 0),  # Background color: RGB [-1,1]
    fullscr=True,  # Fullscreen for better timing
    monitor=my_monitor,
    units="deg",
    winType="pyglet",
    size=(width, height),
)

fps = win.getActualFrameRate(nMaxFrames=1000)

# On which frame rate are we operating? Try getting it several times
# because it can fluctuate a bit
fps_counter = 0
while True:
    fps = win.getActualFrameRate(nMaxFrames=1000)
    if fps is not None:
        fps = int(round(fps))
        print("found fps: {}".format(fps))
    if EXPECTED_FPS == fps:
        break
    else:
        fps_counter += 1
        core.wait(1)
    if fps_counter > 3:
        raise ValueError(
            "Please adjust the EXPECTED_FPS variable " "in define_settings.py"
        )


# Get the objects for the fixation stim
outer, inner, horz, vert = get_fixation_stim(win)
fixation_stim_parts = [outer, horz, vert, inner]


for stim in fixation_stim_parts:
    stim.setAutoDraw(True)

for frame in range(fps * 3):
    win.flip()
    if frame % 10 == 0:
        set_fixstim_color(
            inner, [(1, 0, 0), (0, 1, 0), (0, 0, 1)][np.random.choice([0, 1, 2])]
        )


win.close()
# %%
win.close()
# %%
