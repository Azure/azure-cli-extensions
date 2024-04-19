# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Ip Prefix tests scenarios
"""

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from azure.cli.testsdk.scenario_tests import AllowLargeResponse
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
    step_update(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_list_subscription(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def step_create(test, checks=None):
    '''ipprefix create operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric ipprefix create --resource-group {rg} --location {location} --resource-name {name} --ip-prefix-rules {ipPrefixRules} ', checks=checks)


def step_show(test, checks=None):
    '''ipprefix show operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric ipprefix show --resource-name {name} --resource-group {rg}')


def step_update(test, checks=None):
    '''ipprefix update operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric ipprefix create --resource-group {rg} --location {location} --resource-name {name} --ip-prefix-rules {updatedIpPrefixRules} ', checks=checks)


def step_list_resource_group(test, checks=None):
    '''ipprefix list by resource group operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric ipprefix list --resource-group {rg}')


def step_list_subscription(test, checks=None):
    '''ipprefix list by subscription'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric ipprefix list')


def step_delete(test, checks=None):
    '''ipprefix delete operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric ipprefix delete --resource-name {name} --resource-group {rg}')


class GA_IpPrefixScenarioTest1(ScenarioTest):
    ''' IpPrefix Scenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'name': CONFIG.get('IP_PREFIX', 'name'),
            'rg': CONFIG.get('IP_PREFIX', 'resource_group'),
            'location': CONFIG.get('IP_PREFIX', 'location'),
            'ipPrefixRules': CONFIG.get('IP_PREFIX', 'ip_prefix_rules'),
            'updatedIpPrefixRules': CONFIG.get('IP_PREFIX', 'updated_ip_prefix_rules')
        })

    @AllowLargeResponse()
    def test_GA_ipprefix_scenario1(self):
        ''' test scenario for IpPrefix CRUD operations'''
        call_scenario1(self)
