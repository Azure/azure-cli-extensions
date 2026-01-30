# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import os

from azext_managedcleanroom.aaz.latest.managedcleanroom.private_endpoint_util import PrivateEndpointUtil


class TestPrivateEndpointUtil(unittest.TestCase):
    """Unit tests for the PrivateEndpointUtil class."""

    def tearDown(self):
        """Clean up environment variable after each test."""
        env_var = PrivateEndpointUtil.PRIVATE_NAMESPACE_ENVIRONMENT_VARIABLE
        if env_var in os.environ:
            del os.environ[env_var]

    def test_get_configured_namespace_returns_private_when_env_is_true(self):
        """Test that get_configured_namespace returns PRIVATE_NAMESPACE when env var is 'true'."""
        os.environ[PrivateEndpointUtil.PRIVATE_NAMESPACE_ENVIRONMENT_VARIABLE] = "true"
        result = PrivateEndpointUtil.get_configured_namespace()
        self.assertEqual(result, PrivateEndpointUtil.PRIVATE_NAMESPACE)

    def test_get_configured_namespace_returns_public_when_env_is_false(self):
        """Test that get_configured_namespace returns PUBLIC_NAMESPACE when env var is 'false'."""
        os.environ[PrivateEndpointUtil.PRIVATE_NAMESPACE_ENVIRONMENT_VARIABLE] = "false"
        result = PrivateEndpointUtil.get_configured_namespace()
        self.assertEqual(result, PrivateEndpointUtil.PUBLIC_NAMESPACE)


if __name__ == '__main__':
    unittest.main()
