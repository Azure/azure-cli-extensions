# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from azext_fleet._helpers import is_stdout_path


# Test constants
STDOUT_PATH = '-'
SAMPLE_KUBECONFIG_PATH = "/home/user/.kube/config"
SAMPLE_CONFIG_FILENAME = "config.yaml"


class TestHelpers(unittest.TestCase):
    """Test cases for helper functions."""

    def test_is_stdout_path_with_dash(self):
        """Test that '-' is recognized as stdout path."""
        self.assertTrue(is_stdout_path(STDOUT_PATH))

    def test_is_stdout_path_with_regular_path(self):
        """Test that regular paths are not recognized as stdout."""
        self.assertFalse(is_stdout_path(SAMPLE_KUBECONFIG_PATH))
        self.assertFalse(is_stdout_path(SAMPLE_CONFIG_FILENAME))


if __name__ == '__main__':
    unittest.main()
