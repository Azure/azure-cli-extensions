# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Unit tests for query commands.
Tests query CRUD, execution, voting, and run history commands from _frontend_custom.py.
"""

import json
import unittest
from unittest.mock import Mock, patch
from azext_managedcleanroom._frontend_custom import (
    frontend_collaboration_query_list,
    frontend_collaboration_query_show,
    frontend_collaboration_query_publish,
    frontend_collaboration_query_run,
    frontend_collaboration_query_vote,
    frontend_collaboration_query_runhistory_list,
    frontend_collaboration_query_runresult_show
)


class TestFrontendQuery(unittest.TestCase):
    """Test cases for query commands"""

    # Query CRUD Tests

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_list_queries_success(self, mock_get_client):
        """Test listing queries for a collaboration"""
        # Mock the client and its method chain
        mock_client = Mock()
        mock_client.collaboration.analytics_queries_list_get.return_value = [
            {"queryId": "query-1", "name": "Query 1", "status": "approved"},
            {"queryId": "query-2", "name": "Query 2", "status": "pending"}
        ]
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_query_list(
            cmd=Mock(),
            collaboration_id="test-collab-123"
        )

        # Verify
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["queryId"], "query-1")
        self.assertEqual(result[1]["queryId"], "query-2")
        mock_client.collaboration.analytics_queries_list_get.assert_called_once_with(
            "test-collab-123")

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_show_query_success(self, mock_get_client):
        """Test showing a specific query"""
        # Mock the client and its method chain
        mock_client = Mock()
        mock_client.collaboration.analytics_queries_document_id_get.return_value = {
            "queryId": "test-query-123",
            "name": "Revenue Analysis",
            "status": "approved",
            "sql": "SELECT * FROM revenue"}
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_query_show(
            cmd=Mock(),
            collaboration_id="test-collab-123",
            document_id="test-query-123"
        )

        # Verify
        self.assertEqual(result["queryId"], "test-query-123")
        self.assertEqual(result["name"], "Revenue Analysis")
        self.assertEqual(result["status"], "approved")
        mock_client.collaboration.analytics_queries_document_id_get.assert_called_once_with(
            "test-collab-123", "test-query-123")

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_query_success(self, mock_get_client):
        """Test publishing a query"""
        # Mock the client and its method chain
        mock_client = Mock()
        mock_client.collaboration.analytics_queries_document_id_publish_post.return_value = {
            "queryId": "test-query-123",
            "status": "published",
            "publishedAt": "2024-01-01T00:00:00Z"
        }
        mock_get_client.return_value = mock_client

        # Test body
        test_body = {
            "inputDatasets": [{"datasetDocumentId": "ds1", "view": "view1"}],
            "outputDataset": {"datasetDocumentId": "ds2", "view": "view2"},
            "queryData": {"segments": []}
        }

        # Execute
        result = frontend_collaboration_query_publish(
            cmd=Mock(),
            collaboration_id="test-collab-123",
            document_id="test-query-123",
            body=test_body
        )

        # Verify
        self.assertEqual(result["queryId"], "test-query-123")
        self.assertEqual(result["status"], "published")
        mock_client.collaboration.analytics_queries_document_id_publish_post.assert_called_once_with(
            "test-collab-123", "test-query-123", test_body)

    # Query Execution Test

    @patch('uuid.uuid4')
    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_run_query_success(self, mock_get_client, mock_uuid4):
        """Test executing a query"""
        # Mock UUID generation
        mock_uuid4.return_value = "generated-run-id-123"

        # Mock the client and its method chain
        mock_client = Mock()
        mock_client.collaboration.analytics_queries_document_id_run_post.return_value = {
            "runId": "generated-run-id-123",
            "queryId": "test-query-123",
            "status": "running",
            "startTime": "2024-01-01T00:00:00Z"}
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_query_run(
            cmd=Mock(),
            collaboration_id="test-collab-123",
            document_id="test-query-123"
        )

        # Verify
        self.assertEqual(result["runId"], "generated-run-id-123")
        self.assertEqual(result["status"], "running")
        # Verify the body with auto-generated runId was passed
        mock_client.collaboration.analytics_queries_document_id_run_post.assert_called_once()
        call_args = mock_client.collaboration.analytics_queries_document_id_run_post.call_args
        # Check positional args
        self.assertEqual(call_args[0][0], "test-collab-123")
        self.assertEqual(call_args[0][1], "test-query-123")
        # Check keyword args
        self.assertIn("body", call_args[1])
        self.assertIn("runId", call_args[1]["body"])
        self.assertEqual(call_args[1]["body"]["runId"], "generated-run-id-123")

    # Query Voting Tests

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_vote_accept_query(self, mock_get_client):
        """Test accepting a query vote"""
        # Mock the client and its method chain
        mock_client = Mock()
        # 204 No Content
        mock_client.collaboration.analytics_queries_document_id_vote_post.return_value = None
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_query_vote(
            cmd=Mock(),
            collaboration_id="test-collab-123",
            document_id="test-query-123",
            vote_action="accept"
        )

        # Verify
        self.assertIsNone(result)  # 204 No Content returns None
        mock_client.collaboration.analytics_queries_document_id_vote_post.assert_called_once_with(
            "test-collab-123", "test-query-123", body={"voteAction": "accept"})

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_vote_reject_query(self, mock_get_client):
        """Test rejecting a query vote"""
        # Mock the client and its method chain
        mock_client = Mock()
        # 204 No Content
        mock_client.collaboration.analytics_queries_document_id_vote_post.return_value = None
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_query_vote(
            cmd=Mock(),
            collaboration_id="test-collab-123",
            document_id="test-query-123",
            vote_action="reject"
        )

        # Verify
        self.assertIsNone(result)  # 204 No Content returns None
        mock_client.collaboration.analytics_queries_document_id_vote_post.assert_called_once_with(
            "test-collab-123", "test-query-123", body={"voteAction": "reject"})

    # Query Run History Tests

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_list_query_run_history(self, mock_get_client):
        """Test listing query execution history"""
        # Mock the client and its method chain
        mock_client = Mock()
        mock_client.collaboration.analytics_queries_document_id_runhistory_get.return_value = [
            {
                "runId": "run-1",
                "queryId": "test-query-123",
                "status": "completed",
                "startTime": "2024-01-01T00:00:00Z"},
            {
                "runId": "run-2",
                "queryId": "test-query-123",
                "status": "completed",
                "startTime": "2024-01-02T00:00:00Z"}]
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_query_runhistory_list(
            cmd=Mock(),
            collaboration_id="test-collab-123",
            document_id="test-query-123"
        )

        # Verify
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["runId"], "run-1")
        self.assertEqual(result[1]["runId"], "run-2")
        mock_client.collaboration.analytics_queries_document_id_runhistory_get.assert_called_once_with(
            "test-collab-123", "test-query-123")

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_show_query_run_result(self, mock_get_client):
        """Test showing specific query run details"""
        # Mock the client and its method chain
        mock_client = Mock()
        mock_client.collaboration.analytics_queries_jobid_get.return_value = {
            "runId": "test-job-123",
            "queryId": "test-query-123",
            "status": "completed",
            "startTime": "2024-01-01T00:00:00Z",
            "endTime": "2024-01-01T00:05:00Z",
            "results": {"rowCount": 1000}
        }
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_query_runresult_show(
            cmd=Mock(),
            collaboration_id="test-collab-123",
            job_id="test-job-123"
        )

        # Verify
        self.assertEqual(result["runId"], "test-job-123")
        self.assertEqual(result["queryId"], "test-query-123")
        self.assertEqual(result["status"], "completed")
        mock_client.collaboration.analytics_queries_jobid_get.assert_called_once_with(
            "test-collab-123", "test-job-123")

    # Query Publish with Parameters Tests

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_query_with_parameters_from_files(self, mock_get_client):
        """Test publishing a query with SQL segments from JSON files"""
        # Mock the client
        mock_client = Mock()
        mock_client.collaboration.analytics_queries_document_id_publish_post.return_value = {
            "queryId": "test-query-123",
            "status": "published"
        }
        mock_get_client.return_value = mock_client

        # Mock file reading for JSON segment files
        segment_1 = {
            "data": "SELECT * FROM table1",
            "executionSequence": 1,
            "preConditions": "",
            "postFilters": ""
        }
        segment_2 = {
            "data": "SELECT * FROM table2",
            "executionSequence": 1,
            "preConditions": "",
            "postFilters": ""
        }
        segment_3 = {
            "data": "SELECT * FROM table3",
            "executionSequence": 2,
            "preConditions": "",
            "postFilters": ""
        }
        
        def mock_open_handler(filename, mode='r'):
            content = {
                'segment1.json': json.dumps(segment_1),
                'segment2.json': json.dumps(segment_2),
                'segment3.json': json.dumps(segment_3)
            }
            file_content = content.get(filename, "")
            return unittest.mock.mock_open(read_data=file_content)()

        with patch('builtins.open', side_effect=mock_open_handler):
            # Execute
            result = frontend_collaboration_query_publish(
                cmd=Mock(),
                collaboration_id="test-collab-123",
                document_id="test-query-123",
                body=None,
                query_segment=["@segment1.json", "@segment2.json", "@segment3.json"],
                execution_sequence=None,
                input_datasets="dataset1:view1,dataset2:view2",
                output_dataset="output-dataset:results"
            )

        # Verify
        self.assertEqual(result["queryId"], "test-query-123")
        self.assertEqual(result["status"], "published")
        
        # Verify body construction - segments were parsed from JSON
        call_args = mock_client.collaboration.analytics_queries_document_id_publish_post.call_args
        body = call_args[0][2]
        self.assertEqual(body["inputDatasets"], "dataset1:view1,dataset2:view2")
        self.assertEqual(body["outputDataset"], "output-dataset:results")
        self.assertEqual(len(body["queryData"]), 3)
        self.assertEqual(body["queryData"][0]["data"], "SELECT * FROM table1")
        self.assertEqual(body["queryData"][0]["executionSequence"], 1)
        self.assertEqual(body["queryData"][2]["executionSequence"], 2)

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_query_with_inline_sql(self, mock_get_client):
        """Test publishing a query with inline SQL segments"""
        # Mock the client
        mock_client = Mock()
        mock_client.collaboration.analytics_queries_document_id_publish_post.return_value = {
            "queryId": "test-query-inline",
            "status": "published"
        }
        mock_get_client.return_value = mock_client

        # Execute with inline SQL
        result = frontend_collaboration_query_publish(
            cmd=Mock(),
            collaboration_id="test-collab-123",
            document_id="test-query-inline",
            body=None,
            query_segment=["SELECT * FROM table1", "SELECT * FROM table2"],
            execution_sequence="1,2",
            input_datasets="dataset1:view1",
            output_dataset="output-dataset:results"
        )

        # Verify
        self.assertEqual(result["status"], "published")
        
        # Verify body construction
        call_args = mock_client.collaboration.analytics_queries_document_id_publish_post.call_args
        body = call_args[0][2]
        self.assertEqual(len(body["queryData"]), 2)
        self.assertEqual(body["queryData"][0]["data"], "SELECT * FROM table1")
        self.assertEqual(body["queryData"][1]["executionSequence"], 2)

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_query_mutual_exclusion(self, mock_get_client):
        """Test that body and parameters are mutually exclusive for query publish"""
        from azure.cli.core.util import CLIError
        
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        # Execute with both body and parameters - should raise error
        with self.assertRaises(CLIError) as context:
            frontend_collaboration_query_publish(
                cmd=Mock(),
                collaboration_id="test-collab-123",
                document_id="test-query-123",
                body={"queryData": []},
                query_segment=["SELECT * FROM table1"]
            )

        self.assertIn("Cannot use --body together with individual parameters", str(context.exception))

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_query_segment_count_mismatch(self, mock_get_client):
        """Test validation when segment count doesn't match execution sequence count"""
        from azure.cli.core.util import CLIError
        
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        # Execute with mismatched counts - should raise error
        with self.assertRaises(CLIError) as context:
            frontend_collaboration_query_publish(
                cmd=Mock(),
                collaboration_id="test-collab-123",
                document_id="test-query-123",
                body=None,
                query_segment=["SELECT * FROM table1", "SELECT * FROM table2"],
                execution_sequence="1,2,3",  # 3 numbers for 2 segments
                input_datasets="dataset1:view1",
                output_dataset="output-dataset:results"
            )

        self.assertIn("must match execution sequence count", str(context.exception))

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_query_file_mode_rejects_exec_seq(self, mock_get_client):
        """Test that FILE mode raises error if --execution-sequence is provided"""
        from azure.cli.core.util import CLIError
        
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        segment_json = json.dumps({
            "data": "SELECT * FROM table1",
            "executionSequence": 1,
            "preConditions": "",
            "postFilters": ""
        })
        
        with patch('builtins.open', unittest.mock.mock_open(read_data=segment_json)):
            with self.assertRaises(CLIError) as context:
                frontend_collaboration_query_publish(
                    cmd=Mock(),
                    collaboration_id="test-collab-123",
                    document_id="test-query-123",
                    body=None,
                    query_segment=["@segment1.json"],
                    execution_sequence="1",  # Should raise error
                    input_datasets="dataset1:view1",
                    output_dataset="output-dataset:results"
                )

            self.assertIn("must not be provided when using @file.json", str(context.exception))

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_query_inline_mode_requires_exec_seq(self, mock_get_client):
        """Test that INLINE mode requires --execution-sequence"""
        from azure.cli.core.util import CLIError
        
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        with self.assertRaises(CLIError) as context:
            frontend_collaboration_query_publish(
                cmd=Mock(),
                collaboration_id="test-collab-123",
                document_id="test-query-123",
                body=None,
                query_segment=["SELECT * FROM table1"],
                execution_sequence=None,  # Should raise error
                input_datasets="dataset1:view1",
                output_dataset="output-dataset:results"
            )

        self.assertIn("required when using inline SQL", str(context.exception))

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_query_disallows_mixed_segments(self, mock_get_client):
        """Test that mixing @file.json and inline segments raises error"""
        from azure.cli.core.util import CLIError
        
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        with self.assertRaises(CLIError) as context:
            frontend_collaboration_query_publish(
                cmd=Mock(),
                collaboration_id="test-collab-123",
                document_id="test-query-123",
                body=None,
                query_segment=["@segment1.json", "SELECT * FROM table2"],  # Mixed
                execution_sequence="1,2",
                input_datasets="dataset1:view1",
                output_dataset="output-dataset:results"
            )

        self.assertIn("Cannot mix @file.json and inline SQL", str(context.exception))

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_query_file_missing_execution_sequence(self, mock_get_client):
        """Test that segment JSON file must contain executionSequence"""
        from azure.cli.core.util import CLIError
        
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        # Segment JSON missing executionSequence field
        segment_json = json.dumps({
            "data": "SELECT * FROM table1",
            "preConditions": "",
            "postFilters": ""
        })
        
        with patch('builtins.open', unittest.mock.mock_open(read_data=segment_json)):
            with self.assertRaises(CLIError) as context:
                frontend_collaboration_query_publish(
                    cmd=Mock(),
                    collaboration_id="test-collab-123",
                    document_id="test-query-123",
                    body=None,
                    query_segment=["@segment1.json"],
                    execution_sequence=None,
                    input_datasets="dataset1:view1",
                    output_dataset="output-dataset:results"
                )

            self.assertIn('must contain "executionSequence"', str(context.exception))

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_query_invalid_dataset_format(self, mock_get_client):
        """Test validation of dataset ID:view format"""
        from azure.cli.core.util import CLIError
        
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        # Execute with invalid dataset format - should raise error
        with self.assertRaises(CLIError) as context:
            frontend_collaboration_query_publish(
                cmd=Mock(),
                collaboration_id="test-collab-123",
                document_id="test-query-123",
                body=None,
                query_segment=["SELECT * FROM table1"],
                execution_sequence="1",
                input_datasets="dataset1",  # Missing :viewName
                output_dataset="output-dataset:results"
            )

        self.assertIn("Invalid input dataset format", str(context.exception))

    # Query Run with Parameters Tests

    @patch('uuid.uuid4')
    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_run_query_with_parameters(self, mock_get_client, mock_uuid4):
        """Test running a query with individual parameters"""
        # Mock UUID generation
        mock_uuid4.return_value = "generated-run-id-456"

        # Mock the client
        mock_client = Mock()
        mock_client.collaboration.analytics_queries_document_id_run_post.return_value = {
            "runId": "generated-run-id-456",
            "status": "running"
        }
        mock_get_client.return_value = mock_client

        # Execute with parameters
        result = frontend_collaboration_query_run(
            cmd=Mock(),
            collaboration_id="test-collab-123",
            document_id="test-query-123",
            body=None,
            dry_run=True,
            start_date="2024-01-01",
            end_date="2024-12-31",
            use_optimizer=True
        )

        # Verify
        self.assertEqual(result["runId"], "generated-run-id-456")
        
        # Verify body was constructed with parameters
        call_args = mock_client.collaboration.analytics_queries_document_id_run_post.call_args
        body = call_args[1]["body"]
        self.assertEqual(body["dryRun"], True)
        self.assertEqual(body["startDate"], "2024-01-01")
        self.assertEqual(body["endDate"], "2024-12-31")
        self.assertEqual(body["useOptimizer"], True)
        self.assertEqual(body["runId"], "generated-run-id-456")

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_run_query_mutual_exclusion(self, mock_get_client):
        """Test that body and parameters are mutually exclusive for query run"""
        from azure.cli.core.util import CLIError
        
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        # Execute with both body and parameters - should raise error
        with self.assertRaises(CLIError) as context:
            frontend_collaboration_query_run(
                cmd=Mock(),
                collaboration_id="test-collab-123",
                document_id="test-query-123",
                body={"runId": "test-run-id"},
                dry_run=True
            )

        self.assertIn("Cannot use --body together with individual parameters", str(context.exception))

    @patch('uuid.uuid4')
    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_run_query_with_partial_parameters(self, mock_get_client, mock_uuid4):
        """Test running a query with only some optional parameters"""
        # Mock UUID generation
        mock_uuid4.return_value = "generated-run-id-789"

        # Mock the client
        mock_client = Mock()
        mock_client.collaboration.analytics_queries_document_id_run_post.return_value = {
            "runId": "generated-run-id-789",
            "status": "running"
        }
        mock_get_client.return_value = mock_client

        # Execute with only dry_run parameter
        result = frontend_collaboration_query_run(
            cmd=Mock(),
            collaboration_id="test-collab-123",
            document_id="test-query-123",
            body=None,
            dry_run=True,
            start_date=None,
            end_date=None,
            use_optimizer=False
        )

        # Verify
        self.assertEqual(result["status"], "running")
        
        # Verify only dry_run is in body (not False boolean values)
        call_args = mock_client.collaboration.analytics_queries_document_id_run_post.call_args
        body = call_args[1]["body"]
        self.assertEqual(body["dryRun"], True)
        self.assertNotIn("startDate", body)
        self.assertNotIn("endDate", body)
        self.assertNotIn("useOptimizer", body)


if __name__ == '__main__':
    unittest.main()
