# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

from azure.cli.testsdk.scenario_tests import AllowLargeResponse

"""
Ip Extended Community tests scenarios
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
    step_update(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_list_subscription(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def step_create(test, checks=None):
    '''ipextendedcommunity create operation'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric ipextendedcommunity create --resource-group {rg} --location {location} --resource-name {name}'
             ' --ip-extended-community-rules {ipExtendedCommunityRules}', checks=checks)


def step_show(test, checks=None):
    '''ipextendedcommunity show operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric ipextendedcommunity show --resource-name {name} --resource-group {rg}')


def step_update(test, checks=None):
    '''ipextendedcommunity update operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric ipextendedcommunity create --resource-group {rg} --location {location} --resource-name {name}'
        ' --ip-extended-community-rules {updatedIpExtendedCommunityRules}', checks=checks)


@AllowLargeResponse()
def step_list_resource_group(test, checks=None):
    '''ipextendedcommunity list by resource group operation'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric ipextendedcommunity list --resource-group {rg}')


@AllowLargeResponse()
def step_list_subscription(test, checks=None):
    '''ipextendedcommunity list by subscription'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric ipextendedcommunity list')


def step_delete(test, checks=None):
    '''ipextendedcommunity delete operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric ipextendedcommunity delete --resource-name {name} --resource-group {rg}')


class GA_IpExtendedCommunityScenarioTest1(ScenarioTest):
    ''' Ip Extended Community Scenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'name': CONFIG.get('IP_EXTENDED_COMMUNITY', 'name'),
            'rg': CONFIG.get('IP_EXTENDED_COMMUNITY', 'resource_group'),
            'location': CONFIG.get('IP_EXTENDED_COMMUNITY', 'location'),
            'ipExtendedCommunityRules': CONFIG.get('IP_EXTENDED_COMMUNITY', 'ip_extended_community_rules'),
            'updatedIpExtendedCommunityRules': CONFIG.get('IP_EXTENDED_COMMUNITY', 'updated_ip_extended_community_rules')
        })

    def test_GA_ipextendedcommunity_scenario1(self):
        ''' test scenario for IpExtendedCommunity CRUD operations'''
        call_scenario1(self)
