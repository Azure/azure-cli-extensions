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
    short-summary: If Resource Group is specified, then list Spatial Anchors Accounts in it. Othewise, list Spatial Anchors Accounts in current Subscription.
"""

helps['spatial-anchors-account create'] = """
    type: command
    short-summary: Creating a Spatial Anchors Account.
"""

helps['spatial-anchors-account show'] = """
    type: command
    short-summary: Retrieve a Spatial Anchors Account.
"""

helps['spatial-anchors-account delete'] = """
    type: command
    short-summary: Delete a Spatial Anchors Account.
"""

helps['spatial-anchors-account key'] = """
    type: group
    short-summary: Manage developer keys of a Spatial Anchors Account.'
"""

helps['spatial-anchors-account keys list'] = """
    type: command
    short-summary: Get both of the two developer keys of a Spatial Anchors Account.
"""

helps['spatial-anchors-account key renew'] = """
    type: command
    short-summary: Regenerate a developer keys of a Spatial Anchors Account.
"""
