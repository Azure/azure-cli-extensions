# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.profiles import register_resource_type
from azext_firewall.profiles import CUSTOM_FIREWALL
register_resource_type('latest', CUSTOM_FIREWALL, '2018-08-01')
