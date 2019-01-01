# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import os
import platform
import subprocess
import datetime


class AzCopy(object):
    system_executable_path = {
        'Darwin': ['azcopy_darwin_amd64_10.0.4', 'azcopy'],
        'Linux': ['azcopy_linux_amd64_10.0.4', 'azcopy'],
        'Windows': ['azcopy_windows_amd64_10.0.4', 'azcopy.exe']
    }

    def __init__(self):
        self.system = platform.system()
        curr_path = os.path.dirname(os.path.realpath(__file__))
        self.executable = os.path.join(curr_path, *AzCopy.system_executable_path[self.system])

    def run_command(self, args):
        args = [self.executable] + args
        subprocess.call(args)

    def copy(self, source, destination, flags=None):
        flags = flags or []
        self.run_command(['copy', source, destination] + flags)


def blob_client_auth_for_azcopy(cmd, blob_client):
    if blob_client.sas_token:
        return
    elif blob_client.account_key:
        from .._client_factory import cloud_storage_account_service_factory
        from .._validators import resource_type_type, services_type

        kwargs = {
            'account_name': blob_client.account_name,
            'account_key': blob_client.account_key
        }
        cloud_storage_client = cloud_storage_account_service_factory(cmd.cli_ctx, kwargs)
        t_account_permissions = cmd.loader.get_sdk('common.models#AccountPermissions')
        blob_client.sas_token = cloud_storage_client.generate_shared_access_signature(
            services_type(cmd.loader)('b'),
            resource_type_type(cmd.loader)('so'),
            t_account_permissions(_str='rwdlacup'),
            datetime.datetime.utcnow() + datetime.timedelta(days=1)
        )
    else:
        print("implement Oauth flow")
