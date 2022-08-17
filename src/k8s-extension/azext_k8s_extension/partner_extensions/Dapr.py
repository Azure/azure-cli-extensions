# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument
# pylint: disable=line-too-long
# pylint: disable=too-many-locals

from .DefaultExtension import DefaultExtension

from ..vendored_sdks.models import (
    Extension,
)


class Dapr(DefaultExtension):
    def __init__(self):
        # constants for configuration settings.
        self.CLUSTER_TYPE = 'global.clusterType'

    def Create(self, cmd, client, resource_group_name, cluster_name, name, cluster_type, cluster_rp,
               extension_type, scope, auto_upgrade_minor_version, release_train, version, target_namespace,
               release_namespace, configuration_settings, configuration_protected_settings,
               configuration_settings_file, configuration_protected_settings_file):

        """ExtensionType 'Microsoft.Dapr' specific validations & defaults for Create
           Must create and return a valid 'ExtensionInstance' object.
        """

        if cluster_type.lower() == '' or cluster_type.lower() == 'managedclusters':
            configuration_settings[self.CLUSTER_TYPE] = 'managedclusters'

        create_identity = False
        extension_instance = Extension(
            extension_type=extension_type,
            auto_upgrade_minor_version=auto_upgrade_minor_version,
            release_train=release_train,
            version=version,
            scope=scope,
            configuration_settings=configuration_settings,
            configuration_protected_settings=configuration_protected_settings,
            identity=None,
            location=""
        )
        return extension_instance, name, create_identity
