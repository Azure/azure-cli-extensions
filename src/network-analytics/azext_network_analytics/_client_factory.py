# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from azure.cli.core.profiles import ResourceType


def cf_storage_container(cli_ctx, *_):
    from azure.cli.core.profiles import get_sdk
    return get_sdk(cli_ctx, ResourceType.DATA_STORAGE_BLOB, '_container_client#ContainerClient')
