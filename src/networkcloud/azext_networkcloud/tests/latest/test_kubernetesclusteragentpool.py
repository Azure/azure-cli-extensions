# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Kubernetescluster agentpool tests scenarios
"""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def setup_scenario1(test):
    """Env setup_scenario1"""
    pass


def cleanup_scenario1(test):
    """Env cleanup_scenario1"""
    pass


def call_scenario1(test):
    """# Testcase: scenario1"""
    setup_scenario1(test)
    step_create(test)
    step_update(test)
    step_show(test)
    step_list(test)
    step_delete(test)
    cleanup_scenario1(test)


def setup_scenario2(test):
    """Env setup_scenario2"""
    pass


def cleanup_scenario2(test):
    """Env cleanup_scenario2"""
    pass


def call_scenario2(test):
    """# Testcase: scenario2"""
    setup_scenario2(test)
    step_update_admin_cred(test)
    cleanup_scenario2(test)


def step_create(test, checks=None):
    """Kubernetescluster agentpool create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetescluster agentpool create --name {name} "
        "--kubernetes-cluster-name {clusterName} --resource-group {rg} "
        "--location {location} "
        "--extended-location name={extendedLocation} type={extendedLocationType} "
        "--admin-username={adminUsername} "
        "--ssh-key-values {sshKey} "
        "--count {count} --mode {mode} --vm-sku-name {vmSkuName} "
        "--agent-options {agentOptions} --labels {labels} --taints {taints} "
        "--attached-network-configuration l3-networks={l3Networks} "
        "--availability-zones {availabilityZones} "
        "--upgrade-settings max-surge={maxSurge} "
        "--tags {tags}"
    )


def step_update(test, checks=None):
    """Kubernetescluster agentpool update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetescluster agentpool update --name {name} "
        "--kubernetes-cluster-name {clusterName} --resource-group {rg} "
        "--tags {tagsUpdate}"
    )


def step_show(test, checks=None):
    """Kubernetescluster agentpool show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetescluster agentpool show --name {name} "
        "--kubernetes-cluster-name {clusterName} --resource-group {rg}"
    )


def step_list(test, checks=None):
    """Kubernetescluster agentpool list operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetescluster agentpool list "
        "--kubernetes-cluster-name {clusterName} --resource-group {rg}"
    )


def step_delete(test, checks=None):
    """Kubernetescluster agentpool delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetescluster agentpool delete --name {name} "
        "--kubernetes-cluster-name {clusterName} --resource-group {rg} -y"
    )


def step_update_admin_cred(test, checks=None):
    """Kubernetescluster agentpool update admin credentials operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetescluster agentpool update --name {nameUpdate} --resource-group {rgUpdate} --kubernetes-cluster-name {clusterNameUpdate} --ssh-key-values {sshKeyUpdate}"
    )


class KubernetesClusterAgentPoolScenarioTest(ScenarioTest):
    """Kubernetescluster agentpool scenario tests"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("KUBERNETESCLUSTER_AGENTPOOL", "name"),
                "clusterName": CONFIG.get(
                    "KUBERNETESCLUSTER_AGENTPOOL", "cluster_name"
                ),
                "rg": CONFIG.get("KUBERNETESCLUSTER_AGENTPOOL", "resource_group"),
                "location": CONFIG.get("KUBERNETESCLUSTER_AGENTPOOL", "location"),
                "extendedLocation": CONFIG.get(
                    "KUBERNETESCLUSTER_AGENTPOOL", "extended_location"
                ),
                "extendedLocationType": CONFIG.get("CLUSTER", "extended_location_type"),
                "tags": CONFIG.get("KUBERNETESCLUSTER_AGENTPOOL", "tags"),
                "tagsUpdate": CONFIG.get("KUBERNETESCLUSTER_AGENTPOOL", "tags_update"),
                "adminUsername": CONFIG.get(
                    "KUBERNETESCLUSTER_AGENTPOOL", "admin_username"
                ),
                "sshKey": CONFIG.get("KUBERNETESCLUSTER_AGENTPOOL", "ssh_key_values"),
                "count": CONFIG.get("KUBERNETESCLUSTER_AGENTPOOL", "count"),
                "mode": CONFIG.get("KUBERNETESCLUSTER_AGENTPOOL", "mode"),
                "vmSkuName": CONFIG.get("KUBERNETESCLUSTER_AGENTPOOL", "vm_sku_name"),
                "agentOptions": CONFIG.get(
                    "KUBERNETESCLUSTER_AGENTPOOL", "agent_options"
                ),
                "l3Networks": CONFIG.get("KUBERNETESCLUSTER_AGENTPOOL", "l3_networks"),
                "taints": CONFIG.get("KUBERNETESCLUSTER_AGENTPOOL", "taints"),
                "labels": CONFIG.get("KUBERNETESCLUSTER_AGENTPOOL", "labels"),
                "availabilityZones": CONFIG.get(
                    "KUBERNETESCLUSTER_AGENTPOOL", "availability_zones"
                ),
                "maxSurge": CONFIG.get("KUBERNETESCLUSTER_AGENTPOOL", "max_surge"),
                # scenario 2: update variables
                "rgUpdate": CONFIG.get("KUBERNETESCLUSTER_AGENTPOOL", "rg_update"),
                "clusterNameUpdate": CONFIG.get(
                    "KUBERNETESCLUSTER_AGENTPOOL", "cluster_name_update"
                ),
                "nameUpdate": CONFIG.get("KUBERNETESCLUSTER_AGENTPOOL", "name_update"),
                "sshKeyUpdate": CONFIG.get(
                    "KUBERNETESCLUSTER_AGENTPOOL", "ssh_key_values_update"
                ),
            }
        )

    def test_kubernetesclusteragentpool_scenario(self):
        """test scenario for kubernetes cluster agentpool CRUD operations"""
        call_scenario1(self)

    def test_kubernetesclusteragentpool_scenario2(self):
        """test scenario for kubernetes cluster agentpool administrator credentials update operations"""
        call_scenario2(self)
