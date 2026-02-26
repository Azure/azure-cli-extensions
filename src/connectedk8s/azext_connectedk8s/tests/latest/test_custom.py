# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import MagicMock, patch

from azext_connectedk8s.custom import install_kubectl_client


class TestInstallKubectlClient(unittest.TestCase):
    @patch("azext_connectedk8s.custom.platform.system", return_value="linux")
    @patch("azext_connectedk8s.custom.os.path.isfile", return_value=False)
    @patch("azext_connectedk8s.custom.os.makedirs")
    @patch("azext_connectedk8s.custom.os.path.expanduser", return_value="/tmp/home")
    @patch("azext_connectedk8s.custom.get_default_cli")
    def test_install_kubectl_invokes_install_cli(
        self,
        mock_get_default_cli,
        _mock_expanduser,
        _mock_makedirs,
        _mock_isfile,
        _mock_system,
    ):
        mock_cli = MagicMock()
        mock_cli.invoke.return_value = 0
        mock_get_default_cli.return_value = mock_cli

        result = install_kubectl_client()

        expected_kubectl_path = "/tmp/home/.azure/kubectl-client/kubectl"
        self.assertEqual(result, expected_kubectl_path)
        mock_cli.invoke.assert_called_once_with(
            [
                "aks",
                "install-cli",
                "--install-location",
                expected_kubectl_path,
            ]
        )
