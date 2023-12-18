# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
NF post tests scenarios
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
    step_deprovision(test)
    cleanup_scenario1(test)


def step_deprovision(test, checks=None):
    '''nf deprovision operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric fabric deprovision --resource-name {deprovisionNFName} --resource-group {deprovisionNFRGName}')


class GA_NFDeProvisionScenarioTest1(ScenarioTest):
    ''' NFScenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'deprovisionNFRGName': CONFIG.get('NETWORK_FABRIC_PROVISION', 'deprovision_nf_resource_group'),
            'deprovisionNFName': CONFIG.get('NETWORK_FABRIC_PROVISION', 'deprovision_nf_name')
        })

    def test_GA_nf_deprovision_scenario1(self):
        ''' test scenario for NF deprovision operation'''
        call_scenario1(self)
