# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_support(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_support.vendored_sdks import MicrosoftSupport
    return get_mgmt_service_client(cli_ctx, MicrosoftSupport)


def cf_services(cli_ctx, *_):
    return cf_support(cli_ctx).services


def cf_problem_classifications(cli_ctx, *_):
    return cf_support(cli_ctx).problem_classifications


def cf_support_tickets(cli_ctx, *_):
    return cf_support(cli_ctx).support_tickets


def cf_communications(cli_ctx, *_):
    return cf_support(cli_ctx).communications


def cf_resource(cli_ctx, **_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.cli.core.profiles import ResourceType
    return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)
