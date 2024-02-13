# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType, client_factory
from ._client_factory import (cf_k8s_extension, cf_k8s_extension_operation, cf_k8s_extension_types)
from ._format import k8s_extension_list_table_format, k8s_extension_show_table_format, k8s_extension_types_list_table_format, k8s_extension_type_versions_list_table_format, k8s_extension_type_show_table_format, k8s_extension_type_version_show_table_format
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
        client_factory=cf_k8s_extension_types)
    with self.command_group(consts.EXTENSION_NAME + " extension-types", k8s_cluster_extension_type_sdk, client_factory=cf_k8s_extension_types, is_preview=True) \
            as g:
        g.custom_command('list-by-location', 'list_extension_types_by_location', table_transformer=k8s_extension_types_list_table_format)
        g.custom_command('show-by-location', 'show_extension_type_by_location', table_transformer=k8s_extension_type_show_table_format)

        g.custom_command('list-versions-by-location', 'list_extension_type_versions_by_location', table_transformer=k8s_extension_type_versions_list_table_format)
        g.custom_command('show-version-by-location', 'show_extension_type_version_by_location', table_transformer=k8s_extension_type_version_show_table_format)

        g.custom_command('list-by-cluster', 'list_extension_types_by_cluster', table_transformer=k8s_extension_types_list_table_format)
        g.custom_command('show-by-cluster', 'show_extension_type_by_cluster', table_transformer=k8s_extension_type_show_table_format)

        g.custom_command('list-versions-by-cluster', 'list_extension_type_versions_by_cluster', table_transformer=k8s_extension_type_versions_list_table_format)
        g.custom_command('show-version-by-cluster', 'show_extension_type_version_by_cluster', table_transformer=k8s_extension_type_version_show_table_format)

        g.custom_show_command('show', 'show_extension_type_by_location', deprecate_info=g.deprecate(redirect='az k8s-extension extension-types show-by-cluster', hide=True), table_transformer=k8s_extension_type_show_table_format)

        g.custom_command('list', 'list_extension_types_by_cluster', deprecate_info=g.deprecate(redirect='az k8s-extension extension-types list-by-cluster', hide=True), table_transformer=k8s_extension_types_list_table_format)

        g.custom_command('list-versions', 'list_extension_type_versions_by_cluster', deprecate_info=g.deprecate(redirect='az k8s-extension extension-types list-versions-by-cluster', hide=True), table_transformer=k8s_extension_type_versions_list_table_format)
