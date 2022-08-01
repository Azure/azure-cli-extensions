# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['search-scenario'] = """
type: command
short-summary: Fuzzy search the E2E scenario examples you need
long-summary: >

    This is an intelligent search tool that can help you find and explore the E2E scenarios you need.
    It supports fuzzy search, and will sort the searched results according to the matching degree from high to low.
    It supports flexible custom settings and can search content according to the scope and matching rules you want.
    At the same time, it helps you use these E2E scenarios more efficiently with a friendly interactive process.\n

    There are some custom configurations:\n

    [1] az config set search_scenario.execute_in_prompt=True/False
        Turn on/off the step of executing scenario commands in interactive mode. Turn on by default.

    [2] az config set search_scenario.output=json/jsonc/none/table/tsv/yaml/yamlc/status
        Set default output format. Status is the default.

    [3] az config set search_scenario.show_arguments=True/False
        Show/hide the arguments of scenario commands. False is the default.

    [4] az config set search_scenario.print_help=True/False
        Enable/disable whether to print help actively before executing each command. False is the default.

examples:
  - name: Search scenario examples of how to connect the App Service to SQL Database.
    text: |-
        az search-scenario app service database
  - name: Search scenario examples whose title or description related to app service or web app.
    text: |-
        az search-scenario web app service --scope "scenario" --match-rule "or"
  - name: Search top 3 scenario examples whose commands contain keywords "network","vnet" and "subnet" at the same time.
    text: |-
        az search-scenario network vnet subnet --scope "command" --match-rule "and" --top 3

"""
