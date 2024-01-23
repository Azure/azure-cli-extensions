# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest import mock

from azext_ssh import connectivity_utils

class ConnectivityUtilsTest(unittest.TestCase):
    
    @mock.patch('azext_ssh.aaz.latest.hybrid_connectivity.endpoint.ListCredential')
    def test_list_credentials_with_float_validity(self, mock_list_credential):
        cmd = mock.Mock()
        cmd.cli_ctx = mock.Mock()

        mock_list_credential_instance = mock.Mock()
        mock_list_credential_instance.__call__ = mock.Mock()
        mock_list_credential.return_value = mock_list_credential_instance

        connectivity_utils._list_credentials(cmd, "resource_uri", 100.67)
        mock_list_credential_instance.__call__.assert_called_once_with(command_args={'endpoint_name': 'default', 'resource_uri': 'resource_uri', 'expiresin': 100, 'service_name': 'SSH'})
