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
    frontend_collaboration_workloads_list,
    frontend_collaboration_analytics_show,
    frontend_collaboration_analytics_deploymentinfo,
    frontend_collaboration_analytics_cleanroompolicy,
    frontend_collaboration_oidc_issuerinfo_show
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
        mock_client.collaboration.list.return_value = MOCK_COLLABORATION_LIST
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_list(cmd=Mock())

        # Verify
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["collaborationId"], "collab-1")
        self.assertEqual(result[1]["collaborationId"], "collab-2")
        mock_client.collaboration.list.assert_called_once()

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_list_collaborations_empty(self, mock_get_client):
        """Test listing collaborations with no results"""
        # Mock the client
        mock_client = Mock()
        mock_client.collaboration.list.return_value = []
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
            "test-collab-123")

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

    # Workloads Tests

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_list_workloads_success(self, mock_get_client):
        """Test listing workloads for a collaboration"""
        # Mock workloads response
        mock_workloads = [
            {"workloadId": "workload-1", "name": "Workload 1"},
            {"workloadId": "workload-2", "name": "Workload 2"}
        ]
        mock_client = Mock()
        mock_client.collaboration.workloads_get.return_value = mock_workloads
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_workloads_list(
            cmd=Mock(),
            collaboration_id="test-collab-123"
        )

        # Verify
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["workloadId"], "workload-1")
        mock_client.collaboration.workloads_get.assert_called_once_with(
            "test-collab-123")

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
    def test_show_analytics_deployment_info(self, mock_get_client):
        """Test showing analytics deployment information"""
        # Mock deployment info
        mock_deployment_info = {
            "deploymentId": "deploy-123",
            "region": "eastus",
            "status": "deployed"
        }
        mock_client = Mock()
        mock_client.collaboration.analytics_deployment_info_get.return_value = mock_deployment_info
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_analytics_deploymentinfo(
            cmd=Mock(),
            collaboration_id="test-collab-123"
        )

        # Verify
        self.assertEqual(result["deploymentId"], "deploy-123")
        self.assertEqual(result["region"], "eastus")
        mock_client.collaboration.analytics_deployment_info_get.assert_called_once_with(
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


if __name__ == '__main__':
    unittest.main()
