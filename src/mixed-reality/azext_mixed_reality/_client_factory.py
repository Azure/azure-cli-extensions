# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def spatial_anchors_account(cli_ctx, _):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_mixed_reality.mixed_reality.mixed_reality_client import MixedRealityClient
    return get_mgmt_service_client(cli_ctx, MixedRealityClient).spatial_anchors_accounts