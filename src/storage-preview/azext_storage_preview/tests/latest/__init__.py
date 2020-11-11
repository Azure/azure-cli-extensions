# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.profiles import register_resource_type
from ...profiles import CUSTOM_MGMT_PREVIEW_STORAGE
register_resource_type('latest', CUSTOM_MGMT_PREVIEW_STORAGE, '2020-08-01-preview')
