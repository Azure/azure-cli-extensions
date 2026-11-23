# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.breaking_change import register_command_group_deprecate


register_command_group_deprecate('fleet clustermeshprofile',
                                 redirect='fleet network cross-cluster',
                                 target_version='a future release')
