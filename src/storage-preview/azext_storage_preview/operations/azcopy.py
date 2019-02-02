# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function
from knack.util import CLIError
from ..azcopy.util import AzCopy, blob_client_auth_for_azcopy, login_auth_for_azcopy


def storage_blob_upload(cmd, client, source, destination):
    azcopy = _azcopy_blob_client(cmd, client)
    azcopy.copy(source, _add_url_sas(destination, azcopy.creds.sas_token))


def storage_blob_upload_batch(cmd, client, source, destination):
    azcopy = _azcopy_blob_client(cmd, client)
    azcopy.copy(source, _add_url_sas(destination, azcopy.creds.sas_token), ['--recursive'])


def storage_blob_download(cmd, client, source, destination):
    azcopy = _azcopy_blob_client(cmd, client)
    azcopy.copy(_add_url_sas(source, azcopy.creds.sas_token), destination)


def storage_run_command(cmd, command_args):
    azcopy = _azcopy_login_client(cmd)
    azcopy.run_command([command_args])


def _add_url_sas(url, sas):
    if not sas:
        return url
    return '{}?{}'.format(url, sas)


def _azcopy_blob_client(cmd, client):
    return AzCopy(creds=blob_client_auth_for_azcopy(cmd, client))


def _azcopy_login_client(cmd):
    return AzCopy(creds=login_auth_for_azcopy(cmd))
