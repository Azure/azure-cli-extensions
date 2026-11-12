# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
from uuid import uuid4

from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest, live_only


_LOCATION = os.environ.get("WORKLOAD_MANAGER_TEST_LOCATION")
_CLUSTER_ID = os.environ.get("WORKLOAD_MANAGER_TEST_CLUSTER_ID")
_EXECUTION_SUBNET_ID = os.environ.get("WORKLOAD_MANAGER_TEST_EXECUTION_SUBNET_ID")
_LINK_SUBNET_ID = os.environ.get("WORKLOAD_MANAGER_TEST_LINK_SUBNET_ID")


@live_only()
@unittest.skipUnless(
    _LOCATION,
    "Set WORKLOAD_MANAGER_TEST_LOCATION to a supported region in a preview-enabled subscription "
    "with provider registrations, service permissions and downstream capacity configured.",
)
class WorkloadSpaceUpScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix="cli-ws-managed-", location=_LOCATION)
    def test_workload_space_up_managed(self, resource_group):
        self.kwargs.update({
            "rg": resource_group,
            "space": f"ws{uuid4().hex[:12]}",
            "location": _LOCATION,
        })
        self.cmd(
            "workload-manager workload-space up -g {rg} -n {space} -l {location}",
            checks=self.check("properties.provisioningState", "Succeeded"),
        )
        self._assert_provisioned_composition("Managed")

    @unittest.skipUnless(
        _CLUSTER_ID and _EXECUTION_SUBNET_ID and _LINK_SUBNET_ID,
        "Set WORKLOAD_MANAGER_TEST_CLUSTER_ID, WORKLOAD_MANAGER_TEST_EXECUTION_SUBNET_ID and "
        "WORKLOAD_MANAGER_TEST_LINK_SUBNET_ID to ready resources satisfying the referenced-network prerequisites.",
    )
    @ResourceGroupPreparer(name_prefix="cli-ws-referenced-", location=_LOCATION)
    def test_workload_space_up_referenced(self, resource_group):
        self.kwargs.update({
            "rg": resource_group,
            "space": f"ws{uuid4().hex[:12]}",
            "location": _LOCATION,
            "cluster": _CLUSTER_ID,
            "execution_subnet": _EXECUTION_SUBNET_ID,
            "link_subnet": _LINK_SUBNET_ID,
        })
        self.cmd(
            "workload-manager workload-space up -g {rg} -n {space} -l {location} "
            "--managed-cluster-resource-id {cluster} --workload-execution-subnet-id {execution_subnet} "
            "--runtime-link-subnet-id {link_subnet}",
            checks=self.check("properties.provisioningState", "Succeeded"),
        )
        self._assert_provisioned_composition("Referenced")
        binding = self.cmd(
            "workload-manager workload-space runtime-binding show -g {rg} --space-name {space} -n aks",
        ).get_output_in_json()
        self.assertEqual(binding["properties"]["resourceId"].lower(), _CLUSTER_ID.lower())

    def _assert_provisioned_composition(self, aks_mode):
        deployment = self.cmd(
            "deployment group show -g {rg} -n {space}",
            checks=self.check("properties.provisioningState", "Succeeded"),
        ).get_output_in_json()
        space = self.cmd(
            "workload-manager workload-space show -g {rg} -n {space}",
            checks=self.check("properties.provisioningState", "Succeeded"),
        ).get_output_in_json()
        self.assertEqual(
            deployment["properties"]["outputs"]["workloadSpaceId"]["value"].lower(),
            space["id"].lower(),
        )
        for name, mode in (("aks", aks_mode), ("aci", "Managed")):
            self.cmd(
                f"workload-manager workload-space runtime-binding show -g {{rg}} --space-name {{space}} -n {name}",
                checks=[
                    self.check("properties.provisioningState", "Succeeded"),
                    self.check("properties.provisioningMode", mode),
                ],
            )
        link = self.cmd(
            "workload-manager workload-space runtime-link show -g {rg} --space-name {space} -n link",
            checks=self.check("properties.provisioningState", "Succeeded"),
        ).get_output_in_json()
        for field, name in (("orchestratorBindingResourceId", "aks"), ("executionBindingResourceId", "aci")):
            self.assertEqual(
                link["properties"][field].lower(), f"{space['id']}/runtimeBindings/{name}".lower(),
            )
        for name, kind in (("agent-sandbox", "AgentSandbox"), ("pod-snapshot-restore", "PodSnapshotRestore")):
            self.cmd(
                f"workload-manager workload-space capability show -g {{rg}} --space-name {{space}} -n {name}",
                checks=[
                    self.check("properties.provisioningState", "Succeeded"),
                    self.check("kind", kind),
                ],
            )
