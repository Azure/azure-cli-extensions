# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json

from knack.util import CLIError

from azure.cli.core.util import send_raw_request
from azure.cli.core.commands.client_factory import get_subscription_id


class StaticWebAppFrontDoorClient:
    @classmethod
    def _request(cls, cmd, resource_group, name, http_method="GET", body=None):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = "2021-02-01"
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/staticSites/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group,
            name,
            api_version)

        if body is not None:
            r = send_raw_request(cmd.cli_ctx, http_method, request_url, body=json.dumps(body))
        else:
            r = send_raw_request(cmd.cli_ctx, http_method, request_url)

        return r

    # TODO test SKU validation
    @classmethod
    def set(cls, cmd, resource_group, name, enable):
        params = cls.get(cmd, resource_group, name).json()
        if enable and params["sku"].get("name").lower() != "standard":
            raise CLIError("Invalid SKU: '{}'. Staticwebapp {} must have 'Standard' SKU to use "
                           "enterprise edge CDN").format(params["sku"].get("name"), name)
        params["properties"]["enterpriseGradeCdnStatus"] = "enabled" if enable else "disabled"
        return cls._request(cmd, resource_group, name, "PUT", params)

    @classmethod
    def get(cls, cmd, resource_group, name):
        return cls._request(cmd, resource_group, name)


def enable_staticwebapp_enterprise_edge(cmd, name, resource_group_name):
    return StaticWebAppFrontDoorClient.set(cmd, name=name, resource_group=resource_group_name, enable=True)


def disable_staticwebapp_enterprise_edge(cmd, name, resource_group_name):
    return StaticWebAppFrontDoorClient.set(cmd, name=name, resource_group=resource_group_name, enable=False)


def show_staticwebapp_enterprise_edge_status(cmd, name, resource_group_name):
    staticsite_data = StaticWebAppFrontDoorClient.get(cmd, name=name, resource_group=resource_group_name).json()
    return {"enterpriseGradeCdnStatus": staticsite_data["properties"]["enterpriseGradeCdnStatus"]}
