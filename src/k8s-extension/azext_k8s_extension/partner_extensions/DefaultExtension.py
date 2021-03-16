# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument

from azext_k8s_extension.vendored_sdks.models import ExtensionInstance
from azext_k8s_extension.vendored_sdks.models import ExtensionInstanceUpdate
from azext_k8s_extension.vendored_sdks.models import ScopeCluster
from azext_k8s_extension.vendored_sdks.models import ScopeNamespace
from azext_k8s_extension.vendored_sdks.models import Scope

from azext_k8s_extension.partner_extensions.PartnerExtensionModel import PartnerExtensionModel


class DefaultExtension(PartnerExtensionModel):
    def Create(self, cmd, client, resource_group_name, cluster_name, name, cluster_type, extension_type,
               scope, auto_upgrade_minor_version, release_train, version, target_namespace,
               release_namespace, configuration_settings, configuration_protected_settings,
               configuration_settings_file, configuration_protected_settings_file):

        """Default validations & defaults for Create
           Must create and return a valid 'ExtensionInstance' object.

        """
        ext_scope = None
        if scope is None or scope.lower() == 'cluster':
            scope_cluster = ScopeCluster(release_namespace=release_namespace)
            ext_scope = Scope(cluster=scope_cluster, namespace=None)
        else:
            scope_namespace = ScopeNamespace(target_namespace=target_namespace)
            ext_scope = Scope(namespace=scope_namespace, cluster=None)

        # If release-train is not input, set it to 'stable'
        if release_train is None:
            release_train = 'stable'

        create_identity = False
        extension_instance = ExtensionInstance(
            extension_type=extension_type,
            auto_upgrade_minor_version=auto_upgrade_minor_version,
            release_train=release_train,
            version=version,
            scope=ext_scope,
            configuration_settings=configuration_settings,
            configuration_protected_settings=configuration_protected_settings,
            identity=None,
            location=""
        )
        return extension_instance, name, create_identity

    def Update(self, extension, auto_upgrade_minor_version, release_train, version):
        """Default validations & defaults for Update
           Must create and return a valid 'ExtensionInstanceUpdate' object.

        """
        return ExtensionInstanceUpdate(
            auto_upgrade_minor_version=auto_upgrade_minor_version,
            release_train=release_train,
            version=version
        )
