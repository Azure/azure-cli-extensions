# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest

from knack.util import CLIError
from azext_aimanager._helpers import parse_key_value_list, get_aks_custom_headers


class TestAIManagerHelpers(unittest.TestCase):
    """Test cases for AI Manager helper functions."""

    def test_parse_key_value_list_none(self):
        self.assertEqual(parse_key_value_list(None), {})

    def test_parse_key_value_list_pairs(self):
        self.assertEqual(
            parse_key_value_list(["team=alpha", "env=prod"]),
            {"team": "alpha", "env": "prod"})

    def test_parse_key_value_list_invalid(self):
        with self.assertRaises(CLIError):
            parse_key_value_list(["invalid"])

    def test_get_aks_custom_headers_empty(self):
        self.assertEqual(get_aks_custom_headers(None), {})
        self.assertEqual(get_aks_custom_headers(""), {})

    def test_get_aks_custom_headers_pairs(self):
        self.assertEqual(
            get_aks_custom_headers("a=1,b=2"),
            {"a": "1", "b": "2"})

    def test_get_aks_custom_headers_invalid(self):
        with self.assertRaises(CLIError):
            get_aks_custom_headers("badheader")


if __name__ == '__main__':
    unittest.main()
