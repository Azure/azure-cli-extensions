# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Route Policy tests scenarios
"""

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from .config import CONFIG

def setup_scenario1(test):
    ''' Env setup_scenario1 '''
    pass

def cleanup_scenario1(test):
    '''Env cleanup_scenario1 '''
    pass

def setup_scenario2(test):
    ''' Env setup_scenario1 '''
    pass

def cleanup_scenario2(test):
    '''Env cleanup_scenario1 '''
    pass

def call_scenario1(test):
    ''' # Testcase: scenario1'''
    setup_scenario1(test)
    step_create_s1(test, checks=[])
    step_show(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)

def call_scenario2(test):
    ''' # Testcase: scenario1'''
    setup_scenario2(test)
    step_create_s2(test, checks=[])
    step_show(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario2(test)

def step_create_s1(test, checks=None):
    '''routepolicy create operation with IpCommunities'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric routepolicy create --resource-group {rg} --resource-name {name} --location {location} --nf-id {nfId} --address-family-type {addressFamilyType} --statements {statements_with_ipcommunity}', checks=checks)

def step_create_s2(test, checks=None):
    '''routepolicy create operation with IpExtendedCommunities'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric routepolicy create --resource-group {rg} --resource-name {name} --location {location} --nf-id {nfId} --address-family-type {addressFamilyType} --statements {statements_with_ipextcommunity}', checks=checks)

def step_show(test, checks=None):
    '''routepolicy show operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric routepolicy show --resource-name {name} --resource-group {rg}')

def step_list_resource_group(test, checks=None):
    '''routepolicy list by resource group operation'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric routepolicy list --resource-group {rg}')

def step_delete(test, checks=None):
    '''routepolicy delete operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric routepolicy delete --resource-name {name} --resource-group {rg}')
    test.cmd(
        'az networkfabric routepolicy wait --resource-name {name} --resource-group {rg} --deleted')

class GA_RoutePolicyScenarioTest1(ScenarioTest):
    ''' Route Policy Scenario1 test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'name': CONFIG.get('ROUTE_POLICY', 'name'),
            'rg': CONFIG.get('ROUTE_POLICY', 'resource_group'),
            'location': CONFIG.get('ROUTE_POLICY', 'location'),
            'nfId': CONFIG.get('ROUTE_POLICY', 'nf_id'),
            'addressFamilyType': CONFIG.get('ROUTE_POLICY', 'address_family_type'),
            'statements_with_ipcommunity': CONFIG.get('ROUTE_POLICY', 'statements_with_ipcommunity'),
            'statements_with_ipextcommunity': CONFIG.get('ROUTE_POLICY', 'statements_with_ipextcommunity')
        })

    def test_GA_route_policy_scenario1(self):
        ''' test scenario for Route Policy CRUD operations'''
        call_scenario1(self)
        call_scenario2(self)
