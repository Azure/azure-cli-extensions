# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['internet-analyzer profile'] = """
    type: group
    short-summary: Commands to manage internet analyzer profile.
"""

helps['internet-analyzer profile create'] = """
    type: command
    short-summary: create internet analyzer profile.
    examples:
      - name: Creates an Internet Analyzer Profile in a Resource Group
        text: |-
               az internet-analyzer profile create --resource-group "rg1" --name "Profile1" --location \\
               "WestUs" --enabled-state "Enabled"
"""

helps['internet-analyzer profile update'] = """
    type: command
    short-summary: update internet analyzer profile.
    examples:
      - name: Updates an Internet Analyzer Profile in a Resource Group
        text: |-
               az internet-analyzer profile update --resource-group "rg1" --name "Profile1" \\
               --enabled-state "Enabled"
"""

helps['internet-analyzer profile delete'] = """
    type: command
    short-summary: delete internet analyzer profile.
    examples:
      - name: Deletes an Internet Analyzer Profile in a Resource Group
        text: |-
               az internet-analyzer profile delete --resource-group "rg1" --name "Profile1"
"""

helps['internet-analyzer profile list'] = """
    type: command
    short-summary: list internet analyzer profiles.
"""

helps['internet-analyzer profile show'] = """
    type: command
    short-summary: show internet analyzer profile.
"""

helps['internet-analyzer preconfigured-endpoint'] = """
    type: group
    short-summary: Commands to manage preconfigured endpoints.
"""

helps['internet-analyzer preconfigured-endpoint list'] = """
    type: command
    short-summary: list preconfigured endpoints.
"""

helps['internet-analyzer test'] = """
    type: group
    short-summary: Commands to manage tests.
"""

helps['internet-analyzer test create'] = """
    type: command
    short-summary: create test.
    examples:
      - name: Creates a test
        text: |-
               az internet-analyzer test create --resource-group "rg1" --profile-name "Profile1" --name \\
               "Experiment1" --description "this is my first experiment!" --endpoint-a-name "endpoint A" \\
               --endpoint-a-endpoint "endpointA.net" --endpoint-b-name "endpoint B" \\
               --endpoint-b-endpoint "endpointB.net" --enabled-state "Enabled"
"""

helps['internet-analyzer test update'] = """
    type: command
    short-summary: update test.
    examples:
      - name: Updates a test
        text: |-
               az internet-analyzer test update --resource-group "rg1" --profile-name "Profile1" --name \\
               "Experiment1" --description "string" --enabled-state "Enabled"
"""

helps['internet-analyzer test delete'] = """
    type: command
    short-summary: delete test.
    examples:
      - name: Deletes a test
        text: |-
               az internet-analyzer test delete --resource-group "rg1" --profile-name "Profile1" --name \\
               "Experiment1"
"""

helps['internet-analyzer test list'] = """
    type: command
    short-summary: list tests.
"""

helps['internet-analyzer test show'] = """
    type: command
    short-summary: show test
"""

helps['internet-analyzer show-scorecard'] = """
    type: command
    short-summary: Show latency scorecard for a test.
"""

helps['internet-analyzer show-timeseries'] = """
    type: command
    short-summary: Show timeseries for a test.
    """
