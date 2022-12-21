from azure.cli.core.util import send_raw_request
import json

class ProjectData:            
    def __init__(self,endpoint,project_name):      
        self.endpoint=endpoint                 
        self.project_name=project_name

def get_project_data(cli_ctx, dev_center_name, project_name=None):
    management_hostname = cli_ctx.cloud.endpoints.resource_manager.strip('/')
    api_version = "2021-03-01"
    query = ""
    if project_name is None:
        query = f""" Resources |where type =~'Microsoft.devcenter/projects' 
        | extend devCenterArr = split(properties.devCenterId, '/') 
        | extend devCenterName = devCenterArr[array_length(devCenterArr) -1] 
        | where devCenterName =~ '{dev_center_name}'
        | top 1 by name
        | extend devCenterUri = properties.devCenterUri
        | project name,devCenterUri"""
    else:
        query = f""" Resources |where type =~'Microsoft.devcenter/projects'
        | where name =~ '{project_name}'  
        | extend devCenterArr = split(properties.devCenterId, '/') 
        | extend devCenterName = devCenterArr[array_length(devCenterArr) -1 ]
        | where devCenterName =~ '{dev_center_name}'
        | top 1 by name
        | extend devCenterUri = properties.devCenterUri
        | project name,devCenterUri """ 
    content = {"query": query}
    request_url = f"{management_hostname}/providers/Microsoft.ResourceGraph/resources?api-version={api_version}"

    response = send_raw_request(cli_ctx, "POST", request_url, body=json.dumps(content), resource=cli_ctx.cloud.endpoints.resource_manager)
    responseJson = response.json()
    #TODO: figure out what to do if no projects found (none/or no permissions), should we run query on just Microsoft.devcenter/devcenters? 
    #Error message if project_name is None: Either you have no projects or you don't have access to any projects in dev center "dev_center_name". Please contact your admin. 
    #Error message if project_name is not None: We cannot find the project "project_name" under your dev center "dev_center_name". Please check if you have permissions.
    project = responseJson['data'][0]
    if project_name is None:
        project_name = project['name']
    endpoint = project['devCenterUri']
    return ProjectData(endpoint, project_name)