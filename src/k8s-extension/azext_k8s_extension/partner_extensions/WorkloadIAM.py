# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import subprocess

from knack.log import get_logger
from knack.util import CLIError

from azure.cli.core.azclierror import InvalidArgumentValueError

from ..vendored_sdks.models import (Extension, Scope, ScopeCluster)

from .DefaultExtension import DefaultExtension

logger = get_logger(__name__)

# The user settings are case-insensitive
CONFIG_SETTINGS_USER_TRUST_DOMAIN = 'trustdomain'
CONFIG_SETTINGS_USER_LOCAL_AUTHORITY = 'localauthority'
CONFIG_SETTINGS_USER_TENANT_ID = 'tenantid'
CONFIG_SETTINGS_USER_JOIN_TOKEN = 'jointoken'

CONFIG_SETTINGS_HELM_TRUST_DOMAIN = 'global.workload-iam.trustDomain'
CONFIG_SETTINGS_HELM_TENANT_ID = 'global.workload-iam.tenantID'
CONFIG_SETTINGS_HELM_JOIN_TOKEN = 'workload-iam-local-authority.localAuthorityArgs.joinToken'


class WorkloadIAM(DefaultExtension):

    def Create(self, cmd, client, resource_group_name, cluster_name, name, cluster_type, cluster_rp,
               extension_type, scope, auto_upgrade_minor_version, release_train, version, target_namespace,
               release_namespace, configuration_settings, configuration_protected_settings,
               configuration_settings_file, configuration_protected_settings_file,
               plan_name, plan_publisher, plan_product):
        """
        Create method for ExtensionType 'microsoft.workloadiam'.
        """

        # Ensure that the values provided by the user for generic values of Arc extensions are
        # valid, set sensible default values if not.
        if release_train is None:
            # TODO - Set this to 'stable' when the extension is ready
            release_train = 'preview'

        scope = scope.lower()
        if scope is None:
            scope = 'cluster'
        elif scope != 'cluster':
            raise InvalidArgumentValueError(
                f"Invalid scope '{scope}'. This extension can only be installed at 'cluster' scope.")

        # Scope is always cluster
        scope_cluster = ScopeCluster(release_namespace=release_namespace)
        ext_scope = Scope(cluster=scope_cluster, namespace=None)

        # Create new dictionary where the keys of the user settings are all lowercase (but leave the
        # others alone in case they are specific settings that have to be passed to the Helm chart).
        validated_settings = dict()
        all_user_settings = [CONFIG_SETTINGS_USER_TRUST_DOMAIN, CONFIG_SETTINGS_USER_TENANT_ID,
                             CONFIG_SETTINGS_USER_LOCAL_AUTHORITY, CONFIG_SETTINGS_USER_JOIN_TOKEN]
        for key, value in configuration_settings.items():
            if key.lower() in all_user_settings:
                validated_settings[key.lower()] = value
            else:
                validated_settings[key] = value
        config_settings = validated_settings

        # Get user configuration values and remove them from the dictionary so that they aren't
        # passed to the Helm chart
        trust_domain = config_settings.pop(CONFIG_SETTINGS_USER_TRUST_DOMAIN, None)
        tenant_id = config_settings.pop(CONFIG_SETTINGS_USER_TENANT_ID, None)
        local_authority = config_settings.pop(CONFIG_SETTINGS_USER_LOCAL_AUTHORITY, None)
        join_token = config_settings.pop(CONFIG_SETTINGS_USER_JOIN_TOKEN, None)

        # A trust domain name is always required
        if trust_domain is None:
            raise InvalidArgumentValueError(
                "Invalid configuration settings. Please provide a trust domain name.")

        if tenant_id is None:
            raise InvalidArgumentValueError(
                "Invalid configuration settings. Please provide a tenant ID.")

        # If the user hasn't provided a join token, create one
        if join_token is None:
            if local_authority is None:
                raise InvalidArgumentValueError(
                    "Invalid configuration settings. Either a join token or a local authority name "
                    "must be provided.")
            join_token = self.get_join_token(trust_domain, local_authority)
        else:
            logger.info("Join token is provided")

        # Save configuration setting values to overwrite values in the Helm chart
        configuration_settings[CONFIG_SETTINGS_HELM_TRUST_DOMAIN] = trust_domain
        configuration_settings[CONFIG_SETTINGS_HELM_TENANT_ID] = tenant_id
        configuration_settings[CONFIG_SETTINGS_HELM_JOIN_TOKEN] = join_token

        logger.debug("Configuration settings value for Helm: %s" % str(configuration_settings))

        create_identity = True
        extension = Extension(
            extension_type=extension_type,
            auto_upgrade_minor_version=auto_upgrade_minor_version,
            release_train=release_train,
            version=version,
            scope=ext_scope,
            configuration_settings=configuration_settings,
            configuration_protected_settings=configuration_protected_settings
        )
        return extension, name, create_identity

    def get_join_token(self, trust_domain, local_authority):
        """
        Invoke the az command to obtain a join token.
        """

        logger.info("Getting a join token from the control plane")

        # Invoke az workload-iam command to obtain the join token
        cmd = [
            "az", "workload-iam", "local-authority", "attestation-method", "create",
            "--td", trust_domain,
            "--la", local_authority,
            "--type", "joinTokenAttestationMethod",
            "--query", "singleUseToken",
            "--dn", "myJoinToken",
        ]
        cmd_str = " ".join(cmd)

        try:
            # Note: We can't use get_default_cli() here because its invoke() method
            # always prints the console output, which we want to avoid.
            result = subprocess.run(cmd, capture_output=True, shell=True)
        except Exception as e:
            logger.error(f"Error while generating a join token: {cmd_str}")
            raise e

        if result.returncode != 0:
            raise CLIError(f"Failed to generate a join token (exit code {result.returncode}): {cmd_str}")

        try:
            # Strip double quotes from the output
            command_output = result.stdout.decode("utf-8")
            token = command_output.strip("\r\n").strip("\"")
        except Exception as e:
            logger.error(f"Failed to parse output of join token command: {cmd_str}")
            raise e

        return token
