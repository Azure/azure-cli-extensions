# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument

from knack.log import get_logger

from ..vendored_sdks.models import ExtensionInstance
from ..vendored_sdks.models import ExtensionInstanceUpdate
from ..vendored_sdks.models import ScopeCluster
from ..vendored_sdks.models import Scope

from .PartnerExtensionModel import PartnerExtensionModel
from .ContainerInsights import _get_container_insights_settings

logger = get_logger(__name__)


class AzureDefender(PartnerExtensionModel):
    def Create(self, cmd, client, resource_group_name, cluster_name, name, cluster_type, extension_type,
               scope, auto_upgrade_minor_version, release_train, version, target_namespace,
               release_namespace, configuration_settings, configuration_protected_settings,
               configuration_settings_file, configuration_protected_settings_file):

        """ExtensionType 'microsoft.azuredefender.kubernetes' specific validations & defaults for Create
           Must create and return a valid 'ExtensionInstance' object.

        """
        # NOTE-1: Replace default scope creation with your customization!
        ext_scope = None
        # Hardcoding  name, release_namespace and scope since ci only supports one instance and cluster scope
        # and platform doesnt have support yet extension specific constraints like this
        name = extension_type.lower()
        release_namespace = "azuredefender"
        # Scope is always cluster
        scope_cluster = ScopeCluster(release_namespace=release_namespace)
        ext_scope = Scope(cluster=scope_cluster, namespace=None)

        is_ci_extension_type = False

        logger.warning('Ignoring name, release-namespace and scope parameters since %s '
                       'only supports cluster scope and single instance of this extension.', extension_type)
        logger.warning("Defaulting to extension name '%s' and release-namespace '%s'", name, release_namespace)

        _get_container_insights_settings(cmd, resource_group_name, cluster_name, configuration_settings,
                                         configuration_protected_settings, is_ci_extension_type)

        # NOTE-2: Return a valid ExtensionInstance object, Instance name and flag for Identity
        create_identity = True
        extension_instance = ExtensionInstance(
            extension_type=extension_type,
            auto_upgrade_minor_version=auto_upgrade_minor_version,
            release_train=release_train,
            version=version,
            scope=ext_scope,
            configuration_settings=configuration_settings,
            configuration_protected_settings=configuration_protected_settings
        )
        return extension_instance, name, create_identity

    def Update(self, extension, auto_upgrade_minor_version, release_train, version):
        """ExtensionType 'microsoft.azuredefender.kubernetes' specific validations & defaults for Update
           Must create and return a valid 'ExtensionInstanceUpdate' object.

        """
        return ExtensionInstanceUpdate(
            auto_upgrade_minor_version=auto_upgrade_minor_version,
            release_train=release_train,
            version=version
        )
