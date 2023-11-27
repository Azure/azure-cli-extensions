# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.help_files import helps

helps[
    "aosm"
] = """
    type: group
    short-summary: Commands to interact with Azure Operator Service Manager (AOSM).
"""

helps[
    "aosm nfd"
] = """
    type: group
    short-summary: Manage AOSM publisher Network Function Definitions.
"""

helps[
    "aosm nfd generate-config"
] = """
    type: command
    short-summary: Generate configuration file for building an AOSM publisher Network Function Definition.
"""

helps[
    "aosm nfd build"
] = """
    type: command
    short-summary: Build an AOSM Network Function Definition.
"""

helps[
    "aosm nfd publish"
] = """
    type: command
    short-summary: Publish a pre-built AOSM Network Function definition.
"""


helps[
    "aosm nfd delete"
] = """
    type: command
    short-summary: Delete AOSM Network Function Definition.
"""

helps[
    "aosm nsd"
] = """
    type: group
    short-summary: Manage AOSM publisher Network Service Designs.
"""

helps[
    "aosm nsd generate-config"
] = """
    type: command
    short-summary: Generate configuration file for building an AOSM publisher Network Service Design.
"""

helps[
    "aosm nsd build"
] = """
    type: command
    short-summary: Build an AOSM Network Service Design.
"""

helps[
    "aosm nsd publish"
] = """
    type: command
    short-summary: Publish a pre-built AOSM Network Service Design.
"""


helps[
    "aosm nfd delete"
] = """
    type: command
    short-summary: Delete AOSM Network Function Definition.
"""
