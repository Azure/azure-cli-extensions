# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import
from . import consts

helps[f'{consts.EXTENSION_NAME}'] = """
    type: group
    short-summary: Commands to manage Video Indexer for Cloud and Edge.
"""

helps[f'{consts.EXTENSION_NAME} extension'] = f"""
    type: group
    short-summary: Show Video Indexer Extension details.
"""

helps[f'{consts.EXTENSION_NAME} extension show'] = f"""
    type: command
    short-summary: Show Video Indexer Extension details.
    long-summary: Show Video Indexer Extension details.
    examples:
      - name: Show Video Indexer Extension details
        text: |-
          az {consts.EXTENSION_NAME} extension show --resource-group my-resource-group \
--connected-cluster mycluster
"""

helps[f'{consts.EXTENSION_NAME} extension troubleshoot'] = f"""
    type: command
    short-summary: List Vis.
"""

helps[f'{consts.EXTENSION_NAME} camera'] = f"""
    type: group
    short-summary: Create a Kubernetes
"""

helps[f'{consts.EXTENSION_NAME} camera list'] = f"""
    type: command
    short-summary: Create a Kubernetes Cluster
    long-summary: Show Video Indexer Extension details.
    examples:
      - name: Show Video Indexer Extension details
        text: |-
          az {consts.EXTENSION_NAME} camera list --resource-group my-resource-group \
--connected-cluster mycluster
"""