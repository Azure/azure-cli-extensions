# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.breaking_change import register_command_group_deprecate, register_argument_deprecate

register_command_group_deprecate('networkfabric fabric identity', hide=True)
register_argument_deprecate('networkfabric l3domain create', '--route-prefix-limit', target_version='9.0.x')
register_argument_deprecate('networkfabric l3domain update', '--route-prefix-limit', target_version='9.0.x')