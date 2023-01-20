def _get_data_pod(cmd, resource_port, target_resource_id, bastion):
    from azure.cli.core._profile import Profile
    from azure.cli.core.util import should_disable_connection_verify
    import json
    import requests


    profile = Profile(cli_ctx=cmd.cli_ctx)
    auth_token, _, _ = profile.get_raw_token()
    content = {
        'resourceId': target_resource_id,
        'bastionResourceId': bastion.id,
        'vmPort': resource_port,
        'azToken': auth_token[1],
        'connectionType' : 'nativeclient'
    }
    headers = {
            'Content-Type': 'application/json',
        }

    web_address = 'https://{}/api/connection'.format(bastion.dns_name)
    response = requests.post(web_address, json=content, headers=headers, verify=(not should_disable_connection_verify()))
    response_json = None

    return response.content.decode("utf-8")

    