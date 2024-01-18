# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
L3 Domain tests scenarios
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
    step_update_admin_state_Enable(test, checks=[])
    step_update_admin_state_Disable(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def step_create(test, checks=None):
    '''l3domain create operation'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric l3domain create --resource-group {rg} --resource-name {name} --location {location} --nf-id {nf_id}'
             ' --redistribute-connected-subnets {redistributeConnectedSubnets} --redistribute-static-routes {redistributeStaticRoutes}'
             ' --aggregate-route-configuration {aggregateRouteConf} --connected-subnet-route-policy {connectedSubnetRoutePolicy}', checks=checks)


def step_show(test, checks=None):
    '''l3domain show operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric l3domain show --resource-name {name} --resource-group {rg}')


def step_update(test, checks=None):
    '''l3domain update operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric l3domain update --resource-group {rg} --resource-name {name} --aggregate-route-configuration {updatedAggregateRouteConf}', checks=checks)


def step_list_resource_group(test, checks=None):
    '''l3domain list by resource group operation'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric l3domain list --resource-group {rg}')


def step_list_subscription(test, checks=None):
    '''l3domain list by subscription operation'''
    if checks is None:
        checks = []
    test.cmd('az networkfabric l3domain list')


def step_update_admin_state_Enable(test, checks=None):
    '''l3domain Update admin state operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric l3domain update-admin-state --resource-group {rg} --resource-name {post_name} --state {state_Enable}')


def step_update_admin_state_Disable(test, checks=None):
    '''l3domain Update admin state operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric l3domain update-admin-state --resource-group {rg} --resource-name {post_name} --state {state_Disable}')


def step_delete(test, checks=None):
    '''l3domain delete operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric l3domain delete --resource-name {name} --resource-group {rg}')


class GA_L3DomainScenarioTest1(ScenarioTest):
    ''' L3 Domain Scenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'name': CONFIG.get('L3_ISOLATION_DOMAIN', 'name'),
            'rg': CONFIG.get('L3_ISOLATION_DOMAIN', 'resource_group'),
            'location': CONFIG.get('L3_ISOLATION_DOMAIN', 'location'),
            'nf_id': CONFIG.get('L3_ISOLATION_DOMAIN', 'nf_id'),
            'redistributeConnectedSubnets': CONFIG.get('L3_ISOLATION_DOMAIN', 'redistribute_connected_subnets'),
            'redistributeStaticRoutes': CONFIG.get('L3_ISOLATION_DOMAIN', 'redistribute_static_routes'),
            'connectedSubnetRoutePolicy': CONFIG.get('L3_ISOLATION_DOMAIN', 'connected_subnet_route_policy'),
            'aggregateRouteConf': CONFIG.get('L3_ISOLATION_DOMAIN', 'aggregate_route_conf'),
            'updatedAggregateRouteConf': CONFIG.get('L3_ISOLATION_DOMAIN', 'updated_aggregate_route_conf'),
            'post_name': CONFIG.get('L3_ISOLATION_DOMAIN', 'post_name'),
            'state_Enable': CONFIG.get('L3_ISOLATION_DOMAIN', 'state_Enable'),
            'state_Disable': CONFIG.get('L3_ISOLATION_DOMAIN', 'state_Disable')
        })

    def test_GA_l3domain_scenario1(self):
        ''' test scenario for L3 Domain CRUD operations'''
        call_scenario1(self)
