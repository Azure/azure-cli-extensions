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

helps[f'{consts.EXTENSION_NAME} extension'] = """
    type: group
    short-summary: Commands to manage Video Indexer Extension.
"""

helps[f'{consts.EXTENSION_NAME} extension show'] = f"""
    type: command
    short-summary: Show Video Indexer Extension details.
    long-summary: Show Video Indexer Extension details including its properties.
    examples:
      - name: Show Video Indexer Extension details
        text: |-
          az {consts.EXTENSION_NAME} extension show --resource-group my-resource-group \
          --connected-cluster mycluster
"""

helps[f'{consts.EXTENSION_NAME} extension troubleshoot'] = f"""
    type: command
    short-summary: Perform diagnostic checks on a Video Indexer Extension.
    long-summary: This command is used to troubleshoot a Video Indexer Extension. It \
collects logs and other information that can be used to diagnose issues with the extension.
    examples:
      - name: Troubleshoot a Video Indexer Extension
        text: |-
          az {consts.EXTENSION_NAME} extension troubleshoot --resource-group my-resource-group \
          --connected-cluster mycluster
"""

helps[f'{consts.EXTENSION_NAME} camera'] = """
    type: group
    short-summary: Commands to manage Video Indexer cameras.
"""

helps[f'{consts.EXTENSION_NAME} camera add'] = f"""
    type: command
    short-summary: Add a camera to a Video Indexer Extension.
    long-summary: Add a camera to a Video Indexer Extension on a connected cluster. This command registers a camera with the extension, allowing it to be used for video indexing.
    examples:
      - name: Add a camera to a Video Indexer Extension
        text: |-
          az {consts.EXTENSION_NAME} camera add --resource-group my-resource-group \
          --connected-cluster mycluster --camera-name mycamera --rtsp-url rtsp://my-url
"""

helps[f'{consts.EXTENSION_NAME} camera list'] = f"""
    type: command
    short-summary: List all cameras associated with a Video Indexer Extension.
    long-summary: List all cameras associated with a Video Indexer Extension on a connected cluster.
    examples:
      - name: List all cameras for a Video Indexer Extension
        text: |-
          az {consts.EXTENSION_NAME} camera list --resource-group my-resource-group \
          --connected-cluster mycluster
"""
