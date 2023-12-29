# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import uuid
from knack.util import CLIError
from azext_aks_preview.azuremonitormetrics.constants import (
    GRAFANA_API,
    GRAFANA_ROLE_ASSIGNMENT_API,
    GrafanaLink
)
from azext_aks_preview.azuremonitormetrics.helper import sanitize_resource_id


def link_grafana_instance(cmd, raw_parameters, azure_monitor_workspace_resource_id):
    from azure.cli.core.util import send_raw_request
    # GET grafana principal ID
    try:
        grafana_resource_id = raw_parameters.get("grafana_resource_id")
        if grafana_resource_id is None or grafana_resource_id == "":
            return GrafanaLink.NOPARAMPROVIDED
        grafana_resource_id = sanitize_resource_id(grafana_resource_id)
        grafanaURI = f"{cmd.cli_ctx.cloud.endpoints.resource_manager}{grafana_resource_id}?api-version={GRAFANA_API}"
        headers = ['User-Agent=azuremonitormetrics.link_grafana_instance']
        grafanaArmResponse = send_raw_request(cmd.cli_ctx, "GET", grafanaURI, body={}, headers=headers)
        servicePrincipalId = grafanaArmResponse.json()["identity"]["principalId"]
    except CLIError as e:
        raise CLIError(e)  # pylint: disable=raise-missing-from
    # Add Role Assignment
    try:
        MonitoringDataReader = "b0d8363b-8ddd-447d-831f-62ca05bff136"
        roleDefinitionURI = (
            f"{cmd.cli_ctx.cloud.endpoints.resource_manager}{azure_monitor_workspace_resource_id}/providers/"
            f"Microsoft.Authorization/roleAssignments/{uuid.uuid4()}?api-version={GRAFANA_ROLE_ASSIGNMENT_API}"
        )
        roleDefinitionId = (
            f"{azure_monitor_workspace_resource_id}/providers/"
            f"Microsoft.Authorization/roleDefinitions/{MonitoringDataReader}"
        )
        association_body = json.dumps(
            {
                "properties": {
                    "roleDefinitionId": roleDefinitionId,
                    "principalId": servicePrincipalId,
                }
            }
        )
        headers = ['User-Agent=azuremonitormetrics.add_role_assignment']
        send_raw_request(cmd.cli_ctx, "PUT", roleDefinitionURI, body=association_body, headers=headers)
    except CLIError as e:
        if e.response.status_code != 409:
            erroString = (
                "Role Assingment failed. Please manually assign the `Monitoring Data Reader` role to "
                f"the Azure Monitor Workspace ({azure_monitor_workspace_resource_id}) for the Azure Managed Grafana "
                f"System Assigned Managed Identity ({servicePrincipalId})"
            )
            print(erroString)
    # Setting up AMW Integration
    targetGrafanaArmPayload = grafanaArmResponse.json()
    if targetGrafanaArmPayload["properties"] is None:
        raise CLIError("Invalid grafana payload to add AMW integration")
    if "grafanaIntegrations" not in json.dumps(targetGrafanaArmPayload):
        targetGrafanaArmPayload["properties"]["grafanaIntegrations"] = {}
    if "azureMonitorWorkspaceIntegrations" not in json.dumps(targetGrafanaArmPayload):
        targetGrafanaArmPayload["properties"]["grafanaIntegrations"]["azureMonitorWorkspaceIntegrations"] = []
    amwIntegrations = targetGrafanaArmPayload["properties"]["grafanaIntegrations"]["azureMonitorWorkspaceIntegrations"]
    if amwIntegrations and azure_monitor_workspace_resource_id in json.dumps(amwIntegrations).lower():
        return GrafanaLink.ALREADYPRESENT
    try:
        grafanaURI = f"{cmd.cli_ctx.cloud.endpoints.resource_manager}{grafana_resource_id}?api-version={GRAFANA_API}"
        targetGrafanaArmPayload["properties"]["grafanaIntegrations"][
            "azureMonitorWorkspaceIntegrations"
        ].append(
            {"azureMonitorWorkspaceResourceId": azure_monitor_workspace_resource_id}
        )
        targetGrafanaArmPayload = json.dumps(targetGrafanaArmPayload)
        headers = ['User-Agent=azuremonitormetrics.setup_amw_grafana_integration', 'Content-Type=application/json']
        send_raw_request(cmd.cli_ctx, "PUT", grafanaURI, body=targetGrafanaArmPayload, headers=headers)
    except CLIError as e:
        raise CLIError(e)  # pylint: disable=raise-missing-from
    return GrafanaLink.SUCCESS
