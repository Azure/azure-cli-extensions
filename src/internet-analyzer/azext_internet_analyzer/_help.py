# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['internet-analyzer'] = """
    type: group
    short-summary: Commands to manage internet analyzer.
"""

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
               az internet-analyzer profile create --resource-group "MyResourceGroup" --name "MyProfile" \\
               --location "WestUs" --enabled-state "Enabled"
"""

helps['internet-analyzer profile update'] = """
    type: command
    short-summary: update internet analyzer profile.
    examples:
      - name: Updates an Internet Analyzer Profile in a Resource Group
        text: |-
               az internet-analyzer profile update --resource-group "MyResourceGroup" --name "MyProfile" \\
               --enabled-state "Enabled"
"""

helps['internet-analyzer profile delete'] = """
    type: command
    short-summary: delete internet analyzer profile.
    examples:
      - name: Deletes an Internet Analyzer Profile in a Resource Group
        text: |-
               az internet-analyzer profile delete --resource-group "MyResourceGroup" --name "MyProfile"
"""

helps['internet-analyzer profile list'] = """
    type: command
    short-summary: list internet analyzer profiles.
    examples:
      - name: List Internet Analyzer Profiles in a Resource Group
        text: |-
               az internet-analyzer profile list --resource-group "MyResourceGroup"
"""

helps['internet-analyzer profile show'] = """
    type: command
    short-summary: show internet analyzer profile.
    examples:
      - name: Gets an Internet Analyzer Profile by Profile Id
        text: |-
               az internet-analyzer profile show --resource-group "MyResourceGroup" --name "MyProfile"
"""

helps['internet-analyzer preconfigured-endpoint'] = """
    type: group
    short-summary: Commands to manage preconfigured endpoints.
"""

helps['internet-analyzer preconfigured-endpoint list'] = """
    type: command
    short-summary: list preconfigured endpoints.
    examples:
      - name: Gets a list of Preconfigured Endpoints
        text: |-
               az internet-analyzer preconfigured-endpoint list --resource-group "MyResourceGroup" \\
               --profile-name "MyProfile"
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
               az internet-analyzer test create --resource-group "MyResourceGroup" --profile-name \\
               "MyProfile" --name "MyExperiment" --description "this is my first experiment!" \\
               --endpoint-a-name "endpoint A" --endpoint-a-endpoint "endpointA.net" --endpoint-b-name \\
               "endpoint B" --endpoint-b-endpoint "endpointB.net" --enabled-state "Enabled"
"""

helps['internet-analyzer test update'] = """
    type: command
    short-summary: update test.
    examples:
      - name: Updates a test
        text: |-
               az internet-analyzer test update --resource-group "MyResourceGroup" --profile-name \\
               "MyProfile" --name "MyExperiment" --description "string" --enabled-state "Enabled"
"""

helps['internet-analyzer test delete'] = """
    type: command
    short-summary: delete test.
    examples:
      - name: Deletes a test
        text: |-
               az internet-analyzer test delete --resource-group "MyResourceGroup" --profile-name \\
               "MyProfile" --name "MyExperiment"
"""

helps['internet-analyzer test list'] = """
    type: command
    short-summary: list tests.
    examples:
      - name: Gets a list of tests
        text: |-
               az internet-analyzer test list --resource-group "MyResourceGroup" --profile-name \\
               "MyProfile"
"""

helps['internet-analyzer test show'] = """
    type: command
    short-summary: show test
    examples:
      - name: Gets a test by name
        text: |-
               az internet-analyzer test show --resource-group "MyResourceGroup" --profile-name \\
               "MyProfile" --name "MyExperiment"
"""

helps['internet-analyzer show-scorecard'] = """
    type: command
    short-summary: Show latency scorecard for a test.
"""

helps['internet-analyzer show-timeseries'] = """
    type: command
    short-summary: Show timeseries for a test.
    """
