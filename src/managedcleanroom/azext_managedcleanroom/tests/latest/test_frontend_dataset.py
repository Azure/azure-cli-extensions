# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Unit tests for dataset commands.
Tests dataset list, show, and publish commands from _frontend_custom.py.
"""

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
        mock_client.collaboration.analytics_dataset_document_id_get.return_value = MOCK_DATASET
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
        mock_client.collaboration.analytics_dataset_document_id_get.assert_called_once_with(
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
        mock_client.collaboration.analytics_dataset_document_id_publish_post.return_value = mock_publish_response
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
        mock_client.collaboration.analytics_dataset_document_id_publish_post.assert_called_once_with(
            "test-collab-123", "test-dataset-123", test_body)

    @patch('azext_managedcleanroom._frontend_custom.get_frontend_client')
    def test_publish_dataset_failure(self, mock_get_client):
        """Test handling publish failure (ERROR SCENARIO)"""
        # Mock error
        mock_client = Mock()
        mock_client.collaboration.analytics_dataset_document_id_publish_post.side_effect = Exception(
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


if __name__ == '__main__':
    unittest.main()
