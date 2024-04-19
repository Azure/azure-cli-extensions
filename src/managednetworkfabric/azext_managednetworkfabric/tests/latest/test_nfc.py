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


def call_scenario1(test):
    ''' # Testcase: scenario1'''
    setup_scenario1(test)
    step_show(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_list_subscription(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def step_show(test, checks=None):
    '''nfc show operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric controller show --resource-name {name} --resource-group {rg}')


def step_list_resource_group(test, checks=None):
    '''nfc list by resource group operation'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric controller list --resource-group {rg}')


def step_list_subscription(test, checks=None):
    '''nfc list by subscription'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric controller list')


def step_delete(test, checks=None):
    '''nfc delete operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric controller delete --resource-name {deleteNFCName} --resource-group {rg}')


class GA_NFCScenarioTest1(ScenarioTest):
    ''' NFCScenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'name': CONFIG.get('NETWORK_FABRIC_CONTROLLER', 'name'),
            'rg': CONFIG.get('NETWORK_FABRIC_CONTROLLER', 'resource_group'),
            'location': CONFIG.get('NETWORK_FABRIC_CONTROLLER', 'location'),
            'infraERConnections': CONFIG.get('NETWORK_FABRIC_CONTROLLER', 'infra_ER_Connections'),
            'workloadERConnections': CONFIG.get('NETWORK_FABRIC_CONTROLLER', 'workload_ER_Connections'),
            'ipv4AddressSpace': CONFIG.get('NETWORK_FABRIC_CONTROLLER', 'ipv4_address_space'),
            'isWorkloadManagementNetworkEnabled': CONFIG.get('NETWORK_FABRIC_CONTROLLER', 'is_workload_management_network_enabled'),
            'deleteNFCName': CONFIG.get('NETWORK_FABRIC_CONTROLLER', 'delete_nfc_name'),
            'nfcSku': CONFIG.get('NETWORK_FABRIC_CONTROLLER', 'nfc_sku')
        })

    def test_GA_nfc_scenario1(self):
        ''' test scenario for NFC CRUD operations'''
        call_scenario1(self)
