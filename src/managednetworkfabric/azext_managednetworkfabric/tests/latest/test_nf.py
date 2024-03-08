# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
NF tests scenarios
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
    step_list_subscription(test, checks=[])
    cleanup_scenario1(test)


def step_create(test, checks=None):
    '''nf create operation'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric fabric create --resource-group {rg} --location {location} --resource-name {name} --nf-sku {nf_sku} --nfc-id {nfc_id}'
             ' --fabric-asn {fabric_asn} --ipv4-prefix {ipv4_prefix} --ipv6-prefix {ipv6_prefix} --rack-count {rack_count} --server-count-per-rack {server_count_per_rack}'
             ' --ts-config {terminalServerConf} --managed-network-config {managedNetworkConf}', checks=checks)


def step_show(test, checks=None):
    '''nf show operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric fabric show --resource-name {name} --resource-group {rg}')


def step_list_resource_group(test, checks=None):
    '''nf list by resource group operation'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric fabric list --resource-group {rg}')


def step_list_subscription(test, checks=None):
    '''nf list by subscription'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric fabric list')


class GA_NFScenarioTest1(ScenarioTest):
    ''' NFScenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'name': CONFIG.get('NETWORK_FABRIC', 'name'),
            'rg': CONFIG.get('NETWORK_FABRIC', 'resource_group'),
            'location': CONFIG.get('NETWORK_FABRIC', 'location'),
            'nf_sku': CONFIG.get('NETWORK_FABRIC', 'nf_sku'),
            'nfc_id': CONFIG.get('NETWORK_FABRIC', 'nfc_id'),
            'fabric_asn': CONFIG.get('NETWORK_FABRIC', 'fabric_asn'),
            'ipv4_prefix': CONFIG.get('NETWORK_FABRIC', 'ipv4_prefix'),
            'ipv6_prefix': CONFIG.get('NETWORK_FABRIC', 'ipv6_prefix'),
            'rack_count': CONFIG.get('NETWORK_FABRIC', 'rack_count'),
            'server_count_per_rack': CONFIG.get('NETWORK_FABRIC', 'server_count_per_rack'),
            'terminalServerConf': CONFIG.get('NETWORK_FABRIC', 'terminalServerConf'),
            'deleteNFRGName': CONFIG.get('NETWORK_FABRIC', 'delete_nf_resource_group'),
            'deleteNFName': CONFIG.get('NETWORK_FABRIC', 'delete_nf_name'),
            'managedNetworkConf': CONFIG.get('NETWORK_FABRIC', 'managedNetworkConf')
        })

    def test_GA_nf_scenario1(self):
        ''' test scenario for NF CRUD operations'''
        call_scenario1(self)
