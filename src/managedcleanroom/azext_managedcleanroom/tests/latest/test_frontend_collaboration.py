# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Unit tests for collaboration-related commands.
Tests collaboration, workloads, analytics, and OIDC commands from _frontend_custom.py.
"""

import unittest
from unittest.mock import Mock, patch
from azext_managedcleanroom._frontend_custom import (
    frontend_collaboration_list,
    frontend_collaboration_show,
    frontend_collaboration_analytics_show,
    frontend_collaboration_analytics_cleanroompolicy,
    frontend_collaboration_oidc_issuerinfo_show,
    frontend_collaboration_oidc_set_issuer_url,
    frontend_collaboration_oidc_keys_show,
    frontend_collaboration_report_show,
    frontend_collaboration_dataset_queries_list
)
from azext_managedcleanroom.tests.latest.test_utils import (
    MOCK_COLLABORATION,
    MOCK_COLLABORATION_LIST,
    MOCK_ANALYTICS
)


class TestFrontendCollaboration(unittest.TestCase):
    """Test cases for collaboration commands"""

    # List Collaborations Tests

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_list_collaborations_success(self, mock_get_client):
        """Test listing collaborations returns correct data"""
        # Mock the client and its methods
        mock_client = Mock()
        mock_client.collaboration.list_get.return_value = MOCK_COLLABORATION_LIST
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_list(cmd=Mock())

        # Verify
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["collaborationId"], "collab-1")
        self.assertEqual(result[1]["collaborationId"], "collab-2")
        mock_client.collaboration.list_get.assert_called_once()

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_list_collaborations_empty(self, mock_get_client):
        """Test listing collaborations with no results"""
        # Mock the client
        mock_client = Mock()
        mock_client.collaboration.list_get.return_value = []
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_list(cmd=Mock())

        # Verify
        self.assertEqual(result, [])
        self.assertIsInstance(result, list)

    # Show Collaboration Tests

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_show_collaboration_success(self, mock_get_client):
        """Test showing a specific collaboration"""
        # Mock the client
        mock_client = Mock()
        mock_client.collaboration.id_get.return_value = MOCK_COLLABORATION
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_show(
            cmd=Mock(),
            collaboration_id="test-collab-123"
        )

        # Verify
        self.assertEqual(result["collaborationId"], "test-collab-123")
        self.assertEqual(result["name"], "Test Collaboration")
        mock_client.collaboration.id_get.assert_called_once_with(
            "test-collab-123", active_only=False)

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_show_collaboration_not_found(self, mock_get_client):
        """Test handling of 404 error when collaboration not found (ERROR SCENARIO)"""
        # Mock the client to raise an exception
        mock_client = Mock()
        mock_client.collaboration.id_get.side_effect = Exception(
            "Collaboration not found")
        mock_get_client.return_value = mock_client

        # Execute and verify exception is raised
        with self.assertRaises(Exception) as context:
            frontend_collaboration_show(
                cmd=Mock(),
                collaboration_id="nonexistent"
            )

        self.assertIn("not found", str(context.exception))

    # Analytics Tests

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_show_analytics(self, mock_get_client):
        """Test showing analytics information"""
        # Mock analytics response
        mock_client = Mock()
        mock_client.collaboration.analytics_get.return_value = MOCK_ANALYTICS
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_analytics_show(
            cmd=Mock(),
            collaboration_id="test-collab-123"
        )

        # Verify
        self.assertEqual(result["analyticsId"], "test-analytics-123")
        self.assertEqual(result["status"], "ready")
        mock_client.collaboration.analytics_get.assert_called_once_with(
            "test-collab-123")

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_show_analytics_cleanroom_policy(self, mock_get_client):
        """Test showing cleanroom policy"""
        # Mock policy response
        mock_policy = {
            "policyId": "policy-123",
            "rules": ["rule1", "rule2"]
        }
        mock_client = Mock()
        mock_client.collaboration.analytics_cleanroompolicy_get.return_value = mock_policy
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_analytics_cleanroompolicy(
            cmd=Mock(),
            collaboration_id="test-collab-123"
        )

        # Verify
        self.assertEqual(result["policyId"], "policy-123")
        self.assertEqual(len(result["rules"]), 2)
        mock_client.collaboration.analytics_cleanroompolicy_get.assert_called_once_with(
            "test-collab-123")

    # OIDC Tests

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_show_oidc_issuer_info(self, mock_get_client):
        """Test showing OIDC issuer information"""
        # Mock OIDC response
        mock_oidc = {
            "issuer": "https://issuer.example.com",
            "jwks_uri": "https://issuer.example.com/.well-known/jwks.json"
        }
        mock_client = Mock()
        mock_client.collaboration.oidc_issuer_info_get.return_value = mock_oidc
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_oidc_issuerinfo_show(
            cmd=Mock(),
            collaboration_id="test-collab-123"
        )

        # Verify
        self.assertEqual(result["issuer"], "https://issuer.example.com")
        mock_client.collaboration.oidc_issuer_info_get.assert_called_once_with(
            "test-collab-123")

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_oidc_set_issuer_url(self, mock_get_client):
        """Test setting OIDC issuer URL"""
        # Mock OIDC response
        mock_oidc = {
            "issuer": "https://new-issuer.example.com",
            "updatedAt": "2024-01-01T00:00:00Z"
        }
        mock_client = Mock()
        mock_client.collaboration.oidc_set_issuer_url_post.return_value = mock_oidc
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_oidc_set_issuer_url(
            cmd=Mock(),
            collaboration_id="test-collab-123",
            url="https://new-issuer.example.com"
        )

        # Verify
        self.assertEqual(result["issuer"], "https://new-issuer.example.com")
        mock_client.collaboration.oidc_set_issuer_url_post.assert_called_once_with(
            "test-collab-123", body={"url": "https://new-issuer.example.com"})

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_oidc_keys_show(self, mock_get_client):
        """Test showing OIDC keys"""
        # Mock OIDC keys response
        mock_keys = {
            "keys": [
                {"kid": "key1", "kty": "RSA", "use": "sig"},
                {"kid": "key2", "kty": "RSA", "use": "sig"}
            ]
        }
        mock_client = Mock()
        mock_client.collaboration.oidc_keys_get.return_value = mock_keys
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_oidc_keys_show(
            cmd=Mock(),
            collaboration_id="test-collab-123"
        )

        # Verify
        self.assertEqual(len(result["keys"]), 2)
        self.assertEqual(result["keys"][0]["kid"], "key1")
        mock_client.collaboration.oidc_keys_get.assert_called_once_with(
            "test-collab-123")

    # Report Tests

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_show_collaboration_report(self, mock_get_client):
        """Test showing collaboration report"""
        # Mock report response
        mock_report = {
            "collaborationId": "test-collab-123",
            "reportData": {
                "totalQueries": 42,
                "totalDatasets": 10,
                "participants": 5
            },
            "generatedAt": "2024-01-01T00:00:00Z"
        }
        mock_client = Mock()
        mock_client.collaboration.report_get.return_value = mock_report
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_report_show(
            cmd=Mock(),
            collaboration_id="test-collab-123"
        )

        # Verify
        self.assertEqual(result["collaborationId"], "test-collab-123")
        self.assertEqual(result["reportData"]["totalQueries"], 42)
        mock_client.collaboration.report_get.assert_called_once_with(
            "test-collab-123")

    # Dataset Queries Tests

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_dataset_queries_list(self, mock_get_client):
        """Test listing queries for a dataset"""
        # Mock queries list response
        mock_queries = [
            {"queryId": "query-1", "datasetId": "dataset-123", "name": "Query 1"},
            {"queryId": "query-2", "datasetId": "dataset-123", "name": "Query 2"}
        ]
        mock_client = Mock()
        mock_client.collaboration.analytics_datasets_document_id_queries_get.return_value = mock_queries
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_dataset_queries_list(
            cmd=Mock(),
            collaboration_id="test-collab-123",
            document_id="dataset-123"
        )

        # Verify
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["queryId"], "query-1")
        self.assertEqual(result[1]["queryId"], "query-2")
        mock_client.collaboration.analytics_datasets_document_id_queries_get.assert_called_once_with(
            "test-collab-123", "dataset-123")

    # Filter Tests

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_list_collaborations_with_active_only_filter(
            self, mock_get_client):
        """Test listing collaborations with active_only filter"""
        # Mock the client
        mock_client = Mock()
        mock_client.collaboration.list_get.return_value = [
            {"collaborationId": "collab-1", "name": "Active Collab 1", "status": "active"}
        ]
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_list(
            cmd=Mock(),
            active_only=True
        )

        # Verify
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["status"], "active")
        mock_client.collaboration.list_get.assert_called_once_with(
            active_only=True)

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_show_collaboration_with_active_only_filter(self, mock_get_client):
        """Test showing collaboration with active_only check"""
        # Mock the client
        mock_client = Mock()
        mock_client.collaboration.id_get.return_value = MOCK_COLLABORATION
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_show(
            cmd=Mock(),
            collaboration_id="test-collab-123",
            active_only=True
        )

        # Verify
        self.assertEqual(result["collaborationId"], "test-collab-123")
        mock_client.collaboration.id_get.assert_called_once_with(
            "test-collab-123", active_only=True)


if __name__ == '__main__':
    unittest.main()
