# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os

from azure.cli.core import azclierror
from knack import log

logger = log.get_logger(__name__)


# pylint: disable=too-few-public-methods
class ConnectionInfo:
    """Encapsulates connection-specific information."""

    def __init__(self, storage_account, username=None, host=None, port=None):
        self.storage_account = storage_account
        self.username = username
        self.host = host
        self.port = port


# pylint: disable=too-few-public-methods
class AuthenticationFiles:
    """Encapsulates authentication file paths."""

    def __init__(self, public_key_file=None, private_key_file=None, cert_file=None):
        self.public_key_file = os.path.abspath(os.path.expanduser(public_key_file)) if public_key_file else None
        self.private_key_file = os.path.abspath(os.path.expanduser(private_key_file)) if private_key_file else None
        self.cert_file = os.path.abspath(os.path.expanduser(cert_file)) if cert_file else None


# pylint: disable=too-few-public-methods
class SessionConfiguration:
    """Encapsulates session configuration options."""

    def __init__(self, sftp_args=None, ssh_client_folder=None, ssh_proxy_folder=None,
                 credentials_folder=None, yes_without_prompt=False):
        self.sftp_args = sftp_args or []
        self.ssh_client_folder = os.path.abspath(ssh_client_folder) if ssh_client_folder else None
        self.ssh_proxy_folder = os.path.abspath(ssh_proxy_folder) if ssh_proxy_folder else None
        self.credentials_folder = os.path.abspath(credentials_folder) if credentials_folder else None
        self.yes_without_prompt = yes_without_prompt


# pylint: disable=too-few-public-methods
class RuntimeState:
    """Encapsulates runtime state information."""

    def __init__(self):
        self.delete_credentials = False
        self.local_user = None


class SFTPSession():
    """Class to hold SFTP session information and connection details."""

    def __init__(self, storage_account, username=None, host=None, port=None,
                 public_key_file=None, private_key_file=None, cert_file=None,
                 sftp_args=None, ssh_client_folder=None, ssh_proxy_folder=None,
                 credentials_folder=None, yes_without_prompt=False):
        self.connection = ConnectionInfo(storage_account, username, host, port)
        self.auth_files = AuthenticationFiles(public_key_file, private_key_file, cert_file)
        self.config = SessionConfiguration(sftp_args, ssh_client_folder, ssh_proxy_folder,
                                           credentials_folder, yes_without_prompt)
        self.runtime = RuntimeState()

    @property
    def storage_account(self):
        """Get storage account name."""
        return self.connection.storage_account

    @storage_account.setter
    def storage_account(self, value):
        """Set storage account name."""
        self.connection.storage_account = value

    @property
    def username(self):
        """Get username."""
        return self.connection.username

    @username.setter
    def username(self, value):
        """Set username."""
        self.connection.username = value

    @property
    def host(self):
        """Get host."""
        return self.connection.host

    @host.setter
    def host(self, value):
        """Set host."""
        self.connection.host = value

    @property
    def port(self):
        """Get port."""
        return self.connection.port

    @port.setter
    def port(self, value):
        """Set port."""
        self.connection.port = value

    @property
    def public_key_file(self):
        """Get public key file path."""
        return self.auth_files.public_key_file

    @public_key_file.setter
    def public_key_file(self, value):
        """Set public key file path."""
        self.auth_files.public_key_file = os.path.abspath(value) if value else None

    @property
    def private_key_file(self):
        """Get private key file path."""
        return self.auth_files.private_key_file

    @private_key_file.setter
    def private_key_file(self, value):
        """Set private key file path."""
        self.auth_files.private_key_file = os.path.abspath(value) if value else None

    @property
    def cert_file(self):
        """Get certificate file path."""
        return self.auth_files.cert_file

    @cert_file.setter
    def cert_file(self, value):
        """Set certificate file path."""
        self.auth_files.cert_file = os.path.abspath(value) if value else None

    @property
    def sftp_args(self):
        """Get SFTP arguments."""
        return self.config.sftp_args

    @sftp_args.setter
    def sftp_args(self, value):
        """Set SFTP arguments."""
        self.config.sftp_args = value or []

    @property
    def ssh_client_folder(self):
        """Get SSH client folder path."""
        return self.config.ssh_client_folder

    @ssh_client_folder.setter
    def ssh_client_folder(self, value):
        """Set SSH client folder path."""
        self.config.ssh_client_folder = os.path.abspath(value) if value else None

    @property
    def ssh_proxy_folder(self):
        """Get SSH proxy folder path."""
        return self.config.ssh_proxy_folder

    @ssh_proxy_folder.setter
    def ssh_proxy_folder(self, value):
        """Set SSH proxy folder path."""
        self.config.ssh_proxy_folder = os.path.abspath(value) if value else None

    @property
    def credentials_folder(self):
        """Get credentials folder path."""
        return self.config.credentials_folder

    @credentials_folder.setter
    def credentials_folder(self, value):
        """Set credentials folder path."""
        self.config.credentials_folder = os.path.abspath(value) if value else None

    @property
    def yes_without_prompt(self):
        """Get yes without prompt flag."""
        return self.config.yes_without_prompt

    @yes_without_prompt.setter
    def yes_without_prompt(self, value):
        """Set yes without prompt flag."""
        self.config.yes_without_prompt = value

    @property
    def delete_credentials(self):
        """Get delete credentials flag."""
        return self.runtime.delete_credentials

    @delete_credentials.setter
    def delete_credentials(self, value):
        """Set delete credentials flag."""
        self.runtime.delete_credentials = value

    @property
    def local_user(self):
        """Get local user."""
        return self.runtime.local_user

    @local_user.setter
    def local_user(self, value):
        """Set local user."""
        self.runtime.local_user = value

    def resolve_connection_info(self):
        """Resolve connection information like hostname and username."""
        if not self.connection.host:
            raise azclierror.ValidationError("Host must be set before calling resolve_connection_info()")

        if self.auth_files.cert_file and self.runtime.local_user:
            user = self.runtime.local_user
            if '@' in user:
                user = user.split('@')[0]

            self.connection.username = f"{self.connection.storage_account}.{user}"
        elif not self.connection.username:
            self.connection.username = f"{self.connection.storage_account}.unknown"

    def build_args(self):
        """Build SSH/SFTP command line arguments."""
        args = []

        if self.auth_files.private_key_file:
            args.extend(["-i", self.auth_files.private_key_file])
        if self.auth_files.cert_file:
            args.extend(["-o", f"CertificateFile=\"{self.auth_files.cert_file}\""])

        if self.connection.port is not None:
            args.extend(["-P", str(self.connection.port)])

        return args

    def get_host(self):
        """Get the host for the connection."""
        if not self.connection.host:
            raise azclierror.ValidationError("Host not set. Call resolve_connection_info() first.")
        return self.connection.host

    def get_destination(self):
        """Get the destination string for SFTP connection."""
        return f"{self.connection.username}@{self.get_host()}"

    def validate_session(self):
        """Validate session configuration before connecting."""
        if not self.connection.storage_account:
            raise azclierror.RequiredArgumentMissingError("Storage account name is required.")

        if not self.connection.host:
            raise azclierror.ValidationError("Host information not resolved. Call resolve_connection_info() first.")

        if not self.connection.username:
            raise azclierror.ValidationError("Username not resolved. Call resolve_connection_info() first.")

        if self.auth_files.cert_file and not os.path.isfile(self.auth_files.cert_file):
            raise azclierror.FileOperationError(f"Certificate file {self.auth_files.cert_file} not found.")

        if self.auth_files.public_key_file and not os.path.isfile(self.auth_files.public_key_file):
            raise azclierror.FileOperationError(f"Public key file {self.auth_files.public_key_file} not found.")

        if self.auth_files.private_key_file and not os.path.isfile(self.auth_files.private_key_file):
            raise azclierror.FileOperationError(f"Private key file {self.auth_files.private_key_file} not found.")
