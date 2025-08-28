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

from azext_aks_preview.agent.binary_manager import AksMcpBinaryManager


# Use IsolatedAsyncioTestCase for proper async test method support
class TestAksMcpBinaryManager(IsolatedAsyncioTestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_install_dir = tempfile.mkdtemp()
        self.binary_manager = AksMcpBinaryManager(self.test_install_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary directory
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
            f.write('#!/bin/bash\\necho "aks-mcp version 0.1.0"')
        os.chmod(self.binary_manager.binary_path, 0o755)
        
        # Mock subprocess.run
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "aks-mcp version 0.1.0\\n"
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
        
        # Mock subprocess.run with just version number
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "0.2.5\\n"
        mock_run.return_value = mock_result
        
        version = self.binary_manager.get_binary_version()
        self.assertEqual(version, "0.2.5")

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
                mock_result.stdout = output + "\\n"
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

    # New tests for GitHub Release API Integration (Task 2.1)
    
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
    
    def test_verify_binary_integrity_valid_file(self):
        """Test binary integrity verification with valid file (basic mode)."""
        # Create any size file - size doesn't matter anymore
        test_file = os.path.join(self.test_install_dir, 'test-binary')
        with open(test_file, 'wb') as f:
            f.write(b'any content')  # Size doesn't matter
        
        # Test basic verification without release info (now synchronous)
        result = self.binary_manager._verify_binary_integrity(test_file)
        self.assertTrue(result)
    
    def test_verify_binary_integrity_small_file(self):
        """Test binary integrity verification with small file (should still pass)."""
        test_file = os.path.join(self.test_install_dir, 'test-binary')
        with open(test_file, 'wb') as f:
            f.write(b'small')  # Small file should be fine now
        
        result = self.binary_manager._verify_binary_integrity(test_file)
        self.assertTrue(result)  # Should pass - size doesn't matter anymore
    
    def test_verify_binary_integrity_missing_file(self):
        """Test binary integrity verification with missing file."""
        non_existent = os.path.join(self.test_install_dir, 'non-existent')
        result = self.binary_manager._verify_binary_integrity(non_existent)
        self.assertFalse(result)
    
    def test_verify_binary_integrity_os_error(self):
        """Test binary integrity verification with OS error."""
        with patch('os.path.exists', return_value=False):
            result = self.binary_manager._verify_binary_integrity('/some/path')
            self.assertFalse(result)

    
    @patch('urllib.request.urlopen')
    def test_verify_binary_integrity_with_intoto_success(self, mock_urlopen):
        """Test binary integrity verification with successful in-toto attestation."""
        import hashlib
        
        # Create a test binary file (any size is fine)
        test_file = os.path.join(self.test_install_dir, 'aks-mcp-linux-amd64')
        test_content = b'test binary content'
        with open(test_file, 'wb') as f:
            f.write(test_content)
        
        # Calculate actual SHA256
        actual_hash = hashlib.sha256(test_content).hexdigest()
        
        # Mock release info with attestation file
        release_info = {
            "assets": [
                {"name": "aks-mcp-linux-amd64.intoto.jsonl", "browser_download_url": "https://example.com/attestation"}
            ]
        }
        
        # Mock attestation content with correct hash
        attestation_content = f'''{{
            "predicate": {{
                "materials": {{
                    "aks-mcp-linux-amd64": {{
                        "digest": {{
                            "sha256": "{actual_hash}"
                        }}
                    }}
                }}
            }}
        }}'''
        
        # Mock HTTP response for attestation download
        mock_response = Mock()
        mock_response.status = 200
        mock_response.read.return_value = attestation_content.encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = self.binary_manager._verify_binary_integrity(test_file, release_info)
        self.assertTrue(result)
    
    def test_verify_binary_integrity_with_intoto_hash_mismatch(self):
        """Test binary integrity verification with hash mismatch in attestation."""
        import hashlib
        import json
        from unittest.mock import patch
        
        # Create a test binary file
        test_file = os.path.join(self.test_install_dir, 'aks-mcp-linux-amd64')
        test_content = b'test content for hash verification'
        with open(test_file, 'wb') as f:
            f.write(test_content)
        
        # Calculate the actual hash of our test content
        actual_hash = hashlib.sha256(test_content).hexdigest()
        # Use a definitely different hash
        wrong_hash = hashlib.sha256(b'completely different content that will not match').hexdigest()
        
        # Mock release info with attestation file
        release_info = {
            "assets": [
                {"name": "aks-mcp-linux-amd64.intoto.jsonl", "browser_download_url": "https://example.com/attestation"}
            ]
        }
        
        # Create a simple, valid JSON attestation with wrong hash
        attestation_dict = {
            "predicate": {
                "materials": {
                    "aks-mcp-linux-amd64": {
                        "digest": {
                            "sha256": wrong_hash
                        }
                    }
                }
            }
        }
        attestation_content = json.dumps(attestation_dict)
        
        # Test that our JSON is valid
        parsed_test = json.loads(attestation_content)
        self.assertEqual(parsed_test["predicate"]["materials"]["aks-mcp-linux-amd64"]["digest"]["sha256"], wrong_hash)
        
        # Test by bypassing the network call and directly testing the verification logic
        # We'll temporarily create a mock attestation file locally
        temp_attestation_file = os.path.join(self.test_install_dir, 'temp_attestation.jsonl')
        with open(temp_attestation_file, 'w') as f:
            f.write(attestation_content)
        
        # Mock urllib.request.urlopen to read from our local file
        def mock_urlopen(url, timeout=None):
            class MockResponse:
                def __init__(self, filepath):
                    self.filepath = filepath
                    self.status = 200
                    
                def read(self):
                    with open(self.filepath, 'rb') as f:
                        return f.read()
                        
                def __enter__(self):
                    return self
                    
                def __exit__(self, *args):
                    pass
            
            return MockResponse(temp_attestation_file)
        
        with patch('urllib.request.urlopen', side_effect=mock_urlopen):
            # This should return False due to hash mismatch
            result = self.binary_manager._verify_binary_integrity(test_file, release_info)
            
            # The result should be False because hashes don't match
            self.assertFalse(result, 
                f"Expected False due to hash mismatch.\n"
                f"File content hash: {actual_hash}\n"
                f"Attestation hash: {wrong_hash}\n" 
                f"They should be different: {actual_hash != wrong_hash}")
        
        # Clean up temp file
        os.remove(temp_attestation_file)


    def test_verify_binary_integrity_with_intoto_hash_match(self):
        """Test binary integrity verification with successful hash match."""
        import hashlib
        import json
        from unittest.mock import patch
        
        # Create a test binary file
        test_file = os.path.join(self.test_install_dir, 'aks-mcp-darwin-arm64')
        test_content = b'test content for successful hash verification'
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
        
        # Create a valid JSON attestation with correct hash
        attestation_dict = {
            "predicate": {
                "materials": {
                    "aks-mcp-darwin-arm64": {
                        "digest": {
                            "sha256": actual_hash  # Use the correct hash
                        }
                    }
                }
            }
        }
        attestation_content = json.dumps(attestation_dict)
        
        # Create temporary attestation file
        temp_attestation_file = os.path.join(self.test_install_dir, 'temp_attestation_success.jsonl')
        with open(temp_attestation_file, 'w') as f:
            f.write(attestation_content)
        
        # Mock urllib.request.urlopen
        def mock_urlopen(url, timeout=None):
            class MockResponse:
                def __init__(self, filepath):
                    self.filepath = filepath
                    self.status = 200
                    
                def read(self):
                    with open(self.filepath, 'rb') as f:
                        return f.read()
                        
                def __enter__(self):
                    return self
                    
                def __exit__(self, *args):
                    pass
            
            return MockResponse(temp_attestation_file)
        
        with patch('urllib.request.urlopen', side_effect=mock_urlopen):
            # This should return True due to hash match
            result = self.binary_manager._verify_binary_integrity(test_file, release_info)
            
            # The result should be True because hashes match
            self.assertTrue(result, f"Expected True due to hash match. Hash: {actual_hash}")
        
        # Clean up temp file
        os.remove(temp_attestation_file)
    
    @patch('urllib.request.urlopen')
    def test_verify_binary_integrity_with_intoto_subject_format(self, mock_urlopen):
        """Test binary integrity verification with SLSA subject format."""
        import hashlib
        
        # Create a test binary file (any size)
        test_file = os.path.join(self.test_install_dir, 'aks-mcp-darwin-arm64')
        test_content = b'test binary content'
        with open(test_file, 'wb') as f:
            f.write(test_content)
        
        # Calculate actual SHA256
        actual_hash = hashlib.sha256(test_content).hexdigest()
        
        # Mock release info with attestation file
        release_info = {
            "assets": [
                {"name": "aks-mcp-darwin-arm64.intoto.jsonl", "browser_download_url": "https://example.com/attestation"}
            ]
        }
        
        # Mock attestation content with SLSA subject format
        attestation_content = f'''{{
            "subject": [
                {{
                    "name": "aks-mcp-darwin-arm64",
                    "digest": {{
                        "sha256": "{actual_hash}"
                    }}
                }}
            ]
        }}'''
        
        # Mock HTTP response for attestation download
        mock_response = Mock()
        mock_response.status = 200
        mock_response.read.return_value = attestation_content.encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = self.binary_manager._verify_binary_integrity(test_file, release_info)
        self.assertTrue(result)
    
    def test_verify_binary_integrity_no_attestation_file(self):
        """Test binary integrity verification when no attestation file is available."""
        # Create a test binary file (any size)
        test_file = os.path.join(self.test_install_dir, 'aks-mcp-linux-amd64')
        with open(test_file, 'wb') as f:
            f.write(b'test content')
        
        # Mock release info without matching attestation file
        release_info = {
            "assets": [
                {"name": "other-file.txt", "browser_download_url": "https://example.com/other"}
            ]
        }
        
        # Should fall back to basic verification (return True for existing file)
        result = self.binary_manager._verify_binary_integrity(test_file, release_info)
        self.assertTrue(result)
    
    @patch('urllib.request.urlopen')
    def test_verify_binary_integrity_attestation_download_fails(self, mock_urlopen):
        """Test binary integrity verification when attestation download fails."""
        # Create a test binary file (any size)
        test_file = os.path.join(self.test_install_dir, 'aks-mcp-linux-amd64')
        with open(test_file, 'wb') as f:
            f.write(b'test content')
        
        # Mock release info with attestation file
        release_info = {
            "assets": [
                {"name": "aks-mcp-linux-amd64.intoto.jsonl", "browser_download_url": "https://example.com/attestation"}
            ]
        }
        
        # Mock HTTP error for attestation download
        mock_response = Mock()
        mock_response.status = 404
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        # Should fall back to basic verification (return True for existing file)
        result = self.binary_manager._verify_binary_integrity(test_file, release_info)
        self.assertTrue(result)
    
    def test_get_platform_binary_name_corrected_format(self):
        """Test the corrected platform binary name format (with dashes not underscores)."""
        with patch.object(self.binary_manager, '_get_platform_info', return_value=('linux', 'amd64')):
            binary_name = self.binary_manager._get_platform_binary_name()
            self.assertEqual(binary_name, 'aks-mcp-linux-amd64')  # Note: dash, not underscore
        
        with patch.object(self.binary_manager, '_get_platform_info', return_value=('windows', 'amd64')), \
             patch('platform.system', return_value='Windows'):
            binary_name = self.binary_manager._get_platform_binary_name()
            self.assertEqual(binary_name, 'aks-mcp-windows-amd64.exe')  # Note: dash, not underscore
    
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
        # Mock response with invalid JSON - use json.JSONDecodeError instead of ValueError
        import json
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(side_effect=json.JSONDecodeError("Invalid JSON", "doc", 0))
        
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
        
        self.assertIn("Failed to parse GitHub API response", str(context.exception))
    
    @patch('aiohttp.ClientSession')
    @patch.object(AksMcpBinaryManager, '_get_platform_binary_name')
    @patch.object(AksMcpBinaryManager, 'get_latest_release_info')
    @patch('os.makedirs')
    async def test_download_binary_success(self, mock_makedirs, mock_release_info, 
                                         mock_binary_name, mock_session):
        """Test successful binary download."""
        mock_binary_name.return_value = 'aks-mcp_linux_amd64'
        mock_release_info.return_value = {
            "assets": [
                {"name": "aks-mcp_linux_amd64", "browser_download_url": "https://example.com/binary"}
            ]
        }
        
        # Create mock response for successful download
        mock_response = Mock()
        mock_response.status = 200
        mock_response.headers = {'content-length': '1024'}
        
        # Create async generator for chunked content
        async def mock_iter_chunked(size):
            yield b'binary data chunk'
        
        mock_response.content.iter_chunked = mock_iter_chunked
        
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
        
        # Create a proper context manager mock for the file
        mock_file = Mock()
        mock_file.write = Mock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=None)
        
        with patch('builtins.open', return_value=mock_file), \
             patch.object(self.binary_manager, '_verify_binary_integrity', return_value=True), \
             patch.object(self.binary_manager, '_make_binary_executable', return_value=True):
            result = await self.binary_manager.download_binary()
        
        self.assertTrue(result)
        # Verify that directory creation was attempted
        mock_makedirs.assert_called_once_with(self.test_install_dir, exist_ok=True)
    
    @patch('aiohttp.ClientSession')
    @patch.object(AksMcpBinaryManager, '_get_platform_binary_name')
    @patch.object(AksMcpBinaryManager, 'get_latest_release_info')
    async def test_download_binary_no_asset_found(self, mock_release_info, mock_binary_name, mock_session):
        """Test binary download when no matching asset found."""
        mock_binary_name.return_value = 'aks-mcp_unsupported_platform'
        mock_release_info.return_value = {
            "assets": [
                {"name": "aks-mcp_linux_amd64", "browser_download_url": "https://example.com/binary"}
            ]
        }
        
        with self.assertRaises(Exception) as context:
            await self.binary_manager.download_binary()
        
        self.assertIn("No binary found for platform aks-mcp_unsupported_platform", str(context.exception))
    
    @patch('aiohttp.ClientSession')
    @patch.object(AksMcpBinaryManager, '_get_platform_binary_name')
    @patch.object(AksMcpBinaryManager, 'get_latest_release_info')
    @patch('os.makedirs')
    async def test_download_binary_download_http_error(self, mock_makedirs, mock_release_info, 
                                                     mock_binary_name, mock_session):
        """Test binary download with HTTP error."""
        mock_binary_name.return_value = 'aks-mcp_linux_amd64'
        mock_release_info.return_value = {
            "assets": [
                {"name": "aks-mcp_linux_amd64", "browser_download_url": "https://example.com/binary"}
            ]
        }
        
        # Create mock response with 404 status
        mock_response = Mock()
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
            await self.binary_manager.download_binary()
        
        self.assertIn("Download failed with status 404", str(context.exception))
        # Verify that directory creation was attempted before the HTTP error
        mock_makedirs.assert_called_once_with(self.test_install_dir, exist_ok=True)
    
    @patch('aiohttp.ClientSession')
    @patch.object(AksMcpBinaryManager, '_get_platform_binary_name')
    @patch.object(AksMcpBinaryManager, 'get_latest_release_info')
    @patch.object(AksMcpBinaryManager, '_verify_binary_integrity')
    @patch('os.makedirs')
    @patch('os.remove')
    async def test_download_binary_integrity_failure(self, mock_remove, mock_makedirs, 
                                                   mock_integrity, mock_release_info, 
                                                   mock_binary_name, mock_session):
        """Test binary download with integrity check failure."""
        mock_binary_name.return_value = 'aks-mcp_linux_amd64'
        mock_release_info.return_value = {
            "assets": [
                {"name": "aks-mcp_linux_amd64", "browser_download_url": "https://example.com/binary"}
            ]
        }
        mock_integrity.return_value = False  # Integrity check fails
        
        # Create mock response for successful download
        mock_response = Mock()
        mock_response.status = 200
        mock_response.headers = {'content-length': '1024'}
        
        # Create simple async generator for chunked content - no hanging
        async def mock_iter_chunked(size):
            yield b'corrupted data'
        
        mock_response.content.iter_chunked = mock_iter_chunked
        
        # Use the same working pattern as the successful test
        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session_ctx)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=None)
        
        mock_get_ctx = AsyncMock()
        mock_get_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get_ctx.__aexit__ = AsyncMock(return_value=None)
        
        mock_session.return_value = mock_session_ctx
        mock_session_ctx.get = Mock(return_value=mock_get_ctx)
        
        # Create a proper context manager mock for the file
        mock_file = Mock()
        mock_file.write = Mock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=None)
        
        with patch('builtins.open', return_value=mock_file):
            with self.assertRaises(Exception) as context:
                await self.binary_manager.download_binary()
        
        self.assertIn("Downloaded binary failed integrity check", str(context.exception))
        mock_remove.assert_called_once_with(self.binary_manager.binary_path)
        # Verify that directory creation was attempted before the integrity check
        mock_makedirs.assert_called_once_with(self.test_install_dir, exist_ok=True)
    
    @patch('aiohttp.ClientSession')
    @patch.object(AksMcpBinaryManager, '_get_platform_binary_name')
    @patch.object(AksMcpBinaryManager, 'get_latest_release_info')
    @patch.object(AksMcpBinaryManager, '_verify_binary_integrity')
    @patch.object(AksMcpBinaryManager, '_make_binary_executable')
    @patch('os.makedirs')
    async def test_download_binary_executable_failure(self, mock_makedirs, mock_executable, 
                                                    mock_integrity, mock_release_info, 
                                                    mock_binary_name, mock_session):
        """Test binary download with executable permission failure."""
        mock_binary_name.return_value = 'aks-mcp_linux_amd64'
        mock_release_info.return_value = {
            "assets": [
                {"name": "aks-mcp_linux_amd64", "browser_download_url": "https://example.com/binary"}
            ]
        }
        mock_integrity.return_value = True
        mock_executable.return_value = False  # Executable permission fails
        
        # Create mock response for successful download
        mock_response = Mock()
        mock_response.status = 200
        mock_response.headers = {'content-length': '1024'}
        
        # Create async generator for chunked content
        async def mock_iter_chunked(size):
            yield b'valid binary data'
        
        mock_response.content.iter_chunked = mock_iter_chunked
        
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
        
        # Create a proper context manager mock for the file
        mock_file = Mock()
        mock_file.write = Mock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=None)
        
        with patch('builtins.open', return_value=mock_file):
            with self.assertRaises(Exception) as context:
                await self.binary_manager.download_binary()
        
        self.assertIn("Failed to make binary executable", str(context.exception))
        # Verify that directory creation was attempted before the executable failure
        mock_makedirs.assert_called_once_with(self.test_install_dir, exist_ok=True)
    
    @patch('aiohttp.ClientSession')
    @patch.object(AksMcpBinaryManager, '_get_platform_binary_name')
    @patch.object(AksMcpBinaryManager, 'get_latest_release_info')
    @patch('os.makedirs')
    async def test_download_binary_with_progress_callback(self, mock_makedirs, mock_release_info, 
                                                        mock_binary_name, mock_session):
        """Test binary download with progress callback."""
        mock_binary_name.return_value = 'aks-mcp_linux_amd64'
        mock_release_info.return_value = {
            "assets": [
                {"name": "aks-mcp_linux_amd64", "browser_download_url": "https://example.com/binary"}
            ]
        }
        
        # Create mock response for successful download
        mock_response = Mock()
        mock_response.status = 200
        mock_response.headers = {'content-length': '1024'}
        
        # Create async generator for chunked content
        async def mock_iter_chunked(size):
            yield b'chunk1'  # 6 bytes
            yield b'chunk2'  # 6 bytes
        
        mock_response.content.iter_chunked = mock_iter_chunked
        
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
        
        # Mock progress callback
        progress_calls = []
        def mock_progress_callback(downloaded, total, filename):
            progress_calls.append((downloaded, total, filename))
        
        # Create a proper context manager mock for the file
        mock_file = Mock()
        mock_file.write = Mock()
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=None)
        
        with patch('builtins.open', return_value=mock_file), \
             patch.object(self.binary_manager, '_verify_binary_integrity', return_value=True), \
             patch.object(self.binary_manager, '_make_binary_executable', return_value=True):
            result = await self.binary_manager.download_binary(progress_callback=mock_progress_callback)
        
        self.assertTrue(result)
        # Should have been called twice (once per chunk)
        self.assertEqual(len(progress_calls), 2)
        self.assertEqual(progress_calls[0], (6, 1024, 'aks-mcp_linux_amd64'))
        self.assertEqual(progress_calls[1], (12, 1024, 'aks-mcp_linux_amd64'))
        # Verify that directory creation was attempted
        mock_makedirs.assert_called_once_with(self.test_install_dir, exist_ok=True)

    def test_create_installation_directory_success(self):
        """Test successful directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = os.path.join(temp_dir, "new_install_dir")
            binary_manager = AksMcpBinaryManager(new_dir)
            
            result = binary_manager._create_installation_directory()
            
            self.assertTrue(result)
            self.assertTrue(os.path.exists(new_dir))
            self.assertTrue(os.path.isdir(new_dir))

    def test_create_installation_directory_already_exists(self):
        """Test directory creation when directory already exists."""
        result = self.binary_manager._create_installation_directory()
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.test_install_dir))

    @patch('os.makedirs')
    def test_create_installation_directory_permission_error(self, mock_makedirs):
        """Test directory creation with permission error."""
        mock_makedirs.side_effect = PermissionError("Permission denied")
        
        result = self.binary_manager._create_installation_directory()
        
        self.assertFalse(result)
        mock_makedirs.assert_called_once_with(self.test_install_dir, exist_ok=True)

    @patch('os.makedirs')
    def test_create_installation_directory_os_error(self, mock_makedirs):
        """Test directory creation with OS error."""
        mock_makedirs.side_effect = OSError("Disk full")
        
        result = self.binary_manager._create_installation_directory()
        
        self.assertFalse(result)

    def test_binary_status_dataclass(self):
        """Test BinaryStatus dataclass functionality."""
        from azext_aks_preview.agent.binary_manager import BinaryStatus
        
        # Test default values
        status = BinaryStatus()
        self.assertFalse(status.available)
        self.assertIsNone(status.path)
        self.assertIsNone(status.version)
        self.assertFalse(status.version_valid)
        self.assertIsNone(status.error_message)
        self.assertFalse(status.ready)

        # Test ready property when available and valid
        status = BinaryStatus(available=True, version_valid=True)
        self.assertTrue(status.ready)

        # Test ready property when available but not valid
        status = BinaryStatus(available=True, version_valid=False)
        self.assertFalse(status.ready)

        # Test with all fields populated
        status = BinaryStatus(
            available=True,
            path="/path/to/binary",
            version="1.0.0",
            version_valid=True,
            error_message=None
        )
        self.assertTrue(status.ready)
        self.assertEqual(status.path, "/path/to/binary")
        self.assertEqual(status.version, "1.0.0")

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
