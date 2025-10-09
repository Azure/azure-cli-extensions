# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Binary management module for AKS MCP integration.

This module handles the download, validation, and management of the aks-mcp binary
required for Model Context Protocol integration with the AKS agent.
"""

import os
import platform
import subprocess
import stat
from typing import Optional

from .._consts import (
    CONST_MCP_BINARY_NAME,
    CONST_MCP_MIN_VERSION,
    CONST_MCP_GITHUB_REPO,
)
from .error_handler import BinaryError
from .status_models import BinaryStatus


class AksMcpBinaryManager:
    """Manages aks-mcp binary download and validation."""

    GITHUB_RELEASES_URL = f"https://api.github.com/repos/{CONST_MCP_GITHUB_REPO}/releases"

    def __init__(self, install_dir: str):
        """
        Initialize the binary manager.

        :param install_dir: Directory where the binary should be installed
        :type install_dir: str
        """
        self.install_dir = install_dir
        self.binary_path = self._get_binary_path()

    def _get_binary_path(self) -> str:
        """Get the expected path for the binary."""
        binary_name = CONST_MCP_BINARY_NAME
        if platform.system() == "Windows":
            binary_name += ".exe"
        return os.path.join(self.install_dir, binary_name)

    def get_binary_path(self) -> str:
        """Get expected binary path."""
        return self.binary_path

    def is_binary_available(self) -> bool:
        """
        Check if binary exists and is executable.

        :return: True if binary is available and executable, False otherwise
        :rtype: bool
        """
        if not os.path.exists(self.binary_path):
            return False

        # Check if file is executable
        try:
            return os.access(self.binary_path, os.X_OK)
        except OSError:
            return False

    def get_binary_version(self) -> Optional[str]:
        """
        Get binary version if available.

        :return: Version string if available, None otherwise
        :rtype: Optional[str]
        """
        if not self.is_binary_available():
            return None

        try:
            # Run the binary with --version flag
            result = subprocess.run(
                [self.binary_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                # Parse aks-mcp version output format:
                # "aks-mcp version v0.0.6-16-ga7464eb+2025-08-18T13:33:38Z"
                import re

                # First try to match git-style version format: v0.0.6-16-ga7464eb
                git_version_match = re.search(r'v?(\d+\.\d+\.\d+)(?:-\d+-g[a-f0-9]+)?(?:\+[^\s]+)?', output)
                if git_version_match:
                    return git_version_match.group(1)

                # Fallback to simple semantic version pattern
                version_match = re.search(r'(\d+\.\d+\.\d+(?:\.\d+)?)', output)
                if version_match:
                    return version_match.group(1)

            return None

        except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
            return None

    def validate_version(self, required_version: str = CONST_MCP_MIN_VERSION) -> bool:
        """
        Validate binary meets version requirements.

        :param required_version: Minimum required version (default from constants)
        :type required_version: str
        :return: True if version meets requirements, False otherwise
        :rtype: bool
        """
        current_version = self.get_binary_version()
        if not current_version:
            return False

        try:
            # Parse version strings for comparison
            def parse_version(version_str):
                return tuple(map(int, version_str.split('.')))

            current_parsed = parse_version(current_version)
            required_parsed = parse_version(required_version)

            return current_parsed >= required_parsed

        except (ValueError, TypeError):
            # If version parsing fails, assume invalid
            return False

    def _create_installation_directory(self) -> bool:
        """
        Create installation directory if needed.

        :return: True if directory exists or was created successfully, False otherwise
        :rtype: bool
        """
        try:
            os.makedirs(self.install_dir, exist_ok=True)
            return True
        except (OSError, PermissionError):
            return False

    async def ensure_binary(self, progress_callback: callable = None) -> BinaryStatus:
        """
        Complete binary availability check and auto-download.

        This is the main entry point for binary management. It checks if the binary
        is available and valid, and automatically downloads it if needed.

        :param progress_callback: Optional callback for download progress updates
        :type progress_callback: callable
        :return: Binary status information
        :rtype: BinaryStatus
        """
        try:
            # Check if binary already exists and is valid using enhanced status
            if self.is_binary_available():
                version = self.get_binary_version()
                version_valid = self.validate_version()
                status = BinaryStatus.from_file_path(
                    self.binary_path,
                    version=version,
                    version_valid=version_valid
                )

                if status.ready:
                    # Binary is ready to use
                    return status
            else:
                # Binary not available, create basic status
                status = BinaryStatus(path=self.binary_path)

            # Binary is missing or invalid, attempt to download
            if not self._create_installation_directory():
                status.error_message = f"Failed to create installation directory: {self.install_dir}"
                return status

            # Download the binary
            download_success = await self.download_binary(progress_callback=progress_callback)

            if download_success:
                # Verify the downloaded binary using enhanced status
                version = self.get_binary_version()
                version_valid = self.validate_version()

                if os.path.exists(self.binary_path):
                    status = BinaryStatus.from_file_path(
                        self.binary_path,
                        version=version,
                        version_valid=version_valid
                    )
                else:
                    status = BinaryStatus(
                        available=True,
                        version=version,
                        path=self.binary_path,
                        version_valid=version_valid
                    )

                if not status.ready and version is not None:
                    # Binary present but version invalid
                    status.error_message = "Downloaded binary failed validation"
            else:
                status.error_message = "Binary download failed"

        except Exception as e:  # pylint: disable=broad-exception-caught
            status = BinaryStatus(
                path=self.binary_path,
                error_message=f"Unexpected error during binary management: {str(e)}"
            )

        return status

    def _get_platform_info(self) -> tuple[str, str]:
        """
        Get platform and architecture information for binary selection.

        :return: Tuple of (platform, architecture)
        :rtype: tuple[str, str]
        """
        system = platform.system().lower()
        machine = platform.machine().lower()

        # Map platform names
        platform_map = {
            "windows": "windows",
            "darwin": "darwin",
            "linux": "linux"
        }

        # Map architecture names
        arch_map = {
            "x86_64": "amd64",
            "amd64": "amd64",
            "arm64": "arm64",
            "aarch64": "arm64"
        }

        platform_name = platform_map.get(system, system)
        arch_name = arch_map.get(machine, machine)

        return platform_name, arch_name

    def _make_binary_executable(self, binary_path: str) -> bool:
        """
        Set executable permissions on the binary (Unix-like systems).

        :param binary_path: Path to the binary file
        :type binary_path: str
        :return: True if successful, False otherwise
        :rtype: bool
        """
        try:
            if platform.system() != "Windows":
                # Set executable permissions (owner, group, others can execute)
                current_mode = os.stat(binary_path).st_mode
                os.chmod(binary_path, current_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
            return True
        except (OSError, IOError):
            return False

    async def get_latest_release_info(self) -> dict:
        """
        Get latest release information from GitHub API.

        :return: Release information dictionary
        :rtype: dict
        :raises: Exception if API request fails
        """
        import json
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.GITHUB_RELEASES_URL}/latest",
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    raise RuntimeError(f"GitHub API request failed with status {response.status}")

        except aiohttp.ClientError as e:
            raise RuntimeError(f"Network error accessing GitHub API: {e}") from e
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse GitHub API response: {e}") from e

    def _get_platform_binary_name(self) -> str:
        """
        Get platform-specific binary name from GitHub release assets.

        :return: Binary name pattern for the current platform
        :rtype: str
        """
        platform_name, arch_name = self._get_platform_info()

        # GitHub release asset naming convention for aks-mcp (actual format)
        # Examples: aks-mcp-linux-amd64, aks-mcp-windows-amd64.exe, aks-mcp-darwin-arm64
        binary_name = f"aks-mcp-{platform_name}-{arch_name}"

        if platform.system() == "Windows":
            binary_name += ".exe"

        return binary_name

    def _verify_binary_integrity(self, file_path: str, release_info: dict = None) -> bool:  # pylint: disable=too-many-locals,too-many-return-statements,too-many-nested-blocks,too-many-branches
        """
        Verify downloaded binary integrity using in-toto attestation files.

        :param file_path: Path to the downloaded binary
        :type file_path: str
        :param release_info: Release information from GitHub API (optional)
        :type release_info: dict
        :return: True if binary integrity is verified, False otherwise
        :rtype: bool
        """
        try:
            # Basic file existence check
            if not os.path.exists(file_path):
                return False

            # If no release info provided, use basic verification
            if not release_info:
                return True

            # Find the corresponding .intoto.jsonl file
            binary_filename = os.path.basename(file_path)
            intoto_filename = f"{binary_filename}.intoto.jsonl"
            intoto_url = None

            for asset in release_info.get("assets", []):
                if asset["name"] == intoto_filename:
                    intoto_url = asset["browser_download_url"]
                    break

            if not intoto_url:
                # No attestation file found, fall back to basic verification
                return True

            # Try to download and verify attestation synchronously
            # For production, we could enhance this with proper async HTTP client
            # For now, use basic verification as fallback
            try:
                import urllib.request
                import json
                import hashlib

                # Download attestation file
                with urllib.request.urlopen(intoto_url, timeout=30) as response:
                    if response.status != 200:
                        return True  # Fall back to basic verification
                    attestation_content = response.read().decode('utf-8')

                # Parse the in-toto attestation (JSONL format - one JSON object per line)
                for line in attestation_content.strip().split('\n'):  # pylint: disable=too-many-nested-blocks
                    if line.strip():
                        try:
                            attestation = json.loads(line)

                            # Look for the subject information containing the binary hash
                            predicate = attestation.get("predicate", {})
                            materials = predicate.get("materials", {})

                            # Try to find hash in different possible locations in the attestation
                            binary_hash = None

                            # Check for direct subject hash
                            if "subject" in attestation and isinstance(attestation["subject"], list):
                                for subject in attestation["subject"]:
                                    if subject.get("name") == binary_filename:
                                        digest = subject.get("digest", {})
                                        binary_hash = digest.get("sha256")
                                        break

                            # Fallback: Check materials for hash entries
                            if not binary_hash and isinstance(materials, list):
                                for material in materials:
                                    if material.get("uri", "").endswith(binary_filename):
                                        digest = material.get("digest", {})
                                        binary_hash = digest.get("sha256")
                                        break

                            if not binary_hash:
                                continue

                            # Compute SHA-256 of the binary file
                            sha256_hash = hashlib.sha256()
                            with open(file_path, 'rb') as f:
                                while True:
                                    chunk = f.read(8192)
                                    if not chunk:
                                        break
                                    sha256_hash.update(chunk)
                            calculated_hash = sha256_hash.hexdigest()

                            # Verify the hash matches
                            return calculated_hash == binary_hash

                        except (json.JSONDecodeError, KeyError):
                            continue

                # If we couldn't parse the attestation or find hash, fall back to basic verification
                return True

            except Exception:  # pylint: disable=broad-exception-caught
                # If attestation verification fails, fall back to basic verification
                return True

        except Exception:  # pylint: disable=broad-exception-caught
            # If any error occurs, fall back to basic file existence check for reliability
            try:
                return os.path.exists(file_path)
            except OSError:
                return False

    async def download_binary(
        self,
        progress_callback: callable = None
    ) -> bool:
        """
        Download binary from GitHub releases.

        :param progress_callback: Callback function for progress updates (downloaded, total, filename)
        :type progress_callback: callable
        :return: True if download successful, False otherwise
        :rtype: bool
        """
        import aiohttp

        try:
            # Get release information
            release_info = await self.get_latest_release_info()

            # Find the appropriate asset for current platform
            platform_binary_name = self._get_platform_binary_name()
            download_url = None

            for asset in release_info.get("assets", []):
                if asset["name"] == platform_binary_name:
                    download_url = asset["browser_download_url"]
                    break

            if not download_url:
                raise BinaryError(
                    f"No binary available for your platform ({platform_binary_name})",
                    "PLATFORM_UNSUPPORTED",
                    [
                        "Check if your platform is supported by the aks-mcp project",
                        "Run without --aks-mcp to stay in traditional mode",
                        f"Manually install the binary from {self.GITHUB_RELEASES_URL} if available"
                    ]
                )

            # Create installation directory if it doesn't exist
            if not self._create_installation_directory():
                raise BinaryError(
                    f"Cannot create installation directory: {self.install_dir}",
                    "DIRECTORY_CREATION_FAILED",
                    [
                        "Check if you have write permissions to the Azure CLI config directory",
                        "Ensure sufficient disk space is available",
                        "Try running with elevated permissions if necessary"
                    ]
                )

            # Download the binary
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    download_url,
                    timeout=aiohttp.ClientTimeout(total=300)  # 5 minutes timeout
                ) as response:
                    if response.status != 200:
                        raise RuntimeError(f"Download failed with status {response.status}")

                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0

                    # Download with progress tracking
                    with open(self.binary_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                            downloaded += len(chunk)

                            if progress_callback and total_size > 0:
                                progress_callback(downloaded, total_size, platform_binary_name)

            # Verify download integrity using in-toto attestation (now synchronous)
            if not self._verify_binary_integrity(self.binary_path, release_info):
                # Clean up invalid binary
                try:
                    os.remove(self.binary_path)
                except OSError:
                    pass
                raise RuntimeError("Downloaded binary failed integrity check")

            # Make binary executable
            if not self._make_binary_executable(self.binary_path):
                raise RuntimeError("Failed to make binary executable")

            return True

        except Exception as e:
            # Clean up partial download on failure
            try:
                if os.path.exists(self.binary_path):
                    os.remove(self.binary_path)
            except OSError:
                pass
            raise e
