import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from azext_serialconsole.custom import get_storage_account_info


class GetStorageAccountInfoTest(unittest.TestCase):

    def test_returns_none_when_resource_group_cannot_be_resolved(self):
        storage_accounts = Mock()
        storage_accounts.list.return_value = []
        scf = SimpleNamespace(storage_accounts=storage_accounts)

        self.assertIsNone(get_storage_account_info('https://mystorage.blob.core.windows.net/', scf))
        storage_accounts.get_properties.assert_not_called()

    def test_returns_paired_region_for_firewalled_storage_account(self):
        storage_accounts = Mock()
        storage_accounts.list.return_value = [
            SimpleNamespace(
                id=('/subscriptions/00000000-0000-0000-0000-000000000000/'
                    'resourceGroups/test-rg/providers/Microsoft.Storage/storageAccounts/mystorage')
            )
        ]
        storage_accounts.get_properties.return_value = SimpleNamespace(
            location='eastus',
            network_rule_set=SimpleNamespace(ip_rules=['10.0.0.1'])
        )
        scf = SimpleNamespace(storage_accounts=storage_accounts)

        self.assertEqual('westus', get_storage_account_info('https://mystorage.blob.core.windows.net/', scf))
        storage_accounts.get_properties.assert_called_once_with('test-rg', 'mystorage')
