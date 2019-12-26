# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_mixed_reality(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.mixedreality import MixedRealityClient
    return get_mgmt_service_client(cli_ctx, MixedRealityClient)


def cf_operations(cli_ctx, *_):
    return cf_mixed_reality(cli_ctx).operations


def cf_remote_rendering_accounts(cli_ctx, *_):
    return cf_mixed_reality(cli_ctx).remote_rendering_accounts


def cf_spatial_anchors_accounts(cli_ctx, *_):
    return cf_mixed_reality(cli_ctx).spatial_anchors_accounts
