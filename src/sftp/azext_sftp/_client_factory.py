# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

def cf_sftp(cli_ctx, *_):  # pylint: disable=unused-argument
    """
    Client factory for SFTP extension.
    This extension doesn't require a specific Azure management client
    as it operates using SSH/SFTP protocols directly.
    """
    return None
