# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from sys import api_version
from azure.cli.core.util import send_raw_request
from azure.cli.core.commands.client_factory import get_subscription_id


API_VERSION = "2021-03-01"
NEW_API_VERSION = "2022-01-01-preview"


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

    @classmethod
    def list_by_subscription(cls, cmd, formatter=lambda x: x):
        kube_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = API_VERSION
        sub_id = get_subscription_id(cmd.cli_ctx)
        request_url = "{}/subscriptions/{}/providers/Microsoft.Web/kubeEnvironments?api-version={}".format(
            management_hostname.strip('/'),
            sub_id,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        j = r.json()
        for kube in j["value"]:
            formatted = formatter(kube)
            kube_list.append(formatted)

        while j.get("nextLink") is not None:
            request_url = j["nextLink"]
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)
            j = r.json()
            for kube in j["value"]:
                formatted = formatter(kube)
                kube_list.append(formatted)

        return kube_list

    @classmethod
    def list_by_resource_group(cls, cmd, resource_group_name, formatter=lambda x: x):
        kube_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = API_VERSION
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/kubeEnvironments?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        j = r.json()
        for kube in j["value"]:
            formatted = formatter(kube)
            kube_list.append(formatted)

        while j.get("nextLink") is not None:
            request_url = j["nextLink"]
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)
            j = r.json()
            for kube in j["value"]:
                formatted = formatter(kube)
                kube_list.append(formatted)

        return kube_list


class ManagedEnvironmentClient():
    @classmethod
    def show(cls, cmd, resource_group_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = NEW_API_VERSION
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        return r.json()

    @classmethod
    def list_by_subscription(cls, cmd, formatter=lambda x: x):
        kube_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = NEW_API_VERSION
        sub_id = get_subscription_id(cmd.cli_ctx)
        request_url = "{}/subscriptions/{}/providers/Microsoft.App/managedEnvironments?api-version={}".format(
            management_hostname.strip('/'),
            sub_id,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        j = r.json()
        for kube in j["value"]:
            formatted = formatter(kube)
            kube_list.append(formatted)

        while j.get("nextLink") is not None:
            request_url = j["nextLink"]
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)
            j = r.json()
            for kube in j["value"]:
                formatted = formatter(kube)
                kube_list.append(formatted)

        return kube_list

    @classmethod
    def list_by_resource_group(cls, cmd, resource_group_name, formatter=lambda x: x):
        kube_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = NEW_API_VERSION
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        j = r.json()
        for kube in j["value"]:
            formatted = formatter(kube)
            kube_list.append(formatted)

        while j.get("nextLink") is not None:
            request_url = j["nextLink"]
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)
            j = r.json()
            for kube in j["value"]:
                formatted = formatter(kube)
                kube_list.append(formatted)

        return kube_list
