# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_imagebuilder(cli_ctx, *_):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from .vendored_sdks.imagebuilder import ImageBuilderClient
    return get_mgmt_service_client(cli_ctx, ImageBuilderClient)


def cf_virtual_machine_image_templates(cli_ctx, *_):
    return cf_imagebuilder(cli_ctx).virtual_machine_image_templates


def cf_operations(cli_ctx, *_):
    return cf_imagebuilder(cli_ctx).operations
