# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.profiles import ResourceType
from azure.cli.core.azclierror import CLIInternalError

def cf_vi(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_vi.vendored_sdks import VIManagementClient
    return get_mgmt_service_client(cli_ctx, VIManagementClient)


def cf_vi_extensions(cli_ctx, *_):
    return cf_vi(cli_ctx).extensions


def cf_vi_cameras(cli_ctx, *_):
    return cf_vi(cli_ctx).cameras