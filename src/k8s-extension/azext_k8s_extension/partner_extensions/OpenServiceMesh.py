# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
# pylint: disable=no-member

import json
from knack.log import get_logger

from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.commands.client_factory import get_subscription_id

from packaging import version
import yaml
import requests

from .DefaultExtension import DefaultExtension

from ..vendored_sdks.models import (
    Extension,
    ScopeCluster,
    Scope
)

from .._client_factory import cf_resources

logger = get_logger(__name__)


class OpenServiceMesh(DefaultExtension):

    def Create(self, cmd, client, resource_group_name, cluster_name, name, cluster_type, cluster_rp,
               extension_type, scope, auto_upgrade_minor_version, release_train, version, target_namespace,
               release_namespace, configuration_settings, configuration_protected_settings,
               configuration_settings_file, configuration_protected_settings_file, plan_name, plan_publisher, plan_product):
        """ExtensionType 'microsoft.openservicemesh' specific validations & defaults for Create
           Must create and return a valid 'Extension' object.
        """
        # NOTE-1: Replace default scope creation with your customization, if required
        # Scope must always be cluster
        ext_scope = None
        if scope == 'namespace':
            raise InvalidArgumentValueError("Invalid scope '{}'.  This extension can be installed "
                                            "only at 'cluster' scope.".format(scope))

        scope_cluster = ScopeCluster(release_namespace=release_namespace)
        ext_scope = Scope(cluster=scope_cluster, namespace=None)

        # NOTE-2: Return a valid Extension object, Instance name and flag for Identity
        create_identity = True

        if cluster_type == "connectedClusters":
            _validate_tested_distro(cmd, resource_group_name, cluster_name, version, release_train)

        extension = Extension(
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
        return extension, name, create_identity


def _validate_tested_distro(cmd, cluster_resource_group_name, cluster_name, extension_version, extension_release_train):

    field_unavailable_error = '\"testedDistros\" field unavailable for version {0} of microsoft.openservicemesh, ' \
        'cannot determine if this Kubernetes distribution has been properly tested'.format(extension_version)

    logger.debug('Input version: %s', extension_version)

    subscription_id = get_subscription_id(cmd.cli_ctx)
    resources = cf_resources(cmd.cli_ctx, subscription_id)

    cluster_resource_id = '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Kubernetes' \
        '/connectedClusters/{2}'.format(subscription_id, cluster_resource_group_name, cluster_name)

    resource = resources.get_by_id(cluster_resource_id, '2021-10-01')
    cluster_location = resource.location
    cluster_distro = resource.properties['distribution'].lower()

    if extension_version is None and extension_release_train != "staging":
        if str(cluster_location) == "eastus2euap":
            ring = "canary"
        else:
            ring = "batch1"

        if extension_release_train is None:
            extension_release_train = "stable"

        req_url = 'https://mcr.microsoft.com/v2/oss/openservicemesh/{0}/{1}/osm-arc/tags/list'\
            .format(ring, extension_release_train)
        req = requests.get(url=req_url)
        req_json = json.loads(req.text)
        tags = req_json['tags']

        extension_version = tags[len(tags) - 1]

    ext_str = str(extension_version)

    # Don't parse version for test and CI tags
    if "pr" in ext_str or "release" in ext_str or "beta" in ext_str:
        return

    if version.parse(ext_str) <= version.parse("0.8.3"):
        logger.warning(field_unavailable_error)
        return

    if cluster_distro == "general":
        logger.warning('Unable to determine if distro has been tested for microsoft.openservicemesh, '
                       'kubernetes distro: \"general\"')
        return

    tested_distros = _get_tested_distros(extension_version)

    if tested_distros is None:
        logger.warning(field_unavailable_error)
    elif cluster_distro not in tested_distros.split():
        logger.warning('Untested kubernetes distro for microsoft.openservicemesh, Kubernetes distro is %s',
                       cluster_distro)


def _get_tested_distros(chart_version):

    chart_url = 'https://raw.githubusercontent.com/Azure/osm-azure/' \
        'v{0}/charts/osm-arc/values.yaml'.format(chart_version)
    chart_request = requests.get(url=chart_url)

    if chart_request.status_code == 404:
        raise InvalidArgumentValueError(
            "Invalid version '{}' for microsoft.openservicemesh".format(chart_version)
        )

    values_yaml = yaml.load(chart_request.text, Loader=yaml.FullLoader)

    try:
        return values_yaml['OpenServiceMesh']['testedDistros']
    except KeyError:
        return None
