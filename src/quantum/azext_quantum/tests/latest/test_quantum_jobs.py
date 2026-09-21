# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import pytest
import random
import time
import unittest
import unittest.mock
from urllib.parse import urlparse, parse_qs

from azure.cli.testsdk.scenario_tests import AllowLargeResponse, live_only
from azure.cli.testsdk import ScenarioTest
from azure.cli.core.azclierror import InvalidArgumentValueError, RequiredArgumentMissingError, AzureInternalError, ResourceNotFoundError as CliResourceNotFoundError
from azure.core.exceptions import ResourceNotFoundError as AzureResourceNotFoundError

from .utils import get_test_resource_group, get_test_workspace, get_test_workspace_location, issue_cmd_with_param_missing, get_test_workspace_storage, get_test_workspace_random_name
from ...commands import transform_output
from ...operations.job import (
    list_files,
    download_file,
    update,
    _validate_max_poll_wait_secs,
    _convert_numeric_params,
    _construct_filter_query,
    _construct_orderby_expression,
    ERROR_MSG_INVALID_PRIORITY_ARGUMENT,
    ERROR_MSG_INVALID_ORDER_ARGUMENT,
    ERROR_MSG_MISSING_ORDERBY_ARGUMENT)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class QuantumJobsScenarioTest(ScenarioTest):

    @live_only()
    def test_jobs(self):
        # set current workspace:
        self.cmd(f'az quantum workspace set -g {get_test_resource_group()} -w {get_test_workspace()}')

        # list
        targets = self.cmd('az quantum target list -o json').get_output_in_json()
        assert len(targets) > 0

    # @pytest.fixture(autouse=True)
    # def _pass_fixtures(self, capsys):
    #     self.capsys = capsys
    # # See "TODO" in issue_cmd_with_param_missing un utils.py

    def test_job_errors(self):
        issue_cmd_with_param_missing(self, "az quantum job cancel", "az quantum job cancel -g MyResourceGroup -w MyWorkspace -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy\nCancel an Azure Quantum job by id.")
        issue_cmd_with_param_missing(self, "az quantum job delete", "az quantum job delete -g MyResourceGroup -w MyWorkspace -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy\nDelete an Azure Quantum job by id.")
        issue_cmd_with_param_missing(self, "az quantum job update", "az quantum job update -g MyResourceGroup -w MyWorkspace -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy --job-name 'My new name'\nUpdate an Azure Quantum job by id.")
        issue_cmd_with_param_missing(self, "az quantum job output", "az quantum job output -g MyResourceGroup -w MyWorkspace -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy -o table\nPrint the results of a successful Azure Quantum job.")
        issue_cmd_with_param_missing(self, "az quantum job file list", "az quantum job file list -g MyResourceGroup -w MyWorkspace -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy -o table\nList the files stored in a job's output storage container.")
        issue_cmd_with_param_missing(self, "az quantum job file download", "az quantum job file download -g MyResourceGroup -w MyWorkspace -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy -n rawOutputData\nDownload a file from a job's output storage container.")
        issue_cmd_with_param_missing(self, "az quantum job show", "az quantum job show -g MyResourceGroup -w MyWorkspace -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy --query status\nGet the status of an Azure Quantum job.")
        issue_cmd_with_param_missing(self, "az quantum job wait", "az quantum job wait -g MyResourceGroup -w MyWorkspace -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy --max-poll-wait-secs 60 -o table\nWait for completion of a job, check at 60 second intervals.")

    @unittest.mock.patch('azext_quantum.operations.job.cf_jobs')
    @unittest.mock.patch('azext_quantum.operations.job.ContainerClient')
    @unittest.mock.patch('azext_quantum.operations.job.Workspace')
    @unittest.mock.patch('azext_quantum.operations.job._get_data_credentials')
    @unittest.mock.patch('azext_quantum.operations.job.WorkspaceInfo')
    def test_list_files(self, mock_workspace_info, mock_get_data_credentials, mock_workspace, mock_container_client, mock_cf_jobs):
        import datetime
        info = mock_workspace_info.return_value
        info.subscription = "sub"
        info.resource_group = "rg"
        info.name = "ws"

        mock_cf_jobs.return_value.get.return_value.container_uri = "https://acct.blob.core.windows.net/job-id?sas"

        blob1 = unittest.mock.MagicMock()
        blob1.name = "rawOutputData"
        blob1.size = 42
        blob1.last_modified = datetime.datetime(2026, 1, 15, 12, 0, 0)

        blob2 = unittest.mock.MagicMock()
        blob2.name = "atom-logs.txt"
        blob2.size = 1024
        blob2.last_modified = None

        mock_container_client.from_container_url.return_value.list_blobs.return_value = [blob1, blob2]

        cmd = unittest.mock.MagicMock()
        job_id = "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"

        result = list_files(cmd, job_id, "rg", "ws")

        mock_cf_jobs.return_value.get.assert_called_once_with("sub", "rg", "ws", job_id)
        mock_container_client.from_container_url.assert_called_once_with("https://acct.blob.core.windows.net/job-id?sas")
        self.assertEqual(result, [
            {"name": "rawOutputData", "size": 42, "lastModified": "2026-01-15T12:00:00"},
            {"name": "atom-logs.txt", "size": 1024, "lastModified": None}
        ])

    @unittest.mock.patch('azext_quantum.operations.job.cf_jobs')
    @unittest.mock.patch('azext_quantum.operations.job.ContainerClient')
    @unittest.mock.patch('azext_quantum.operations.job.Workspace')
    @unittest.mock.patch('azext_quantum.operations.job._get_data_credentials')
    @unittest.mock.patch('azext_quantum.operations.job.WorkspaceInfo')
    def test_list_files_raises_when_container_missing(self, mock_workspace_info, mock_get_data_credentials, mock_workspace, mock_container_client, mock_cf_jobs):
        info = mock_workspace_info.return_value
        info.subscription = "sub"
        info.resource_group = "rg"
        info.name = "ws"

        mock_cf_jobs.return_value.get.return_value.container_uri = "https://acct.blob.core.windows.net/job-id?sas"
        mock_container_client.from_container_url.return_value.list_blobs.side_effect = AzureResourceNotFoundError("not found")

        cmd = unittest.mock.MagicMock()
        job_id = "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"

        with self.assertRaises(CliResourceNotFoundError):
            list_files(cmd, job_id, "rg", "ws")

    @unittest.mock.patch('azext_quantum.operations.job.cf_jobs')
    @unittest.mock.patch('azext_quantum.operations.job.ContainerClient')
    @unittest.mock.patch('azext_quantum.operations.job.Workspace')
    @unittest.mock.patch('azext_quantum.operations.job._get_data_credentials')
    @unittest.mock.patch('azext_quantum.operations.job.WorkspaceInfo')
    def test_download_file_raises_when_file_missing(self, mock_workspace_info, mock_get_data_credentials, mock_workspace, mock_container_client, mock_cf_jobs):
        info = mock_workspace_info.return_value
        info.subscription = "sub"
        info.resource_group = "rg"
        info.name = "ws"

        mock_cf_jobs.return_value.get.return_value.container_uri = "https://acct.blob.core.windows.net/job-id?sas"
        blob_client = mock_container_client.from_container_url.return_value.get_blob_client.return_value
        blob_client.download_blob.side_effect = AzureResourceNotFoundError("not found")

        cmd = unittest.mock.MagicMock()
        job_id = "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"

        with self.assertRaises(CliResourceNotFoundError):
            download_file(cmd, job_id, "missingFile", "rg", "ws")

    @unittest.mock.patch('azext_quantum.operations.job.cf_jobs')
    @unittest.mock.patch('azext_quantum.operations.job.ContainerClient')
    @unittest.mock.patch('azext_quantum.operations.job.Workspace')
    @unittest.mock.patch('azext_quantum.operations.job._get_data_credentials')
    @unittest.mock.patch('azext_quantum.operations.job.WorkspaceInfo')
    def test_download_file(self, mock_workspace_info, mock_get_data_credentials, mock_workspace, mock_container_client, mock_cf_jobs):
        import tempfile

        info = mock_workspace_info.return_value
        info.subscription = "sub"
        info.resource_group = "rg"
        info.name = "ws"

        mock_cf_jobs.return_value.get.return_value.container_uri = "https://acct.blob.core.windows.net/job-id?sas"

        blob_client = mock_container_client.from_container_url.return_value.get_blob_client.return_value
        file_content = b"hello world"

        def fake_readinto(stream):
            stream.write(file_content)
            return len(file_content)

        blob_client.download_blob.return_value.readinto.side_effect = fake_readinto

        cmd = unittest.mock.MagicMock()
        job_id = "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"

        with tempfile.TemporaryDirectory() as tmp_dir:
            result = download_file(cmd, job_id, "rawOutputData", "rg", "ws", dest=tmp_dir)

            expected_path = os.path.join(tmp_dir, "rawOutputData")
            self.assertTrue(os.path.exists(expected_path))
            with open(expected_path, "rb") as file_handle:
                self.assertEqual(file_handle.read(), file_content)

            mock_cf_jobs.return_value.get.assert_called_once_with("sub", "rg", "ws", job_id)
            mock_container_client.from_container_url.return_value.get_blob_client.assert_called_once_with("rawOutputData")
            self.assertEqual(result["name"], "rawOutputData")
            self.assertEqual(result["path"], os.path.abspath(expected_path))
            self.assertEqual(result["size"], len(file_content))

    @unittest.mock.patch('azext_quantum.operations.job.cf_jobs')
    @unittest.mock.patch('azext_quantum.operations.job.ContainerClient')
    @unittest.mock.patch('azext_quantum.operations.job.Workspace')
    @unittest.mock.patch('azext_quantum.operations.job._get_data_credentials')
    @unittest.mock.patch('azext_quantum.operations.job.WorkspaceInfo')
    def test_download_file_sanitizes_traversal_name(self, mock_workspace_info, mock_get_data_credentials, mock_workspace, mock_container_client, mock_cf_jobs):
        import tempfile

        info = mock_workspace_info.return_value
        info.subscription = "sub"
        info.resource_group = "rg"
        info.name = "ws"

        mock_cf_jobs.return_value.get.return_value.container_uri = "https://acct.blob.core.windows.net/job-id?sas"

        blob_client = mock_container_client.from_container_url.return_value.get_blob_client.return_value
        file_content = b"payload"

        def fake_readinto(stream):
            stream.write(file_content)
            return len(file_content)

        blob_client.download_blob.return_value.readinto.side_effect = fake_readinto

        cmd = unittest.mock.MagicMock()
        job_id = "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"

        with tempfile.TemporaryDirectory() as tmp_dir:
            target_dir = os.path.join(tmp_dir, "downloads")
            os.makedirs(target_dir)

            result = download_file(cmd, job_id, "../../evil.txt", "rg", "ws", dest=target_dir)

            # Only the basename is used, so the file stays inside target_dir
            # and never escapes via the traversal segments in the blob name.
            safe_path = os.path.join(target_dir, "evil.txt")
            self.assertTrue(os.path.exists(safe_path))
            self.assertFalse(os.path.exists(os.path.join(tmp_dir, "evil.txt")))
            self.assertEqual(result["path"], os.path.abspath(safe_path))

    @unittest.mock.patch('azext_quantum.operations.job.cf_jobs')
    @unittest.mock.patch('azext_quantum.operations.job.ContainerClient')
    @unittest.mock.patch('azext_quantum.operations.job.Workspace')
    @unittest.mock.patch('azext_quantum.operations.job._get_data_credentials')
    @unittest.mock.patch('azext_quantum.operations.job.WorkspaceInfo')
    def test_download_file_creates_missing_output_directory(self, mock_workspace_info, mock_get_data_credentials, mock_workspace, mock_container_client, mock_cf_jobs):
        import tempfile

        info = mock_workspace_info.return_value
        info.subscription = "sub"
        info.resource_group = "rg"
        info.name = "ws"

        mock_cf_jobs.return_value.get.return_value.container_uri = "https://acct.blob.core.windows.net/job-id?sas"

        blob_client = mock_container_client.from_container_url.return_value.get_blob_client.return_value
        file_content = b"payload"

        def fake_readinto(stream):
            stream.write(file_content)
            return len(file_content)

        blob_client.download_blob.return_value.readinto.side_effect = fake_readinto

        cmd = unittest.mock.MagicMock()
        job_id = "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"

        with tempfile.TemporaryDirectory() as tmp_dir:
            # A non-existent --dest is created and treated as a directory.
            new_dir = os.path.join(tmp_dir, "downloads")

            result = download_file(cmd, job_id, "outputData", "rg", "ws", dest=new_dir)

            expected_path = os.path.join(new_dir, "outputData")
            self.assertTrue(os.path.isdir(new_dir))
            self.assertTrue(os.path.exists(expected_path))
            self.assertEqual(result["path"], os.path.abspath(expected_path))

    @unittest.mock.patch('azext_quantum.operations.job.cf_jobs')
    @unittest.mock.patch('azext_quantum.operations.job.WorkspaceInfo')
    def test_job_update(self, mock_workspace_info, mock_cf_jobs):
        info = mock_workspace_info.return_value
        info.subscription = "sub"
        info.resource_group = "rg"
        info.name = "ws"
        info.endpoint = "endpoint"
        client = mock_cf_jobs.return_value
        client.get.return_value.as_dict.return_value = {"id": "job-id"}
        cmd = unittest.mock.MagicMock()
        job_id = "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"

        # Calling with no updatable fields should raise.
        with self.assertRaises(RequiredArgumentMissingError):
            update(cmd, job_id, "rg", "ws")

        # An invalid priority value should raise.
        with self.assertRaises(InvalidArgumentValueError) as context:
            update(cmd, job_id, "rg", "ws", job_priority="NotAPriority")
        self.assertEqual(str(context.exception), ERROR_MSG_INVALID_PRIORITY_ARGUMENT)

        # An empty or whitespace-only job name is ignored, so with no other fields it should raise.
        with self.assertRaises(RequiredArgumentMissingError):
            update(cmd, job_id, "rg", "ws", job_name="   ")

        # Passing only blank/whitespace tags is an explicit request to clear all tags,
        # which sends an empty list rather than raising.
        result = update(cmd, job_id, "rg", "ws", job_tags=["", "   "])
        client.update.assert_called_once_with("sub", "rg", "ws", job_id, {"tags": []})
        self.assertEqual(result, {"id": "job-id"})
        client.update.reset_mock()
        client.get.reset_mock()

        # A valid update should build a merge-patch with only the provided fields
        # and return the refreshed job. Surrounding whitespace is trimmed and blank
        # tags are dropped.
        result = update(cmd, job_id, "rg", "ws", job_name="  New name  ", job_priority="High", job_tags=["a", "  ", "b "])
        client.update.assert_called_once_with("sub", "rg", "ws", job_id, {"name": "New name", "priority": "High", "tags": ["a", "b"]})
        client.get.assert_called_once_with("sub", "rg", "ws", job_id)
        self.assertEqual(result, {"id": "job-id"})

    def test_transform_output(self):
        # Call with a good histogram
        test_job_results = '{"Histogram":["[0,0,0]",0.125,"[1,0,0]",0.125,"[0,1,0]",0.125,"[1,1,0]",0.125]}'
        table = transform_output(json.loads(test_job_results))
        table_row = table[0]
        hist_row = table_row['']
        second_char = hist_row[1]
        self.assertEqual(second_char, "\u2588")    # Expecting a "Full Block" character here

        # Give it a malformed histogram
        test_job_results = '{"Histogram":["[0,0,0]",0.125,"[1,0,0]",0.125,"[0,1,0]",0.125,"[1,1,0]"]}'
        table = transform_output(json.loads(test_job_results))
        self.assertEqual(table, json.loads(test_job_results))    # No transform should be done if input param is bad

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
        self.assertEqual(table['Status'], "Failed")
        self.assertEqual(table['Error Code'], "InsufficientResources")
        self.assertEqual(table['Error Message'], "Too many qubits requested")
        self.assertEqual(table['Target'], "ionq.simulator")
        self.assertEqual(table['Job ID'], "11111111-2222-3333-4444-555555555555")
        self.assertEqual(table['Submission Time'], "2022-02-25T18:56:53.275035+00:00")

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
        self.assertEqual(table['Status'], notFound)
        self.assertEqual(table['Error Code'], notFound)
        self.assertEqual(table['Error Message'], notFound)
        self.assertEqual(table['Target'], notFound)
        self.assertEqual(table['Job ID'], notFound)
        self.assertEqual(table['Submission Time'], notFound)

    def test_validate_max_poll_wait_secs(self):
        wait_secs = _validate_max_poll_wait_secs(1)
        self.assertEqual(type(wait_secs), float)
        self.assertEqual(wait_secs, 1.0)

        wait_secs = _validate_max_poll_wait_secs("60")
        self.assertEqual(type(wait_secs), float)
        self.assertEqual(wait_secs, 60.0)

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

    def test_convert_numeric_params(self):
        # Show that it converts numeric strings, but doesn't modify params that are already numeric
        test_job_params = {"integer1": "1", "float1.5": "1.5", "integer2": 2, "float2.5": 2.5, "integer3": "3", "float3.5": "3.5"}
        _convert_numeric_params(test_job_params)
        assert test_job_params == {"integer1": 1, "float1.5": 1.5, "integer2": 2, "float2.5": 2.5, "integer3": 3, "float3.5": 3.5}

        # Make sure it doesn't modify non-numeric strings
        test_job_params = {"string1": "string_value1", "string2": "string_value2", "string3": "string_value3"}
        _convert_numeric_params(test_job_params)
        assert test_job_params == {"string1": "string_value1", "string2": "string_value2", "string3": "string_value3"}

        # Make sure it doesn't modify the "tags" list
        test_job_params = {"string1": "string_value1", "tags": ["tag1", "tag2", "3", "4"], "integer1": "1"}
        _convert_numeric_params(test_job_params)
        assert test_job_params == {"string1": "string_value1", "tags": ["tag1", "tag2", "3", "4"], "integer1": 1}

        # Make sure it doesn't modify nested dict like metadata uses
        test_job_params = {"string1": "string_value1", "metadata": {"meta1": "meta_value1", "meta2": "2"}, "integer1": "1"}
        _convert_numeric_params(test_job_params)
        assert test_job_params == {"string1": "string_value1", "metadata": {"meta1": "meta_value1", "meta2": "2"}, "integer1": 1}

    @live_only()
    def test_submit(self):
        test_location = get_test_workspace_location()
        test_resource_group = get_test_resource_group()
        test_workspace_temp = get_test_workspace_random_name()
        test_provider_sku_list = "rigetti/azure-basic-qvm-only-unlimited,ionq/aq-internal-testing"
        test_storage = get_test_workspace_storage()

        self.cmd(f"az quantum workspace create --auto-accept -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage} -r {test_provider_sku_list} --skip-autoadd")
        
        # Wait for role assignments to propagate so the new workspace can access the storage account
        time.sleep(60)
        
        self.cmd(f"az quantum workspace set -g {test_resource_group} -w {test_workspace_temp}")

        # Submit a job to Rigetti and look for SAS tokens in URIs in the output
        results = self.cmd("az quantum job submit -t rigetti.sim.qvm --job-input-format rigetti.quil.v1 --job-input-file src/quantum/azext_quantum/tests/latest/input_data/bell-state.quil --job-output-format rigetti.quil-results.v1 -o json").get_output_in_json()
        self.assert_not_contains_standard_sas_params(results["containerUri"])
        self.assert_not_contains_standard_sas_params(results["inputDataUri"])
        self.assert_not_contains_standard_sas_params(results["outputDataUri"])

        job = self.cmd(f"az quantum job show -j {results['id']} -o json").get_output_in_json()
  
        self.assert_contains_standard_sas_params(job["containerUri"])
        self.assert_contains_standard_sas_params(job["inputDataUri"])
        self.assert_contains_standard_sas_params(job["outputDataUri"])

        # Update the submitted job's name, priority, and tags, then confirm all three changes were applied
        updated_job = self.cmd(f'az quantum job update -j {results["id"]} --job-name "Updated job name" --job-priority High --job-tags tag1 tag2 -o json').get_output_in_json()
        self.assertEqual(updated_job["name"], "Updated job name")
        self.assertEqual(updated_job["priority"], "High")
        self.assertEqual(updated_job["tags"], ["tag1", "tag2"])

        # Run a Quil pass-through job on Rigetti
        results = self.cmd("az quantum run -t rigetti.sim.qvm --job-input-format rigetti.quil.v1 --job-input-file src/quantum/azext_quantum/tests/latest/input_data/bell-state.quil --job-output-format rigetti.quil-results.v1 -o json").get_output_in_json()
        self.assertIn("ro", results)

        # Run an IonQ Circuit pass-through job on IonQ
        results = self.cmd("az quantum run -t ionq.simulator --shots 100 --job-input-format ionq.circuit.v1 --job-input-file src/quantum/azext_quantum/tests/latest/input_data/Qiskit-3-qubit-GHZ-circuit.json --job-output-format ionq.quantum-results.v1 --job-params shots=100 content-type=application/json -o json").get_output_in_json()
        self.assertIn("histogram", results)

        # Test "az quantum job list" output, for filter-params, --skip, --top, and --orderby
        results = self.cmd("az quantum job list --provider-id rigetti -o json").get_output_in_json()
        self.assertIn("rigetti", str(results))

        results = self.cmd("az quantum job list --target-id ionq.simulator -o json").get_output_in_json()
        self.assertIn("ionq.simulator", str(results))

        jobs_list = self.cmd("az quantum job list --top 1 -o json").get_output_in_json()
        self.assertEqual(len(jobs_list), 1)
    
        jobs_list = self.cmd("az quantum job list --skip 1 -o json").get_output_in_json()
        self.assertEqual(len(jobs_list), 2)

        jobs_list = self.cmd("az quantum job list --orderby Target --top 1 -o json").get_output_in_json()
        self.assertEqual(len(jobs_list), 1)
        results = str(jobs_list)
        self.assertIn("ionq", results)
        self.assertTrue("rigetti" not in results)

        jobs_list = self.cmd("az quantum job list --orderby Target --skip 1 -o json").get_output_in_json()
        self.assertEqual(len(jobs_list), 2)
        results = str(jobs_list)
        self.assertIn("rigetti", results)
        self.assertTrue("ionq" not in results)

        self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp}')

    @live_only()
    def test_submit_with_disabled_then_enabled_storage_key_access(self):
        test_location = get_test_workspace_location()
        test_resource_group = get_test_resource_group()
        test_workspace_temp = get_test_workspace_random_name()
        test_provider_sku_list = "rigetti/azure-basic-qvm-only-unlimited"
        test_storage_temp = "e2etests" + str(random.randint(10000000, 99999999))

        # Test that create workspace with not existing storage will create storage
        self.cmd(f"az quantum workspace create --auto-accept -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_temp} -r {test_provider_sku_list} --skip-autoadd")

        # Verify that access keys are disabled on the newly created storage account
        storage_info = self.cmd(f"az storage account show -g {test_resource_group} -n {test_storage_temp} -o json").get_output_in_json()
        self.assertFalse(storage_info["allowSharedKeyAccess"], "Access keys should be disabled on the newly created storage account for new workspace")

        self.cmd(f"az quantum workspace set -g {test_resource_group} -w {test_workspace_temp}")
        time.sleep(60) # wait for role assignments to propagate so the new workspace can access the storage account

        # Test that job submission works with disabled access keys on linked storage (/sasUri returns user delegation SAS)
        results = self.cmd("az quantum job submit -t rigetti.sim.qvm --job-input-format rigetti.quil.v1 --job-input-file src/quantum/azext_quantum/tests/latest/input_data/bell-state.quil --job-output-format rigetti.quil-results.v1 -o json").get_output_in_json()
        self.assertIn("id", results)

        job = self.cmd(f"az quantum job show -j {results['id']} -o json").get_output_in_json()
        self.assert_contains_standard_sas_params(job["containerUri"])
        self.assert_contains_standard_sas_params(job["inputDataUri"])
        self.assert_contains_standard_sas_params(job["outputDataUri"])
        self.assert_contains_user_delegation_sas_params(job["containerUri"])
        self.assert_contains_user_delegation_sas_params(job["inputDataUri"])
        self.assert_contains_user_delegation_sas_params(job["outputDataUri"])

        # Enable access keys on the storage account
        updated = self.cmd(f"az storage account update -g {test_resource_group} -n {test_storage_temp} --allow-shared-key-access true -o json").get_output_in_json()
        self.assertTrue(updated["allowSharedKeyAccess"], "Access keys should be enabled after update")

        time.sleep(300) # wait for the cache to update

        # Test that job submission works with enabled access keys on linked storage (/sasUri returns container-scoped Service SAS)
        results = self.cmd("az quantum job submit -t rigetti.sim.qvm --job-input-format rigetti.quil.v1 --job-input-file src/quantum/azext_quantum/tests/latest/input_data/bell-state.quil --job-output-format rigetti.quil-results.v1 -o json").get_output_in_json()
        self.assertIn("id", results)

        job = self.cmd(f"az quantum job show -j {results['id']} -o json").get_output_in_json()
        self.assert_contains_standard_sas_params(job["containerUri"])
        self.assert_contains_standard_sas_params(job["inputDataUri"])
        self.assert_contains_standard_sas_params(job["outputDataUri"])
        self.assert_not_contains_user_delegation_sas_params(job["containerUri"])
        self.assert_not_contains_user_delegation_sas_params(job["inputDataUri"])
        self.assert_not_contains_user_delegation_sas_params(job["outputDataUri"])

        # Clean up
        self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp}')
        self.cmd(f'az storage account delete -g {test_resource_group} -n {test_storage_temp} --yes')

    def test_job_list_param_formating(self):
        # Validate filter query formatting for each param
        #
        # Should return None if params are set to None
        job_type = None
        item_type = None
        provider_id = None
        target_id = None
        job_status = None
        created_after = None
        created_before = None
        job_name = None
        query = _construct_filter_query(job_type, item_type, provider_id, target_id, job_status, created_after, created_before, job_name)
        assert query is None

        job_type = "QuantumComputing"
        query = _construct_filter_query(job_type, item_type, provider_id, target_id, job_status, created_after, created_before, job_name)
        assert query == "JobType eq 'QuantumComputing'"
        job_type = None

        item_type = "job"
        query = _construct_filter_query(job_type, item_type, provider_id, target_id, job_status, created_after, created_before, job_name)
        assert query == "ItemType eq 'job'"
        item_type = None

        provider_id = "Microsoft"
        query = _construct_filter_query(job_type, item_type, provider_id, target_id, job_status, created_after, created_before, job_name)
        assert query == "ProviderId eq 'Microsoft'"
        provider_id = None

        target_id = "Awesome.Quantum.SuperComputer"
        query = _construct_filter_query(job_type, item_type, provider_id, target_id, job_status, created_after, created_before, job_name)
        assert query == "Target eq 'Awesome.Quantum.SuperComputer'"
        target_id = None

        job_status = "Succeeded"        
        query = _construct_filter_query(job_type, item_type, provider_id, target_id, job_status, created_after, created_before, job_name)
        assert query == "State eq 'Succeeded'"
        job_status = None        

        created_after = "2025-01-27"
        query = _construct_filter_query(job_type, item_type, provider_id, target_id, job_status, created_after, created_before, job_name)
        assert query == "CreationTime ge 2025-01-27"
        created_after = None

        created_before = "2025-01-27"
        query = _construct_filter_query(job_type, item_type, provider_id, target_id, job_status, created_after, created_before, job_name)
        assert query == "CreationTime le 2025-01-27"
        created_before = None

        job_name = "TestJob"
        query = _construct_filter_query(job_type, item_type, provider_id, target_id, job_status, created_after, created_before, job_name)
        assert query == "startswith(Name, 'TestJob')"
        job_name = None


        # Validate orderby expression formatting
        # Should return None if params are set to None
        orderby = None
        order = None
        orderby_expression = _construct_orderby_expression(orderby, order)
        assert orderby_expression is None

        # Test valid params
        orderby = "Target"
        orderby_expression = _construct_orderby_expression(orderby, order)
        assert orderby_expression == "Target"

        order = "asc"
        orderby_expression = _construct_orderby_expression(orderby, order)
        assert orderby_expression == "Target asc"

        order = "desc"
        orderby_expression = _construct_orderby_expression(orderby, order)
        assert orderby_expression == "Target desc"

        # Test orderby/order errors
        orderby = "Target"
        order = "foo"
        try:
            orderby_expression = _construct_orderby_expression(orderby, order)
            assert False
        except InvalidArgumentValueError as e:
            assert str(e) == ERROR_MSG_INVALID_ORDER_ARGUMENT

        orderby = ""
        order = "desc"
        try:
            orderby_expression = _construct_orderby_expression(orderby, order)
            assert False
        except RequiredArgumentMissingError as e:
            assert str(e) == ERROR_MSG_MISSING_ORDERBY_ARGUMENT

    def assert_contains_user_delegation_sas_params(self, uri: str):
        """Assert that the given URI contains user delegation SAS parameters."""
        params = parse_qs(urlparse(uri).query)
        self.assertIn("skoid", params)   # signed key object ID (service principal OID)
        self.assertIn("sktid", params)   # signed key tenant ID
        self.assertIn("skt", params)     # signed key start time
        self.assertIn("ske", params)     # signed key expiry time
        self.assertIn("sks", params)     # signed key service (b = Blob)
        self.assertIn("skv", params)     # signed key version

    def assert_not_contains_user_delegation_sas_params(self, uri: str):
        """Assert that the given URI does not contain user delegation SAS parameters."""
        params = parse_qs(urlparse(uri).query)
        self.assertNotIn("skoid", params)
        self.assertNotIn("sktid", params)
        self.assertNotIn("skt", params)
        self.assertNotIn("ske", params)
        self.assertNotIn("sks", params)
        self.assertNotIn("skv", params)

    def assert_contains_standard_sas_params(self, uri: str):
        """Assert that the given URI contains standard SAS parameters."""
        params = parse_qs(urlparse(uri).query)
        self.assertIn("sv", params)    # SAS version
        self.assertIn("st", params)    # start time
        self.assertIn("se", params)    # expiry time
        self.assertIn("sr", params)    # signed resource (e.g. c = container)
        self.assertIn("sp", params)    # permissions
        self.assertIn("sig", params)   # signature

    def assert_not_contains_standard_sas_params(self, uri: str):
        """Assert that the given URI does not contain standard SAS parameters."""
        params = parse_qs(urlparse(uri).query)
        self.assertNotIn("sv", params)
        self.assertNotIn("st", params)
        self.assertNotIn("se", params)
        self.assertNotIn("sr", params)
        self.assertNotIn("sp", params)
        self.assertNotIn("sig", params)
