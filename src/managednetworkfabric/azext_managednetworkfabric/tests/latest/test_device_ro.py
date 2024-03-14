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
    step_ro(test, checks=[])
    cleanup_scenario1(test)


def step_ro(test, checks=None):
    '''Device run RO operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric device run-ro --resource-name {name} --resource-group {rg} --ro-command {command}')


class GA_DeviceRoScenarioTest1(ScenarioTest):
    ''' DeviceScenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'name': CONFIG.get('NETWORK_DEVICE', 'ro_device_name'),
            'rg': CONFIG.get('NETWORK_DEVICE', 'ro_device_rg'),
            'command': CONFIG.get('NETWORK_DEVICE', 'ro_command')
        })

    @AllowLargeResponse()
    def test_GA_Device_Ro_scenario1(self):
        ''' test scenario for Device CRUD operations'''
        call_scenario1(self)
