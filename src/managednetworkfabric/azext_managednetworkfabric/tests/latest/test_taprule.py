# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Network Tap Rule tests scenarios
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
    ''' Network Tap Rule create operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric taprule create --resource-group {rg} --location {location} --resource-name {name} --configuration-type {configurationType} --match-configurations {matchConfigurations}', checks=checks)


def step_show(test, checks=None):
    ''' Network Tap Rule show operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric taprule show --resource-name {name} --resource-group {rg}')


def step_list_resource_group(test, checks=None):
    ''' Network Tap Rule list by resource group operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric taprule list --resource-group {rg}')


def step_list_subscription(test, checks=None):
    ''' Network Tap Rule list by subscription operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric taprule list')


def step_delete(test, checks=None):
    ''' Network Tap Rule delete operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric taprule delete --resource-name {deleteName} --resource-group {rg}')


class GA_TapRuleScenarioTest1(ScenarioTest):
    ''' Network Tap Rule Scenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'name': CONFIG.get('NETWORK_TAP_RULE', 'name'),
            'deleteName': CONFIG.get('NETWORK_TAP_RULE', 'delete_name'),
            'rg': CONFIG.get('NETWORK_TAP_RULE', 'resource_group'),
            'location': CONFIG.get('NETWORK_TAP_RULE', 'location'),
            'pollingIntervalInSeconds': CONFIG.get('NETWORK_TAP_RULE', 'polling_interval_in_seconds'),
            'configurationType': CONFIG.get('NETWORK_TAP_RULE', 'configuration_type'),
            'tapRulesUrl': CONFIG.get('NETWORK_TAP_RULE', 'tap_rules_url'),
            'matchConfigurations': CONFIG.get('NETWORK_TAP_RULE', 'match_configurations')
        })

    def test_GA_taprule_scenario1(self):
        ''' test scenario for Network Tap Rule CRUD operations'''
        call_scenario1(self)
