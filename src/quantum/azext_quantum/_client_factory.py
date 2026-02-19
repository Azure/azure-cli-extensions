# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,protected-access

import os
from ._location_helper import normalize_location
from .__init__ import CLI_REPORTED_VERSION
from .vendored_sdks.azure_quantum_python._client import WorkspaceClient
from .vendored_sdks.azure_mgmt_quantum import AzureQuantumManagementClient


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
    creds, _, _ = profile.get_login_credentials(subscription_id=subscription_id)
    return creds


def get_appid():
    return f"az-cli-ext/{CLI_REPORTED_VERSION}"


# Control Plane clients

def cf_quantum_mgmt(cli_ctx, *_) -> AzureQuantumManagementClient:
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
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

def cf_quantum(cli_ctx, subscription: str, resource_group: str, ws_name: str, endpoint: str | None) -> WorkspaceClient:
    creds = _get_data_credentials(cli_ctx, subscription)
    if not endpoint:
        client = cf_workspaces(cli_ctx)
        ws = client.get(resource_group, ws_name)
        endpoint = ws.properties.endpoint_uri
    ws_cl = WorkspaceClient(endpoint, creds)
    return ws_cl


def cf_providers(cli_ctx, subscription: str, resource_group: str, ws_name: str, endpoint: str | None):
    return cf_quantum(cli_ctx, subscription, resource_group, ws_name, endpoint).services.providers


def cf_jobs(cli_ctx, subscription: str, resource_group: str, ws_name: str, endpoint: str | None):
    return cf_quantum(cli_ctx, subscription, resource_group, ws_name, endpoint).services.jobs


def cf_quotas(cli_ctx, subscription: str, resource_group: str, ws_name: str, endpoint: str | None):
    return cf_quantum(cli_ctx, subscription, resource_group, ws_name, endpoint).services.quotas


# Helper clients

def cf_vm_image_term(cli_ctx):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.marketplaceordering import MarketplaceOrderingAgreements
    market_place_client = get_mgmt_service_client(cli_ctx, MarketplaceOrderingAgreements)
    return market_place_client.marketplace_agreements
