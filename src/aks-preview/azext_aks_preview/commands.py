# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType

from azext_aks_preview._client_factory import (
    cf_agent_pools,
    cf_maintenance_configurations,
    cf_managed_clusters,
    cf_mc_snapshots,
    cf_nodepool_snapshots,
    cf_trustedaccess_role,
    cf_trustedaccess_role_binding,
    cf_machines,
)
from azext_aks_preview._format import (
    aks_addon_list_available_table_format,
    aks_addon_list_table_format,
    aks_addon_show_table_format,
    aks_agentpool_list_table_format,
    aks_agentpool_show_table_format,
    aks_machine_list_table_format,
    aks_machine_show_table_format,
    aks_list_nodepool_snapshot_table_format,
    aks_list_snapshot_table_format,
    aks_list_table_format,
    aks_pod_identities_table_format,
    aks_pod_identity_exceptions_table_format,
    aks_show_nodepool_snapshot_table_format,
    aks_show_snapshot_table_format,
    aks_show_table_format,
    aks_upgrades_table_format,
    aks_versions_table_format,
    aks_mesh_revisions_table_format,
    aks_mesh_upgrades_table_format,
)
from knack.log import get_logger

logger = get_logger(__name__)


def transform_mc_objects_with_custom_cas(result):
    # convert custom_ca_trust_certificates in bytearray format encoded in utf-8 to string
    if not result:
        return result
    from msrest.paging import Paged

    def _patch_custom_cas_in_security_profile(security_profile):
        # modify custom_ca_trust_certificates in-place
        # security_profile shouldn't be None
        custom_cas = getattr(security_profile, "custom_ca_trust_certificates", None)
        if custom_cas:
            decoded_custom_cas = []
            for custom_ca in custom_cas:
                try:
                    decoded_custom_ca = custom_ca.decode("utf-8")
                except Exception:  # pylint: disable=broad-except
                    logger.warning("failed to decode customCaTrustCertificates")
                    decoded_custom_ca = None
                decoded_custom_cas.append(decoded_custom_ca)
            security_profile.custom_ca_trust_certificates = decoded_custom_cas

    singular = False
    if isinstance(result, Paged):
        result = list(result)

    if not isinstance(result, list):
        singular = True
        result = [result]

    for r in result:
        if getattr(r, "security_profile", None):
            # security_profile shouldn't be None
            _patch_custom_cas_in_security_profile(r.security_profile)

    return result[0] if singular else result


# pylint: disable=too-many-statements
def load_command_table(self, _):
    managed_clusters_sdk = CliCommandType(
        operations_tmpl="azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks."
        "operations._managed_clusters_operations#ManagedClustersOperations.{}",
        operation_group="managed_clusters",
        client_factory=cf_managed_clusters,
    )

    agent_pools_sdk = CliCommandType(
        operations_tmpl="azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks."
        "operations._agent_pools_operations#AgentPoolsOperations.{}",
        client_factory=cf_managed_clusters,
    )

    machines_sdk = CliCommandType(
        operations_tmpl="azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks."
        "operations._machine_operations#MachinesOperations.{}",
        client_factory=cf_managed_clusters,
    )

    maintenance_configuration_sdk = CliCommandType(
        operations_tmpl="azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks."
        "operations._maintenance_configurations_operations#MaintenanceConfigurationsOperations.{}",
        client_factory=cf_maintenance_configurations,
    )

    nodepool_snapshot_sdk = CliCommandType(
        operations_tmpl="azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks."
        "operations._snapshots_operations#SnapshotsOperations.{}",
        client_factory=cf_nodepool_snapshots,
    )

    mc_snapshot_sdk = CliCommandType(
        operations_tmpl="azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks."
        "operations._managed_clusters_snapshots_operations#ManagedClusterSnapshotsOperations.{}",
        client_factory=cf_mc_snapshots,
    )

    trustedaccess_role_sdk = CliCommandType(
        operations_tmpl="azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks."
        "operations._trusted_access_roles_operations#TrustedAccessRolesOperations.{}",
        client_factory=cf_trustedaccess_role,
    )

    trustedaccess_role_binding_sdk = CliCommandType(
        operations_tmpl="azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks."
        "operations._trusted_access_role_bindings_operations#TrustedAccessRoleBindingsOperations.{}",
        client_factory=cf_trustedaccess_role_binding,
    )

    # AKS managed cluster commands
    with self.command_group(
        "aks",
        managed_clusters_sdk,
        client_factory=cf_managed_clusters,
        transform=transform_mc_objects_with_custom_cas,
    ) as g:
        g.custom_command("browse", "aks_browse")
        g.custom_command("create", "aks_create", supports_no_wait=True)
        g.custom_command("update", "aks_update", supports_no_wait=True)
        g.command(
            "get-upgrades",
            "get_upgrade_profile",
            table_transformer=aks_upgrades_table_format,
        )
        g.custom_command("upgrade", "aks_upgrade", supports_no_wait=True)
        g.custom_command("scale", "aks_scale", supports_no_wait=True)
        g.command("delete", "begin_delete", supports_no_wait=True, confirmation=True)
        g.custom_show_command(
            "show", "aks_show", table_transformer=aks_show_table_format
        )
        g.custom_command("list", "aks_list", table_transformer=aks_list_table_format)
        g.custom_command("enable-addons", "aks_enable_addons", supports_no_wait=True)
        g.custom_command("disable-addons", "aks_disable_addons", supports_no_wait=True)
        g.custom_command("get-credentials", "aks_get_credentials")
        g.custom_command(
            "rotate-certs",
            "aks_rotate_certs",
            supports_no_wait=True,
            confirmation="Kubernetes will be unavailable during certificate rotation process.\n"
            + "Are you sure you want to perform this operation?",
        )
        g.custom_command("stop", "aks_stop", supports_no_wait=True)
        g.command("start", "begin_start", supports_no_wait=True)
        g.wait_command("wait")
        g.custom_command(
            "get-versions",
            "aks_get_versions",
            table_transformer=aks_versions_table_format,
        )
        # aks-preview only
        g.custom_command("kollect", "aks_kollect")
        g.custom_command("kanalyze", "aks_kanalyze")
        g.custom_command("get-os-options", "aks_get_os_options")
        g.custom_command(
            "operation-abort", "aks_operation_abort", supports_no_wait=True
        )

    # AKS maintenance configuration commands
    with self.command_group(
        "aks maintenanceconfiguration",
        maintenance_configuration_sdk,
        client_factory=cf_maintenance_configurations,
    ) as g:
        g.custom_command("list", "aks_maintenanceconfiguration_list")
        g.custom_show_command("show", "aks_maintenanceconfiguration_show")
        g.custom_command("add", "aks_maintenanceconfiguration_add")
        g.custom_command("update", "aks_maintenanceconfiguration_update")
        g.custom_command("delete", "aks_maintenanceconfiguration_delete")

    # AKS addon commands
    with self.command_group(
        "aks addon", managed_clusters_sdk, client_factory=cf_managed_clusters
    ) as g:
        g.custom_command(
            "list-available",
            "aks_addon_list_available",
            table_transformer=aks_addon_list_available_table_format,
        )
        g.custom_command(
            "list", "aks_addon_list", table_transformer=aks_addon_list_table_format
        )
        g.custom_show_command(
            "show", "aks_addon_show", table_transformer=aks_addon_show_table_format
        )
        g.custom_command("enable", "aks_addon_enable", supports_no_wait=True)
        g.custom_command("disable", "aks_addon_disable", supports_no_wait=True)
        g.custom_command("update", "aks_addon_update", supports_no_wait=True)

    # AKS agent pool commands
    with self.command_group(
        "aks nodepool", agent_pools_sdk, client_factory=cf_agent_pools
    ) as g:
        g.custom_command(
            "list",
            "aks_agentpool_list",
            table_transformer=aks_agentpool_list_table_format,
        )
        g.custom_show_command(
            "show",
            "aks_agentpool_show",
            table_transformer=aks_agentpool_show_table_format,
        )
        g.custom_command("add", "aks_agentpool_add", supports_no_wait=True)
        g.custom_command("scale", "aks_agentpool_scale", supports_no_wait=True)
        g.custom_command("upgrade", "aks_agentpool_upgrade", supports_no_wait=True)
        g.custom_command("update", "aks_agentpool_update", supports_no_wait=True)
        g.custom_command("delete", "aks_agentpool_delete", supports_no_wait=True)
        g.custom_command("get-upgrades", "aks_agentpool_get_upgrade_profile")
        g.custom_command("stop", "aks_agentpool_stop", supports_no_wait=True)
        g.custom_command("start", "aks_agentpool_start", supports_no_wait=True)
        g.custom_command(
            "operation-abort", "aks_agentpool_operation_abort", supports_no_wait=True
        )
        g.custom_command(
            "delete-machines", "aks_agentpool_delete_machines", supports_no_wait=True
        )

    with self.command_group(
        "aks machine", machines_sdk, client_factory=cf_machines
    ) as g:
        g.custom_command(
            "list", "aks_machine_list", table_transformer=aks_machine_list_table_format
        )
        g.custom_show_command(
            "show", "aks_machine_show", table_transformer=aks_machine_show_table_format
        )

    # AKS draft commands
    with self.command_group(
        "aks draft", managed_clusters_sdk, client_factory=cf_managed_clusters
    ) as g:
        g.custom_command("create", "aks_draft_create")
        g.custom_command("setup-gh", "aks_draft_setup_gh")
        g.custom_command("generate-workflow", "aks_draft_generate_workflow")
        g.custom_command("up", "aks_draft_up")
        g.custom_command("update", "aks_draft_update")

    # AKS pod identity commands
    with self.command_group(
        "aks pod-identity", managed_clusters_sdk, client_factory=cf_managed_clusters
    ) as g:
        g.custom_command("add", "aks_pod_identity_add")
        g.custom_command("delete", "aks_pod_identity_delete")
        g.custom_command(
            "list",
            "aks_pod_identity_list",
            table_transformer=aks_pod_identities_table_format,
        )

    # AKS pod identity exception commands
    with self.command_group(
        "aks pod-identity exception",
        managed_clusters_sdk,
        client_factory=cf_managed_clusters,
    ) as g:
        g.custom_command("add", "aks_pod_identity_exception_add")
        g.custom_command("delete", "aks_pod_identity_exception_delete")
        g.custom_command("update", "aks_pod_identity_exception_update")
        g.custom_command(
            "list",
            "aks_pod_identity_exception_list",
            table_transformer=aks_pod_identity_exceptions_table_format,
        )

    # AKS egress commands
    with self.command_group(
        "aks egress-endpoints", managed_clusters_sdk, client_factory=cf_managed_clusters
    ) as g:
        g.custom_command("list", "aks_egress_endpoints_list")

    # AKS nodepool snapshot commands
    with self.command_group(
        "aks nodepool snapshot",
        nodepool_snapshot_sdk,
        client_factory=cf_nodepool_snapshots,
    ) as g:
        g.custom_command(
            "list",
            "aks_nodepool_snapshot_list",
            table_transformer=aks_list_nodepool_snapshot_table_format,
        )
        g.custom_show_command(
            "show",
            "aks_nodepool_snapshot_show",
            table_transformer=aks_show_nodepool_snapshot_table_format,
        )
        g.custom_command(
            "create", "aks_nodepool_snapshot_create", supports_no_wait=True
        )
        g.custom_command("update", "aks_nodepool_snapshot_update")
        g.custom_command(
            "delete", "aks_nodepool_snapshot_delete", supports_no_wait=True
        )

    # AKS mc snapshot commands
    with self.command_group(
        "aks snapshot", mc_snapshot_sdk, client_factory=cf_mc_snapshots
    ) as g:
        g.custom_command(
            "list",
            "aks_snapshot_list",
            table_transformer=aks_list_snapshot_table_format,
        )
        g.custom_show_command(
            "show",
            "aks_snapshot_show",
            table_transformer=aks_show_snapshot_table_format,
        )
        g.custom_command("create", "aks_snapshot_create", supports_no_wait=True)
        g.custom_command("delete", "aks_snapshot_delete", supports_no_wait=True)

    # AKS trusted access role commands
    with self.command_group(
        "aks trustedaccess role",
        trustedaccess_role_sdk,
        client_factory=cf_trustedaccess_role,
    ) as g:
        g.custom_command("list", "aks_trustedaccess_role_list")

    # AKS trusted access rolebinding commands
    with self.command_group(
        "aks trustedaccess rolebinding",
        trustedaccess_role_binding_sdk,
        client_factory=cf_trustedaccess_role_binding,
    ) as g:
        g.custom_command("list", "aks_trustedaccess_role_binding_list")
        g.custom_show_command("show", "aks_trustedaccess_role_binding_get")
        g.custom_command("create", "aks_trustedaccess_role_binding_create")
        g.custom_command("update", "aks_trustedaccess_role_binding_update")
        g.custom_command(
            "delete", "aks_trustedaccess_role_binding_delete", confirmation=True
        )

    # AKS mesh commands
    with self.command_group(
        "aks mesh", managed_clusters_sdk, client_factory=cf_managed_clusters
    ) as g:
        g.custom_command("enable", "aks_mesh_enable", supports_no_wait=True)
        g.custom_command(
            "disable",
            "aks_mesh_disable",
            supports_no_wait=True,
            confirmation="Existing Azure Service Mesh Profile values will be reset.\n"
            + "Are you sure you want to perform this operation?"
        )
        g.custom_command(
            "enable-ingress-gateway",
            "aks_mesh_enable_ingress_gateway",
            supports_no_wait=True,
        )
        g.custom_command(
            "enable-egress-gateway",
            "aks_mesh_enable_egress_gateway",
            supports_no_wait=True,
        )
        g.custom_command(
            "disable-ingress-gateway",
            "aks_mesh_disable_ingress_gateway",
            supports_no_wait=True,
            confirmation=True,
        )
        g.custom_command(
            "disable-egress-gateway",
            "aks_mesh_disable_egress_gateway",
            supports_no_wait=True,
            confirmation=True,
        )
        g.custom_command(
            "get-revisions",
            "aks_mesh_get_revisions",
            table_transformer=aks_mesh_revisions_table_format,
        )
        g.custom_command(
            "get-upgrades",
            "aks_mesh_get_upgrades",
            table_transformer=aks_mesh_upgrades_table_format,
        )

    # AKS mesh upgrade commands
    with self.command_group(
        "aks mesh upgrade", managed_clusters_sdk, client_factory=cf_managed_clusters
    ) as g:
        g.custom_command("start", "aks_mesh_upgrade_start", supports_no_wait=True)
        g.custom_command("complete", "aks_mesh_upgrade_complete", supports_no_wait=True)
        g.custom_command("rollback", "aks_mesh_upgrade_rollback", supports_no_wait=True)

    # AKS approuting commands
    with self.command_group(
        "aks approuting", managed_clusters_sdk, client_factory=cf_managed_clusters
    ) as g:
        g.custom_command("enable", "aks_approuting_enable")
        g.custom_command("disable", "aks_approuting_disable", confirmation=True)
        g.custom_command("update", "aks_approuting_update")

    # AKS approuting dns-zone commands
    with self.command_group(
        "aks approuting zone", managed_clusters_sdk, client_factory=cf_managed_clusters
    ) as g:
        g.custom_command("add", "aks_approuting_zone_add")
        g.custom_command("delete", "aks_approuting_zone_delete", confirmation=True)
        g.custom_command("update", "aks_approuting_zone_update")
        g.custom_command("list", "aks_approuting_zone_list")

    # AKS check-network command
    with self.command_group(
        "aks check-network", managed_clusters_sdk, client_factory=cf_managed_clusters
    ) as g:
        g.custom_command("outbound", "aks_check_network_outbound")
