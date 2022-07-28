# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['fleet'] = """
    type: group
    short-summary: Commands to manage fleet.
"""

helps['fleet create'] = """
    type: command
    short-summary: Create a new fleet.
    parameters:
        - name: --tags
          type: string
          short-summary: (TODO)The tags of the managed cluster. The managed cluster instance and all resources managed by the cloud provider will be tagged.
        - name: --dns-name-prefix -p
          type: string
          short-summary: (TODO)Prefix for hostnames that are created. If not specified, generate a hostname using the
                         managed cluster and resource group names.

"""

helps['fleet delete'] = """
    type: command
    short-summary: Delete an existing fleet.
"""

helps['fleet member'] = """
    type: group
    short-summary: Commands to manage a fleet member.
"""

helps['fleet member join'] = """
    type: command
    short-summary: Join member cluster to a fleet.
    parameters:
        - name: --member-cluster-id
          type: string
          short-summary: Name or ID of the managed cluster.
"""

helps['fleet member list'] = """
    type: command
    short-summary: List member cluster(s) of a fleet.
"""

helps['fleet member remove'] = """
    type: command
    short-summary: Remove member cluster from a fleet
"""
