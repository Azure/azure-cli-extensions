# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import io
import itertools
import unittest
from types import SimpleNamespace
from unittest.mock import ANY, Mock, patch

from azure.core.exceptions import HttpResponseError
from azure.cli.core import MainCommandsLoader, get_default_cli
from azure.cli.core.azclierror import InvalidArgumentValueError, RequiredArgumentMissingError
from azure.cli.core.profiles import ResourceType, get_sdk

from azext_workload_manager import WorkloadManagerCommandsLoader
from azext_workload_manager._workload_space_up import workload_space_up


class WorkloadSpaceUpTest(unittest.TestCase):

    _SUBSCRIPTION = "11111111-1111-1111-1111-111111111111"
    _CLUSTER_ID = (
        f"/subscriptions/{_SUBSCRIPTION}/resourceGroups/cluster-rg/"
        "providers/Microsoft.ContainerService/managedClusters/cluster"
    )
    _VNET_ID = (
        f"/subscriptions/{_SUBSCRIPTION}/resourceGroups/network-rg/"
        "providers/Microsoft.Network/virtualNetworks/vnet"
    )
    _REFERENCES = {
        "managed_cluster_resource_id": _CLUSTER_ID,
        "workload_execution_subnet_id": f"{_VNET_ID}/subnets/aci",
        "runtime_link_subnet_id": f"{_VNET_ID}/subnets/link",
    }

    def setUp(self):
        self.cmd = Mock(cli_ctx=get_default_cli())
        self.client = Mock()
        self.poller = self.client.deployments.begin_create_or_update.return_value
        factory = patch(
            "azext_workload_manager._workload_space_up.get_mgmt_service_client", return_value=self.client
        )
        self.factory = factory.start()
        self.addCleanup(factory.stop)
        subscription = patch(
            "azext_workload_manager._workload_space_up.get_subscription_id", return_value=self._SUBSCRIPTION
        )
        subscription.start()
        self.addCleanup(subscription.stop)

    def _invoke(self, **overrides):
        arguments = {
            "resource_group_name": "workload-rg",
            "space_name": "my-space",
            "location": "eastus2",
            **overrides,
        }
        return workload_space_up(self.cmd, **arguments)

    def _deployment(self):
        return self.client.deployments.begin_create_or_update.call_args.kwargs["parameters"].serialize()

    @staticmethod
    def _load_workload_commands(main_loader, args):
        loader = WorkloadManagerCommandsLoader(cli_ctx=main_loader.cli_ctx)
        main_loader.command_table = loader.load_command_table(args)
        main_loader.cmd_to_loader_map = {name: [loader] for name in main_loader.command_table}
        return main_loader.command_table

    def test_managed_composition_submits_one_incremental_deployment(self):
        result = self._invoke(tags={"environment": "test", "literal": "[not-an-expression]"})

        self.assertIs(result, self.poller)
        self.client.deployments.begin_create_or_update.assert_called_once()
        call = self.client.deployments.begin_create_or_update.call_args.kwargs
        self.assertEqual(call["resource_group_name"], "workload-rg")
        self.assertEqual(call["deployment_name"], "my-space")
        properties = self._deployment()["properties"]
        self.assertEqual(properties["mode"], "Incremental")
        self.assertEqual(properties["parameters"], {
            "workloadSpaceName": {"value": "my-space"},
            "location": {"value": "eastus2"},
            "tags": {"value": {"environment": "test", "literal": "[not-an-expression]"}},
        })
        resources = properties["template"]["resources"]
        self.assertEqual(len(resources), 6)
        self.assertEqual(resources[0]["location"], "[parameters('location')]")
        self.assertEqual(resources[0]["tags"], "[parameters('tags')]")
        self.assertEqual(resources[1]["kind"], "Kubernetes")
        self.assertEqual(resources[1]["properties"], {
            "provisioningMode": "Managed", "managedProfile": {"offering": "Standard"},
        })
        self.assertEqual(resources[2]["kind"], "ServerlessContainers")
        self.assertEqual(resources[2]["properties"], {
            "provisioningMode": "Managed", "managedProfile": {"provider": "ACI"},
        })
        self.assertNotIn("subnetResourceId", resources[3]["properties"])
        self.assertEqual(
            [resource["kind"] for resource in resources[4:]],
            ["AgentSandbox", "PodSnapshotRestore"],
        )
        for resource in resources[4:]:
            self.assertEqual(resource["properties"], {"versionPolicy": "ServiceManaged"})
        for resource in resources[1:]:
            self.assertNotIn("location", resource)
            self.assertNotIn("tags", resource)

    def test_referenced_composition_routes_ids_to_the_correct_resources(self):
        self._invoke(**self._REFERENCES)

        resources = self._deployment()["properties"]["template"]["resources"]
        self.assertEqual(resources[1]["properties"], {
            "provisioningMode": "Referenced",
            "resourceId": self._CLUSTER_ID,
        })
        self.assertEqual(resources[2]["properties"], {
            "provisioningMode": "Managed",
            "managedProfile": {"provider": "ACI"},
            "networkProfile": {"subnetResourceId": self._REFERENCES["workload_execution_subnet_id"]},
        })
        self.assertEqual(resources[3]["properties"], {
            "orchestratorBindingResourceId":
                "[resourceId('Microsoft.Compute/workloadSpaces/runtimeBindings', "
                "parameters('workloadSpaceName'), 'aks')]",
            "executionBindingResourceId":
                "[resourceId('Microsoft.Compute/workloadSpaces/runtimeBindings', "
                "parameters('workloadSpaceName'), 'aci')]",
            "subnetResourceId": self._REFERENCES["runtime_link_subnet_id"],
        })
        self.assertEqual(len(resources), 6)

    def test_every_mutation_depends_on_the_previous_resource_in_both_modes(self):
        for references in ({}, self._REFERENCES):
            with self.subTest(referenced=bool(references)):
                self._invoke(**references)
                template = self._deployment()["properties"]["template"]
                resources = template["resources"]
                predecessor = template["outputs"]["workloadSpaceId"]["value"]
                self.assertNotIn("dependsOn", resources[0])
                for resource, child_name in zip(
                        resources[1:], ("aks", "aci", "link", "agent-sandbox", "pod-snapshot-restore")):
                    self.assertEqual(resource["dependsOn"], [predecessor])
                    self.assertEqual(
                        resource["name"], f"[format('{{0}}/{child_name}', parameters('workloadSpaceName'))]"
                    )
                    predecessor = (
                        f"[resourceId('{resource['type']}', parameters('workloadSpaceName'), '{child_name}')]"
                    )

    def test_partial_or_empty_reference_arguments_fail_before_submission(self):
        for count in (1, 2):
            for keys in itertools.combinations(self._REFERENCES, count):
                with self.subTest(keys=keys):
                    with self.assertRaisesRegex(RequiredArgumentMissingError, "together"):
                        self._invoke(**{key: self._REFERENCES[key] for key in keys})
        for key in self._REFERENCES:
            with self.subTest(empty=key):
                with self.assertRaises(RequiredArgumentMissingError):
                    self._invoke(**{**self._REFERENCES, key: ""})
        self.factory.assert_not_called()

    def test_wrong_resource_types_and_malformed_ids_fail_before_submission(self):
        invalid_values = (
            ("managed_cluster_resource_id", "cluster"),
            ("managed_cluster_resource_id", self._VNET_ID),
            ("managed_cluster_resource_id", f"{self._CLUSTER_ID}/agentPools/pool"),
            ("workload_execution_subnet_id", self._VNET_ID),
            ("runtime_link_subnet_id", self._CLUSTER_ID),
            ("runtime_link_subnet_id", f"{self._VNET_ID}/subnets/link/extra/value"),
        )
        for key, value in invalid_values:
            with self.subTest(key=key, value=value):
                with self.assertRaisesRegex(InvalidArgumentValueError, "full"):
                    self._invoke(**{**self._REFERENCES, key: value})
        self.factory.assert_not_called()

    def test_cross_subscription_references_fail_before_submission(self):
        for key, value in self._REFERENCES.items():
            with self.subTest(key=key):
                foreign_id = value.replace(self._SUBSCRIPTION, "22222222-2222-2222-2222-222222222222")
                with self.assertRaisesRegex(InvalidArgumentValueError, "selected subscription"):
                    self._invoke(**{**self._REFERENCES, key: foreign_id})
        self.factory.assert_not_called()

    def test_subnets_must_be_distinct_and_in_the_same_vnet(self):
        for subnet, message in (
                (self._REFERENCES["workload_execution_subnet_id"].upper(), "distinct"),
                (f"{self._VNET_ID}-other/subnets/link", "same VNet")):
            with self.subTest(subnet=subnet):
                with self.assertRaisesRegex(InvalidArgumentValueError, message):
                    self._invoke(**{**self._REFERENCES, "runtime_link_subnet_id": subnet})
        self.factory.assert_not_called()

    def test_reference_id_matching_is_case_insensitive(self):
        self._invoke(**{key: value.upper() for key, value in self._REFERENCES.items()})

        resources = self._deployment()["properties"]["template"]["resources"]
        self.assertEqual(resources[1]["properties"]["resourceId"], self._CLUSTER_ID.upper())

    def test_invalid_space_and_deployment_names_fail_before_submission(self):
        for name in ("", "-space", ".space", "a" * 65, "space/child", "space'"):
            with self.subTest(space_name=name):
                with self.assertRaisesRegex(InvalidArgumentValueError, "--space-name"):
                    self._invoke(space_name=name)
        for name in ("a" * 65, "deployment/name", "deployment'"):
            with self.subTest(deployment_name=name):
                with self.assertRaisesRegex(InvalidArgumentValueError, "--deployment-name"):
                    self._invoke(deployment_name=name)
        self.factory.assert_not_called()

    def test_reruns_keep_resource_ids_and_support_maximum_length_space_names(self):
        self._invoke(space_name="a" * 64)
        first = self._deployment()
        self._invoke(space_name="a" * 64)

        self.assertEqual(first, self._deployment())
        self.assertEqual(
            self.client.deployments.begin_create_or_update.call_args.kwargs["deployment_name"],
            "a" * 64,
        )

    def test_no_wait_submits_the_whole_template_with_polling_disabled(self):
        result = self._invoke(no_wait=True, deployment_name="custom-deployment")

        call = self.client.deployments.begin_create_or_update.call_args.kwargs
        self.assertEqual(call["deployment_name"], "custom-deployment")
        self.assertIs(call["polling"], False)
        self.assertEqual(len(self._deployment()["properties"]["template"]["resources"]), 6)
        self.poller.result.assert_not_called()
        self.assertIs(result, self.poller)

    def test_submission_errors_propagate_without_retry_or_rollback(self):
        self.client.deployments.begin_create_or_update.side_effect = HttpResponseError("deployment rejected")

        with self.assertRaisesRegex(HttpResponseError, "deployment rejected"):
            self._invoke()
        self.client.deployments.begin_create_or_update.assert_called_once()
        self.client.deployments.begin_delete.assert_not_called()

    def test_cli_versions_before_the_deployment_sdk_split_use_resource_client(self):
        deployment_type = getattr(ResourceType, "MGMT_RESOURCE_DEPLOYMENTS", ResourceType.MGMT_RESOURCE_RESOURCES)
        models = get_sdk(self.cmd.cli_ctx, deployment_type, "Deployment", "DeploymentProperties", mod="models")
        old_resource_type = SimpleNamespace(MGMT_RESOURCE_RESOURCES=ResourceType.MGMT_RESOURCE_RESOURCES)
        with patch("azext_workload_manager._workload_space_up.ResourceType", old_resource_type), patch(
                "azext_workload_manager._workload_space_up.get_sdk", return_value=models) as model_factory:
            self._invoke()

        model_factory.assert_called_once_with(
            self.cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES, "Deployment", "DeploymentProperties", mod="models"
        )
        self.factory.assert_called_once_with(self.cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)

    def test_cli_arguments_submit_the_composition_with_a_stable_deployment_name(self):
        self.client.deployments.begin_create_or_update.return_value = {"properties": {"provisioningState": "Accepted"}}
        cases = (
            ["-n", "my-space"],
            ["--space-name", "my-space",
             "--managed-cluster-resource-id", self._CLUSTER_ID,
             "--workload-execution-subnet-id", self._REFERENCES["workload_execution_subnet_id"],
             "--runtime-link-subnet-id", self._REFERENCES["runtime_link_subnet_id"]],
            ["--name", "my-space",
             "--managed-cluster-id", self._CLUSTER_ID,
             "--execution-subnet-id", self._REFERENCES["workload_execution_subnet_id"],
             "--runtime-link-subnet-id", self._REFERENCES["runtime_link_subnet_id"]],
        )
        with patch.object(MainCommandsLoader, "load_command_table", self._load_workload_commands), patch(
                "socket.socket.connect", side_effect=AssertionError("Unexpected network request")):
            for options in cases:
                with self.subTest(options=options):
                    self.client.reset_mock()
                    cli = get_default_cli()
                    arguments = [
                        "workload-manager", "workload-space", "up", "-g", "workload-rg", "-l", "eastus2",
                        "--tags", "environment=test", "--no-wait", "--only-show-errors", "-o", "none",
                    ] + options
                    self.assertEqual(cli.invoke(arguments, out_file=io.StringIO()), 0)
                    self.client.deployments.begin_create_or_update.assert_called_once()
                    call = self.client.deployments.begin_create_or_update.call_args.kwargs
                    self.assertEqual(call["deployment_name"], "my-space")
                    self.assertEqual(call["resource_group_name"], "workload-rg")
                    self.assertIs(call["polling"], False)
                    properties = self._deployment()["properties"]
                    self.assertEqual(properties["parameters"]["tags"]["value"], {"environment": "test"})
                    resources = properties["template"]["resources"]
                    self.assertEqual(len(resources), 6)
                    self.assertEqual(
                        resources[1]["properties"]["provisioningMode"],
                        "Referenced" if len(options) > 2 else "Managed",
                    )

    def test_cli_location_uses_explicit_configured_or_resource_group_value(self):
        self.client.deployments.begin_create_or_update.return_value = {"properties": {"provisioningState": "Accepted"}}
        resource_client = Mock()
        resource_client.resource_groups.get.return_value = SimpleNamespace(name="workload-rg", location="westus2")
        cases = (
            ([], None, "westus2"),
            ([], "centralus", "centralus"),
            (["-l", "eastus2"], "centralus", "eastus2"),
        )
        with patch.object(MainCommandsLoader, "load_command_table", self._load_workload_commands), patch(
                "azure.cli.core.commands.client_factory.get_mgmt_service_client",
                return_value=resource_client) as resource_factory, patch(
                "socket.socket.connect", side_effect=AssertionError("Unexpected network request")):
            for options, configured_location, expected_location in cases:
                with self.subTest(options=options, configured_location=configured_location):
                    self.client.reset_mock()
                    resource_client.reset_mock()
                    resource_factory.reset_mock()
                    cli = get_default_cli()
                    read_config = cli.config.get

                    def get_config(section, option, *args, **kwargs):
                        if section == cli.config.defaults_section_name and option == "location":
                            return configured_location
                        return read_config(section, option, *args, **kwargs)

                    arguments = [
                        "workload-manager", "workload-space", "up", "-g", "workload-rg", "-n", "my-space",
                        "--no-wait", "--only-show-errors", "-o", "none",
                    ] + options
                    with patch.object(cli.config, "get", side_effect=get_config):
                        self.assertEqual(cli.invoke(arguments, out_file=io.StringIO()), 0)
                    self.client.deployments.begin_create_or_update.assert_called_once()
                    self.assertEqual(
                        self._deployment()["properties"]["parameters"]["location"]["value"],
                        expected_location,
                    )
                    if not options and configured_location is None:
                        resource_client.resource_groups.get.assert_called_once_with("workload-rg")
                        resource_factory.assert_called_once_with(ANY, ResourceType.MGMT_RESOURCE_RESOURCES)
                    else:
                        resource_client.resource_groups.get.assert_not_called()
                        resource_factory.assert_not_called()


if __name__ == "__main__":
    unittest.main()
