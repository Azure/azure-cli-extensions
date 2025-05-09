# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['nexusidentity'] = """
    type: group
    short-summary: Command to manage Nexusidentity keys.
"""

helps['nexusidentity gen-keys'] = """
    type: command
    short-summary: Generate Nexusidentity keys.
    parameters:
        - name: --algorithm
          short-summary: Algorithm to use for generating keys. It can either be ecdsa-sk or ed25519-sk
"""
