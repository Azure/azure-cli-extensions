# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Internet Gateway tests scenarios
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
    step_list_subscription(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_update(test, checks=[])
    cleanup_scenario1(test)


def step_show(test, checks=None):
    '''Internet Gateway show operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric internetgateway show --resource-name {name} --resource-group {rg}')


def step_list_resource_group(test, checks=None):
    '''Internet Gateway list by resource group operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric internetgateway list --resource-group {rg}')


def step_list_subscription(test, checks=None):
    '''Internet Gateway list by subscription operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric internetgateway list')


def step_update(test, checks=None):
    '''Internet Gateway update operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric internetgateway update --resource-group {rg} --resource-name {name} --internet-gateway-rule-id {internetGatewayRuleId}', checks=checks)


class GA_InternetGatewayScenarioTest1(ScenarioTest):
    ''' Internet Gateway Scenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'name': CONFIG.get('INTERNET_GATEWAY', 'name'),
            'rg': CONFIG.get('INTERNET_GATEWAY', 'resource_group'),
            'internetGatewayRuleId': CONFIG.get('INTERNET_GATEWAY', 'internet_gateway_rule_id')
        })

    def test_GA_internetgateway_scenario1(self):
        ''' test scenario for Internet Gateway CRUD operations'''
        call_scenario1(self)
