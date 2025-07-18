# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Azure CLI SFTP Extension

This extension provides secure SFTP connectivity to Azure Storage Accounts
with automatic Azure AD authentication and certificate management.

Key Features:
- Fully managed SSH certificate generation using Azure AD
- Support for existing SSH keys and certificates
- Interactive and batch SFTP operations
- Automatic credential cleanup for security
- Integration with Azure Storage SFTP endpoints

Commands:
- az sftp cert: Generate SSH certificates for SFTP authentication
- az sftp connect: Connect to Azure Storage Account via SFTP
"""

from azure.cli.core import AzCommandsLoader

from azext_sftp._help import helps  # pylint: disable=unused-import


class SftpCommandsLoader(AzCommandsLoader):
    """Command loader for the SFTP extension."""

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType

        super().__init__(
            cli_ctx=cli_ctx,
            custom_command_type=CliCommandType(
                operations_tmpl='azext_sftp.custom#{}'))

    def load_command_table(self, args):
        """Load the command table for SFTP commands."""
        from azext_sftp.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        """Load arguments for SFTP commands."""
        from azext_sftp._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = SftpCommandsLoader
