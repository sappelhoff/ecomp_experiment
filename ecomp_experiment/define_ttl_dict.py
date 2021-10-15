"""Definitions for the TTL triggers to be sent.

We have a "single" and a "dual" task, which will be performed in separate EEG recordings
that are then optionally concatenated for analysis.
Both tasks will have the same number of events,
hence we will use the same number of TTL triggers.
However all TTL trigger codes for the "dual" task will be incremented by a constant.

"""

from time import perf_counter

import serial

DUAL_STREAM_CONST = 100


def send_trigger(ser, tk, byte):
    """Send an event code to serial and eye-tracker."""
    ser.write(byte)
    tk.sendMessage(f"{ord(byte)}")


def get_ttl_dict():
    """Provide a dictionnary mapping str names to byte values."""
    ttl_dict = {}

    # At the beginning and end of the experiment ... take these triggers to
    # crop the meaningful EEG data. Make sure to include some time BEFORE and
    # AFTER the triggers so that filtering does not introduce artifacts into
    # important parts.
    ttl_dict["single_begin_experiment"] = bytes([1])
    ttl_dict["single_end_experiment"] = bytes([2])

    # New trial starts
    ttl_dict["single_new_trl"] = bytes([3])

    # first fixstim offset in trial
    ttl_dict["single_fixstim_offset"] = bytes([4])

    # Show a digit
    ttl_dict["single_digit_1"] = bytes([11])
    ttl_dict["single_digit_2"] = bytes([12])
    ttl_dict["single_digit_3"] = bytes([13])
    ttl_dict["single_digit_4"] = bytes([14])
    ttl_dict["single_digit_5"] = bytes([15])
    ttl_dict["single_digit_6"] = bytes([16])
    ttl_dict["single_digit_7"] = bytes([17])
    ttl_dict["single_digit_8"] = bytes([18])
    ttl_dict["single_digit_9"] = bytes([19])

    # prompt a response
    ttl_dict["single_response_prompt"] = bytes([5])

    # participant took to long to respond
    ttl_dict["single_response_timeout"] = bytes([6])

    # valid participant respones
    ttl_dict["single_response_lower"] = bytes([7])
    ttl_dict["single_response_higher"] = bytes([8])
    ttl_dict["single_response_blue"] = bytes([9])
    ttl_dict["single_response_red"] = bytes([10])

    # feedback: timeout warning
    ttl_dict["single_feedback_timeout"] = bytes([20])

    # feedback: block break
    ttl_dict["single_feedback_break_begin"] = bytes([21])
    ttl_dict["single_feedback_break_end"] = bytes([22])

    # Generate the triggers for the "dual" task
    dict_to_add = {}
    for key, val in ttl_dict.items():
        new_key = key.replace("single_", "dual_")
        new_val = ord(val) + DUAL_STREAM_CONST
        dict_to_add[new_key] = bytes([new_val])
    ttl_dict.update(dict_to_add)

    return ttl_dict


class FakeSerial:
    """Convenience class to run the code without true serial connection."""

    def write(self, byte):
        """Take a byte and do nothing."""
        return byte


class MySerial:
    """Convenience class that always resets the event marker to zero."""

    def __init__(self, ser, waitsecs):
        """Take a serial object, and a time to wait before resetting.

        Parameters
        ----------
        ser : str | serial.Serial | FakeSerial
            A (optionally "fake") serial port object or an address of a serial port.
        waitsecs : float
            Time in seconds to wait until resetting the serial port to zero.
        """
        if isinstance(ser, (serial.Serial, FakeSerial)):
            self.ser = ser
        else:
            self.ser = serial.Serial(ser)
        self.waitsecs = waitsecs
        self.reset_val = bytes([0])

    def write(self, byte):
        """Take a byte, write it, and reset to zero."""
        self.ser.write(byte)
        perf_sleep(self.waitsecs)
        self.ser.write(self.reset_val)


def perf_sleep(waitsecs):
    """Block execution of further code for `waitsecs` seconds."""
    twaited = 0
    start = perf_counter()
    while twaited < waitsecs:
        twaited = perf_counter() - start
