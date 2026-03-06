# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Unit tests for query commands.
Tests query CRUD, execution, voting, and run history commands from _frontend_custom.py.
"""

import unittest
from unittest.mock import Mock, patch
from azext_managedcleanroom._frontend_custom import (
    frontend_collaboration_query_list,
    frontend_collaboration_query_show,
    frontend_collaboration_query_publish,
    frontend_collaboration_query_run,
    frontend_collaboration_query_vote_accept,
    frontend_collaboration_query_vote_reject,
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
        mock_client.collaboration.analytics_queries_document_id_vote_accept_post.return_value = {
            "queryId": "test-query-123", "voteStatus": "accepted", "votedAt": "2024-01-01T00:00:00Z"}
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_query_vote_accept(
            cmd=Mock(),
            collaboration_id="test-collab-123",
            document_id="test-query-123"
        )

        # Verify
        self.assertEqual(result["voteStatus"], "accepted")
        mock_client.collaboration.analytics_queries_document_id_vote_accept_post.assert_called_once_with(
            "test-collab-123", "test-query-123", body=None)

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_vote_reject_query(self, mock_get_client):
        """Test rejecting a query vote"""
        # Mock the client and its method chain
        mock_client = Mock()
        mock_client.collaboration.analytics_queries_document_id_vote_reject_post.return_value = {
            "queryId": "test-query-123", "voteStatus": "rejected", "votedAt": "2024-01-01T00:00:00Z"}
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_query_vote_reject(
            cmd=Mock(),
            collaboration_id="test-collab-123",
            document_id="test-query-123"
        )

        # Verify
        self.assertEqual(result["voteStatus"], "rejected")
        mock_client.collaboration.analytics_queries_document_id_vote_reject_post.assert_called_once_with(
            "test-collab-123", "test-query-123", body=None)

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


if __name__ == '__main__':
    unittest.main()
