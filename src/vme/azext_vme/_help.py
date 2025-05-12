# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['vme'] = """
    type: group
    short-summary: Commands to manage version manged extensions.
"""

helps['vme install'] = """
    type: command
    short-summary: Install version managed extensions.
"""

helps['vme uninstall'] = """
    type: command
    short-summary: Uninstall version managed extensions.
"""

helps['vme upgrade'] = """
    type: command
    short-summary: Check version manged extensions' upgrade status.
"""
