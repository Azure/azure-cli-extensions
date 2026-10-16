import ast
import unittest

from pathlib import Path
from types import SimpleNamespace
from urllib.parse import quote
from unittest.mock import Mock


CUSTOM_PATH = Path(__file__).resolve().parents[2] / 'manual' / 'custom.py'
FUNCTION_NAMES = {
    '_normalize_arm_id',
    '_get_attribute_value',
    '_serialize_dataset_configuration',
    '_serialize_time_period',
    '_build_export_body',
    '_get_storage_account_location',
    '_put_export',
    'costmanagement_export_create',
    'costmanagement_export_update',
}


def load_custom_functions():
    module = ast.parse(CUSTOM_PATH.read_text(encoding='utf-8'))
    namespace = {
        'COSTMANAGEMENT_EXPORT_API_VERSION': '2023-11-01',
        'STORAGE_ACCOUNT_API_VERSION': '2023-05-01',
        'quote': quote,
    }

    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name in FUNCTION_NAMES:
            exec(compile(ast.Module(body=[node], type_ignores=[]), str(CUSTOM_PATH), 'exec'), namespace)

    return namespace


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


class CostManagementExportUnitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.namespace = load_custom_functions()

    def setUp(self):
        self.send_raw_request = Mock()
        self.namespace['send_raw_request'] = self.send_raw_request
        self.cmd = SimpleNamespace(
            cli_ctx=SimpleNamespace(
                cloud=SimpleNamespace(
                    endpoints=SimpleNamespace(resource_manager='https://management.azure.com/'))))

    def test_export_create_uses_latest_api_and_system_identity(self):
        self.send_raw_request.side_effect = [
            FakeResponse({'location': 'westus2'}),
            FakeResponse({'name': 'test-export'})
        ]

        result = self.namespace['costmanagement_export_create'](
            self.cmd,
            None,
            scope='subscriptions/00000000-0000-0000-0000-000000000000',
            export_name='test export',
            delivery_storage_container='exports',
            delivery_storage_account_id='/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/account',
            definition_timeframe='MonthToDate',
            delivery_directory='ad-hoc',
            definition_type='Usage',
            definition_time_period={'from_property': '2026-03-05T14:00:00Z', 'to': '2027-03-05T13:20:00Z'},
            definition_dataset_configuration={'columns': ['Date', 'MeterId']},
            schedule_status='Active',
            schedule_recurrence='Daily',
            schedule_recurrence_period={'from_property': '2026-03-05T14:00:00Z', 'to': '2027-03-05T13:20:00Z'})

        self.assertEqual(result, {'name': 'test-export'})
        self.assertEqual(self.send_raw_request.call_count, 2)

        storage_call = self.send_raw_request.call_args_list[0]
        self.assertEqual(storage_call.args[1], 'GET')
        self.assertEqual(
            storage_call.args[2],
            'https://management.azure.com/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/account?api-version=2023-05-01')

        export_call = self.send_raw_request.call_args_list[1]
        self.assertEqual(export_call.args[1], 'PUT')
        self.assertEqual(
            export_call.args[2],
            'https://management.azure.com/subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.CostManagement/exports/test%20export?api-version=2023-11-01')
        self.assertEqual(export_call.kwargs['body'], {
            'identity': {'type': 'SystemAssigned'},
            'location': 'westus2',
            'properties': {
                'format': 'Csv',
                'deliveryInfo': {
                    'destination': {
                        'resourceId': '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/account',
                        'container': 'exports',
                        'rootFolderPath': 'ad-hoc'
                    }
                },
                'definition': {
                    'type': 'Usage',
                    'timeframe': 'MonthToDate',
                    'timePeriod': {
                        'from': '2026-03-05T14:00:00Z',
                        'to': '2027-03-05T13:20:00Z'
                    },
                    'dataSet': {
                        'granularity': 'Daily',
                        'configuration': {
                            'columns': ['Date', 'MeterId']
                        }
                    }
                },
                'schedule': {
                    'status': 'Active',
                    'recurrence': 'Daily',
                    'recurrencePeriod': {
                        'from': '2026-03-05T14:00:00Z',
                        'to': '2027-03-05T13:20:00Z'
                    }
                }
            }
        })

    def test_export_update_preserves_etag_and_existing_destination(self):
        self.send_raw_request.side_effect = [
            FakeResponse({'location': 'eastus'}),
            FakeResponse({'name': 'test-export'})
        ]

        export_instance = SimpleNamespace(
            e_tag='etag-value',
            format='Csv',
            delivery_info=SimpleNamespace(
                destination=SimpleNamespace(
                    resource_id='/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/account',
                    container='exports',
                    root_folder_path='ad-hoc')),
            definition=SimpleNamespace(
                type='Usage',
                timeframe='TheLastMonth',
                time_period=SimpleNamespace(from_property='2026-01-01T00:00:00Z', to='2026-01-31T00:00:00Z'),
                data_set=SimpleNamespace(configuration=SimpleNamespace(columns=['Date']), granularity='Daily')),
            schedule=SimpleNamespace(
                status='Inactive',
                recurrence='Weekly',
                recurrence_period=SimpleNamespace(from_property='2026-02-01T00:00:00Z', to='2026-03-01T00:00:00Z')))
        client = SimpleNamespace(get=Mock(return_value=export_instance))

        result = self.namespace['costmanagement_export_update'](
            self.cmd,
            client,
            'subscriptions/00000000-0000-0000-0000-000000000000',
            'test export')

        self.assertEqual(result, {'name': 'test-export'})
        client.get.assert_called_once_with(
            scope='subscriptions/00000000-0000-0000-0000-000000000000',
            export_name='test export')
        self.assertEqual(self.send_raw_request.call_count, 2)
        export_call = self.send_raw_request.call_args_list[1]
        self.assertEqual(export_call.kwargs['body']['eTag'], 'etag-value')
        self.assertEqual(export_call.kwargs['body']['identity'], {'type': 'SystemAssigned'})
        self.assertEqual(export_call.kwargs['body']['location'], 'eastus')
        self.assertEqual(
            export_call.kwargs['body']['properties']['deliveryInfo']['destination']['resourceId'],
            '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/account')
        self.assertEqual(
            export_call.kwargs['body']['properties']['schedule']['recurrencePeriod'],
            {'from': '2026-02-01T00:00:00Z', 'to': '2026-03-01T00:00:00Z'})


if __name__ == '__main__':
    unittest.main()
