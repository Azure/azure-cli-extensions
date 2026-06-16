# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_aks_preview._client_factory import cf_managed_clusters, cf_prepared_image_specifications, get_msi_client
from azext_aks_preview._roleassignments import add_role_assignment
from azure.cli.command_modules.acs._consts import CONST_MANAGED_IDENTITY_OPERATOR_ROLE
from azure.cli.core.azclierror import RequiredArgumentMissingError
from azure.mgmt.core.tools import parse_resource_id
from knack.log import get_logger
from knack.util import CLIError

logger = get_logger(__name__)


def pis_identity_resource_id(cmd, agentpool):
    if not agentpool.prepared_image_specification_profile:
        return ""

    pis_id = agentpool.prepared_image_specification_profile.prepared_image_specification_id
    if not pis_id:
        return ""

    parsed = parse_resource_id(pis_id)
    pis_resource_group = parsed.get("resource_group")
    pis_name = parsed.get("name")
    pis_subscription = parsed.get("subscription")

    pis = cf_prepared_image_specifications(cmd.cli_ctx, subscription_id=pis_subscription) \
        .get(pis_resource_group, pis_name)

    if not pis.properties.identity_profile:
        return None

    return pis.properties.identity_profile.resource_id


def ensure_pis_managed_identity_permission_for_cluster(cmd, cluster):
    for agentpool in cluster.agent_pool_profiles:
        pis_identity_id = pis_identity_resource_id(cmd, agentpool)
        if not pis_identity_id:
            continue

        _ensure_managed_identity_operator_permission(cmd, cluster, pis_identity_id)


def ensure_pis_managed_identity_permission_for_agentpool(cmd, agentpool, resource_group_name, cluster_name):
    pis_identity_id = pis_identity_resource_id(cmd, agentpool)
    if not pis_identity_id:
        return

    cluster = cf_managed_clusters(cmd.cli_ctx).get(resource_group_name, cluster_name)

    _ensure_managed_identity_operator_permission(cmd, cluster, pis_identity_id)


def _ensure_managed_identity_operator_permission(cmd, cluster, scope):
    if not cluster.identity.user_assigned_identities:
        raise RequiredArgumentMissingError(
            "The prepared image specification references a managed identity.  As a result, this cluster must have a "
            "user-assigned managed identity.  Specify `--assign-identity`."
        )

    object_id = get_msi_object_id(cmd, next(iter(cluster.identity.user_assigned_identities.keys())))

    if not add_role_assignment(cmd, CONST_MANAGED_IDENTITY_OPERATOR_ROLE, object_id,
                               is_service_principal=False, scope=scope):
        raise CLIError("Could not grant Managed Identity Operator permission for cluster")


def get_msi_object_id(cmd, msi_resource_id):
    parsed = parse_resource_id(msi_resource_id)
    subscription_id = parsed['subscription']
    resource_group_name = parsed['resource_group']
    msi_name = parsed['resource_name']

    msi_client = get_msi_client(cmd.cli_ctx, subscription_id=subscription_id)
    msi = msi_client.user_assigned_identities.get(resource_name=msi_name, resource_group_name=resource_group_name)

    return msi.principal_id
