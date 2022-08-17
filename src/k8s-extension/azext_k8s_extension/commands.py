# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType, client_factory
from ._client_factory import (cf_k8s_extension, cf_k8s_extension_operation, cf_k8s_cluster_extension_types_operation, cf_k8s_cluster_extension_type_operation, cf_k8s_location_extension_types_operation, cf_k8s_extension_type_versions_operation)
from ._format import k8s_extension_list_table_format, k8s_extension_show_table_format, k8s_extension_types_list_table_format, k8s_extension_type_versions_list_table_format, k8s_extension_type_show_table_format
from . import consts


def load_command_table(self, _):

    k8s_extension_sdk = CliCommandType(
        operations_tmpl=consts.EXTENSION_PACKAGE_NAME + '.vendored_sdks.operations#K8sExtensionsOperations.{}',
        client_factory=cf_k8s_extension)

    with self.command_group(consts.EXTENSION_NAME, k8s_extension_sdk, client_factory=cf_k8s_extension_operation) \
            as g:
        g.custom_command('create', 'create_k8s_extension', supports_no_wait=True)
        g.custom_command('delete', 'delete_k8s_extension', supports_no_wait=True)
        g.custom_command('list', 'list_k8s_extension', table_transformer=k8s_extension_list_table_format)
        g.custom_show_command('show', 'show_k8s_extension', table_transformer=k8s_extension_show_table_format)
        g.custom_command('update', 'update_k8s_extension', supports_no_wait=True)

    # Subgroup - k8s-extension extension-types
    k8s_cluster_extension_type_sdk = CliCommandType(
        operations_tmpl=consts.EXTENSION_PACKAGE_NAME + '.vendored_sdks.operations#ClusterExtensionTypeOperations.{}',
        client_factory=cf_k8s_cluster_extension_type_operation)
    with self.command_group(consts.EXTENSION_NAME + " extension-types", k8s_cluster_extension_type_sdk, client_factory=cf_k8s_cluster_extension_type_operation, is_preview=True) \
            as g:
        g.custom_show_command('show', 'show_k8s_cluster_extension_type', table_transformer=k8s_extension_type_show_table_format)

    k8s_cluster_extension_types_sdk = CliCommandType(
        operations_tmpl=consts.EXTENSION_PACKAGE_NAME + '.vendored_sdks.operations.#ClusterExtensionTypesOperations.{}',
        client_factory=cf_k8s_cluster_extension_types_operation)
    with self.command_group(consts.EXTENSION_NAME + " extension-types", k8s_cluster_extension_types_sdk, client_factory=cf_k8s_cluster_extension_types_operation, is_preview=True) \
            as g:
        g.custom_command('list', 'list_k8s_cluster_extension_types', table_transformer=k8s_extension_types_list_table_format)

    k8s_location_extension_types_sdk = CliCommandType(
        operations_tmpl=consts.EXTENSION_PACKAGE_NAME + '.vendored_sdks.operations.#LocationExtensionTypesOperations.{}',
        client_factory=cf_k8s_location_extension_types_operation)
    with self.command_group(consts.EXTENSION_NAME + " extension-types", k8s_location_extension_types_sdk, client_factory=cf_k8s_location_extension_types_operation, is_preview=True) \
            as g:
        g.custom_command('list-by-location', 'list_k8s_location_extension_types', table_transformer=k8s_extension_types_list_table_format)

    k8s_extension_type_versions_sdk = CliCommandType(
        operations_tmpl=consts.EXTENSION_PACKAGE_NAME + '.vendored_sdks.operations.#ExtensionTypeVersionsOperations.{}',
        client_factory=cf_k8s_extension_type_versions_operation)
    with self.command_group(consts.EXTENSION_NAME + " extension-types", k8s_extension_type_versions_sdk, client_factory=cf_k8s_extension_type_versions_operation, is_preview=True) \
            as g:
        g.custom_command('list-versions', 'list_k8s_extension_type_versions', table_transformer=k8s_extension_type_versions_list_table_format)
