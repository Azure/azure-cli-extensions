# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from unittest.mock import MagicMock, patch

from azext_ad.manual.custom import create_service_principal_for_rbac_safe


@patch('azext_ad.manual.custom._get_role_custom_module')
def test_create_for_rbac_never_uses_user_display_name(mock_get_role_custom_module):
    cmd = MagicMock()
    cmd.cli_ctx = MagicMock()

    role_custom = MagicMock()
    mock_get_role_custom_module.return_value = role_custom

    graph_client = MagicMock()
    graph_client.application_list.return_value = iter([{'id': 'app-obj-id'}])
    graph_client.service_principal_list.return_value = iter([{'id': 'sp-obj-id'}])
    role_custom._graph_client_factory.return_value = graph_client

    role_custom.create_service_principal_for_rbac.return_value = {'appId': 'app-id'}
    create_service_principal_for_rbac_safe(cmd, display_name='shared-name')

    _, kwargs = role_custom.create_service_principal_for_rbac.call_args
    assert kwargs['display_name'] is None
    graph_client.application_update.assert_called_once_with('app-obj-id', {'displayName': 'shared-name'})
    graph_client.service_principal_update.assert_called_once_with('sp-obj-id', {'displayName': 'shared-name'})


@patch('azext_ad.manual.custom._get_role_custom_module')
def test_create_for_rbac_without_name_does_not_patch_display_name(mock_get_role_custom_module):
    cmd = MagicMock()
    cmd.cli_ctx = MagicMock()

    role_custom = MagicMock()
    mock_get_role_custom_module.return_value = role_custom
    role_custom.create_service_principal_for_rbac.return_value = {'appId': 'app-id'}

    create_service_principal_for_rbac_safe(cmd)

    role_custom._graph_client_factory.assert_not_called()
