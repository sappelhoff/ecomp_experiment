# eye-tracking

## General information

**NOTE: All eye-tracking is intended to run only on Windows 10!**

The experiment can also be run without eye-tracking, see `define_settings.py`.

This experiment is developed with the following eye-tracking equipment by SR-Research Ltd. in mind:

- EyeLink 1000 Plus
- EyeLink Desktop Mount (DM-890)
- EyeLink High Speed 35mm lens (F=2.4) for DM-890/AM-890
- An EyeLink host computer (including monitor, keyboard, mouse)
- EyeLink "Target Stickers"
- A chinrest

The Eyelink host computer is set up as follows:

- Version 5.12 (at time of writing, the up-to-date version is 5.15)
- Configuration
    - Desktop (Remote mode)
    - Target Sticker
    - Monocular
    - 16/25mm lens
- See also EyeLink manual, section 3.2.3

The stimulus computer (aka, display computer) needs to following software installed:

- EyeLink Developers Kit (at least version 1.11.5, at time of writing, the up-to-date version is 2.1.1)
- Pylink for Python 3.8 (recommended to install using pip via SR-Research package index)
- EyeLinkCoreGraphicsPsychoPy (recommended to install using pip via https://github.com/sappelhoff/EyeLinkCoreGraphicsPsychoPy/)

The following materials are helpful for learning how to setup the EyeLink.
The PDFs are shipped in this repository, but can also be freely downloaded from the
SR-Research support forum after a (free) registration using an Email address and name:
https://www.sr-support.com

- `EyeLink 1000 Plus - User Manual 1.0.18.pdf`
- `Quick Start Guide - EyeLink 1000 Plus - Dell Workstation Version 5.11W.pdf`
- `EyeLink 1000 Plus - Install Guide 1.0.18.pdf`
- `Getting started with Python and Pylink.pdf`
- `Pylink api userguide.pdf`

The installation files for the EyeLink Developers Kit and the EyeLink host PC software can
be downloaded from the SR-Research support forum.
These files are not included in this repository, because they are too large.
In case the pylink software is not available via the SR-Research package index,
you can obtain it after installing the EyeLink Developers Kit.
Please refer to the manuals.

## Python "try out script"

See `try_eyelink.py`.

## Recommendations and hints

Page numbers refer to the EyeLink Manual.

- In the EyeLink host PC, leave the "File Sample Filter" setting on "Extra" at all times (p.100)
- Set the Eyelink to the "cognitive" configuration (p.105)
- EyeLink should be switched on at least 15 minutes before recording (p.58)
- The lens settings on the host PC must match the physically used lens (section 3.2.3)
- Eyes of participant should be level with top quarter of screen (section 3.2.3)
- Eye-tracker should be 60cm away from the participant's eyes (section 3.2.3)
- Sticker should be on the forehead between the two eyes (section 3.2.3)
- If CR signal not reliable, or pupil threshold >> 120, set illuminator to 75% (p.69)
- You can edit the EyeLink host PC settings via the stimulus computer's browser. Type in this address: `100.1.1.1` (p.12)
- Look up any confusing `sendCommand` calls in the INI files you can find on the EyeLink host PC.

## Glossary

- HREF --> eye-rotation angle
- GAZE --> display-gaze coordinates
