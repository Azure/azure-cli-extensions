# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.breaking_change import register_command_group_deprecate

# https://aka.ms/asaretirement
register_command_group_deprecate('spring', target_version='Mar 2028')
