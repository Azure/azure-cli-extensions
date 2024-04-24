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
    step_show(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_list_subscription(test, checks=[])
    step_update(test, checks=[])
    cleanup_scenario1(test)


def step_show(test, checks=None):
    '''Device show operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric device show --resource-name {name} --resource-group {rg}')


def step_list_resource_group(test, checks=None):
    '''Device list by resource group operation'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric device list --resource-group {rg}')


def step_list_subscription(test, checks=None):
    '''Device list by subscription operation'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric device list')


def step_update(test, checks=None):
    '''Device update operation'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric device update --resource-group {rg} --resource-name {name} '
             ' --serial-number {serial_number}', checks=checks)


class GA_DeviceScenarioTest1(ScenarioTest):
    ''' DeviceScenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'name': CONFIG.get('NETWORK_DEVICE', 'name'),
            'rg': CONFIG.get('NETWORK_DEVICE', 'resource_group'),
            'host_name': CONFIG.get('NETWORK_DEVICE', 'host_name'),
            'serial_number': CONFIG.get('NETWORK_DEVICE', 'serial_number')
        })

    @AllowLargeResponse()
    def test_GA_Device_scenario1(self):
        ''' test scenario for Device CRUD operations'''
        call_scenario1(self)
