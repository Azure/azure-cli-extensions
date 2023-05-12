# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps[
    "aosm"
] = """
    type: group
    short-summary: Commands to interact with Azure Operator Service Manager (AOSM).
"""

helps[
    "aosm definition"
] = """
    type: group
    short-summary: Manage AOSM publisher definitions.
"""

helps[
    "aosm definition generate-config"
] = """
    type: command
    short-summary: Generate configuration file for building an AOSM publisher definition.
"""

helps[
    "aosm definition build"
] = """
    type: command
    short-summary: Build an AOSM publisher definition.
"""

helps[
    "aosm definition publish"
] = """
    type: command
    short-summary: Publish a pre-built AOSM publisher definition.
"""


helps[
    "aosm definition delete"
] = """
    type: command
    short-summary: Delete AOSM publisher definition.
"""
