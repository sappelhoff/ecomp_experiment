"""Provide constants for several settings in the experiment."""

# pick a monitor
monitor = "benq"  # benq, latitude7490, eizoforis
MONITOR_NAME, EXPECTED_FPS = {
    "benq": ("benq", 144),
    "latitude7490": ("latitude7490", 60),
    "eizoforis": ("eizoforis", 60),
}[monitor]


# Serial port for sending TTL triggers to EEG
# INSTRUCTIONS TRIGGER BOX
# https://www.brainproducts.com/downloads.php?kid=40
# Open the Windows device manager,
# search for the "TriggerBox VirtualSerial Port (COM6)"
# in "Ports /COM & LPT)" and enter the COM port number in the constructor.
# If there is no TriggerBox, set ser to None
SER = None
