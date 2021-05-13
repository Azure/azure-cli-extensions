# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument

from azure.cli.core.azclierror import InvalidArgumentValueError, RequiredArgumentMissingError
from knack.log import get_logger

from ..vendored_sdks.models import ExtensionInstance
from ..vendored_sdks.models import ExtensionInstanceUpdate
from ..vendored_sdks.models import ScopeCluster
from ..vendored_sdks.models import Scope

from .PartnerExtensionModel import PartnerExtensionModel

logger = get_logger(__name__)


class OpenServiceMesh(PartnerExtensionModel):
    def Create(self, cmd, client, resource_group_name, cluster_name, name, cluster_type, extension_type,
               scope, auto_upgrade_minor_version, release_train, version, target_namespace,
               release_namespace, configuration_settings, configuration_protected_settings,
               configuration_settings_file, configuration_protected_settings_file):

        """ExtensionType 'microsoft.openservicemesh' specific validations & defaults for Create
           Must create and return a valid 'ExtensionInstance' object.

        """
        # NOTE-1: Replace default scope creation with your customization, if required
        # Scope must always be cluster
        ext_scope = None
        if scope == 'namespace':
            raise InvalidArgumentValueError("Invalid scope '{}'.  This extension can be installed "
                                            "only at 'cluster' scope.".format(scope))

        scope_cluster = ScopeCluster(release_namespace=release_namespace)
        ext_scope = Scope(cluster=scope_cluster, namespace=None)

        valid_release_trains = ['staging', 'pilot']
        # If release-train is not input, set it to 'stable'
        if release_train is None:
            raise RequiredArgumentMissingError(
                "A release-train must be provided.  Valid values are 'staging', 'pilot'."
            )

        if release_train.lower() in valid_release_trains:
            # version is a mandatory if release-train is staging or pilot
            if version is None:
                raise RequiredArgumentMissingError(
                    "A version must be provided for release-train {}.".format(release_train)
                )
            # If the release-train is 'staging' or 'pilot' then auto-upgrade-minor-version MUST be set to False
            if auto_upgrade_minor_version or auto_upgrade_minor_version is None:
                auto_upgrade_minor_version = False
                logger.warning("Setting auto-upgrade-minor-version to False since release-train is '%s'", release_train)
        else:
            raise InvalidArgumentValueError(
                "Invalid release-train '{}'.  Valid values are 'staging', 'pilot'.".format(release_train)
            )

        # NOTE-2: Return a valid ExtensionInstance object, Instance name and flag for Identity
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
        """ExtensionType 'microsoft.openservicemesh' specific validations & defaults for Update
           Must create and return a valid 'ExtensionInstanceUpdate' object.

        """
        #  auto-upgrade-minor-version MUST be set to False if release_train is staging or pilot
        if release_train.lower() in 'staging' 'pilot':
            if auto_upgrade_minor_version or auto_upgrade_minor_version is None:
                auto_upgrade_minor_version = False
                # Set version to None to always get the latest version - user cannot override
                version = None
                logger.warning("Setting auto-upgrade-minor-version to False since release-train is '%s'", release_train)

        return ExtensionInstanceUpdate(
            auto_upgrade_minor_version=auto_upgrade_minor_version,
            release_train=release_train,
            version=version
        )
