"""Provide constants for several settings in the experiment."""

# pick a monitor
monitor = "latitude7490"  # benq, latitude7490, eizoforis
MONITOR_NAME, EXPECTED_FPS = {
    "benq": ("benq", 144),
    "latitude7490": ("latitude7490", 60),
    "eizoforis": ("eizoforis", 60),
}[monitor]
