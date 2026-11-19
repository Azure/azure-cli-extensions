# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from types import SimpleNamespace
from unittest import mock

import pytest
from azure.core.exceptions import HttpResponseError

from azext_vm_repair import storage_utils


def test_get_unmanaged_blob_service_client_uses_key_and_account_endpoint():
    storage_accounts = mock.Mock()
    storage_accounts.list_keys.return_value = SimpleNamespace(
        keys_property=[SimpleNamespace(value='account-key')])
    storage_accounts.get_properties.return_value = SimpleNamespace(
        primary_endpoints=SimpleNamespace(blob='https://account.blob.custom.example/'))
    blob_service = object()
    cmd = SimpleNamespace(cli_ctx=object())

    with mock.patch.object(storage_utils, 'cf_sa_for_keys', return_value=storage_accounts) as get_accounts, \
            mock.patch.object(storage_utils, 'cf_blob_service', return_value=blob_service) as create_blob_service:
        result = storage_utils.get_unmanaged_blob_service_client(cmd, 'source-rg', 'account')

    assert result is blob_service
    get_accounts.assert_called_once_with(cmd.cli_ctx, None)
    storage_accounts.list_keys.assert_called_once_with('source-rg', 'account', logging_enable=False)
    storage_accounts.get_properties.assert_called_once_with('source-rg', 'account')
    create_blob_service.assert_called_once_with(cmd.cli_ctx, {
        'account_name': 'account',
        'account_key': 'account-key',
        'account_url': 'https://account.blob.custom.example/',
    })


def test_get_unmanaged_blob_service_client_uses_cloud_endpoint_default_when_account_endpoint_missing():
    storage_accounts = mock.Mock()
    storage_accounts.list_keys.return_value = SimpleNamespace(
        keys_property=[SimpleNamespace(value='account-key')])
    storage_accounts.get_properties.return_value = SimpleNamespace(primary_endpoints=None)
    cmd = SimpleNamespace(cli_ctx=object())

    with mock.patch.object(storage_utils, 'cf_sa_for_keys', return_value=storage_accounts), \
            mock.patch.object(storage_utils, 'cf_blob_service', return_value='blob-service') as create_blob_service:
        result = storage_utils.get_unmanaged_blob_service_client(cmd, 'source-rg', 'account')

    assert result == 'blob-service'
    create_blob_service.assert_called_once_with(cmd.cli_ctx, {
        'account_name': 'account',
        'account_key': 'account-key',
    })


def test_storage_blob_operations_preserve_names_and_source_uri():
    blob_service = mock.Mock()
    source_blob = mock.Mock()
    destination_blob = mock.Mock()
    blob_service.get_blob_client.side_effect = [source_blob, destination_blob]
    source_uri = 'https://account.blob.example/container/source%25.vhd?snapshot=2026-10-23T01%3A02%3A03.0000000Z'
    snapshot_response = {'snapshot': '2026-10-23T01:02:03.0000000Z'}
    copy_response = {'copy_id': 'copy-id', 'copy_status': 'pending'}
    source_blob.create_snapshot.return_value = snapshot_response
    destination_blob.start_copy_from_url.return_value = copy_response
    destination_blob.get_blob_properties.return_value = {
        'copy': {'status': 'success'},
    }

    assert storage_utils.get_unmanaged_blob_client(blob_service, 'container', 'source%25.vhd') is source_blob
    assert storage_utils.create_unmanaged_blob_snapshot(source_blob) == snapshot_response['snapshot']
    assert storage_utils.get_unmanaged_blob_client(blob_service, 'container', 'copy.vhd') is destination_blob
    assert storage_utils.start_unmanaged_blob_copy(destination_blob, source_uri) == copy_response
    assert storage_utils.get_unmanaged_blob_copy_status(destination_blob) == 'success'

    assert blob_service.get_blob_client.call_args_list == [
        mock.call(container='container', blob='source%25.vhd'),
        mock.call(container='container', blob='copy.vhd'),
    ]
    source_blob.create_snapshot.assert_called_once_with()
    destination_blob.start_copy_from_url.assert_called_once_with(source_uri)
    destination_blob.get_blob_properties.assert_called_once_with()


@pytest.mark.parametrize('method_name,args', [
    ('create_snapshot', ()),
    ('start_copy_from_url', ('https://account/container/source?snapshot=timestamp',)),
    ('get_blob_properties', ()),
])
def test_storage_blob_http_errors_propagate(method_name, args):
    error = HttpResponseError(message='Storage request failed')
    blob_client = mock.Mock()
    getattr(blob_client, method_name).side_effect = error

    with pytest.raises(HttpResponseError) as raised:
        if method_name == 'create_snapshot':
            storage_utils.create_unmanaged_blob_snapshot(blob_client)
        elif method_name == 'start_copy_from_url':
            storage_utils.start_unmanaged_blob_copy(blob_client, *args)
        else:
            storage_utils.get_unmanaged_blob_copy_status(blob_client)

    assert raised.value is error
