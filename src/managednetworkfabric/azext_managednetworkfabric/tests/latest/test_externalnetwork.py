# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
External Network tests scenarios
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
    '''externalnetwork create operation'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric externalnetwork create --resource-group {rg} --l3domain {l3domain} --resource-name {name} --peering-option {peering_option} --option-a-properties {optionAProperties} --option-b-properties {optionBProperties}', checks=checks)

def step_show(test, checks=None):
    '''externalnetwork show operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric externalnetwork show --resource-name {name} --l3domain {l3domain} --resource-group {rg}')
    
def step_delete(test, checks=None):
    '''externalnetwork delete operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric externalnetwork delete --resource-name {name} --l3domain {l3domain} --resource-group {rg}')

def step_list_resource_group(test, checks=None):
    '''externalnetwork list by resource group operation'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric externalnetwork list --resource-group {rg} --l3domain {l3domain}')

class ExternalNetworkScenarioTest1(ScenarioTest):
    ''' External Network Scenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'name': CONFIG.get('External_Network', 'name'),
            'rg': CONFIG.get('External_Network', 'resource_group'),
            'l3domain': CONFIG.get('External_Network', 'l3domain'),
            'peering_option': CONFIG.get('External_Network', 'peering_option'),
            'importRoutePolicyId': CONFIG.get('External_Network', 'import_route_policy_id'),
            'exportRoutePolicyId': CONFIG.get('External_Network', 'export_route_policy_id'),
            'optionBProperties': CONFIG.get('External_Network', 'option_b_properties'),
            'optionAProperties': CONFIG.get('External_Network', 'option_a_properties')
        })

    def test_externalnetwork_scenario1(self):
        ''' test scenario for externalnetwork CRUD operations'''
        call_scenario1(self)