# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from msrestazure.tools import parse_resource_id

from knack.util import CLIError

from azure.cli.core.commands.validators import get_default_location_from_resource_group, validate_tags
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType


def process_grafana_create_namespace(cmd, namespace):
    validate_tags(namespace)
    if not namespace.location:
        get_default_location_from_resource_group(cmd, namespace)


def process_missing_resource_group_parameter(cmd, namespace):
    if not namespace.resource_group_name and namespace.grafana_name:
        client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)
        resources = client.resources.list(filter="resourceType eq 'Microsoft.Dashboard/grafana'")
        resources = list(resources)
        match = next((i for i in resources if i.name == namespace.grafana_name), None)
        if match:
            namespace.resource_group_name = parse_resource_id(match.id)["resource_group"]
        else:
            raise CLIError((f"Not able to find the Grafana instance: '{namespace.grafana_name}'. Please "
                            f"correct the name, or provide resource group name, or set CLI "
                            f"subscription the workspace belongs to"))
