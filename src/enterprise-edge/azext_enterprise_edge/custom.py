# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json

from knack.util import CLIError
from knack.log import get_logger

from azure.cli.core.util import send_raw_request
from azure.cli.core.commands.client_factory import get_subscription_id


logger = get_logger(__name__)


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

    @classmethod
    def set(cls, cmd, resource_group, name, enable):
        params = cls.get(cmd, resource_group, name).json()

        if enable:
            cls._validate_cdn_provider_registered(cmd)
            cls._validate_sku(params["sku"].get("name"))

        params["properties"]["enterpriseGradeCdnStatus"] = "enabled" if enable else "disabled"
        return cls._request(cmd, resource_group, name, "PUT", params)

    @classmethod
    def get(cls, cmd, resource_group, name):
        return cls._request(cmd, resource_group, name)

    @classmethod
    def _validate_cdn_provider_registered(cls, cmd):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = "2021-04-01"
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/providers/Microsoft.CDN?api-version={}"

        request_url = url_fmt.format(management_hostname.strip('/'), sub_id, api_version)

        registration = send_raw_request(cmd.cli_ctx, "GET", request_url).json().get("registrationState").lower()
        if registration != "registered":
            raise CLIError("Provider Microsoft.CDN is not registered. "
                           "Please run 'az provider register --wait --namespace Microsoft.CDN'")

    @classmethod
    def _validate_sku(cls, sku_name):
        if sku_name.lower() != "standard":
            raise CLIError("Invalid SKU: '{}'. Staticwebapp must have 'Standard' SKU to use "
                           "enterprise edge CDN").format(sku_name)


def enable_staticwebapp_enterprise_edge(cmd, name, resource_group_name):
    logger.warn("For optimal experience and availability please check our documentation https://aka.ms/swaedge")
    return StaticWebAppFrontDoorClient.set(cmd, name=name, resource_group=resource_group_name, enable=True)


def disable_staticwebapp_enterprise_edge(cmd, name, resource_group_name):
    logger.warn("For optimal experience and availability please check our documentation https://aka.ms/swaedge")
    return StaticWebAppFrontDoorClient.set(cmd, name=name, resource_group=resource_group_name, enable=False)


def show_staticwebapp_enterprise_edge_status(cmd, name, resource_group_name):
    logger.warn("For optimal experience and availability please check our documentation https://aka.ms/swaedge")
    staticsite_data = StaticWebAppFrontDoorClient.get(cmd, name=name, resource_group=resource_group_name).json()
    return {"enterpriseGradeCdnStatus": staticsite_data["properties"]["enterpriseGradeCdnStatus"]}
