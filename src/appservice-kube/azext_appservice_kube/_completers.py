# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.decorators import Completer
from ._utils import _get_location_from_resource_group
from ._constants import KUBE_DEFAULT_SKU


@Completer
def get_vm_size_completion_list(cmd, prefix, namespace):    # pylint: disable=unused-argument
    """Return the intersection of the VM sizes allowed by the ACS SDK with those returned by the Compute Service."""
    from azure.mgmt.containerservice.models import ContainerServiceVMSizeTypes

    location = _get_location(cmd.cli_ctx, namespace)
    result = get_vm_sizes(cmd.cli_ctx, location)
    return set(r.name for r in result) & set(c.value for c in ContainerServiceVMSizeTypes)


@Completer
def get_kube_sku_completion_list(cmd, prefix, namespace):   # pylint: disable=unused-argument
    """
    Return the VM sizes allowed by AKS, or 'ANY'
    """
    return get_vm_size_completion_list(cmd, prefix, namespace) & set(KUBE_DEFAULT_SKU)


def get_vm_sizes(cli_ctx, location):
    from ._client_factory import cf_compute_service
    return cf_compute_service(cli_ctx).virtual_machine_sizes.list(location)


def _get_location(cli_ctx, namespace):
    """
    Return an Azure location by using an explicit `--location` argument, then by `--resource-group`, and
    finally by the subscription if neither argument was provided.
    """
    from azure.core.exceptions import HttpResponseError
    from azure.cli.core.commands.parameters import get_one_of_subscription_locations

    location = None
    if getattr(namespace, 'location', None):
        location = namespace.location
    elif getattr(namespace, 'resource_group_name', None):
        try:
            location = _get_location_from_resource_group(cli_ctx, namespace.resource_group_name)
        except HttpResponseError as err:
            from argcomplete import warn
            warn(f'Warning: {err.message}')
    if not location:
        location = get_one_of_subscription_locations(cli_ctx)
    return location
