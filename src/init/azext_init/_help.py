# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['init'] = """
type: command
short-summary: Set Azure CLI global configurations by selecting a bundle or responding to questions with walk-through
long-summary: |
    The Azure CLI offers `az init` to help you quickly understand and set global configurations that are suitable for your usage environment:
    Global settings are grouped into bundles that help you optimize your settings for scenarios such as "interaction" or "automation". So it supports setting bundles for interactive and automation scenarios to help you quickly set up the recommended configurations.
    It also supports a walk-through experience to help you get familiar with the common configurations and customize them one by one.

    The purpose of `az init` is not to replace the `az config` command, but to simplify the setting of configurations by offering an interactive question-answer experience.
    While both `az init` and `az config` modify the same configuration file, `az init` is aimed at an interactive, standardized approach to managing your configuration and designed to only set the most common configurations.
    For more granular control of all available configurations, please use `az config`.
    For more information on configuring your Azure CLI environment, please see https://docs.microsoft.com/en-us/cli/azure/azure-cli-configuration.
"""
