# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from azext_aks_agent.agent.aks import get_aks_credentials


class TestGetAksCredentials(unittest.TestCase):

    @patch("azext_aks_agent.agent.aks.subprocess.run")
    @patch("azext_aks_agent.agent.aks.shutil.which")
    def test_uses_resolved_kubelogin_path(self, mock_which, mock_run):
        kubelogin_path = r"C:\Program Files\Azure\kubelogin.exe"
        mock_which.return_value = kubelogin_path

        kubeconfig = b"""
users:
- user:
    exec:
      command: kubelogin
      args:
      - --login
      - devicecode
"""
        client = MagicMock()
        client.list_cluster_user_credentials.return_value.kubeconfigs = [
            MagicMock(value=kubeconfig)
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            kubeconfig_path = os.path.join(temp_dir, "config")
            with patch(
                "azext_aks_agent.agent.aks._get_kubeconfig_file_path",
                return_value=kubeconfig_path,
            ):
                result = get_aks_credentials(client, "resource-group", "cluster")

        self.assertEqual(result, kubeconfig_path)
        mock_run.assert_called_once_with(
            [
                kubelogin_path,
                "convert-kubeconfig",
                "-l",
                "azurecli",
                "--kubeconfig",
                kubeconfig_path,
            ],
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
