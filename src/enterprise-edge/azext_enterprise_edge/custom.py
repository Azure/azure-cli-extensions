# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json

from knack.util import CLIError
from knack.log import get_logger

from azure.cli.core.util import send_raw_request
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.command_modules.appservice._client_factory import web_client_factory


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
    def set(cls, cmd, resource_group, name, enable, no_register=False):
        params = cls.get(cmd, resource_group, name).json()

        if enable and not no_register:
            cls._register_cdn_provider(cmd)
            cls._validate_sku(params["sku"].get("name"))

        params["properties"]["enterpriseGradeCdnStatus"] = "enabled" if enable else "disabled"
        return cls._request(cmd, resource_group, name, "PUT", params)

    @classmethod
    def get(cls, cmd, resource_group, name):
        return cls._request(cmd, resource_group, name)

    @classmethod
    def _register_cdn_provider(cls, cmd):
        namespace = "Microsoft.CDN"
        api_version = "2021-04-01"
        ProviderRegistrationRequest, ProviderConsentDefinition = cmd.get_models('ProviderRegistrationRequest',
                                                                                'ProviderConsentDefinition')
        properties = ProviderRegistrationRequest(third_party_provider_consent=ProviderConsentDefinition(
            consent_to_authorization=True))
        client = web_client_factory(cmd.cli_ctx, api_version=api_version)
        try:
            client.providers.register(namespace, properties=properties)
        except Exception as e:
            msg = "Server responded with error message : {} \n"\
                  "Enabling enterprise-grade edge requires reregistration for the Azure Front "\
                  "Door Microsoft.CDN resource provider. We were unable to perform that reregistration on your "\
                  "behalf. Please check with your admin on permissions and review the documentation available at "\
                  "https://go.microsoft.com/fwlink/?linkid=2185350. "\
                  "Or try running registration manually with: az provider register --wait --namespace Microsoft.CDN"
            raise CLIError(msg.format(e.args)) from e

    @classmethod
    def _validate_sku(cls, sku_name):
        if sku_name.lower() != "standard":
            raise CLIError("Invalid SKU: '{}'. Staticwebapp must have 'Standard' SKU to use "
                           "enterprise edge CDN".format(sku_name))


def _format_show_response(cmd, name, resource_group_name):
    staticsite_data = StaticWebAppFrontDoorClient.get(cmd, name=name, resource_group=resource_group_name).json()
    return {"enterpriseGradeCdnStatus": staticsite_data["properties"]["enterpriseGradeCdnStatus"]}


def enable_staticwebapp_enterprise_edge(cmd, name, resource_group_name, no_register=False):
    logger.warning("For optimal experience and availability please check our documentation https://aka.ms/swaedge")
    StaticWebAppFrontDoorClient.set(cmd, name=name, resource_group=resource_group_name, enable=True,
                                    no_register=no_register)
    return _format_show_response(cmd, name, resource_group_name)


def disable_staticwebapp_enterprise_edge(cmd, name, resource_group_name):
    logger.warning("For optimal experience and availability please check our documentation https://aka.ms/swaedge")
    StaticWebAppFrontDoorClient.set(cmd, name=name, resource_group=resource_group_name, enable=False)
    return _format_show_response(cmd, name, resource_group_name)


def show_staticwebapp_enterprise_edge_status(cmd, name, resource_group_name):
    logger.warning("For optimal experience and availability please check our documentation https://aka.ms/swaedge")
    return _format_show_response(cmd, name, resource_group_name)
