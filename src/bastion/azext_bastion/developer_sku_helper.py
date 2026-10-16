# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=import-error,unused-import

def _get_data_pod(cmd, resource_port, target_resource_id, bastion):
    from azure.core.exceptions import HttpResponseError
    from azure.cli.core._profile import Profile
    from azure.cli.core.util import should_disable_connection_verify
    from azure.mgmt.core.tools import parse_resource_id
    import requests

    subscription_id = parse_resource_id(bastion['id'])['subscription']
    auth_token, _, _ = Profile(cli_ctx=cmd.cli_ctx).get_raw_token(subscription=subscription_id)
    content = {
        'resourceId': target_resource_id,
        'bastionResourceId': bastion['id'],
        'vmPort': resource_port,
        'azToken': auth_token[1],
        'connectionType': 'nativeclient'
    }
    headers = {'Content-Type': 'application/json'}

    web_address = f"https://{bastion['dnsName']}/api/connection"
    response = requests.post(web_address, json=content, headers=headers,
                             verify=not should_disable_connection_verify())

    if not response.ok:
        raise HttpResponseError(
            response=response,
            message=f"Bastion connection request failed (HTTP {response.status_code})."
        )

    return response.content.decode("utf-8")
