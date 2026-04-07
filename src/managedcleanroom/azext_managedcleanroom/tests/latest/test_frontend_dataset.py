# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Unit tests for dataset commands.
Tests dataset list, show, and publish commands from _frontend_custom.py.
"""

import json
import unittest
from unittest.mock import Mock, patch
from azext_managedcleanroom._frontend_custom import (
    frontend_collaboration_dataset_list,
    frontend_collaboration_dataset_show,
    frontend_collaboration_dataset_publish
)
from azext_managedcleanroom.tests.latest.test_utils import (
    MOCK_DATASET,
    MOCK_DATASET_LIST
)


class TestFrontendDataset(unittest.TestCase):
    """Test cases for dataset commands"""

    # List Datasets Test

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_list_datasets_success(self, mock_get_client):
        """Test listing datasets for a collaboration"""
        # Mock the client
        mock_client = Mock()
        mock_client.collaboration.analytics_datasets_list_get.return_value = MOCK_DATASET_LIST
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_dataset_list(
            cmd=Mock(),
            collaboration_id="test-collab-123"
        )

        # Verify
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["datasetId"], "dataset-1")
        self.assertEqual(result[1]["datasetId"], "dataset-2")
        mock_client.collaboration.analytics_datasets_list_get.assert_called_once_with(
            "test-collab-123")

    # Show Dataset Test

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_show_dataset_success(self, mock_get_client):
        """Test showing a specific dataset"""
        # Mock the client
        mock_client = Mock()
        mock_client.collaboration.analytics_datasets_document_id_get.return_value = MOCK_DATASET
        mock_get_client.return_value = mock_client

        # Execute
        result = frontend_collaboration_dataset_show(
            cmd=Mock(),
            collaboration_id="test-collab-123",
            document_id="test-dataset-123"
        )

        # Verify
        self.assertEqual(result["datasetId"], "test-dataset-123")
        self.assertEqual(result["name"], "Customer Data")
        self.assertEqual(result["status"], "published")
        mock_client.collaboration.analytics_datasets_document_id_get.assert_called_once_with(
            "test-collab-123", "test-dataset-123")

    # Publish Dataset Tests

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_dataset_success(self, mock_get_client):
        """Test publishing a dataset successfully"""
        # Mock publish response
        mock_publish_response = {
            "datasetId": "test-dataset-123",
            "status": "published",
            "publishedAt": "2024-01-01T00:00:00Z"
        }
        mock_client = Mock()
        mock_client.collaboration.analytics_datasets_document_id_publish_post.return_value = mock_publish_response
        mock_get_client.return_value = mock_client

        # Test body
        test_body = {
            "data": {
                "datasetAccessPoint": {
                    "name": "test-dataset",
                    "path": "/data/test",
                    "protection": {}
                }
            }
        }

        # Execute
        result = frontend_collaboration_dataset_publish(
            cmd=Mock(),
            collaboration_id="test-collab-123",
            document_id="test-dataset-123",
            body=test_body
        )

        # Verify
        self.assertEqual(result["datasetId"], "test-dataset-123")
        self.assertEqual(result["status"], "published")
        mock_client.collaboration.analytics_datasets_document_id_publish_post.assert_called_once_with(
            "test-collab-123", "test-dataset-123", test_body)

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_dataset_failure(self, mock_get_client):
        """Test handling publish failure (ERROR SCENARIO)"""
        # Mock error
        mock_client = Mock()
        mock_client.collaboration.analytics_datasets_document_id_publish_post.side_effect = Exception(
            "Dataset validation failed")
        mock_get_client.return_value = mock_client

        # Test body
        test_body = {"data": {"datasetAccessPoint": {}}}

        # Execute and verify exception
        with self.assertRaises(Exception) as context:
            frontend_collaboration_dataset_publish(
                cmd=Mock(),
                collaboration_id="test-collab-123",
                document_id="invalid-dataset",
                body=test_body
            )

        self.assertIn("validation failed", str(context.exception))

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_dataset_with_sse_parameters(self, mock_get_client):
        """Test publishing a dataset using SSE parameters"""
        # Mock publish response
        mock_publish_response = {
            "datasetId": "test-dataset-123",
            "status": "published",
            "publishedAt": "2024-01-01T00:00:00Z"
        }
        mock_client = Mock()
        mock_client.collaboration.analytics_datasets_document_id_publish_post.return_value = mock_publish_response
        mock_get_client.return_value = mock_client

        # Mock file reading
        test_schema = {
            "fields": [
                {"fieldName": "customer_id", "fieldType": "string"},
                {"fieldName": "revenue", "fieldType": "decimal"}
            ],
            "format": "Delta"
        }

        with patch('builtins.open', unittest.mock.mock_open(read_data=json.dumps(test_schema))):
            # Execute with SSE parameters
            result = frontend_collaboration_dataset_publish(
                cmd=Mock(),
                collaboration_id="test-collab-123",
                document_id="test-dataset-123",
                body=None,
                storage_account_url="https://mystorageaccount.blob.core.windows.net",
                container_name="datasets",
                storage_account_type="AzureStorageAccount",
                encryption_mode="SSE",
                schema_file="@schema.json",
                schema_format=None,
                access_mode="ReadWrite",
                allowed_fields="customer_id,revenue",
                identity_name="northwind-identity",
                identity_client_id="fb907136-1234-5678-9abc-def012345678",
                identity_tenant_id="72f988bf-1234-5678-9abc-def012345678",
                identity_issuer_url="https://oidc.example.com/issuer",
                dek_keyvault_url=None,
                dek_secret_id=None,
                kek_keyvault_url=None,
                kek_secret_id=None,
                kek_maa_url=None)

        # Verify
        self.assertEqual(result["datasetId"], "test-dataset-123")
        self.assertEqual(result["status"], "published")

        # Verify the body was constructed correctly
        call_args = mock_client.collaboration.analytics_datasets_document_id_publish_post.call_args
        body = call_args[0][2]
        self.assertEqual(body["name"], "test-dataset-123")
        self.assertEqual(
            body["store"]["storageAccountUrl"],
            "https://mystorageaccount.blob.core.windows.net")
        self.assertEqual(body["store"]["encryptionMode"], "SSE")
        self.assertEqual(body["identity"]["name"], "northwind-identity")
        self.assertNotIn("dek", body)
        self.assertNotIn("kek", body)

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_dataset_with_cpk_parameters(self, mock_get_client):
        """Test publishing a dataset using CPK parameters"""
        # Mock publish response
        mock_publish_response = {
            "datasetId": "test-dataset-cpk",
            "status": "published",
            "publishedAt": "2024-01-01T00:00:00Z"
        }
        mock_client = Mock()
        mock_client.collaboration.analytics_datasets_document_id_publish_post.return_value = mock_publish_response
        mock_get_client.return_value = mock_client

        # Mock file reading
        test_schema = {
            "fields": [{"fieldName": "id", "fieldType": "string"}],
            "format": "Delta"
        }

        with patch('builtins.open', unittest.mock.mock_open(read_data=json.dumps(test_schema))):
            # Execute with CPK parameters
            result = frontend_collaboration_dataset_publish(
                cmd=Mock(),
                collaboration_id="test-collab-123",
                document_id="test-dataset-cpk",
                body=None,
                storage_account_url="https://mystorageaccount.blob.core.windows.net",
                container_name="datasets",
                storage_account_type="AzureStorageAccount",
                encryption_mode="CPK",
                schema_file="@schema.json",
                schema_format=None,
                access_mode="ReadWrite",
                allowed_fields=None,
                identity_name="northwind-identity",
                identity_client_id="fb907136-1234-5678-9abc-def012345678",
                identity_tenant_id="72f988bf-1234-5678-9abc-def012345678",
                identity_issuer_url="https://oidc.example.com/issuer",
                dek_keyvault_url="https://mykeyvault.vault.azure.net",
                dek_secret_id="dek-secret-123",
                kek_keyvault_url="https://mykeyvault.vault.azure.net",
                kek_secret_id="kek-secret-123",
                kek_maa_url="https://sharedeus.eus.attest.azure.net")

        # Verify
        self.assertEqual(result["datasetId"], "test-dataset-cpk")
        self.assertEqual(result["status"], "published")

        # Verify CPK fields are present in body
        call_args = mock_client.collaboration.analytics_datasets_document_id_publish_post.call_args
        body = call_args[0][2]
        self.assertIn("dek", body)
        self.assertEqual(
            body["dek"]["keyVaultUrl"],
            "https://mykeyvault.vault.azure.net")
        self.assertIn("kek", body)
        self.assertEqual(body["kek"]["secretId"], "kek-secret-123")

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_dataset_mutual_exclusion(self, mock_get_client):
        """Test that body and parameters are mutually exclusive"""
        from azure.cli.core.util import CLIError

        mock_client = Mock()
        mock_get_client.return_value = mock_client

        # Execute with both body and parameters - should raise error
        with self.assertRaises(CLIError) as context:
            frontend_collaboration_dataset_publish(
                cmd=Mock(),
                collaboration_id="test-collab-123",
                document_id="test-dataset-123",
                body={"data": "test"},
                storage_account_url="https://mystorageaccount.blob.core.windows.net",
                container_name="datasets"
            )

        self.assertIn(
            "Cannot use --body together with individual parameters", str(context.exception))

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_dataset_missing_required_parameters(
            self, mock_get_client):
        """Test validation of required parameters"""
        from azure.cli.core.util import CLIError

        mock_client = Mock()
        mock_get_client.return_value = mock_client

        # Execute with missing required parameters - should raise error
        with self.assertRaises(CLIError) as context:
            frontend_collaboration_dataset_publish(
                cmd=Mock(),
                collaboration_id="test-collab-123",
                document_id="test-dataset-123",
                body=None,
                storage_account_url="https://mystorageaccount.blob.core.windows.net",
                # Missing container_name and other required params
            )

        self.assertIn("Missing required parameters", str(context.exception))

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_dataset_cpk_missing_keys(self, mock_get_client):
        """Test CPK mode requires DEK/KEK parameters"""
        from azure.cli.core.util import CLIError

        mock_client = Mock()
        mock_get_client.return_value = mock_client

        # Mock file reading
        test_schema = {"fields": [], "format": "Delta"}

        with patch('builtins.open', unittest.mock.mock_open(read_data=json.dumps(test_schema))):
            # Execute CPK mode without DEK/KEK params - should raise error
            with self.assertRaises(CLIError) as context:
                frontend_collaboration_dataset_publish(
                    cmd=Mock(),
                    collaboration_id="test-collab-123",
                    document_id="test-dataset-123",
                    body=None,
                    storage_account_url="https://mystorageaccount.blob.core.windows.net",
                    container_name="datasets",
                    storage_account_type="AzureStorageAccount",
                    encryption_mode="CPK",
                    schema_file="@schema.json",
                    access_mode="ReadWrite",
                    identity_name="northwind-identity",
                    identity_client_id="fb907136-1234-5678-9abc-def012345678",
                    identity_tenant_id="72f988bf-1234-5678-9abc-def012345678",
                    identity_issuer_url="https://oidc.example.com/issuer"
                    # Missing DEK/KEK params
                )

            self.assertIn(
                "CPK encryption mode requires", str(
                    context.exception))


if __name__ == '__main__':
    unittest.main()
