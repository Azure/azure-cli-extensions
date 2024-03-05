# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Network Tap tests scenarios
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
    step_resync(test, checks=[])
    cleanup_scenario1(test)


def step_resync(test, checks=None):
    '''Network Tap create operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric tap resync --resource-group {rg} --network-tap-name {name}', checks=checks)


class GA_TapResyncScenarioTest1(ScenarioTest):
    ''' Network Tap Scenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'name': CONFIG.get('NETWORK_TAP', 'resync_name'),
            'rg': CONFIG.get('NETWORK_TAP', 'resync_resource_group'),

        })

    def test_GA_tap_resync_scenario1(self):
        ''' test scenario for Network Tap CRUD operations'''
        call_scenario1(self)
