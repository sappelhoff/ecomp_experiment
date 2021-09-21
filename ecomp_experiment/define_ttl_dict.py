"""Definitions for the TTL triggers to be sent.

We have a "single" and a "dual" task, which will be performed in separate EEG recordings
that are then optionally concatenated for analysis.
Both tasks will have the same number of events,
hence we will use the same number of TTL triggers.
However all TTL trigger codes for the "dual" task will be incremented by a constant.

"""

DUAL_STREAM_CONST = 100


def get_ttl_dict():
    """Provide a dictionnary mapping str names to byte values."""
    ttl_dict = {}

    # At the beginning and end of the experiment ... take these triggers to
    # crop the meaningful EEG data. Make sure to include some time BEFORE and
    # AFTER the triggers so that filtering does not introduce artifacts into
    # important parts.
    ttl_dict["single_begin_experiment"] = bytes([1])
    ttl_dict["single_end_experiment"] = bytes([2])

    # Indication when a new trial is started
    ttl_dict["single_new_trl"] = bytes([3])

    # Generate the triggers for the "dual" task
    dict_to_add = {}
    for key, val in ttl_dict.items():
        new_key = key.replace("single_", "dual_")
        new_val = ord(val) + DUAL_STREAM_CONST
        dict_to_add[new_key] = bytes([new_val])
    ttl_dict.update(dict_to_add)

    return ttl_dict
