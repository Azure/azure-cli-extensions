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
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def step_delete(test, checks=None):
    '''l3domain delete operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric l3domain delete --resource-name {name} --resource-group {rg}')


class GA_L3DomainDeleteScenarioTest1(ScenarioTest):
    ''' L3 Domain Scenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'name': CONFIG.get('L3_ISOLATION_DOMAIN', 'deletename'),
            'rg': CONFIG.get('L3_ISOLATION_DOMAIN', 'delete_resource_group')
        })

    def test_GA_l3domain_delete_scenario1(self):
        ''' test scenario for L3 Domain CRUD operations'''
        call_scenario1(self)
