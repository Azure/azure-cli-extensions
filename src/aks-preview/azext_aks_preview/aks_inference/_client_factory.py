# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Client factory — the classic equivalent of `_client_factory.py:22` (cf_managed_clusters)."""

from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType  # noqa: F401  (real code registers a custom profile)

from .vendored_sdk import AIManagerMgmtClient


def cf_ai_managers(cli_ctx, *_):
    # get_mgmt_service_client wires up the credential, subscription id, ARM base url and
    # cloud-specific scopes, then instantiates our (vendored) client.
    client = get_mgmt_service_client(cli_ctx, AIManagerMgmtClient)
    return client.ai_managers


def cf_ai_manager_namespaces(cli_ctx, *_):
    client = get_mgmt_service_client(cli_ctx, AIManagerMgmtClient)
    return client.ai_manager_namespaces
