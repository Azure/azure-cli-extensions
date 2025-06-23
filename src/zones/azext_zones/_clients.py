# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.util import send_raw_request
from azure.cli.core.commands.client_factory import get_subscription_id


# pylint: disable=too-few-public-methods
class MgmtApiClient():

    def query(self, cmd, method, resource, api_version, requestBody):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = ("{}/subscriptions/{}/{}?api-version={}")
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource,
            api_version)

        r = send_raw_request(cmd.cli_ctx, method, request_url, body=requestBody)
        return r.json()
