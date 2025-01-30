# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azext_connectedk8s._utils import *
import sys
import os
import unittest
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


class TestUtils(unittest.TestCase):

    def test_remove_rsa_private_key(self):
        input_text = "Error: -----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA7\n-----END RSA PRIVATE KEY-----"
        expected_output = "Error: [RSA PRIVATE KEY REMOVED]"
        self.assertEqual(remove_rsa_private_key(input_text), expected_output)

        input_text_no_key = "Error: No RSA key here"
        self.assertEqual(remove_rsa_private_key(input_text_no_key), input_text_no_key)

    def test_scrub_proxy_url_with_url(self):
        input_text = "text with proxy URL http://proxy:pass@example.com:8080 in it"
        expected_output = "text with proxy URL http://[REDACTED]:[REDACTED]@example.com:8080 in it"
        self.assertEqual(scrub_proxy_url(input_text), expected_output)

    def test_scrub_proxy_url_without_url(self):
        input_text = "text without proxy URL"
        self.assertEqual(scrub_proxy_url(input_text), input_text)

    def test_process_helm_error_detail(self):
        input_text = "Some text\n-----BEGIN RSA PRIVATE KEY-----\nkey\n-----END RSA PRIVATE KEY-----\nwith proxy URL http://proxy:pass@example.com:8080 in it"
        expected_output = "Some text\n[RSA PRIVATE KEY REMOVED]\nwith proxy URL http://[REDACTED]:[REDACTED]@example.com:8080 in it"
        self.assertEqual(process_helm_error_detail(input_text), expected_output)

    def test_process_helm_error_detail_no_changes(self):
        input_text = "Some text without RSA key or proxy URL"
        self.assertEqual(process_helm_error_detail(input_text), input_text)


if __name__ == '__main__':
    unittest.main()
