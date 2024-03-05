# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,protected-access

import os
from ._location_helper import normalize_location
from .__init__ import CLI_REPORTED_VERSION


def is_env(name):
    return 'AZURE_QUANTUM_ENV' in os.environ and os.environ['AZURE_QUANTUM_ENV'] == name


def base_url(location):
    if 'AZURE_QUANTUM_BASEURL' in os.environ:
        return os.environ['AZURE_QUANTUM_BASEURL']
    if is_env('canary'):
        return "https://eastus2euap.quantum.azure.com/"
    normalized_location = normalize_location(location)
    if is_env('dogfood'):
        return f"https://{normalized_location}.quantum-test.azure.com/"
    return f"https://{normalized_location}.quantum.azure.com/"


def _get_data_credentials(cli_ctx, subscription_id=None):
    from azure.cli.core._profile import Profile
    profile = Profile(cli_ctx=cli_ctx)
    creds, _, _ = profile.get_login_credentials(subscription_id=subscription_id, resource="https://quantum.microsoft.com")
    return creds


def get_appid():
    return f"az-cli-ext/{CLI_REPORTED_VERSION}"


# Control Plane clients


def cf_quantum_mgmt(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.azure_mgmt_quantum import AzureQuantumManagementClient
    client = get_mgmt_service_client(cli_ctx, AzureQuantumManagementClient, base_url_bound=False)
    # Add user agent on the management client to include extension information
    client._config.user_agent_policy.add_user_agent(get_appid())
    return client


def cf_workspaces(cli_ctx, *_):
    return cf_quantum_mgmt(cli_ctx).workspaces


def cf_workspace(cli_ctx, *_):
    return cf_quantum_mgmt(cli_ctx).workspace


def cf_offerings(cli_ctx, *_):
    return cf_quantum_mgmt(cli_ctx).offerings


# Data Plane clients

def cf_quantum(cli_ctx, subscription_id=None, resource_group_name=None, workspace_name=None, location=None):
    from .vendored_sdks.azure_quantum import QuantumClient
    creds = _get_data_credentials(cli_ctx, subscription_id)
    client = QuantumClient(creds, subscription_id, resource_group_name, workspace_name, base_url=base_url(location), user_agent=get_appid())
    return client


def cf_providers(cli_ctx, subscription_id=None, resource_group_name=None, workspace_name=None, location=None):
    return cf_quantum(cli_ctx, subscription_id, resource_group_name, workspace_name, location).providers


def cf_jobs(cli_ctx, subscription_id=None, resource_group_name=None, workspace_name=None, location=None):
    return cf_quantum(cli_ctx, subscription_id, resource_group_name, workspace_name, location).jobs


def cf_quotas(cli_ctx, subscription_id=None, resource_group_name=None, workspace_name=None, location=None):
    return cf_quantum(cli_ctx, subscription_id, resource_group_name, workspace_name, location).quotas


# Helper clients

def cf_vm_image_term(cli_ctx):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.marketplaceordering import MarketplaceOrderingAgreements
    market_place_client = get_mgmt_service_client(cli_ctx, MarketplaceOrderingAgreements)
    return market_place_client.marketplace_agreements
