# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core import AzCli
# Client factory for vmware clients.
from .vendored_sdks.connectedvmware import AzureArcVMwareManagementServiceAPI
from .vendored_sdks.hybridcompute import HybridComputeManagementClient
from .vendored_sdks.resourcegraph import ResourceGraphClient


def cf_connectedvmware(cli_ctx: AzCli, *_) -> AzureArcVMwareManagementServiceAPI:
    return get_mgmt_service_client(cli_ctx, AzureArcVMwareManagementServiceAPI)


def cf_hybridcompute(cli_ctx: AzCli, *_) -> HybridComputeManagementClient:
    return get_mgmt_service_client(cli_ctx, HybridComputeManagementClient)


def cf_vcenter(cli_ctx: AzCli, *_):
    """
    Client factory for vcenters.
    """
    return cf_connectedvmware(cli_ctx).vcenters


def cf_resource_pool(cli_ctx: AzCli, *_):
    """
    Client factory for resourcepools.
    """
    return cf_connectedvmware(cli_ctx).resource_pools


def cf_cluster(cli_ctx: AzCli, *_):
    """
    Client factory for clusters.
    """
    return cf_connectedvmware(cli_ctx).clusters


def cf_datastore(cli_ctx: AzCli, *_):
    """
    Client factory for datastores.
    """
    return cf_connectedvmware(cli_ctx).datastores


def cf_host(cli_ctx: AzCli, *_):
    """
    Client factory for hosts.
    """
    return cf_connectedvmware(cli_ctx).hosts


def cf_virtual_network(cli_ctx: AzCli, *_):
    """
    Client factory for virtual networks.
    """
    return cf_connectedvmware(cli_ctx).virtual_networks


def cf_virtual_machine_template(cli_ctx: AzCli, *_):
    """
    Client factory for vm templates.
    """
    return cf_connectedvmware(cli_ctx).virtual_machine_templates


def cf_virtual_machine_instance(cli_ctx: AzCli, *_):
    """
    Client factory for virtual machine instances.
    """
    return cf_connectedvmware(cli_ctx).virtual_machine_instances


def cf_inventory_item(cli_ctx: AzCli, *_):
    """
    Client factory for inventory items.
    """
    return cf_connectedvmware(cli_ctx).inventory_items


def cf_vminstance_guest_agent(cli_ctx: AzCli, *_):
    """
    Client factory for guest agent.
    """
    return cf_connectedvmware(cli_ctx).vm_instance_guest_agents


def cf_machine(cli_ctx: AzCli, *_):
    """
    Client factory for machines.
    """
    return cf_hybridcompute(cli_ctx).machines


def cf_machine_extension(cli_ctx: AzCli, *_):
    """
    Client factory for machines.
    """
    return cf_hybridcompute(cli_ctx).machine_extensions


def cf_resource_graph(cli_ctx: AzCli, *_) -> ResourceGraphClient:
    """
    Client factory for resource graph.
    """
    # NOTE 1: Adding base_url_bound=False to avoid the following error
    # TypeError: __init__() got multiple values for argument 'base_url'
    # NOTE 2: Hardcoding subscription_bound=False to avoid the following error
    # Bearer token authentication is not permitted for non-TLS protected (non-https) URLs.
    return get_mgmt_service_client(
        cli_ctx,
        ResourceGraphClient,
        subscription_bound=False,
        base_url_bound=False,
    )
