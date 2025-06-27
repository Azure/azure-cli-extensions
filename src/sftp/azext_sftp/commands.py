# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Command definitions for the Azure CLI SFTP extension.

This module defines the available SFTP commands and their routing
to the appropriate custom functions.
"""


def load_command_table(self, _):
    """
    Load command table for SFTP extension.

    Commands:
    - sftp cert: Generate SSH certificates for SFTP authentication
    - sftp connect: Connect to Azure Storage Account via SFTP
    """
    with self.command_group('sftp') as g:
        g.custom_command('cert', 'sftp_cert')
        g.custom_command('connect', 'sftp_connect')
