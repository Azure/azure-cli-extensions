# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._client_factory import spatial_anchors_account_factory


def list_spatial_anchors_accounts(
        cmd,
        resource_group_name=None,
        custom_headers=None,
        raw=False,
        **operation_config):
    operations = spatial_anchors_account_factory(cmd.cli_ctx, None)
    if resource_group_name:
        return operations.list_by_resource_group(resource_group_name, custom_headers, raw, **operation_config)
    return operations.list_by_subscription(custom_headers, raw, **operation_config)


def renew_key(
        cmd,
        resource_group_name,
        spatial_anchors_account_name,
        key,
        custom_headers=None,
        raw=False,
        **operation_config):
    operations = spatial_anchors_account_factory(cmd.cli_ctx, None)
    serial = ['primary', 'secondary'].index(key) + 1
    return operations.regenerate_keys(
        resource_group_name,
        spatial_anchors_account_name,
        serial,
        custom_headers,
        raw,
        **operation_config)
