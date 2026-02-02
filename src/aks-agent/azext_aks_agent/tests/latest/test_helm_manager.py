# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Unit tests for HelmManager.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

from azext_aks_agent._consts import HELM_VERSION
from azext_aks_agent.agent.k8s.helm_manager import HelmManager


class TestHelmManager(unittest.TestCase):
    """Test cases for HelmManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_helm_version = HELM_VERSION
        self.test_kubeconfig = "/mock/kubeconfig"
        self.test_bin_dir = "/mock/bin"

    @patch('azext_aks_agent.agent.k8s.helm_manager.Path.mkdir')
    @patch('azext_aks_agent.agent.k8s.helm_manager.HelmManager._ensure_helm_binary')
    def test_init_default_values(self, mock_ensure_helm, mock_mkdir):
        """Test HelmManager initialization with default values."""
        mock_ensure_helm.return_value = "/mock/helm"

        manager = HelmManager()

        self.assertEqual(manager.helm_version, "3.16.0")
        self.assertIsNone(manager.kubeconfig_path)
        self.assertIsNotNone(manager.local_bin_dir)
        mock_mkdir.assert_called_once()
        mock_ensure_helm.assert_called_once()

    @patch('azext_aks_agent.agent.k8s.helm_manager.Path.mkdir')
    @patch('azext_aks_agent.agent.k8s.helm_manager.HelmManager._ensure_helm_binary')
    def test_init_custom_values(self, mock_ensure_helm, mock_mkdir):
        """Test HelmManager initialization with custom values."""
        mock_ensure_helm.return_value = "/mock/helm"

        manager = HelmManager(
            helm_version=self.test_helm_version,
            local_bin_dir=self.test_bin_dir,
            kubeconfig_path=self.test_kubeconfig
        )

        self.assertEqual(manager.helm_version, self.test_helm_version)
        self.assertEqual(manager.kubeconfig_path, self.test_kubeconfig)
        self.assertEqual(str(manager.local_bin_dir), self.test_bin_dir)

    @patch('azext_aks_agent.agent.k8s.helm_manager.platform.system')
    @patch('azext_aks_agent.agent.k8s.helm_manager.platform.machine')
    @patch('azext_aks_agent.agent.k8s.helm_manager.Path.mkdir')
    @patch('azext_aks_agent.agent.k8s.helm_manager.HelmManager._ensure_helm_binary')
    def test_get_platform_info_linux_amd64(self, mock_ensure_helm, mock_mkdir, mock_machine, mock_system):
        """Test platform detection for Linux AMD64."""
        mock_ensure_helm.return_value = "/mock/helm"
        mock_system.return_value = "Linux"
        mock_machine.return_value = "x86_64"

        manager = HelmManager()
        os_name, arch = manager._get_platform_info()

        self.assertEqual(os_name, "linux")
        self.assertEqual(arch, "amd64")

    @patch('azext_aks_agent.agent.k8s.helm_manager.platform.system')
    @patch('azext_aks_agent.agent.k8s.helm_manager.platform.machine')
    @patch('azext_aks_agent.agent.k8s.helm_manager.Path.mkdir')
    @patch('azext_aks_agent.agent.k8s.helm_manager.HelmManager._ensure_helm_binary')
    def test_get_platform_info_darwin_arm64(self, mock_ensure_helm, mock_mkdir, mock_machine, mock_system):
        """Test platform detection for macOS ARM64."""
        mock_ensure_helm.return_value = "/mock/helm"
        mock_system.return_value = "Darwin"
        mock_machine.return_value = "arm64"

        manager = HelmManager()
        os_name, arch = manager._get_platform_info()

        self.assertEqual(os_name, "darwin")
        self.assertEqual(arch, "arm64")

    @patch('azext_aks_agent.agent.k8s.helm_manager.platform.system')
    @patch('azext_aks_agent.agent.k8s.helm_manager.platform.machine')
    @patch('azext_aks_agent.agent.k8s.helm_manager.Path.mkdir')
    @patch('azext_aks_agent.agent.k8s.helm_manager.HelmManager._ensure_helm_binary')
    def test_get_platform_info_windows_amd64(self, mock_ensure_helm, mock_mkdir, mock_machine, mock_system):
        """Test platform detection for Windows AMD64."""
        mock_ensure_helm.return_value = "/mock/helm"
        mock_system.return_value = "Windows"
        mock_machine.return_value = "AMD64"

        manager = HelmManager()
        os_name, arch = manager._get_platform_info()

        self.assertEqual(os_name, "windows")
        self.assertEqual(arch, "amd64")

    @patch('azext_aks_agent.agent.k8s.helm_manager.subprocess.run')
    @patch('azext_aks_agent.agent.k8s.helm_manager.Path.mkdir')
    @patch('azext_aks_agent.agent.k8s.helm_manager.HelmManager._ensure_helm_binary')
    def test_run_command_success(self, mock_ensure_helm, mock_mkdir, mock_run):
        """Test successful helm command execution."""
        mock_ensure_helm.return_value = "/mock/helm"
        mock_run.return_value = Mock(
            returncode=0,
            stdout="success output",
            stderr=""
        )

        manager = HelmManager()
        success, output = manager.run_command(["version"])

        self.assertTrue(success)
        self.assertEqual(output, "success output")
        mock_run.assert_called_once()

    @patch('azext_aks_agent.agent.k8s.helm_manager.subprocess.run')
    @patch('azext_aks_agent.agent.k8s.helm_manager.Path.mkdir')
    @patch('azext_aks_agent.agent.k8s.helm_manager.HelmManager._ensure_helm_binary')
    def test_run_command_with_kubeconfig(self, mock_ensure_helm, mock_mkdir, mock_run):
        """Test helm command execution with kubeconfig."""
        mock_ensure_helm.return_value = "/mock/helm"
        mock_run.return_value = Mock(
            returncode=0,
            stdout="success",
            stderr=""
        )

        manager = HelmManager(kubeconfig_path=self.test_kubeconfig)
        success, output = manager.run_command(["list"])

        self.assertTrue(success)
        # Verify --kubeconfig flag was added
        call_args = mock_run.call_args[0][0]
        self.assertIn("--kubeconfig", call_args)
        self.assertIn(self.test_kubeconfig, call_args)

    @patch('azext_aks_agent.agent.k8s.helm_manager.subprocess.run')
    @patch('azext_aks_agent.agent.k8s.helm_manager.Path.mkdir')
    @patch('azext_aks_agent.agent.k8s.helm_manager.HelmManager._ensure_helm_binary')
    def test_run_command_failure(self, mock_ensure_helm, mock_mkdir, mock_run):
        """Test helm command execution failure."""
        mock_ensure_helm.return_value = "/mock/helm"
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="error output"
        )

        manager = HelmManager()
        success, output = manager.run_command(["invalid"], check=False)

        self.assertFalse(success)
        self.assertIn("error output", output)

    @patch('azext_aks_agent.agent.k8s.helm_manager.subprocess.run')
    @patch('azext_aks_agent.agent.k8s.helm_manager.Path.mkdir')
    @patch('azext_aks_agent.agent.k8s.helm_manager.HelmManager._ensure_helm_binary')
    def test_get_version(self, mock_ensure_helm, mock_mkdir, mock_run):
        """Test getting helm version."""
        mock_ensure_helm.return_value = "/mock/helm"
        mock_run.return_value = Mock(
            returncode=0,
            stdout="version.BuildInfo{Version:\"v3.16.0\"}",
            stderr=""
        )

        manager = HelmManager()
        version = manager.get_version()

        self.assertIsNotNone(version)
        self.assertIn("3.16.0", version)

    @patch('azext_aks_agent.agent.k8s.helm_manager.subprocess.run')
    @patch('azext_aks_agent.agent.k8s.helm_manager.Path.mkdir')
    @patch('azext_aks_agent.agent.k8s.helm_manager.HelmManager._ensure_helm_binary')
    def test_repo_add_success(self, mock_ensure_helm, mock_mkdir, mock_run):
        """Test adding helm repository."""
        mock_ensure_helm.return_value = "/mock/helm"
        mock_run.return_value = Mock(
            returncode=0,
            stdout="repo added",
            stderr=""
        )

        manager = HelmManager()
        result = manager.repo_add("test-repo", "https://test.repo")

        self.assertTrue(result)
        call_args = mock_run.call_args[0][0]
        self.assertIn("repo", call_args)
        self.assertIn("add", call_args)

    @patch('azext_aks_agent.agent.k8s.helm_manager.subprocess.run')
    @patch('azext_aks_agent.agent.k8s.helm_manager.Path.mkdir')
    @patch('azext_aks_agent.agent.k8s.helm_manager.HelmManager._ensure_helm_binary')
    def test_repo_update_success(self, mock_ensure_helm, mock_mkdir, mock_run):
        """Test updating helm repositories."""
        mock_ensure_helm.return_value = "/mock/helm"
        mock_run.return_value = Mock(
            returncode=0,
            stdout="repos updated",
            stderr=""
        )

        manager = HelmManager()
        result = manager.repo_update()

        self.assertTrue(result)
        call_args = mock_run.call_args[0][0]
        self.assertIn("repo", call_args)
        self.assertIn("update", call_args)


class TestHelmManagerRealDownload(unittest.TestCase):
    """Integration tests for HelmManager that perform real downloads."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_helm_version = HELM_VERSION
        self.temp_dir = None

    def tearDown(self):
        """Clean up test fixtures."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    @unittest.skipIf(os.environ.get('SKIP_INTEGRATION_TESTS'), "Skipping integration test")
    def test_real_download_all_platforms(self):
        """Test real helm binary download for all supported OS and architecture combinations."""
        import shutil

        platforms = [
            ("linux", "amd64"),
            ("linux", "arm64"),
            ("linux", "arm"),
            ("linux", "386"),
            ("darwin", "amd64"),
            ("darwin", "arm64"),
            ("windows", "amd64"),
            ("windows", "arm64"),
        ]

        for os_name, arch in platforms:
            with self.subTest(os=os_name, arch=arch):
                # Create fresh temp directory for each platform
                if self.temp_dir and os.path.exists(self.temp_dir):
                    shutil.rmtree(self.temp_dir, ignore_errors=True)

                self.temp_dir = tempfile.mkdtemp()

                try:
                    with patch('azext_aks_agent.agent.k8s.helm_manager.HelmManager._get_platform_info') as mock_platform:
                        mock_platform.return_value = (os_name, arch)

                        manager = HelmManager.__new__(HelmManager)
                        manager.local_bin_dir = Path(self.temp_dir)
                        manager.helm_version = self.test_helm_version

                        # Perform actual download
                        result = manager._download_helm_binary()

                        # Verify no exception was raised and binary exists
                        self.assertIsNotNone(result, f"Download failed for {os_name}-{arch}")
                        self.assertTrue(os.path.exists(result), f"Binary not found for {os_name}-{arch}")
                        self.assertIn("helm", result)

                        # Verify binary is executable on Unix systems
                        if os_name != "windows":
                            self.assertTrue(os.access(result, os.X_OK), f"Binary not executable for {os_name}-{arch}")
                finally:
                    # Clean up temp directory after each platform test
                    if self.temp_dir and os.path.exists(self.temp_dir):
                        shutil.rmtree(self.temp_dir, ignore_errors=True)
                    self.temp_dir = None


if __name__ == '__main__':
    unittest.main()
