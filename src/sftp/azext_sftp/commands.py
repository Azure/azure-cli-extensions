# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Command definitions for the Azure CLI SFTP extension."""


def load_command_table(self, _):
    """Load command table for SFTP extension."""
    with self.command_group('sftp') as g:
        g.custom_command('cert', 'sftp_cert')
        g.custom_command('connect', 'sftp_connect')
