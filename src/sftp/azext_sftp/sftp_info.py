# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os

from azure.cli.core import azclierror
from knack import log
from . import file_utils

logger = log.get_logger(__name__)


class SFTPSession():
    """Class to hold SFTP session information and connection details.

    Similar to SSH extension's SSHSession class, this encapsulates all
    connection parameters and provides methods for session management.
    """

    def __init__(self, storage_account, username=None, host=None, port=None,
                 public_key_file=None, private_key_file=None, cert_file=None,
                 sftp_args=None, ssh_client_folder=None, ssh_proxy_folder=None,
                 credentials_folder=None, yes_without_prompt=False, sftp_batch_commands=None):
        # Core connection parameters
        self.storage_account = storage_account
        self.username = username
        self.host = host
        self.port = port

        # Authentication files
        self.public_key_file = os.path.abspath(public_key_file) if public_key_file else None
        self.private_key_file = os.path.abspath(private_key_file) if private_key_file else None
        self.cert_file = os.path.abspath(cert_file) if cert_file else None

        # Additional configuration
        self.sftp_args = sftp_args or []
        self.ssh_client_folder = os.path.abspath(ssh_client_folder) if ssh_client_folder else None
        self.ssh_proxy_folder = os.path.abspath(ssh_proxy_folder) if ssh_proxy_folder else None
        self.credentials_folder = os.path.abspath(credentials_folder) if credentials_folder else None
        self.yes_without_prompt = yes_without_prompt
        self.sftp_batch_commands = sftp_batch_commands

        # Runtime state (similar to SSH extension patterns)
        self.delete_credentials = False
        self.local_user = None

    def resolve_connection_info(self):
        """Resolve connection information like hostname and username."""
        # Hostname should already be set by the caller using cloud-aware logic
        if not self.host:
            raise azclierror.ValidationError("Host must be set before calling resolve_connection_info()")

        # Extract username from certificate if available
        if self.cert_file and self.local_user:
            # Process username - extract username part if it's a UPN
            user = self.local_user
            if '@' in user:
                user = user.split('@')[0]

            # Build Azure Storage SFTP username format
            self.username = f"{self.storage_account}.{user}"
        elif not self.username:
            # Fallback username format (will be set by caller)
            self.username = f"{self.storage_account}.unknown"

    def build_args(self):
        """Build SSH/SFTP command line arguments.

        Returns:
            list: Command line arguments for SSH/SFTP client
        """
        args = []

        # Add private key if provided
        if self.private_key_file:
            args.extend(["-i", self.private_key_file])
        # Add certificate if provided
        if self.cert_file:
            args.extend(["-o", f"CertificateFile=\"{self.cert_file}\""])

        # Add port if specified
        if self.port is not None:
            args.extend(["-P", str(self.port)])

        return args

    def get_host(self):
        """Get the host for the connection (similar to SSH extension pattern)."""
        if not self.host:
            raise azclierror.ValidationError("Host not set. Call resolve_connection_info() first.")
        return self.host

    def get_destination(self):
        """Get the destination string for SFTP connection."""
        return f"{self.username}@{self.get_host()}"

    def validate_session(self):
        """Validate session configuration before connecting."""
        if not self.storage_account:
            raise azclierror.RequiredArgumentMissingError("Storage account name is required.")

        if not self.host:
            raise azclierror.ValidationError("Host information not resolved. Call resolve_connection_info() first.")

        if not self.username:
            raise azclierror.ValidationError("Username not resolved. Call resolve_connection_info() first.")

        # Validate certificate file exists if provided
        if self.cert_file and not os.path.isfile(self.cert_file):
            raise azclierror.FileOperationError(f"Certificate file {self.cert_file} not found.")

        # Validate key files exist if provided
        if self.public_key_file and not os.path.isfile(self.public_key_file):
            raise azclierror.FileOperationError(f"Public key file {self.public_key_file} not found.")

        if self.private_key_file and not os.path.isfile(self.private_key_file):
            raise azclierror.FileOperationError(f"Private key file {self.private_key_file} not found.")

    def is_cert_valid(self):
        """Check if the certificate is still valid."""
        if not self.cert_file:
            return None, "No certificate file provided"

        return file_utils.validate_certificate(self.cert_file, self.ssh_client_folder)
