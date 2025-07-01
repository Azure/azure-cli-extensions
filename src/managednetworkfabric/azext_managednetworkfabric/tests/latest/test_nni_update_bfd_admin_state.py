# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

from azure.cli.testsdk.scenario_tests import AllowLargeResponse

"""
NNI tests scenarios
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
    step_update_bfd_admin_state(test, checks=[])
    cleanup_scenario1(test)


def step_update_bfd_admin_state(test, checks=None):
    """nni run Update BFD Admin State operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric nni update-bfd-administrative-state  --network-fabric-name {fabric} --nni-name {name}"
        " --resource-group {rg} --administrative-state {administrativeState} --route-type {routeType}"
    )


class GA_NNIUpdateBFDAdminStateTest1(ScenarioTest):
    """NNIScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_TO_NETWORK_INTERCONNECT", "name"),
                "rg": CONFIG.get("NETWORK_TO_NETWORK_INTERCONNECT", "resource_group"),
                "fabric": CONFIG.get("NETWORK_TO_NETWORK_INTERCONNECT", "fabric"),
                "administrativeState": CONFIG.get(
                    "NETWORK_TO_NETWORK_INTERCONNECT", "administrative_state"
                ),
                "routeType": CONFIG.get(
                    "NETWORK_TO_NETWORK_INTERCONNECT", "route_type"
                ),
            }
        )

    @AllowLargeResponse()
    def test_GA_nni_UpdateBFDAdminState_scenario1(self):
        """test scenario for NNI CRUD operations"""
        call_scenario1(self)
