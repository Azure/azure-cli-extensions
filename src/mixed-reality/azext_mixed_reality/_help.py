# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['spatial-anchors-account'] = """
    type: group
    short-summary: Manage Spatial Anchors Accounts.
"""

helps['spatial-anchors-account list'] = """
    type: command
    short-summary: List Spatial Anchors Accounts.
    long-summary: If Resource Group is specified, then list Spatial Anchors Accounts in it. Othewise, list Spatial Anchors Accounts in current Subscription.
"""

helps['spatial-anchors-account create'] = """
    type: command
    short-summary: Create a Spatial Anchors Account.
"""

helps['spatial-anchors-account show'] = """
    type: command
    short-summary: Get a Spatial Anchors Account.
"""

helps['spatial-anchors-account delete'] = """
    type: command
    short-summary: Delete a Spatial Anchors Account.
"""

helps['spatial-anchors-account key'] = """
    type: group
    short-summary: Manage developer keys of a Spatial Anchors Account.
"""

helps['spatial-anchors-account key show'] = """
    type: command
    short-summary: Get Spatial Anchors Accounts Keys.
    long-summary: Get both the primary and the secondary developer keys of a Spatial Anchors Account.
"""

helps['spatial-anchors-account key renew'] = """
    type: command
    short-summary: Renew a Spatial Anchors Accounts Key.
    long-summary: Regenerate either the primary or the secondary developer keys of a Spatial Anchors Account.
"""
