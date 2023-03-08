# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# --------------------------------------------------------------------------
import json
from azure.cli.core.azclierror import ResourceNotFoundError
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

    content = {"query": query}
    request_url = f"{management_hostname}/providers/Microsoft.ResourceGraph/resources?api-version={api_version}"

    response = send_raw_request(
        cli_ctx,
        "POST",
        request_url,
        body=json.dumps(content),
        resource=cli_ctx.cloud.endpoints.active_directory_resource_id,
    )
    return response.json()["data"]


def get_project_data(cli_ctx, dev_center_name, project_name=None):
    profile = Profile()
    tenant_id = profile.get_subscription()['tenantId']

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
