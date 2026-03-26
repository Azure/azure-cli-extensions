# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Assist the command module to get correct type from SDK based on current API version"""

from azure.cli.core.profiles import get_sdk
from .profiles import CUSTOM_DATA_STORAGE


def get_blob_service_by_type(cli_ctx, blob_type):
    type_to_service = {
        'block': lambda ctx: get_sdk(ctx, CUSTOM_DATA_STORAGE, 'BlockBlobService', mod='blob'),
        'page': lambda ctx: get_sdk(ctx, CUSTOM_DATA_STORAGE, 'PageBlobService', mod='blob'),
        'append': lambda ctx: get_sdk(ctx, CUSTOM_DATA_STORAGE, 'AppendBlobService', mod='blob')
    }

    try:
        return type_to_service[blob_type](cli_ctx)
    except KeyError:
        return None


def get_blob_types():
    return 'block', 'page', 'append'


def get_blob_tier_names(cli_ctx, model):
    t_blob_tier_model = get_sdk(cli_ctx, CUSTOM_DATA_STORAGE, 'blob.models#' + model)
    return [v for v in dir(t_blob_tier_model) if not v.startswith('_')]


def get_delete_blob_snapshot_type_names():
    return 'include', 'only'


def get_delete_blob_snapshot_type(cli_ctx, name):
    t_delete_snapshot = get_sdk(cli_ctx, CUSTOM_DATA_STORAGE, 'DeleteSnapshot', mod='blob')
    return {'include': t_delete_snapshot.Include, 'only': t_delete_snapshot.Only}[name]


def get_delete_file_snapshot_type_names():
    return ['include']


def get_delete_file_snapshot_type(cli_ctx, name):
    t_delete_snapshot = get_sdk(cli_ctx, CUSTOM_DATA_STORAGE, 'DeleteSnapshot', mod='file.models')
    return {'include': t_delete_snapshot.Include}[name]


def get_container_access_type_names():
    return 'off', 'blob', 'container'


def get_container_access_type(cli_ctx, name):
    if name == 'off':
        return None
    if name == 'blob':
        return get_sdk(cli_ctx, CUSTOM_DATA_STORAGE, 'PublicAccess', mod='blob.models').Blob
    if name == 'container':
        return get_sdk(cli_ctx, CUSTOM_DATA_STORAGE, 'PublicAccess', mod='blob.models').Container
    raise KeyError
