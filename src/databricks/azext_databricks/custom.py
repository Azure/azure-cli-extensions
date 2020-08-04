# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument


from azure.cli.core.util import sdk_no_wait


def create_databricks_workspace(cmd, client,
                                resource_group_name,
                                workspace_name,
                                location,
                                sku_name,
                                managed_resource_group=None,
                                custom_virtual_network_id=None,
                                custom_public_subnet_name=None,
                                custom_private_subnet_name=None,
                                tags=None,
                                prepare_encryption=None,
                                require_infrastructure_encryption=None,
                                no_wait=False):
    body = {}
    body['tags'] = tags  # dictionary
    body['location'] = location  # str
    body['managed_resource_group_id'] = managed_resource_group  # str
    body.setdefault('sku', {})['name'] = sku_name  # str

    parameters = {}
    _set_parameter_value(parameters, 'custom_virtual_network_id', custom_virtual_network_id)  # str
    _set_parameter_value(parameters, 'custom_public_subnet_name', custom_public_subnet_name)  # str
    _set_parameter_value(parameters, 'custom_private_subnet_name', custom_private_subnet_name)  # str
    _set_parameter_value(parameters, 'prepare_encryption', prepare_encryption)
    _set_parameter_value(parameters, 'require_infrastructure_encryption', require_infrastructure_encryption)
    body['parameters'] = parameters

    return sdk_no_wait(no_wait, client.create_or_update,
                       resource_group_name=resource_group_name,
                       workspace_name=workspace_name,
                       parameters=body)


def _set_parameter_value(parameters, field, value):
    if value is not None:
        parameters.setdefault(field, {})['value'] = value


def update_databricks_workspace(cmd, client,  # pylint: disable=too-many-branches
                                resource_group_name,
                                workspace_name,
                                tags=None,
                                prepare_encryption=None,
                                encryption_key_source=None,
                                encryption_key_name=None,
                                encryption_key_version=None,
                                encryption_key_vault=None,
                                no_wait=False):
    body = client.get(resource_group_name=resource_group_name,
                      workspace_name=workspace_name).as_dict()
    parameters = body['parameters']
    if tags is not None:
        body['tags'] = tags
    if prepare_encryption is not None:
        _set_parameter_value(parameters, 'prepare_encryption', prepare_encryption)
    if encryption_key_source is not None:
        encryption = {}
        encryption['key_source'] = encryption_key_source
        if encryption_key_name is not None:
            encryption['key_name'] = encryption_key_name
        if encryption_key_version is not None:
            encryption['key_version'] = encryption_key_version
        if encryption_key_vault is not None:
            encryption['key_vault_uri'] = encryption_key_vault
        _set_parameter_value(parameters, 'encryption', encryption)

    return sdk_no_wait(no_wait, client.create_or_update,
                       resource_group_name=resource_group_name,
                       workspace_name=workspace_name,
                       parameters=body)


def delete_databricks_workspace(cmd, client, resource_group_name,
                                workspace_name,
                                no_wait=False):
    return sdk_no_wait(no_wait, client.delete,
                       resource_group_name=resource_group_name,
                       workspace_name=workspace_name)


def get_databricks_workspace(cmd, client, resource_group_name, workspace_name):
    return client.get(resource_group_name=resource_group_name,
                      workspace_name=workspace_name)


def list_databricks_workspace(cmd, client, resource_group_name=None):
    if not resource_group_name:
        return client.list_by_subscription()  # todo service 502
    return client.list_by_resource_group(resource_group_name=resource_group_name)


def create_databricks_vnet_peering(client, resource_group_name, workspace_name, peering_name,
                                   remote_virtual_network,
                                   allow_virtual_network_access=None,
                                   allow_forwarded_traffic=None,
                                   allow_gateway_transit=None,
                                   use_remote_gateways=None,
                                   no_wait=False):
    from .vendored_sdks.databricks.models._models_py3 import \
        VirtualNetworkPeering, VirtualNetworkPeeringPropertiesFormatRemoteVirtualNetwork

    peering = VirtualNetworkPeering(
        remote_virtual_network=VirtualNetworkPeeringPropertiesFormatRemoteVirtualNetwork(id=remote_virtual_network)
    )

    if allow_virtual_network_access is None:
        allow_virtual_network_access = True
    peering.allow_virtual_network_access = allow_virtual_network_access

    if allow_forwarded_traffic is not None:
        peering.allow_forwarded_traffic = allow_forwarded_traffic
    if allow_gateway_transit is not None:
        peering.allow_gateway_transit = allow_gateway_transit
    if use_remote_gateways is not None:
        peering.use_remote_gateways = use_remote_gateways

    return sdk_no_wait(no_wait, client.create_or_update,
                       virtual_network_peering_parameters=peering,
                       resource_group_name=resource_group_name,
                       workspace_name=workspace_name,
                       peering_name=peering_name)


def update_databricks_vnet_peering(client, resource_group_name, workspace_name, peering_name,
                                   allow_virtual_network_access=None,
                                   allow_forwarded_traffic=None,
                                   allow_gateway_transit=None,
                                   use_remote_gateways=None,
                                   no_wait=False):
    peering = client.get(
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
        peering_name=peering_name
    )

    if allow_virtual_network_access is not None:
        peering.allow_virtual_network_access = allow_virtual_network_access
    if allow_forwarded_traffic is not None:
        peering.allow_forwarded_traffic = allow_forwarded_traffic
    if allow_gateway_transit is not None:
        peering.allow_gateway_transit = allow_gateway_transit
    if use_remote_gateways is not None:
        peering.use_remote_gateways = use_remote_gateways

    return sdk_no_wait(no_wait, client.create_or_update,
                       virtual_network_peering_parameters=peering,
                       resource_group_name=resource_group_name,
                       workspace_name=workspace_name,
                       peering_name=peering_name)


def delete_databricks_vnet_peering(client, resource_group_name, workspace_name, peering_name, no_wait=False):
    return sdk_no_wait(no_wait, client.delete,
                       resource_group_name=resource_group_name,
                       workspace_name=workspace_name,
                       peering_name=peering_name)
