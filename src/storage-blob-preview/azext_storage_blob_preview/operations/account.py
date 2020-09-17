# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Custom operations for storage account commands"""

import os
from azure.cli.core.util import get_file_json, shell_safe_json_parse


def create_management_policies(client, resource_group_name, account_name, policy):
    if os.path.exists(policy):
        policy = get_file_json(policy)
    else:
        policy = shell_safe_json_parse(policy)
    return client.create_or_update(resource_group_name, account_name, policy=policy)


def update_management_policies(client, resource_group_name, account_name, parameters=None):
    if parameters:
        parameters = parameters.policy
    return client.create_or_update(resource_group_name, account_name, policy=parameters)


# TODO: support updating other properties besides 'enable_change_feed,delete_retention_policy'
def update_blob_service_properties(cmd, instance, enable_change_feed=None, enable_delete_retention=None,
                                   delete_retention_days=None, enable_restore_policy=None, restore_days=None,
                                   enable_versioning=None, enable_container_delete_retention=None,
                                   container_delete_retention_days=None, enable_last_access_tracking=None):
    if enable_change_feed is not None:
        instance.change_feed = cmd.get_models('ChangeFeed')(enabled=enable_change_feed)

    if enable_container_delete_retention is not None:
        if enable_container_delete_retention is False:
            container_delete_retention_days = None
        instance.container_delete_retention_policy = cmd.get_models('DeleteRetentionPolicy')(
            enabled=enable_container_delete_retention, days=container_delete_retention_days)

    if enable_delete_retention is not None:
        if enable_delete_retention is False:
            delete_retention_days = None
        instance.delete_retention_policy = cmd.get_models('DeleteRetentionPolicy')(
            enabled=enable_delete_retention, days=delete_retention_days)

    if enable_restore_policy is not None:
        if enable_restore_policy is False:
            restore_days = None
        instance.restore_policy = cmd.get_models('RestorePolicyProperties')(
            enabled=enable_restore_policy, days=restore_days)

    if enable_versioning is not None:
        instance.is_versioning_enabled = enable_versioning

    # Update last access time tracking policy
    if enable_last_access_tracking is not None:
        LastAccessTimeTrackingPolicy = cmd.get_models('LastAccessTimeTrackingPolicy')
        instance.last_access_time_tracking_policy = LastAccessTimeTrackingPolicy(enable=enable_last_access_tracking)

    return instance
