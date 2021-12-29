# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=wrong-import-order
import os
from re import L
import tempfile
import uuid
from azure.cli.core.azclierror import InvalidArgumentValueError
from .azure_storage_file import FileService
from ._utils import (get_azure_files_info, _pack_source_code)


class Empty:
    def upload_and_build(self, **_):
        pass


class FileUpload:
    '''
    Upload a file in local file system to upload url
    '''
    def __init__(self, upload_url):
        account_name, endpoint_suffix, share_name, relative_name, sas_token = get_azure_files_info(upload_url)
        self.account_name = account_name
        self.endpoint_suffix = endpoint_suffix
        self.share_name = share_name
        self.relative_name = relative_name
        self.sas_token = sas_token

    def upload_and_build(self, artifact_path, **_):
        if not artifact_path:
            raise InvalidArgumentValueError('--artifact-path is not set.')
        self._upload(artifact_path)

    def _upload(self, artifact_path):
        file_service = FileService(self.account_name, sas_token=self.sas_token, endpoint_suffix=self.endpoint_suffix)
        file_service.create_file_from_path(self.share_name, None, self.relative_name, artifact_path)


class FolderUpload(FileUpload):
    '''
    Compress and upload a folder in local file system to upload url
    '''
    def upload_and_build(self, source_path, **kwargs):
        if not source_path:
            raise InvalidArgumentValueError('--source-path is not set.')
        artifact_path = self._compress_folder(source_path)
        self._upload(artifact_path)

    def _compress_folder(self, folder):
        file_path = os.path.join(tempfile.gettempdir(), 'build_archive_{}.tar.gz'.format(uuid.uuid4().hex))
        _pack_source_code(os.path.abspath(folder), file_path)
        return file_path


def uploader_selector(source_path=None, artifact_path=None, upload_url=None, **_):
    if source_path:
        return FolderUpload(upload_url)
    if artifact_path:
        return FileUpload(upload_url)
    return Empty()
