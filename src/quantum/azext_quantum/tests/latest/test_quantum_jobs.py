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
from urllib.parse import urlparse, parse_qs

from azure.cli.testsdk.scenario_tests import AllowLargeResponse, live_only
from azure.cli.testsdk import ScenarioTest
from azure.cli.core.azclierror import InvalidArgumentValueError, RequiredArgumentMissingError, AzureInternalError

from .utils import get_test_resource_group, get_test_workspace, get_test_workspace_location, issue_cmd_with_param_missing, get_test_workspace_storage, get_test_workspace_random_name
from ...commands import transform_output
from ...operations.job import (
    _validate_max_poll_wait_secs,
    _convert_numeric_params,
    _construct_filter_query,
    _construct_orderby_expression,
    ERROR_MSG_INVALID_ORDER_ARGUMENT,
    ERROR_MSG_MISSING_ORDERBY_ARGUMENT)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class QuantumJobsScenarioTest(ScenarioTest):

    @live_only()
    def test_jobs(self):
        # set current workspace:
        self.cmd(f'az quantum workspace set -g {get_test_resource_group()} -w {get_test_workspace()} -l {get_test_workspace_location()}')

        # list
        targets = self.cmd('az quantum target list -o json').get_output_in_json()
        assert len(targets) > 0

    # @pytest.fixture(autouse=True)
    # def _pass_fixtures(self, capsys):
    #     self.capsys = capsys
    # # See "TODO" in issue_cmd_with_param_missing un utils.py

    def test_job_errors(self):
        issue_cmd_with_param_missing(self, "az quantum job cancel", "az quantum job cancel -g MyResourceGroup -w MyWorkspace -l MyLocation -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy\nCancel an Azure Quantum job by id.")
        issue_cmd_with_param_missing(self, "az quantum job output", "az quantum job output -g MyResourceGroup -w MyWorkspace -l MyLocation -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy -o table\nPrint the results of a successful Azure Quantum job.")
        issue_cmd_with_param_missing(self, "az quantum job show", "az quantum job show -g MyResourceGroup -w MyWorkspace -l MyLocation -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy --query status\nGet the status of an Azure Quantum job.")
        issue_cmd_with_param_missing(self, "az quantum job wait", "az quantum job wait -g MyResourceGroup -w MyWorkspace -l MyLocation -j yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy --max-poll-wait-secs 60 -o table\nWait for completion of a job, check at 60 second intervals.")

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
        
        self.cmd(f"az quantum workspace set -g {test_resource_group} -w {test_workspace_temp} -l {test_location}")

        # Submit a job to Rigetti and look for SAS tokens in URIs in the output
        results = self.cmd("az quantum job submit -t rigetti.sim.qvm --job-input-format rigetti.quil.v1 --job-input-file src/quantum/azext_quantum/tests/latest/input_data/bell-state.quil --job-output-format rigetti.quil-results.v1 -o json").get_output_in_json()
        self.assert_not_contains_standard_sas_params(results["containerUri"])
        self.assert_not_contains_standard_sas_params(results["inputDataUri"])
        self.assert_not_contains_standard_sas_params(results["outputDataUri"])

        job = self.cmd(f"az quantum job show -j {results['id']} -o json").get_output_in_json()
  
        self.assert_contains_standard_sas_params(job["containerUri"])
        self.assert_contains_standard_sas_params(job["inputDataUri"])
        self.assert_contains_standard_sas_params(job["outputDataUri"])

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

        self.cmd(f"az quantum workspace set -g {test_resource_group} -w {test_workspace_temp} -l {test_location}")
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
