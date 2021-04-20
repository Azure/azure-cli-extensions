# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import
import azext_k8s_extension._consts as consts


helps[f'{consts.EXTENSION_NAME}'] = """
    type: group
    short-summary: Commands to manage K8s-extensions.
"""

helps[f'{consts.EXTENSION_NAME} create'] = """
    type: command
    short-summary: Create a K8s-extension.
"""

helps[f'{consts.EXTENSION_NAME} list'] = """
    type: command
    short-summary: List K8s-extensions.
"""

helps[f'{consts.EXTENSION_NAME} delete'] = """
    type: command
    short-summary: Delete a K8s-extension.
"""

helps[f'{consts.EXTENSION_NAME} show'] = """
    type: command
    short-summary: Show details of a K8s-extension.
"""
