# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType

# pylint: disable=import-outside-toplevel

RM_URI_OVERRIDE = 'AZURE_CLI_HORIZONDB_FLEXIBLE_RM_URI'
SUB_ID_OVERRIDE = 'AZURE_CLI_HORIZONDB_FLEXIBLE_SUB_ID'


def get_horizondb_management_client(cli_ctx, subscription_id=None, **_):
    from os import getenv
    from azext_horizondb.vendored_sdks import HorizonDBMgmtClient
    # Allow overriding resource manager URI using environment variable
    # for testing purposes. Subscription id is also determined by environment
    # variable.
    rm_uri_override = getenv(RM_URI_OVERRIDE)
    subscription = subscription_id if subscription_id is not None else getenv(SUB_ID_OVERRIDE)
    if rm_uri_override:
        return get_mgmt_service_client(
            cli_ctx,
            HorizonDBMgmtClient,
            subscription_id=subscription,
            base_url=rm_uri_override)
    # Normal production scenario.
    return get_mgmt_service_client(cli_ctx, HorizonDBMgmtClient, subscription_id=subscription)


def resource_client_factory(cli_ctx, subscription_id=None):
    return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES, subscription_id=subscription_id)


def cf_horizondb_clusters(cli_ctx, _):
    return get_horizondb_management_client(cli_ctx).horizon_db_clusters
