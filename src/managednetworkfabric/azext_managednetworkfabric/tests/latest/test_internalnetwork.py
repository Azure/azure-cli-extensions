# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Internal Network tests scenarios
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
    '''internalnetwork create operation'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric internalnetwork create --resource-group {rg} --l3-isolation-domain-name {l3domain} --resource-name {name} --vlan-id {vlan_id}'
			 ' --mtu {mtu} --connected-ipv4-subnets {connectedIpv4Subnets} --connected-ipv6-subnets {connectedIpv6Subnets} --static-route-configuration {staticRouteConf} --bgp-configuration {bgpConf} --no-wait', checks=checks)

def step_show(test, checks=None):
    '''internalnetwork show operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric internalnetwork show --resource-name {name} --l3domain {l3domain} --resource-group {rg}')
    
def step_delete(test, checks=None):
    '''internalnetwork delete operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric internalnetwork delete --resource-name {name} --l3domain {l3domain} --resource-group {rg}')

def step_list_resource_group(test, checks=None):
    '''internalnetwork list by resource group operation'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric internalnetwork list --resource-group {rg} --l3domain {l3domain}')

class InternalNetworkScenarioTest1(ScenarioTest):
    ''' Internal Network Scenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'name': CONFIG.get('Internal_Network', 'name'),
            'rg': CONFIG.get('Internal_Network', 'resource_group'),
            'l3domain': CONFIG.get('Internal_Network', 'l3domain'),
            'vlan_id': CONFIG.get('Internal_Network', 'vlan_id'),
            'mtu': CONFIG.get('Internal_Network', 'mtu'),
            'connectedIpv4Subnets': CONFIG.get('Internal_Network', 'connected_Ipv4_subnets'),
            'connectedIpv6Subnets': CONFIG.get('Internal_Network', 'connected_Ipv6_subnets'),
            'staticRouteConf': CONFIG.get('Internal_Network', 'static_route_conf'),
            'bgpConf': CONFIG.get('Internal_Network', 'bgp_conf')
        })

    def test_internalnetwork_scenario1(self):
        ''' test scenario for internalnetwork CRUD operations'''
        call_scenario1(self)