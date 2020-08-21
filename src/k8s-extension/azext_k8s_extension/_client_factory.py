# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_k8s_extension(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_k8s_extension.vendored_sdks import K8sExtensionClient
    return get_mgmt_service_client(cli_ctx, K8sExtensionClient)


def cf_k8s_extension_operation(cli_ctx, _):
    return cf_k8s_extension(cli_ctx).k8s_extensions
