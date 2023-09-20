# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# --------------------------------------------------------------------------
import json
from datetime import (timedelta, datetime)
from azure.cli.core.azclierror import ResourceNotFoundError, AzureInternalError
from azure.cli.core.util import send_raw_request
from azure.cli.core._profile import Profile


def get_project_arg(cli_ctx, dev_center_name, project_name=None):
    management_hostname = cli_ctx.cloud.endpoints.resource_manager.strip("/")
    api_version = "2021-03-01"

    project_filter = ""
    if project_name is not None:
        project_filter = f"| where name =~ '{project_name}'"

    query = f""" Resources |where type =~'Microsoft.devcenter/projects'
    {project_filter}
    | extend devCenterArr = split(properties.devCenterId, '/')
    | extend devCenterName = devCenterArr[array_length(devCenterArr) -1]
    | where devCenterName =~ '{dev_center_name}'
    | take 1
    | extend devCenterUri = properties.devCenterUri
    | project name,devCenterUri """
    options = {
        "allowPartialScopes": True}  # maximum of 5000 subs for cross tenant query

    content = {"query": query, "options": options}
    request_url = f"{management_hostname}/providers/Microsoft.ResourceGraph/resources?api-version={api_version}"

    response = send_raw_request(
        cli_ctx,
        "POST",
        request_url,
        body=json.dumps(content),
        resource=cli_ctx.cloud.endpoints.active_directory_resource_id,
    )

    response_code = int(response.status_code)
    if response_code != 200:
        error_details = json.loads(response.text, strict=False)
        error_message = f"""Azure Resource Graph encountered an error. \
Please try using the endpoint parameter instead of the dev center parameter. Error details: {error_details}"""
        raise AzureInternalError(error_message)
    return response.json()["data"]


def get_project_data(cli_ctx, dev_center_name, project_name=None):
    profile = Profile()
    tenant_id = profile.get_subscription()["tenantId"]

    resource_graph_data = get_project_arg(
        cli_ctx, dev_center_name, project_name)

    error_help = f"""under the current tenant '{tenant_id}'. \
Please contact your admin to gain access to specific projects or \
use a different tenant where you have access to projects."""

    if len(resource_graph_data) == 0 and project_name is None:
        error_message = f"""No projects were found in the dev center \
'{dev_center_name}' {error_help}"""
        raise ResourceNotFoundError(error_message)
    if len(resource_graph_data) == 0:
        error_message = f"""No project '{project_name}' was found in the dev center \
'{dev_center_name}' {error_help}"""
        raise ResourceNotFoundError(error_message)

    return resource_graph_data[0]


def get_earliest_time(action_iterator):
    earliest_time = None
    for action in action_iterator:
        if action["next"] is not None:
            action_string = action["next"]["scheduledTime"]
            action_time = datetime.strptime(action_string, "%Y-%m-%dT%H:%M:%S.%fZ")
            if earliest_time is None or action_time < earliest_time:
                earliest_time = action_time
    return earliest_time


def get_delayed_time(delay_time, action_time):
    split_time = delay_time.split(":")
    hours = int(split_time[0])
    minutes = int(split_time[1])
    return action_time + timedelta(hours=hours, minutes=minutes)
