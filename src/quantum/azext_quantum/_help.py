# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

helps['quantum'] = """
    type: group
    short-summary: Manage Azure Quantum Workspaces and submit jobs to Azure Quantum Providers.
"""

helps['quantum job'] = """
type: group
short-summary: Manage jobs for Azure Quantum.
"""

helps['quantum target'] = """
type: group
short-summary: Manage execution targets for Azure Quantum workspaces.
"""

helps['quantum workspace'] = """
type: group
short-summary: Manage Azure Quantum workspaces.
"""
