# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['durabletask'] = """
    type: group
    short-summary: Commands to manage Durabletasks.
"""

helps['durabletask namespace'] = """
    type: group
    short-summary: Commands to manage Durabletask namespaces.
"""

helps['durabletask namespace create'] = """
    type: command
    short-summary: Create a Durabletask namespace.
"""

helps['durabletask namespace list'] = """
    type: command
    short-summary: List Durabletasks namespaces.
"""

helps['durabletask namespace show'] = """
    type: command
    short-summary: Show details of a Durabletask namespace.
"""

helps['durabletask namespace delete'] = """
    type: command
    short-summary: Delete a Durabletask namespace.
"""


helps['durabletask taskhub'] = """
    type: group
    short-summary: Commands to manage Durabletask taskhubs.
"""

helps['durabletask taskhub create'] = """
    type: command
    short-summary: Create a Durabletask taskhub.
"""

helps['durabletask taskhub delete'] = """
    type: command
    short-summary: Delete a Durabletask taskhub.
"""

helps['durabletask taskhub list'] = """
    type: command
    short-summary: List Durabletasks taskhubs.
"""

helps['durabletask taskhub show'] = """
    type: command
    short-summary: Show details of a Durabletask taskhub.
"""
