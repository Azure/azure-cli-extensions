# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.core.azclierror import InvalidArgumentValueError
from knack.util import CLIError
from .helper import (
    get_cluster_region,
    rp_registrations
)
from .amw.helper import get_azure_monitor_workspace_resource
from .dc.dce_api import create_dce
from .dc.dcr_api import create_dcr
from .dc.dcra_api import create_dcra
from .amg.link import link_grafana_instance
from .recordingrules.create import create_rules
from .recordingrules.delete import delete_rules
from .dc.delete import get_dc_objects_list, delete_dc_objects_if_prometheus_enabled
from .helper import safe_key_check, safe_value_get


# pylint: disable=line-too-long
def link_azure_monitor_profile_artifacts(
        cmd,
        cluster_rp,
        cluster_subscription,
        cluster_resource_group_name,
        cluster_name,
        configuration_settings,
        cluster_type
):
    cluster_region = get_cluster_region(cmd, cluster_rp, cluster_subscription, cluster_resource_group_name, cluster_name, cluster_type)
    # MAC creation if required
    azure_monitor_workspace_resource_id, azure_monitor_workspace_location = get_azure_monitor_workspace_resource(cmd, cluster_subscription, cluster_region, configuration_settings)
    # DCE creation
    dce_resource_id = create_dce(cmd, cluster_subscription, cluster_resource_group_name, cluster_name, azure_monitor_workspace_location)
    # DCR creation
    dcr_resource_id = create_dcr(cmd, azure_monitor_workspace_location, azure_monitor_workspace_resource_id, cluster_subscription, cluster_resource_group_name, cluster_name, dce_resource_id)
    # DCRA creation
    create_dcra(cmd, cluster_region, cluster_subscription, cluster_resource_group_name, cluster_name, dcr_resource_id)
    # Link grafana
    link_grafana_instance(cmd, azure_monitor_workspace_resource_id, configuration_settings)
    # create recording rules and alerts
    create_rules(cmd, cluster_subscription, cluster_resource_group_name, cluster_name, azure_monitor_workspace_resource_id, azure_monitor_workspace_location)


# pylint: disable=line-too-long
def unlink_azure_monitor_profile_artifacts(cmd, cluster_subscription, cluster_resource_group_name, cluster_name):
    # Remove DC* if prometheus is enabled
    dc_objects_list = get_dc_objects_list(cmd, cluster_subscription, cluster_resource_group_name, cluster_name)
    delete_dc_objects_if_prometheus_enabled(cmd, dc_objects_list, cluster_subscription, cluster_resource_group_name, cluster_name)
    # Delete rules (Conflict({"error":{"code":"InvalidResourceLocation","message":"The resource 'NodeRecordingRulesRuleGroup-<clustername>' already exists in location 'eastus2' in resource group '<clustername>'.
    # A resource with the same name cannot be created in location 'eastus'. Please select a new resource name."}})
    delete_rules(cmd, cluster_subscription, cluster_resource_group_name, cluster_name)


# pylint: disable=too-many-locals,too-many-branches,too-many-statements,line-too-long
def ensure_azure_monitor_profile_prerequisites(
        cmd,
        cluster_rp,
        cluster_subscription,
        cluster_resource_group_name,
        cluster_name,
        configuration_settings,
        cluster_type
):
    cloud_name = cmd.cli_ctx.cloud.name
    if cloud_name.lower() == 'azurechinacloud':
        raise CLIError("Azure China Cloud is not supported for the Azure Monitor Metrics extension")

    if cloud_name.lower() == "azureusgovernment":
        if safe_key_check('grafana-resource-id', configuration_settings):
            grafana_resource_id = safe_value_get('grafana-resource-id', configuration_settings)
        if grafana_resource_id is not None:
            if grafana_resource_id != "":
                raise InvalidArgumentValueError("Azure US Government cloud does not support Azure Managed Grarfana yet. Please follow this documenation for enabling it via the public cloud : aka.ms/ama-grafana-link-ff")

    # Do RP registrations if required
    rp_registrations(cmd, cluster_subscription)
    link_azure_monitor_profile_artifacts(
        cmd,
        cluster_rp,
        cluster_subscription,
        cluster_resource_group_name,
        cluster_name,
        configuration_settings,
        cluster_type
    )
