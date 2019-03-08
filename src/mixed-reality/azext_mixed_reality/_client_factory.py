# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def mixed_reality_client_factory(cli_ctx):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_mixed_reality.vendored_sdks.mixedreality.mixed_reality_client import MixedRealityClient
    return get_mgmt_service_client(cli_ctx, MixedRealityClient, subscription_bound=True)


def spatial_anchors_account_factory(cli_ctx, _):
    return mixed_reality_client_factory(cli_ctx).spatial_anchors_accounts
