# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import jmespath
import collections
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from azure.cli.testsdk.checkers import JMESPathCheck
from azure.cli.testsdk.exceptions import JMESPathCheckAssertionError
from .utils import ApicServicePreparer, ApimServicePreparer
from .constants import TEST_REGION, AWS_ACCESS_KEY_LINK, AWS_SECRET_ACCESS_KEY_LINK, AWS_REGION, USERASSIGNED_IDENTITY


class ApiAnalysisCommandTests(ScenarioTest):

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    def test_api_analysis_create(self):
        # create an API Analysis configuration
        self.kwargs.update({
            'config_name': self.create_random_name(prefix='clianalysisconfig', length=24)
        })
        self.cmd('az apic api-analysis create -g {rg} -n {s} -c {config_name}', checks=[
            self.check('name', '{config_name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('type', 'Microsoft.ApiCenter/services/workspaces/analyzerConfigs')
        ])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    def test_api_analysis_list(self):
        # create an API Analysis configuration
        self.kwargs.update({
            'config_name': self.create_random_name(prefix='clianalysisconfig', length=24)
        })
        self.cmd('az apic api-analysis create -g {rg} -n {s} -c {config_name}', checks=[
            self.check('name', '{config_name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('type', 'Microsoft.ApiCenter/services/workspaces/analyzerConfigs')
        ])

        self.cmd('az apic api-analysis list -g {rg} -n {s}', checks=[
            self.check('[0].name', '{config_name}'),
            self.check('[0].resourceGroup', '{rg}'),
            self.check('[0].type', 'Microsoft.ApiCenter/services/workspaces/analyzerConfigs')
        ])
