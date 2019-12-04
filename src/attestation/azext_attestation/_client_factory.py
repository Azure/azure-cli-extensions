# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_attestation(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.attestation import AttestationManagementClient
    return get_mgmt_service_client(cli_ctx, AttestationManagementClient)


def cf_operations(cli_ctx, *_):
    return cf_attestation(cli_ctx).operations


def cf_attestation_providers(cli_ctx, *_):
    return cf_attestation(cli_ctx).attestation_providers
