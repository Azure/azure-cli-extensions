# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from abc import ABC, abstractmethod
from azext_k8s_extension.vendored_sdks.models import ExtensionInstanceForCreate
from azext_k8s_extension.vendored_sdks.models import ExtensionInstanceUpdate


class PartnerExtensionModel(ABC):
    @abstractmethod
    def Create(self, cmd, client, resource_group_name: str, cluster_name: str, name: str, cluster_type: str,
               extension_type: str, scope: str, auto_upgrade_minor_version: bool, release_train: str, version: str,
               target_namespace: str, release_namespace: str, configuration_settings: dict,
               configuration_protected_settings: dict, configuration_settings_file: str,
               configuration_protected_settings_file: str) -> ExtensionInstanceForCreate:
        pass

    @abstractmethod
    def Update(self, extension: ExtensionInstanceForCreate, auto_upgrade_minor_version: bool,
               release_train: str, version: str) -> ExtensionInstanceUpdate:
        pass
