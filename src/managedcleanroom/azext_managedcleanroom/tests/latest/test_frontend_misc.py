# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Unit tests for miscellaneous commands.
Tests invitation, consent, audit, and attestation commands from _frontend_custom.py.
"""

import unittest
from unittest.mock import Mock, patch
from azext_managedcleanroom._frontend_custom import (
    frontend_collaboration_invitation_list,
    frontend_collaboration_invitation_show,
    frontend_collaboration_invitation_accept,
    frontend_collaboration_consent_check,
    frontend_collaboration_consent_set,
    frontend_collaboration_audit_list,
    frontend_collaboration_attestation_cgs,
    frontend_collaboration_attestation_cleanroom
)


class TestFrontendMisc(unittest.TestCase):
    """Test cases for miscellaneous commands"""

    # Invitation Tests

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_list_invitations(self, mock_get_client):
        """Test listing invitations for a collaboration"""
        # Mock the client and its method chain
        mock_client = Mock()
        mock_client.collaboration.invitations_get.return_value = [
            {
                "invitationId": "invite-1",
                "collaborationId": "test-collab-123",
                "inviteeEmail": "user1@example.com",
                "status": "pending"
            },
            {
                "invitationId": "invite-2",
                "collaborationId": "test-collab-123",
                "inviteeEmail": "user2@example.com",
                "status": "accepted"
            }
        ]
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_invitation_list(
            cmd=Mock(),
            collaboration_id="test-collab-123"
        )

        # Verify
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["invitationId"], "invite-1")
        self.assertEqual(result[1]["invitationId"], "invite-2")
        mock_client.collaboration.invitations_get.assert_called_once_with(
            "test-collab-123")

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_show_invitation(self, mock_get_client):
        """Test showing a specific invitation"""
        # Mock the client and its method chain
        mock_client = Mock()
        mock_client.collaboration.invitation_id_get.return_value = {
            "invitationId": "test-invitation-123",
            "collaborationId": "test-collab-123",
            "inviteeEmail": "user@example.com",
            "status": "pending"
        }
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_invitation_show(
            cmd=Mock(),
            collaboration_id="test-collab-123",
            invitation_id="test-invitation-123"
        )

        # Verify
        self.assertEqual(result["invitationId"], "test-invitation-123")
        self.assertEqual(result["collaborationId"], "test-collab-123")
        self.assertEqual(result["status"], "pending")
        mock_client.collaboration.invitation_id_get.assert_called_once_with(
            "test-collab-123", "test-invitation-123"
        )

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_accept_invitation(self, mock_get_client):
        """Test accepting an invitation"""
        # Mock the client and its method chain
        mock_client = Mock()
        mock_client.collaboration.invitation_id_accept_post.return_value = {
            "invitationId": "test-invitation-123",
            "status": "accepted",
            "acceptedAt": "2024-01-01T00:00:00Z"
        }
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_invitation_accept(
            cmd=Mock(),
            collaboration_id="test-collab-123",
            invitation_id="test-invitation-123"
        )

        # Verify
        self.assertEqual(result["status"], "accepted")
        mock_client.collaboration.invitation_id_accept_post.assert_called_once_with(
            "test-collab-123", "test-invitation-123")

    # Consent Tests

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_check_consent(self, mock_get_client):
        """Test checking consent status"""
        # Mock the client and its method chain
        mock_client = Mock()
        mock_client.collaboration.check_consent_document_id_get.return_value = {
            "documentId": "doc-123",
            "consentGiven": True,
            "consentedAt": "2024-01-01T00:00:00Z"
        }
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_consent_check(
            cmd=Mock(),
            collaboration_id="test-collab-123",
            document_id="doc-123"
        )

        # Verify
        self.assertEqual(result["documentId"], "doc-123")
        self.assertTrue(result["consentGiven"])
        mock_client.collaboration.check_consent_document_id_get.assert_called_once_with(
            "test-collab-123", "doc-123")

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_set_consent(self, mock_get_client):
        """Test setting consent action"""
        # Mock the client and its method chain
        mock_client = Mock()
        mock_client.collaboration.set_consent_document_id_consent_action_post.return_value = {
            "documentId": "doc-123", "action": "enable", "updatedAt": "2024-01-01T00:00:00Z"}
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_consent_set(
            cmd=Mock(),
            collaboration_id="test-collab-123",
            document_id="doc-123",
            consent_action="enable"
        )

        # Verify
        self.assertEqual(result["action"], "enable")
        mock_client.collaboration.set_consent_document_id_consent_action_post.assert_called_once_with(
            "test-collab-123", "doc-123", "enable")

    # Audit Test

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_list_audit_logs(self, mock_get_client):
        """Test listing audit logs"""
        # Mock the client and its method chain
        mock_client = Mock()
        mock_client.collaboration.analytics_auditevents_get.return_value = [
            {
                "logId": "test-log-123",
                "timestamp": "2024-01-01T00:00:00Z",
                "action": "dataset_published",
                "userId": "user-123"
            },
            {
                "logId": "log-456",
                "timestamp": "2024-01-02T00:00:00Z",
                "action": "query_executed",
                "userId": "user-456"
            }
        ]
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_audit_list(
            cmd=Mock(),
            collaboration_id="test-collab-123"
        )

        # Verify
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["logId"], "test-log-123")
        self.assertEqual(result[1]["logId"], "log-456")
        mock_client.collaboration.analytics_auditevents_get.assert_called_once_with(
            "test-collab-123")

    # Attestation Tests

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_get_attestation_cgs(self, mock_get_client):
        """Test getting CGS attestation"""
        # Mock the client and its method chain
        mock_client = Mock()
        mock_client.collaboration.attestationreport_cgs_get.return_value = {
            "attestationType": "cgs",
            "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
            "issuedAt": "2024-01-01T00:00:00Z"
        }
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_attestation_cgs(
            cmd=Mock(),
            collaboration_id="test-collab-123"
        )

        # Verify
        self.assertEqual(result["attestationType"], "cgs")
        self.assertIn("token", result)
        mock_client.collaboration.attestationreport_cgs_get.assert_called_once_with(
            "test-collab-123")

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_get_attestation_cleanroom(self, mock_get_client):
        """Test getting cleanroom attestation"""
        # Mock the client and its method chain
        mock_client = Mock()
        mock_client.collaboration.attestationreport_cleanroom_get.return_value = {
            "attestationType": "cleanroom",
            "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
            "issuedAt": "2024-01-01T00:00:00Z",
            "cleanroomId": "cleanroom-123"}
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_attestation_cleanroom(
            cmd=Mock(),
            collaboration_id="test-collab-123"
        )

        # Verify
        self.assertEqual(result["attestationType"], "cleanroom")
        self.assertIn("cleanroomId", result)
        mock_client.collaboration.attestationreport_cleanroom_get.assert_called_once_with(
            "test-collab-123")


if __name__ == '__main__':
    unittest.main()
