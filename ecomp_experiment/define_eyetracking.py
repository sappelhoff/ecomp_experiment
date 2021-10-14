"""Define eye-tracking for the experiment.

See also the eye-tracking directory for more information.
"""


from psychopy import event, visual


class DummyEyeLink:
    """Convenience class to run the code without true EyeLink connection."""


def setup_eyetracker(dummy_mode, mon, edf_fname, calibration_type):
    """Do setup and calibrate the EyeLink.

    A well documented version of this setup is described in the try_eyelink.py
    script in the eye-tracking/ directory.

    Parameters
    ----------
    dummy_mode : bool
        Whether or not to run in dummy mode.
    mon : psychopy.monitors.Monitor
        The monitor object to use for calibration.
    edf_fname : str
        The name of the file to save the eyetracking data to.
    calibration_type : {"HV5", "HV9"}
        The type of calibration to perform.

    Returns
    -------
    tk : DummyEyeLink | EyeLinkCBind
        Either a dummy object, or an EyeLink object.
    """
    # If we run in dummy mode, return early
    if dummy_mode:
        tk = DummyEyeLink()
        return tk

    # Else, we need to import some libraries
    import pylink
    from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy

    # And start the setup
    scn_w, scn_h = mon.getSizePix()

    tk = pylink.EyeLink("100.1.1.1")

    tk_version = tk.getTrackerVersion()
    assert tk_version == 3, "Expecting an Eyelink 1000 Plus"

    tvstr = tk.getTrackerVersionString()
    vindex = tvstr.find("EYELINK CL")
    host_version = int(float(tvstr[(vindex + len("EYELINK CL")) :].strip()))
    assert host_version == 5, "Expecting to work with version 5.x"

    assert (len(edf_fname) - len(".edf")) <= 8
    tk.openDataFile(edf_fname)

    tk.setOfflineMode()

    tk.sendMessage(f"DISPLAY_COORDS = 0 0 {scn_w - 1} {scn_h - 1}")
    tk.sendCommand("sample_rate 1000")
    tk.sendCommand(f"screen_pixel_coords = 0 0 {scn_w - 1} {scn_h - 1}")
    tk.sendCommand("add_file_preamble_text eComp")
    tk.sendCommand("recording_parse_type = GAZE")
    tk.sendCommand(f"calibration_type = {calibration_type}")
    tk.sendCommand("calibration_area_proportion 0.7 0.7")
    tk.sendCommand("validation_area_proportion  0.7 0.7")
    file_sample_data = "LEFT,RIGHT,GAZE,GAZERES,HREF,HTARGET,PUPIL,AREA,STATUS,INPUT"
    tk.sendCommand(f"file_sample_data  = {file_sample_data}")
    tk.sendCommand("file_event_data  = GAZE,GAZERES,AREA,HREF,VELOCITY")
    file_event_filter = "LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,INPUT"
    tk.sendCommand(f"file_event_filter = {file_event_filter}")

    # Do calibration
    win = visual.Window(
        size=(scn_w, scn_h),
        fullscr=False,
        monitor=mon,
        winType="pyglet",
        units="pix",
    )

    text_stim = visual.TextStim(
        win,
        text="Press ENTER twice to calibrate the eye-tracker",
    )
    text_stim.draw()
    win.flip()
    event.waitkeys()

    genv = EyeLinkCoreGraphicsPsychoPy(tk, win)
    pylink.openGraphicsEx(genv)

    tk.doTrackerSetup()

    text_stim.text = "Calibration done. Press any key to continue."
    text_stim.draw()
    win.flip()
    event.waitkeys()
    return tk
