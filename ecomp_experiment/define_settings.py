"""Provide constants for several settings in the experiment."""

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
DIGIT_FRAMES = int(EXPECTED_FPS / 2.75)
FADE_FRAMES = int(EXPECTED_FPS / 12)
MAXWAIT_RESPONSE_S = 3

# Eye-tracker settings
TK_DUMMY_MODE = True
CALIBRATION_TYPE = "HV5"

# Experiment settings
NSAMPLES = 8
NTRIALS = 2
BLOCKSIZE = 1
FULLSCR = False
