# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_import_export(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from ..vendored_sdks.storageimportexport import StorageImportExport
    return get_mgmt_service_client(cli_ctx, StorageImportExport)


def cf_job(cli_ctx, *_):
    return cf_import_export(cli_ctx).job


def cf_bit_locker_key(cli_ctx, *_):
    return cf_import_export(cli_ctx).bit_locker_key


def cf_location(cli_ctx, *_):
    return cf_import_export(cli_ctx).location
