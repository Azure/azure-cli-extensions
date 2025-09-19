# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_mcp.server import AzMCP


def mcp_up(cmd, disable_elicit=False):
    az_mcp = AzMCP(
        cli_ctx=cmd.cli_ctx,
        name='AzMCP',
        enable_elicit=not disable_elicit
    )
    az_mcp.run()
