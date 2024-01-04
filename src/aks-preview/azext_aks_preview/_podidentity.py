# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import time
from types import SimpleNamespace

from knack.log import get_logger
from knack.util import CLIError

from azext_aks_preview._client_factory import get_auth_management_client
from azext_aks_preview._consts import (
    CONST_MANAGED_IDENTITY_OPERATOR_ROLE,
    CONST_MANAGED_IDENTITY_OPERATOR_ROLE_ID,
)
from azext_aks_preview._roleassignments import add_role_assignment

logger = get_logger(__name__)


def _is_pod_identity_addon_enabled(instance):
    if not instance:
        return False
    if not instance.pod_identity_profile:
        return False
    return bool(instance.pod_identity_profile.enabled)


def _ensure_pod_identity_addon_is_enabled(instance):
    if not _is_pod_identity_addon_enabled(instance):
        raise CLIError('The pod identity addon is not enabled for this managed cluster yet.\n'
                       'To enable, run "az aks update --enable-pod-identity')


def _ensure_pod_identity_kubenet_consent(network_profile, pod_identity_profile, customer_consent):
    if not network_profile or not network_profile.network_plugin:
        # invalid data
        return
    if network_profile.network_plugin.lower() != 'kubenet':
        # not kubenet, no need to check
        return

    if customer_consent is None:
        # no set this time, read from previous value
        customer_consent = bool(
            pod_identity_profile.allow_network_plugin_kubenet)

    if not customer_consent:
        raise CLIError(
            "--enable-pod-identity-with-kubenet is required for "
            "enabling pod identity addon when using Kubenet network plugin")
    pod_identity_profile.allow_network_plugin_kubenet = True


def _fill_defaults_for_pod_identity_exceptions(pod_identity_exceptions):
    if not pod_identity_exceptions:
        return

    for exc in pod_identity_exceptions:
        if exc.pod_labels is None:
            # in previous version, we accidentally allowed user to specify empty pod labels,
            # which will be converted to `None` in response. This behavior will break the extension
            # when using 2021-10-01 version. As a workaround, we always back fill the empty dict value
            # before sending to the server side.
            exc.pod_labels = {}


def _fill_defaults_for_pod_identity_profile(pod_identity_profile):
    if not pod_identity_profile:
        return

    _fill_defaults_for_pod_identity_exceptions(pod_identity_profile.user_assigned_identity_exceptions)


def _update_addon_pod_identity(
    instance,
    enable,
    pod_identities=None,
    pod_identity_exceptions=None,
    allow_kubenet_consent=None,
    models: SimpleNamespace = None,
):
    if not enable:
        ManagedClusterPodIdentityProfile = models.ManagedClusterPodIdentityProfile
        # when disable, remove previous saved value
        instance.pod_identity_profile = ManagedClusterPodIdentityProfile(
            enabled=False)
        return

    _fill_defaults_for_pod_identity_exceptions(pod_identity_exceptions)

    if not instance.pod_identity_profile:
        ManagedClusterPodIdentityProfile = models.ManagedClusterPodIdentityProfile
        # not set before
        instance.pod_identity_profile = ManagedClusterPodIdentityProfile(
            enabled=enable,
            user_assigned_identities=pod_identities,
            user_assigned_identity_exceptions=pod_identity_exceptions,
        )

    _ensure_pod_identity_kubenet_consent(
        instance.network_profile, instance.pod_identity_profile, allow_kubenet_consent)

    instance.pod_identity_profile.enabled = enable
    instance.pod_identity_profile.user_assigned_identities = pod_identities or []
    instance.pod_identity_profile.user_assigned_identity_exceptions = pod_identity_exceptions or []


def _ensure_managed_identity_operator_permission(cmd, instance, scope):
    cluster_identity_object_id = None
    if instance.identity.type.lower() == 'userassigned':
        for identity in instance.identity.user_assigned_identities.values():
            cluster_identity_object_id = identity.principal_id
            break
    elif instance.identity.type.lower() == 'systemassigned':
        cluster_identity_object_id = instance.identity.principal_id
    else:
        raise CLIError(f"unsupported identity type: {instance.identity.type}")
    if cluster_identity_object_id is None:
        raise CLIError('unable to resolve cluster identity')

    factory = get_auth_management_client(cmd.cli_ctx, scope)
    assignments_client = factory.role_assignments
    cluster_identity_object_id = cluster_identity_object_id.lower()
    scope = scope.lower()

    # list all assignments of the target identity (scope) that assigned to the cluster identity
    filter_query = f"atScope() and assignedTo('{cluster_identity_object_id}')"
    for i in assignments_client.list_for_scope(scope=scope, filter=filter_query):
        if not i.role_definition_id.lower().endswith(CONST_MANAGED_IDENTITY_OPERATOR_ROLE_ID):
            continue

        # sanity checks to make sure we see the correct assignments
        if i.principal_id.lower() != cluster_identity_object_id:
            # assignedTo() should return the assignment to cluster identity
            continue
        if not scope.startswith(i.scope.lower()):
            # atScope() should return the assignments in subscription / resource group / resource level
            continue

        # already assigned
        logger.debug('Managed Identity Opereator role has been assigned to %s', i.scope)
        return

    if not add_role_assignment(cmd, CONST_MANAGED_IDENTITY_OPERATOR_ROLE, cluster_identity_object_id,
                               is_service_principal=False, scope=scope):
        raise CLIError(
            'Could not grant Managed Identity Operator permission for cluster')

    # need more time to propogate this assignment...
    print()
    print('Wait 30 seconds for identity role assignment propagation.')
    time.sleep(30)
