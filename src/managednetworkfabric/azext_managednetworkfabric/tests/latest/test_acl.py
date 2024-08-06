# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Access Control Lists tests scenarios
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
    step_update(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_list_subscription(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def step_create(test, checks=None):
    '''Access Control List create operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric acl create --resource-group {rg} --location {location} --resource-name {name} --configuration-type {configuration_type}'
        ' --default-action {default_action} '
        ' --match-configurations {match_configurations}', checks=checks)


def step_show(test, checks=None):
    '''Access Control List show operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric acl show --resource-name {name} --resource-group {rg}')


def step_update(test, checks=None):
    '''Access Control List update operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric acl update --resource-group {rg} --resource-name {name}'
        ' --configuration-type "Inline" --default-action {default_action}'
        ' --match-configurations {updated_match_configurations}', checks=checks)


def step_list_resource_group(test, checks=None):
    '''Access Control List list by resource group operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric acl list --resource-group {rg}')


def step_list_subscription(test, checks=None):
    '''Access Control List list by subscription operation'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric acl list')


def step_delete(test, checks=None):
    '''Access Control List delete operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric acl delete --resource-name {name} --resource-group {rg}')


class GA_AccessControlListsScenarioTest1(ScenarioTest):
    ''' Access Control List Scenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'name': CONFIG.get('ACCESS_CONTROL_LIST', 'name'),
            'rg': CONFIG.get('ACCESS_CONTROL_LIST', 'resource_group'),
            'location': CONFIG.get('ACCESS_CONTROL_LIST', 'location'),
            'configuration_type': CONFIG.get('ACCESS_CONTROL_LIST', 'configuration_type'),
            'default_action': CONFIG.get('ACCESS_CONTROL_LIST', 'default_action'),
            'dynamic_match_configurations': CONFIG.get('ACCESS_CONTROL_LIST', 'dynamic_match_configurations'),
            'updated_match_configurations': CONFIG.get('ACCESS_CONTROL_LIST', 'updated_match_configurations'),
            'match_configurations': CONFIG.get('ACCESS_CONTROL_LIST', 'match_configurations'),
        })

    def test_GA_accesscontrollists_scenario1(self):
        ''' test scenario for Access Control List CRUD operations'''
        call_scenario1(self)
