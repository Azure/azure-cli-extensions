# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import re
import yaml
import tempfile

from knack.util import CLIError

from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import sdk_no_wait, get_file_json, shell_safe_json_parse
from azure.cli.core import get_default_cli

from azext_fleet._client_factory import CUSTOM_MGMT_FLEET, cf_fleet_members, cf_fleets
from azext_fleet._helpers import print_or_merge_credentials
from azext_fleet._helpers import assign_network_contributor_role_to_subnet
from azext_fleet.constants import UPGRADE_TYPE_CONTROLPLANEONLY
from azext_fleet.constants import UPGRADE_TYPE_FULL
from azext_fleet.constants import UPGRADE_TYPE_NODEIMAGEONLY
from azext_fleet.constants import UPGRADE_TYPE_ERROR_MESSAGES
from azext_fleet.constants import SUPPORTED_GATE_STATES_FILTERS
from azext_fleet.constants import SUPPORTED_GATE_STATES_PATCH


# pylint: disable=too-many-locals
def create_fleet(cmd,
                 client,
                 resource_group_name,
                 name,
                 location=None,
                 tags=None,
                 enable_hub=False,
                 vm_size=None,
                 dns_name_prefix=None,
                 enable_private_cluster=False,
                 enable_vnet_integration=False,
                 apiserver_subnet_id=None,
                 agent_subnet_id=None,
                 enable_managed_identity=False,
                 assign_identity=None,
                 no_wait=False):
    fleet_model = cmd.get_models(
        "Fleet",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="fleets"
    )

    poll_interval = 5
    if enable_hub:
        poll_interval = 30
        fleet_hub_profile_model = cmd.get_models(
            "FleetHubProfile",
            resource_type=CUSTOM_MGMT_FLEET,
            operation_group="fleets"
        )
        api_server_access_profile_model = cmd.get_models(
            "APIServerAccessProfile",
            resource_type=CUSTOM_MGMT_FLEET,
            operation_group="fleets"
        )
        agent_profile_model = cmd.get_models(
            "AgentProfile",
            resource_type=CUSTOM_MGMT_FLEET,
            operation_group="fleets",
        )
        api_server_access_profile = api_server_access_profile_model(
            enable_private_cluster=enable_private_cluster,
            enable_vnet_integration=enable_vnet_integration,
            subnet_id=apiserver_subnet_id
        )
        agent_profile = agent_profile_model(
            subnet_id=agent_subnet_id,
            vm_size=vm_size
        )
        fleet_hub_profile = fleet_hub_profile_model(
            dns_prefix=dns_name_prefix,
            api_server_access_profile=api_server_access_profile,
            agent_profile=agent_profile)
    else:
        if dns_name_prefix is not None or \
           enable_private_cluster or \
           enable_vnet_integration or \
           apiserver_subnet_id is not None or \
           agent_subnet_id is not None:
            raise CLIError(
                "The parameters for private cluster, vnet & subnet integration are only valid if hub is enabled.")
        fleet_hub_profile = None

    fleet_managed_service_identity_model = cmd.get_models(
        "ManagedServiceIdentity",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="fleets"
    )
    managed_service_identity = fleet_managed_service_identity_model(type="None")
    if enable_managed_identity:
        managed_service_identity.type = "SystemAssigned"
        if assign_identity is not None:
            user_assigned_identity_model = cmd.get_models(
                "UserAssignedIdentity",
                resource_type=CUSTOM_MGMT_FLEET,
                operation_group="fleets"
            )
            managed_service_identity.type = "UserAssigned"
            managed_service_identity.user_assigned_identities = {assign_identity: user_assigned_identity_model()}
    elif assign_identity is not None:
        raise CLIError("Cannot assign identity without enabling managed identity.")

    fleet = fleet_model(
        location=location,
        tags=tags,
        hub_profile=fleet_hub_profile,
        identity=managed_service_identity
    )

    if enable_private_cluster:
        assign_network_contributor_role_to_subnet(cmd, agent_subnet_id)

    return sdk_no_wait(no_wait,
                       client.begin_create_or_update,
                       resource_group_name,
                       name,
                       fleet,
                       polling_interval=poll_interval)


def update_fleet(cmd,
                 client,
                 resource_group_name,
                 name,
                 enable_managed_identity=None,
                 assign_identity=None,
                 tags=None,
                 no_wait=False):
    fleet_patch_model = cmd.get_models(
        "FleetPatch",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="fleets"
    )
    fleet_managed_service_identity_model = cmd.get_models(
        "ManagedServiceIdentity",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="fleets"
    )

    if enable_managed_identity is None:
        managed_service_identity = None
        if assign_identity is not None:
            raise CLIError("Cannot assign identity without enabling managed identity.")
    elif enable_managed_identity is False:
        managed_service_identity = fleet_managed_service_identity_model(type="None")
    else:
        managed_service_identity = fleet_managed_service_identity_model(type="SystemAssigned")
        if assign_identity is not None:
            user_assigned_identity_model = cmd.get_models(
                "UserAssignedIdentity",
                resource_type=CUSTOM_MGMT_FLEET,
                operation_group="fleets"
            )
            managed_service_identity.type = "UserAssigned"
            managed_service_identity.user_assigned_identities = {assign_identity: user_assigned_identity_model()}

    fleet_patch = fleet_patch_model(
        tags=tags,
        identity=managed_service_identity
    )

    return sdk_no_wait(no_wait, client.begin_update, resource_group_name, name, fleet_patch, polling_interval=5)


def show_fleet(cmd,  # pylint: disable=unused-argument
               client,
               resource_group_name,
               name):
    return client.get(resource_group_name, name)


def list_fleet(cmd,  # pylint: disable=unused-argument
               client,
               resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)
    return client.list_by_subscription()


def delete_fleet(cmd,  # pylint: disable=unused-argument
                 client,
                 resource_group_name,
                 name,
                 no_wait=False):
    return sdk_no_wait(no_wait, client.begin_delete, resource_group_name, name, polling_interval=5)


def get_credentials(cmd,
                    client,
                    resource_group_name,
                    name,
                    path=os.path.join(os.path.expanduser('~'), '.kube', 'config'),
                    overwrite_existing=False,
                    context_name=None,
                    member_name=None):
    
    if member_name:
        # Get credentials from a specific fleet member's managed cluster
        fleet_members_client = cf_fleet_members(cmd.cli_ctx)
        
        try:
            # Get the fleet member to find the associated managed cluster
            fleet_member = fleet_members_client.get(resource_group_name, name, member_name)
            
            if not fleet_member or not fleet_member.cluster_resource_id:
                raise CLIError(f"Fleet member '{member_name}' not found or has no associated cluster.")
            
            # Parse the cluster resource ID to extract subscription, resource group, and cluster name
            cluster_resource_id = fleet_member.cluster_resource_id
            
            # Resource ID format: /subscriptions/{subscription}/resourceGroups/{rg}/providers/Microsoft.ContainerService/managedClusters/{cluster}
            match = re.match(
                r'/subscriptions/([^/]+)/resourceGroups/([^/]+)/providers/Microsoft\.ContainerService/managedClusters/([^/]+)',
                cluster_resource_id
            )
            
            if not match:
                raise CLIError(f"Invalid cluster resource ID format: {cluster_resource_id}")
            
            cluster_subscription = match.group(1)
            cluster_resource_group = match.group(2)
            cluster_name = match.group(3)
            
            # Build the AKS get-credentials command
            aks_command = [
                'aks', 'get-credentials',
                '--subscription', cluster_subscription,
                '--resource-group', cluster_resource_group,
                '--name', cluster_name,
                '--user'
            ]
            
            # Add optional parameters if provided
            if path != os.path.join(os.path.expanduser('~'), '.kube', 'config'):
                aks_command.extend(['--file', path])
            
            if overwrite_existing:
                aks_command.append('--overwrite-existing')
                
            if context_name:
                aks_command.extend(['--context', context_name])
            
            # Execute the AKS get-credentials command
            cli = get_default_cli()
            exit_code = cli.invoke(aks_command)
            
            if exit_code != 0:
                raise CLIError(f"Failed to get credentials from managed cluster '{cluster_name}' in fleet member '{member_name}'.")
                
        except Exception as exc:
            if isinstance(exc, CLIError):
                raise
            raise CLIError(f"Error getting credentials for fleet member '{member_name}': {str(exc)}") from exc
    
    else:
        # Original fleet hub credentials behavior
        credential_results = client.list_credentials(resource_group_name, name)
        if not credential_results:
            raise CLIError("No Kubernetes credentials found.")

        try:
            kubeconfig = credential_results.kubeconfigs[0].value.decode(encoding='UTF-8')
            print_or_merge_credentials(path, kubeconfig, overwrite_existing, context_name)
        except (IndexError, ValueError) as exc:
            raise CLIError("Fail to find kubeconfig file.") from exc


def reconcile_fleet(cmd,  # pylint: disable=unused-argument
                    client,
                    resource_group_name,
                    name,
                    no_wait=False):

    poll_interval = 5
    fleet = client.get(resource_group_name, name)
    if fleet.hub_profile is not None:
        poll_interval = 30

    return sdk_no_wait(no_wait,
                       client.begin_create_or_update,
                       resource_group_name,
                       name,
                       fleet,
                       if_match=fleet.e_tag,
                       polling_interval=poll_interval)


def create_fleet_member(cmd,
                        client,
                        resource_group_name,
                        name,
                        fleet_name,
                        member_cluster_id,
                        update_group=None,
                        member_labels=None,
                        no_wait=False):
    fleet_member_model = cmd.get_models(
        "FleetMember",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="fleet_members"
    )
    fleet_member = fleet_member_model(cluster_resource_id=member_cluster_id, group=update_group, labels=member_labels)
    return sdk_no_wait(no_wait, client.begin_create, resource_group_name, fleet_name, name, fleet_member)


def update_fleet_member(cmd,
                        client,
                        resource_group_name,
                        name,
                        fleet_name,
                        update_group=None,
                        member_labels=None,
                        no_wait=False):
    fleet_member_update_model = cmd.get_models(
        "FleetMemberUpdate",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="fleet_members"
    )
    properties = fleet_member_update_model(group=update_group, labels=member_labels)
    return sdk_no_wait(no_wait, client.begin_update, resource_group_name, fleet_name, name, properties)


def list_fleet_member(cmd,  # pylint: disable=unused-argument
                      client,
                      resource_group_name,
                      fleet_name):
    return client.list_by_fleet(resource_group_name, fleet_name)


def show_fleet_member(cmd,  # pylint: disable=unused-argument
                      client,
                      resource_group_name,
                      fleet_name,
                      name):
    return client.get(resource_group_name, fleet_name, name)


def delete_fleet_member(cmd,  # pylint: disable=unused-argument
                        client,
                        resource_group_name,
                        fleet_name,
                        name,
                        no_wait=False):
    return sdk_no_wait(no_wait, client.begin_delete, resource_group_name, fleet_name, name)


def reconcile_fleet_member(cmd,  # pylint: disable=unused-argument
                           client,
                           resource_group_name,
                           name,
                           fleet_name,
                           no_wait=False):

    member = client.get(resource_group_name, fleet_name, name)
    return sdk_no_wait(no_wait,
                       client.begin_create,
                       resource_group_name,
                       fleet_name,
                       name,
                       member,
                       if_match=member.e_tag)


def create_update_run(cmd,
                      client,
                      resource_group_name,
                      fleet_name,
                      name,
                      upgrade_type,
                      node_image_selection=None,
                      kubernetes_version=None,
                      stages=None,
                      update_strategy_name=None,
                      no_wait=False):

    if upgrade_type in UPGRADE_TYPE_ERROR_MESSAGES:
        if (
            ((upgrade_type in (UPGRADE_TYPE_FULL, UPGRADE_TYPE_CONTROLPLANEONLY)) and kubernetes_version is None) or  # pylint: disable=line-too-long
            (upgrade_type == UPGRADE_TYPE_NODEIMAGEONLY and kubernetes_version is not None)
        ):
            raise CLIError(UPGRADE_TYPE_ERROR_MESSAGES[upgrade_type])
    else:
        raise CLIError((f"The upgrade type parameter '{upgrade_type}' is not valid."
                        f"Valid options are: '{UPGRADE_TYPE_FULL}', '{UPGRADE_TYPE_CONTROLPLANEONLY}', or '{UPGRADE_TYPE_NODEIMAGEONLY}'"))  # pylint: disable=line-too-long

    if stages is not None and update_strategy_name is not None:
        raise CLIError("Cannot set stages when update strategy name is set.")

    update_run_strategy = get_update_run_strategy(cmd, "update_runs", stages)

    managed_cluster_upgrade_spec_model = cmd.get_models(
        "ManagedClusterUpgradeSpec",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="update_runs"
    )
    managed_cluster_update_model = cmd.get_models(
        "ManagedClusterUpdate",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="update_runs"
    )
    node_image_selection_model = cmd.get_models(
        "NodeImageSelection",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="update_runs"
    )
    update_run_model = cmd.get_models(
        "UpdateRun",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="update_runs"
    )

    managed_cluster_upgrade_spec = managed_cluster_upgrade_spec_model(
        type=upgrade_type, kubernetes_version=kubernetes_version)
    if node_image_selection is None:
        node_image_selection = "Latest"
    node_image_selection_type = node_image_selection_model(type=node_image_selection)

    managed_cluster_update = managed_cluster_update_model(
        upgrade=managed_cluster_upgrade_spec,
        node_image_selection=node_image_selection_type)

    updateStrategyId = None
    if update_strategy_name is not None:
        subId = get_subscription_id(cmd.cli_ctx)
        updateStrategyId = (
            f"/subscriptions/{subId}/resourceGroups/{resource_group_name}"
            f"/providers/Microsoft.ContainerService/fleets/{fleet_name}/updateStrategies/{update_strategy_name}"
        )

    update_run = update_run_model(
        update_strategy_id=updateStrategyId,
        strategy=update_run_strategy,
        managed_cluster_update=managed_cluster_update)

    result = sdk_no_wait(no_wait, client.begin_create_or_update, resource_group_name, fleet_name, name, update_run)
    print("After successfully creating the run, you need to use the following command to start the run:"
          f"az fleet updaterun start --resource-group={resource_group_name} --fleet={fleet_name} --name={name}")
    return result


def show_update_run(cmd,  # pylint: disable=unused-argument
                    client,
                    resource_group_name,
                    fleet_name,
                    name):
    return client.get(resource_group_name, fleet_name, name)


def list_update_run(cmd,  # pylint: disable=unused-argument
                    client,
                    resource_group_name,
                    fleet_name):
    return client.list_by_fleet(resource_group_name, fleet_name)


def delete_update_run(cmd,  # pylint: disable=unused-argument
                      client,
                      resource_group_name,
                      fleet_name,
                      name,
                      no_wait=False):
    return sdk_no_wait(no_wait, client.begin_delete, resource_group_name, fleet_name, name)


def start_update_run(cmd,  # pylint: disable=unused-argument
                     client,
                     resource_group_name,
                     fleet_name,
                     name,
                     no_wait=False):
    return sdk_no_wait(no_wait, client.begin_start, resource_group_name, fleet_name, name)


def stop_update_run(cmd,  # pylint: disable=unused-argument
                    client,
                    resource_group_name,
                    fleet_name,
                    name,
                    no_wait=False):
    return sdk_no_wait(no_wait, client.begin_stop, resource_group_name, fleet_name, name)


def skip_update_run(cmd,  # pylint: disable=unused-argument
                    client,
                    resource_group_name,
                    fleet_name,
                    name,
                    targets=None,
                    no_wait=False):

    update_run_skip_properties_model = cmd.get_models(
        "SkipProperties",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="update_runs"
    )

    update_run_skip_target_model = cmd.get_models(
        "SkipTarget",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="update_runs"
    )

    skipTargets = []
    for target in targets:
        key, value = target.split(':')
        skipTargets.append(update_run_skip_target_model(
            type=key,
            name=value
        ))

    skip_properties = update_run_skip_properties_model(targets=skipTargets)
    return sdk_no_wait(no_wait, client.begin_skip, resource_group_name, fleet_name, name, skip_properties)


def get_update_run_strategy(cmd, operation_group, stages):
    if stages is None:
        return None

    # Check if the input is a file path or inline JSON
    if os.path.exists(stages):
        data = get_file_json(stages)
    else:
        data = shell_safe_json_parse(stages)

    update_group_model = cmd.get_models(
        "UpdateGroup",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group=operation_group
    )
    update_stage_model = cmd.get_models(
        "UpdateStage",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group=operation_group
    )
    update_run_strategy_model = cmd.get_models(
        "UpdateRunStrategy",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group=operation_group
    )

    update_stages = []

    for stage in data["stages"]:
        update_groups = []
        for group in stage["groups"]:
            update_groups.append(update_group_model(
                name=group["name"],
                before_gates=group.get("beforeGates", []),
                after_gates=group.get("afterGates", []),
            ))

        after_wait = stage.get("afterStageWaitInSeconds") or 0

        update_stages.append(update_stage_model(
            name=stage["name"],
            groups=update_groups,
            before_gates=stage.get("beforeGates", []),
            after_gates=stage.get("afterGates", []),
            after_stage_wait_in_seconds=after_wait
        ))

    return update_run_strategy_model(stages=update_stages)


def create_fleet_update_strategy(cmd,
                                 client,
                                 resource_group_name,
                                 fleet_name,
                                 name,
                                 stages,
                                 no_wait=False):
    update_run_strategy_model = get_update_run_strategy(cmd, "fleet_update_strategies", stages)

    fleet_update_strategy_model = cmd.get_models(
        "FleetUpdateStrategy",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="fleet_update_strategies"
    )
    fleet_update_strategy = fleet_update_strategy_model(strategy=update_run_strategy_model)
    return sdk_no_wait(
        no_wait, client.begin_create_or_update, resource_group_name, fleet_name, name, fleet_update_strategy)


def show_fleet_update_strategy(cmd,  # pylint: disable=unused-argument
                               client,
                               resource_group_name,
                               fleet_name,
                               name):
    return client.get(resource_group_name, fleet_name, name)


def list_fleet_update_strategies(cmd,  # pylint: disable=unused-argument
                                 client,
                                 resource_group_name,
                                 fleet_name):
    return client.list_by_fleet(resource_group_name, fleet_name)


def delete_fleet_update_strategy(cmd,  # pylint: disable=unused-argument
                                 client,
                                 resource_group_name,
                                 fleet_name,
                                 name,
                                 no_wait=False):
    return sdk_no_wait(no_wait, client.begin_delete, resource_group_name, fleet_name, name)


def create_auto_upgrade_profile(cmd,  # pylint: disable=unused-argument
                                client,
                                resource_group_name,
                                fleet_name,
                                name,
                                channel,
                                update_strategy_id=None,
                                node_image_selection=None,
                                target_kubernetes_version=None,
                                long_term_support=False,
                                disabled=False,
                                no_wait=False):

    if channel == "NodeImage" and node_image_selection is not None:
        raise CLIError("node_image_selection must NOT be populated when channel type `NodeImage` is selected")

    upgrade_channel_model = cmd.get_models(
        "UpgradeChannel",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="auto_upgrade_profiles",
    )
    upgrade_channel = upgrade_channel_model(channel)

    auto_upgrade_node_image_selection = None
    if node_image_selection:
        auto_upgrade_node_image_selection_model = cmd.get_models(
            "AutoUpgradeNodeImageSelection",
            resource_type=CUSTOM_MGMT_FLEET,
            operation_group="auto_upgrade_profiles",
        )
        auto_upgrade_node_image_selection = auto_upgrade_node_image_selection_model(type=node_image_selection)

    auto_upgrade_profile_model = cmd.get_models(
        "AutoUpgradeProfile",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="auto_upgrade_profiles",
    )
    auto_upgrade_profile = auto_upgrade_profile_model(
        update_strategy_id=update_strategy_id,
        channel=upgrade_channel,
        node_image_selection=auto_upgrade_node_image_selection,
        target_kubernetes_version=target_kubernetes_version,
        long_term_support=long_term_support,
        disabled=disabled
    )

    return sdk_no_wait(no_wait,
                       client.begin_create_or_update,
                       resource_group_name,
                       fleet_name,
                       name,
                       auto_upgrade_profile)


def show_auto_upgrade_profile(cmd,  # pylint: disable=unused-argument
                              client,
                              resource_group_name,
                              fleet_name,
                              name):
    return client.get(resource_group_name, fleet_name, name)


def list_auto_upgrade_profiles(cmd,  # pylint: disable=unused-argument
                               client,
                               resource_group_name,
                               fleet_name):
    return client.list_by_fleet(resource_group_name, fleet_name)


def delete_auto_upgrade_profile(cmd,  # pylint: disable=unused-argument
                                client,
                                resource_group_name,
                                fleet_name,
                                name,
                                no_wait=False):
    return sdk_no_wait(no_wait, client.begin_delete, resource_group_name, fleet_name, name)


def generate_update_run(cmd,  # pylint: disable=unused-argument
                        client,
                        resource_group_name,
                        fleet_name,
                        auto_upgrade_profile_name,
                        no_wait=False):
    return sdk_no_wait(
        no_wait,
        client.begin_generate_update_run,
        resource_group_name,
        fleet_name,
        auto_upgrade_profile_name
    )


def list_gates_by_fleet(cmd,  # pylint: disable=unused-argument
                        client,
                        resource_group_name,
                        fleet_name,
                        state_filter=None):
    params = {}

    if state_filter:
        if state_filter not in SUPPORTED_GATE_STATES_FILTERS:
            raise CLIError(
                f"Unsupported gate state filter value: '{state_filter}'. "
                f"Allowed values are {SUPPORTED_GATE_STATES_FILTERS}"
            )

        params["$filter"] = f"state eq {state_filter}"

    return client.list_by_fleet(resource_group_name, fleet_name, params=params)


def show_gate(cmd,  # pylint: disable=unused-argument
              client,
              resource_group_name,
              fleet_name,
              gate_name):
    return client.get(resource_group_name, fleet_name, gate_name)


def _patch_gate(cmd,  # pylint: disable=unused-argument
                client,
                resource_group_name,
                fleet_name,
                gate_name,
                gate_state,
                no_wait=False):
    if gate_state not in SUPPORTED_GATE_STATES_PATCH:
        raise CLIError(
            f"Unsupported gate state value: '{gate_state}'. "
            f"Allowed values are {SUPPORTED_GATE_STATES_PATCH}"
        )

    gate_model = cmd.get_models(
        "GatePatch",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="gates"
    )
    gate_properties_model = cmd.get_models(
        "GatePatchProperties",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="gates"
    )

    properties = gate_properties_model(state=gate_state)
    patch_request = gate_model(properties=properties)

    return sdk_no_wait(no_wait, client.begin_update, resource_group_name, fleet_name, gate_name, patch_request)


def update_gate(cmd,  # pylint: disable=unused-argument
                client,
                resource_group_name,
                fleet_name,
                gate_name,
                gate_state=None,
                no_wait=False):
    return _patch_gate(cmd, client, resource_group_name, fleet_name, gate_name, gate_state, no_wait)


def approve_gate(cmd,  # pylint: disable=unused-argument
                 client,
                 resource_group_name,
                 fleet_name,
                 gate_name,
                 no_wait=False):
    return _patch_gate(cmd, client, resource_group_name, fleet_name, gate_name, "Completed", no_wait)


def create_managed_namespace(cmd,
                             client,
                             resource_group_name,
                             fleet_name,
                             managed_namespace_name,
                             labels=None,
                             annotations=None,
                             cpu_requests=None,
                             cpu_limits=None,
                             memory_requests=None,
                             memory_limits=None,
                             ingress_policy=None,
                             egress_policy=None,
                             delete_policy=None,
                             adoption_policy=None,
                             member_cluster_names=None):
    managed_namespace_model = cmd.get_models(
        "FleetManagedNamespace",
        resource_type=CUSTOM_MGMT_FLEET
    )

    managed_namespace_properties_model = cmd.get_models(
        "ManagedNamespaceProperties",
        resource_type=CUSTOM_MGMT_FLEET
    )

    fleet_managed_namespace_properties_model = cmd.get_models(
        "FleetManagedNamespaceProperties",
        resource_type=CUSTOM_MGMT_FLEET
    )

    resource_limits = {}
    if cpu_requests or cpu_limits or memory_requests or memory_limits:
        if cpu_requests or memory_requests:
            resource_limits['requests'] = {}
            if cpu_requests:
                resource_limits['requests']['cpu'] = cpu_requests
            if memory_requests:
                resource_limits['requests']['memory'] = memory_requests

        if cpu_limits or memory_limits:
            resource_limits['limits'] = {}
            if cpu_limits:
                resource_limits['limits']['cpu'] = cpu_limits
            if memory_limits:
                resource_limits['limits']['memory'] = memory_limits

    member_clusters = None
    if member_cluster_names:
        member_clusters = [name.strip() for name in member_cluster_names.split(',') if name.strip()]

    managed_namespace_props = managed_namespace_properties_model(
        labels=labels,
        annotations=annotations,
        resource_quota=resource_limits if resource_limits else None,
        ingress_policy=ingress_policy,
        egress_policy=egress_policy,
        delete_policy=delete_policy,
        adoption_policy=adoption_policy,
        member_clusters=member_clusters
    )

    fleet_managed_namespace_props = fleet_managed_namespace_properties_model(
        managed_namespace_properties=managed_namespace_props
    )

    managed_namespace = managed_namespace_model(
        properties=fleet_managed_namespace_props
    )

    return client.begin_create_or_update(
        resource_group_name=resource_group_name,
        fleet_name=fleet_name,
        managed_namespace_name=managed_namespace_name,
        resource=managed_namespace
    )


def update_managed_namespace(cmd,
                             client,
                             resource_group_name,
                             fleet_name,
                             managed_namespace_name,
                             labels=None,
                             annotations=None,
                             cpu_requests=None,
                             cpu_limits=None,
                             memory_requests=None,
                             memory_limits=None,
                             ingress_policy=None,
                             egress_policy=None,
                             delete_policy=None,
                             adoption_policy=None,
                             member_cluster_names=None):

    fleet_managed_namespace_patch_model = cmd.get_models(
        "FleetManagedNamespacePatch",
        resource_type=CUSTOM_MGMT_FLEET
    )

    managed_namespace_properties_model = cmd.get_models(
        "ManagedNamespaceProperties",
        resource_type=CUSTOM_MGMT_FLEET
    )

    resource_limits = {}
    if cpu_requests or cpu_limits or memory_requests or memory_limits:
        if cpu_requests or memory_requests:
            resource_limits['requests'] = {}
            if cpu_requests:
                resource_limits['requests']['cpu'] = cpu_requests
            if memory_requests:
                resource_limits['requests']['memory'] = memory_requests

        if cpu_limits or memory_limits:
            resource_limits['limits'] = {}
            if cpu_limits:
                resource_limits['limits']['cpu'] = cpu_limits
            if memory_limits:
                resource_limits['limits']['memory'] = memory_limits

    member_clusters = None
    if member_cluster_names:
        member_clusters = [name.strip() for name in member_cluster_names.split(',') if name.strip()]

    properties = managed_namespace_properties_model(
        labels=labels,
        annotations=annotations,
        resource_quota=resource_limits if resource_limits else None,
        ingress_policy=ingress_policy,
        egress_policy=egress_policy,
        delete_policy=delete_policy,
        adoption_policy=adoption_policy,
        member_clusters=member_clusters
    )

    patch = fleet_managed_namespace_patch_model(properties=properties)

    return client.begin_update(
        resource_group_name=resource_group_name,
        fleet_name=fleet_name,
        managed_namespace_name=managed_namespace_name,
        properties=patch
    )


def delete_managed_namespace(cmd,  # pylint: disable=unused-argument
                             client,
                             resource_group_name,
                             fleet_name,
                             managed_namespace_name):
    return client.begin_delete(
        resource_group_name=resource_group_name,
        fleet_name=fleet_name,
        managed_namespace_name=managed_namespace_name
    )


def show_managed_namespace(cmd,  # pylint: disable=unused-argument
                           client,
                           resource_group_name,
                           fleet_name,
                           managed_namespace_name):
    return client.get(
        resource_group_name=resource_group_name,
        fleet_name=fleet_name,
        managed_namespace_name=managed_namespace_name
    )


def list_managed_namespaces(cmd,  # pylint: disable=unused-argument
                            client,
                            resource_group_name,
                            fleet_name):
    return client.list_by_fleet(
        resource_group_name=resource_group_name,
        fleet_name=fleet_name
    )


def get_namespace_credentials(cmd,
                             client,  # pylint: disable=unused-argument
                             resource_group_name,
                             fleet_name,
                             managed_namespace_name,
                             path=os.path.join(os.path.expanduser('~'), '.kube', 'config'),
                             overwrite_existing=False,
                             context_name=None,
                             member_name=None):
    """
    Get credentials for a fleet namespace by calling fleet get-credentials backend
    and modifying the namespace in the kubeconfig.
    """
    
    fleet_client = cf_fleets(cmd.cli_ctx)
    
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.kubeconfig', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        get_credentials(
            cmd=cmd,
            client=fleet_client,
            resource_group_name=resource_group_name,
            name=fleet_name,
            path=temp_path,
            overwrite_existing=True, 
            context_name=context_name,
            member_name=member_name
        )
        
        with open(temp_path, 'r', encoding='utf-8') as f:
            kubeconfig_content = f.read()
        
        kubeconfig = yaml.safe_load(kubeconfig_content)
        
        if 'contexts' in kubeconfig:
            for context in kubeconfig['contexts']:
                if 'context' in context:
                    context['context']['namespace'] = managed_namespace_name
        
        if path == '-':
            print(yaml.dump(kubeconfig, default_flow_style=False))
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            if not overwrite_existing and os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    existing_config = yaml.safe_load(f.read())
                
                if existing_config:
                    merged_config = existing_config.copy()
                    
                    if 'clusters' in kubeconfig:
                        if 'clusters' not in merged_config:
                            merged_config['clusters'] = []
                        for cluster in kubeconfig['clusters']:
                            existing_cluster = next((c for c in merged_config['clusters'] if c['name'] == cluster['name']), None)
                            if existing_cluster:
                                existing_cluster.update(cluster)
                            else:
                                merged_config['clusters'].append(cluster)
                    
                    if 'users' in kubeconfig:
                        if 'users' not in merged_config:
                            merged_config['users'] = []
                        for user in kubeconfig['users']:
                            existing_user = next((u for u in merged_config['users'] if u['name'] == user['name']), None)
                            if existing_user:
                                existing_user.update(user)
                            else:
                                merged_config['users'].append(user)
                    
                    if 'contexts' in kubeconfig:
                        if 'contexts' not in merged_config:
                            merged_config['contexts'] = []
                        for context in kubeconfig['contexts']:
                            existing_context = next((c for c in merged_config['contexts'] if c['name'] == context['name']), None)
                            if existing_context:
                                existing_context.update(context)
                            else:
                                merged_config['contexts'].append(context)
                    
                    if 'current-context' in kubeconfig:
                        merged_config['current-context'] = kubeconfig['current-context']
                    
                    kubeconfig = merged_config
            
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(kubeconfig, f, default_flow_style=False)
            
            print(f"Merged kubeconfig saved to {path}")
            if 'contexts' in kubeconfig and kubeconfig['contexts']:
                print(f"Default namespace set to '{managed_namespace_name}' for all contexts")
    
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
