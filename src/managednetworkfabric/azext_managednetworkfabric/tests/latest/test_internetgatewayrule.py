# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Internet Gateway Rule tests scenarios
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
    step_create(test, checks=[])
    step_show(test, checks=[])
    step_list_subscription(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def step_create(test, checks=None):
    '''Internet Gateway Rule create operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric internetgatewayrule create --resource-group {rg} --location {location} --resource-name {name} --rule-properties {ruleProperties}', checks=checks)


def step_show(test, checks=None):
    '''Internet Gateway Rule show operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric internetgatewayrule show --resource-name {name} --resource-group {rg}')


def step_list_resource_group(test, checks=None):
    '''Internet Gateway Rule list by resource group operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric internetgatewayrule list --resource-group {rg}')


def step_list_subscription(test, checks=None):
    '''Internet Gateway Rule list by subscription operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric internetgatewayrule list')


def step_delete(test, checks=None):
    '''Internet Gateway Rule delete operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric internetgatewayrule delete --resource-name {name} --resource-group {rg}')


class GA_InternetGatewayRuleScenarioTest1(ScenarioTest):
    ''' Internet Gateway Rule Scenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'name': CONFIG.get('INTERNET_GATEWAY_RULE', 'name'),
            'rg': CONFIG.get('INTERNET_GATEWAY_RULE', 'resource_group'),
            'location': CONFIG.get('INTERNET_GATEWAY_RULE', 'location'),
            'ruleProperties': CONFIG.get('INTERNET_GATEWAY_RULE', 'rule_properties')
        })

    def test_GA_internetgatewayrule_scenario1(self):
        ''' test scenario for Internet Gateway Rule CRUD operations'''
        call_scenario1(self)
