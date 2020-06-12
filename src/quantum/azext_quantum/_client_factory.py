# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

import os


def is_env(name):
    return 'AZURE_QUANTUM_ENV' in os.environ and os.environ['AZURE_QUANTUM_ENV'] == name


def base_url():
    if 'AZURE_QUANTUM_BASEURL' in os.environ:
        return os.environ['AZURE_QUANTUM_BASEURL']
    if is_env('canary'):
        return "https://app-jobs-canarysouthcentralus.azurewebsites.net/"
    return "https://app-jobscheduler-prod.azurewebsites.net/"


def _get_data_credentials(cli_ctx, subscription_id=None):
    from azure.cli.core._profile import Profile
    profile = Profile(cli_ctx=cli_ctx)
    creds, _, _ = profile.get_login_credentials(subscription_id=subscription_id, resource="https://quantum.microsoft.com")
    return creds


def cf_quantum(cli_ctx, subscription_id=None, resource_group_name=None, workspace_name=None):
    from .vendored_sdks.azure_quantum import QuantumClient
    creds = _get_data_credentials(cli_ctx, subscription_id)
    return QuantumClient(creds, subscription_id, resource_group_name, workspace_name, base_url=base_url())


def cf_quantum_mgmt(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.azure_mgmt_quantum import QuantumManagementClient
    return get_mgmt_service_client(cli_ctx, QuantumManagementClient)


def cf_workspaces(cli_ctx, *_):
    return cf_quantum_mgmt(cli_ctx).workspaces


def cf_providers(cli_ctx, subscription_id=None, resource_group_name=None, workspace_name=None):
    return cf_quantum(cli_ctx, subscription_id, resource_group_name, workspace_name).providers


def cf_jobs(cli_ctx, subscription_id=None, resource_group_name=None, workspace_name=None):
    return cf_quantum(cli_ctx, subscription_id, resource_group_name, workspace_name).jobs
