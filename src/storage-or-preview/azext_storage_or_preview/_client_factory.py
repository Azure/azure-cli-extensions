# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.client_factory import get_mgmt_service_client

from .profiles import CUSTOM_MGMT_STORAGE_ORS


def storage_client_factory(cli_ctx, **_):
    return get_mgmt_service_client(cli_ctx, CUSTOM_MGMT_STORAGE_ORS)


def cf_sa(cli_ctx, _):
    return storage_client_factory(cli_ctx).storage_accounts


def cf_or_policy(cli_ctx, _):
    return storage_client_factory(cli_ctx).object_replication_policies
