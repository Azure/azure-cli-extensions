# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from cryptography.hazmat import backends
import cryptography.hazmat.primitives
from cryptography.hazmat.primitives.asymmetric import rsa
import mock
import sys
import unittest

from azext_ssh import rsa_generator

class RSAGeneratorTest(unittest.TestCase):
    @mock.patch.object(backends, 'default_backend')
    @mock.patch.object(rsa, 'generate_private_key')
    def test_rsa_generator_default_generate(self, mock_generate, mock_backend):
        mock_key = mock.Mock()
        mock_generate.return_value = mock_key

        expected_public = mock.Mock()
        mock_key.public_key.return_value = expected_public
        mock_key.private_bytes.return_value = b'privatekey'

        generator = rsa_generator.RSAGenerator()

        with mock.patch.object(rsa_generator, 'serialization') as mock_serialization:
            actual_public, actual_private = generator.generate()

        self.assertEqual(expected_public, actual_public)
        self.assertEqual('privatekey', actual_private)
        mock_generate.assert_called_once_with(
            backend=mock_backend.return_value,
            public_exponent=65537,
            key_size=2048
        )
        mock_key.public_key.assert_called_once_with()
        mock_key.private_bytes.assert_called_once_with(
            mock_serialization.Encoding.PEM,
            mock_serialization.PrivateFormat.TraditionalOpenSSL,
            mock_serialization.NoEncryption.return_value
        )

    @mock.patch.object(backends, 'default_backend')
    @mock.patch.object(rsa, 'generate_private_key')
    def test_rsa_generator_custom_keysize_exponent(self, mock_generate, mock_backend):
        expected_exponent = 13
        expected_keysize = 4096

        generator = rsa_generator.RSAGenerator(exponent=expected_exponent, key_size=expected_keysize)

        with mock.patch.object(rsa_generator, 'serialization') as mock_serialization:
            actual_public, actual_private = generator.generate()

        mock_generate.assert_called_once_with(
            backend=mock_backend.return_value,
            public_exponent=expected_exponent,
            key_size=expected_keysize
        )

    def test_rsa_generator_public_key_to_openssh(self):
        mock_key = mock.Mock()
        mock_key.public_bytes.return_value = b'publickey'

        with mock.patch.object(rsa_generator, 'serialization') as mock_serialization:
            actual_public = rsa_generator.RSAGenerator.public_key_to_openssh(mock_key)

        self.assertEqual('publickey', actual_public)
        mock_key.public_bytes.assert_called_once_with(
            mock_serialization.Encoding.OpenSSH,
            mock_serialization.PublicFormat.OpenSSH
        )

    def test_rsa_generator_public_key_to_base64_modulus_exponent(self):
        mock_key = mock.Mock()
        mock_mod = mock.Mock()
        mock_exp = mock.Mock()

        mock_key.public_numbers.return_value.n = mock_mod
        mock_key.public_numbers.return_value.e = mock_exp

        mock_mod.bit_length.return_value = 100
        mock_exp.bit_length.return_value = 3

        with mock.patch('base64.urlsafe_b64encode') as mock_b64encode:
            mock_b64encode.side_effect = [b'b64mod', b'b64exp']
            mod, exp = rsa_generator.RSAGenerator.public_key_to_base64_modulus_exponent(mock_key)

        self.assertEqual('b64mod', mod)
        self.assertEqual('b64exp', exp)
        mock_mod.to_bytes.assert_called_once_with(13, byteorder='big')
        mock_exp.to_bytes.assert_called_once_with(1, byteorder='big')
        mock_b64encode.assert_any_call(mock_mod.to_bytes.return_value)
        mock_b64encode.assert_any_call(mock_exp.to_bytes.return_value)

if __name__ == '__main__':
    unittest.main()
