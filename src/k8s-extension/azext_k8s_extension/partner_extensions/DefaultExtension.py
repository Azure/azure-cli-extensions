# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument

from azure.cli.core.util import user_confirmation

from ..vendored_sdks.models import Extension
from ..vendored_sdks.models import PatchExtension
from ..vendored_sdks.models import ScopeCluster
from ..vendored_sdks.models import ScopeNamespace
from ..vendored_sdks.models import Scope

from .PartnerExtensionModel import PartnerExtensionModel


class DefaultExtension(PartnerExtensionModel):
    def Create(
        self,
        cmd,
        client,
        resource_group_name,
        cluster_name,
        name,
        cluster_type,
        extension_type,
        scope,
        auto_upgrade_minor_version,
        release_train,
        version,
        target_namespace,
        release_namespace,
        configuration_settings,
        configuration_protected_settings,
        configuration_settings_file,
        configuration_protected_settings_file,
    ):
        """Default validations & defaults for Create
        Must create and return a valid 'Extension' object.
        """
        ext_scope = None
        if scope is not None:
            if scope.lower() == "cluster":
                scope_cluster = ScopeCluster(release_namespace=release_namespace)
                ext_scope = Scope(cluster=scope_cluster, namespace=None)
            elif scope.lower() == "namespace":
                scope_namespace = ScopeNamespace(target_namespace=target_namespace)
                ext_scope = Scope(namespace=scope_namespace, cluster=None)

        create_identity = True
        extension = Extension(
            extension_type=extension_type,
            auto_upgrade_minor_version=auto_upgrade_minor_version,
            release_train=release_train,
            version=version,
            scope=ext_scope,
            configuration_settings=configuration_settings,
            configuration_protected_settings=configuration_protected_settings,
        )
        return extension, name, create_identity

    def Update(
        self,
        cmd,
        resource_group_name,
        cluster_name,
        auto_upgrade_minor_version,
        release_train,
        version,
        configuration_settings,
        configuration_protected_settings,
        original_extension: Extension,
        yes=False,
    ):
        """Default validations & defaults for Update
        Must create and return a valid 'PatchExtension' object.
        """

        return PatchExtension(
            auto_upgrade_minor_version=auto_upgrade_minor_version,
            release_train=release_train,
            version=version,
            configuration_settings=configuration_settings,
            configuration_protected_settings=configuration_protected_settings,
        )

    def Delete(
        self, cmd, client, resource_group_name, cluster_name, name, cluster_type, yes
    ):
        user_confirmation_factory(cmd, yes)


def user_confirmation_factory(
    cmd, yes, message="Are you sure you want to perform this operation?"
):
    if cmd.cli_ctx.config.getboolean("core", "disable_confirm_prompt", fallback=False):
        return
    user_confirmation(message, yes=yes)
