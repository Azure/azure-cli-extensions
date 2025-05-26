# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import jmespath
import collections
import json
import shutil
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from azure.cli.testsdk.checkers import JMESPathCheck
from azure.cli.testsdk.exceptions import JMESPathCheckAssertionError
from .utils import ApicServicePreparer, ApiAnalysisPreparer
from .constants import TEST_REGION, AWS_ACCESS_KEY_LINK, AWS_SECRET_ACCESS_KEY_LINK, AWS_REGION, USERASSIGNED_IDENTITY

current_dir = os.path.dirname(os.path.realpath(__file__))
test_assets_dir = os.path.join(current_dir, 'test_assets')


class ApiAnalysisCommandTests(ScenarioTest):
    async def _delete_existing_analyzer_configs(self):
        # Helper to delete all existing analyzer configs for the service
        try:
            configs = self.cmd('az apic api-analysis list -g {rg} -n {s}').get_output_in_json()
        except Exception:
            # If the list command fails (e.g., service not ready), skip deletion
            return
        if configs:
            for config in configs:
                config_name = config.get('name')
                if config_name:
                    try:
                        await self.cmd('az apic api-analysis delete -g {rg} -n {s} -c {config_name} --yes')
                    except Exception:
                        # Ignore errors if deletion fails (e.g., already deleted)
                        pass

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    async def test_api_analysis_create(self):
        await self._delete_existing_analyzer_configs()
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
    @ApiAnalysisPreparer()
    def test_api_analysis_list(self):
        self.cmd('az apic api-analysis list -g {rg} -n {s}', checks=[
            self.check('[0].name', '{config_name}'),
            self.check('[0].resourceGroup', '{rg}'),
            self.check('[0].type', 'Microsoft.ApiCenter/services/workspaces/analyzerConfigs')
        ])
    
    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApiAnalysisPreparer()
    def test_api_analysis_show(self):
        self.cmd('az apic api-analysis show -g {rg} -n {s} -c {config_name}', checks=[
            self.check('name', '{config_name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('type', 'Microsoft.ApiCenter/services/workspaces/analyzerConfigs')
        ])
    
    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApiAnalysisPreparer()
    def test_api_analysis_import_ruleset(self):
        self.kwargs.update({
            'ruleset_path': os.path.join(test_assets_dir, 'ruleset_test\\')
        })
        self.cmd('az apic api-analysis import-ruleset -g {rg} -n {s} -c {config_name} --path \'{ruleset_path}\' --no-wait', expect_failure=False)
    
    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApiAnalysisPreparer()
    def test_api_analysis_export_ruleset(self):
        self.kwargs.update({
            'ruleset_path': os.path.join(test_assets_dir, 'ruleset_test\\')
        })
        self.cmd('az apic api-analysis import-ruleset -g {rg} -n {s} -c {config_name} --path \'{ruleset_path}\'', expect_failure=False)
        
        self.kwargs.update({
            'ruleset_path_tmp': os.path.join(test_assets_dir, 'ruleset_test_tmp\\')
        })
        self.cmd('az apic api-analysis export-ruleset -g {rg} -n {s} -c {config_name} --path \'{ruleset_path_tmp}\'', expect_failure=False)

        try:
            # Check if the folder 'functions' and file 'ruleset.yml' exist in 'ruleset_path_tmp'
            functions_path = os.path.join(self.kwargs['ruleset_path_tmp'], 'functions')
            ruleset_file_path = os.path.join(self.kwargs['ruleset_path_tmp'], 'ruleset.yml')
            assert os.path.isdir(functions_path), f"Directory 'functions' not found in {self.kwargs['ruleset_path_tmp']}"
            assert os.path.isfile(ruleset_file_path), f"File 'ruleset.yml' not found in {self.kwargs['ruleset_path_tmp']}"
        finally:
            # Remove the 'ruleset_path_tmp' folder
            if os.path.exists(self.kwargs['ruleset_path_tmp']):
                shutil.rmtree(self.kwargs['ruleset_path_tmp'])

    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApiAnalysisPreparer()
    def test_api_analysis_update(self):
        filter_file = os.path.join(test_assets_dir, 'filter.json')
        with open(filter_file, 'r') as f:
            filter_content = f.read()
        filter_content = json.loads(filter_content)
        self.kwargs.update({
            'filter': filter_content
        })
        self.cmd('az apic api-analysis update -g {rg} -n {s} -c {config_name} --filter "{filter}"')
        self.cmd('az apic api-analysis show -g {rg} -n {s} -c {config_name}', checks=[
            self.check('name', '{config_name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('filter.apiDefinitions[0].value', '[\'openapi\', \'asyncapi\']')
        ])
    
    @ResourceGroupPreparer(name_prefix="clirg", location=TEST_REGION, random_name_length=32)
    @ApicServicePreparer()
    @ApiAnalysisPreparer()
    def test_api_analysis_delete(self):
        self.cmd('az apic api-analysis delete -g {rg} -n {s} -c {config_name} --yes')
        self.cmd('az apic api-analysis show -g {rg} -n {s} -c {config_name}', expect_failure=True)