"""Provide constants for several settings in the experiment."""

import numpy as np

# pick a monitor
monitor = "benq"  # benq, latitude7490, eizoforis
MONITOR_NAME, EXPECTED_FPS = {
    "benq": ("benq", 144),
    "latitude7490": ("latitude7490", 60),
    "eizoforis": ("eizoforis", 144),
}[monitor]


# Serial port for sending TTL triggers to EEG
# INSTRUCTIONS TRIGGER BOX
# https://www.brainproducts.com/downloads.php?kid=40
# Open the Windows device manager,
# search for the "TriggerBox VirtualSerial Port (COM4)"
# in "Ports /COM & LPT)" and enter the COM port number in the constructor.
# If there is no TriggerBox, set SER_ADDRESS to None
SER_ADDRESS = None  # "COM4"
SER_WAITSECS = 0.005  # depending on sampling frequncy: at 1000Hz, must be >= 0.001s

# Define stimuli lengths
MIN_ITI_MS = 500
MAX_ITI_MS = 1500

# times we want to *show* and *fade* a digit. Try to get as close as possible, given FPS
digit_ms = 270
fade_ms = 80
DIGIT_FRAMES = int(np.round(digit_ms / (1000 / EXPECTED_FPS)))
FADE_FRAMES = int(np.round(fade_ms / (1000 / EXPECTED_FPS)))

MAXWAIT_RESPONSE_S = 3
TRAINING_FEEDBACK_FRAMES = EXPECTED_FPS * 2

feedback_ms = 350
FEEDBACK_FRAMES = int(np.round(feedback_ms / (1000 / EXPECTED_FPS)))

TIMEOUT_FRAMES = EXPECTED_FPS
FIXSTIM_OFF_FRAMES = int(np.ceil(EXPECTED_FPS / 2))

delay_feedback_ms = 100
DELAY_FEEDBACK_FRAMES = int(np.round(delay_feedback_ms / (1000 / EXPECTED_FPS)))

# Eye-tracker settings
TK_DUMMY_MODE = True
CALIBRATION_TYPE = "HV5"

# other settings
DIGIT_HEIGHT_DVA = 4
TEXT_HEIGHT_DVA = 1
CHOICE_STIM_HEIGHT_DVA = 2
NSAMPLES = 10
NTRIALS = 300
BLOCKSIZE = 50
HARD_BREAK = 2
FULLSCR = False
SHOW_FEEDBACK = True

NTRIALS_TRAINING = 10
BLOCKSIZE_TRAINING = 5
HARD_BREAK_TRAINING = 2

# acceptable keys to respond for actions "left", "right", and "quit"
KEYLIST_DICT = dict(left=["left", "s"], right=["right", "d"], quit=["escape"])
