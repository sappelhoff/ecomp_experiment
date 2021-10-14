"""Test those parts of eye-tracking scripts that we easily can in CI."""

from ecomp_experiment.define_eyetracking import (
    DummyEyeLink,
    setup_eyetracker,
    start_eye_recording,
    stop_eye_recording,
)


def test_dummy_eyelink():
    """Test the dummy."""
    tk = setup_eyetracker(True, 1, 2, 3)
    assert isinstance(tk, DummyEyeLink)

    msg_send = "test"
    msg_rec = tk.sendMessage(msg_send)
    assert msg_rec == msg_send

    start_eye_recording(tk)

    stop_eye_recording(tk, 1, 2)
