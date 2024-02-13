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
    step_update_s1(test, checks=[])
    common_methods(test)
    cleanup_scenario1(test)


def call_scenario2(test):
    ''' # Testcase: scenario2'''
    setup_scenario2(test)
    step_create_s2(test, checks=[])
    step_update_s2(test, checks=[])
    common_methods(test)
    cleanup_scenario2(test)


def common_methods(test):
    step_show(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_delete(test, checks=[])


def step_create_s1(test, checks=None):
    '''externalnetwork create operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric externalnetwork create --resource-group {rg} --l3domain {l3domain} --resource-name {name} --peering-option {s1_peering_option} --option-b-properties {optionBProperties} --import-route-policy {importRoutePolicy} --export-route-policy {exportRoutePolicy}', checks=checks)


def step_create_s2(test, checks=None):
    '''externalnetwork create operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric externalnetwork create --resource-group {rg} --l3domain {l3domain} --resource-name {name} --peering-option {s2_peering_option} --option-a-properties {optionAProperties} --import-route-policy {importRoutePolicy} --export-route-policy {exportRoutePolicy}', checks=checks)


def step_show(test, checks=None):
    '''externalnetwork show operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric externalnetwork show --resource-name {name} --l3domain {l3domain} --resource-group {rg}')


def step_update_s1(test, checks=None):
    '''externalnetwork update operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric externalnetwork update --resource-group {rg} --l3domain {l3domain} --resource-name {name} --peering-option {s1_peering_option} --option-b-properties {updatedOptionBProperties}', checks=checks)


def step_update_s2(test, checks=None):
    '''externalnetwork update operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric externalnetwork update --resource-group {rg} --l3domain {l3domain} --resource-name {name} --peering-option {s2_peering_option} --option-a-properties {updatedOptionAProperties}', checks=checks)


def step_list_resource_group(test, checks=None):
    '''externalnetwork list by resource group operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric externalnetwork list --resource-group {rg} --l3domain {l3domain}')


def step_delete(test, checks=None):
    '''externalnetwork delete operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric externalnetwork delete --resource-name {name} --l3domain {l3domain} --resource-group {rg}')


class GA_ExternalNetworkScenarioTest1(ScenarioTest):
    ''' External Network Scenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'name': CONFIG.get('EXTERNAL_NETWORK', 'name'),
            'rg': CONFIG.get('EXTERNAL_NETWORK', 'resource_group'),
            'l3domain': CONFIG.get('EXTERNAL_NETWORK', 'l3domain'),
            's1_peering_option': CONFIG.get('EXTERNAL_NETWORK', 's1_peering_option'),
            's2_peering_option': CONFIG.get('EXTERNAL_NETWORK', 's2_peering_option'),
            'importRoutePolicy': CONFIG.get('EXTERNAL_NETWORK', 'import_route_policy'),
            'exportRoutePolicy': CONFIG.get('EXTERNAL_NETWORK', 'export_route_policy'),
            'optionBProperties': CONFIG.get('EXTERNAL_NETWORK', 'option_b_properties'),
            'updatedOptionBProperties': CONFIG.get('EXTERNAL_NETWORK', 'updated_option_b_properties'),
            'optionAProperties': CONFIG.get('EXTERNAL_NETWORK', 'option_a_properties'),
            'updatedOptionAProperties': CONFIG.get('EXTERNAL_NETWORK', 'updated_option_a_properties')

        })

    def test_GA_externalnetwork_scenario1(self):
        ''' test scenario for externalnetwork CRUD operations'''
        call_scenario1(self)
        call_scenario2(self)
