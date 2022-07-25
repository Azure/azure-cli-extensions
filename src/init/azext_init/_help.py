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
The Azure CLI offers `az init` to help you set global configurations through an interactive format.  Global settings are grouped into bundles that help you optimize your settings for scenarios such as "interaction" or "automation".  It also supports a walk-through experience to help you get familiar with the common configurations and customize them one by one.

The purpose of `az init` is not to replace the `az config` command, but to simplify the setting of configurations by offering an interactive question-answer experience.  While both `az init` and `az config` modify the same configuration file, `az init` is designed to only set the most common configurations.  For more granular control of all available configurations, use `az config`.  For more information on configuring your Azure CLI environment, see https://docs.microsoft.com/en-us/cli/azure/azure-cli-configuration.
        az init can help you quickly understand and set up global configurations that are suitable for your current usage environment:
        It supports setting bundles for interactive and automation scenarios to help you quickly set the recommended configurations.
        It also supports a walk-through experience to help you get familiar with the common configurations and customize them one by one.

        The purpose of "az init" is not to replace the "az config" command, but to simplify common configurations by supporting setting bundles.
        While "az init" and "az config" modify the same configuration file, "az init" is aimed at an interactive, standardized approach to managing your configuration and "az config" is better at more granular control and setting configurations in automation scenarios.
"""
