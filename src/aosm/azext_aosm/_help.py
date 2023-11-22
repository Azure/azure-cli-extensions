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
    "aosm onboard"
] = """
    type: group
    short-summary: Commands to aid onboarding network functions and network services to AOSM.
"""

helps[
    "aosm onboard nfd"
] = """
    type: group
    short-summary: Manage AOSM publisher Network Function Definitions.
"""

helps[
    "aosm onboard nfd generate-config"
] = """
    type: command
    short-summary: Generate configuration file for building an AOSM publisher Network Function Definition.
"""

helps[
    "aosm onboard nfd build"
] = """
    type: command
    short-summary: Build an AOSM Network Function Definition.
"""

helps[
    "aosm onboard nfd publish"
] = """
    type: command
    short-summary: Publish a pre-built AOSM Network Function definition.
"""


helps[
    "aosm onboard nfd delete"
] = """
    type: command
    short-summary: Delete AOSM Network Function Definition.
"""

helps[
    "aosm onboard nsd"
] = """
    type: group
    short-summary: Manage AOSM publisher Network Service Designs.
"""

helps[
    "aosm onboard nsd generate-config"
] = """
    type: command
    short-summary: Generate configuration file for building an AOSM publisher Network Service Design.
"""

helps[
    "aosm onboard nsd build"
] = """
    type: command
    short-summary: Build an AOSM Network Service Design.
"""

helps[
    "aosm onboard nsd publish"
] = """
    type: command
    short-summary: Publish a pre-built AOSM Network Service Design.
"""


helps[
    "aosm onboard nfd delete"
] = """
    type: command
    short-summary: Delete AOSM Network Function Definition.
"""
