# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import ResourceNotFoundError
from azure.core.exceptions import HttpResponseError
from knack.log import get_logger

from ..utils import (
    fix_compliance_state,
    get_cluster_rp_api_version,
    get_data_from_key_or_file,
    to_base64,
)
from ..validators import (
    validate_cc_registration,
    validate_known_hosts,
    validate_url_with_params,
)
from .. import consts

from ..vendored_sdks.v2022_03_01.models import (
    HelmOperatorProperties,
    SourceControlConfiguration,
)

logger = get_logger(__name__)


def show_config(cmd, client, resource_group_name, cluster_type, cluster_name, name):
    # Validate that the subscription is registered to Microsoft.KubernetesConfiguration
    validate_cc_registration(cmd)

    # Determine ClusterRP
    cluster_rp, _ = get_cluster_rp_api_version(cluster_type)
    try:
        extension = client.get(
            resource_group_name, cluster_rp, cluster_type, cluster_name, name
        )
        return extension
    except HttpResponseError as ex:
        # Customize the error message for resources not found
        if ex.response.status_code == 404:
            # If Cluster not found
            if ex.message.__contains__("(ResourceNotFound)"):
                message = "{0} Verify that the cluster-type is correct and the resource exists.".format(
                    ex.message
                )
            # If Configuration not found
            elif ex.message.__contains__(
                "Operation returned an invalid status code 'Not Found'"
            ):
                message = (
                    "(SourceControlConfigurationNotFound) The Resource {0}/{1}/{2}/"
                    "Microsoft.KubernetesConfiguration/sourceControlConfigurations/{3}"
                    "could not be found!".format(
                        cluster_rp, cluster_type, cluster_name, name
                    )
                )
            else:
                message = ex.message
            raise ResourceNotFoundError(message) from ex
        raise ex


def list_configs(cmd, client, resource_group_name, cluster_type, cluster_name):
    # Validate that the subscription is registered to Microsoft.KubernetesConfiguration
    validate_cc_registration(cmd)

    cluster_rp, _ = get_cluster_rp_api_version(cluster_type)
    return client.list(resource_group_name, cluster_rp, cluster_type, cluster_name)


def delete_config(cmd, client, resource_group_name, cluster_type, cluster_name, name):
    # Validate that the subscription is registered to Microsoft.KubernetesConfiguration
    validate_cc_registration(cmd)

    cluster_rp, _ = get_cluster_rp_api_version(cluster_type)
    return client.begin_delete(
        resource_group_name, cluster_rp, cluster_type, cluster_name, name
    )


# pylint: disable=too-many-locals
def create_config(
    cmd,
    client,
    resource_group_name,
    cluster_name,
    name,
    repository_url,
    scope,
    cluster_type,
    operator_instance_name=None,
    operator_namespace="default",
    helm_operator_chart_version="1.4.0",
    operator_type="flux",
    operator_params="",
    ssh_private_key="",
    ssh_private_key_file="",
    https_user="",
    https_key="",
    ssh_known_hosts="",
    ssh_known_hosts_file="",
    enable_helm_operator=None,
    helm_operator_params="",
):

    """Create a new Kubernetes Source Control Configuration."""
    # Determine ClusterRP
    cluster_rp, _ = get_cluster_rp_api_version(cluster_type)

    # Determine operatorInstanceName
    if operator_instance_name is None:
        operator_instance_name = name

    # Create helmOperatorProperties object
    helm_operator_properties = None
    if enable_helm_operator:
        helm_operator_properties = HelmOperatorProperties()
        helm_operator_properties.chart_version = helm_operator_chart_version.strip()
        helm_operator_properties.chart_values = helm_operator_params.strip()

    validate_url_with_params(
        repository_url,
        ssh_private_key,
        ssh_private_key_file,
        ssh_known_hosts,
        ssh_known_hosts_file,
        https_user,
        https_key,
    )

    protected_settings = get_protected_settings(
        ssh_private_key, ssh_private_key_file, https_user, https_key
    )
    knownhost_data = get_data_from_key_or_file(ssh_known_hosts, ssh_known_hosts_file)
    if knownhost_data:
        validate_known_hosts(knownhost_data)

    # Validate that the subscription is registered to Microsoft.KubernetesConfiguration
    validate_cc_registration(cmd)

    # Create sourceControlConfiguration object
    source_control_configuration = SourceControlConfiguration(
        repository_url=repository_url,
        operator_namespace=operator_namespace,
        operator_instance_name=operator_instance_name,
        operator_type=operator_type,
        operator_params=operator_params,
        configuration_protected_settings=protected_settings,
        operator_scope=scope,
        ssh_known_hosts_contents=knownhost_data,
        enable_helm_operator=enable_helm_operator,
        helm_operator_properties=helm_operator_properties,
    )

    # Try to create the resource
    config = client.create_or_update(
        resource_group_name,
        cluster_rp,
        cluster_type,
        cluster_name,
        name,
        source_control_configuration,
    )

    return fix_compliance_state(config)


def get_protected_settings(
    ssh_private_key, ssh_private_key_file, https_user, https_key
):
    protected_settings = {}
    ssh_private_key_data = get_data_from_key_or_file(
        ssh_private_key, ssh_private_key_file
    )

    # Add gitops private key data to protected settings if exists
    # Dry-run all key types to determine if the private key is in a valid format
    if ssh_private_key_data:
        protected_settings[consts.SSH_PRIVATE_KEY_KEY] = ssh_private_key_data

    # Check if both httpsUser and httpsKey exist, then add to protected settings
    if https_user and https_key:
        protected_settings[consts.HTTPS_USER_KEY] = to_base64(https_user)
        protected_settings[consts.HTTPS_KEY_KEY] = to_base64(https_key)

    return protected_settings
