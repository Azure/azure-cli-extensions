# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

from azure.cli.testsdk.scenario_tests import AllowLargeResponse

"""
Device tests scenarios
"""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG
from .utils.output_checks import attr


def setup_scenario(test):
    """Env setup_scenario1"""
    pass


def cleanup_scenario(test):
    """Env cleanup_scenario1"""
    pass


def call_scenario1(test):
    """Testcase: scenario1"""
    setup_scenario(test)
    step_ro_valid_json(test, checks=[test.check("@", attr(test, "expectedResponse"))])
    cleanup_scenario(test)


def call_scenario2(test):
    """Testcase: scenario2"""
    setup_scenario(test)
    step_ro_invalid_json(test, checks=[test.check("@", attr(test, "expectedResponse"))])
    cleanup_scenario(test)


def call_scenario3(test):
    """Testcase: scenario3"""
    setup_scenario(test)
    step_ro_missing_keys(test, checks=[test.check("@", attr(test, "expectedResponse"))])
    cleanup_scenario(test)


def step_ro_valid_json(test, checks=None):
    """Device run RO operation - valid JSON"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric device run-ro --resource-name {name} --resource-group {rg} --ro-command {command}",
        checks=checks,
    )


def step_ro_invalid_json(test, checks=None):
    """Device run RO operation - Invalid  JSON - truncated at server"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric device run-ro --resource-name {name} --resource-group {rg} --ro-command {command}",
        checks=checks,
    )


def step_ro_missing_keys(test, checks=None):
    """Device run RO operation - missing configurationState and outputUrl"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric device run-ro --resource-name {name} --resource-group {rg} --ro-command {command}",
        checks=checks,
    )


class GA_DeviceRoScenarioTest1(ScenarioTest):
    """DeviceScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_DEVICE", "ro_device_name"),
                "rg": CONFIG.get("NETWORK_DEVICE", "ro_device_rg"),
                "command": CONFIG.get("NETWORK_DEVICE", "ro_command"),
                "expectedResponse": CONFIG.get(
                    "NETWORK_DEVICE", "ro_valid_json_response"
                ),
            }
        )

    @AllowLargeResponse()
    def test_GA_device_ro_scenario1(self):
        """test scenario for Device CRUD operations - valid JSON"""
        call_scenario1(self)


class GA_DeviceRoScenarioTest2(ScenarioTest):
    """DeviceScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_DEVICE", "ro_device_name"),
                "rg": CONFIG.get("NETWORK_DEVICE", "ro_device_rg"),
                "command": CONFIG.get("NETWORK_DEVICE", "ro_command"),
                "expectedResponse": CONFIG.get(
                    "NETWORK_DEVICE", "ro_invalid_json_response"
                ),
            }
        )

    @AllowLargeResponse()
    def test_GA_device_ro_scenario2(self):
        """test scenario for Device CRUD operations - invalid JSON"""
        call_scenario2(self)


class GA_DeviceRoScenarioTest3(ScenarioTest):
    """DeviceScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_DEVICE", "ro_device_name"),
                "rg": CONFIG.get("NETWORK_DEVICE", "ro_device_rg"),
                "command": CONFIG.get("NETWORK_DEVICE", "ro_command"),
                "expectedResponse": CONFIG.get(
                    "NETWORK_DEVICE", "ro_missing_keys_response"
                ),
            }
        )

    @AllowLargeResponse()
    def test_GA_device_ro_scenario3(self):
        """test scenario for Device CRUD operations - invalid JSON"""
        call_scenario3(self)
