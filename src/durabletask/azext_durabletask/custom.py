# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import httpx
from azure.cli.core.commands.client_factory import get_subscription_id
from .aaz.latest.durabletask.scheduler import Show

def list_orchestrations(cmd, resource_group_name, scheduler_name, taskhub_name, max_items=100):
    # Get FQDN of the scheduler
    resource_group_name = resource_group_name
    scheduler_name = scheduler_name
    scheduler = Show(cli_ctx=cmd.cli_ctx)(command_args={    
        "resource_group": resource_group_name,
        "name": scheduler_name,
        "subscription": get_subscription_id(cmd.cli_ctx)
    })

    endpoint = scheduler['properties']['endpoint']
    endpoint+="/v1/taskhubs/orchestrations/query"
    grabbed_token = f"Bearer {get_bearer_token(cmd.cli_ctx)}"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': grabbed_token,
        'x-taskhub': taskhub_name
    }

    payload = {"filter":{},"pagination":{"startIndex":0,"count":max_items},"sort":[{"column":"LAST_UPDATED_AT","direction":"DESCENDING_SORT"}]}

    client = httpx.Client(http2=True)
    response = client.post(endpoint, json=payload, headers=headers)
    return response.json()

def get_bearer_token(cli_ctx):
    from azure.cli.core._profile import Profile
    from azure.cli.core.auth.util import resource_to_scopes
    profile = Profile(cli_ctx=cli_ctx)
    credential, _, _ = profile.get_login_credentials()
    scopes = resource_to_scopes("https://durabletask.io/")
    bearer_token = credential.get_token(*scopes).token
    return bearer_token