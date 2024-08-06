# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import json

from knack.util import CLIError

from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import sdk_no_wait

from azext_fleet._client_factory import CUSTOM_MGMT_FLEET
from azext_fleet._helpers import print_or_merge_credentials
from azext_fleet.constants import UPGRADE_TYPE_CONTROLPLANEONLY
from azext_fleet.constants import UPGRADE_TYPE_FULL
from azext_fleet.constants import UPGRADE_TYPE_NODEIMAGEONLY
from azext_fleet.constants import UPGRADE_TYPE_ERROR_MESSAGES


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
            vm_size=vm_size
        )
        api_server_access_profile = api_server_access_profile_model(
            enable_private_cluster=enable_private_cluster,
            enable_vnet_integration=enable_vnet_integration,
            subnet_id=apiserver_subnet_id
        )
        agent_profile = agent_profile_model(
            subnet_id=agent_subnet_id
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


def get_credentials(cmd,  # pylint: disable=unused-argument
                    client,
                    resource_group_name,
                    name,
                    path=os.path.join(os.path.expanduser(
                        '~'), '.kube', 'config'),
                    overwrite_existing=False,
                    context_name=None):
    credential_results = client.list_credentials(resource_group_name, name)
    if not credential_results:
        raise CLIError("No Kubernetes credentials found.")

    try:
        kubeconfig = credential_results.kubeconfigs[0].value.decode(
            encoding='UTF-8')
        print_or_merge_credentials(
            path, kubeconfig, overwrite_existing, context_name)
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
                        no_wait=False):
    fleet_member_model = cmd.get_models(
        "FleetMember",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="fleet_members"
    )
    fleet_member = fleet_member_model(cluster_resource_id=member_cluster_id, group=update_group)
    return sdk_no_wait(no_wait, client.begin_create, resource_group_name, fleet_name, name, fleet_member)


def update_fleet_member(cmd,
                        client,
                        resource_group_name,
                        name,
                        fleet_name,
                        update_group=None,
                        no_wait=False):
    fleet_member_update_model = cmd.get_models(
        "FleetMemberUpdate",
        resource_type=CUSTOM_MGMT_FLEET,
        operation_group="fleet_members"
    )
    properties = fleet_member_update_model(group=update_group)
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

    with open(stages, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
        fp.close()

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
            update_groups.append(update_group_model(name=group["name"]))
        sec = stage.get("afterStageWaitInSeconds") or 0
        update_stages.append(update_stage_model(
            name=stage["name"],
            groups=update_groups,
            after_stage_wait_in_seconds=sec))

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
