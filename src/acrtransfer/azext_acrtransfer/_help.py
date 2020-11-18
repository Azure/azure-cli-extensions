# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['acrtransfer'] = """
    type: group
    short-summary: Commands to manage Acrtransfers.
"""

helps['acrtransfer importpipeline create'] = """
    type: command
    short-summary: Create a Acrtransfer.
    parameters:
        - name: --storage-account-container-uri
          type: string
          short-summary: storage account container uri string
    examples: 
        - name: Create an import pipeline
          text: whatever
"""

helps['acrtransfer list'] = """
    type: command
    short-summary: List Acrtransfers.
"""

helps['acrtransfer delete'] = """
    type: command
    short-summary: Delete a Acrtransfer.
"""

helps['acrtransfer show'] = """
    type: command
    short-summary: Show details of a Acrtransfer.
"""

helps['acrtransfer update'] = """
    type: command
    short-summary: Update a Acrtransfer.
"""
