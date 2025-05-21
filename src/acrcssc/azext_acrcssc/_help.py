# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

helps['acr supply-chain'] = """
    type: group
    short-summary: Commands to manage acr supply chain resources.
"""

helps['acr supply-chain workflow'] = """
    type: group
    short-summary: Commands to manage acr supply chain workflows.
"""

helps['acr supply-chain workflow create'] = """
    type: command
    short-summary: Create acr supply chain workflow.
    examples:
        - name: Create acr supply chain workflow
          text: az acr supply-chain workflow create -r $MyRegistry -g $MyResourceGroup \
                --type continuouspatchv1 --schedule 1d --config path-to-config-file
"""
helps['acr supply-chain workflow update'] = """
    type: command
    short-summary: Update acr supply chain workflow.
    examples:
        - name: Update acr supply chain workflow
          text: az acr supply-chain workflow update -r $MyRegistry -g $MyResourceGroup --type \
                continuouspatchv1 --schedule 1d --config path-to-config-file
"""

helps['acr supply-chain workflow show'] = """
     type: command
     short-summary: Show acr supply chain workflow tasks.
     examples:
        - name: Show all acr supply chain workflow
          text: az acr supply-chain workflow show -r $MyRegistry -g $MyResourceGroup --type continuouspatchv1
"""

helps['acr supply-chain workflow delete'] = """
    type: command
    short-summary: Delete acr supply chain workflow.
    examples:
        - name: Delete acr supply chain workflow and associated configuration files
          text: az acr supply-chain workflow delete -r $MyRegistry -g $MyResourceGroup --type continuouspatchv1
"""

helps['acr supply-chain workflow cancel-run'] = """
    type: command
    short-summary: Cancel currently running supply chain workflow.
    examples:
        - name: Cancel currently running acr supply chain workflow scans/patch
          text: az acr supply-chain workflow cancel-run -r $MyRegistry -g $MyResourceGroup --type continuouspatchv1
"""

helps['acr supply-chain workflow list'] = """
    type: command
    short-summary: List status of acr supply chain workflow images.
    examples:
        - name: List all acr supply chain workflow images based on the status provided
          text: az acr supply-chain workflow list -r $MyRegistry -g $MyResourceGroup --type continuouspatchv1 --run-status Failed
"""
