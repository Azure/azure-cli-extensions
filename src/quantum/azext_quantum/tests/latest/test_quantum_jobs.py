# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import unittest

from azure.cli.testsdk.scenario_tests import AllowLargeResponse, live_only
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from azure.cli.core.azclierror import InvalidArgumentValueError, AzureInternalError

from .utils import get_test_subscription_id, get_test_resource_group, get_test_workspace, get_test_workspace_location
from ..._client_factory import _get_data_credentials
from ...commands import transform_output
from ...operations.workspace import WorkspaceInfo
from ...operations.target import TargetInfo
from ...operations.job import _generate_submit_args, _parse_blob_url, _validate_max_poll_wait_secs, build

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class QuantumJobsScenarioTest(ScenarioTest):

    def test_jobs(self):
        # set current workspace:
        self.cmd(f'az quantum workspace set -g {get_test_resource_group()} -w {get_test_workspace()} -l {get_test_workspace_location()}')

        # list
        targets = self.cmd('az quantum target list -o json').get_output_in_json()
        assert len(targets) > 0

    def test_build(self):
        result = build(self, target_id='ionq.simulator', project='src\\quantum\\azext_quantum\\tests\\latest\\source_for_build_test\\QuantumRNG.csproj', target_capability='BasicQuantumFunctionality')
        assert result == {'result': 'ok'}

        self.testfile = open(os.path.join(os.path.dirname(__file__), 'source_for_build_test/obj/qsharp/config/qsc.rsp'))
        self.testdata = self.testfile.read()
        self.assertIn('TargetCapability:BasicQuantumFunctionality', self.testdata)
        self.testfile.close()

        try:
            build(self, target_id='ionq.simulator', project='src\\quantum\\azext_quantum\\tests\\latest\\source_for_build_test\\QuantumRNG.csproj', target_capability='BogusQuantumFunctionality')
            assert False
        except AzureInternalError as e:
            assert str(e) == "Failed to compile program."

    @live_only()
    def test_submit_args(self):
        test_location = get_test_workspace_location()
        test_workspace = get_test_workspace()
        test_resource_group = get_test_resource_group()
        ws = WorkspaceInfo(self, test_resource_group, test_workspace, test_location)
        target = TargetInfo(self, 'ionq.simulator')

        token = _get_data_credentials(self.cli_ctx, get_test_subscription_id()).get_token().token
        assert len(token) > 0

        job_parameters = {}
        job_parameters["key1"] = "value1"
        job_parameters["key2"] = "value2"

        args = _generate_submit_args(["--foo", "--bar"], ws, target, token, project=None,
                                     job_name=None, storage=None, shots=None, job_params=None)
        self.assertEquals(args[0], "dotnet")
        self.assertEquals(args[1], "run")
        self.assertEquals(args[2], "--no-build")
        self.assertIn("--", args)
        self.assertIn("submit", args)
        self.assertIn(test_workspace, args)
        self.assertIn(test_resource_group, args)
        self.assertIn("ionq.simulator", args)
        self.assertIn("--aad-token", args)
        self.assertIn(token, args)
        self.assertIn("--foo", args)
        self.assertIn("--bar", args)
        self.assertNotIn("--project", args)
        self.assertNotIn("--job-name", args)
        self.assertNotIn("--storage", args)
        self.assertNotIn("--shots", args)

        args = _generate_submit_args(["--foo", "--bar"], ws, target, token, "../other/path",
                                     "job-name", 1234, "az-stor", job_parameters)
        self.assertEquals(args[0], "dotnet")
        self.assertEquals(args[1], "run")
        self.assertEquals(args[2], "--no-build")
        self.assertIn("../other/path", args)
        self.assertIn("job-name", args)
        self.assertIn("az-stor", args)
        self.assertIn(1234, args)
        self.assertIn("--project", args)
        self.assertIn("--job-name", args)
        self.assertIn("--storage", args)
        self.assertIn("--shots", args)
        self.assertIn("--job-params", args)
        self.assertIn("key1=value1", args)
        self.assertIn("key2=value2", args)

    def test_parse_blob_url(self):
        sas = "sv=2018-03-28&sr=c&sig=some-sig&sp=racwl"
        url = f"https://getest2.blob.core.windows.net/qio/rawOutputData?{sas}"
        args = _parse_blob_url(url)

        self.assertEquals(args['account_name'], "getest2")
        self.assertEquals(args['container'], "qio")
        self.assertEquals(args['blob'], "rawOutputData")
        self.assertEquals(args['sas_token'], sas)

    def test_transform_output(self):
        # Call with a good histogram
        test_job_results = '{"Histogram":["[0,0,0]",0.125,"[1,0,0]",0.125,"[0,1,0]",0.125,"[1,1,0]",0.125]}'
        table = transform_output(json.loads(test_job_results))
        table_row = table[0]
        hist_row = table_row['']
        second_char = hist_row[1]
        self.assertEquals(second_char, "\u2588")    # Expecting a "Full Block" character here 

        # Give it a malformed histogram
        test_job_results = '{"Histogram":["[0,0,0]",0.125,"[1,0,0]",0.125,"[0,1,0]",0.125,"[1,1,0]"]}'
        table = transform_output(json.loads(test_job_results))
        self.assertEquals(table, json.loads(test_job_results))    # No transform should be done if input param is bad

        # Call with output from a failed job
        test_job_results = \
        '{\
            "beginExecutionTime": "2022-02-25T18:57:26.093000+00:00",\
            "cancellationTime": null,\
            "containerUri": "https://foo...",\
            "costEstimate": null,\
            "creationTime": "2022-02-25T18:56:53.275035+00:00",\
            "endExecutionTime": "2022-02-25T18:57:26.093000+00:00",\
            "errorData": {\
                "code": "InsufficientResources",\
                "message": "Too many qubits requested"\
            },\
            "id": "11111111-2222-3333-4444-555555555555",\
            "inputDataFormat": "microsoft.ionq-ir.v2",\
            "inputDataUri": "https://bar...",\
            "inputParams": {\
                "shots": "500"\
            },\
            "isCancelling": false,\
            "metadata": {\
                "entryPointInput": {\"Qubits\":null},\
                "outputMappingBlobUri": "https://baz..."\
            },\
            "name": "",\
            "outputDataFormat": "microsoft.quantum-results.v1",\
            "outputDataUri": "https://quux...",\
            "providerId": "ionq",\
            "status": "Failed",\
            "tags": [],\
            "target": "ionq.simulator"\
        }'

        table = transform_output(json.loads(test_job_results))
        self.assertEquals(table['Status'], "Failed")
        self.assertEquals(table['Error Code'], "InsufficientResources")
        self.assertEquals(table['Error Message'], "Too many qubits requested")
        self.assertEquals(table['Target'], "ionq.simulator")
        self.assertEquals(table['Job ID'], "11111111-2222-3333-4444-555555555555")
        self.assertEquals(table['Submission Time'], "2022-02-25T18:56:53.275035+00:00")

        # Call with missing "status", "code", "message", "target", "id", and "creationTime"
        test_job_results = \
        '{\
            "beginExecutionTime": "2022-02-25T18:57:26.093000+00:00",\
            "cancellationTime": null,\
            "containerUri": "https://foo...",\
            "costEstimate": null,\
            "endExecutionTime": "2022-02-25T18:57:26.093000+00:00",\
            "errorData": {\
            },\
            "inputDataFormat": "microsoft.ionq-ir.v2",\
            "inputDataUri": "https://bar...",\
            "inputParams": {\
                "shots": "500"\
            },\
            "isCancelling": false,\
            "metadata": {\
                "entryPointInput": {\"Qubits\":null},\
                "outputMappingBlobUri": "https://baz..."\
            },\
            "name": "",\
            "outputDataFormat": "microsoft.quantum-results.v1",\
            "outputDataUri": "https://quux...",\
            "providerId": "ionq",\
            "tags": []\
        }'

        table = transform_output(json.loads(test_job_results))
        notFound = "Not found"
        self.assertEquals(table['Status'], notFound)
        self.assertEquals(table['Error Code'], notFound)
        self.assertEquals(table['Error Message'], notFound)
        self.assertEquals(table['Target'], notFound)
        self.assertEquals(table['Job ID'], notFound)
        self.assertEquals(table['Submission Time'], notFound)

    def test_validate_max_poll_wait_secs(self):
        wait_secs = _validate_max_poll_wait_secs(1)
        self.assertEquals(type(wait_secs), float)
        self.assertEquals(wait_secs, 1.0)

        wait_secs = _validate_max_poll_wait_secs("60")
        self.assertEquals(type(wait_secs), float)
        self.assertEquals(wait_secs, 60.0)

        # Invalid values should raise errors
        try:
            wait_secs = _validate_max_poll_wait_secs(0.999999999)
            assert False
        except InvalidArgumentValueError as e:
            assert str(e) == "--max-poll-wait-secs parameter is not valid: 0.999999999"

        try:
            wait_secs = _validate_max_poll_wait_secs(-1.0)
            assert False
        except InvalidArgumentValueError as e:
            assert str(e) == "--max-poll-wait-secs parameter is not valid: -1.0"

        try:
            wait_secs = _validate_max_poll_wait_secs("foobar")
            assert False
        except InvalidArgumentValueError as e:
            assert str(e) == "--max-poll-wait-secs parameter is not valid: foobar"
