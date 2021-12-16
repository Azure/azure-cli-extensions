# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.client_factory import get_mgmt_service_client
# Client factory for vmware clients.
from .vendored_sdks import AzureArcVMwareManagementServiceAPI


def cf_connectedvmware(cli_ctx, *_):
    return get_mgmt_service_client(cli_ctx, AzureArcVMwareManagementServiceAPI)


def cf_vcenter(cli_ctx, *_):
    """
    Client factory for vcenters.
    """
    return cf_connectedvmware(cli_ctx).vcenters


def cf_resource_pool(cli_ctx, *_):
    """
    Client factory for resourcepools.
    """
    return cf_connectedvmware(cli_ctx).resource_pools


def cf_cluster(cli_ctx, *_):
    """
    Client factory for clusters.
    """
    return cf_connectedvmware(cli_ctx).clusters


def cf_datastore(cli_ctx, *_):
    """
    Client factory for datastores.
    """
    return cf_connectedvmware(cli_ctx).datastores


def cf_host(cli_ctx, *_):
    """
    Client factory for hosts.
    """
    return cf_connectedvmware(cli_ctx).hosts


def cf_virtual_network(cli_ctx, *_):
    """
    Client factory for virtual networks.
    """
    return cf_connectedvmware(cli_ctx).virtual_networks


def cf_virtual_machine_template(cli_ctx, *_):
    """
    Client factory for vm templates.
    """
    return cf_connectedvmware(cli_ctx).virtual_machine_templates


def cf_virtual_machine(cli_ctx, *_):
    """
    Client factory for virtual machines.
    """
    return cf_connectedvmware(cli_ctx).virtual_machines


def cf_inventory_item(cli_ctx, *_):
    """
    Client factory for inventory items.
    """
    return cf_connectedvmware(cli_ctx).inventory_items


def cf_guest_agent(cli_ctx, *_):
    """
    Client factory for guest agent.
    """
    return cf_connectedvmware(cli_ctx).guest_agent
