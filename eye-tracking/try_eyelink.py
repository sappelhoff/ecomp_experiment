"""Testing the EyeLink 1000 Plus eye-tracker.

- Done on Windows
- Must install Eyelink Developers Kit first
- Must download pylink via one of the options below:
    - pip install --index-url=https://pypi.sr-support.com sr-research-pylink
    - copy the library from the Eyelink Developers Kit to site-packages
    - install wheels that are shipped in the Eyelink Developers Kit
- Must download EyeLinkCoreGraphicsPsychopy
    - either include it as local module
    - or install via pip:
      pip install https://github.com/sappelhoff/EyeLinkCoreGraphicsPsychoPy/archive/main.tar.gz
- Eyelink ethernet connection to stimulus computer must be set up (see manual)
- Eyelink computer must be running, eye-tracker must be connected
- Install Python environment as for "ecomp_experiment"

"""  # noqa: E501
# %% imports
import datetime
import os

from psychopy import core, event, monitors, visual

try:
    import pylink
    from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy
except Exception as err:  # noqa: E722
    print("\n\nImporting pylink and/or EyeLinkCoreGraphicsPsychoPy failed.\n")
    if os.name != "nt":
        print("You are not on Windows - this script only works on Windows.\n\n")
    raise (err)


# %% Get psychopy monitor
monitor_name = "eizoforis"
assert (
    monitor_name in monitors.getAllMonitors()
), f"Monitor '{monitor_name}' is not defined."
my_monitor = monitors.Monitor(name=monitor_name)

# %% Get the screen resolution
scn_w, scn_h = my_monitor.getSizePix()

# %% Connect to the eye-tracker
# in Dummy mode, the tracker is not used.
tk_dummy_mode = False
if not tk_dummy_mode:
    tk = pylink.EyeLink("100.1.1.1")
else:
    tk = pylink.EyeLink(None)

# %% Assert we are working with the correct equipment

# get model of the tracker, 1-EyeLink I, 2-EyeLink II, 3-Newer models (100/1000Plus/DUO)
tk_version = tk.getTrackerVersion()
assert tk_version == 3, "Expecting an Eyelink 1000 Plus"

# get Host tracking software version
tvstr = tk.getTrackerVersionString()
vindex = tvstr.find("EYELINK CL")
host_version = int(float(tvstr[(vindex + len("EYELINK CL")) :].strip()))
assert host_version == 5, "Expecting to work with version 5.x"

# %% Open an EDF data file on the Host PC
# up to 8 characters, containing letters, numbers, and underscores (_) only.
month_day_hour_minute = datetime.datetime.today().strftime("%m%d%H%M")
edf_fname = f"{month_day_hour_minute}.edf"
assert (len(edf_fname) - len(".edf")) <= 8
tk.openDataFile(edf_fname)
tk.sendCommand("add_file_preamble_text 'RECORDED BY try_eyelink.py'")

# %% Prepare some settings for the EyeLink

# put tracker in offline mode before we change its configrations
tk.setOfflineMode()

# sampling rate, 250, 500, or 1000
tk.sendCommand("sample_rate 1000")

# inform tracker about display resolution (see Eyelink Installation Guide, Section 8.4)
tk.sendCommand(f"screen_pixel_coords = 0 0 {scn_w - 1} {scn_h - 1}")

# save display resolution in EDF data file for Data Viewer integration purposes
# (see Data Viewer User Manual, Section 7)
tk.sendMessage(f"DISPLAY_COORDS = 0 0 {scn_w - 1} {scn_h - 1}")

# data type used to compute velocity for parsing of eye movements during recording
# should be GAZE
tk.sendCommand("recording_parse_type = GAZE")

# specify the calibration type, for example HV5 or HV9
calibration_type = "HV5"
tk.sendCommand(f"calibration_type = {calibration_type}")

# specify the proportion of subject display to calibrate/validate
# (useful/needed for wide screen monitors)
tk.sendCommand("calibration_area_proportion 0.7 0.7")
tk.sendCommand("validation_area_proportion  0.7 0.7")

# Set EDF file contents (see section 4.6 in EyeLink manual)
# The following commands make the tracker record all important data
tk.sendCommand(
    "file_sample_data  = LEFT,RIGHT,GAZE,GAZERES,HREF,HTARGET,PUPIL,AREA,STATUS,INPUT"
)
tk.sendCommand("file_event_data  = GAZE,GAZERES,AREA,HREF,VELOCITY")
tk.sendCommand("file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,INPUT")

# %% Prepare for calibration
# Open a window using PsychoPy, not in fullscreen, for testing
win = visual.Window(
    size=(scn_w, scn_h),
    fullscr=False,
    monitor=my_monitor,
    winType="pyglet",
    units="pix",
)

text_stim = visual.TextStim(
    win,
    text="Press ENTER twice to calibrate the eye-tracker",
)
text_stim.draw()
win.flip()
event.waitKeys()

# open graphics environment
genv = EyeLinkCoreGraphicsPsychoPy(tk, win)
pylink.openGraphicsEx(genv)

# Do calibration
if not tk_dummy_mode:
    try:
        tk.doTrackerSetup()
    except RuntimeError as err:
        print("ERROR:", err)
        tk.exitCalibration()

text_stim.text = "Calibration done. Press any key to start recording."
text_stim.draw()
win.flip()
event.waitKeys()
win.flip()

# %% Record data for a bit

# record
error = tk.startRecording(1, 1, 1, 1)
assert error == 0

# send a message to the EyeLink, like a TTL trigger
tk.sendMessage("test starts")

# record until you press a key
text_stim.text = "Recording in progress ... Press any key to stop recording."
text_stim.draw()
win.flip()
event.waitKeys()

# stop recording
tk.sendMessage("test ends")
pylink.pumpDelay(100)
tk.stopRecording()

# close the EDF data file
tk.setOfflineMode()
tk.closeDataFile()
pylink.pumpDelay(100)

# Get the EDF data from the host PC to the stimulus PC
edf_local = os.path.join(os.path.expanduser("~"), "Desktop", edf_fname)
tk.receiveDataFile(edf_fname, edf_local)

# close the link to the tracker
tk.close()

# close the graphics
pylink.closeGraphics()

# close the psychopy window and exit
win.close()
core.quit()
