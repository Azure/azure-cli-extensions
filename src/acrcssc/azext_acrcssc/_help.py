# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

helps['acr supply-chain'] = """
    type: group
    short-summary: Commands to manage acr supply chain workflow.
"""

helps['acr supply-chain task'] = """
    type: group
    short-summary: Commands to manage acr supply chain workflow tasks.
"""

helps['acr supply-chain task create'] = """
    type: command
    short-summary: Create acr supply chain tasks.
    examples:
        - name: Create acr supply chain task
          text: az acr supply-chain task create -r $MyRegistry -g $MyResourceGroup \
                --task-type ContinuousPatchV1 --cadence 1d --config path-to-config-file --dry-run false
"""
helps['acr supply-chain task update'] = """
    type: command
    short-summary: Update acr supply chain task properties.
    examples:
        - name: Updates acr supply chain task
          text: az acr supply-chain task update -r $MyRegistry -g $MyResourceGroup --task-type \
                ContinuousPatchV1 --cadence 1d --config path-to-config-file --dry-run false
"""

helps['acr supply-chain task show'] = """
     type: command
     short-summary: Show acr supply chain tasks.
     examples:
        - name: Show all acr supply chain tasks
          text: az acr supply-chain task show -r $MyRegistry -g $MyResourceGroup --task-type ContinuousPatchV1
"""

helps['acr supply-chain task delete'] = """
    type: command
    short-summary: Delete acr supply chain tasks.
    examples:
        - name: Delete acr supply chain tasks and associated configuration files
          text: az acr supply-chain task delete -r $MyRegistry -g $MyResourceGroup --task-type ContinuousPatchV1
"""
