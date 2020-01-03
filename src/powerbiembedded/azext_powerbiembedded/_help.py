# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import

helps['powerbi-embedded'] = """
    type: group
    short-summary: Manage Azure Power BI Embedded.
"""

helps['powerbi-embedded workspace-collection'] = """
    type: group
    short-summary: Commands to manage powerbi-embedded workspace collection.
"""

helps['powerbi-embedded workspace-collection create'] = """
    type: command
    short-summary: Creates a new Power BI Workspace Collection with the specified properties. A Power BI Workspace Collection contains one or more workspaces, and can be used to provision keys that provide API access to those workspaces.
"""

helps['powerbi-embedded workspace-collection update'] = """
    type: command
    short-summary: Creates a new Power BI Workspace Collection with the specified properties. A Power BI Workspace Collection contains one or more workspaces, and can be used to provision keys that provide API access to those workspaces.
"""

helps['powerbi-embedded workspace-collection delete'] = """
    type: command
    short-summary: Delete a Power BI Workspace Collection.
"""

helps['powerbi-embedded workspace-collection show'] = """
    type: command
    short-summary: Retrieves an existing Power BI Workspace Collection.
"""

helps['powerbi-embedded workspace-collection list'] = """
    type: command
    short-summary: Retrieves all existing Power BI workspace collections in the specified resource group.
"""

helps['powerbi-embedded workspace-collection check-name-availability'] = """
    type: command
    short-summary: Verify the specified Power BI Workspace Collection name is valid and not already in use.
"""

helps['powerbi-embedded workspace-collection get-access-keys'] = """
    type: command
    short-summary: Retrieves the primary and secondary access keys for the specified Power BI Workspace Collection.
"""

helps['powerbi-embedded workspace-collection regenerate-key'] = """
    type: command
    short-summary: Regenerates the primary or secondary access key for the specified Power BI Workspace Collection.
"""

helps['powerbi-embedded workspace-collection workspace'] = """
    type: group
    short-summary: Commands to manage powerbi-embedded workspace collection workspace.
"""

helps['powerbi-embedded workspace-collection workspace list'] = """
    type: command
    short-summary: Retrieves all existing Power BI workspaces in the specified workspace collection.
"""
