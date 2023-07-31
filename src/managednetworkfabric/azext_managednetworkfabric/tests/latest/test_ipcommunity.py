# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Ip Community tests scenarios
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
    step_list_resource_group(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)

def step_create(test, checks=None):
    '''ipcommunity create operation'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric ipcommunity create --resource-group {rg} --location {location} --resource-name {name}'
             ' --ip-community-rules {ipCommunityRules}', checks=checks)

def step_show(test, checks=None):
    '''ipcommunity show operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric ipcommunity show --resource-name {name} --resource-group {rg}')

def step_list_resource_group(test, checks=None):
    '''ipcommunity list by resource group operation'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric ipcommunity list --resource-group {rg}')

def step_delete(test, checks=None):
    '''ipcommunity delete operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric ipcommunity delete --resource-name {name} --resource-group {rg}')

class GA_IpCommunityScenarioTest1(ScenarioTest):
    ''' Ip Community Scenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'name': CONFIG.get('IP_COMMUNITY', 'name'),
            'rg': CONFIG.get('IP_COMMUNITY', 'resource_group'),
            'location': CONFIG.get('IP_COMMUNITY', 'location'),
            'ipCommunityRules': CONFIG.get('IP_COMMUNITY', 'ip_community_rules')
        })

    def test_GA_ipcommunity_scenario1(self):
        ''' test scenario for IpCommunity CRUD operations'''
        call_scenario1(self)