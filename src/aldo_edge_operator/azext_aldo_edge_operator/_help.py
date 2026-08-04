# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['aldo-edge-operator'] = """
    type: group
    short-summary: Manage ALDO EdgeOperator resources.
"""

helps['aldo-edge-operator billing-configuration'] = """
    type: group
    short-summary: Manage ALDO billing configuration resources.
"""

helps['aldo-edge-operator billing-configuration show'] = """
    type: command
    short-summary: Show the active billing configuration singleton for the current subscription.
"""

helps['aldo-edge-operator billing-configuration create-or-update'] = """
    type: command
    short-summary: Create or fully replace the active billing configuration singleton.
"""

helps['aldo-edge-operator billing-configuration list'] = """
    type: command
    short-summary: List billing configuration resources for the current subscription.
"""

helps['aldo-edge-operator billing-configuration snapshot'] = """
    type: group
    short-summary: Manage immutable billing configuration snapshots.
"""

helps['aldo-edge-operator billing-configuration snapshot show'] = """
    type: command
    short-summary: Show a billing configuration snapshot by name.
"""

helps['aldo-edge-operator billing-configuration snapshot list'] = """
    type: command
    short-summary: List billing configuration snapshots.
"""
