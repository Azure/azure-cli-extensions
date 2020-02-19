# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['attestation operations'] = """
    type: group
    short-summary: attestation operations
"""

helps['attestation operations list'] = """
    type: command
    short-summary: Lists all of the available Azure attestation operations.
"""

helps['attestation attestation_providers'] = """
    type: group
    short-summary: attestation attestation-providers
"""

helps['attestation attestation-providers list'] = """
    type: command
    short-summary: Returns a list of attestation providers in a subscription.
"""

helps['attestation attestation-providers show'] = """
    type: command
    short-summary: Get the status of Attestation Provider.
"""

helps['attestation attestation-providers create'] = """
    type: command
    short-summary: Creates or updates the Attestation Provider.
"""

helps['attestation attestation-providers delete'] = """
    type: command
    short-summary: Delete Attestation Service.
"""
