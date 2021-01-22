# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import mock

from azext_ssh import rsa_parser


class RSAParserTest(unittest.TestCase):
    def test_rsa_parser_success(self):
        public_key_text = 'ssh-rsa ' + self._get_good_key()
        parser = rsa_parser.RSAParser()

        parser.parse(public_key_text)

        print(parser.modulus)
        self.assertEqual('ssh-rsa', parser.algorithm)
        self.assertEqual(self._get_good_modulus(), parser.modulus)
        self.assertEqual(self._get_good_exponent(), parser.exponent)

    def test_rsa_parser_too_few_public_key_text_fields(self):
        public_key_text = 'algo'
        parser = rsa_parser.RSAParser()

        self.assertRaises(ValueError, parser.parse, public_key_text)

    def test_rsa_parser_wrong_algorithm(self):
        public_key_text = 'wrongalgo key'
        parser = rsa_parser.RSAParser()

        self.assertRaises(ValueError, parser.parse, public_key_text)

    @mock.patch('base64.b64decode')
    def test_rsa_parser_algorithm_mismatch(self, mock_decode):
        public_key_text = 'ssh-rsa key'
        parser = rsa_parser.RSAParser()

        with mock.patch.object(parser, '_get_fields') as mock_get_fields:
            mock_get_fields.return_value = [b'otheralgo', b'exp', b'mod']
            self.assertRaises(ValueError, parser.parse, public_key_text)

        mock_decode.assert_called_once_with('key')
        mock_get_fields.assert_called_once_with(mock_decode.return_value)

    @mock.patch('base64.b64decode')
    def test_rsa_parser_too_few_encoded_fields(self, mock_decode):
        public_key_text = 'ssh-rsa key'
        mock_decode.return_value = b'decodedkey'
        parser = rsa_parser.RSAParser()

        with mock.patch.object(parser, '_get_fields') as mock_get_fields:
            mock_get_fields.return_value = [b'ssh-rsa', b'exp']
            self.assertRaises(ValueError, parser.parse, public_key_text)

        mock_decode.assert_called_once_with('key')
        mock_get_fields.assert_called_once_with(mock_decode.return_value)

    def _get_good_key(self):
        return (
            "AAAAB3NzaC1yc2EAAAADAQABAAABAQChdsBRgNFUAmv4UEYFVSVP2xf0z3rPiS"
            "ewgrV16p3Qu7VdxBokCAwvV6KGOGjAU/DKopmKaXcSTDg0mADdgtjJHfZi38Pg"
            "55UbFnz/G5RteiUt/IVcz6XdR1ejkxmzFkkAP1LqGSsZWOT+0mJIDuydGleS4h"
            "Y5KLle/elhlL8DBbmGFiQwxkAV+ujHCAVs8XDPJPkdiP3F5NGOFIHW09KnuRvE"
            "TGgBEJmwCtqr7dWm5rGIU3CTcQHNP+LiYUFTbQKLmwKO6YN7tFGp+DrQNjVTtO"
            "01WNK+pzLPEynJr2tJ5g3VgJKJ8QwaDBuK+OASyeTS3ejmvn+b0FDzAHASHn+H"
        )

    def _get_good_modulus(self):
        return (
            "AKF2wFGA0VQCa_hQRgVVJU_bF_TPes-JJ7CCtXXqndC7tV3EGiQIDC9XooY4aM"
            "BT8MqimYppdxJMODSYAN2C2Mkd9mLfw-DnlRsWfP8blG16JS38hVzPpd1HV6OT"
            "GbMWSQA_UuoZKxlY5P7SYkgO7J0aV5LiFjkouV796WGUvwMFuYYWJDDGQBX66M"
            "cIBWzxcM8k-R2I_cXk0Y4UgdbT0qe5G8RMaAEQmbAK2qvt1abmsYhTcJNxAc0_"
            "4uJhQVNtAoubAo7pg3u0Uan4OtA2NVO07TVY0r6nMs8TKcmva0nmDdWAkonxDB"
            "oMG4r44BLJ5NLd6Oa-f5vQUPMAcBIef4c="
        )

    def _get_good_exponent(self):
        return "AQAB"


if __name__ == '__main__':
    unittest.main()
