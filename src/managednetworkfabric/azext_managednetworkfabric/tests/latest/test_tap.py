# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Network Tap tests scenarios
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
    step_list_subscription(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_update_admin_state_Enable(test, checks=[])
    step_update_admin_state_Disable(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def step_create(test, checks=None):
    '''Network Tap create operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric tap create --resource-group {rg} --location {location} --resource-name {name} --network-packet-broker-id {npbId} --polling-type {pollingType} --destinations {destinations}', checks=checks)


def step_show(test, checks=None):
    '''Network Tap show operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric tap show --resource-name {name} --resource-group {rg}')


def step_list_resource_group(test, checks=None):
    '''Network Tap list by resource group operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric tap list --resource-group {rg}')


def step_list_subscription(test, checks=None):
    '''Network Tap list by subscription operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric tap list')


def step_update_admin_state_Enable(test, checks=None):
    '''Network Tap Update admin state operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric tap update-admin-state --resource-group {rg} --resource-name {name} --state {state_Enable}')


def step_update_admin_state_Disable(test, checks=None):
    '''Network Tap Update admin state operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric tap update-admin-state --resource-group {rg} --resource-name {name} --state {state_Disable}')


def step_delete(test, checks=None):
    '''Network Tap delete operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric tap delete --resource-name {name} --resource-group {rg}')


class GA_TapScenarioTest1(ScenarioTest):
    ''' Network Tap Scenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'name': CONFIG.get('NETWORK_TAP', 'name'),
            'rg': CONFIG.get('NETWORK_TAP', 'resource_group'),
            'location': CONFIG.get('NETWORK_TAP', 'location'),
            'npbId': CONFIG.get('NETWORK_TAP', 'network_packet_broker_id'),
            'pollingType': CONFIG.get('NETWORK_TAP', 'polling_type'),
            'destinations': CONFIG.get('NETWORK_TAP', 'destinations'),
            'state_Enable': CONFIG.get('NETWORK_TAP', 'state_Enable'),
            'state_Disable': CONFIG.get('NETWORK_TAP', 'state_Disable')
        })

    def test_GA_tap_scenario1(self):
        ''' test scenario for Network Tap CRUD operations'''
        call_scenario1(self)
