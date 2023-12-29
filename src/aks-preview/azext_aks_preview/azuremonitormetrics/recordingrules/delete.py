# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azext_aks_preview.azuremonitormetrics.constants import RULES_API


def delete_rule(cmd, cluster_subscription, cluster_resource_group_name, default_rule_group_name):
    from azure.cli.core.util import send_raw_request
    default_rule_group_id = (
        f"/subscriptions/{cluster_subscription}/resourceGroups/{cluster_resource_group_name}/providers/"
        f"Microsoft.AlertsManagement/prometheusRuleGroups/{default_rule_group_name}"
    )
    headers = ['User-Agent=azuremonitormetrics.delete_rule.' + default_rule_group_name]
    url = f"{cmd.cli_ctx.cloud.endpoints.resource_manager}{default_rule_group_id}?api-version={RULES_API}"
    send_raw_request(cmd.cli_ctx, "DELETE", url, headers=headers)


def delete_rules(cmd, cluster_subscription, cluster_resource_group_name, cluster_name):
    delete_rule(
        cmd,
        cluster_subscription,
        cluster_resource_group_name,
        f"NodeRecordingRulesRuleGroup-{cluster_name}",
    )
    delete_rule(
        cmd,
        cluster_subscription,
        cluster_resource_group_name,
        f"KubernetesRecordingRulesRuleGroup-{cluster_name}",
    )
    delete_rule(
        cmd,
        cluster_subscription,
        cluster_resource_group_name,
        f"NodeRecordingRulesRuleGroup-Win-{cluster_name}",
    )
    delete_rule(
        cmd,
        cluster_subscription,
        cluster_resource_group_name,
        f"NodeAndKubernetesRecordingRulesRuleGroup-Win-{cluster_name}",
    )
