# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

if 'containerapp' not in helps.keys():
    helps['containerapp'] = """
    type: group
    short-summary: Manage Azure Container Apps.
"""

helps['containerapp compose'] = """
    type: group
    short-summary: Commands to manage Containerappss.
"""

helps['containerapp compose create'] = """
    type: command
    short-summary: Create a Containerapps.
"""
