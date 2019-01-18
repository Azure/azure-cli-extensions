# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function
from knack.util import CLIError
import subprocess
import os
from ..azcopy.util import AzCopy, blob_client_auth_for_azcopy


def storage_blob_upload(cmd, client, source, destination):
    azcopy_creds = blob_client_auth_for_azcopy(cmd, client)
    azcopy = AzCopy(creds=azcopy_creds)
    # azcopy.copy(source, destination + '?' + (azcopy.creds.sas_token or ''), ['--recursive'])
    
    azcopy.copy(source, destination + '?' + (azcopy.creds.sas_token or ''))


def storage_blob_upload_batch(cmd, client, source, destination):
    azcopy_creds = blob_client_auth_for_azcopy(cmd, client)
    azcopy = AzCopy(creds=azcopy_creds)
    # azcopy.copy(source, destination + '?' + (azcopy.creds.sas_token or ''), ['--recursive'])
    azcopy.copy(source, destination + '?' + (azcopy.creds.sas_token or ''), ['--recursive'])
