# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core.breaking_change import (register_required_flag_breaking_change,
                                            register_default_value_breaking_change)

register_required_flag_breaking_change('redisenterprise create', '--public-network-access')
register_default_value_breaking_change('redisenterprise create', '--access-keys-auth', 'Enabled', 'Disabled')
