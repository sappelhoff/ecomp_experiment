"""Main flow of the eComp experiment."""

# %%

import numpy as np
from psychopy import core, event, monitors, visual

from ecomp_experiment.define_routines import (
    display_block_break,
    display_instructions,
    display_iti,
    display_survey_gui,
    display_trial,
)
from ecomp_experiment.define_settings import (
    EXPECTED_FPS,
    MONITOR_NAME,
    SER_ADDRESS,
    SER_WAITSECS,
    FakeSerial,
    MySerial,
    get_ttl_dict,
)
from ecomp_experiment.define_stimuli import (
    get_central_text_stim,
    get_choice_stims,
    get_digit_stims,
    get_fixation_stim,
)
from ecomp_experiment.define_trials import evaluate_trial_correct, gen_trials
from ecomp_experiment.utils import check_framerate, map_key_to_choice, save_dict

# Prepare logging
run_type, streamdir, stream = display_survey_gui()
if streamdir is not None:
    logfile = streamdir / "data.tsv"

# prepare the trials
trials = gen_trials(2)

# prepare the window
my_monitor = monitors.Monitor(name=MONITOR_NAME)
width, height = my_monitor.getSizePix()

win = visual.Window(
    color=(-1, -1, -1),
    fullscr=True,
    monitor=my_monitor,
    units="deg",
    winType="pyglet",
    size=(width, height),
)

fps = check_framerate(win, EXPECTED_FPS)

# *if just instructions*, display and quit.
if run_type == "instructions":
    display_instructions(win, stream)
    win.close()
    core.quit()

# get stimuli
digit_stims = get_digit_stims(win, height=5)

outer, inner, horz, vert = get_fixation_stim(win)
fixation_stim_parts = [outer, horz, vert, inner]

# Setup serial port
ttl_dict = get_ttl_dict()

if SER_ADDRESS is None:
    ser_port = FakeSerial()
    print("No serial port specified. We will not send TTL triggers to EEG.")
else:
    ser_port = MySerial(SER_ADDRESS, waitsecs=SER_WAITSECS)

# Start experiment
# ----------------
value = ttl_dict[f"{stream}_begin_experiment"]
ser_port.write(value)

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

    # 500ms before first sample onset, remove fixstim
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
    key_rt = event.waitKeys(
        maxWait=3, keyList=["left", "right", "escape"], timeStamped=rt_clock
    )

    if key_rt is None:
        choice = "n/a"
        rt = "n/a"
        valid = False
    else:
        assert len(key_rt) == 1
        key = key_rt[0][0]
        if key == "escape":
            print("\n\nYou pressed the 'escape' key, quitting now ...")
            core.quit()
        choice = map_key_to_choice(key, state, stream)
        rt = key_rt[0][1]
        valid = True

    # evaluate correctness of choice
    correct, ambiguous = evaluate_trial_correct(trial, choice, stream)

    # send feedback *if training trials*
    if (run_type == "training") and (choice != "n/a"):
        correct_str = "correct" if correct else "wrong"
        msg = f"Your choice ({choice}) was {correct_str}."
        training_stim = get_central_text_stim(win, 1, msg, (1, 1, 1))
        for frame in range(fps * 3):
            training_stim.draw()
            win.flip()

    # send timeout warning *if choice too slow*
    if choice == "n/a":
        warn_stim = get_central_text_stim(win, 1, "Too slow!", (1, -1, -1))
        for frame in range(fps):
            warn_stim.draw()
            win.flip()

    # Save trial data
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
    samples = dict([(f"sample{i+1}", sample) for i, sample in enumerate(trial)])
    savedict.update(samples)
    save_dict(logfile, savedict)

    # Every nth trial, do a block break and display feedback
    block_counter = display_block_break(win, logfile, itrial, 2, 1, block_counter, 2)


# Finish experiment
win.close()
