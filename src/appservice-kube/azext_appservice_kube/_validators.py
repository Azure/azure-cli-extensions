# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from ._client_factory import web_client_factory
from ._utils import _normalize_sku, _validate_asp_sku
from ._constants import KUBE_DEFAULT_SKU


def validate_asp_sku(cmd, namespace):
    import json
    client = web_client_factory(cmd.cli_ctx)
    serverfarm = namespace.name
    resource_group_name = namespace.resource_group_name
    asp = client.app_service_plans.get(resource_group_name, serverfarm, None, raw=True)
    if asp.response.status_code != 200:
        raise CLIError(asp.response.text)
    # convert byte array to json
    output_str = asp.response.content.decode('utf8')
    res = json.loads(output_str)

    # Isolated SKU is supported only for ASE
    if namespace.sku in ['I1', 'I2', 'I3']:
        if res.get('properties').get('hostingEnvironment') is None:
            raise CLIError("The pricing tier 'Isolated' is not allowed for this app service plan. Use this link to "
                           "learn more: https://docs.microsoft.com/en-us/azure/app-service/overview-hosting-plans")
    else:
        if res.get('properties').get('hostingEnvironment') is not None:
            raise CLIError("Only pricing tier 'Isolated' is allowed in this app service plan. Use this link to "
                           "learn more: https://docs.microsoft.com/en-us/azure/app-service/overview-hosting-plans")


def validate_asp_create(cmd, namespace):
    """Validate the SiteName that is being used to create is available
    This API requires that the RG is already created"""

    # need to validate SKU before the general ASP create validation
    sku = namespace.sku
    if not sku:
        sku = 'B1' if not namespace.custom_location else KUBE_DEFAULT_SKU
    sku = _normalize_sku(sku)
    _validate_asp_sku(namespace.app_service_environment, namespace.custom_location, sku)

    client = web_client_factory(cmd.cli_ctx)
    if isinstance(namespace.name, str) and isinstance(namespace.resource_group_name, str):
        resource_group_name = namespace.resource_group_name
        if isinstance(namespace.location, str):
            location = namespace.location
        else:
            from azure.cli.core.profiles import ResourceType
            rg_client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)

            group = rg_client.resource_groups.get(resource_group_name)
            location = group.location
        validation_payload = {
            "name": namespace.name,
            "type": "Microsoft.Web/serverfarms",
            "location": location,
            "properties": {
                "skuName": sku,
                "capacity": namespace.number_of_workers or 1,
                "needLinuxWorkers": namespace.is_linux if namespace.custom_location is None else 'false',
                "isXenon": namespace.hyper_v
            }
        }
        validation = client.validate(resource_group_name, validation_payload)
        if validation.status.lower() == "failure" and validation.error.code != 'ServerFarmAlreadyExists':
            raise CLIError(validation.error.message)


def validate_nodes_count(namespace):
    """Validates that node_count and max_count is set between 1-100"""
    if namespace.node_count is not None:
        if namespace.node_count < 1 or namespace.node_count > 100:
            raise CLIError('--node-count must be in the range [1,100]')
    if namespace.max_count is not None:
        if namespace.max_count < 1 or namespace.max_count > 100:
            raise CLIError('--max-count must be in the range [1,100]')


def validate_nodepool_name(namespace):
    """Validates a nodepool name to be at most 12 characters, alphanumeric only."""
    if namespace.nodepool_name != "":
        if len(namespace.nodepool_name) > 12:
            raise CLIError('--nodepool-name can contain at most 12 characters')
        if not namespace.nodepool_name.isalnum():
            raise CLIError('--nodepool-name should contain only alphanumeric characters')


def validate_app_or_slot_exists_in_rg(cmd, namespace):
    """Validate that the App/slot exists in the RG provided"""
    client = web_client_factory(cmd.cli_ctx)
    webapp = namespace.name
    resource_group_name = namespace.resource_group_name
    if isinstance(namespace.slot, str):
        app = client.web_apps.get_slot(resource_group_name, webapp, namespace.slot, raw=True)
    else:
        app = client.web_apps.get(resource_group_name, webapp, None, raw=True)
    if app.response.status_code != 200:
        raise CLIError(app.response.text)


def validate_timeout_value(namespace):
    """Validates that zip deployment timeout is set to a reasonable min value"""
    if isinstance(namespace.timeout, int):
        if namespace.timeout <= 29:
            raise CLIError('--timeout value should be a positive value in seconds and should be at least 30')
