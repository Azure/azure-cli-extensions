# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.profiles import register_resource_type
from azext_vwan.profiles import CUSTOM_VHUB_ROUTE_TABLE, CUSTOM_VWAN

register_resource_type('latest', CUSTOM_VWAN, '2018-08-01')
register_resource_type('latest', CUSTOM_VHUB_ROUTE_TABLE, '2019-09-01')