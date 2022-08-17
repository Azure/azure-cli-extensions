# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['next'] = """
type: command
short-summary: Recommend the possible next set of commands to take
long-summary: >
    There are some custom configurations:\n

    [1] az config set next.execute_in_prompt=True/False
        Turn on/off the step of executing recommended commands in interactive mode. Turn on by default.

    [2] az config set next.filter_type=True/False
        Turn on/off the step of filtering recommendation type. Turn off by default.

    [3] az config set next.output=json/jsonc/none/table/tsv/yaml/yamlc/status
        Set default output format. Status is the default.

    [4] az config set next.num_limit={amount_limit}
        Set the limit of recommended items. 5 is the default.

    [5] az config set next.show_arguments=True/False
        Show/hide the arguments of recommended items. False is the default.

    [6] az config set next.print_help=True/False
        Enable/disable whether to print help actively before executing each command. False is the default.

"""
