# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_portal(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from ..vendored_sdks.portal import Portal
    return get_mgmt_service_client(cli_ctx, Portal)


def cf_dashboard(cli_ctx, *_):
    return cf_portal(cli_ctx).dashboard
