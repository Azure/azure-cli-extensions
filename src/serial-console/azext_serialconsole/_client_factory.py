# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def _compute_client_factory(cli_ctx, **kwargs):
    from azure.cli.core.profiles import ResourceType
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_COMPUTE,
                                   subscription_id=kwargs.get('subscription_id'),
                                   aux_subscriptions=kwargs.get('aux_subscriptions'))


def cf_serialconsole(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_serialconsole.vendored_sdks.serialconsole import MicrosoftSerialConsoleClient
    return get_mgmt_service_client(cli_ctx,
                                   MicrosoftSerialConsoleClient)


def cf_serial_port(cli_ctx, *_):
    return cf_serialconsole(cli_ctx).serial_ports
