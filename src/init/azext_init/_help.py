# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['init'] = """
    type: command
    short-summary: It's an effortless setting up tool for configs.
    long-summary: |
        This tool can help you quickly know and set up global configurations that are suitable for your current usage environment:
        It supports setting bundles for interactive mode and automatic mode to help you quickly set the recommended configurations.
        It also supports walk through style to help you get familiar with the common configurations and customize them one by one.

        In addition, it's purpose is not to replace the "az config" command, but to reduce the common repeated configuration behaviors by supporting setting bindles.
        The configuration set by "az init" can also be modified by "az config", because they modify the same configuration file.
"""
