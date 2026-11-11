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
                storage_account_type="Azure_BlobStorage",
                encryption_mode="SSE",
                schema_file="@schema.json",
                schema_format=None,
                access_mode="read",
                allowed_fields="customer_id,revenue",
                identity_name="northwind-identity",
                identity_client_id="fb907136-1234-5678-9abc-def012345678",
                identity_tenant_id="72f988bf-1234-5678-9abc-def012345678",
                dek_keyvault_url=None,
                dek_secret_id=None,
                kek_keyvault_url=None,
                kek_secret_id=None,
                kek_authority_type=None,
                kek_authority_endpoint=None)

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
        self.assertNotIn("issuerUrl", body["identity"])
        self.assertEqual(
            body["datasetAccessPolicy"],
            {"accessMode": "read", "allowedFields": ["customer_id", "revenue"]})
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
                storage_account_type="Azure_BlobStorage",
                encryption_mode="CPK",
                schema_file="@schema.json",
                schema_format=None,
                access_mode="read",
                allowed_fields="id",
                identity_name="northwind-identity",
                identity_client_id="fb907136-1234-5678-9abc-def012345678",
                identity_tenant_id="72f988bf-1234-5678-9abc-def012345678",
                dek_keyvault_url="https://mykeyvault.vault.azure.net",
                dek_secret_id="dek-secret-123",
                kek_keyvault_url="https://mykeyvault.vault.azure.net",
                kek_secret_id="kek-secret-123",
                kek_authority_type="MAA",
                kek_authority_endpoint="https://sharedeus.eus.attest.azure.net")

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
        self.assertEqual(
            body["kek"]["authority"],
            {"type": "MAA", "endpoint": "https://sharedeus.eus.attest.azure.net"})
        # Deprecated maaUrl is still sent for MAA for backward compatibility.
        self.assertEqual(
            body["kek"]["maaUrl"], "https://sharedeus.eus.attest.azure.net")

    def _publish_cpk(self, mock_get_client, **kek_authority_kwargs):
        mock_client = Mock()
        mock_client.collaboration.analytics_datasets_document_id_publish_post.return_value = {}
        mock_get_client.return_value = mock_client

        test_schema = {"fields": [{"fieldName": "id", "fieldType": "string"}]}
        with patch('builtins.open', unittest.mock.mock_open(read_data=json.dumps(test_schema))):
            frontend_collaboration_dataset_publish(
                cmd=Mock(),
                collaboration_id="test-collab-123",
                document_id="test-dataset-cpk",
                storage_account_url="https://mystorageaccount.blob.core.windows.net",
                container_name="datasets",
                storage_account_type="Azure_BlobStorage",
                encryption_mode="CPK",
                schema_file="@schema.json",
                access_mode="read",
                allowed_fields="id",
                identity_name="northwind-identity",
                identity_client_id="fb907136-1234-5678-9abc-def012345678",
                identity_tenant_id="72f988bf-1234-5678-9abc-def012345678",
                dek_keyvault_url="https://mykeyvault.vault.azure.net",
                dek_secret_id="dek-secret-123",
                kek_keyvault_url="https://mykeyvault.vault.azure.net",
                kek_secret_id="kek-secret-123",
                **kek_authority_kwargs)

        call_args = mock_client.collaboration.analytics_datasets_document_id_publish_post.call_args
        return call_args[0][2]

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_dataset_cpk_cgs_authority(self, mock_get_client):
        """Test CPK publish with CGS authority sends authority and omits maaUrl"""
        body = self._publish_cpk(mock_get_client, kek_authority_type="CGS")

        self.assertEqual(body["kek"]["authority"], {"type": "CGS"})
        self.assertNotIn("maaUrl", body["kek"])
        self.assertNotIn("authority", body["dek"])

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_dataset_cpk_authority_type_case_insensitive(self, mock_get_client):
        """Test that authority type is normalized to upper case"""
        body = self._publish_cpk(mock_get_client, kek_authority_type="cgs")

        self.assertEqual(body["kek"]["authority"], {"type": "CGS"})

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_dataset_cpk_endpoint_only_defaults_to_maa(self, mock_get_client):
        """Test that an endpoint without a type (e.g. deprecated --kek-maa-url) implies MAA"""
        body = self._publish_cpk(
            mock_get_client,
            kek_authority_endpoint="https://sharedeus.eus.attest.azure.net")

        self.assertEqual(
            body["kek"]["authority"],
            {"type": "MAA", "endpoint": "https://sharedeus.eus.attest.azure.net"})
        self.assertEqual(
            body["kek"]["maaUrl"], "https://sharedeus.eus.attest.azure.net")

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_dataset_cpk_maa_requires_endpoint(self, mock_get_client):
        """Test that MAA authority without an endpoint is rejected"""
        from azure.cli.core.util import CLIError

        with self.assertRaises(CLIError) as context:
            self._publish_cpk(mock_get_client, kek_authority_type="MAA")

        self.assertIn("--kek-authority-endpoint is required", str(context.exception))
        mock_get_client.return_value.collaboration \
            .analytics_datasets_document_id_publish_post.assert_not_called()

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_dataset_cpk_cgs_rejects_endpoint(self, mock_get_client):
        """Test that CGS authority with an endpoint is rejected"""
        from azure.cli.core.util import CLIError

        with self.assertRaises(CLIError) as context:
            self._publish_cpk(
                mock_get_client,
                kek_authority_type="CGS",
                kek_authority_endpoint="https://sharedeus.eus.attest.azure.net")

        self.assertIn("not supported when --kek-authority-type is CGS", str(context.exception))

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_dataset_cpk_missing_authority(self, mock_get_client):
        """Test that CPK mode requires a KEK authority"""
        from azure.cli.core.util import CLIError

        with self.assertRaises(CLIError) as context:
            self._publish_cpk(mock_get_client)

        self.assertIn("--kek-authority-type", str(context.exception))

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
    def test_publish_dataset_body_conflicts_with_every_parameter_flag(self, mock_get_client):
        """Test that no parameter-mode flag is silently ignored when combined with --body"""
        from azure.cli.core.util import CLIError

        mock_client = Mock()
        mock_get_client.return_value = mock_client

        parameter_flags = {
            "kek_authority_type": "CGS",
            "kek_authority_endpoint": "https://sharedeus.eus.attest.azure.net",
            "dek_keyvault_url": "https://mykeyvault.vault.azure.net",
            "dek_secret_id": "dek-secret-123",
            "kek_keyvault_url": "https://mykeyvault.vault.azure.net",
            "kek_secret_id": "kek-secret-123",
            "schema_format": "Delta",
            "allowed_fields": "id",
            "subdirectory": "year=2026",
            "identity_issuer_url": "https://oidc.example.com/issuer",
        }
        for flag, value in parameter_flags.items():
            with self.subTest(flag=flag):
                with self.assertRaises(CLIError) as context:
                    frontend_collaboration_dataset_publish(
                        cmd=Mock(),
                        collaboration_id="test-collab-123",
                        document_id="test-dataset-123",
                        body={"data": "test"},
                        **{flag: value})
                self.assertIn(
                    "Cannot use --body together with individual parameters",
                    str(context.exception))

        mock_client.collaboration.analytics_datasets_document_id_publish_post.assert_not_called()

    def _publish_sse(self, mock_get_client, **overrides):
        mock_client = Mock()
        mock_client.collaboration.analytics_datasets_document_id_publish_post.return_value = {}
        mock_get_client.return_value = mock_client

        kwargs = {
            "storage_account_url": "https://mystorageaccount.blob.core.windows.net",
            "container_name": "datasets",
            "storage_account_type": "Azure_BlobStorage",
            "encryption_mode": "SSE",
            "schema_file": "@schema.json",
            "access_mode": "read",
            "allowed_fields": "id",
            "identity_name": "northwind-identity",
            "identity_client_id": "fb907136-1234-5678-9abc-def012345678",
            "identity_tenant_id": "72f988bf-1234-5678-9abc-def012345678",
        }
        kwargs.update(overrides)

        test_schema = {"fields": [{"fieldName": "id", "fieldType": "string"}]}
        with patch('builtins.open', unittest.mock.mock_open(read_data=json.dumps(test_schema))):
            frontend_collaboration_dataset_publish(
                cmd=Mock(),
                collaboration_id="test-collab-123",
                document_id="test-dataset-sse",
                **kwargs)

        call_args = mock_client.collaboration.analytics_datasets_document_id_publish_post.call_args
        return call_args[0][2]

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_dataset_requires_allowed_fields(self, mock_get_client):
        """Test that --allowed-fields is required because the frontend requires allowedFields"""
        from azure.cli.core.util import CLIError

        with self.assertRaises(CLIError) as context:
            self._publish_sse(mock_get_client, allowed_fields=None)

        self.assertIn("Missing required parameters: --allowed-fields", str(context.exception))

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_dataset_rejects_empty_allowed_fields(self, mock_get_client):
        """Test that --allowed-fields must contain at least one field name"""
        from azure.cli.core.util import CLIError

        with self.assertRaises(CLIError) as context:
            self._publish_sse(mock_get_client, allowed_fields=" , ")

        self.assertIn("--allowed-fields must contain at least one field name", str(context.exception))

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_dataset_allowed_fields_are_trimmed(self, mock_get_client):
        """Test that allowed field names are trimmed and empty entries dropped"""
        body = self._publish_sse(mock_get_client, allowed_fields=" id , name ,")

        self.assertEqual(body["datasetAccessPolicy"]["allowedFields"], ["id", "name"])

    @patch('azext_managedcleanroom._frontend_custom.logger')
    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_dataset_identity_issuer_url_is_ignored(self, mock_get_client, mock_logger):
        """Test that deprecated --identity-issuer-url is not sent and a warning is logged"""
        body = self._publish_sse(
            mock_get_client, identity_issuer_url="https://oidc.example.com/issuer")

        self.assertEqual(
            body["identity"],
            {
                "name": "northwind-identity",
                "clientId": "fb907136-1234-5678-9abc-def012345678",
                "tenantId": "72f988bf-1234-5678-9abc-def012345678",
            })
        mock_logger.warning.assert_called_once()
        self.assertIn("--identity-issuer-url", mock_logger.warning.call_args[0][0])

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
                    storage_account_type="Azure_BlobStorage",
                    encryption_mode="CPK",
                    schema_file="@schema.json",
                    access_mode="read",
                    allowed_fields="id",
                    identity_name="northwind-identity",
                    identity_client_id="fb907136-1234-5678-9abc-def012345678",
                    identity_tenant_id="72f988bf-1234-5678-9abc-def012345678",
                    # Missing DEK/KEK params
                )

            self.assertIn(
                "CPK encryption mode requires", str(
                    context.exception))

    @patch("azext_managedcleanroom._frontend_custom.get_frontend_client")
    def test_publish_dataset_with_subdirectory(self, mock_get_client):
        """Test that --subdirectory propagates into the request body's store"""
        mock_publish_response = {"datasetId": "test-dataset-sub", "status": "published"}
        mock_client = Mock()
        mock_client.collaboration.analytics_datasets_document_id_publish_post.return_value = mock_publish_response
        mock_get_client.return_value = mock_client

        test_schema = {"fields": [], "format": "Delta"}

        with patch("builtins.open", unittest.mock.mock_open(read_data=json.dumps(test_schema))):
            frontend_collaboration_dataset_publish(
                cmd=Mock(),
                collaboration_id="test-collab-123",
                document_id="test-dataset-sub",
                body=None,
                storage_account_url="https://mystorageaccount.blob.core.windows.net",
                container_name="datasets",
                storage_account_type="Azure_BlobStorage",
                encryption_mode="SSE",
                schema_file="@schema.json",
                access_mode="read",
                allowed_fields="id",
                identity_name="northwind-identity",
                identity_client_id="fb907136-1234-5678-9abc-def012345678",
                identity_tenant_id="72f988bf-1234-5678-9abc-def012345678",
                subdirectory="year=2026/month=05",
            )

        call_args = mock_client.collaboration.analytics_datasets_document_id_publish_post.call_args
        body = call_args[0][2]
        self.assertEqual(body["store"]["subdirectory"], "year=2026/month=05")

    @patch("azext_managedcleanroom._frontend_custom.get_frontend_client")
    def test_publish_dataset_subdirectory_default_omitted(self, mock_get_client):
        """Test that subdirectory key is omitted from store when not provided"""
        mock_publish_response = {"datasetId": "test-dataset-nosub", "status": "published"}
        mock_client = Mock()
        mock_client.collaboration.analytics_datasets_document_id_publish_post.return_value = mock_publish_response
        mock_get_client.return_value = mock_client

        test_schema = {"fields": [], "format": "Delta"}

        with patch("builtins.open", unittest.mock.mock_open(read_data=json.dumps(test_schema))):
            frontend_collaboration_dataset_publish(
                cmd=Mock(),
                collaboration_id="test-collab-123",
                document_id="test-dataset-nosub",
                body=None,
                storage_account_url="https://mystorageaccount.blob.core.windows.net",
                container_name="datasets",
                storage_account_type="Azure_BlobStorage",
                encryption_mode="SSE",
                schema_file="@schema.json",
                access_mode="read",
                allowed_fields="id",
                identity_name="northwind-identity",
                identity_client_id="fb907136-1234-5678-9abc-def012345678",
                identity_tenant_id="72f988bf-1234-5678-9abc-def012345678",
            )

        call_args = mock_client.collaboration.analytics_datasets_document_id_publish_post.call_args
        body = call_args[0][2]
        self.assertNotIn("subdirectory", body["store"])


if __name__ == '__main__':
    unittest.main()
