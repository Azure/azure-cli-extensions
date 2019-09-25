# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
from cryptography.hazmat import backends
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import sys


class RSAGenerator(object):
    def __init__(self, exponent=65537, key_size=2048):
        self._exponent = exponent
        self._key_size = key_size

    def generate(self):
        key = rsa.generate_private_key(
            backend=backends.default_backend(),
            public_exponent=self._exponent,
            key_size=self._key_size
        )

        public_key = key.public_key()

        private_key = key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption()
        ).decode('ascii')

        return public_key, private_key

    @staticmethod
    def public_key_to_openssh(public_key):
        return public_key.public_bytes(
            serialization.Encoding.OpenSSH,
            serialization.PublicFormat.OpenSSH
        )

    @staticmethod
    def public_key_to_base64_modulus_exponent(public_key):
        modulus = public_key.public_numbers().n
        exponent = public_key.public_numbers().e

        modulus_bytes = modulus.to_bytes(int(modulus.bit_length() / 8) + 1, byteorder='big')
        exponent_bytes = exponent.to_bytes(int(exponent.bit_length() / 8) + 1, byteorder='big')

        b64_modulus = base64.b64encode(modulus_bytes).decode('ascii')
        b64_exponent = base64.b64encode(exponent_bytes).decode('ascii')
        return b64_modulus, b64_exponent

    @staticmethod
    def _int_length(integer):
        return int(math.log(integer, 256)) + 1
