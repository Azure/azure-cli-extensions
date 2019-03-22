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
    examples:
        - name: List all Spatial Anchors Accounts in Resource Group 'example'.
          text: az spatial-anchors-account list -g example
        - name: List all Spatial Anchors Accounts in current Subscription.
          text: az spatial-anchors-account list
"""

helps['spatial-anchors-account create'] = """
    type: command
    short-summary: Create a Spatial Anchors Account.
    examples:
        - name: Create a Spatial Anchors Account.
          text: az spatial-anchors-account create -g example -n example -l eastus2
        - name: Create a Spatial Anchors Account without Location specified.
          text: az spatial-anchors-account create -g example -n example
"""

helps['spatial-anchors-account show'] = """
    type: command
    short-summary: Show a Spatial Anchors Account.
    examples:
        - name: Show properties of a Spatial Anchors Account.
          text: az spatial-anchors-account show -g example -n example
"""

helps['spatial-anchors-account delete'] = """
    type: command
    short-summary: Delete a Spatial Anchors Account.
    examples:
        - name: Delete of a Spatial Anchors Account.
          text: az spatial-anchors-account delete -g example -n example
"""

helps['spatial-anchors-account key'] = """
    type: group
    short-summary: Manage developer keys of a Spatial Anchors Account.
"""

helps['spatial-anchors-account key show'] = """
    type: command
    short-summary: Show keys of a Spatial Anchors Account.
    examples:
        - name: Show primary key and secondary key of a Spatial Anchors Account.
          text: az spatial-anchors-account key show -g example -n example
"""

helps['spatial-anchors-account key renew'] = """
    type: command
    short-summary: Renew one of the keys of a Spatial Anchors Account.
    examples:
        - name: Renew primary key of a Spatial Anchors Account.
          text: az spatial-anchors-account key renew -g example -n example -k primary
        - name: Renew secondary key of a Spatial Anchors Account.
          text: az spatial-anchors-account key renew -g example -n example -k secondary
"""
