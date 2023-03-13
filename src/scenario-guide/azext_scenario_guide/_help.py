# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['scenario'] = """
type: group
short-summary: E2E Scenario Usage Guidance
"""


helps['scenario guide'] = """
type: command
short-summary: Fuzzy search E2E scenario examples and execute them with walk-through
long-summary: >

    This an intelligent guidance tool that can help you find and execute E2E scenario samples!
    It supports fuzzy search and sort the searched results according to the matching degree from high to low.
    It supports flexible search scenarios, you can specify the search scope and customize the matching rules.
    Moreover, it helps you execute these E2E scenarios more efficiently with a friendly walk-through process.\n

    There are some custom configurations:\n

    [1] az config set scenario_guide.execute_in_prompt=True/False
        Turn on/off the step of executing scenario commands in interactive mode. Turn on by default.

    [2] az config set scenario_guide.output=json/jsonc/none/table/tsv/yaml/yamlc/status
        Set default output format. Status is the default.

    [3] az config set scenario_guide.show_arguments=True/False
        Show/hide the arguments of scenario commands. False is the default.

    [4] az config set scenario_guide.print_help=True/False
        Enable/disable whether to print help actively before executing each command. False is the default.

examples:
  - name: Search and execute scenario examples of how to connect the App Service to SQL Database.
    text: |-
        az scenario guide "app service database"
  - name: Search and execute scenario examples whose title or description related to app service or web app.
    text: |-
        az scenario guide "web app service" --scope "scenario" --match-rule "or"
  - name: Search and execute top 3 scenario examples whose commands contain keywords "network","vnet" and "subnet" at the same time.
    text: |-
        az scenario guide "network vnet subnet" --scope "command" --match-rule "and" --top 3

"""
