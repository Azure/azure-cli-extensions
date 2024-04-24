# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Rack tests scenarios
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
    cleanup_scenario1(test)


def step_show(test, checks=None):
    '''Rack show operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric rack show --resource-name {name} --resource-group {rg}')


def step_list_resource_group(test, checks=None):
    '''Rack list by resource group operation'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric rack list --resource-group {rg}')


def step_list_subscription(test, checks=None):
    '''Rack list by subscription'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric rack list')


class GA_RackScenarioTest1(ScenarioTest):
    ''' RackScenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'name': CONFIG.get('NETWORK_RACK', 'name'),
            'rg': CONFIG.get('NETWORK_RACK', 'resource_group')
        })

    def test_GA_Rack_scenario1(self):
        ''' test scenario for Rack CRUD operations'''
        call_scenario1(self)
