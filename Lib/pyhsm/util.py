"""
collection of utility functions
"""

# Copyright (c) 2011, Yubico AB
# All rights reserved.

import struct
import exception

__all__ = [
    # constants
    # functions
    'hexdump',
    'group',
    'key_handle_to_int',
    # classes
]

def hexdump(src, length=8):
    """ Produce a string hexdump of src, for debug output."""
    if not src:
        return str(src)
    if type(src) is not str:
        raise Exception('Hexdump \'src\' must be string (got %s)' % type(src))
    offset = 0
    result = ''
    for this in group(src, length):
        hex_s = ' '.join(["%02x" % ord(x) for x in this])
        result += "%04X   %s\n" % (offset, hex_s)
        offset += length
    return result

def group(data, num):
    """ Split data into chunks of num chars each """
    return [data[i:i+num] for i in xrange(0, len(data), num)]

def key_handle_to_int(this):
    """
    Turn "123" into 123 and "KSM1" into 827151179
    (0x314d534b, 'K' = 0x4b, S = '0x53', M = 0x4d).

    YHSM is little endian, so this makes the bytes KSM1 appear
    in the most human readable form in packet traces.
    """
    try:
        n = int(this)
        return n
    except ValueError:
        if this[:2] == "0x":
            return int(this, 16)
        if (len(this) == 4):
            n = struct.unpack('<I', this)[0]
            return n
    raise exception.YHSM_Error("Could not parse key_handle '%s'" % (this))