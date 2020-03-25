# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from enum import Enum


class IncludeOptionsEnum(str, Enum):
    none = "none"
    display_names = "displayNames"


class ResourceGraphTablesEnum(str, Enum):
    advisor_resources = 'advisorresources'
    alerts_management_resources = 'alertsmanagementresources'
    maintenance_resources = 'maintenanceresources'
    resources = 'resources'
    resource_containers = 'resourcecontainers'
    security_resources = 'securityresources'
