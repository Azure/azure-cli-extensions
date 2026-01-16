# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
NNI tests scenarios
"""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG


def setup_scenario(test):
    """Env setup_scenario"""
    pass


def cleanup_scenario(test):
    """Env cleanup_scenario"""
    pass


def call_scenario1(test):
    """Testcase: scenario1"""
    setup_scenario(test)
    step_update_scenario1(test, checks=[])
    cleanup_scenario(test)


def call_scenario1(test):
    """Testcase: scenario1"""
    setup_scenario(test)
    step_update_scenario2(test, checks=[])
    cleanup_scenario(test)


def step_update_scenario1(test, checks=None):
    """nni delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric nni update --resource-group {rg} --resource-name {name} --fabric {fabric} --layer2-configuration {layer2Configuration}"
        " --option-b-layer3-configuration {optionBLayer3Configuration} --import-route-policy {importRoutePolicy} --export-route-policy {exportRoutePolicy}"
        " --egress-acl-id {egressAclId} --ingress-acl-id {ingressAclId} --micro-bfd-state {microBfdState} --npb-static-route-configuration {npbStaticRouteConfiguration} "
        " --static-route-configuration {staticRouteConfiguration}",
        checks=checks,
    )


def step_update_scenario2(test, checks=None):
    """nni delete operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric nni update --resource-group {rg} --resource-name {name} --fabric-name {fabric} --l2-config {layer2Configuration}"
        " --option-b-l3-config {optionBLayer3Configuration} --import-route-policy {importRoutePolicy} --export-route-policy {exportRoutePolicy}"
        " --egress-acl-id {egressAclId} --ingress-acl-id {ingressAclId} --micro-bfd-state {microBfdState} --npb-static-route-conf {npbStaticRouteConfiguration} "
        " --static-route-config {staticRouteConfiguration}",
        checks=checks,
    )


class GA_NNI_update_ScenarioTest1(ScenarioTest):
    """NNIScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_TO_NETWORK_INTERCONNECT", "name"),
                "rg": CONFIG.get("NETWORK_TO_NETWORK_INTERCONNECT", "resource_group"),
                "fabric": CONFIG.get("NETWORK_TO_NETWORK_INTERCONNECT", "fabric"),
                "layer2Configuration": CONFIG.get(
                    "NETWORK_TO_NETWORK_INTERCONNECT", "layer2_Configuration"
                ),
                "optionBLayer3Configuration": CONFIG.get(
                    "NETWORK_TO_NETWORK_INTERCONNECT", "option_b_layer3_configuration"
                ),
                "importRoutePolicy": CONFIG.get(
                    "NETWORK_TO_NETWORK_INTERCONNECT", "import_route_policy"
                ),
                "exportRoutePolicy": CONFIG.get(
                    "NETWORK_TO_NETWORK_INTERCONNECT", "export_route_policy"
                ),
                "egressAclId": CONFIG.get(
                    "NETWORK_TO_NETWORK_INTERCONNECT", "egress_acl_id"
                ),
                "ingressAclId": CONFIG.get(
                    "NETWORK_TO_NETWORK_INTERCONNECT", "ingress_acl_id"
                ),
                "microBfdState": CONFIG.get(
                    "NETWORK_TO_NETWORK_INTERCONNECT", "micro_bfd_state"
                ),
                "npbStaticRouteConfiguration": CONFIG.get(
                    "NETWORK_TO_NETWORK_INTERCONNECT", "npb_static_route_configuration"
                ),
                "staticRouteConfiguration": CONFIG.get(
                    "NETWORK_TO_NETWORK_INTERCONNECT", "static_route_configuration"
                ),
            }
        )

    def test_GA_nni_update_scenario1(self):
        """test scenario for NNI CRUD operations"""
        call_scenario1(self)
