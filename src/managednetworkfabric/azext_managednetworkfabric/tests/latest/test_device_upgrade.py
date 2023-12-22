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

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from .config import CONFIG


def setup_scenario1(test):
    ''' Env setup_scenario1 '''
    pass


def cleanup_scenario1(test):
    '''Env cleanup_scenario1 '''
    pass


def call_scenario1(test):
    ''' # Testcase: scenario1'''
    setup_scenario1(test)
    step_upgrade(test, checks=[])
    cleanup_scenario1(test)


def step_upgrade(test, checks=None):
    '''Device upgrade operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric device upgrade --resource-group {upgradeDeviceRGName} --resource-name {upgradeDeviceName} --version {upgradeVersion}', checks=checks)


class GA_DeviceUpgradeScenarioTest1(ScenarioTest):
    ''' DeviceScenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'upgradeDeviceRGName': CONFIG.get('NETWORK_DEVICE', 'upgrade_resource_group'),
            'upgradeDeviceName': CONFIG.get('NETWORK_DEVICE', 'upgrade_device_name'),
            'upgradeVersion': CONFIG.get('NETWORK_DEVICE', 'upgrade_version')
        })

    @AllowLargeResponse()
    def test_GA_Device_upgrade_scenario1(self):
        ''' test scenario for Device upgrade operation'''
        call_scenario1(self)
