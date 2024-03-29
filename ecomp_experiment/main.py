"""Main flow of the eComp experiment."""

# %%
import datetime

import numpy as np
from psychopy import core, event, monitors, visual

from ecomp_experiment.define_eyetracking import (
    setup_eyetracker,
    start_eye_recording,
    stop_eye_recording,
)
from ecomp_experiment.define_routines import (
    display_block_break,
    display_instructions,
    display_iti,
    display_survey_gui,
    display_trial,
)
from ecomp_experiment.define_settings import (
    BLOCKSIZE,
    BLOCKSIZE_TRAINING,
    CALIBRATION_TYPE,
    CHOICE_STIM_HEIGHT_DVA,
    DELAY_FEEDBACK_FRAMES,
    DIGIT_FRAMES,
    DIGIT_HEIGHT_DVA,
    EXPECTED_FPS,
    FADE_FRAMES,
    FEEDBACK_FRAMES,
    FIXSTIM_OFF_FRAMES,
    FULLSCR,
    HARD_BREAK,
    HARD_BREAK_TRAINING,
    KEYLIST_DICT,
    MAX_ITI_MS,
    MAXWAIT_RESPONSE_S,
    MIN_ITI_MS,
    MONITOR_NAME,
    NSAMPLES,
    NTRIALS,
    NTRIALS_TRAINING,
    SAME_TRIALS_OVER_CONDITIONS,
    SER_ADDRESS,
    SER_WAITSECS,
    SHOW_FEEDBACK,
    TEXT_HEIGHT_DVA,
    TIMEOUT_FRAMES,
    TK_DUMMY_MODE,
    TRAINING_FEEDBACK_FRAMES,
)
from ecomp_experiment.define_stimuli import (
    get_central_text_stim,
    get_choice_stims,
    get_digit_stims,
    get_fixation_stim,
)
from ecomp_experiment.define_trials import evaluate_trial_correct, gen_trials
from ecomp_experiment.define_ttl import FakeSerial, MySerial, get_ttl_dict, send_trigger
from ecomp_experiment.utils import check_framerate, map_key_to_choice, save_dict

# Prepare logging
run_type, streamdir, stream, substr = display_survey_gui()

# *if just bonus*, display and quit.
if run_type == "bonus":
    core.quit()

# *if just training*, adjust trials.
if run_type == "training":
    ntrials = NTRIALS_TRAINING
    blocksize = BLOCKSIZE_TRAINING
    hard_break = HARD_BREAK_TRAINING
else:
    ntrials = NTRIALS
    blocksize = BLOCKSIZE
    hard_break = HARD_BREAK

# Prepare monitor
my_monitor = monitors.Monitor(name=MONITOR_NAME)

# prepare the window
width, height = my_monitor.getSizePix()

win = visual.Window(
    color=(-1, -1, -1),
    fullscr=FULLSCR,
    monitor=my_monitor,
    units="deg",
    winType="pyglet",
    size=(width, height),
)
win.mouseVisible = False

fps = check_framerate(win, EXPECTED_FPS)

# *if just instructions*, display and quit.
if run_type == "instructions":
    display_instructions(win, stream)
    win.close()
    core.quit()

# Prepare logfile
if streamdir is not None:
    logfile = streamdir / f"sub-{substr}_stream-{stream}_beh.tsv"

# Prepare eyetracking
# (only track eyes in "experiment" mode and if TK_DUMMY_MODE is False)
month_day_hour_minute = datetime.datetime.today().strftime("%m%d%H%M")
edf_fname = f"{month_day_hour_minute}.edf"
tk_dummy_mode = TK_DUMMY_MODE if run_type == "experiment" else True
tk = setup_eyetracker(tk_dummy_mode, my_monitor, edf_fname, CALIBRATION_TYPE)

# prepare the trials
trlgen_seed = None
if (substr != "test") and (substr is not None) and SAME_TRIALS_OVER_CONDITIONS:
    # subjs get the same trials for single and dual
    trlgen_seed = int(substr)
trials = gen_trials(ntrials, NSAMPLES, seed=trlgen_seed)

# get stimuli
digit_stims = get_digit_stims(win, height=DIGIT_HEIGHT_DVA)

outer, inner, horz, vert = get_fixation_stim(win)
fixation_stim_parts = [outer, horz, vert, inner]

# Start eye-tracking
error = start_eye_recording(tk)
assert error == 0, "Problem during eye-tracker setup."

# Setup serial port
ttl_dict = get_ttl_dict()

if SER_ADDRESS is None:
    ser_port = MySerial(FakeSerial(), waitsecs=SER_WAITSECS)
    print("No serial port specified. We will not send TTL triggers to EEG.")
else:
    ser_port = MySerial(SER_ADDRESS, waitsecs=SER_WAITSECS)

trigger_kwargs = dict(ser=ser_port, tk=tk, byte=bytes([0]))
send_trigger(**trigger_kwargs)

# Start experiment
# ----------------
key_list = [key for action_list in KEYLIST_DICT.values() for key in action_list]
start_stim = get_central_text_stim(
    win,
    height=TEXT_HEIGHT_DVA,
    text="-> Please wait for the experimenter. <-",
)
start_stim.draw()
win.flip()
event.waitKeys(keyList=KEYLIST_DICT["quit"])

start_stim.text = "Press any key to start."
start_stim.draw()
win.flip()
event.waitKeys()

# Show fixstim
for stim in fixation_stim_parts:
    stim.setAutoDraw(True)
win.flip()

trigger_kwargs["byte"] = ttl_dict[f"{stream}_begin_experiment"]
send_trigger(**trigger_kwargs)
core.wait(1)

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
    trigger_kwargs["byte"] = ttl_dict[f"{stream}_new_trl"]
    iti_ms = display_iti(win, MIN_ITI_MS, MAX_ITI_MS, fps, iti_rng, trigger_kwargs)

    # 500ms before first sample onset, remove fixstim
    for stim in fixation_stim_parts:
        stim.setAutoDraw(False)

    trigger_kwargs["byte"] = ttl_dict[f"{stream}_fixstim_offset"]
    win.callOnFlip(send_trigger, **trigger_kwargs)
    for frame in range(FIXSTIM_OFF_FRAMES):
        win.flip()

    # show samples
    trigger_kwargs_list = [
        dict(ser=ser_port, tk=tk, byte=ttl_dict[f"{stream}_digit_{int(digit)}"])
        for digit in trial
    ]
    display_trial(
        win,
        trial,
        digit_frames=DIGIT_FRAMES,
        fade_frames=FADE_FRAMES,
        digit_stims=digit_stims,
        trigger_kwargs_list=trigger_kwargs_list,
    )

    # get choice from participant
    choice_stims = get_choice_stims(
        win, stream=stream, state=state, height=CHOICE_STIM_HEIGHT_DVA
    )
    for stim in choice_stims:
        stim.draw()

    trigger_kwargs["byte"] = ttl_dict[f"{stream}_response_prompt"]
    win.callOnFlip(send_trigger, **trigger_kwargs)
    rt_clock.reset()
    win.flip()
    key_rt = event.waitKeys(
        maxWait=MAXWAIT_RESPONSE_S,
        keyList=key_list,
        timeStamped=rt_clock,
    )

    if key_rt is None:
        trigger_kwargs["byte"] = ttl_dict[f"{stream}_response_timeout"]
        send_trigger(**trigger_kwargs)
        key = "n/a"
        choice = "n/a"
        rt = "n/a"
        valid = False
    else:
        assert len(key_rt) == 1
        key = key_rt[0][0]
        if key in KEYLIST_DICT["quit"]:
            print(f"\n\nYou pressed the '{key}' key, quitting now ...")
            win.close()
            core.quit()
        choice = map_key_to_choice(key, state, stream)
        trigger_kwargs["byte"] = ttl_dict[f"{stream}_response_{choice}"]
        send_trigger(**trigger_kwargs)
        rt = key_rt[0][1]
        valid = True

    # evaluate correctness of choice
    correct, ambiguous = evaluate_trial_correct(trial, choice, stream)

    # delay feedback
    for frame in range(DELAY_FEEDBACK_FRAMES):
        win.flip()

    # show feedback
    show_feedback = (run_type == "training") or SHOW_FEEDBACK
    if choice == "n/a":
        # timeout feedback is always shown
        trigger_kwargs["byte"] = ttl_dict[f"{stream}_feedback_timeout"]
        win.callOnFlip(send_trigger, **trigger_kwargs)
        warn_stim = get_central_text_stim(
            win, height=TEXT_HEIGHT_DVA, text="Too slow!", color=(1, -1, -1)
        )
        for frame in range(TIMEOUT_FRAMES):
            warn_stim.draw()
            win.flip()
    elif show_feedback:
        # training feedback is always shown
        # to show all other feedback, set SHOW_FEEDBACK=True
        correct_str = "correct" if correct else "wrong"
        trigger_kwargs["byte"] = ttl_dict[f"{stream}_feedback_{correct_str}"]
        win.callOnFlip(send_trigger, **trigger_kwargs)
        feedback_stim = get_central_text_stim(win, height=TEXT_HEIGHT_DVA)
        if run_type == "training":
            feedback_stim.text = f"Your choice ({choice}) was {correct_str}."
            feedback_frames = TRAINING_FEEDBACK_FRAMES
        else:
            feedback_stim.text = f"{correct_str}"
            feedback_stim.color = (-1, 1, -1) if correct else (1, 0, -1)
            feedback_frames = FEEDBACK_FRAMES

        for frame in range(feedback_frames):
            feedback_stim.draw()
            win.flip()

    # Map pressed key to "direction" left/right
    key2direction_map = {i: key for key, val in KEYLIST_DICT.items() for i in val}
    direction = key2direction_map.get(key, "n/a")

    # Save trial data
    savedict = dict(
        trial=itrial,
        direction=direction,
        choice=choice,
        ambiguous=ambiguous,
        rt=rt,
        validity=valid,
        iti=iti_ms,
        correct=correct,
        stream=stream,
        state=state,
    )
    samples = dict([(f"sample{i+1}", int(sample)) for i, sample in enumerate(trial)])
    savedict.update(samples)
    save_dict(logfile, savedict)

    # Every nth trial, do a block break and display feedback
    if (1 + itrial) % blocksize == 0:
        trigger_kwargs["byte"] = ttl_dict[f"{stream}_feedback_break_begin"]
        block_counter = display_block_break(
            win,
            logfile,
            itrial,
            ntrials,
            blocksize,
            block_counter,
            hard_break=hard_break,
            trigger_kwargs=trigger_kwargs,
        )
        trigger_kwargs["byte"] = ttl_dict[f"{stream}_feedback_break_end"]
        send_trigger(**trigger_kwargs)


# Finish experiment
end_stim = get_central_text_stim(
    win,
    height=TEXT_HEIGHT_DVA,
    text="Done so far. Thanks for doing this task!",
)
end_stim.draw()
win.flip()
core.wait(2)
trigger_kwargs["byte"] = ttl_dict[f"{stream}_end_experiment"]
send_trigger(**trigger_kwargs)


# Stop eye-tracking and get the data
edf_fname_local = str(streamdir / f"sub-{substr}_stream-{stream}_eyetrack.edf")
stop_eye_recording(tk, edf_fname, edf_fname_local)

# Close and exit
ser_port.ser.close()
win.close()
core.quit()
