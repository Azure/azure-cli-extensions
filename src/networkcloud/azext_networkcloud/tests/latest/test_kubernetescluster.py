# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Kubernetescluster tests scenarios
"""

from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

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
    step_list_subscription(test)
    step_restart_node(test)
    step_delete(test)
    cleanup_scenario1(test)


def setup_scenario2(test):
    """Env setup_scenario1"""
    pass


def cleanup_scenario2(test):
    """Env cleanup_scenario1"""
    pass


def call_scenario2(test):
    """# Testcase: scenario2"""
    setup_scenario2(test)
    step_update_admin_cred(test)
    step_update_control_plane_ssh_key(test)
    cleanup_scenario2(test)


def step_create(test, checks=None):
    """Kubernetescluster create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetescluster create --name {name} --resource-group {rg} "
        "--location {location} --extended-location name={extendedLocation} type={extendedLocationType} "
        "--kubernetes-version {kubernetesVersion} "
        "--admin-username {adminUsername} --ssh-key-values {sshKey} "
        "--aad-configuration admin-group-object-ids={adminGroupObjectIds} "
        "--initial-agent-pool-configurations {initialNodeConfiguration} "
        "--control-plane-node-configuration count={count} vmSkuName={vmSkuName} adminUsername={cpAdminUsername} sshKeyValues={cpSshKeyList} "
        "--network-configuration cloud-services-network-id={csnId} cni-network-id={cniId} pod-cidrs={podCidrs} service-cidrs={serviceCidrs} dns-service-ip={dnsServiceIp} "
        "bgp-service-load-balancer-configuration.fabric-peering-enabled={fabricPeeringEnabled} "
        "bgp-service-load-balancer-configuration.ip-address-pools={ipAddressPools} "
        "--tags {tags}"
    )


def step_update(test, checks=None):
    """Kubernetescluster update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetescluster update --name {name} --kubernetes-version {kubernetesVersion} "
        "--control-plane-node-configuration count={countUpdate} --resource-group {rg} --tags {tagsUpdate}"
    )


def step_show(test, checks=None):
    """Kubernetescluster show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetescluster show --name {name} --resource-group {rg}"
    )


def step_list(test, checks=None):
    """Kubernetescluster list operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud kubernetescluster list ")


def step_list_subscription(test, checks=None):
    """Kubernetescluster list in subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud kubernetescluster list --resource-group {rg}")


def step_restart_node(test, checks=None):
    """Kubernetescluster restart node operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetescluster restart-node --node-name {nodeName} "
        "--kubernetes-cluster-name {kubernetesClusterName} --resource-group {resourceGroup}"
    )


def step_delete(test, checks=None):
    """Kubernetescluster delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetescluster delete --name {name} --resource-group {rg} -y"
    )


def step_update_admin_cred(test, checks=None):
    """Kubernetescluster update admin credentials operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetescluster update --name {nameUpdate} --resource-group {rgUpdate} --ssh-key-values {sshKeyUpdate}"
    )


def step_update_control_plane_ssh_key(test, checks=None):
    """Kubernetescluster update control plane admin credentials operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetescluster update --name {nameUpdate} --resource-group {rgUpdate} --control-plane-node-configuration ssh-key-values={cpSshKeyListUpdate}"
    )


class KubernetesClusterScenarioTest(ScenarioTest):
    """Kubernetescluster scenario tests"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": self.create_random_name(prefix="cli-test-naks-", length=24),
                "location": CONFIG.get("KUBERNETESCLUSTER", "location"),
                "extendedLocation": CONFIG.get(
                    "KUBERNETESCLUSTER", "extended_location"
                ),
                "extendedLocationType": CONFIG.get("CLUSTER", "extended_location_type"),
                "tags": CONFIG.get("KUBERNETESCLUSTER", "tags"),
                "tagsUpdate": CONFIG.get("KUBERNETESCLUSTER", "tags_update"),
                "adminUsername": CONFIG.get("KUBERNETESCLUSTER", "admin_username"),
                "sshKey": CONFIG.get("KUBERNETESCLUSTER", "ssh_key_values"),
                "cpAdminUsername": CONFIG.get("KUBERNETESCLUSTER", "cp_admin_username"),
                "cpSshKeyList": CONFIG.get("KUBERNETESCLUSTER", "cp_ssh_key_list"),
                "adminGroupObjectIds": CONFIG.get(
                    "KUBERNETESCLUSTER", "admin_group_object_ids"
                ),
                "initialNodeConfiguration": CONFIG.get(
                    "KUBERNETESCLUSTER", "initial_node_configuration"
                ),
                "csnId": CONFIG.get("KUBERNETESCLUSTER", "cloud_services_network_id"),
                "cniId": CONFIG.get("KUBERNETESCLUSTER", "cni_network_id"),
                "podCidrs": CONFIG.get("KUBERNETESCLUSTER", "pod_cidrs"),
                "serviceCidrs": CONFIG.get("KUBERNETESCLUSTER", "service_cidrs"),
                "dnsServiceIp": CONFIG.get("KUBERNETESCLUSTER", "dns_service_ip"),
                "fabricPeeringEnabled": CONFIG.get(
                    "KUBERNETESCLUSTER", "fabric_peering_enabled"
                ),
                "ipAddressPools": CONFIG.get("KUBERNETESCLUSTER", "ip_address_pools"),
                "kubernetesVersion": CONFIG.get(
                    "KUBERNETESCLUSTER", "kubernetes_version"
                ),
                "countUpdate": CONFIG.get("KUBERNETESCLUSTER", "count_update"),
                "vmSkuName": CONFIG.get("KUBERNETESCLUSTER", "vm_sku_name"),
                "count": CONFIG.get("KUBERNETESCLUSTER", "count"),
                "nodeName": CONFIG.get("KUBERNETESCLUSTER_NODE", "node_name"),
                "kubernetesClusterName": CONFIG.get(
                    "KUBERNETESCLUSTER_NODE", "kubernetes_cluster_name"
                ),
                "resourceGroup": CONFIG.get("KUBERNETESCLUSTER_NODE", "resource_group"),
                # scenario 2: update variables
                "rgUpdate": CONFIG.get("KUBERNETESCLUSTER", "rg_update"),
                "nameUpdate": CONFIG.get("KUBERNETESCLUSTER", "name_update"),
                "sshKeyUpdate": CONFIG.get(
                    "KUBERNETESCLUSTER", "ssh_key_values_update"
                ),
                "cpSshKeyListUpdate": CONFIG.get(
                    "KUBERNETESCLUSTER", "cp_ssh_key_list_update"
                ),
            }
        )

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix="clitest_rg"[:7], key="rg", parameter_name="rg")
    def test_kubernetescluster_scenario(self):
        """test scenario for kubernetes cluster CRUD operations"""
        call_scenario1(self)

    @AllowLargeResponse()
    def test_kubernetescluster_scenario2(self):
        """test scenario for kubernetes cluster administrator credentials update operations"""
        call_scenario2(self)
