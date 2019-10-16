# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['networkexperiment profile'] = """
    type: group
    short-summary: Commands to manage network experiment profile.
"""

helps['networkexperiment profile create'] = """
    type: command
    short-summary: create network experiment profile.
    examples:
      - name: Creates an NetworkExperiment Profile in a Resource Group
        text: |-
               az networkexperiment profile create --profile-name "Profile1" --name "rg1" --location \\
               "WestUs" --enabled-state "Enabled"
"""

helps['networkexperiment profile update'] = """
    type: command
    short-summary: update network experiment profile.
    examples:
      - name: Updates an Experiment
        text: |-
               az networkexperiment profile update --profile-name "Profile1" --name "rg1" \\
               --enabled-state "Enabled"
"""

helps['networkexperiment profile delete'] = """
    type: command
    short-summary: delete network experiment profile.
    examples:
      - name: Deletes an NetworkExperiment Profile by ProfileName
        text: |-
               az networkexperiment profile delete --name "rg1" --profile-name "Profile1"
"""

helps['networkexperiment profile list'] = """
    type: command
    short-summary: list network experiment profile.
"""

helps['networkexperiment profile show'] = """
    type: command
    short-summary: show network experiment profile.
"""

helps['networkexperiment experiment'] = """
    type: group
    short-summary: Commands to manage experiment.
"""

helps['networkexperiment experiment create'] = """
    type: command
    short-summary: create experiment.
    examples:
      - name: Creates an Experiment
        text: |-
               az networkexperiment experiment create --resource-group "rg1" --profile-name "Profile1" \\
               --name "Experiment1" --description "this is my first experiment!" --endpoint-a-name \\
               "endpoint A" --endpoint-a-endpoint "endpointA.net" --endpoint-b-name "endpoint B" \\
               --endpoint-b-endpoint "endpointB.net" --enabled-state "Enabled"
"""

helps['networkexperiment experiment update'] = """
    type: command
    short-summary: update experiment.
    examples:
      - name: Updates an Experiment
        text: |-
               az networkexperiment experiment update --resource-group "rg1" --profile-name "Profile1" \\
               --name "Experiment1" --description "string" --enabled-state "Enabled"
"""

helps['networkexperiment experiment delete'] = """
    type: command
    short-summary: delete experiment.
    examples:
      - name: Deletes an Experiment
        text: |-
               az networkexperiment experiment delete --resource-group "rg1" --profile-name "Profile1" \\
               --name "Experiment1"
"""

helps['networkexperiment experiment list'] = """
    type: command
    short-summary: list experiment.
"""

helps['networkexperiment experiment show'] = """
    type: command
    short-summary: show experiment.
"""

helps['-'] = """
    type: group
    short-summary: Commands to manage front door.
"""

helps['-'] = """
    type: group
    short-summary: Commands to manage policy.
"""
