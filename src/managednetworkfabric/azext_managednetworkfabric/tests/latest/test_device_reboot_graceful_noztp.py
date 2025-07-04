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


def setup_scenario1(test):
    """Env setup_scenario1"""
    pass


def cleanup_scenario1(test):
    """Env cleanup_scenario1"""
    pass


def call_scenario1(test):
    """# Testcase: scenario1"""
    setup_scenario1(test)
    step_reboot(
        test,
        checks=[
            test.check("status", "Succeeded"),
        ],
    )
    cleanup_scenario1(test)


def step_reboot(test, checks=None):
    """Device run reboot operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric device reboot --resource-name {name} --resource-group {rg} --reboot-type {rebootType}"
    )


class GA_DeviceRebootGracefulNoZTPScenarioTest1(ScenarioTest):
    """DeviceScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_DEVICE", "reboot_device_name"),
                "rg": CONFIG.get("NETWORK_DEVICE", "reboot_device_rg"),
                "rebootType": CONFIG.get(
                    "NETWORK_DEVICE", "graceful_noztp_reboot_type"
                ),
            }
        )

    @AllowLargeResponse()
    def test_GA_Device_Reboot_GracefulNoZTP_scenario1(self):
        """test scenario for Device CRUD operations"""
        call_scenario1(self)
