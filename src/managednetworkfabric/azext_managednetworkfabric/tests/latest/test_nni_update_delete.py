# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
NNI tests scenarios
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
    step_update(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def step_update(test, checks=None):
    '''nni delete operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric nni update --resource-name {name} --resource-group {rg} --fabric {fabric} --option-b-layer3-configuration {updatedOptionBLayer3Configuration}')


def step_delete(test, checks=None):
    '''nni delete operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric nni delete --resource-name {name} --resource-group {rg} --fabric {fabric}')


class GA_NNI_update_Delete_ScenarioTest1(ScenarioTest):
    ''' NNIScenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'name': CONFIG.get('NETWORK_TO_NETWORK_INTERCONNECT', 'name'),
            'rg': CONFIG.get('NETWORK_TO_NETWORK_INTERCONNECT', 'resource_group'),
            'fabric': CONFIG.get('NETWORK_TO_NETWORK_INTERCONNECT', 'fabric'),
            'nniType': CONFIG.get('NETWORK_TO_NETWORK_INTERCONNECT', 'nni_type'),
            'isManagementType': CONFIG.get('NETWORK_TO_NETWORK_INTERCONNECT', 'is_management_type'),
            'useOptionB': CONFIG.get('NETWORK_TO_NETWORK_INTERCONNECT', 'use_option_b'),
            'layer2Configuration': CONFIG.get('NETWORK_TO_NETWORK_INTERCONNECT', 'layer2_Configuration'),
            'optionBLayer3Configuration': CONFIG.get('NETWORK_TO_NETWORK_INTERCONNECT', 'option_b_layer3_configuration'),
            'updatedOptionBLayer3Configuration': CONFIG.get('NETWORK_TO_NETWORK_INTERCONNECT', 'updated_option_b_layer3_configuration'),
            'importRoutePolicy': CONFIG.get('NETWORK_TO_NETWORK_INTERCONNECT', 'import_route_policy'),
            'exportRoutePolicy': CONFIG.get('NETWORK_TO_NETWORK_INTERCONNECT', 'export_route_policy')
        })

    def test_GA_nni_Update_Delete_scenario1(self):
        ''' test scenario for NNI CRUD operations'''
        call_scenario1(self)
