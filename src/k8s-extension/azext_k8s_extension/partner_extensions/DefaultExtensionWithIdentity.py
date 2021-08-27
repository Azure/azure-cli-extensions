# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument

from .DefaultExtension import DefaultExtension


class DefaultExtensionWithIdentity(DefaultExtension):
    def Create(self, cmd, client, resource_group_name, cluster_name, name, cluster_type, extension_type,
               scope, auto_upgrade_minor_version, release_train, version, target_namespace,
               release_namespace, configuration_settings, configuration_protected_settings,
               configuration_settings_file, configuration_protected_settings_file):

        """Default validations & defaults for Create
           Must create and return a valid 'ExtensionInstance' object.

        """

        extension_instance, extension_name, _ = super(). \
            Create(cmd, client, resource_group_name, cluster_name, name, cluster_type, extension_type,
                   scope, auto_upgrade_minor_version, release_train, version, target_namespace,
                   release_namespace, configuration_settings, configuration_protected_settings,
                   configuration_settings_file, configuration_protected_settings_file)
        return extension_instance, extension_name, True
