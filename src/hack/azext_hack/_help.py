# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['hack'] = """
    type: group
    short-summary: Commands to manage resources commonly used for student hacks.
"""

helps['hack create'] = """
    type: command
    short-summary: Create resources commonly used for a student hack, including a website, database, and artificial intelligence.
    examples:
        - name: Create website using Python and MySQL
          text: az hack create --name samplename --runtime python --location westus2 --database mysql
        - name: Create website using Node.js, SQL and Cognitive Services key
          text: az hack create --name samplename --runtime node --location westus2 --database sql --ai
"""

helps['hack show'] = """
    type: command
    short-summary: Display settings for created resources, including database name and password, Git url, and website url.
    examples:
        - name: Display settings
          text: az hack show --name samplename
"""
