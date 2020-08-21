# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
import struct


class RSAParser(object):
    # pylint: disable=too-few-public-methods
    RSAAlgorithm = 'ssh-rsa'

    def __init__(self):
        self.algorithm = ''
        self.modulus = ''
        self.exponent = ''
        self._key_length_big_endian = True

    def parse(self, public_key_text):
        text_parts = public_key_text.split(' ')

        if len(text_parts) < 2:
            error_str = ("Incorrectly formatted public key. "
                         "Key must be format '<algorithm> <base64_key>'")
            raise ValueError(error_str)

        algorithm = text_parts[0]
        if algorithm != RSAParser.RSAAlgorithm:
            raise ValueError(f"Public key is not ssh-rsa algorithm ({algorithm})")

        b64_string = text_parts[1]
        key_bytes = base64.b64decode(b64_string)
        fields = list(self._get_fields(key_bytes))

        if len(fields) < 3:
            error_str = ("Incorrectly encoded public key. "
                         "Encoded key must be base64 encoded <algorithm><exponent><modulus>")
            raise ValueError(error_str)

        encoded_algorithm = fields[0].decode("ascii")
        if encoded_algorithm != RSAParser.RSAAlgorithm:
            raise ValueError(f"Encoded public key is not ssh-rsa algorithm ({encoded_algorithm})")

        self.algorithm = encoded_algorithm
        self.exponent = base64.urlsafe_b64encode(fields[1]).decode("ascii")
        self.modulus = base64.urlsafe_b64encode(fields[2]).decode("ascii")

    def _get_fields(self, key_bytes):
        read = 0
        while read < len(key_bytes):
            length = struct.unpack(self._get_struct_format(), key_bytes[read:read + 4])[0]
            read = read + 4
            data = key_bytes[read:read + length]
            read = read + length
            yield data

    def _get_struct_format(self):
        format_start = ">" if self._key_length_big_endian else "<"
        return format_start + "L"
