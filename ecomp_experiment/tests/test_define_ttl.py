"""Test the TTL trigger script for basic integrity."""
import time

from ecomp_experiment.define_ttl import (
    DUAL_STREAM_CONST,
    FakeSerial,
    MySerial,
    get_ttl_dict,
)


def test_get_ttl_dict():
    """Test that values in dict are unique."""
    ttl_dict = get_ttl_dict()

    # Should be a dict of byte values
    assert isinstance(ttl_dict, dict)
    for key, val in ttl_dict.items():

        # also test that "dual" triggers are the same but with an added constant
        if key.startswith("single_"):

            new_key = key.replace("single_", "dual_")

            assert isinstance(val, bytes)
            assert isinstance(ttl_dict[new_key], bytes)
            assert ord(ttl_dict[new_key]) - DUAL_STREAM_CONST == ord(val)

    # Trigger values should be unique
    trigger_values = list(ttl_dict.values())
    assert len(trigger_values) == len(set(trigger_values))


def test_serials():
    """Test the FakeSerial class."""
    some_byte = bytes([1])
    ser = FakeSerial()
    assert ser.write(some_byte) == some_byte

    # Also covers "perf_sleep"
    ser_waitsecs = 1
    ser = MySerial(ser, ser_waitsecs)
    start = time.perf_counter()
    ser.write(some_byte)
    stop = time.perf_counter()
    assert (stop - start) >= ser_waitsecs

    # Close it
    ser.ser.close()
