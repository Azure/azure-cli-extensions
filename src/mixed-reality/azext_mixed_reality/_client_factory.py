# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_mixedreality_cl(cli_ctx):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_mixed_reality.vendored_sdks.mixedreality import MixedRealityClient
    return get_mgmt_service_client(cli_ctx, MixedRealityClient)


def cf_spatial_anchor_account(cli_ctx):
    return cf_mixedreality_cl(cli_ctx).spatial_anchors_accounts


def cf_remote_rendering_account(cli_ctx):
    return cf_mixedreality_cl(cli_ctx).remote_rendering_accounts
