# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from .aaz.latest.monitor.account import Show as MonitorAccountShow
from ._client_factory import cf_amg
from .custom import _create_role_assignment, _delete_role_assignment

from azure.cli.core.azclierror import ArgumentUsageError
from azure.cli.core.commands.arm import resolve_role_id
from knack.log import get_logger


logger = get_logger(__name__)


def link_amw_to_amg(cmd, grafana_name, monitor_name, grafana_resource_group_name, monitor_resource_group_name,
                    skip_role_assignments):
    grafana_client = cf_amg(cmd.cli_ctx, subscription=None)
    grafana = grafana_client.grafana.get(grafana_resource_group_name, grafana_name)

    principal_id = grafana.identity.principal_id
    if not principal_id:
        raise ArgumentUsageError("The Grafana instance does not have a managed identity.")

    monitor = MonitorAccountShow(cli_ctx=cmd.cli_ctx)(command_args={
        "resource_group": monitor_resource_group_name,
        "azure_monitor_workspace_name": monitor_name
    })

    monitors = grafana.properties.grafana_integrations.azure_monitor_workspace_integrations
    if monitor['id'].lower() in [m.azure_monitor_workspace_resource_id.lower() for m in monitors]:
        raise ArgumentUsageError("The Azure Monitor workspace is already linked to the Grafana instance.")
    monitors.append({"azureMonitorWorkspaceResourceId": monitor['id']})
    resource = {
        "properties": {
            "grafanaIntegrations": {
                "azureMonitorWorkspaceIntegrations": monitors
            }
        }
    }

    grafana_client.grafana.update(grafana_resource_group_name, grafana_name, resource)

    if not skip_role_assignments:
        subscription_scope = '/'.join(monitor['id'].split('/')[0:3])  # /subscriptions/<sub_id>
        monitor_role_id = resolve_role_id(cmd.cli_ctx, "Monitoring Data Reader", subscription_scope)
        # assign the Grafana instance the Monitoring Data Reader role on the Azure Monitor workspace
        logger.warning("Azure Monitor workspace of '%s' was linked to the Grafana instance. Now assigning the Grafana"
                       " instance the Monitoring Data Reader role on the Azure Monitor workspace.", monitor['name'])
        _create_role_assignment(cmd.cli_ctx, principal_id, monitor_role_id, monitor['id'])


def unlink_amw_from_amg(cmd, grafana_name, monitor_name, grafana_resource_group_name, monitor_resource_group_name,
                        skip_role_assignments):
    grafana_client = cf_amg(cmd.cli_ctx, subscription=None)
    grafana = grafana_client.grafana.get(grafana_resource_group_name, grafana_name)

    monitor = MonitorAccountShow(cli_ctx=cmd.cli_ctx)(command_args={
        "resource_group": monitor_resource_group_name,
        "azure_monitor_workspace_name": monitor_name
    })

    monitors = grafana.properties.grafana_integrations.azure_monitor_workspace_integrations
    if monitor['id'].lower() not in [m.azure_monitor_workspace_resource_id.lower() for m in monitors]:
        raise ArgumentUsageError("The Azure Monitor workspace is not linked to the Grafana instance.")
    monitors = [m for m in monitors if m.azure_monitor_workspace_resource_id != monitor['id']]
    resource = {
        "properties": {
            "grafanaIntegrations": {
                "azureMonitorWorkspaceIntegrations": monitors
            }
        }
    }

    grafana_client.grafana.update(grafana_resource_group_name, grafana_name, resource)

    principal_id = grafana.identity.principal_id
    if principal_id and not skip_role_assignments:
        subscription_scope = '/'.join(monitor['id'].split('/')[0:3])  # /subscriptions/<sub_id>
        monitor_role_id = resolve_role_id(cmd.cli_ctx, "Monitoring Data Reader", subscription_scope)
        # assign the Grafana instance the Monitoring Data Reader role on the Azure Monitor workspace
        logger.warning("Azure Monitor workspace of '%s' was unlinked from the Grafana instance. Now removing the"
                       " Monitoring Data Reader role assignment from the Azure Monitor workspace.", monitor['name'])
        _delete_role_assignment(cmd.cli_ctx, principal_id, monitor_role_id, monitor['id'])


def list_amw_linked_to_amg(cmd, grafana_name, grafana_resource_group_name):
    grafana_client = cf_amg(cmd.cli_ctx, subscription=None)
    grafana = grafana_client.grafana.get(grafana_resource_group_name, grafana_name)

    monitors = grafana.properties.grafana_integrations.azure_monitor_workspace_integrations
    return [m.azure_monitor_workspace_resource_id for m in monitors]
