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
    step_update(test, checks=[])
    cleanup_scenario1(test)


def step_update(test, checks=None):
    '''l3domain update operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric l3domain update --resource-group {rg} --resource-name {name} --aggregate-route-configuration {updatedAggregateRouteConf}', checks=checks)


class GA_L3DomainUpdateScenarioTest1(ScenarioTest):
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
            'updatedAggregateRouteConf': CONFIG.get('L3_ISOLATION_DOMAIN', 'updated_aggregate_route_conf')
        })

    def test_GA_l3domainupdate_scenario1(self):
        ''' test scenario for L3 Domain CRUD operations'''
        call_scenario1(self)
