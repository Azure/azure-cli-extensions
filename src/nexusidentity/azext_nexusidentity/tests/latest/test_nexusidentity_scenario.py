# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

'''
Nexus Identity Ssh-Key Geneation Scenario Test
'''

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer

def setup_scenario1(test):
    ''' Env setup_scenario1 '''
    pass


def cleanup_scenario1(test):
    '''Env cleanup_scenario1 '''
    pass

def call_scenario1(test):
    ''' # Testcase: scenario1'''
    setup_scenario1(test)
    step_gen_keys(test, checks=[])
    cleanup_scenario1(test)

def step_gen_keys(test, checks=None):
    '''Generate Nexus Identity ssh keys '''
    if checks is None:
        checks = []
    test.cmd('az nexusidentity gen-keys')

class NexusidentityScenarioTest(ScenarioTest):
    ''' Nexus Identity Ssh-Key Generation Scenario Test '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_nexusidentity_scenario1(self):

        # Testcase: scenario1
        call_scenario1(self)