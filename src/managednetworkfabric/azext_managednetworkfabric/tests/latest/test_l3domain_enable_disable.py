# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
L3 Domain tests scenarios
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
    step_update_admin_state_Enable(test, checks=[])
    step_update_admin_state_Disable(test, checks=[])
    cleanup_scenario1(test)


def step_update_admin_state_Enable(test, checks=None):
    '''l3domain Update admin state operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric l3domain update-admin-state --resource-group {rg} --resource-name {post_name} --state {state_Enable}')


def step_update_admin_state_Disable(test, checks=None):
    '''l3domain Update admin state operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric l3domain update-admin-state --resource-group {rg} --resource-name {post_name} --state {state_Disable}')


class GA_L3DomainEnableDisableScenarioTest1(ScenarioTest):
    ''' L3 Domain Scenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'rg': CONFIG.get('L3_ISOLATION_DOMAIN', 'resource_group'),
            'post_name': CONFIG.get('L3_ISOLATION_DOMAIN', 'post_name'),
            'state_Enable': CONFIG.get('L3_ISOLATION_DOMAIN', 'state_Enable'),
            'state_Disable': CONFIG.get('L3_ISOLATION_DOMAIN', 'state_Disable')
        })

    def test_GA_l3domain_enable_disable_scenario1(self):
        ''' test scenario for L3 Domain CRUD operations'''
        call_scenario1(self)
