# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_mcp.server import AzMCP


def mcp_up(cmd):
    az_mcp = AzMCP(
        cli_ctx=cmd.cli_ctx,
        name='AzMCP',
    )
    az_mcp.run()
