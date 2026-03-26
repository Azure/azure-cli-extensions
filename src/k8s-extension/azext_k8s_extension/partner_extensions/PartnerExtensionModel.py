# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from abc import ABC, abstractmethod
from ..vendored_sdks.models import Extension
from ..vendored_sdks.models import PatchExtension


class PartnerExtensionModel(ABC):
    @abstractmethod
    def Create(
        self,
        cmd,
        client,
        resource_group_name: str,
        cluster_name: str,
        name: str,
        cluster_type: str,
        cluster_rp: str,
        extension_type: str,
        scope: str,
        auto_upgrade_minor_version: bool,
        release_train: str,
        version: str,
        target_namespace: str,
        release_namespace: str,
        configuration_settings: dict,
        configuration_protected_settings: dict,
        configuration_settings_file: str,
        configuration_protected_settings_file: str,
        plan_name: str,
        plan_publisher: str,
        plan_product: str,
    ) -> Extension:
        pass

    @abstractmethod
    def Update(
        self,
        cmd,
        resource_group_name: str,
        cluster_name: str,
        auto_upgrade_minor_version: bool,
        release_train: str,
        version: str,
        configuration_settings: dict,
        configuration_protected_settings: dict,
        original_extension: Extension,
        yes: bool,
    ) -> PatchExtension:
        pass

    @abstractmethod
    def Delete(
        self,
        cmd,
        client,
        resource_group_name: str,
        cluster_name: str,
        name: str,
        cluster_type: str,
        cluster_rp: str,
        yes: bool,
    ):
        pass
