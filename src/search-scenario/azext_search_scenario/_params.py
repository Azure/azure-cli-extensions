# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType


def load_arguments(self, _):

    from azure.cli.core.commands.parameters import get_enum_type

    with self.argument_context('search-scenario') as c:
        c.positional('search_keyword', help="Keywords used to search. Every word will match")
        c.argument('type', arg_type=get_enum_type(["all", "scenario", "command"], default='all'),
                   help = 'Specifies the search range. ')
        c.argument('top', type=int, default=5,
                   help='Specifies the number of results to return. Max value: 20', )
