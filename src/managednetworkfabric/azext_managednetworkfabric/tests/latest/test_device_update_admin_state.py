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
    step_update_admin_state(test, checks=[])
    cleanup_scenario1(test)


def step_update_admin_state(test, checks=None):
    '''Device run Update Admin State operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric device update-admin-state --resource-name {name} --resource-group {rg} --state {state}')


class GA_DeviceUpdateAdminStateScenarioTest1(ScenarioTest):
    ''' DeviceScenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'name': CONFIG.get('NETWORK_DEVICE', 'update_admin_state_device_name'),
            'rg': CONFIG.get('NETWORK_DEVICE', 'update_admin_state_device_rg'),
            'state': CONFIG.get('NETWORK_DEVICE', 'update_admin_state_device_state')
        })

    @AllowLargeResponse()
    def test_GA_Device_UpdateAdminState_scenario1(self):
        ''' test scenario for Device CRUD operations'''
        call_scenario1(self)
