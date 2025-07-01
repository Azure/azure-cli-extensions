# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Kubernetescluster feature tests scenarios
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


def step_create(test, checks=None):
    """Kubernetescluster feature create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetescluster feature create --name {name} "
        "--kubernetes-cluster-name {clusterName} --resource-group {rg} "
        "--location {location} "
        "--tags {tags}"
    )


def step_update(test, checks=None):
    """Kubernetescluster feature update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetescluster feature update --name {name} "
        "--kubernetes-cluster-name {clusterName} --resource-group {rg} "
        "--tags {tagsUpdate}"
    )


def step_show(test, checks=None):
    """Kubernetescluster feature show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetescluster feature show --name {name} "
        "--kubernetes-cluster-name {clusterName} --resource-group {rg}"
    )


def step_list(test, checks=None):
    """Kubernetescluster feature list operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetescluster feature list "
        "--kubernetes-cluster-name {clusterName} --resource-group {rg}"
    )


def step_delete(test, checks=None):
    """Kubernetescluster feature delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetescluster feature delete --name {name} "
        "--kubernetes-cluster-name {clusterName} --resource-group {rg} -y"
    )


class KubernetesClusterFeatureScenarioTest(ScenarioTest):
    """Kubernetescluster feature scenario tests"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("KUBERNETESCLUSTER_FEATURE", "name"),
                "clusterName": CONFIG.get("KUBERNETESCLUSTER_FEATURE", "cluster_name"),
                "rg": CONFIG.get("KUBERNETESCLUSTER_FEATURE", "resource_group"),
                "location": CONFIG.get("KUBERNETESCLUSTER_FEATURE", "location"),
                "tags": CONFIG.get("KUBERNETESCLUSTER_AGENTPOOL", "tags"),
                "tagsUpdate": CONFIG.get("KUBERNETESCLUSTER_FEATURE", "tags_update"),
            }
        )

    def test_kubernetesclusterfeature_scenario(self):
        """test scenario for kubernetes cluster feature CRUD operations"""
        call_scenario1(self)
