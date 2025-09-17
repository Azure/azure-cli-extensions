# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
import struct


# pylint: disable=too-few-public-methods
class RSAParser:
    RSAAlgorithm = 'ssh-rsa'

    def __init__(self):
        self.algorithm = ''
        self.modulus = ''
        self.exponent = ''
        self._key_length_big_endian = True

    def parse(self, public_key_text):
        text_parts = public_key_text.split(' ')
        if len(text_parts) < 2:
            raise ValueError("Incorrectly formatted public key. "
                             "Key must be format '<algorithm> <base64_key>'")

        algorithm = text_parts[0]
        if algorithm != self.RSAAlgorithm:
            raise ValueError(f"Public key is not ssh-rsa algorithm ({algorithm})")

        key_bytes = base64.b64decode(text_parts[1])
        fields = list(self._get_fields(key_bytes))
        if len(fields) < 3:
            raise ValueError("Incorrectly encoded public key. "
                             "Encoded key must be base64 encoded <algorithm><exponent><modulus>")

        encoded_algorithm = fields[0].decode("ascii")
        if encoded_algorithm != self.RSAAlgorithm:
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
        return ">" + "L" if self._key_length_big_endian else "<L"
