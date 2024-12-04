# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import telemetry

import azext_connectedk8s._constants as consts
import azext_connectedk8s.clientproxyhelper._utils as clientproxyutils

from ..vendored_sdks.models import (
    ListClusterUserCredentialProperties,
)


def handle_post_at_to_csp(cmd, api_server_port, tenant_id, clientproxy_process):
    kid = clientproxyutils.fetch_pop_publickey_kid(api_server_port, clientproxy_process)
    post_at_response, expiry = clientproxyutils.fetch_and_post_at_to_csp(
        cmd, api_server_port, tenant_id, kid, clientproxy_process
    )

    if post_at_response.status_code != 200:
        if (
            post_at_response.status_code == 500
            and "public key expired" in post_at_response.text
        ):
            # Handle public key rotation
            telemetry.set_exception(
                exception=post_at_response.text,
                fault_type=consts.PoP_Public_Key_Expried_Fault_Type,
                summary="PoP public key has expired",
            )
            kid = clientproxyutils.fetch_pop_publickey_kid(
                api_server_port, clientproxy_process
            )  # Fetch rotated public key
            # Retry posting AT with the new public key
            post_at_response, expiry = clientproxyutils.fetch_and_post_at_to_csp(
                cmd, api_server_port, tenant_id, kid, clientproxy_process
            )
        # If after second try we still dont get a 200, raise error
        if post_at_response.status_code != 200:
            telemetry.set_exception(
                exception=post_at_response.text,
                fault_type=consts.Post_AT_To_ClientProxy_Failed_Fault_Type,
                summary="Failed to post access token to client proxy",
            )
            clientproxyutils.close_subprocess_and_raise_cli_error(
                clientproxy_process,
                "Failed to post access token to client proxy" + post_at_response.text,
            )

    return expiry


def get_cluster_user_credentials(
    client, resource_group_name, cluster_name, auth_method
):
    list_prop = ListClusterUserCredentialProperties(
        authentication_method=auth_method, client_proxy=True
    )
    return client.list_cluster_user_credential(
        resource_group_name, cluster_name, list_prop
    )


def post_register_to_proxy(
    data,
    token,
    client_proxy_port,
    subscription_id,
    resource_group_name,
    cluster_name,
    clientproxy_process,
):
    if token is not None:
        data["kubeconfigs"][0]["value"] = clientproxyutils.insert_token_in_kubeconfig(
            data, token
        )

    uri = (
        f"http://localhost:{client_proxy_port}/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}"
        f"/providers/Microsoft.Kubernetes/connectedClusters/{cluster_name}/register?api-version=2020-10-01"
    )

    # Posting hybrid connection details to proxy in order to get kubeconfig
    response = clientproxyutils.make_api_call_with_retries(
        uri,
        data,
        "post",
        False,
        consts.Post_Hybridconn_Fault_Type,
        "Unable to post hybrid connection details to clientproxy",
        "Failed to pass hybrid connection details to proxy.",
        clientproxy_process,
    )
    return response
