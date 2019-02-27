# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def mixed_reality_client_factory(cli_ctx, **_):
    from azure.cli.core.commands.client_factory import _get_mgmt_service_client
    from azext_mixed_reality.mixed_reality.mixed_reality_client import MixedRealityClient
    client, _ = _get_mgmt_service_client(cli_ctx, MixedRealityClient, subscription_bound=False)
    return client


def spatial_anchors_account_factory(cli_ctx, kwargs):
    return mixed_reality_client_factory(cli_ctx, **kwargs).spatial_anchors_accounts