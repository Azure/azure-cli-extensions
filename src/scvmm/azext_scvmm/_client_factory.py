# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.client_factory import get_mgmt_service_client
from .vendored_sdks import SCVMM


def cf_scvmm(cli_ctx, *_) -> SCVMM:
    """
    Client factory for scvmm clients.
    """
    return get_mgmt_service_client(cli_ctx, SCVMM)


def cf_vmmserver(cli_ctx, *_):
    """
    Client factory for vmmservers.
    """
    return cf_scvmm(cli_ctx).vmm_servers


def cf_cloud(cli_ctx, *_):
    """
    Client factory for clouds.
    """
    return cf_scvmm(cli_ctx).clouds


def cf_virtual_network(cli_ctx, *_):
    """
    Client factory for virtual networks.
    """
    return cf_scvmm(cli_ctx).virtual_networks


def cf_virtual_machine_template(cli_ctx, *_):
    """
    Client factory for vm templates.
    """
    return cf_scvmm(cli_ctx).virtual_machine_templates


def cf_virtual_machine(cli_ctx, *_):
    """
    Client factory for virtual machines.
    """
    return cf_scvmm(cli_ctx).virtual_machines


def cf_availability_sets(cli_ctx, *_):
    """
    Client factory for availability sets.
    """
    return cf_scvmm(cli_ctx).availability_sets


def cf_inventory_items(cli_ctx, *_):
    """
    Client factory for inventory items.
    """
    return cf_scvmm(cli_ctx).inventory_items
