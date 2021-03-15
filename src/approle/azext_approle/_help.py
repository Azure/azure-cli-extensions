# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps[
    "approle"
] = """
    type: group
    short-summary: Commands to manage app roles.
"""

helps["approle list"] = """
    type: command
    short-summary: List app roles defined for application.
"""

helps[
    "approle assignment"
] = """
    type: group
    short-summary: Commands to manage assignment of app roles for service principals.
"""

helps[
    "approle assignment add"
] = """
    type: command
    short-summary: Assign an app role to a service principal.
"""

helps[
    "approle assignment list"
] = """
    type: command
    short-summary: List all app role assignments for service principal.
"""

helps[
    "approle assignment remove"
] = """
    type: command
    short-summary: Remove an app role from a service principal.
"""
