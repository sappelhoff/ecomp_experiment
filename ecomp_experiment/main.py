"""Try this."""

# %%

import numpy as np
from psychopy import core, event, monitors, visual

from ecomp_experiment.define_routines import (
    display_block_break,
    display_iti,
    display_survey_gui,
    display_trial,
)
from ecomp_experiment.define_settings import EXPECTED_FPS, MONITOR_NAME
from ecomp_experiment.define_stimuli import (
    get_central_text_stim,
    get_choice_stims,
    get_digit_stims,
    get_fixation_stim,
)
from ecomp_experiment.define_trials import evaluate_trial_correct, gen_trials
from ecomp_experiment.utils import check_framerate, map_key_to_choice, save_dict

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
state_rng = np.random.default_rng()
block_counter = 1  # start with first block
for itrial, trial in enumerate(trials):

    # get state for this trial
    state = state_rng.choice([0, 1])

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

    # send timeout warning if choice too slow
    if choice == "n/a":
        warn_stim = get_central_text_stim(win, 1, "Too slow!", (1, -1, -1))
        for frame in range(fps):
            warn_stim.draw()
            win.flip()

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
        state=state,
    )
    samples = dict(
        zip([f"sample{i}" for i in range(1, 9)], [sample for sample in trial])
    )
    savedict.update(samples)
    save_dict(logfile, savedict)

    # Do a block break and display feedback
    block_counter = display_block_break(win, logfile, itrial, 2, 1, block_counter, 2)


win.close()


# %%
win.close()
# %%
