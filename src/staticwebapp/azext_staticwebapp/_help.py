# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['staticwebapp dbconnection'] = """
    type: group
    short-summary: Manage Static Web App database connections.
"""

helps['staticwebapp dbconnection create'] = """
    type: command
    short-summary: Create a Static Web App database connection.
"""

helps['staticwebapp dbconnection show'] = """
    type: command
    short-summary: Get details for a Static Web App database connection.
"""

helps['staticwebapp dbconnection delete'] = """
    type: command
    short-summary: Delete a Static Web App database connection.
"""
