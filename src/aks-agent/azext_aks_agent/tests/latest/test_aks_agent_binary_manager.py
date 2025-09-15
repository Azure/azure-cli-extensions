# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest import IsolatedAsyncioTestCase
import os
import tempfile
import platform
import stat
import subprocess
from unittest.mock import Mock, patch, AsyncMock

from azext_aks_agent.agent.binary_manager import AksMcpBinaryManager


# Use IsolatedAsyncioTestCase for proper async test method support
class TestAksMcpBinaryManager(IsolatedAsyncioTestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_install_dir = tempfile.mkdtemp()
        self.binary_manager = AksMcpBinaryManager(self.test_install_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_install_dir, ignore_errors=True)
    
    def test_get_binary_path_linux(self):
        """Test binary path resolution on Linux."""
        with patch('platform.system', return_value='Linux'):
            manager = AksMcpBinaryManager('/test/dir')
            expected_path = os.path.join('/test/dir', 'aks-mcp')
            self.assertEqual(manager.get_binary_path(), expected_path)
    
    def test_get_binary_path_windows(self):
        """Test binary path resolution on Windows."""
        with patch('platform.system', return_value='Windows'):
            manager = AksMcpBinaryManager('/test/dir')
            expected_path = os.path.join('/test/dir', 'aks-mcp.exe')
            self.assertEqual(manager.get_binary_path(), expected_path)
    
    def test_get_binary_path_darwin(self):
        """Test binary path resolution on macOS."""
        with patch('platform.system', return_value='Darwin'):
            manager = AksMcpBinaryManager('/test/dir')
            expected_path = os.path.join('/test/dir', 'aks-mcp')
            self.assertEqual(manager.get_binary_path(), expected_path)
    
    def test_is_binary_available_not_exists(self):
        """Test binary availability when file doesn't exist."""
        self.assertFalse(self.binary_manager.is_binary_available())
    
    def test_is_binary_available_exists_but_not_executable(self):
        """Test binary availability when file exists but is not executable."""
        # Create a non-executable file
        with open(self.binary_manager.binary_path, 'w') as f:
            f.write('dummy content')
        os.chmod(self.binary_manager.binary_path, 0o644)  # Read/write but not execute
        
        self.assertFalse(self.binary_manager.is_binary_available())
    
    def test_is_binary_available_exists_and_executable(self):
        """Test binary availability when file exists and is executable."""
        # Create an executable file
        with open(self.binary_manager.binary_path, 'w') as f:
            f.write('dummy content')
        os.chmod(self.binary_manager.binary_path, 0o755)  # Read/write/execute
        
        self.assertTrue(self.binary_manager.is_binary_available())
    
    @patch('os.access')
    def test_is_binary_available_os_error(self, mock_access):
        """Test binary availability when os.access raises OSError."""
        # Create file first
        with open(self.binary_manager.binary_path, 'w') as f:
            f.write('dummy content')
        
        mock_access.side_effect = OSError("Permission denied")
        self.assertFalse(self.binary_manager.is_binary_available())
    
    def test_get_binary_version_not_available(self):
        """Test version retrieval when binary is not available."""
        self.assertIsNone(self.binary_manager.get_binary_version())
    
    @patch('subprocess.run')
    def test_get_binary_version_success(self, mock_run):
        """Test successful version retrieval."""
        # Create an executable file
        with open(self.binary_manager.binary_path, 'w') as f:
            f.write('#!/bin/bash\necho "aks-mcp version 0.1.0"')
        os.chmod(self.binary_manager.binary_path, 0o755)
        
        # Mock subprocess.run
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "aks-mcp version 0.1.0\n"
        mock_run.return_value = mock_result
        
        version = self.binary_manager.get_binary_version()
        self.assertEqual(version, "0.1.0")
        mock_run.assert_called_once_with(
            [self.binary_manager.binary_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )
    
    @patch('subprocess.run')
    def test_get_binary_version_different_format(self, mock_run):
        """Test version retrieval with different output format."""
        # Create an executable file
        with open(self.binary_manager.binary_path, 'w') as f:
            f.write('dummy content')
        os.chmod(self.binary_manager.binary_path, 0o755)
        
        # Different format
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "version: 1.2.3\n"
        mock_run.return_value = mock_result
        
        version = self.binary_manager.get_binary_version()
        self.assertEqual(version, "1.2.3")
    
    @patch('subprocess.run')
    def test_get_binary_version_actual_format(self, mock_run):
        """Test version retrieval with actual aks-mcp version format."""
        # Create an executable file
        with open(self.binary_manager.binary_path, 'w') as f:
            f.write('dummy content')
        os.chmod(self.binary_manager.binary_path, 0o755)
        
        # Mock subprocess.run with actual aks-mcp output format
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = """aks-mcp version v0.0.6-16-ga7464eb+2025-08-18T13:33:38Z
Git commit: a7464eb458bcb138599519a0281b1047cc63b749
Git tree state: clean
Go version: go1.24.5
Platform: darwin/arm64
"""
        mock_run.return_value = mock_result
        
        version = self.binary_manager.get_binary_version()
        self.assertEqual(version, "0.0.6")
    
    @patch('subprocess.run')
    def test_get_binary_version_git_format_variations(self, mock_run):
        """Test version retrieval with different git-style version formats."""
        # Create an executable file
        with open(self.binary_manager.binary_path, 'w') as f:
            f.write('dummy content')
        os.chmod(self.binary_manager.binary_path, 0o755)
        
        test_cases = [
            ("aks-mcp version v0.1.0", "0.1.0"),
            ("aks-mcp version v0.1.0-5-g123abc", "0.1.0"),
            ("aks-mcp version v1.2.3-10-gabc123+2025-01-01T12:00:00Z", "1.2.3"),
            ("version v0.0.7-dirty", "0.0.7"),
        ]
        
        for output, expected_version in test_cases:
            with self.subTest(output=output):
                mock_result = Mock()
                mock_result.returncode = 0
                mock_result.stdout = output + "\n"
                mock_run.return_value = mock_result
                
                version = self.binary_manager.get_binary_version()
                self.assertEqual(version, expected_version)
    
    @patch('subprocess.run')
    def test_get_binary_version_subprocess_error(self, mock_run):
        """Test version retrieval when subprocess fails."""
        # Create an executable file
        with open(self.binary_manager.binary_path, 'w') as f:
            f.write('dummy content')
        os.chmod(self.binary_manager.binary_path, 0o755)
        
        mock_run.side_effect = subprocess.SubprocessError("Command failed")
        version = self.binary_manager.get_binary_version()
        self.assertIsNone(version)
    
    @patch('subprocess.run')
    def test_get_binary_version_timeout(self, mock_run):
        """Test version retrieval when subprocess times out."""
        # Create an executable file
        with open(self.binary_manager.binary_path, 'w') as f:
            f.write('dummy content')
        os.chmod(self.binary_manager.binary_path, 0o755)
        
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 10)
        version = self.binary_manager.get_binary_version()
        self.assertIsNone(version)
    
    @patch('subprocess.run')
    def test_get_binary_version_non_zero_exit(self, mock_run):
        """Test version retrieval when command returns non-zero exit code."""
        # Create an executable file
        with open(self.binary_manager.binary_path, 'w') as f:
            f.write('dummy content')
        os.chmod(self.binary_manager.binary_path, 0o755)
        
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = "error"
        mock_run.return_value = mock_result
        
        version = self.binary_manager.get_binary_version()
        self.assertIsNone(version)
    
    @patch.object(AksMcpBinaryManager, 'get_binary_version')
    def test_validate_version_success(self, mock_get_version):
        """Test successful version validation."""
        mock_get_version.return_value = "0.1.0"
        self.assertTrue(self.binary_manager.validate_version("0.0.6"))
        self.assertTrue(self.binary_manager.validate_version("0.1.0"))
        self.assertFalse(self.binary_manager.validate_version("0.2.0"))
    
    @patch.object(AksMcpBinaryManager, 'get_binary_version')
    def test_validate_version_no_version(self, mock_get_version):
        """Test version validation when no version available."""
        mock_get_version.return_value = None
        self.assertFalse(self.binary_manager.validate_version("0.0.6"))
    
    @patch.object(AksMcpBinaryManager, 'get_binary_version')
    def test_validate_version_invalid_format(self, mock_get_version):
        """Test version validation with invalid version format."""
        mock_get_version.return_value = "invalid-version"
        self.assertFalse(self.binary_manager.validate_version("0.0.6"))
    
    def test_validate_version_complex_versions(self):
        """Test version validation with complex version numbers."""
        with patch.object(self.binary_manager, 'get_binary_version') as mock_get_version:
            # Test 4-part version
            mock_get_version.return_value = "0.1.0.1"
            self.assertTrue(self.binary_manager.validate_version("0.1.0.0"))
            self.assertFalse(self.binary_manager.validate_version("0.2.0.0"))
            
            # Test equal versions
            mock_get_version.return_value = "1.2.3"
            self.assertTrue(self.binary_manager.validate_version("1.2.3"))
    
    def test_get_platform_info_linux_amd64(self):
        """Test platform info detection for Linux amd64."""
        with patch('platform.system', return_value='Linux'), \
             patch('platform.machine', return_value='x86_64'):
            platform_name, arch_name = self.binary_manager._get_platform_info()
            self.assertEqual(platform_name, 'linux')
            self.assertEqual(arch_name, 'amd64')
    
    def test_get_platform_info_darwin_arm64(self):
        """Test platform info detection for macOS ARM64."""
        with patch('platform.system', return_value='Darwin'), \
             patch('platform.machine', return_value='arm64'):
            platform_name, arch_name = self.binary_manager._get_platform_info()
            self.assertEqual(platform_name, 'darwin')
            self.assertEqual(arch_name, 'arm64')
    
    def test_get_platform_info_windows_amd64(self):
        """Test platform info detection for Windows amd64."""
        with patch('platform.system', return_value='Windows'), \
             patch('platform.machine', return_value='AMD64'):
            platform_name, arch_name = self.binary_manager._get_platform_info()
            self.assertEqual(platform_name, 'windows')
            self.assertEqual(arch_name, 'amd64')
    
    def test_get_platform_info_linux_aarch64(self):
        """Test platform info detection for Linux aarch64."""
        with patch('platform.system', return_value='Linux'), \
             patch('platform.machine', return_value='aarch64'):
            platform_name, arch_name = self.binary_manager._get_platform_info()
            self.assertEqual(platform_name, 'linux')
            self.assertEqual(arch_name, 'arm64')
    
    def test_make_binary_executable_unix(self):
        """Test making binary executable on Unix-like systems."""
        if platform.system() == 'Windows':
            self.skipTest("Skipping Unix test on Windows")
        
        # Create a test file
        test_file = os.path.join(self.test_install_dir, 'test-binary')
        with open(test_file, 'w') as f:
            f.write('dummy content')
        os.chmod(test_file, 0o644)  # Read/write only
        
        # Make it executable
        success = self.binary_manager._make_binary_executable(test_file)
        self.assertTrue(success)
        
        # Check that it's now executable
        file_mode = os.stat(test_file).st_mode
        self.assertTrue(file_mode & stat.S_IEXEC)  # Owner executable
        self.assertTrue(file_mode & stat.S_IXGRP)  # Group executable
        self.assertTrue(file_mode & stat.S_IXOTH)  # Others executable
    
    @patch('platform.system', return_value='Windows')
    def test_make_binary_executable_windows(self, mock_system):
        """Test making binary executable on Windows (should always succeed)."""
        test_file = os.path.join(self.test_install_dir, 'test-binary.exe')
        with open(test_file, 'w') as f:
            f.write('dummy content')
        
        success = self.binary_manager._make_binary_executable(test_file)
        self.assertTrue(success)
    
    def test_make_binary_executable_os_error(self):
        """Test making binary executable when OS operations fail."""
        if platform.system() == 'Windows':
            self.skipTest("Skipping Unix test on Windows")
        
        # Try to make a non-existent file executable
        non_existent_file = os.path.join(self.test_install_dir, 'non-existent')
        success = self.binary_manager._make_binary_executable(non_existent_file)
        self.assertFalse(success)

    # New tests for GitHub Release API Integration
    
    def test_get_platform_binary_name_linux_amd64(self):
        """Test platform binary name generation for Linux AMD64."""
        with patch.object(self.binary_manager, '_get_platform_info', return_value=('linux', 'amd64')):
            binary_name = self.binary_manager._get_platform_binary_name()
            self.assertEqual(binary_name, 'aks-mcp-linux-amd64')
    
    def test_get_platform_binary_name_windows_amd64(self):
        """Test platform binary name generation for Windows AMD64."""
        with patch.object(self.binary_manager, '_get_platform_info', return_value=('windows', 'amd64')), \
             patch('platform.system', return_value='Windows'):
            binary_name = self.binary_manager._get_platform_binary_name()
            self.assertEqual(binary_name, 'aks-mcp-windows-amd64.exe')
    
    def test_get_platform_binary_name_darwin_arm64(self):
        """Test platform binary name generation for macOS ARM64."""
        with patch.object(self.binary_manager, '_get_platform_info', return_value=('darwin', 'arm64')):
            binary_name = self.binary_manager._get_platform_binary_name()
            self.assertEqual(binary_name, 'aks-mcp-darwin-arm64')

    @patch('aiohttp.ClientSession')
    async def test_get_latest_release_info_success(self, mock_session):
        """Test successful GitHub API release info retrieval."""
        # Mock successful API response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "tag_name": "v0.1.0",
            "assets": [
                {"name": "aks-mcp-linux-amd64", "browser_download_url": "https://example.com/binary"}
            ]
        })
        
        # Create mock session with proper async context manager support
        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session_ctx)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=None)
        
        # Create mock get response with proper async context manager support  
        mock_get_ctx = AsyncMock()
        mock_get_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get_ctx.__aexit__ = AsyncMock(return_value=None)
        
        # Wire up the mocks
        mock_session.return_value = mock_session_ctx
        mock_session_ctx.get = Mock(return_value=mock_get_ctx)
        
        result = await self.binary_manager.get_latest_release_info()
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["tag_name"], "v0.1.0")
        self.assertIn("assets", result)
    
    @patch('aiohttp.ClientSession')
    async def test_get_latest_release_info_http_error(self, mock_session):
        """Test GitHub API release info with HTTP error."""
        # Mock HTTP error response
        mock_response = AsyncMock()
        mock_response.status = 404
        
        # Create mock session with proper async context manager support
        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session_ctx)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=None)
        
        # Create mock get response with proper async context manager support  
        mock_get_ctx = AsyncMock()
        mock_get_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get_ctx.__aexit__ = AsyncMock(return_value=None)
        
        # Wire up the mocks
        mock_session.return_value = mock_session_ctx
        mock_session_ctx.get = Mock(return_value=mock_get_ctx)
        
        with self.assertRaises(Exception) as context:
            await self.binary_manager.get_latest_release_info()
        
        self.assertIn("GitHub API request failed with status 404", str(context.exception))
    
    @patch('aiohttp.ClientSession')
    async def test_get_latest_release_info_network_error(self, mock_session):
        """Test GitHub API release info with network error."""
        # Create mock session that raises ClientError
        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session_ctx)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=None)
        
        # Mock get to raise aiohttp.ClientError
        import aiohttp
        mock_session_ctx.get = Mock(side_effect=aiohttp.ClientError("Network unreachable"))
        
        # Wire up the mocks
        mock_session.return_value = mock_session_ctx
        
        with self.assertRaises(Exception) as context:
            await self.binary_manager.get_latest_release_info()
        
        self.assertIn("Network error accessing GitHub API", str(context.exception))
    
    @patch('aiohttp.ClientSession')
    async def test_get_latest_release_info_json_error(self, mock_session):
        """Test GitHub API release info with JSON decode error."""
        # Mock response with invalid JSON
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(side_effect=ValueError("Invalid JSON"))
        
        # Create mock session with proper async context manager support
        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session_ctx)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=None)
        
        # Create mock get response with proper async context manager support  
        mock_get_ctx = AsyncMock()
        mock_get_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get_ctx.__aexit__ = AsyncMock(return_value=None)
        
        # Wire up the mocks
        mock_session.return_value = mock_session_ctx
        mock_session_ctx.get = Mock(return_value=mock_get_ctx)
        
        with self.assertRaises(Exception):
            await self.binary_manager.get_latest_release_info()
    
    @patch('urllib.request.urlopen')
    def test_verify_binary_integrity_subject_hash(self, mock_urlopen):
        """Test binary integrity verification with subject hash in attestation."""
        import json
        import hashlib
        
        # Create a test binary file (any size)
        test_file = os.path.join(self.test_install_dir, 'aks-mcp-darwin-arm64')
        test_content = b'test content'
        with open(test_file, 'wb') as f:
            f.write(test_content)
        
        # Calculate the actual hash of our test content
        actual_hash = hashlib.sha256(test_content).hexdigest()
        
        # Mock release info with attestation file
        release_info = {
            "assets": [
                {"name": "aks-mcp-darwin-arm64.intoto.jsonl", "browser_download_url": "https://example.com/attestation"}
            ]
        }
        
        # Mock attestation content with subject hash
        attestation_dict = {
            "subject": [
                {
                    "name": "aks-mcp-darwin-arm64",
                    "digest": {
                        "sha256": actual_hash
                    }
                }
            ]
        }
        attestation_content = json.dumps(attestation_dict)
        
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.read.return_value = attestation_content.encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = self.binary_manager._verify_binary_integrity(test_file, release_info)
        self.assertTrue(result)
    
    def test_verify_binary_integrity_fallback_to_basic(self):
        """Test binary integrity verification fallback when no attestation found."""
        # Create a test binary file (any size)
        test_file = os.path.join(self.test_install_dir, 'aks-mcp-linux-amd64')
        with open(test_file, 'wb') as f:
            f.write(b'test content')
        
        release_info = {"assets": []}
        result = self.binary_manager._verify_binary_integrity(test_file, release_info)
        self.assertTrue(result)

    async def test_ensure_binary_already_available_and_valid(self):
        """Test ensure_binary when binary is already available and valid."""
        with patch.object(self.binary_manager, 'is_binary_available', return_value=True), \
             patch.object(self.binary_manager, 'get_binary_version', return_value="1.0.0"), \
             patch.object(self.binary_manager, 'validate_version', return_value=True):
            
            status = await self.binary_manager.ensure_binary()
            
            self.assertTrue(status.available)
            self.assertEqual(status.version, "1.0.0")
            self.assertTrue(status.version_valid)
            self.assertTrue(status.ready)
            self.assertIsNone(status.error_message)

    async def test_ensure_binary_available_but_invalid_version(self):
        """Test ensure_binary when binary is available but has invalid version."""
        mock_progress = Mock()
        
        with patch.object(self.binary_manager, 'is_binary_available', side_effect=[True, True]), \
             patch.object(self.binary_manager, 'get_binary_version', side_effect=["0.0.1", "1.0.0"]), \
             patch.object(self.binary_manager, 'validate_version', side_effect=[False, True]), \
             patch.object(self.binary_manager, '_create_installation_directory', return_value=True), \
             patch.object(self.binary_manager, 'download_binary', return_value=True):
            
            status = await self.binary_manager.ensure_binary(progress_callback=mock_progress)
            
            self.assertTrue(status.available)
            self.assertEqual(status.version, "1.0.0")
            self.assertTrue(status.version_valid)
            self.assertTrue(status.ready)
            self.assertIsNone(status.error_message)

    async def test_ensure_binary_not_available_download_success(self):
        """Test ensure_binary when binary is not available but download succeeds."""
        mock_progress = Mock()
        
        with patch.object(self.binary_manager, 'is_binary_available', side_effect=[False, True]), \
             patch.object(self.binary_manager, 'get_binary_version', return_value="1.0.0"), \
             patch.object(self.binary_manager, 'validate_version', return_value=True), \
             patch.object(self.binary_manager, '_create_installation_directory', return_value=True), \
             patch.object(self.binary_manager, 'download_binary', return_value=True) as mock_download:
            
            status = await self.binary_manager.ensure_binary(progress_callback=mock_progress)
            
            self.assertTrue(status.available)
            self.assertEqual(status.version, "1.0.0")
            self.assertTrue(status.version_valid)
            self.assertTrue(status.ready)
            self.assertIsNone(status.error_message)
            mock_download.assert_called_once_with(progress_callback=mock_progress)

    async def test_ensure_binary_directory_creation_fails(self):
        """Test ensure_binary when directory creation fails."""
        with patch.object(self.binary_manager, 'is_binary_available', return_value=False), \
             patch.object(self.binary_manager, '_create_installation_directory', return_value=False):
            
            status = await self.binary_manager.ensure_binary()
            
            self.assertFalse(status.ready)
            self.assertIn("Failed to create installation directory", status.error_message)

    async def test_ensure_binary_download_fails(self):
        """Test ensure_binary when download fails."""
        with patch.object(self.binary_manager, 'is_binary_available', return_value=False), \
             patch.object(self.binary_manager, '_create_installation_directory', return_value=True), \
             patch.object(self.binary_manager, 'download_binary', return_value=False):
            
            status = await self.binary_manager.ensure_binary()
            
            self.assertFalse(status.ready)
            self.assertEqual(status.error_message, "Binary download failed")

    async def test_ensure_binary_download_success_but_validation_fails(self):
        """Test ensure_binary when download succeeds but validation fails."""
        with patch.object(self.binary_manager, 'is_binary_available', side_effect=[False, True]), \
             patch.object(self.binary_manager, 'get_binary_version', return_value="0.0.1"), \
             patch.object(self.binary_manager, 'validate_version', return_value=False), \
             patch.object(self.binary_manager, '_create_installation_directory', return_value=True), \
             patch.object(self.binary_manager, 'download_binary', return_value=True):
            
            status = await self.binary_manager.ensure_binary()
            
            self.assertTrue(status.available)
            self.assertEqual(status.version, "0.0.1")
            self.assertFalse(status.version_valid)
            self.assertFalse(status.ready)
            self.assertEqual(status.error_message, "Downloaded binary failed validation")

    async def test_ensure_binary_unexpected_exception(self):
        """Test ensure_binary handles unexpected exceptions gracefully."""
        with patch.object(self.binary_manager, 'is_binary_available', side_effect=Exception("Unexpected error")):
            
            status = await self.binary_manager.ensure_binary()
            
            self.assertFalse(status.ready)
            self.assertIn("Unexpected error during binary management", status.error_message)
            self.assertIn("Unexpected error", status.error_message)


if __name__ == '__main__':
    unittest.main()

