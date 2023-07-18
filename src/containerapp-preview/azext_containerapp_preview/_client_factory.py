# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType
from ._utils import (_get_azext_containerapp_module)


def handle_raw_exception(e):
    azext_client_factory = _get_azext_containerapp_module("azext_containerapp._client_factory")
    return azext_client_factory.handle_raw_exception(e)


def providers_client_factory(cli_ctx, subscription_id=None):
    return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES, subscription_id=subscription_id).providers


def customlocation_client_factory(cli_ctx, api_version=None, subscription_id=None, **_):
    from azure.cli.core.profiles import ResourceType
    from azure.cli.core.commands.client_factory import get_mgmt_service_client

    return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_CUSTOMLOCATION, api_version=api_version,
                                   subscription_id=subscription_id).custom_locations


def k8s_extension_client_factory(cli_ctx, subscription_id=None):
    from azure.mgmt.kubernetesconfiguration import SourceControlConfigurationClient

    r = get_mgmt_service_client(cli_ctx, SourceControlConfigurationClient, subscription_id=subscription_id)
    return r.extensions