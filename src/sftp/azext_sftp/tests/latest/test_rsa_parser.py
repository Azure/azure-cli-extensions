# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest import mock

from azext_sftp import rsa_parser


class RSAParserTest(unittest.TestCase):
    """Test suite for RSAParser class.
    
    Owner: johnli1
    """

    def test_rsa_parser_success(self):
        """Test successful parsing of a valid RSA public key."""
        public_key_text = 'ssh-rsa ' + self._get_good_key()
        parser = rsa_parser.RSAParser()

        parser.parse(public_key_text)

        self.assertEqual('ssh-rsa', parser.algorithm)
        self.assertEqual(self._get_good_modulus(), parser.modulus)
        self.assertEqual(self._get_good_exponent(), parser.exponent)

    def test_rsa_parser_too_few_public_key_text_fields(self):
        """Test error when public key text has insufficient fields."""
        public_key_text = 'algo'
        parser = rsa_parser.RSAParser()

        with self.assertRaises(ValueError) as context:
            parser.parse(public_key_text)
        
        self.assertIn("Incorrectly formatted public key", str(context.exception))

    def test_rsa_parser_wrong_algorithm(self):
        """Test error when public key uses wrong algorithm."""
        public_key_text = 'wrongalgo key'
        parser = rsa_parser.RSAParser()

        with self.assertRaises(ValueError) as context:
            parser.parse(public_key_text)
        
        self.assertIn("Public key is not ssh-rsa algorithm", str(context.exception))

    @mock.patch('base64.b64decode')
    def test_rsa_parser_algorithm_mismatch(self, mock_decode):
        """Test error when decoded algorithm doesn't match ssh-rsa."""
        public_key_text = 'ssh-rsa key'
        parser = rsa_parser.RSAParser()

        with mock.patch.object(parser, '_get_fields') as mock_get_fields:
            mock_get_fields.return_value = [b'otheralgo', b'exp', b'mod']
            
            with self.assertRaises(ValueError) as context:
                parser.parse(public_key_text)
            
            self.assertIn("Encoded public key is not ssh-rsa algorithm", str(context.exception))

        mock_decode.assert_called_once_with('key')
        mock_get_fields.assert_called_once_with(mock_decode.return_value)

    @mock.patch('base64.b64decode')
    def test_rsa_parser_too_few_encoded_fields(self, mock_decode):
        """Test error when decoded key has too few fields."""
        public_key_text = 'ssh-rsa key'
        mock_decode.return_value = b'decodedkey'
        parser = rsa_parser.RSAParser()

        with mock.patch.object(parser, '_get_fields') as mock_get_fields:
            mock_get_fields.return_value = [b'ssh-rsa', b'exp']
            
            with self.assertRaises(ValueError) as context:
                parser.parse(public_key_text)
            
            self.assertIn("Incorrectly encoded public key", str(context.exception))

        mock_decode.assert_called_once_with('key')
        mock_get_fields.assert_called_once_with(mock_decode.return_value)

    def test_rsa_parser_initialization(self):
        """Test proper initialization of RSAParser."""
        parser = rsa_parser.RSAParser()
        
        self.assertEqual('', parser.algorithm)
        self.assertEqual('', parser.modulus)
        self.assertEqual('', parser.exponent)
        self.assertTrue(parser._key_length_big_endian)

    def test_get_struct_format_big_endian(self):
        """Test struct format for big endian."""
        parser = rsa_parser.RSAParser()
        parser._key_length_big_endian = True
        
        format_str = parser._get_struct_format()
        
        self.assertEqual(">L", format_str)

    def test_get_struct_format_little_endian(self):
        """Test struct format for little endian."""
        parser = rsa_parser.RSAParser()
        parser._key_length_big_endian = False
        
        format_str = parser._get_struct_format()
        
        self.assertEqual("<L", format_str)

    @mock.patch('struct.unpack')
    def test_get_fields_parsing(self, mock_unpack):
        """Test field parsing from key bytes."""
        parser = rsa_parser.RSAParser()
        key_bytes = b'\x00\x00\x00\x04test\x00\x00\x00\x04data'
        
        mock_unpack.side_effect = [
            (4,),  # First field length
            (4,),  # Second field length
        ]
        
        fields = list(parser._get_fields(key_bytes))
        
        self.assertEqual(2, len(fields))
        self.assertEqual(b'test', fields[0])
        self.assertEqual(b'data', fields[1])

    def test_get_fields_empty_bytes(self):
        """Test field parsing with empty bytes."""
        parser = rsa_parser.RSAParser()
        key_bytes = b''
        
        fields = list(parser._get_fields(key_bytes))
        
        self.assertEqual(0, len(fields))

    def test_rsa_algorithm_constant(self):
        """Test the RSA algorithm constant."""
        self.assertEqual('ssh-rsa', rsa_parser.RSAParser.RSAAlgorithm)

    def _get_good_key(self):
        """Get a valid RSA public key string for testing."""
        return (
            "AAAAB3NzaC1yc2EAAAADAQABAAABAQChdsBRgNFUAmv4UEYFVSVP2xf0z3rPiS"
            "ewgrV16p3Qu7VdxBokCAwvV6KGOGjAU/DKopmKaXcSTDg0mADdgtjJHfZi38Pg"
            "55UbFnz/G5RteiUt/IVcz6XdR1ejkxmzFkkAP1LqGSsZWOT+0mJIDuydGleS4h"
            "Y5KLle/elhlL8DBbmGFiQwxkAV+ujHCAVs8XDPJPkdiP3F5NGOFIHW09KnuRvE"
            "TGgBEJmwCtqr7dWm5rGIU3CTcQHNP+LiYUFTbQKLmwKO6YN7tFGp+DrQNjVTtO"
            "01WNK+pzLPEynJr2tJ5g3VgJKJ8QwaDBuK+OASyeTS3ejmvn+b0FDzAHASHn+H"
        )

    def _get_good_modulus(self):
        """Get the expected modulus for the good key."""
        return (
            "AKF2wFGA0VQCa_hQRgVVJU_bF_TPes-JJ7CCtXXqndC7tV3EGiQIDC9XooY4aM"
            "BT8MqimYppdxJMODSYAN2C2Mkd9mLfw-DnlRsWfP8blG16JS38hVzPpd1HV6OT"
            "GbMWSQA_UuoZKxlY5P7SYkgO7J0aV5LiFjkouV796WGUvwMFuYYWJDDGQBX66M"
            "cIBWzxcM8k-R2I_cXk0Y4UgdbT0qe5G8RMaAEQmbAK2qvt1abmsYhTcJNxAc0_"
            "4uJhQVNtAoubAo7pg3u0Uan4OtA2NVO07TVY0r6nMs8TKcmva0nmDdWAkonxDB"
            "oMG4r44BLJ5NLd6Oa-f5vQUPMAcBIef4c="
        )

    def _get_good_exponent(self):
        """Get the expected exponent for the good key."""
        return "AQAB"


if __name__ == '__main__':
    unittest.main()
