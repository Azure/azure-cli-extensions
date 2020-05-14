# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------\
from azure.cli.core.profiles import register_resource_type
from ...profiles import CUSTOM_MGMT_STORAGE_ORS
register_resource_type('latest', CUSTOM_MGMT_STORAGE_ORS, '2019-06-01')
