# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def synapse_client_factory(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_synapse.vendored_sdks.azure_mgmt_synapse import SynapseManagementClient
    return get_mgmt_service_client(cli_ctx, SynapseManagementClient)


def cf_synapse_client_workspace_factory(cli_ctx, *_):
    return synapse_client_factory(cli_ctx).workspaces


def cf_synapse_client_bigdatapool_factory(cli_ctx, *_):
    return synapse_client_factory(cli_ctx).big_data_pools


def cf_synapse_client_sqlpool_factory(cli_ctx, *_):
    return synapse_client_factory(cli_ctx).sql_pools


def cf_synapse_client_ipfirewallrules_factory(cli_ctx, *_):
    return synapse_client_factory(cli_ctx).ip_firewall_rules


def cf_synapse_client_operations_factory(cli_ctx, *_):
    return synapse_client_factory(cli_ctx).operations


# TODO: add Synapse endpoint and synapse_dns_suffix to azure.cli.core
def synapse_data_plane_factory(cli_ctx, _, subscription=None):
    from azext_synapse.vendored_sdks.azure_synapse import SynapseClient
    from azure.cli.core._profile import Profile
    profile = Profile(cli_ctx=cli_ctx)
    cred, _, _ = profile.get_login_credentials(
        resource="https://dev.azuresynapse.net",
        subscription_id=subscription
    )
    return SynapseClient(
        synapse_dns_suffix='dev.azuresynapse.net',
        livy_api_version='2019-11-01-preview',
        credentials=cred
    )


def cf_synapse_spark_batch(cli_ctx, _, subscription=None):
    return synapse_data_plane_factory(cli_ctx, _, subscription=subscription).spark_batch


def cf_synapse_spark_session(cli_ctx, _, subscription=None):
    return synapse_data_plane_factory(cli_ctx, _, subscription=subscription).spark_session
