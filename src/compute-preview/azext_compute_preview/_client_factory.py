# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# def cf_compute-preview(cli_ctx, *_):
#
#     from azure.cli.core.commands.client_factory import get_mgmt_service_client
#     # TODO: Replace CONTOSO with the appropriate label and uncomment
#     # from azure.mgmt.CONTOSO import CONTOSOManagementClient
#     # return get_mgmt_service_client(cli_ctx, CONTOSOManagementClient)
#     return None

from azure.cli.core.profiles import (CustomResourceType, ResourceType)
from azure.cli.core.commands.client_factory import get_mgmt_service_client

CUSTOM_MGMT_COMPUTE = CustomResourceType('azext_compute_preview.vendored_sdks.v2019_12', 'ComputeManagementClient')


def _compute_client_factory(cli_ctx, **kwargs):
    return get_mgmt_service_client(cli_ctx, CUSTOM_MGMT_COMPUTE,
                                   subscription_id=kwargs.get('subscription_id'),
                                   aux_subscriptions=kwargs.get('aux_subscriptions'))


def cf_shared_vm_extensions(cli_ctx, _):
    return _compute_client_factory(cli_ctx).shared_vm_extensions


def cf_shared_vm_extension_versions(cli_ctx, _):
    return _compute_client_factory(cli_ctx).shared_vm_extension_versions
