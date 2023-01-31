# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument
# pylint: disable=too-many-locals
# pylint: disable=too-many-instance-attributes

from typing import Tuple

from azure.cli.core.azclierror import InvalidArgumentValueError
from knack.log import get_logger
from knack.prompting import prompt, prompt_y_n

from ..vendored_sdks.models import Extension, Scope, ScopeCluster
from .DefaultExtension import DefaultExtension

logger = get_logger(__name__)


class Dapr(DefaultExtension):
    def __init__(self):
        self.TSG_LINK = "https://docs.microsoft.com/en-us/azure/aks/dapr"
        self.DEFAULT_RELEASE_NAME = 'dapr'
        self.DEFAULT_RELEASE_NAMESPACE = 'dapr-system'
        self.DEFAULT_RELEASE_TRAIN = 'stable'
        self.DEFAULT_CLUSTER_TYPE = 'managedclusters'
        self.DEFAULT_HA = 'true'

        # constants for configuration settings.
        self.CLUSTER_TYPE_KEY = 'global.clusterType'
        self.HA_KEY_ENABLED_KEY = 'global.ha.enabled'
        self.SKIP_EXISTING_DAPR_CHECK_KEY = 'skipExistingDaprCheck'
        self.EXISTING_DAPR_RELEASE_NAME_KEY = 'existingDaprReleaseName'
        self.EXISTING_DAPR_RELEASE_NAMESPACE_KEY = 'existingDaprReleaseNamespace'

        # constants for message prompts.
        self.MSG_IS_DAPR_INSTALLED = "Is Dapr already installed in the cluster?"
        self.MSG_ENTER_RELEASE_NAME = "Enter the Helm release name for Dapr, "\
            f"or press Enter to use the default name [{self.DEFAULT_RELEASE_NAME}]: "
        self.MSG_ENTER_RELEASE_NAMESPACE = "Enter the namespace where Dapr is installed, "\
            f"or press Enter to use the default namespace [{self.DEFAULT_RELEASE_NAMESPACE}]: "
        self.MSG_WARN_EXISTING_INSTALLATION = "The extension will use your existing Dapr installation. "\
            f"Note, if you have updated the default values for global.ha.* or dapr_placement.* in your existing "\
            "Dapr installation, you must provide them via --configuration-settings. Failing to do so will result in"\
            "an error, since Helm upgrade will try to modify the StatefulSet."\
            f"Please refer to {self.TSG_LINK} for more information."

        self.RELEASE_INFO_HELP_STRING = "The Helm release name and namespace can be found by running 'helm list -A'."

        # constants for error messages.
        self.ERR_MSG_INVALID_SCOPE_TPL = "Invalid scope '{}'. This extension can be installed only at 'cluster' scope."\
            f" Check {self.TSG_LINK} for more information."

    def _get_release_info(self, release_name: str, release_namespace: str, configuration_settings: dict)\
            -> Tuple[str, str, bool]:
        '''
        Check if Dapr is already installed in the cluster and get the release name and namespace.
        If user has provided the release name and namespace in configuration settings, use those.
        Otherwise, prompt the user for the release name and namespace.
        If Dapr is not installed, return the default release name and namespace.
        '''
        name, namespace, dapr_exists = release_name, release_namespace, False

        # Set the default release name and namespace if not provided.
        name = name or self.DEFAULT_RELEASE_NAME
        namespace = namespace or self.DEFAULT_RELEASE_NAMESPACE

        if configuration_settings.get(self.SKIP_EXISTING_DAPR_CHECK_KEY, 'false') == 'true':
            logger.info("%s is set to true, skipping existing Dapr check.", self.SKIP_EXISTING_DAPR_CHECK_KEY)
            return name, namespace, False

        cfg_name = configuration_settings.get(self.EXISTING_DAPR_RELEASE_NAME_KEY, None)
        cfg_namespace = configuration_settings.get(self.EXISTING_DAPR_RELEASE_NAMESPACE_KEY, None)

        # If the user has specified the release name and namespace in configuration settings, then use it.
        if cfg_name and cfg_namespace:
            logger.info("Using the release name and namespace specified in the configuration settings.")
            return cfg_name, cfg_namespace, True

        # If either release name or namespace is missing, ignore the configuration settings and prompt the user.
        if cfg_name or cfg_namespace:
            logger.warning("Both '%s' and '%s' must be specified via --configuration-settings. Only one of them is "
                           "specified, ignoring.", self.EXISTING_DAPR_RELEASE_NAME_KEY,
                           self.EXISTING_DAPR_RELEASE_NAMESPACE_KEY)

        # Check explictly if Dapr is already installed in the cluster.
        # If so, reuse the release name and namespace to avoid conflicts.
        if prompt_y_n(self.MSG_IS_DAPR_INSTALLED, default='n'):
            dapr_exists = True

            name = prompt(self.MSG_ENTER_RELEASE_NAME, self.RELEASE_INFO_HELP_STRING) or self.DEFAULT_RELEASE_NAME
            if release_name and name != release_name:
                logger.warning("The release name has been changed from '%s' to '%s'.", release_name, name)

            namespace = prompt(self.MSG_ENTER_RELEASE_NAMESPACE, self.RELEASE_INFO_HELP_STRING)\
                or self.DEFAULT_RELEASE_NAMESPACE
            if release_namespace and namespace != release_namespace:
                logger.warning("The release namespace has been changed from '%s' to '%s'.",
                               release_namespace, namespace)

        return name, namespace, dapr_exists

    def Create(self, cmd, client, resource_group_name: str, cluster_name: str, name: str, cluster_type: str,
               cluster_rp: str, extension_type: str, scope: str, auto_upgrade_minor_version: bool,
               release_train: str, version: str, target_namespace: str, release_namespace: str,
               configuration_settings: dict, configuration_protected_settings: dict,
               configuration_settings_file: str, configuration_protected_settings_file: str):
        """ExtensionType 'Microsoft.Dapr' specific validations & defaults for Create
           Must create and return a valid 'ExtensionInstance' object.
        """

        # Dapr extension is only supported at the cluster scope.
        if scope == 'namespace':
            raise InvalidArgumentValueError(self.ERR_MSG_INVALID_SCOPE_TPL.format(scope))

        release_name, release_namespace, dapr_exists = \
            self._get_release_info(name, release_namespace, configuration_settings)

        # Inform the user that the extension will be installed on an existing Dapr installation.
        # Disable HA mode if Dapr is already installed in the cluster.
        if dapr_exists:
            logger.warning(self.MSG_WARN_EXISTING_INSTALLATION)
            if self.HA_KEY_ENABLED_KEY not in configuration_settings:
                configuration_settings[self.HA_KEY_ENABLED_KEY] = 'false'

        scope_cluster = ScopeCluster(release_namespace=release_namespace or self.DEFAULT_RELEASE_NAMESPACE)
        extension_scope = Scope(cluster=scope_cluster, namespace=None)

        if cluster_type.lower() == '' or cluster_type.lower() == self.DEFAULT_CLUSTER_TYPE:
            configuration_settings[self.CLUSTER_TYPE_KEY] = self.DEFAULT_CLUSTER_TYPE

        create_identity = False
        extension_instance = Extension(
            extension_type=extension_type,
            auto_upgrade_minor_version=auto_upgrade_minor_version,
            release_train=release_train or self.DEFAULT_RELEASE_TRAIN,
            version=version,
            scope=extension_scope,
            configuration_settings=configuration_settings,
            configuration_protected_settings=configuration_protected_settings,
            identity=None,
            location=""
        )
        return extension_instance, release_name, create_identity
