# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument

from knack.log import get_logger

from msrestazure.azure_exceptions import CloudError
from azext_k8s_extension.vendored_sdks.models import ExtensionInstance
from azext_k8s_extension.vendored_sdks.models import ExtensionInstanceUpdate
from azext_k8s_extension.vendored_sdks.models import ScopeCluster
from azext_k8s_extension.vendored_sdks.models import Scope
from azure.cli.core.commands.client_factory import get_subscription_id

from pyhelm.chartbuilder import ChartBuilder
from packaging import version
import yaml

from azext_k8s_extension.partner_extensions.PartnerExtensionModel import PartnerExtensionModel
from azext_k8s_extension.partner_extensions.ContainerInsights import _get_container_insights_settings

from .._client_factory import cf_resources

logger = get_logger(__name__)


class Openservicemesh(PartnerExtensionModel):
    def Create(self, cmd, client, resource_group_name, cluster_name, name, cluster_type, extension_type,
               scope, auto_upgrade_minor_version, release_train, version, target_namespace,
               release_namespace, configuration_settings, configuration_protected_settings,
               configuration_settings_file, configuration_protected_settings_file):

        """ExtensionType 'microsoft.openservicemesh' specific validations & defaults for Create
           Must create and return a valid 'ExtensionInstance' object.

        """
        ext_scope = None
        if scope is not None:
            if scope.lower() == 'cluster':
                scope_cluster = ScopeCluster(release_namespace=release_namespace)
                ext_scope = Scope(cluster=scope_cluster, namespace=None)
            elif scope.lower() == 'namespace':
                scope_namespace = ScopeNamespace(target_namespace=target_namespace)
                ext_scope = Scope(namespace=scope_namespace, cluster=None)

        create_identity = False

        _validate_tested_distro(cmd, resource_group_name, cluster_name, version)

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


def _validate_tested_distro(cmd, cluster_resource_group_name, cluster_name, extension_version):

    if version.parse(str(extension_version)) <= version.parse("0.8.3"):
        logger.warning(f'\"testedDistros\" field unavailable for version {extension_version} of osm-arc, '
            'cannot determine if this kubernetes distribution has been tested for osm-arc')
        return

    subscription_id = get_subscription_id(cmd.cli_ctx)
    resources = cf_resources(cmd.cli_ctx, subscription_id)

    cluster_resource_id = '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Kubernetes' \
        '/connectedClusters/{2}'.format(subscription_id, cluster_resource_group_name, cluster_name)
    try:
        resource = resources.get_by_id(cluster_resource_id, '2020-01-01-preview')
        cluster_distro = resource.distribution.lower()
    except CloudError as ex:
        raise ex

    if cluster_distro == "general":
        logger.warning('kubernetes distribution is \"general\", cannot determine if this kubernetes '
            'distribution has been tested for osm-arc')
        return

    tested_distros = _get_tested_distros(extension_version)

    if tested_distros is None:
        logger.warning(f'\"testedDistros\" field unavailable for version {extension_version} of osm-arc, '
            'cannot determine if this kubernetes distribution has been tested for osm-arc')
    elif cluster_distro in tested_distros.split():
        logger.info(f'{cluster_distro} is a tested kubernetes distribution for osm-arc')
    else:
        logger.warning(f'{cluster_distro} is not a tested kubernetes distribution for osm-arc')


def _get_tested_distros(version):

    chart_arc = ChartBuilder({
        "name": "osm-arc",
        "version": str(version),
        "source": {
            "type": "repo",
            "location": "https://azure.github.io/osm-azure"
        }
    })
    values = chart_arc.get_values()
    values_yaml = yaml.load(values.raw)

    try:
        return values_yaml['OpenServiceMesh']['testedDistros']
    except KeyError:
        return None
