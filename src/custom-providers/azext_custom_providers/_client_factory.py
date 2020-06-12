# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_custom_providers(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.customproviders import CustomProvidersClient
    return get_mgmt_service_client(cli_ctx, CustomProvidersClient)


def cf_custom_resource_provider(cli_ctx, *_):
    return cf_custom_providers(cli_ctx).custom_resource_provider
