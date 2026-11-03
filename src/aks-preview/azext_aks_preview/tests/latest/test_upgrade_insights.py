# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
from io import StringIO
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from azure.cli.core.azclierror import InvalidArgumentValueError, RequiredArgumentMissingError
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from knack.output import format_tsv
from knack.util import CommandResultItem

from azext_aks_preview._client_factory import cf_upgrade_insights
from azext_aks_preview.upgrade_insights import (
    aks_nodepool_upgrade_insights_create,
    aks_nodepool_upgrade_insights_show,
    aks_upgrade_insights_create,
    aks_upgrade_insights_list,
    aks_upgrade_insights_show,
    aks_upgrade_insights_table_format,
    format_upgrade_insight_report,
    validate_upgrade_insights_create,
)
from azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks.models import UpgradeInsight


ISSUE = {
    "issueType": "PDBConstraint",
    "severity": "Blocking",
    "message": "The workload PDB allows no pod disruptions.",
    "impactedResources": [{
        "kind": "Kubernetes", "resourceType": "PodDisruptionBudget",
        "namespace": "payments", "name": "payments-pdb",
    }],
    "recommendedActions": [{
        "title": "Allow pod eviction",
        "details": "Adjust the PDB or scale the workload before upgrading.",
        "documentationLink": "https://example.com/pdb",
    }],
}


def evaluation(status="Passed", issues=None):
    return {
        "status": status,
        "evaluatedAt": "2026-11-03T20:00:00Z",
        "detectedIssues": issues or [],
    }


def insight(upgrade_type="ControlPlaneAndAgentPools", pool_name="pool1"):
    properties = {
        "upgradeType": upgrade_type,
        "provisioningState": "Succeeded",
        "lastEvaluatedAt": "2026-11-03T20:00:00Z",
        "expiresAt": "2026-11-17T20:00:00Z",
    }
    if upgrade_type == "NodeImage":
        properties.update({
            "agentPoolName": pool_name,
            "currentNodeImageVersion": "image-current",
            "targetNodeImageVersion": "image-target",
            "evaluation": evaluation("Failed", [copy.deepcopy(ISSUE)]),
        })
    else:
        properties["targetKubernetesVersion"] = "1.35.1"
        if upgrade_type == "ControlPlaneAndAgentPools":
            properties.update({
                "controlPlane": {
                    "currentKubernetesVersion": "1.34.2",
                    "evaluation": evaluation(),
                },
                "agentPools": [{
                    "agentPoolName": pool_name,
                    "currentKubernetesVersion": "1.34.2",
                    "evaluation": evaluation("Failed", [copy.deepcopy(ISSUE)]),
                }],
            })
        else:
            properties["evaluation"] = evaluation()
            if upgrade_type == "AgentPool":
                properties["agentPoolName"] = pool_name
    return {"name": "stored-insight", "properties": properties}


class UpgradeInsightsCommandsTest(unittest.TestCase):
    def setUp(self):
        self.output = StringIO()
        config = Mock()
        config.get.return_value = None
        self.cmd = SimpleNamespace(cli_ctx=SimpleNamespace(
            data={"safe_params": ["--output"]}, config=config, out_file=self.output,
            invocation=SimpleNamespace(data={"output": "json"}),
            output=Mock(),
        ))
        self.client = Mock()
        self.client.generate.return_value = UpgradeInsight(insight())
        self.client.get.return_value = UpgradeInsight(insight())

    def test_client_factory_uses_upgrade_insights_operations(self):
        with patch("azext_aks_preview._client_factory.get_container_service_client") as factory:
            self.assertIs(cf_upgrade_insights("context"), factory.return_value.upgrade_insights)
            factory.assert_called_once_with("context")

    def test_cluster_create_defaults_to_combined(self):
        result = aks_upgrade_insights_create(self.cmd, self.client, "rg", "cluster", "1.35.1")
        args = self.client.generate.call_args.args
        self.assertEqual(args[:2], ("rg", "cluster"))
        self.assertEqual(args[2].as_dict(), {
            "upgradeType": "ControlPlaneAndAgentPools", "targetKubernetesVersion": "1.35.1",
        })
        self.assertEqual(result["name"], "stored-insight")

    def test_cluster_create_control_plane(self):
        aks_upgrade_insights_create(
            self.cmd, self.client, "rg", "cluster", "1.35.1", upgrade_type="ControlPlane",
        )
        self.assertEqual(self.client.generate.call_args.args[2].as_dict(), {
            "upgradeType": "ControlPlane", "targetKubernetesVersion": "1.35.1",
        })

    def test_cluster_create_rejects_pool_type_before_request(self):
        with self.assertRaises(InvalidArgumentValueError):
            aks_upgrade_insights_create(
                self.cmd, self.client, "rg", "cluster", "1.35.1", upgrade_type="AgentPool",
            )
        self.client.generate.assert_not_called()

    def test_pool_create_defaults_to_agent_pool(self):
        aks_nodepool_upgrade_insights_create(
            self.cmd, self.client, "rg", "cluster", "pool1", target_kubernetes_ver="1.35.1",
        )
        self.assertEqual(self.client.generate.call_args.args[:2], ("rg", "cluster"))
        self.assertEqual(self.client.generate.call_args.args[2].as_dict(), {
            "upgradeType": "AgentPool", "agentPoolName": "pool1", "targetKubernetesVersion": "1.35.1",
        })

    def test_node_image_create_omits_target_for_latest(self):
        aks_nodepool_upgrade_insights_create(
            self.cmd, self.client, "rg", "cluster", "pool1", upgrade_type="NodeImage",
        )
        self.assertEqual(self.client.generate.call_args.args[2].as_dict(), {
            "upgradeType": "NodeImage", "agentPoolName": "pool1",
        })

    def test_node_image_create_passes_explicit_target(self):
        aks_nodepool_upgrade_insights_create(
            self.cmd, self.client, "rg", "cluster", "pool1",
            upgrade_type="NodeImage", target_node_image_ver="image-target",
        )
        self.assertEqual(self.client.generate.call_args.args[2].as_dict(), {
            "upgradeType": "NodeImage", "agentPoolName": "pool1", "targetNodeImageVersion": "image-target",
        })

    def test_invalid_pool_targets_do_not_send_requests(self):
        cases = [
            ({}, RequiredArgumentMissingError),
            ({"target_kubernetes_ver": ""}, InvalidArgumentValueError),
            ({"target_kubernetes_ver": " "}, InvalidArgumentValueError),
            ({"target_kubernetes_ver": "1.35.1", "target_node_image_ver": "image"}, InvalidArgumentValueError),
            ({"upgrade_type": "NodeImage", "target_kubernetes_ver": "1.35.1"}, InvalidArgumentValueError),
            ({"upgrade_type": "NodeImage", "target_node_image_ver": ""}, InvalidArgumentValueError),
            ({"upgrade_type": "ControlPlane", "target_kubernetes_ver": "1.35.1"}, InvalidArgumentValueError),
        ]
        for kwargs, error_type in cases:
            with self.subTest(kwargs=kwargs), self.assertRaises(error_type):
                aks_nodepool_upgrade_insights_create(self.cmd, self.client, "rg", "cluster", "pool1", **kwargs)
        self.client.generate.assert_not_called()

    def test_argument_validator_checks_targets(self):
        with self.assertRaises(RequiredArgumentMissingError):
            validate_upgrade_insights_create(SimpleNamespace(upgrade_type="AgentPool"))
        validate_upgrade_insights_create(SimpleNamespace(upgrade_type="NodeImage"))

    def test_show_uses_server_name_without_regenerating(self):
        result = aks_upgrade_insights_show(self.cmd, self.client, "rg", "cluster", "stored-insight")
        self.client.get.assert_called_once_with("rg", "cluster", "stored-insight")
        self.client.generate.assert_not_called()
        self.assertEqual(result["name"], "stored-insight")

    def test_pool_show_accepts_agent_pool_and_node_image(self):
        for upgrade_type in ("AgentPool", "NodeImage"):
            with self.subTest(upgrade_type=upgrade_type):
                self.client.get.return_value = UpgradeInsight(insight(upgrade_type))
                result = aks_nodepool_upgrade_insights_show(
                    self.cmd, self.client, "rg", "cluster", "POOL1", "stored-insight",
                )
                self.assertEqual(result["properties"]["agentPoolName"], "pool1")
        self.client.generate.assert_not_called()

    def test_pool_show_rejects_other_pools_and_combined_insights(self):
        for data in (insight("AgentPool", "otherpool"), insight(), insight("ControlPlane")):
            with self.subTest(data=data):
                self.client.get.return_value = UpgradeInsight(data)
                with self.assertRaisesRegex(InvalidArgumentValueError, "not a single-pool insight"):
                    aks_nodepool_upgrade_insights_show(
                        self.cmd, self.client, "rg", "cluster", "pool1", "stored-insight",
                    )
        self.assertEqual(self.output.getvalue(), "")

    def test_list_consumes_every_page_and_keeps_all_scopes(self):
        self.client.list.return_value = iter([
            UpgradeInsight(insight()), UpgradeInsight(insight("AgentPool")), UpgradeInsight(insight("NodeImage")),
        ])
        result = aks_upgrade_insights_list(self.cmd, self.client, "rg", "cluster")
        self.assertEqual([item["properties"]["upgradeType"] for item in result], [
            "ControlPlaneAndAgentPools", "AgentPool", "NodeImage",
        ])
        self.client.list.assert_called_once_with("rg", "cluster")
        self.client.generate.assert_not_called()

    def test_service_errors_are_propagated(self):
        for error in (ResourceNotFoundError("expired"), HttpResponseError("forbidden")):
            with self.subTest(error=error):
                self.client.get.side_effect = error
                with self.assertRaises(type(error)):
                    aks_upgrade_insights_show(self.cmd, self.client, "rg", "cluster", "stored-insight")
        self.assertEqual(self.output.getvalue(), "")

    def test_default_output_is_nested_report_without_json_trailer(self):
        self.cmd.cli_ctx.data["safe_params"] = []
        result = aks_upgrade_insights_create(self.cmd, self.client, "rg", "cluster", "1.35.1")
        self.assertIsInstance(result, str)
        self.assertEqual(self.cmd.cli_ctx.invocation.data["output"], "tsv")
        self.assertEqual(self.output.getvalue(), "")
        output = format_tsv(CommandResultItem(result))
        self.assertIn("Upgrade readiness: FAILED", output)
        self.assertIn("  Agent pool: pool1 - FAILED\n", output)
        self.assertIn("    BLOCKING: PDBConstraint\n", output)
        self.assertIn("      Issue: The workload PDB allows no pod disruptions.", output)
        self.assertIn("payments/payments-pdb", output)
        self.assertIn("Recommended action: Allow pod eviction", output)
        self.assertIn("Documentation: https://example.com/pdb", output)
        self.assertNotIn('"properties"', output)
        self.assertNotIn("\nnull", output)

    def test_explicit_output_and_query_preserve_full_results(self):
        for option in ("--output", "-o", "--query"):
            with self.subTest(option=option):
                self.cmd.cli_ctx.data["safe_params"] = [option]
                result = aks_upgrade_insights_show(self.cmd, self.client, "rg", "cluster", "stored-insight")
                self.assertEqual(result["properties"]["agentPools"][0]["evaluation"]["detectedIssues"], [ISSUE])
                self.assertEqual(self.output.getvalue(), "")

    def test_configured_output_is_respected(self):
        self.cmd.cli_ctx.data["safe_params"] = []
        self.cmd.cli_ctx.config.get.return_value = "json"
        result = aks_upgrade_insights_show(self.cmd, self.client, "rg", "cluster", "stored-insight")
        self.assertIsInstance(result, dict)
        self.assertEqual(self.output.getvalue(), "")

    def test_empty_list_reports_no_stored_insights(self):
        self.cmd.cli_ctx.data["safe_params"] = []
        self.client.list.return_value = []
        result = aks_upgrade_insights_list(self.cmd, self.client, "rg", "cluster")
        self.assertEqual(result, "No stored upgrade insights for cluster: cluster")
        self.assertEqual(self.output.getvalue(), "")

    def test_list_report_includes_issue_messages_and_insight_names(self):
        self.cmd.cli_ctx.data["safe_params"] = []
        self.client.list.return_value = [UpgradeInsight(insight())]
        output = aks_upgrade_insights_list(self.cmd, self.client, "rg", "cluster")
        self.assertIn("Insight: stored-insight", output)
        self.assertIn("    BLOCKING: PDBConstraint", output)
        self.assertIn("      Issue: The workload PDB allows no pod disruptions.", output)


class UpgradeInsightsReportTest(unittest.TestCase):
    def test_issues_are_nested_under_only_the_affected_scope(self):
        report = format_upgrade_insight_report(insight(), "cluster")
        control_plane, pool = report.split("  Agent pool: pool1")
        self.assertIn("  Control plane - PASSED\n    Current Kubernetes version:", control_plane)
        self.assertNotIn("BLOCKING", control_plane)
        self.assertIn("\n    BLOCKING: PDBConstraint\n      Issue:", pool)

    def test_multiple_pool_issues_remain_under_their_own_scope(self):
        data = insight()
        warning = {"severity": "Warning", "issueType": "QuotaExceeded", "message": "Check quota for pool2."}
        data["properties"]["agentPools"].append({
            "agentPoolName": "pool2", "evaluation": evaluation("Warning", [warning]),
        })
        report = format_upgrade_insight_report(data, "cluster")
        pool1, pool2 = report.split("  Agent pool: pool2")
        self.assertIn("PDBConstraint", pool1)
        self.assertNotIn("QuotaExceeded", pool1)
        self.assertIn("    WARNING: QuotaExceeded\n      Issue: Check quota for pool2.", pool2)
        self.assertNotIn("PDBConstraint", pool2)

    def test_node_image_report_shows_resolved_target_and_current_image(self):
        report = format_upgrade_insight_report(insight("NodeImage"), "cluster")
        self.assertIn("Target node image version: image-target", report)
        self.assertIn("  Agent pool: pool1 (node image) - FAILED", report)
        self.assertIn("    Current node image version: image-current", report)

    def test_control_plane_issues_are_nested_under_control_plane(self):
        data = insight("ControlPlane")
        data["properties"]["evaluation"] = evaluation("Failed", [ISSUE])
        report = format_upgrade_insight_report(data, "cluster")
        self.assertIn("  Control plane - FAILED", report)
        self.assertIn("\n    BLOCKING: PDBConstraint\n      Issue:", report)
        self.assertNotIn("Agent pool", report)

    def test_warning_and_passed_rollup(self):
        data = insight()
        data["properties"]["agentPools"][0]["evaluation"] = evaluation("Warning")
        self.assertTrue(format_upgrade_insight_report(data, "cluster").startswith("Upgrade readiness: WARNING"))
        data["properties"]["agentPools"][0]["evaluation"] = evaluation()
        self.assertTrue(format_upgrade_insight_report(data, "cluster").startswith("Upgrade readiness: PASSED"))

    def test_missing_evaluation_never_reports_passed_or_no_issues(self):
        data = insight("AgentPool")
        del data["properties"]["evaluation"]
        report = format_upgrade_insight_report(data, "cluster")
        self.assertIn("Upgrade readiness: NOT EVALUATED", report)
        self.assertIn("No issue details were returned.", report)
        self.assertNotIn("PASSED", report)
        self.assertNotIn("No issues detected.", report)

    def test_failed_or_canceled_evaluation_never_reports_overall_passed(self):
        for state in ("Failed", "Canceled"):
            with self.subTest(state=state):
                data = insight("ControlPlane")
                data["properties"]["provisioningState"] = state
                report = format_upgrade_insight_report(data, "cluster")
                self.assertTrue(report.startswith("Upgrade readiness: NOT EVALUATED"))
                self.assertIn(f"Provisioning state: {state}", report)

    def test_wrapped_issue_lines_keep_scope_indentation(self):
        data = insight()
        data["properties"]["agentPools"][0]["evaluation"]["detectedIssues"][0]["message"] = "A long issue message. " * 20
        report = format_upgrade_insight_report(data, "cluster")
        issue = report.split("      Issue: ", 1)[1].split("      Affected resource:", 1)[0]
        for line in issue.splitlines()[1:]:
            self.assertTrue(line.startswith("        "), line)

    def test_arm_resources_are_shown_by_resource_id(self):
        data = insight()
        data["properties"]["agentPools"][0]["evaluation"]["detectedIssues"][0]["impactedResources"] = [{
            "kind": "Arm", "resourceType": "Microsoft.Network/virtualNetworks/subnets",
            "resourceId": "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Network/virtualNetworks/vnet/subnets/subnet",
        }]
        self.assertIn("/virtualNetworks/vnet/subnets/subnet", format_upgrade_insight_report(data, "cluster"))

    def test_table_output_retains_issue_messages_and_scope(self):
        rows = aks_upgrade_insights_table_format(insight())
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["Scope"], "ControlPlane")
        self.assertEqual(rows[0]["Status"], "Passed")
        self.assertEqual(rows[1]["Pool"], "pool1")
        self.assertEqual(rows[1]["Issue"], ISSUE["message"])
        self.assertEqual(rows[1]["Severity"], "Blocking")
        self.assertEqual(aks_upgrade_insights_table_format([]), [])
