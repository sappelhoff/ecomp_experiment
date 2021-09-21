"""Test importing the monitors.

By calling this test, you will define the monitors as in define_monitors.py

"""
import subprocess

from psychopy import monitors


def test_monitors():
    """Test that monitors get defined."""
    # must be called from root of package
    cmd = ["python", "ecomp_experiment/define_monitors.py"]
    subprocess.call(cmd)
    my_monitors = monitors.getAllMonitors()
    for mon in ["eizoforis", "latitude7490"]:
        assert mon in my_monitors, f"not present: {mon}"
