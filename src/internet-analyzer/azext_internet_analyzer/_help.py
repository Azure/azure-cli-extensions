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
    short-summary: Commands to manage network experiment profile.
"""

helps['internet-analyzer profile create'] = """
    type: command
    short-summary: create network experiment profile.
    examples:
      - name: Creates an NetworkExperiment Profile in a Resource Group
        text: |-
               az internet-analyzer profile create --profile-name "Profile1" --name "rg1" --location \\
               "WestUs" --enabled-state "Enabled"
"""

helps['internet-analyzer profile update'] = """
    type: command
    short-summary: update network experiment profile.
    examples:
      - name: Updates an Experiment
        text: |-
               az internet-analyzer profile update --profile-name "Profile1" --name "rg1" \\
               --enabled-state "Enabled"
"""

helps['internet-analyzer profile delete'] = """
    type: command
    short-summary: delete network experiment profile.
    examples:
      - name: Deletes an NetworkExperiment Profile by ProfileName
        text: |-
               az internet-analyzer profile delete --name "rg1" --profile-name "Profile1"
"""

helps['internet-analyzer profile list'] = """
    type: command
    short-summary: list network experiment profile.
"""

helps['internet-analyzer profile show'] = """
    type: command
    short-summary: show network experiment profile.
"""

helps['internet-analyzer preconfigured-endpoint'] = """
    type: group
    short-summary: Commands to manage preconfigured endpoint.
"""

helps['internet-analyzer preconfigured-endpoint list'] = """
    type: command
    short-summary: list preconfigured endpoint.
"""

helps['internet-analyzer experiment'] = """
    type: group
    short-summary: Commands to manage experiment.
"""

helps['internet-analyzer experiment create'] = """
    type: command
    short-summary: create experiment.
    examples:
      - name: Creates an Experiment
        text: |-
               az internet-analyzer experiment create --resource-group "rg1" --profile-name "Profile1" \\
               --name "Experiment1" --description "this is my first experiment!" --endpoint-a-name \\
               "endpoint A" --endpoint-a-endpoint "endpointA.net" --endpoint-b-name "endpoint B" \\
               --endpoint-b-endpoint "endpointB.net" --enabled-state "Enabled"
"""

helps['internet-analyzer experiment update'] = """
    type: command
    short-summary: update experiment.
    examples:
      - name: Updates an Experiment
        text: |-
               az internet-analyzer experiment update --resource-group "rg1" --profile-name "Profile1" \\
               --name "Experiment1" --description "string" --enabled-state "Enabled"
"""

helps['internet-analyzer experiment delete'] = """
    type: command
    short-summary: delete experiment.
    examples:
      - name: Deletes an Experiment
        text: |-
               az internet-analyzer experiment delete --resource-group "rg1" --profile-name "Profile1" \\
               --name "Experiment1"
"""

helps['internet-analyzer experiment list'] = """
    type: command
    short-summary: list experiment.
"""

helps['internet-analyzer experiment show'] = """
    type: command
    short-summary: show experiment.
"""

helps['internet-analyzer profile experiment timeseries'] = """
    type: group
    short-summary: Commands to manage report.
"""

