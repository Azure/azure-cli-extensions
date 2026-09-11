# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import ast
import os
import sys
import tempfile
import types
import unittest
from unittest.mock import MagicMock, patch


# Extract _upload_zip_to_storage from custom.py using ast/exec to avoid
# importing the full Azure CLI runtime.
_CUSTOM_PY = os.path.join(os.path.dirname(__file__), '..', '..', 'custom.py')

_ns = {
    '__name__': 'azext_functionapp.custom',
    'logger': MagicMock(),
    'time': __import__('time'),
}

with open(_CUSTOM_PY) as _f:
    _tree = ast.parse(_f.read())

for _node in _tree.body:
    if isinstance(_node, ast.FunctionDef) and _node.name in ('_upload_zip_to_storage',):
        exec(  # pylint: disable=exec-used
            compile(ast.Module(body=[_node], type_ignores=[]), _CUSTOM_PY, 'exec'),
            _ns)

_upload_zip_to_storage = _ns['_upload_zip_to_storage']


class TestUploadZipToStorage(unittest.TestCase):
    """Unit tests for _upload_zip_to_storage.

    These tests guard against the regression described in
    azure-cli-extensions#10024 / azure-cli#32044 where the zip file path
    string was uploaded as the blob content instead of the actual file bytes.
    """

    def _make_mocks(self):
        """Build the minimum set of mocks required to exercise _upload_zip_to_storage."""
        uploaded = {}

        def fake_upload_blob(blob_name, data, validate_content=False, progress_hook=None):
            uploaded['data'] = data
            mock_bc = MagicMock()
            mock_bc.url = 'https://fake.blob.core.windows.net/function-releases/' + blob_name
            return mock_bc

        mock_container = MagicMock()
        mock_container.exists.return_value = True
        mock_container.upload_blob.side_effect = fake_upload_blob

        mock_blob_svc = MagicMock()
        mock_blob_svc.account_name = 'fakeaccount'
        mock_blob_svc.credential.account_key = 'fakekey=='
        mock_blob_svc.get_container_client.return_value = mock_container

        mock_sas = MagicMock()
        mock_sas.generate_blob.return_value = 'se=2030&sp=r&sig=abc'

        mock_cmd = MagicMock()
        mock_cmd.cli_ctx.get_progress_controller.return_value = MagicMock()

        fake_appservice = types.ModuleType('azure.cli.command_modules.appservice.custom')
        fake_appservice.get_app_settings = MagicMock(return_value=[
            {'name': 'AzureWebJobsStorage',
             'value': 'DefaultEndpointsProtocol=https;AccountName=fakeaccount'}
        ])
        fake_appservice.update_app_settings = MagicMock()
        fake_appservice.web_client_factory = MagicMock(return_value=MagicMock())

        def fake_get_sdk(_cli_ctx, _resource_type, path):
            if 'BlobServiceClient' in path:
                cls = MagicMock()
                cls.from_connection_string.return_value = mock_blob_svc
                return cls
            if 'BlobSharedAccessSignature' in path:
                return MagicMock(return_value=mock_sas)
            return MagicMock()

        fake_profiles = types.ModuleType('azure.cli.core.profiles')
        fake_profiles.ResourceType = MagicMock(DATA_STORAGE_BLOB='DATA_STORAGE_BLOB')
        fake_profiles.get_sdk = fake_get_sdk

        return mock_cmd, fake_appservice, fake_profiles, uploaded

    def test_upload_reads_file_content_not_path_string(self):
        """_upload_zip_to_storage must upload the zip file's binary content,
        not the path string (regression test for azure-cli-extensions#10024)."""
        zip_bytes = b'PK\x03\x04' + b'\x00' * 26  # minimal ZIP local file header

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp.write(zip_bytes)
            tmp_path = tmp.name

        try:
            mock_cmd, fake_appservice, fake_profiles, uploaded = self._make_mocks()

            with patch.dict(sys.modules, {
                'azure.cli.command_modules.appservice.custom': fake_appservice,
                'azure.cli.core.profiles': fake_profiles,
            }):
                _upload_zip_to_storage(mock_cmd, 'my-rg', 'my-func', tmp_path)

            # The blob must contain the actual zip bytes, not the path string.
            self.assertIn('data', uploaded,
                          "upload_blob() was never called")
            self.assertEqual(uploaded['data'], zip_bytes,
                             "upload_blob() should receive the zip file content, "
                             "not the path string (fix for azure-cli-extensions#10024)")
        finally:
            os.unlink(tmp_path)

    def test_upload_does_not_pass_path_string_as_blob_content(self):
        """Explicitly verify that the src path string is NOT passed as blob data."""
        zip_bytes = b'PK\x03\x04fake zip content'

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp.write(zip_bytes)
            tmp_path = tmp.name

        try:
            mock_cmd, fake_appservice, fake_profiles, uploaded = self._make_mocks()

            with patch.dict(sys.modules, {
                'azure.cli.command_modules.appservice.custom': fake_appservice,
                'azure.cli.core.profiles': fake_profiles,
            }):
                _upload_zip_to_storage(mock_cmd, 'my-rg', 'my-func', tmp_path)

            # The blob must NOT be the raw path string encoded as bytes.
            self.assertNotEqual(
                uploaded.get('data'), tmp_path.encode(),
                "upload_blob() must NOT receive the file path as blob content")
            self.assertNotEqual(
                uploaded.get('data'), tmp_path,
                "upload_blob() must NOT receive the file path string as blob content")
        finally:
            os.unlink(tmp_path)


if __name__ == '__main__':
    unittest.main()
