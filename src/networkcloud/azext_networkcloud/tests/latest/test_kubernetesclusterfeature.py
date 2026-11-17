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
from .utils.output_checks import attr


def setup_scenario1(test):
    """Env setup_scenario1"""
    pass


def cleanup_scenario1(test):
    """Env cleanup_scenario1"""
    pass


def call_scenario1(test):
    """# Testcase: scenario1"""
    setup_scenario1(test)
    step_create_scenario1(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "provisioningState")),
            test.check("required", attr(test, "required")),
            test.check("version", attr(test, "version")),
        ],
    )
    step_update(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "provisioningState")),
            test.check("tags", attr(test, "tagsUpdate")),
            test.check("required", attr(test, "required")),
            test.check("version", attr(test, "version")),
        ],
    )
    step_show(
        test,
        checks=[
            test.exists("name"),
            test.exists("id"),
            test.check("required", attr(test, "required")),
            test.check("version", attr(test, "version")),
        ],
    )
    step_list(test)
    step_delete(test)
    cleanup_scenario1(test)


def call_scenario2(test):
    """# Testcase: scenario2"""
    setup_scenario1(test)
    step_create_scenario2(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "provisioningState")),
            test.check("required", attr(test, "required")),
            test.check("version", attr(test, "version")),
        ],
    )
    cleanup_scenario1(test)


def step_create_scenario1(test, checks=None):
    """Kubernetescluster feature create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetescluster feature create --name {name} "
        "--kubernetes-cluster-name {clusterName} --resource-group {rg} "
        "--location {location} "
        "--tags {tags}",
        checks=checks,
    )


def step_create_scenario2(test, checks=None):
    """Kubernetescluster feature create operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetescluster feature create --feature-name {name} "
        "--kc-name {clusterName} --resource-group {rg} "
        "--location {location} "
        "--options {options} "
        "--tags {tags}",
        checks=checks,
    )


def step_update(test, checks=None):
    """Kubernetescluster feature update operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetescluster feature update --name {name} "
        "--kubernetes-cluster-name {clusterName} --resource-group {rg} "
        "--tags {tagsUpdate}",
        checks=checks,
    )


def step_show(test, checks=None):
    """Kubernetescluster feature show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetescluster feature show --name {name} "
        "--kubernetes-cluster-name {clusterName} --resource-group {rg}",
        checks=checks,
    )


def step_list(test, checks=None):
    """Kubernetescluster feature list operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetescluster feature list "
        "--kubernetes-cluster-name {clusterName} --resource-group {rg}",
        checks=checks,
    )


def step_delete(test, checks=None):
    """Kubernetescluster feature delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkcloud kubernetescluster feature delete --name {name} "
        "--kubernetes-cluster-name {clusterName} --resource-group {rg} --yes",
        checks=checks,
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
                "options": CONFIG.get("KUBERNETESCLUSTER_FEATURE", "options"),
                "required": CONFIG.get("KUBERNETESCLUSTER_FEATURE", "required"),
                "version": CONFIG.get("KUBERNETESCLUSTER_FEATURE", "version"),
                "provisioningState": CONFIG.get(
                    "KUBERNETESCLUSTER_FEATURE", "provisioning_state"
                ),
            }
        )

    def test_kubernetesclusterfeature_scenario1(self):
        """test scenario for kubernetes cluster feature CRUD operations"""
        call_scenario1(self)

    def test_kubernetesclusterfeature_scenario2(self):
        """test scenario for kubernetes cluster feature create operation"""
        call_scenario2(self)
