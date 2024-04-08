# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['fleet'] = """
    type: group
    short-summary: Commands to manage fleet.
"""

helps['fleet create'] = """
    type: command
    short-summary: Creates or updates a fleet.
    parameters:
        - name: --dns-name-prefix -p
          type: string
          short-summary: Prefix for host names that are created. If not specified, generate a host name using the
                         managed cluster and resource group names.
    examples:
        - name: Create a hubless fleet.
          text: az fleet create -g MyFleetResourceGroup -l MyLocation -n MyFleetName --tags "TagKey=TagValue"
        - name: Create a hubful fleet.
          text: az fleet create -g MyFleetResourceGroup -l MyLocation -n MyFleetName --enable-hub --tags "TagKey=TagValue"
        - name: Create a fleet with a system assigned managed service identity.
          text: az fleet create -g MyFleetResourceGroup -l MyLocation -n MyFleetName --enable-managed-identity
        - name: Create a fleet with a user assigned managed service identity.
          text: az fleet create -g MyFleetResourceGroup -l MyLocation -n MyFleetName --enable-managed-identity --assign-identity "/subscription/00000000-0000-0000-0000-000000000000/resourcegroup/MyFleetResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/MyIdentity"
"""

helps['fleet update'] = """
    type: command
    short-summary: Patches a fleet resource.
    examples:
        - name: Update a fleet's tags.
          text: az fleet update -g MyFleetResourceGroup -n MyFleetName --tags Key=Value
        - name: Update a fleet to use a system assigned managed service identity.
          text: az fleet update -g MyFleetResourceGroup -n MyFleetName --enable-managed-identity --tags Key=Value
        - name: Update a fleet to use a user assigned managed service identity.
          text: az fleet update -g MyFleetResourceGroup -n MyFleetName --enable-managed-identity --assign-identity "/subscription/00000000-0000-0000-0000-000000000000/resourcegroup/MyFleetResourceGroup/providers/Microsoft.ManagedIdentity/userAssignedIdentities/MyIdentity" --tags Key=Value
"""

helps['fleet show'] = """
    type: command
    short-summary: Gets a fleet.
    examples:
        - name: Show the details of a fleet.
          text: az fleet show -g MyFleetResourceGroup -n MyFleetName
"""

helps['fleet list'] = """
    type: command
    short-summary: Lists all fleets within a resource group.
    examples:
        - name: List all fleets with a specific subscription.
          text: az fleet list
        - name: List all fleets that exist within a specific subscription and resource group.
          text: az fleet list -g MyResourceGroup
"""

helps['fleet delete'] = """
    type: command
    short-summary: Deletes a fleet.
    examples:
        - name: Delete a specific fleet.
          text: az fleet delete -g MyFleetResourceGroup -n MyFleetName
"""

helps['fleet get-credentials'] = """
    type: command
    short-summary: For hubful fleets, gets the kubeconfig for the fleet's hub cluster.
    parameters:
    - name: --overwrite-existing
      type: bool
      short-summary: Overwrite any existing cluster entry with the same name.
    - name: --file -f
      type: string
      short-summary: Kubernetes configuration file to update. Use "-" to print YAML to stdout instead.
    examples:
        - name: Get a fleet's hub cluster kubeconfig.
          text: az fleet get-credentials -g MyFleetResourceGroup -n MyFleetName
        - name: Get a fleet's hub cluster kubeconfig, and save it to a specific file.
          text: az fleet get-credentials -g MyFleetResourceGroup -n MyFleetName -f ~/mykubeconfigfile.txt
"""

helps['fleet reconcile'] = """
    type: command
    short-summary: Reconciles a fleet.
    examples:
        - name: Reconcile a fleet.
          text: az fleet reconcile -g MyFleetResourceGroup -n MyFleetName
"""

helps['fleet wait'] = """
type: command
short-summary: Wait for a fleet resource to reach a desired state.
long-summary: If an operation on fleet was interrupted or was started with `--no-wait`, use this command to wait for it to complete.
"""

helps['fleet member'] = """
    type: group
    short-summary: Commands to manage members.
"""

helps['fleet member create'] = """
    type: command
    short-summary: Creates or updates a member.
    parameters:
        - name: --member-cluster-id
          type: string
          short-summary: ID of the managed cluster.
        - name: --update-group
          type: string
          short-summary: Update group of the member.
    examples:
        - name: Create a member and assign it to an update group.
          text: az fleet member create -g MyFleetResourceGroup -f MyFleetName -n NameOfMember --update-group UpdateGroup1 --member-cluster-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MyFleetResourceGroup/providers/Microsoft.ContainerService/managedClusters/MyManagedCluster"
"""

helps['fleet member update'] = """
    type: command
    short-summary: Update a member.
    parameters:
        - name: --update-group
          type: string
          short-summary: Update group of the member.
    examples:
        - name: Update an existing member's update group.
          text: az fleet member update -g MyFleetResourceGroup -f MyFleetName -n NameOfMember --update-group UpdateGroup2
"""

helps['fleet member list'] = """
    type: command
    short-summary: Lists a fleet's members.
    examples:
        - name: List all members for a given fleet.
          text: az fleet member list -g MyFleetResourceGroup -f MyFleetName
"""

helps['fleet member show'] = """
    type: command
    short-summary: Gets a fleet member.
    examples:
        - name: Show the details of a specific fleet member.
          text: az fleet member show -g MyFleetResourceGroup -f MyFleetName -n NameOfMember
"""

helps['fleet member delete'] = """
    type: command
    short-summary: Deletes a fleet member.
    examples:
        - name: Delete a specific fleet member.
          text: az fleet member delete -g MyFleetResourceGroup -f MyFleetName -n NameOfMember
"""

helps['fleet member reconcile'] = """
    type: command
    short-summary: Reconciles a member.
    examples:
        - name: Reconcile a member.
          text: az fleet member reconcile -g MyFleetResourceGroup -f MyFleetName -n NameOfMember
"""

helps['fleet member wait'] = """
    type: command
    short-summary: Wait for a member resource to reach a desired state.
    long-summary: If an operation on member was interrupted or was started with `--no-wait`, use this command to wait for it to complete.
"""

helps['fleet updaterun'] = """
    type: group
    short-summary: Commands to manage update runs.
"""

helps['fleet updaterun create'] = """
    type: command
    short-summary: Creates or updates an update run.
    parameters:
        - name: --upgrade-type
          type: string
          short-summary: Specify the upgrade type of members. Acceptable values are 'Full', 'ControlPlaneOnly', and 'NodeImageOnly'.
        - name: --kubernetes-version
          type: string
          short-summary: Specify the kubernetes version to upgrade member(s) to, when --upgrade-type is set to 'Full' or 'ControlPlaneOnly'. Acceptable format is x.x.x (eg. 1.2.3).
        - name: --stages
          type: string
          short-summary: Path to a JSON file that defines stages to upgrade a fleet. See examples for reference.
    examples:
        - name: Create an update run for a fleet with 'Full' upgrade type.
          text: az fleet updaterun create -g MyResourceGroup -f MyFleet -n MyUpdateRun --upgrade-type Full --kubernetes-version 1.25.0 --node-image-selection Latest
        - name: Create an update run for a fleet with 'NodeImageOnly' upgrade type.
          text: az fleet updaterun create -g MyResourceGroup -f MyFleet -n MyUpdateRun --upgrade-type NodeImageOnly --node-image-selection Latest
        - name: Create an update run for a fleet with 'Full' upgrade type & stages.
          text: |
            az fleet updaterun create -g MyResourceGroup -f MyFleet -n MyUpdateRun --upgrade-type Full --kubernetes-version 1.25.0 --node-image-selection Latest --stages ./test/stages.json

                The following JSON structure represents example contents of the parameter '--stages ./test/stages.json'.
                A stages array is composed of one or more stages, each containing one or more groups.
                Each group contains the 'name' property, which represents the group to which a cluster belongs (see 'az fleet member create --help').
                Stages have an optional 'afterStageWaitInSeconds' integer property, acting as a delay between stage execution.
                {
                    "stages": [
                        {
                            "name": "stage1",
                            "groups": [
                                {
                                    "name": "group-a1"
                                },
                                {
                                    "name": "group-a2"
                                },
                                {
                                    "name": "group-a3"
                                }
                            ],
                            "afterStageWaitInSeconds": 3600
                        },
                        {
                            "name": "stage2",
                            "groups": [
                                {
                                    "name": "group-b1"
                                },
                                {
                                    "name": "group-b2"
                                },
                                {
                                    "name": "group-b3"
                                }
                            ]
                        },
                    ]
                }
"""

helps['fleet updaterun show'] = """
    type: command
    short-summary: Shows an update run.
    examples:
        - name: Show the details of an update run.
          text: az fleet updaterun show -g MyFleetResourceGroup -f MyFleetName -n NameofUpdateRun
"""

helps['fleet updaterun list'] = """
    type: command
    short-summary: Lists a fleet's update runs.
    examples:
        - name: Show the details of an update run.
          text: az fleet updaterun list -g MyFleetResourceGroup -f MyFleetName
"""

helps['fleet updaterun delete'] = """
    type: command
    short-summary: Deletes an update run.
    examples:
        - name: Delete an update run.
          text: az fleet updaterun delete -g MyFleetResourceGroup -f MyFleetName -n NameofUpdateRun
"""

helps['fleet updaterun start'] = """
    type: command
    short-summary: Starts an update run.
    examples:
        - name: Start an update run.
          text: az fleet updaterun start -g MyFleetResourceGroup -f MyFleetName -n NameofUpdateRun
"""

helps['fleet updaterun stop'] = """
    type: command
    short-summary: Stops an update run.
    examples:
        - name: Stop an update run.
          text: az fleet updaterun stop -g MyFleetResourceGroup -f MyFleetName -n NameofUpdateRun
"""

helps['fleet updaterun skip'] = """
    type: command
    short-summary: Sets targets to be skipped within an UpdateRun.
    parameters:
        - name: --targets
          type: string array
          short-summary: Space-separated list of targets to skip.  Targets must be of the form 'targetType:targetName' such as Group:MyGroup. Valid target types are ('Member', 'Group', 'Stage', 'AfterStageWait'). The target type is case-sensitive.
    examples:
        - name: Set two targets to be skipped.
          text: az fleet updaterun skip -g MyFleetResourceGroup -f MyFleetName -n NameofUpdateRun --targets Group:my-group-name Stage:my-stage-name
"""

helps['fleet updaterun wait'] = """
    type: command
    short-summary: Wait for an update run resource to reach a desired state.
    long-summary: If an operation on an update run was interrupted or was started with `--no-wait`, use this command to wait for it to complete.
"""

helps['fleet updatestrategy'] = """
    type: group
    short-summary: Commands to manage update strategies.
"""

helps['fleet updatestrategy create'] = """
    type: command
    short-summary: Creates or updates an update strategy.
    parameters:
        - name: --stages
          type: string
          short-summary: Path to a JSON file that defines the update strategy.
    examples:
        - name: Create an update strategy from a JSON file.
          text: az fleet updatestrategy create -g MyFleetResourceGroup -f MyFleetName -n MyUpdateStrategy --stages MyUpdateStrategyFile.json
"""

helps['fleet updatestrategy show'] = """
    type: command
    short-summary: Shows an update strategy.
    examples:
        - name: Show the details of an update strategy.
          text: az fleet updatestrategy show -g MyFleetResourceGroup -f MyFleetName -n MyUpdateStrategy
"""

helps['fleet updatestrategy list'] = """
    type: command
    short-summary: Lists the fleet's update strategies.
    examples:
        - name: List all update strategies for a given fleet.
          text: az fleet updatestrategy list -g MyFleetResourceGroup -f MyFleetName
"""

helps['fleet updatestrategy delete'] = """
    type: command
    short-summary: Deletes a update strategy.
    examples:
        - name: Delete an update strategy.
          text: az fleet updatestrategy delete -g MyFleetResourceGroup -f MyFleetName -n MyUpdateStrategy
"""

helps['fleet updatestrategy wait'] = """
    type: command
    short-summary: Wait for a update strategy resource to reach a desired state.
    long-summary: If an operation on an update strategy was interrupted or was started with `--no-wait`, use this command to wait for it to complete.
"""
