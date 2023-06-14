# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
NFC tests scenarios
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
    ''' Env setup_scenario2 '''
    pass

def cleanup_scenario2(test):
    '''Env cleanup_scenario2 '''
    pass

def call_scenario1(test):
    ''' # Testcase: scenario1'''
    setup_scenario1(test)
    step_create(test, checks=[])
    step_show(test, checks=[])
    step_list_subscription(test, checks=[])
    step_list_resource_group(test, checks=[])
    # skip testing delete until the Network Fabric Controller can be deleted without being created
    # Instead we will delete in scenario 2
    # step_delete(test, checks=[])
    cleanup_scenario1(test)

def call_scenario2(test):
    setup_scenario2(test)
    step_delete(test, checks=[])
    cleanup_scenario2(test)

def step_create(test, checks=None):
    '''nfc create operation'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric controller create --resource-group {rg} --location {location} --resource-name {name}'
			 ' --infra-er-connections {infraERConnections} --workload-er-connections {workloadERConnections}'
             ' --ipv4-address-space {ipv4AddressSpace} --no-wait' , checks=checks)

def step_show(test, checks=None):
    '''nfc show operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric controller show --resource-name {name} --resource-group {rg}')
    
def step_delete(test, checks=None):
    '''nfc delete operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric controller delete --resource-name {nameDelete} --resource-group {rg}')

def step_list_resource_group(test, checks=None):
    '''nfc list by resource group operation'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric controller list --resource-group {rg}')

def step_list_subscription(test, checks=None):
    '''nfc list by subscription operation'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric controller list')

class NFCScenarioTest1(ScenarioTest):
    ''' NFCScenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'name': CONFIG.get('NETWORK_FABRIC_CONTROLLER', 'name'),
            'nameDelete': CONFIG.get('NETWORK_FABRIC_CONTROLLER', 'nameDelete'),
            'rg': CONFIG.get('NETWORK_FABRIC_CONTROLLER', 'resource_group'),
            'location': CONFIG.get('NETWORK_FABRIC_CONTROLLER', 'location'),
            'infraERConnections': CONFIG.get('NETWORK_FABRIC_CONTROLLER', 'infra_ER_Connections'),
            'workloadERConnections': CONFIG.get('NETWORK_FABRIC_CONTROLLER', 'workload_ER_Connections'),
            'ipv4AddressSpace': CONFIG.get('NETWORK_FABRIC_CONTROLLER', 'ipv4_address_space')
        })

    def test_nfc_scenario1(self):
        ''' test scenario for NFC CRUD operations'''
        call_scenario1(self)

    def test_nfc_scenario2(self):
        ''' test scenario for NFC CRUD operations'''
        call_scenario2(self)