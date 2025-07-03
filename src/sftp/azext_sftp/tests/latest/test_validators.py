# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest import mock
from types import SimpleNamespace

from azext_sftp import _validators
from azure.cli.core import azclierror


class SftpValidatorsTest(unittest.TestCase):
    """Test suite for SFTP validators.
    
    Owner: johnli1
    """

    def test_storage_account_name_or_id_validator_no_storage_account(self):
        """Test validator with no storage account provided."""
        # Arrange
        cmd_mock = mock.Mock()
        namespace = SimpleNamespace()
        
        # Act
        _validators.storage_account_name_or_id_validator(cmd_mock, namespace)
        
        # Assert - should not raise any errors and not modify namespace
        self.assertFalse(hasattr(namespace, 'storage_account'))

    def test_storage_account_name_or_id_validator_none_storage_account(self):
        """Test validator with None storage account."""
        # Arrange
        cmd_mock = mock.Mock()
        namespace = SimpleNamespace(storage_account=None)
        
        # Act
        _validators.storage_account_name_or_id_validator(cmd_mock, namespace)
        
        # Assert - should not raise any errors and not modify namespace
        self.assertEqual(None, namespace.storage_account)

    def test_storage_account_name_or_id_validator_empty_storage_account(self):
        """Test validator with empty storage account."""
        # Arrange
        cmd_mock = mock.Mock()
        namespace = SimpleNamespace(storage_account="")
        
        # Act
        _validators.storage_account_name_or_id_validator(cmd_mock, namespace)
        
        # Assert - should not raise any errors and not modify namespace
        self.assertEqual("", namespace.storage_account)

    @mock.patch('azext_sftp._validators.is_valid_resource_id')
    def test_storage_account_name_or_id_validator_with_valid_resource_id(self, mock_is_valid_resource_id):
        """Test validator with already valid resource ID."""
        # Arrange
        mock_is_valid_resource_id.return_value = True
        resource_id = "/subscriptions/test-sub/resourceGroups/test-rg/providers/Microsoft.Storage/storageAccounts/testaccount"
        
        cmd_mock = mock.Mock()
        namespace = SimpleNamespace(
            storage_account=resource_id,
            resource_group_name="test-rg"
        )
        
        # Act
        _validators.storage_account_name_or_id_validator(cmd_mock, namespace)
        
        # Assert
        mock_is_valid_resource_id.assert_called_once_with(resource_id)
        # Storage account should remain unchanged
        self.assertEqual(resource_id, namespace.storage_account)

    @mock.patch('azext_sftp._validators.is_valid_resource_id')
    def test_storage_account_name_or_id_validator_missing_resource_group(self, mock_is_valid_resource_id):
        """Test validator error when resource group is missing."""
        # Arrange
        mock_is_valid_resource_id.return_value = False
        
        cmd_mock = mock.Mock()
        namespace = SimpleNamespace(
            storage_account="testaccount"
        )
        
        # Act & Assert
        with self.assertRaises(azclierror.RequiredArgumentMissingError) as context:
            _validators.storage_account_name_or_id_validator(cmd_mock, namespace)
        
        self.assertIn("When providing storage account name, --resource-group is required", str(context.exception))
        mock_is_valid_resource_id.assert_called_once_with("testaccount")

    @mock.patch('azext_sftp._validators.is_valid_resource_id')
    def test_storage_account_name_or_id_validator_empty_resource_group(self, mock_is_valid_resource_id):
        """Test validator error when resource group is empty."""
        # Arrange
        mock_is_valid_resource_id.return_value = False
        
        cmd_mock = mock.Mock()
        namespace = SimpleNamespace(
            storage_account="testaccount",
            resource_group_name=""
        )
        
        # Act & Assert
        with self.assertRaises(azclierror.RequiredArgumentMissingError) as context:
            _validators.storage_account_name_or_id_validator(cmd_mock, namespace)
        
        self.assertIn("When providing storage account name, --resource-group is required", str(context.exception))
        mock_is_valid_resource_id.assert_called_once_with("testaccount")

    @mock.patch('azext_sftp._validators.is_valid_resource_id')
    def test_storage_account_name_or_id_validator_none_resource_group(self, mock_is_valid_resource_id):
        """Test validator error when resource group is None."""
        # Arrange
        mock_is_valid_resource_id.return_value = False
        
        cmd_mock = mock.Mock()
        namespace = SimpleNamespace(
            storage_account="testaccount",
            resource_group_name=None
        )
        
        # Act & Assert
        with self.assertRaises(azclierror.RequiredArgumentMissingError) as context:
            _validators.storage_account_name_or_id_validator(cmd_mock, namespace)
        
        self.assertIn("When providing storage account name, --resource-group is required", str(context.exception))
        mock_is_valid_resource_id.assert_called_once_with("testaccount")

    @mock.patch('azext_sftp._validators.resource_id')
    @mock.patch('azext_sftp._validators.get_subscription_id')
    @mock.patch('azext_sftp._validators.is_valid_resource_id')
    def test_storage_account_name_or_id_validator_with_name_and_rg(
        self, mock_is_valid_resource_id, mock_get_subscription, mock_resource_id
    ):
        """Test validator with storage account name and resource group."""
        # Arrange
        mock_is_valid_resource_id.return_value = False
        mock_get_subscription.return_value = "test-subscription-id"
        mock_resource_id.return_value = "/subscriptions/test-subscription-id/resourceGroups/test-rg/providers/Microsoft.Storage/storageAccounts/testaccount"
        
        cmd_mock = mock.Mock()
        namespace = SimpleNamespace(
            storage_account="testaccount",
            resource_group_name="test-rg"
        )
        
        # Act
        _validators.storage_account_name_or_id_validator(cmd_mock, namespace)
        
        # Assert
        mock_is_valid_resource_id.assert_called_once_with("testaccount")
        mock_get_subscription.assert_called_once_with(cmd_mock.cli_ctx)
        mock_resource_id.assert_called_once_with(
            subscription="test-subscription-id",
            resource_group="test-rg",
            namespace="Microsoft.Storage",
            type="storageAccounts",
            name="testaccount"
        )
        self.assertEqual(
            namespace.storage_account,
            "/subscriptions/test-subscription-id/resourceGroups/test-rg/providers/Microsoft.Storage/storageAccounts/testaccount"
        )


if __name__ == '__main__':
    unittest.main()
