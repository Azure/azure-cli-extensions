# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument

import datetime
import json
import re

from ..utils import get_cluster_rp_api_version, is_skip_prerequisites_specified

from knack.log import get_logger

from azure.cli.core.commands.client_factory import get_subscription_id

from ..vendored_sdks.models import Extension
from ..vendored_sdks.models import ScopeCluster
from ..vendored_sdks.models import Scope

from .DefaultExtension import DefaultExtension
from .azuremonitormetrics.azuremonitorprofile import ensure_azure_monitor_profile_prerequisites, unlink_azure_monitor_profile_artifacts

from .._client_factory import (
    cf_resources, cf_resource_groups, cf_log_analytics)

logger = get_logger(__name__)


class AzureMonitorMetrics(DefaultExtension):
    def Create(self, cmd, client, resource_group_name, cluster_name, name, cluster_type, cluster_rp,
               extension_type, scope, auto_upgrade_minor_version, release_train, version, target_namespace,
               release_namespace, configuration_settings, configuration_protected_settings,
               configuration_settings_file, configuration_protected_settings_file,
               plan_name, plan_publisher, plan_product):
        """ExtensionType 'microsoft.azuremonitor.containers.metrics' specific validations & defaults for Create
           Must create and return a valid 'Extension' object.

        """
        name = 'azuremonitor-metrics'
        release_namespace = 'kube-system'
        # Scope is always cluster
        scope_cluster = ScopeCluster(release_namespace=release_namespace)
        ext_scope = Scope(cluster=scope_cluster, namespace=None)

        # If release-train is not input, set it to 'stable'
        if release_train is None:
            release_train = 'stable'

        if not is_skip_prerequisites_specified(configuration_settings):
            cluster_subscription = get_subscription_id(cmd.cli_ctx)
            ensure_azure_monitor_profile_prerequisites(
                cmd,
                cluster_rp,
                cluster_subscription,
                resource_group_name,
                cluster_name,
                configuration_settings,
                cluster_type
            )
        else:
            logger.info("Provisioning of prerequisites is skipped")

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

    def Delete(self, cmd, client, resource_group_name, cluster_name, name, cluster_type, cluster_rp, yes):
        cluster_rp, _ = get_cluster_rp_api_version(cluster_type=cluster_type, cluster_rp=cluster_rp)
        try:
            extension = client.get(resource_group_name, cluster_rp, cluster_type, cluster_name, name)
        except Exception:
            pass  # its OK to ignore the exception since MSI auth in preview

        if (extension is not None) and (extension.configuration_settings is not None):
            if is_skip_prerequisites_specified(extension.configuration_settings):
                logger.info("Deprovisioning of prerequisites is skipped")
                return

        cluster_subscription = get_subscription_id(cmd.cli_ctx)
        unlink_azure_monitor_profile_artifacts(cmd, cluster_subscription, resource_group_name, cluster_name)
