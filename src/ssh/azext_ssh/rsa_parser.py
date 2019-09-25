# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
import functools
import struct
import sys


class RSAParser(object):
    def __init__(self):
        self.algorithm = ''
        self.modulus = ''
        self.exponent = ''
        self._key_length_big_endian = True

    def parse(self, b64_string):
        key_bytes = base64.b64decode(b64_string)
        fields = list(self._get_fields(key_bytes))

        self.algorithm = fields[0].decode("ascii")
        self.exponent = base64.b64encode(fields[1]).decode("ascii")
        self.modulus = base64.b64encode(fields[2]).decode("ascii")

    def _get_fields(self, key_bytes):
        read = 0
        while read < len(key_bytes):
            length = struct.unpack(self._get_struct_format(), key_bytes[read:read+4])[0]
            read = read + 4
            data = key_bytes[read:read + length]
            read = read + length
            yield data

    def _get_struct_format(self):
        format_start = ">" if self._key_length_big_endian else "<"
        return format_start + "L"