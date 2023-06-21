# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
DefaultCNINetwork tests scenarios
"""

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from .config import CONFIG


def setup_scenario1(test):
    ''' Env setup_scenario1 '''


def cleanup_scenario1(test):
    '''Env cleanup_scenario1 '''


def call_scenario1(test):
    ''' # Testcase: scenario1'''
    setup_scenario1(test)
    step_create(test, checks=[
        test.check('name', '{name}'),
        test.check('provisioningState', 'Succeeded')
    ])
    step_update(test, checks=[
        test.check('tags', '{tagsUpdate}'),
        test.check('provisioningState', 'Succeeded')
    ])
    step_show(test, checks=[])
    step_list_subscription(test, checks=[])
    step_list_resource_group(test, checks=[])
    step_delete(test, checks=[])
    cleanup_scenario1(test)


def step_create(test, checks=None):
    '''DefaultCNINetwork create operation'''
    if checks is None:
        checks = []
    test.cmd('az networkcloud defaultcninetwork create --name {name} --extended-location '
             ' name={extendedLocation} type="CustomLocation" --location {location} '
             ' --cni-bgp-configuration {cniBgpConfiguration} --ip-allocation-type {ipAllocationType}'
             ' --ipv4-connected-prefix {ipv4prefix} --ipv6-connected-prefix {ipv6prefix}  '
             ' --l3-isolation-domain-id  {l3_isolation_domain_id} --vlan  {vlan}'
             ' --tags {tags} --resource-group {rg}', checks=checks)


def step_show(test, checks=None):
    '''DefaultCNINetwork show operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkcloud defaultcninetwork show --name {name} --resource-group {rg}')


def step_delete(test, checks=None):
    '''DefaultCNINetwork delete operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkcloud defaultcninetwork delete --name {name} --resource-group {rg} -y')


def step_list_resource_group(test, checks=None):
    '''DefaultCNINetwork list by resource group operation'''
    if checks is None:
        checks = []
    test.cmd('az networkcloud defaultcninetwork list --resource-group {rg}')


def step_list_subscription(test, checks=None):
    '''DefaultCNINetwork list by subscription operation'''
    if checks is None:
        checks = []
    test.cmd('az networkcloud defaultcninetwork list')


def step_update(test, checks=None):
    '''DefaultCNINetwork update operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkcloud defaultcninetwork update --name {name} --tags {tagsUpdate} --resource-group {rg}')


class DefaultCNINetworkScenarioTest(ScenarioTest):
    ''' DefaultCNINetwork scenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'name': self.create_random_name(prefix="cli-test-defaultcni-", length=24),
            'location': CONFIG.get('DEFAULT_CNI_NETWORK', 'location'),
            'extendedLocation': CONFIG.get('DEFAULT_CNI_NETWORK', 'extended_location'),
            'tags': CONFIG.get('DEFAULT_CNI_NETWORK', 'tags'),
            'tagsUpdate': CONFIG.get('DEFAULT_CNI_NETWORK', 'tags_update'),
            "type": CONFIG.get('DEFAULT_CNI_NETWORK', 'type'),
            'vlan': CONFIG.get('DEFAULT_CNI_NETWORK', 'vlan'),
            "ipAllocationType": CONFIG.get('DEFAULT_CNI_NETWORK', 'ip_allocation_type'),
            "cniBgpConfiguration": CONFIG.get('DEFAULT_CNI_NETWORK', 'cni_bgp_configuration'),
            "ipv4prefix": CONFIG.get('DEFAULT_CNI_NETWORK', 'ipv4prefix'),
            "ipv6prefix": CONFIG.get('DEFAULT_CNI_NETWORK', 'ipv6prefix'),
            "l3_isolation_domain_id": CONFIG.get('DEFAULT_CNI_NETWORK', 'l3_isolation_domain_id'),
        })

    @ResourceGroupPreparer(name_prefix='clitest_rg'[:7], key='rg', parameter_name='rg')
    def test_defaultcninetwork_scenario1(self):
        ''' test scenario for DefaultCNINetwork CRUD operations'''
        call_scenario1(self)
