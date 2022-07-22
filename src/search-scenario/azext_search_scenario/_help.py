# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['search-scenario'] = """
type: command
short-summary: It's a tool for searching E2E scenario samples.
long-summary: >

    There are some custom configurations:\n

    [1] az config set search_scenario.execute_in_prompt=True/False
        Turn on/off the step of executing scenario commands in interactive mode. Turn on by default.

    [2] az config set search_scenario.output=json/jsonc/none/table/tsv/yaml/yamlc/status
        Set default output format. Status is the default.

    [3] az config set search_scenario.show_arguments=True/False
        Show/hide the arguments of scenario commands. False is the default.

    [4] az config set search_scenario.print_help=True/False
        Enable/disable whether to print help actively before executing each command. False is the default.

"""
