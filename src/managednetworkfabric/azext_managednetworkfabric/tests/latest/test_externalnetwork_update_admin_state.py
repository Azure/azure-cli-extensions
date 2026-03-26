# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

from azure.cli.testsdk.scenario_tests import AllowLargeResponse

"""
ExternalNetwork tests scenarios
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
    step_update_admin_state_scenario1(test, checks=[])
    cleanup_scenario(test)


def call_scenario2(test):
    """Testcase: scenario2"""
    setup_scenario(test)
    step_update_admin_state_scenario2(test, checks=[])
    cleanup_scenario(test)


def step_update_admin_state_scenario1(test, checks=None):
    """ExternalNetwork run Update Admin State operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric externalnetwork update-admin-state --resource-name {name} --resource-group {rg} --l3domain {l3Domain} --state {state} --resource-ids {resourceIds}"
    )


def step_update_admin_state_scenario2(test, checks=None):
    """ExternalNetwork run Update Admin State operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric externalnetwork update-admin-state --resource-name {name} --resource-group {rg} --l3-isolation-domain-name {l3Domain} --state {state} --resource-ids {resourceIds}"
    )


class GA_InternalNNetworkUpdateAdminStateScenarioTest1(ScenarioTest):
    """ExternalNetwork Scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("EXTERNAL_NETWORK", "optiona_name"),
                "rg": CONFIG.get("EXTERNAL_NETWORK", "optiona_resource_group"),
                "l3Domain": CONFIG.get("EXTERNAL_NETWORK", "optiona_l3_domain"),
                "state": CONFIG.get("EXTERNAL_NETWORK", "enabled_state"),
                "resourceIds": CONFIG.get("EXTERNAL_NETWORK", "resource_ids"),
            }
        )

    @AllowLargeResponse()
    def test_GA_externalnetwork_update_admin_state_scenario1(self):
        """test scenario for ExternalNetwork CRUD operations"""
        call_scenario1(self)
