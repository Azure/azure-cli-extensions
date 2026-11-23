# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from azext_aks_agent.agent.aks import get_aks_credentials
from azure.cli.core.azclierror import AzCLIError


class TestGetAksCredentials(unittest.TestCase):

    def setUp(self):
        self.kubeconfig = b"""
users:
- user:
    exec:
      command: kubelogin
      args:
      - --login
      - devicecode
"""
        self.client = MagicMock()
        self.client.list_cluster_user_credentials.return_value.kubeconfigs = [
            MagicMock(value=self.kubeconfig)
        ]

    def test_ignores_working_directory_executable(self):
        with tempfile.TemporaryDirectory() as directory:
            working = os.path.join(directory, "working")
            tools = os.path.join(directory, "installed tools")
            binary = "kubelogin.exe" if os.name == "nt" else "kubelogin"
            for folder in (working, tools):
                os.mkdir(folder)
                executable = os.path.join(folder, binary)
                with open(executable, "w"):
                    pass
                os.chmod(executable, 0o700)

            old_cwd = os.getcwd()
            try:
                os.chdir(working)
                for prefix in (None, "", ".", working):
                    for installed in (True, False):
                        search_path = [] if prefix is None else [prefix]
                        search_path.append(tools if installed else os.path.join(directory, "missing"))
                        config_path = os.path.join(directory, "selected config")
                        with (
                            self.subTest(prefix=prefix, installed=installed),
                            patch.dict(os.environ, {
                                "PATH": os.pathsep.join(search_path),
                                "PATHEXT": ".exe",
                                "SystemRoot": os.path.join(directory, "system"),
                            }),
                            patch("azext_aks_agent.agent.aks._get_kubeconfig_file_path",
                                  return_value=config_path),
                            patch("azext_aks_agent.agent.aks.subprocess.run") as run,
                        ):
                            os.environ.pop("NoDefaultCurrentDirectoryInExePath", None)
                            if installed:
                                result = get_aks_credentials(self.client, "resource-group", "cluster")
                                self.assertEqual(result, config_path)
                                run.assert_called_once_with(
                                    [os.path.join(tools, binary), "convert-kubeconfig", "-l", "azurecli",
                                     "--kubeconfig", config_path],
                                    check=True,
                                )
                            else:
                                with self.assertRaisesRegex(AzCLIError, "Please install kubelogin"):
                                    get_aks_credentials(self.client, "resource-group", "cluster")
                                run.assert_not_called()
            finally:
                os.chdir(old_cwd)

    @patch("azext_aks_agent.agent.aks.subprocess.run")
    @patch("azext_aks_agent.agent.aks.get_safe_executable_path")
    def test_uses_resolved_kubelogin_path(self, mock_which, mock_run):
        kubelogin_path = r"C:\Program Files\Azure\kubelogin.exe"
        mock_which.return_value = kubelogin_path

        with tempfile.TemporaryDirectory() as temp_dir:
            kubeconfig_path = os.path.join(temp_dir, "config")
            with patch(
                "azext_aks_agent.agent.aks._get_kubeconfig_file_path",
                return_value=kubeconfig_path,
            ):
                result = get_aks_credentials(self.client, "resource-group", "cluster")

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
