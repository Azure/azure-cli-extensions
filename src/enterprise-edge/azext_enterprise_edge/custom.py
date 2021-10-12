# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.command_modules.appservice.utils import retryable_method

class StaticWebAppFrontDoorClient:
    @classmethod
    def _request(cls, cmd, resource_group, name, http_method="GET", body=None):
        from azure.cli.core.util import send_raw_request
        from azure.cli.core.commands.client_factory import get_subscription_id
        import json

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


    # TODO test with nonextant staticsite
    @classmethod
    def set(cls, cmd, resource_group, name, enable):
        params = cls.get(cmd, resource_group, name).json()
        params["properties"]["enterpriseGradeCdnStatus"] = "enabled" if enable else "disabled"
        return cls._request(cmd, resource_group, name, "PUT", params)

    @classmethod
    def get(cls, cmd, resource_group, name):
        return cls._request(cmd, resource_group, name)

    class StatusPoller:
        def __init__(self, cmd, name, resource_group_name, status):
            self.cmd = cmd
            self.name = name
            self.resource_group = resource_group_name
            self.status = status
            self._response = None
            self._staticsite_status = None

        @retryable_method(3, 5)
        def done(self):
            self._response = StaticWebAppFrontDoorClient.get(self.cmd, name=self.name, resource_group=self.resource_group)
            self._staticsite_status = self._response.json()["properties"]["enterpriseGradeCdnStatus"]
            return self._response.json()["properties"]["enterpriseGradeCdnStatus"] == self.status

        def result(self):
            return self._response.json()["properties"]


# TODO verify that SKU is standard
def enable_staticwebapp_enterprise_edge(cmd, name, resource_group_name):
    return StaticWebAppFrontDoorClient.set(cmd, name=name, resource_group=resource_group_name, enable=True)


def disable_staticwebapp_enterprise_edge(cmd, name, resource_group_name):
    return StaticWebAppFrontDoorClient.set(cmd, name=name, resource_group=resource_group_name, enable=False)


def show_staticwebapp_enterprise_edge_status(cmd, name, resource_group_name):
    staticsite_data = StaticWebAppFrontDoorClient.get(cmd, name=name, resource_group=resource_group_name).json()
    return {"enterpriseGradeCdnStatus": staticsite_data["properties"]["enterpriseGradeCdnStatus"]}


def staticwebapp_enterprise_edge_wait(cmd, name, resource_group_name, status="Enabled"):
    from azure.cli.core.commands import LongRunningOperation

    poller = StaticWebAppFrontDoorClient.StatusPoller(cmd, name, resource_group_name, status)
    return LongRunningOperation(cmd.cli_ctx)(poller)