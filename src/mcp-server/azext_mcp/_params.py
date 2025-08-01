# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType


def load_arguments(self, _):

    with self.argument_context('mcp') as c:
        pass

    with self.argument_context('mcp up') as c:
        # c.argument('port', required=False, default=8080, type=int, help='MCP server port.')
        pass
