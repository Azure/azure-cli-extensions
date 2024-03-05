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
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def step_delete(test, checks=None):
    '''nf delete operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric fabric delete --resource-name {deleteNFName} --resource-group {deleteNFRGName}')


class GA_NFDelteScenarioTest1(ScenarioTest):
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

    def test_GA_nf_Delete_scenario1(self):
        ''' test scenario for NF CRUD operations'''
        call_scenario1(self)
