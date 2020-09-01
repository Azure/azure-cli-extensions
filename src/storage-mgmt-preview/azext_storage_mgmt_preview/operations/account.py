# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Custom operations for storage account commands"""

from knack.log import get_logger
from knack.util import CLIError

logger = get_logger(__name__)


def update_file_service_properties(cmd, instance, enable_delete_retention=None,
                                   delete_retention_days=None, enable_smb_multichannel=None):

    if enable_delete_retention is not None:
        if enable_delete_retention is False:
            delete_retention_days = None
        instance.share_delete_retention_policy = cmd.get_models('DeleteRetentionPolicy')(
            enabled=enable_delete_retention, days=delete_retention_days)

    # If already enabled, only update days
    if enable_delete_retention is None and delete_retention_days is not None:
        if instance.share_delete_retention_policy is not None and instance.share_delete_retention_policy.enabled:
            instance.share_delete_retention_policy.days = delete_retention_days
        else:
            raise CLIError("Delete Retention Policy hasn't been enabled, and you cannot set delete retention days. "
                           "Please set --enable-delete-retention as true to enable Delete Retention Policy.")

    if enable_smb_multichannel is not None:
        instance.protocol_settings.smb.multichannel.enabled = enable_smb_multichannel

    return instance
