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
    short-summary: Creates or updates a Fleet.
    parameters:
        - name: --tags
          type: string
          short-summary: The tags of the managed cluster. The managed cluster instance and all resources managed by the cloud provider will be tagged.
        - name: --dns-name-prefix -p
          type: string
          short-summary: Prefix for hostnames that are created. If not specified, generate a hostname using the
                         managed cluster and resource group names.
"""

helps['fleet update'] = """
    type: command
    short-summary: Patches a fleet resource.
    parameters:
        - name: --tags
          type: string
          short-summary: The tags of the managed cluster. The managed cluster instance and all resources managed by the cloud provider will be tagged.
"""

helps['fleet show'] = """
    type: command
    short-summary: Gets a Fleet.
"""

helps['fleet list'] = """
    type: command
    short-summary: Lists fleets in the specified subscription and resource group.
"""

helps['fleet delete'] = """
    type: command
    short-summary: Deletes a Fleet.
"""

helps['fleet get-credentials'] = """
    type: command
    short-summary: Lists the user credentials of a Fleet.
    parameters:
    - name: --overwrite-existing
      type: bool
      short-summary: Overwrite any existing cluster entry with the same name.
    - name: --file -f
      type: string
      short-summary: Kubernetes configuration file to update. Use "-" to print YAML to stdout instead.
"""

helps['fleet wait'] = """
type: command
short-summary: Wait for a fleet resouce to reach a desired state.
long-summary: If an operation on fleet was interrupted or was started with `--no-wait`, use this command to wait for it to complete.
"""

helps['fleet member'] = """
    type: group
    short-summary: Commands to manage a fleet member.
"""

helps['fleet member create'] = """
    type: command
    short-summary: Creates or updates a fleet member.
    parameters:
        - name: --member-cluster-id
          type: string
          short-summary: ID of the managed cluster.
"""

helps['fleet member list'] = """
    type: command
    short-summary: Lists the members of a fleet.
"""

helps['fleet member show'] = """
    type: command
    short-summary: Gets a Fleet member.
"""

helps['fleet member delete'] = """
    type: command
    short-summary: Deletes a fleet member.
"""

helps['fleet member wait'] = """
type: command
short-summary: Wait for a fleet member resouce to reach a desired state.
long-summary: If an operation on fleet member was interrupted or was started with `--no-wait`, use this command to wait for it to complete.
"""
