# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long


def load_arguments(self, _):

    from azure.cli.core.commands.parameters import get_enum_type

    with self.argument_context('scenario guide') as c:
        c.positional('search_keyword', nargs='+', help="Keywords for search. If there are multiple keywords, please separate them with spaces. Fuzzy search is supported, and the returned results are sorted by keyword matching degree.")
        c.argument('scope', arg_type=get_enum_type(["all", "scenario", "command"], default='all'),
                   help='The scope of search: "scenario" is to search whether the title and description in E2E scenario data contain keywords, "command" is to search whether the commands in E2E scenario data contain keywords, "all" is to search all contents.')
        c.argument('match_rule', arg_type=get_enum_type(["all", "and", "or"]), default="all",
                   help='The matching rules for multi-keywords: "and" is to search scenarios that match all keywords, "or" is to search scenarios that match any keyword, "all" is to search scenarios that match all keywords first, if the number is not enough then search any keyword.')
        c.argument('top', type=int, default=5,
                   help='Specify the number of results to return. The maximum value is limited to 20. ')
