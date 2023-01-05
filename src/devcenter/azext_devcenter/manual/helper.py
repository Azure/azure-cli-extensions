import json
from azure.cli.core.azclierror import ResourceNotFoundError
from azure.cli.core.util import send_raw_request


def get_project_data(cli_ctx, dev_center_name, project_name=None):
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
        resource=cli_ctx.cloud.endpoints.resource_manager,
    )
    resource_graph_data = response.json()["data"]

    # TODO: confirm this scenario and error messages
    if len(resource_graph_data) == 0 and project_name is None:
        error_message = f"""No projects were found in the dev center \
'{dev_center_name}'. Please contact your admin to gain access to specific projects."""
        raise ResourceNotFoundError(error_message)
    if len(resource_graph_data) == 0:
        error_message = f"""No project '{project_name}' was found in the dev center \
'{dev_center_name}'. Please contact your admin to gain access to specific projects."""
        raise ResourceNotFoundError(error_message)

    return resource_graph_data[0]
