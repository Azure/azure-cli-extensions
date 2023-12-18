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
    step_validateconfiguration(test)
    cleanup_scenario1(test)


def step_validateconfiguration(test, checks=None):
    '''nf validate configuration operation'''
    if checks is None:
        checks = []
    test.cmd(
        'az networkfabric fabric validate-configuration --resource-name {validateNFName} --resource-group {validateNFRGName} --validate-action {validateAction}')


class GA_NFValidateScenarioTest1(ScenarioTest):
    ''' NFScenario test'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'validateNFRGName': CONFIG.get('NETWORK_FABRIC', 'validate_nf_resource_group'),
            'validateNFName': CONFIG.get('NETWORK_FABRIC', 'validate_nf_name'),
            'validateAction': CONFIG.get('NETWORK_FABRIC', 'validate_action')
        })

    def test_GA_nf_validate_scenario1(self):
        ''' test scenario for NF validate operations'''
        call_scenario1(self)
