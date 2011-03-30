"""
implementations of HMAC commands to execute on a YubiHSM
"""
# Copyright (c) 2011, Yubico AB
# All rights reserved.

import struct
import defines

__all__ = [
    # constants
    # functions
    # classes
    'YHSM_Cmd_Echo',
    'YHSM_Cmd_System_Info',
    'YHSM_Cmd_Random',
]

import exception
from cmd import YHSM_Cmd

class YHSM_Cmd_HMAC_SHA1_Write(YHSM_Cmd):
    """
    Calculate HMAC SHA1 using a key_handle in the YubiHSM.

    Set final=False to not get a hash generated for the initial request.
    """
    def __init__(self, stick, key_handle, data, flags = None, final = True):
        if flags != None and type(flags) is not int:
            raise exception.YHSM_WrongInputType(
                'flags', type(1), type(flags))
        if type(data) is not str:
            raise exception.YHSM_WrongInputType(
                'data', type(''), type(data))
        if len(data) > defines.YSM_MAX_PKT_SIZE - 6:
            raise exception.YHSM_InputTooLong(
                'data', defines.YSM_MAX_PKT_SIZE - 6, len(data))

        if flags == None:
            flags = defines.YSM_HMAC_RESET
            if final:
                flags |= defines.YSM_HMAC_FINAL

        self.final = final
        self.key_handle = key_handle
        self.flags = flags
        packed = _raw_pack(self.key_handle, self.flags, data)
        YHSM_Cmd.__init__(self, stick, defines.YSM_HMAC_SHA1_GENERATE, packed)

    def next(self, data, final = False):
        """
        Add more input to the HMAC SHA1.
        """
        if final:
            self.flags = defines.YSM_HMAC_FINAL
        else:
            self.flags = 0x0
        self.payload = _raw_pack(self.key_handle, self.flags, data)
        self.final = final
        return self

    def __repr__(self):
        if self.executed:
            return '<%s instance at %s: key_handle=0x%x, flags=0x%x>' % (
                self.__class__.__name__,
                hex(id(self)),
                self.key_handle,
                self.flags,
                )
        else:
            return '<%s instance at %s (not executed)>' % (
                self.__class__.__name__,
                hex(id(self))
                )

    def parse_result(self, data):
        # typedef struct {
        #   uint32_t keyHandle;                 // Key handle
        #   YHSM_STATUS status;                 // Status
        #   uint8_t numBytes;                   // Number of bytes in hash output
        #   uint8_t hash[SHA1_HASH_SIZE];       // Hash output (if applicable)
        # } YHSM_HMAC_SHA1_GENERATE_RESP;
        key_handle, \
             self.status, \
             num_bytes = struct.unpack_from('<IBB', data, 0)
        if self.status == defines.YSM_STATUS_OK:
            # struct.hash is not always of size SHA1_HASH_SIZE,
            # it is really the size of numBytes
            if num_bytes:
                sha1 = data[6:6 + num_bytes]
            else:
                sha1 = '\x00' * defines.SHA1_HASH_SIZE
            self.response = YHSM_GeneratedHMACSHA1(key_handle, sha1, self.final)
            return self.response
        else:
            raise exception.YHSM_CommandFailed('YHSM_HMAC_SHA1_GENERATE', self.status)

def _raw_pack(key_handle, flags, data):
    # #define YHSM_HMAC_RESET          0x01    // Flag to indicate reset at first packet
    # #define YHSM_HMAC_FINAL          0x02    // Flag to indicate that the hash shall be calculated
    # typedef struct {
    #   uint32_t keyHandle;                 // Key handle
    #   uint8_t flags;                      // Flags
    #   uint8_t numBytes;                   // Number of bytes in data packet
    #   uint8_t data[YHSM_MAX_PKT_SIZE - 6]; // Data to be written
    # } YHSM_HMAC_SHA1_GENERATE_REQ;
    return struct.pack('<IBB', key_handle, flags, len(data)) + data

class YHSM_GeneratedHMACSHA1():
    """ Small class to represent a YHSM_HMAC_SHA1_GENERATE_RESP. """
    def __init__(self, key_handle, sha1, final):
        self.key_handle = key_handle
        self.hash_result = sha1
        self.final = final

    def __repr__(self):
        return '<%s instance at %s: key_handle=0x%x, t(hash_result)=%s, final=%s>' % (
            self.__class__.__name__,
            hex(id(self)),
            self.key_handle,
            hash_result[:4].encode('hex'),
            self.final,
            )