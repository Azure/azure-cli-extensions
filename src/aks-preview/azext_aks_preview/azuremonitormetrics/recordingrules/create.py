# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
from azext_aks_preview.azuremonitormetrics.constants import ALERTS_API, RULES_API
from knack.util import CLIError


def get_recording_rules_template(cmd, azure_monitor_workspace_resource_id):
    from azure.cli.core.util import send_raw_request
    headers = ['User-Agent=azuremonitormetrics.get_recording_rules_template']
    armendpoint = cmd.cli_ctx.cloud.endpoints.resource_manager
    url = (
        f"{armendpoint}{azure_monitor_workspace_resource_id}/providers/"
        f"microsoft.alertsManagement/alertRuleRecommendations?api-version={ALERTS_API}"
    )
    r = send_raw_request(cmd.cli_ctx, "GET", url, headers=headers)
    data = json.loads(r.text)
    return data['value']


def put_rules(
    cmd,
    default_rule_group_id,
    default_rule_group_name,
    mac_region,
    azure_monitor_workspace_resource_id,
    cluster_name,
    default_rules_template,
    url,
    enable_rules,
    i,
):
    from azure.cli.core.util import send_raw_request
    body = json.dumps({
        "id": default_rule_group_id,
        "name": default_rule_group_name,
        "type": "Microsoft.AlertsManagement/prometheusRuleGroups",
        "location": mac_region,
        "properties": {
            "scopes": [
                azure_monitor_workspace_resource_id
            ],
            "enabled": enable_rules,
            "clusterName": cluster_name,
            "interval": "PT1M",
            "rules": default_rules_template[i]["properties"]["rulesArmTemplate"]["resources"][0]["properties"]["rules"]
        }
    })
    for _ in range(3):
        try:
            headers = ['User-Agent=azuremonitormetrics.put_rules.' + default_rule_group_name]
            send_raw_request(cmd.cli_ctx, "PUT", url,
                             body=body, headers=headers)
            break
        except CLIError as e:
            error = e
    else:
        # TODO: where is error defined?
        raise error  # pylint: disable=used-before-assignment


def create_rules(
    cmd,
    cluster_subscription,
    cluster_resource_group_name,
    cluster_name,
    azure_monitor_workspace_resource_id,
    mac_region,
    raw_parameters,
):
    default_rules_template = get_recording_rules_template(cmd, azure_monitor_workspace_resource_id)
    default_rule_group_name = f"NodeRecordingRulesRuleGroup-{cluster_name}"
    default_rule_group_id = (
        f"/subscriptions/{cluster_subscription}/resourceGroups/{cluster_resource_group_name}/providers/"
        f"Microsoft.AlertsManagement/prometheusRuleGroups/{default_rule_group_name}"
    )
    url = f"{cmd.cli_ctx.cloud.endpoints.resource_manager}{default_rule_group_id}?api-version={RULES_API}"
    put_rules(
        cmd,
        default_rule_group_id,
        default_rule_group_name,
        mac_region,
        azure_monitor_workspace_resource_id,
        cluster_name,
        default_rules_template,
        url,
        True,
        0,
    )

    default_rule_group_name = f"KubernetesRecordingRulesRuleGroup-{cluster_name}"
    default_rule_group_id = (
        f"/subscriptions/{cluster_subscription}/resourceGroups/{cluster_resource_group_name}/providers/"
        f"Microsoft.AlertsManagement/prometheusRuleGroups/{default_rule_group_name}"
    )
    url = f"{cmd.cli_ctx.cloud.endpoints.resource_manager}{default_rule_group_id}?api-version={RULES_API}"
    put_rules(
        cmd,
        default_rule_group_id,
        default_rule_group_name,
        mac_region,
        azure_monitor_workspace_resource_id,
        cluster_name,
        default_rules_template,
        url,
        True,
        1,
    )

    enable_windows_recording_rules = raw_parameters.get("enable_windows_recording_rules")

    if enable_windows_recording_rules is not True:
        enable_windows_recording_rules = False

    default_rule_group_name = f"NodeRecordingRulesRuleGroup-Win-{cluster_name}"
    default_rule_group_id = (
        f"/subscriptions/{cluster_subscription}/resourceGroups/{cluster_resource_group_name}/providers/"
        f"Microsoft.AlertsManagement/prometheusRuleGroups/{default_rule_group_name}"
    )
    url = f"{cmd.cli_ctx.cloud.endpoints.resource_manager}{default_rule_group_id}?api-version={RULES_API}"
    put_rules(
        cmd,
        default_rule_group_id,
        default_rule_group_name,
        mac_region,
        azure_monitor_workspace_resource_id,
        cluster_name,
        default_rules_template,
        url,
        enable_windows_recording_rules,
        2,
    )

    default_rule_group_name = f"NodeAndKubernetesRecordingRulesRuleGroup-Win-{cluster_name}"
    default_rule_group_id = (
        f"/subscriptions/{cluster_subscription}/resourceGroups/{cluster_resource_group_name}/providers/"
        f"Microsoft.AlertsManagement/prometheusRuleGroups/{default_rule_group_name}"
    )
    url = f"{cmd.cli_ctx.cloud.endpoints.resource_manager}{default_rule_group_id}?api-version={RULES_API}"
    put_rules(
        cmd,
        default_rule_group_id,
        default_rule_group_name,
        mac_region,
        azure_monitor_workspace_resource_id,
        cluster_name,
        default_rules_template,
        url,
        enable_windows_recording_rules,
        3,
    )
