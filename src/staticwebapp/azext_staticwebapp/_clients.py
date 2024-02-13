# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json

from azure.cli.core.util import send_raw_request
from azure.cli.core.commands.client_factory import get_subscription_id


API_VERSION = "2022-03-01"


class DbConnectionClient():
    @classmethod
    def create_or_update(cls, cmd, resource_group_name, name, environment, connection_name="default",
                         db_connection=None):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = API_VERSION
        sub_id = get_subscription_id(cmd.cli_ctx)
        if environment:
            url_fmt = ("{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/staticsites/{}/builds/{}"
                       "/databaseConnections/{}?api-version={}")
            request_url = url_fmt.format(
                management_hostname.strip('/'),
                sub_id,
                resource_group_name,
                name,
                environment,
                connection_name,
                api_version)
        else:
            url_fmt = ("{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/staticsites/{}"
                       "/databaseConnections/{}?api-version={}")
            request_url = url_fmt.format(
                management_hostname.strip('/'),
                sub_id,
                resource_group_name,
                name,
                connection_name,
                api_version)

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(db_connection))
        return r.json()

    @classmethod
    def show(cls, cmd, resource_group_name, name, environment, connection_name="default", detailed=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = API_VERSION
        sub_id = get_subscription_id(cmd.cli_ctx)
        if environment:
            url_fmt = ("{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/staticsites/{}/builds/{}"
                       "/databaseConnections/{}?api-version={}")
            request_url = url_fmt.format(
                management_hostname.strip('/'),
                sub_id,
                resource_group_name,
                name,
                environment,
                connection_name,
                api_version)
        else:
            url_fmt = ("{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/staticsites/{}"
                       "/databaseConnections/{}?api-version={}")
            request_url = url_fmt.format(
                management_hostname.strip('/'),
                sub_id,
                resource_group_name,
                name,
                connection_name,
                api_version)

        verb = "GET" if not detailed else "POST"

        r = send_raw_request(cmd.cli_ctx, verb, request_url)
        return r.json()

    @classmethod
    def list(cls, cmd, resource_group_name, name, environment, connection_name="default", detailed=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = API_VERSION
        sub_id = get_subscription_id(cmd.cli_ctx)
        if environment:
            url_fmt = ("{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/staticsites/{}/builds/{}"
                       "/databaseConnections/{}?api-version={}")
            request_url = url_fmt.format(
                management_hostname.strip('/'),
                sub_id,
                resource_group_name,
                name,
                environment,
                connection_name if not detailed else f"{connection_name}/show",
                api_version)
        else:
            url_fmt = ("{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/staticsites/{}"
                       "/databaseConnections/{}?api-version={}")
            request_url = url_fmt.format(
                management_hostname.strip('/'),
                sub_id,
                resource_group_name,
                name,
                connection_name if not detailed else f"{connection_name}/show",
                api_version)

        verb = "GET" if not detailed else "POST"

        r = send_raw_request(cmd.cli_ctx, verb, request_url)
        return r.json()

    @classmethod
    def delete(cls, cmd, resource_group_name, name, environment, connection_name="default"):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = API_VERSION
        sub_id = get_subscription_id(cmd.cli_ctx)
        if environment:
            url_fmt = ("{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/staticsites/{}/builds/{}"
                       "/databaseConnections/{}?api-version={}")
            request_url = url_fmt.format(
                management_hostname.strip('/'),
                sub_id,
                resource_group_name,
                name,
                environment,
                connection_name,
                api_version)
        else:
            url_fmt = ("{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Web/staticsites/{}"
                       "/databaseConnections/{}?api-version={}")
            request_url = url_fmt.format(
                management_hostname.strip('/'),
                sub_id,
                resource_group_name,
                name,
                connection_name,
                api_version)

        send_raw_request(cmd.cli_ctx, "DELETE", request_url)
