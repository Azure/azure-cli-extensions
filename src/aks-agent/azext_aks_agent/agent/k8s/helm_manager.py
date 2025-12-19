# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import platform
import shutil
import stat
import subprocess
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import List, Optional, Tuple

from azext_aks_agent._consts import HELM_VERSION
from knack.log import get_logger

logger = get_logger(__name__)


class HelmManager:
    """
    Helm Binary Manager for OS-agnostic helm operations.

    This class provides functionality to:
    - Download and manage helm binaries locally
    - Support multiple operating systems and architectures
    - Execute helm commands using the managed binary
    - Share helm functionality across different chart deployments
    """

    def __init__(self, helm_version: str = HELM_VERSION, local_bin_dir: Optional[str] = None,
                 kubeconfig_path: Optional[str] = None):
        """
        Initialize the Helm Manager.

        Args:
            helm_version: Helm version to use (default: HELM_VERSION from _consts)
            local_bin_dir: Local directory for helm binary (default: ~/.aks-agent/bin)
            kubeconfig_path: Path to kubeconfig file (default: None - use default config)
        """
        self.helm_version = helm_version
        self.kubeconfig_path = kubeconfig_path

        # Set up local binary directory
        if local_bin_dir:
            self.local_bin_dir = Path(local_bin_dir)
        else:
            home_dir = Path.home()
            self.local_bin_dir = home_dir / ".aks-agent" / "bin"

        self.local_bin_dir.mkdir(parents=True, exist_ok=True)
        self.helm_binary_path = self._ensure_helm_binary()

    def _get_platform_info(self) -> Tuple[str, str]:
        """
        Get platform-specific information for helm binary download.

        Returns:
            Tuple of (os_name, arch) for helm binary selection
        """
        system = platform.system().lower()
        machine = platform.machine().lower()

        # Map system names
        if system == "darwin":
            os_name = "darwin"
        elif system == "windows":
            os_name = "windows"
        elif system == "linux":
            os_name = "linux"
        else:
            raise ValueError(f"Unsupported operating system: {system}")

        # Map architecture names
        if machine in ("x86_64", "amd64"):
            arch = "amd64"
        elif machine in ("aarch64", "arm64"):
            arch = "arm64"
        elif machine.startswith("arm"):
            arch = "arm"
        elif machine in ("i386", "i686"):
            arch = "386"
        else:
            # Default to amd64 for unknown architectures
            logger.warning("Unknown architecture %s, defaulting to amd64", machine)
            arch = "amd64"

        return os_name, arch

    def _download_helm_binary(self) -> str:
        """
        Download helm binary for the current platform.

        Returns:
            Path to the downloaded helm binary
        """
        os_name, arch = self._get_platform_info()

        # Construct download URL
        if os_name == "windows":
            filename = f"helm-v{self.helm_version}-{os_name}-{arch}.zip"
            binary_name = "helm.exe"
        else:
            filename = f"helm-v{self.helm_version}-{os_name}-{arch}.tar.gz"
            binary_name = "helm"

        download_url = f"https://get.helm.sh/{filename}"
        logger.info("Downloading helm binary from: %s", download_url)

        # Download to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{filename.split('.')[-1]}") as temp_file:
            try:
                with urllib.request.urlopen(download_url) as response:
                    shutil.copyfileobj(response, temp_file)
                temp_file_path = temp_file.name
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("Failed to download helm binary: %s", e)
                raise

        # Extract binary
        extracted_binary_path = None
        try:
            if os_name == "windows":
                # Handle ZIP file
                with zipfile.ZipFile(temp_file_path, 'r') as zip_file:
                    # Find the helm binary in the zip
                    for member in zip_file.namelist():
                        if member.endswith(binary_name):
                            # Extract to local bin directory
                            zip_file.extract(member, self.local_bin_dir)
                            extracted_path = self.local_bin_dir / member
                            extracted_binary_path = self.local_bin_dir / binary_name
                            # Move to final location if needed
                            if extracted_path != extracted_binary_path:
                                shutil.move(str(extracted_path), str(extracted_binary_path))
                                # Clean up extracted directory if it exists
                                parent_dir = extracted_path.parent
                                if parent_dir != self.local_bin_dir and parent_dir.exists():
                                    shutil.rmtree(parent_dir)
                            break
            else:
                # Handle TAR.GZ file
                with tarfile.open(temp_file_path, 'r:gz') as tar_file:
                    # Find the helm binary in the tar
                    for member in tar_file.getnames():
                        if member.endswith(binary_name):
                            # Extract to local bin directory
                            tar_file.extract(member, self.local_bin_dir)
                            extracted_path = self.local_bin_dir / member
                            extracted_binary_path = self.local_bin_dir / binary_name
                            # Move to final location if needed
                            if extracted_path != extracted_binary_path:
                                shutil.move(str(extracted_path), str(extracted_binary_path))
                                # Clean up extracted directory if it exists
                                parent_dir = extracted_path.parent
                                if parent_dir != self.local_bin_dir and parent_dir.exists():
                                    shutil.rmtree(parent_dir)
                            break

            if not extracted_binary_path or not extracted_binary_path.exists():
                raise ValueError("Helm binary not found in downloaded archive")

            # Make binary executable on Unix systems
            if os_name != "windows":
                extracted_binary_path.chmod(extracted_binary_path.stat().st_mode | stat.S_IEXEC)

            logger.info("Helm binary downloaded and extracted to: %s", extracted_binary_path)
            return str(extracted_binary_path)

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Failed to extract helm binary: %s", e)
            raise
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass

    def _ensure_helm_binary(self) -> str:
        """
        Ensure helm binary is available locally.

        Returns:
            Path to helm binary
        """
        os_name, _ = self._get_platform_info()
        binary_name = "helm.exe" if os_name == "windows" else "helm"
        binary_path = self.local_bin_dir / binary_name

        # Check if binary already exists and is executable
        if binary_path.exists():
            try:
                # Test if binary works
                result = subprocess.run(
                    [str(binary_path), "version", "--client", "--short"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    logger.debug("Using existing helm binary: %s", binary_path)
                    return str(binary_path)
                logger.warning("Existing helm binary is not working, downloading new one")
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.warning("Failed to test existing helm binary: %s", e)

        # Download helm binary
        return self._download_helm_binary()

    def run_command(self, args: List[str], check: bool = True,  # pylint: disable=too-many-return-statements
                    timeout: int = 300) -> Tuple[bool, str]:
        """
        Execute a helm command using the locally managed helm binary.

        Args:
            args: List of helm command arguments
            check: Whether to raise exception on non-zero exit code
            timeout: Command timeout in seconds

        Returns:
            Tuple of (success, output)
        """
        cmd = [self.helm_binary_path]

        # Add --kubeconfig flag if specified
        if self.kubeconfig_path:
            cmd.extend(["--kubeconfig", self.kubeconfig_path])
            logger.debug("Using kubeconfig: %s", self.kubeconfig_path)

        cmd.extend(args)
        logger.debug("Executing helm command: %s", ' '.join(cmd))

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check,
                timeout=timeout
            )

            if result.returncode == 0:
                logger.debug("Helm command succeeded: %s", result.stdout)
                return True, result.stdout
            # Check if this is a "release not found" error
            stderr_lower = result.stderr.lower()
            if "release: not found" in stderr_lower or "not found" in stderr_lower:
                logger.debug("Helm release not found: %s", result.stderr)
                return False, "RELEASE_NOT_FOUND"

            logger.error("Helm command failed: %s", result.stderr)
            return False, result.stderr

        except subprocess.TimeoutExpired:
            error_msg = f"Helm command timed out: {' '.join(cmd)}"
            logger.error("%s", error_msg)
            return False, error_msg
        except subprocess.CalledProcessError as e:
            # Check if this is a "release not found" error
            stderr_lower = e.stderr.lower() if e.stderr else ""
            if "release: not found" in stderr_lower or "not found" in stderr_lower:
                logger.debug("Helm release not found: %s", e.stderr)
                return False, "RELEASE_NOT_FOUND"

            error_msg = f"Helm command failed with exit code {e.returncode}: {e.stderr}"
            logger.error("%s", error_msg)
            return False, error_msg
        except Exception as e:  # pylint: disable=broad-exception-caught
            error_msg = f"Unexpected error running helm command: {e}"
            logger.error("%s", error_msg)
            return False, error_msg

    def get_version(self) -> Optional[str]:
        """
        Get the version of the helm binary.

        Returns:
            Helm version string or None if failed
        """
        success, output = self.run_command(["version", "--client", "--short"], check=False)
        if success:
            return output.strip()
        return None

    def repo_add(self, name: str, url: str) -> bool:
        """
        Add a helm repository.

        Args:
            name: Repository name
            url: Repository URL

        Returns:
            True if successful
        """
        success, _ = self.run_command(["repo", "add", name, url])
        return success

    def repo_update(self) -> bool:
        """
        Update helm repositories.

        Returns:
            True if successful
        """
        success, _ = self.run_command(["repo", "update"])
        return success


def create_helm_manager(helm_version: str = HELM_VERSION,
                        local_bin_dir: Optional[str] = None) -> HelmManager:
    """
    Factory function to create a HelmManager instance.

    Args:
        helm_version: Helm version to use (default: HELM_VERSION from _consts)
        local_bin_dir: Local directory for helm binary

    Returns:
        HelmManager instance
    """
    return HelmManager(
        helm_version=helm_version,
        local_bin_dir=local_bin_dir
    )
