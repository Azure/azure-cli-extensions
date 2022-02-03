# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from sys import api_version
from azure.cli.core.util import send_raw_request
from azure.cli.core.commands.client_factory import get_subscription_id


API_VERSION = "2021-03-01"


class KubeEnvironmentClient():
    @classmethod
    def show(cls, cmd, resource_group_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = API_VERSION
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/kubeEnvironments/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        return r.json()
