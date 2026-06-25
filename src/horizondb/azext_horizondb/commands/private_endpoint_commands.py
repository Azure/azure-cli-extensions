# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def horizondb_approve_private_endpoint_connection(
        cmd, client, resource_group_name, cluster_name, private_endpoint_connection_name,
        description=None):
    return _update_private_endpoint_connection_status(
        cmd, client, resource_group_name, cluster_name, private_endpoint_connection_name,
        is_approved=True, description=description)


def horizondb_reject_private_endpoint_connection(
        cmd, client, resource_group_name, cluster_name, private_endpoint_connection_name,
        description=None):
    return _update_private_endpoint_connection_status(
        cmd, client, resource_group_name, cluster_name, private_endpoint_connection_name,
        is_approved=False, description=description)


def _update_private_endpoint_connection_status(
        cmd, client, resource_group_name, cluster_name, private_endpoint_connection_name,
        is_approved=True, description=None):  # pylint: disable=unused-argument
    from azext_horizondb._client_factory import cf_horizondb_private_endpoint_connections
    from azext_horizondb.vendored_sdks.models import (
        OptionalPropertiesUpdateableProperties,
        PrivateEndpointConnectionUpdate,
        PrivateLinkServiceConnectionState,
    )

    private_endpoint_connections_client = cf_horizondb_private_endpoint_connections(cmd.cli_ctx, None)
    private_endpoint_connections_client.get(
        resource_group_name=resource_group_name,
        cluster_name=cluster_name,
        private_endpoint_connection_name=private_endpoint_connection_name)

    new_status = 'Approved' if is_approved else 'Rejected'
    state = PrivateLinkServiceConnectionState(
        status=new_status,
        description=description)
    update = PrivateEndpointConnectionUpdate(
        properties=OptionalPropertiesUpdateableProperties(
            private_link_service_connection_state=state))

    return client.begin_update(
        resource_group_name=resource_group_name,
        cluster_name=cluster_name,
        private_endpoint_connection_name=private_endpoint_connection_name,
        properties=update)


def horizondb_private_link_resource_get(
        client, resource_group_name, cluster_name, group_name):
    return client.get(
        resource_group_name=resource_group_name,
        cluster_name=cluster_name,
        group_name=group_name)
