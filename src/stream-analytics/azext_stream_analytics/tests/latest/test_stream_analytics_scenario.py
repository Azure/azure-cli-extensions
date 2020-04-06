# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import json

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class StreamAnalyticsScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_stream_analytics')
    @StorageAccountPreparer(parameter_name='storage_account')
    def test_stream_analytics(self, resource_group, storage_account):

        self.kwargs.update({
            'job_name': 'test_job',
            'input_name': 'input',
            'output_name': 'output',
            'transformation_name': 'transformation',
            'function_name': 'function',
            'storage_account': storage_account,
            'blob_name': 'blob'
        })

        self.cmd('stream-analytics job create '
                 '--resource-group {rg} '
                 '--name {job_name} '
                 '--location "West US" '
                 '--output-error-policy "Drop" '
                 '--events-outoforder-policy "Drop" '
                 '--events-outoforder-max-delay "0" '
                 '--events-late-arrival-max-delay "5" '
                 '--data-locale "en-US" ',
                 checks=[self.check('name', '{job_name}')])
        self.cmd('stream-analytics job update '
                 '--resource-group {rg} '
                 '--name {job_name} '
                 '--events-outoforder-max-delay 21 '
                 '--events-late-arrival-max-delay 13',
                 checks=[self.check('eventsOutOfOrderMaxDelayInSeconds', 21),
                         self.check('eventsLateArrivalMaxDelayInSeconds', 13)])
        self.cmd('stream-analytics job list '
                 '--resource-group {rg}',
                 checks=[self.check('length([])', 1)])
        self.cmd('stream-analytics job show '
                 '--resource-group {rg} '
                 '--name {job_name}',
                 checks=[self.check('name', '{job_name}')])

        self.kwargs['transformation_query'] = 'SELECT * INTO {} FROM {}'.format(
            self.kwargs['output_name'], self.kwargs['input_name'])
        self.cmd('stream-analytics transformation create '
                 '--resource-group {rg} '
                 '--job-name {job_name} '
                 '--name {transformation_name} '
                 '--streaming-units 12 '
                 '--transformation-query "{transformation_query}"',
                 checks=[self.check('name', '{transformation_name}')])
        self.cmd('stream-analytics transformation show '
                 '--resource-group {rg} '
                 '--job-name {job_name} '
                 '--name {transformation_name}',
                 checks=[self.check('name', '{transformation_name}')])
        self.cmd('stream-analytics transformation update '
                 '--resource-group {rg} '
                 '--job-name {job_name} '
                 '--name {transformation_name} '
                 '--streaming-units 6',
                 checks=[self.check('streamingUnits', 6)])

        # Prepare storage
        self.kwargs['account_key'] = \
            self.cmd('storage account keys list --account-name {storage_account}').get_output_in_json()[0]['value']
        self.cmd('storage container create --name {blob_name} --account-name {storage_account} '
                 '--account-key {account_key}')

        self.kwargs['input_datasource'] = json.dumps({
            "container": self.kwargs['blob_name'],
            "dateFormat": "yyyy/MM/dd",
            "pathPattern": "{date}/{time}",
            "sourcePartitionCount": 1,
            "storageAccounts": [
                {
                    "accountKey": self.kwargs['account_key'],
                    "accountName": self.kwargs['storage_account']
                }
            ],
            "timeFormat": "HH",
            "type": "Microsoft.Storage/Blob"
        })
        self.kwargs['input_serialization'] = json.dumps({
            "encoding": "UTF8",
            "fieldDelimiter": ",",
            "type": "Csv"
        })
        self.cmd('stream-analytics input create '
                 '--resource-group {rg} '
                 '--job-name {job_name} '
                 '--name {input_name} '
                 '--type Stream '
                 "--datasource '{input_datasource}' "
                 "--serialization '{input_serialization}'")
        self.cmd('stream-analytics input list '
                 '--resource-group {rg} '
                 '--job-name {job_name}',
                 checks=[self.check('length([])', 1)])
        self.cmd('stream-analytics input show '
                 '--resource-group {rg} '
                 '--job-name {job_name} '
                 '--name {input_name}',
                 checks=[self.check('name', '{input_name}')])
        self.cmd('stream-analytics input test '
                 '--resource-group {rg} '
                 '--job-name {job_name} '
                 '--name {input_name}')

        self.kwargs['output_datasource'] = json.dumps({
            "container": self.kwargs['blob_name'],
            "dateFormat": "yyyy/MM/dd",
            "pathPattern": "/output/{date}/{time}",
            "storageAccounts": [
                {
                    "accountKey": self.kwargs['account_key'],
                    "accountName": self.kwargs['storage_account']
                }
            ],
            "timeFormat": "HH",
            "type": "Microsoft.Storage/Blob"
        })
        self.kwargs['output_serialization'] = json.dumps({
            "encoding": "UTF8",
            "format": "LineSeparated",
            "type": "Json"
        })

        self.cmd('stream-analytics output create '
                 '--resource-group {rg} '
                 '--job-name {job_name} '
                 '--name {output_name} '
                 "--datasource '{output_datasource}' "
                 "--serialization '{output_serialization}'")
        self.cmd('stream-analytics output list '
                 '--resource-group {rg} '
                 '--job-name {job_name}',
                 checks=[self.check('length([])', 1)])
        self.cmd('stream-analytics output show '
                 '--resource-group {rg} '
                 '--job-name {job_name} '
                 '--name {output_name}',
                 checks=[self.check('name', '{output_name}')])
        self.cmd('stream-analytics output test '
                 '--resource-group {rg} '
                 '--job-name {job_name} '
                 '--name {output_name}')

        self.cmd('stream-analytics job start '
                 '--resource-group {rg} '
                 '--name {job_name} '
                 '--output-start-mode JobStartTime')

        self.cmd('stream-analytics job stop '
                 '--resource-group {rg} '
                 '--name {job_name}')

        self.kwargs['inputs'] = json.dumps([
            {
                'dataType': 'Any'
            }
        ])
        self.kwargs['function_output'] = json.dumps({
            "dataType": "Any"
        })
        self.kwargs['binding'] = json.dumps({
            "type": "Microsoft.StreamAnalytics/JavascriptUdf",
            "properties": {
                "script": "function (x, y) { return x + y; }"
            }
        })
        self.cmd('stream-analytics function create '
                 '--resource-group {rg} '
                 '--job-name {job_name} '
                 '--name {function_name} '
                 "--inputs '{inputs}' "
                 "--function-output '{function_output}' "
                 "--binding '{binding}'",
                 checks=[self.check('name', '{function_name}')])
        self.cmd('stream-analytics function list '
                 '--resource-group {rg} '
                 '--job-name {job_name}',
                 checks=[self.check('length([])', 1)])
        self.cmd('stream-analytics function show '
                 '--resource-group {rg} '
                 '--job-name {job_name} '
                 '--name {function_name}',
                 checks=[self.check('name', '{function_name}')])
        self.cmd('stream-analytics function test '
                 '--resource-group {rg} '
                 '--job-name {job_name} '
                 '--name {function_name}')

        self.cmd('stream-analytics function delete '
                 '--resource-group {rg} '
                 '--job-name {job_name} '
                 '--name {function_name}')

        self.cmd('stream-analytics output delete '
                 '--resource-group {rg} '
                 '--job-name {job_name} '
                 '--name {output_name}')

        self.cmd('stream-analytics input delete '
                 '--resource-group {rg} '
                 '--job-name {job_name} '
                 '--name {input_name}')

        self.cmd('stream-analytics job delete '
                 '--resource-group {rg} '
                 '--name {job_name}')

        self.cmd('stream-analytics quota show '
                 '--location "West US"')
