# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

helps['devcenter admin'] = """
    type: group
    short-summary: "Manages DevCenter admin resources"
"""

helps['devcenter dev project'] = """
    type: group
    short-summary: Manage project with devcenter
"""

helps['devcenter dev project list'] = """
    type: command
    short-summary: "Lists all projects."
    examples:
      - name: Project_ListByDevCenter
        text: |-
               az devcenter project list --dev-center "{devCenter}" --dev-center-dns-suffix "devcenter.azure.com"
"""

helps['devcenter dev project show'] = """
    type: command
    short-summary: "Gets a project."
    examples:
      - name: Project_Get
        text: |-
               az devcenter project show --dev-center "{devCenter}" --dev-center-dns-suffix "devcenter.azure.com" \
--name "{projectName}"
"""

helps['devcenter dev pool'] = """
    type: group
    short-summary: Manage pool with devcenter
"""

helps['devcenter dev pool list'] = """
    type: command
    short-summary: "Lists available pools."
    examples:
      - name: listPools
        text: |-
               az devcenter pool list --dev-center "{devCenter}" --dev-center-dns-suffix "devcenter.azure.com" \
--project-name "{projectName}"
"""

helps['devcenter dev pool show'] = """
    type: command
    short-summary: "Gets a pool."
    examples:
      - name: Pools_Get
        text: |-
               az devcenter pool show --dev-center "{devCenter}" --dev-center-dns-suffix "devcenter.azure.com" --name \
"{poolName}" --project-name "{projectName}"
"""

helps['devcenter dev schedule'] = """
    type: group
    short-summary: Manage schedule with devcenter
"""

helps['devcenter dev schedule list'] = """
    type: command
    short-summary: "Lists available schedules for a pool."
    examples:
      - name: listSchedules
        text: |-
               az devcenter schedule list --dev-center "{devCenter}" --dev-center-dns-suffix "devcenter.azure.com" \
--pool-name "{poolName}" --project-name "{projectName}"
"""

helps['devcenter dev schedule show'] = """
    type: command
    short-summary: "Gets a schedule."
    examples:
      - name: Schedule_Get
        text: |-
               az devcenter schedule show --dev-center "{devCenter}" --dev-center-dns-suffix "devcenter.azure.com" \
--pool-name "{poolName}" --project-name "{projectName}" --name "{scheduleName}"
"""

helps['devcenter dev dev-box'] = """
    type: group
    short-summary: Manage dev box with devcenter
"""

helps['devcenter dev dev-box list'] = """
    type: command
    short-summary: "Lists Dev Boxes in the project for a particular user. And Lists Dev Boxes in the Dev Center for a \
particular user. And Lists Dev Boxes that the caller has access to in the DevCenter."
    examples:
      - name: DevBox_ListByUserByProject
        text: |-
               az devcenter dev-box list --dev-center "{devCenter}" --dev-center-dns-suffix "devcenter.azure.com" \
--project-name "{projectName}" --user-id "me"
      - name: DevBox_ListByUserByProject
        text: |-
               az devcenter dev-box list --dev-center "{devCenter}" --dev-center-dns-suffix "devcenter.azure.com" \
--user-id "me"
      - name: DevBox_List
        text: |-
               az devcenter dev-box list --dev-center "{devCenter}" --dev-center-dns-suffix "devcenter.azure.com"
"""

helps['devcenter dev dev-box show'] = """
    type: command
    short-summary: "Gets a Dev Box."
    examples:
      - name: getDevBoxForUser
        text: |-
               az devcenter dev-box show --name "MyDevBox" --dev-center "{devCenter}" --dev-center-dns-suffix \
"devcenter.azure.com" --project-name "{projectName}" --user-id "me"
"""

helps['devcenter dev dev-box create'] = """
    type: command
    short-summary: "Creates or updates a Dev Box."
    examples:
      - name: createDevBox
        text: |-
               az devcenter dev-box create --pool-name "LargeDevWorkStationPool" --name "MyDevBox" --dev-center \
"{devCenter}" --dev-center-dns-suffix "devcenter.azure.com" --project-name "{projectName}" --user-id "me"
"""

helps['devcenter dev dev-box delete'] = """
    type: command
    short-summary: "Deletes a Dev Box."
    examples:
      - name: deleteDevBox
        text: |-
               az devcenter dev-box delete --name "MyDevBox" --dev-center "{devCenter}" --dev-center-dns-suffix \
"devcenter.azure.com" --project-name "{projectName}" --user-id "me"
"""

helps['devcenter dev dev-box get-remote-connection'] = """
    type: command
    short-summary: "Gets RDP Connection info."
    examples:
      - name: DevBox_GetRemoteConnection
        text: |-
               az devcenter dev-box get-remote-connection --name "MyDevBox" --dev-center "{devCenter}" \
--dev-center-dns-suffix "devcenter.azure.com" --project-name "{projectName}" --user-id "me"
"""

helps['devcenter dev dev-box start'] = """
    type: command
    short-summary: "Starts a Dev Box."
    examples:
      - name: startDevBoxForUser
        text: |-
               az devcenter dev-box start --name "MyDevBox" --dev-center "{devCenter}" --dev-center-dns-suffix \
"devcenter.azure.com" --project-name "{projectName}" --user-id "me"
"""

helps['devcenter dev dev-box stop'] = """
    type: command
    short-summary: "Stops a Dev Box."
    examples:
      - name: stopDevBoxForUser
        text: |-
               az devcenter dev-box stop --name "MyDevBox" --dev-center "{devCenter}" --dev-center-dns-suffix \
"devcenter.azure.com" --project-name "{projectName}" --user-id "me"
"""

helps['devcenter dev dev-box wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the devcenter dev-box is met.
    examples:
      - name: Pause executing next line of CLI script until the devcenter dev-box is successfully created.
        text: |-
               az devcenter dev-box wait --name "MyDevBox" --dev-center "{devCenter}" --dev-center-dns-suffix \
"devcenter.azure.com" --project-name "{projectName}" --user-id "me" --created
      - name: Pause executing next line of CLI script until the devcenter dev-box is successfully deleted.
        text: |-
               az devcenter dev-box wait --name "MyDevBox" --dev-center "{devCenter}" --dev-center-dns-suffix \
"devcenter.azure.com" --project-name "{projectName}" --user-id "me" --deleted
"""

helps['devcenter dev environment'] = """
    type: group
    short-summary: Manage environment with devcenter
"""

helps['devcenter dev environment list'] = """
    type: command
    short-summary: "Lists the environments for a project."
    examples:
      - name: Environments_ListByProject
        text: |-
               az devcenter environment list --dev-center "{devCenter}" --dev-center-dns-suffix "devcenter.azure.com" \
--project-name "{projectName}"
"""

helps['devcenter dev environment show'] = """
    type: command
    short-summary: "Gets an environment."
    examples:
      - name: Environments_Get
        text: |-
               az devcenter environment show --dev-center "{devCenter}" --dev-center-dns-suffix "devcenter.azure.com" \
--name "{environmentName}" --project-name "{projectName}" --user-id "{userId}"
"""

helps['devcenter dev environment create'] = """
    type: command
    short-summary: "Create an environment."
    examples:
      - name: Environments_CreateByCatalogItem
        text: |-
               az devcenter environment create --description "Personal Dev Environment" --catalog-item-name \
"helloworld" --catalog-name "main" --environment-type "DevTest" --parameters "{\\"functionAppRuntime\\":\\"node\\",\\"s\
torageAccountType\\":\\"Standard_LRS\\"}" --dev-center "{devCenter}" --dev-center-dns-suffix "devcenter.azure.com" \
--name "{environmentName}" --project-name "{projectName}" --user-id "{userId}"
      - name: Environments_CreateWithAutoExpire
        text: |-
               az devcenter environment create --description "Personal Dev Environment" --catalog-item-name \
"helloworld" --catalog-name "main" --environment-type "DevTest" --parameters "{\\"functionAppRuntime\\":\\"node\\",\\"s\
torageAccountType\\":\\"Standard_LRS\\"}" --scheduled-tasks "{\\"autoExpire\\":{\\"type\\":\\"AutoExpire\\",\\"startTim\
e\\":\\"2022-01-01T00:01:00Z\\"}}" --dev-center "{devCenter}" --dev-center-dns-suffix "devcenter.azure.com" --name \
"{environmentName}" --project-name "{projectName}" --user-id "{userId}"
"""

helps['devcenter dev environment update'] = """
    type: command
    short-summary: "Partially updates an environment."
    examples:
      - name: Environments_Update
        text: |-
               az devcenter environment update --description "Personal Dev Environment 2" --dev-center "{devCenter}" \
--dev-center-dns-suffix "devcenter.azure.com" --name "{environmentName}" --project-name "{projectName}" --user-id \
"{userId}"
"""

helps['devcenter dev environment delete'] = """
    type: command
    short-summary: "Deletes an environment and all it's associated resources."
    examples:
      - name: Environments_Delete
        text: |-
               az devcenter environment delete --dev-center "{devCenter}" --dev-center-dns-suffix \
"devcenter.azure.com" --name "{environmentName}" --project-name "{projectName}" --user-id "{userId}"
"""

helps['devcenter dev environment list-by-project'] = """
    type: command
    short-summary: "Lists the environments for a project and user."
    examples:
      - name: Environments_ListByProject
        text: |-
               az devcenter environment list-by-project --dev-center "{devCenter}" --dev-center-dns-suffix \
"devcenter.azure.com" --project-name "{projectName}" --user-id "{userId}"
"""

helps['devcenter dev environment wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the devcenter environment is met.
    examples:
      - name: Pause executing next line of CLI script until the devcenter environment is successfully created.
        text: |-
               az devcenter environment wait --dev-center "{devCenter}" --dev-center-dns-suffix "devcenter.azure.com" \
--name "{environmentName}" --project-name "{projectName}" --user-id "{userId}" --created
      - name: Pause executing next line of CLI script until the devcenter environment is successfully updated.
        text: |-
               az devcenter environment wait --dev-center "{devCenter}" --dev-center-dns-suffix "devcenter.azure.com" \
--name "{environmentName}" --project-name "{projectName}" --user-id "{userId}" --updated
      - name: Pause executing next line of CLI script until the devcenter environment is successfully deleted.
        text: |-
               az devcenter environment wait --dev-center "{devCenter}" --dev-center-dns-suffix "devcenter.azure.com" \
--name "{environmentName}" --project-name "{projectName}" --user-id "{userId}" --deleted
"""

helps['devcenter dev action'] = """
    type: group
    short-summary: Manage action with devcenter
"""

helps['devcenter dev action list'] = """
    type: command
    short-summary: "Gets an environment's actions."
    examples:
      - name: Actions_ListByEnvironment
        text: |-
               az devcenter action list --dev-center "{devCenter}" --dev-center-dns-suffix "devcenter.azure.com" \
--environment-name "{environmentName}" --project-name "{projectName}" --user-id "{userId}"
"""

helps['devcenter dev action show'] = """
    type: command
    short-summary: "Gets an environment's deployment history."
    examples:
      - name: Actions_Get
        text: |-
               az devcenter action show --action-id "{actionId}" --dev-center "{devCenter}" --dev-center-dns-suffix \
"devcenter.azure.com" --environment-name "{environmentName}" --project-name "{projectName}" --user-id "{userId}"
"""

helps['devcenter dev action create'] = """
    type: command
    short-summary: "Creates and executes an action."
    examples:
      - name: Actions_Create
        text: |-
               az devcenter action create --action-id "deploy" --parameters "{\\"functionAppRuntime\\":\\"node\\",\\"st\
orageAccountType\\":\\"Standard_LRS\\"}" --dev-center "{devCenter}" --dev-center-dns-suffix "devcenter.azure.com" \
--environment-name "{environmentName}" --project-name "{projectName}" --user-id "{userId}"
"""

helps['devcenter dev action wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the devcenter action is met.
    examples:
      - name: Pause executing next line of CLI script until the devcenter action is successfully created.
        text: |-
               az devcenter action wait --action-id "{actionId}" --dev-center "{devCenter}" --dev-center-dns-suffix \
"devcenter.azure.com" --environment-name "{environmentName}" --project-name "{projectName}" --user-id "{userId}" \
--created
"""

helps['devcenter dev artifact'] = """
    type: group
    short-summary: Manage artifact with devcenter
"""

helps['devcenter dev artifact list'] = """
    type: command
    short-summary: "Lists the artifacts for an environment at a specified path, or returns the file at the path. And \
Lists the artifacts for an environment."
    examples:
      - name: Artifacts_Get
        text: |-
               az devcenter artifact list --artifact-path "{artifactPath}" --dev-center "{devCenter}" \
--dev-center-dns-suffix "devcenter.azure.com" --environment-name "{environmentName}" --project-name "{projectName}" \
--user-id "{userId}"
      - name: Artifacts_ListByEnvironment
        text: |-
               az devcenter artifact list --dev-center "{devCenter}" --dev-center-dns-suffix "devcenter.azure.com" \
--environment-name "{environmentName}" --project-name "{projectName}" --user-id "{userId}"
"""

helps['devcenter dev catalog-item'] = """
    type: group
    short-summary: Manage catalog item with devcenter
"""

helps['devcenter dev catalog-item list'] = """
    type: command
    short-summary: "Lists latest version of all catalog items available for a project."
    examples:
      - name: CatalogItems_ListByProject
        text: |-
               az devcenter catalog-item list --dev-center "{devCenter}" --dev-center-dns-suffix "devcenter.azure.com" \
--project-name "{projectName}"
"""

helps['devcenter dev catalog-item'] = """
    type: group
    short-summary: Manage catalog item with devcenter
"""

helps['devcenter dev catalog-item show'] = """
    type: command
    short-summary: "Get a catalog item from a project."
    examples:
      - name: CatalogItems_Get
        text: |-
               az devcenter catalog-item show --dev-center "{devCenter}" --dev-center-dns-suffix "devcenter.azure.com" \
--project-name "{projectName}"
"""

helps['devcenter dev catalog-item-version'] = """
    type: group
    short-summary: Manage catalog item version with devcenter
"""

helps['devcenter dev catalog-item-version list'] = """
    type: command
    short-summary: "List all versions of a catalog item from a project."
    examples:
      - name: CatalogItemVersions_ListByProject
        text: |-
               az devcenter catalog-item-version list --dev-center "{devCenter}" --dev-center-dns-suffix \
"devcenter.azure.com" --project-name "{projectName}"
"""

helps['devcenter dev catalog-item-version show'] = """
    type: command
    short-summary: "Get a specific catalog item version from a project."
    examples:
      - name: CatalogItemVersion_Get
        text: |-
               az devcenter catalog-item-version show --dev-center "{devCenter}" --dev-center-dns-suffix \
"devcenter.azure.com" --project-name "{projectName}"
"""

helps['devcenter dev environment-type'] = """
    type: group
    short-summary: Manage environment type with devcenter
"""

helps['devcenter dev environment-type list'] = """
    type: command
    short-summary: "Lists all environment types configured for a project."
    examples:
      - name: EnvironmentType_ListByProject
        text: |-
               az devcenter environment-type list --dev-center "{devCenter}" --dev-center-dns-suffix \
"devcenter.azure.com" --project-name "{projectName}"
"""

#control plane
helps['devcenter'] = '''
    type: group
    short-summary: Manage DevCenter
'''

helps['devcenter admin dev-center'] = """
    type: group
    short-summary: Manage dev center with devcenter
"""

helps['devcenter admin dev-center list'] = """
    type: command
    short-summary: "Lists all devcenters in a resource group. And Lists all devcenters in a subscription."
    examples:
      - name: DevCenters_ListByResourceGroup
        text: |-
               az devcenter admin dev-center list --resource-group "rg1"
      - name: DevCenters_ListBySubscription
        text: |-
               az devcenter admin dev-center list
"""

helps['devcenter admin dev-center show'] = """
    type: command
    short-summary: "Gets a devcenter."
    examples:
      - name: DevCenters_Get
        text: |-
               az devcenter admin dev-center show --name "Contoso" --resource-group "rg1"
"""

helps['devcenter admin dev-center create'] = """
    type: command
    short-summary: "Create a devcenter resource."
    examples:
      - name: DevCenters_Create
        text: |-
               az devcenter admin dev-center create --location "centralus" --tags CostCode="12345" --name "Contoso" \
--resource-group "rg1"
      - name: DevCenters_CreateWithUserIdentity
        text: |-
               az devcenter admin dev-center create --identity-type "UserAssigned" --user-assigned-identity \
"/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/identityGroup/providers/Microsoft.ManagedIdenti\
ty/userAssignedIdentities/testidentity1" --location "centralus" --tags CostCode="12345" --name "Contoso" \
--resource-group "rg1"
"""

helps['devcenter admin dev-center update'] = """
    type: command
    short-summary: "Partially updates a devcenter."
    examples:
      - name: DevCenters_Update
        text: |-
               az devcenter admin dev-center update --tags CostCode="12345" --name "Contoso" --resource-group "rg1"
"""

helps['devcenter admin dev-center delete'] = """
    type: command
    short-summary: "Deletes a devcenter."
    examples:
      - name: DevCenters_Delete
        text: |-
               az devcenter admin dev-center delete --name "Contoso" --resource-group "rg1"
"""

helps['devcenter admin dev-center attach-network'] = """
    type: command
    short-summary: "Attaches a network connection to a DevCenter."
    examples:
      - name: DevCenters_AttachNetwork
        text: |-
               az devcenter admin dev-center attach-network --dev-center-name "Contoso" --resource-group "rg1" --network-connection-id
"""

helps['devcenter admin dev-center detach-network'] = """
    type: command
    short-summary: "Detaches a network connection from a DevCenter."
    examples:
      - name: DevCenters_AttachNetwork
        text: |-
               az devcenter admin dev-center attach-network --dev-center-name "Contoso" --resource-group "rg1" --network-connection-id
"""

helps['devcenter admin dev-center wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the devcenter dev-center is met.
    examples:
      - name: Pause executing next line of CLI script until the devcenter dev-center is successfully created.
        text: |-
               az devcenter admin dev-center wait --name "Contoso" --resource-group "rg1" --created
      - name: Pause executing next line of CLI script until the devcenter dev-center is successfully updated.
        text: |-
               az devcenter admin dev-center wait --name "Contoso" --resource-group "rg1" --updated
      - name: Pause executing next line of CLI script until the devcenter dev-center is successfully deleted.
        text: |-
               az devcenter admin dev-center wait --name "Contoso" --resource-group "rg1" --deleted
"""

helps['devcenter admin project'] = """
    type: group
    short-summary: Manage project with devcenter
"""

helps['devcenter admin project list'] = """
    type: command
    short-summary: "Lists all projects in the resource group. And Lists all projects in the subscription."
    examples:
      - name: Projects_ListByResourceGroup
        text: |-
               az devcenter admin project list --resource-group "rg1"
      - name: Projects_ListBySubscription
        text: |-
               az devcenter admin project list
"""

helps['devcenter admin project show'] = """
    type: command
    short-summary: "Gets a specific project."
    examples:
      - name: Projects_Get
        text: |-
               az devcenter admin project show --name "{projectName}" --resource-group "rg1"
"""

helps['devcenter admin project create'] = """
    type: command
    short-summary: "Create a project."
    examples:
      - name: Projects_CreateOrUpdate
        text: |-
               az devcenter admin project create --location "centralus" --description "This is my first project." \
--dev-center-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.DevCenter/devcenters/{devCenterNa\
me}" --tags CostCenter="R&D" --name "{projectName}" --resource-group "rg1"
"""

helps['devcenter admin project update'] = """
    type: command
    short-summary: "Partially updates a project."
    examples:
      - name: Projects_Update
        text: |-
               az devcenter admin project update --description "This is my first project." --tags CostCenter="R&D" --name \
"{projectName}" --resource-group "rg1"
"""

helps['devcenter admin project delete'] = """
    type: command
    short-summary: "Deletes a project resource."
    examples:
      - name: Projects_Delete
        text: |-
               az devcenter admin project delete --name "{projectName}" --resource-group "rg1"
"""

helps['devcenter admin project wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the devcenter project is met.
    examples:
      - name: Pause executing next line of CLI script until the devcenter project is successfully created.
        text: |-
               az devcenter admin project wait --name "{projectName}" --resource-group "rg1" --created
      - name: Pause executing next line of CLI script until the devcenter project is successfully updated.
        text: |-
               az devcenter admin project wait --name "{projectName}" --resource-group "rg1" --updated
      - name: Pause executing next line of CLI script until the devcenter project is successfully deleted.
        text: |-
               az devcenter admin project wait --name "{projectName}" --resource-group "rg1" --deleted
"""

helps['devcenter admin attached-network'] = """
    type: group
    short-summary: Manage attached network with devcenter
"""

helps['devcenter admin attached-network list'] = """
    type: command
    short-summary: "Lists the attached NetworkConnections for a Project. And Lists the attached NetworkConnections for \
a DevCenter."
    examples:
      - name: AttachedNetworks_ListByProject
        text: |-
               az devcenter admin attached-network list --project-name "{projectName}" --resource-group "rg1"
      - name: AttachedNetworks_ListByDevCenter
        text: |-
               az devcenter admin attached-network list --dev-center-name "Contoso" --resource-group "rg1"
"""

helps['devcenter admin attached-network show'] = """
    type: command
    short-summary: "Gets an attached NetworkConnection. And Gets an attached NetworkConnection."
    examples:
      - name: AttachedNetworks_GetByProject
        text: |-
               az devcenter admin attached-network show --name "{attachedNetworkConnectionName}" \
--project-name "{projectName}" --resource-group "rg1"
      - name: AttachedNetworks_GetByDevCenter
        text: |-
               az devcenter admin attached-network show --name "{attachedNetworkConnectionName}" \
--dev-center-name "Contoso" --resource-group "rg1"
"""

helps['devcenter admin attached-network create'] = """
    type: command
    short-summary: "Create an attached NetworkConnection."
    examples:
      - name: AttachedNetworks_Create
        text: |-
               az devcenter admin attached-network create --attached-network-connection-name "{attachedNetworkConnectionName}" \
--network-connection-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.DevCenter/networ\
kConnections/{networkConnectionName}" --dev-center-name "Contoso" --resource-group "rg1"
"""

helps['devcenter admin attached-network update'] = """
    type: command
    short-summary: "Update an attached NetworkConnection."
"""

helps['devcenter admin attached-network delete'] = """
    type: command
    short-summary: "Un-attach a NetworkConnection."
    examples:
      - name: AttachedNetworks_Delete
        text: |-
               az devcenter admin attached-network delete --attached-network-connection-name "{attachedNetworkConnectionName}" \
--dev-center-name "Contoso" --resource-group "rg1"
"""

helps['devcenter admin attached-network wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the devcenter admin attached-network is met.
    examples:
      - name: Pause executing next line of CLI script until the devcenter admin attached-network is successfully created.
        text: |-
               az devcenter admin attached-network wait --attached-network-connection-name "{attachedNetworkConnectionName}" \
--dev-center-name "Contoso" --resource-group "rg1" --created
      - name: Pause executing next line of CLI script until the devcenter admin attached-network is successfully updated.
        text: |-
               az devcenter admin attached-network wait --attached-network-connection-name "{attachedNetworkConnectionName}" \
--dev-center-name "Contoso" --resource-group "rg1" --updated
      - name: Pause executing next line of CLI script until the devcenter admin attached-network is successfully deleted.
        text: |-
               az devcenter admin attached-network wait --attached-network-connection-name "{attachedNetworkConnectionName}" \
--dev-center-name "Contoso" --resource-group "rg1" --deleted
"""

helps['devcenter admin environment-type'] = """
    type: group
    short-summary: Manage environment type with devcenter
"""

helps['devcenter admin environment-type list'] = """
    type: command
    short-summary: "Lists all environment types configured for this project. And Lists environment types for the \
devcenter."
    examples:
      - name: EnvironmentTypes_ListByProject
        text: |-
               az devcenter admin environment-type list --project-name "Contoso" --resource-group "rg1"
      - name: EnvironmentTypes_ListByDevCenter
        text: |-
               az devcenter environment-type list --dev-center-name "Contoso" --resource-group "rg1"
"""

helps['devcenter admin environment-type show'] = """
    type: command
    short-summary: "Gets an environment type."
    examples:
      - name: EnvironmentTypes_Get
        text: |-
               az devcenter admin environment-type show --dev-center-name "Contoso" --name "{environmentTypeName}" \
--resource-group "rg1"
"""

helps['devcenter admin environment-type create'] = """
    type: command
    short-summary: "Create an environment type."
    examples:
      - name: EnvironmentTypes_CreateOrUpdate
        text: |-
               az devcenter admin environment-type create --description "Developer/Testing environment" --dev-center-name \
"Contoso" --name "{environmentTypeName}" --resource-group "rg1"
"""

helps['devcenter admin environment-type update'] = """
    type: command
    short-summary: "Partially updates an environment type."
    examples:
      - name: EnvironmentTypes_Update
        text: |-
               az devcenter admin environment-type update --description "Updated description" --dev-center-name "Contoso" \
--name "{environmentTypeName}" --resource-group "rg1"
"""

helps['devcenter admin environment-type delete'] = """
    type: command
    short-summary: "Deletes an environment type."
    examples:
      - name: EnvironmentTypes_Delete
        text: |-
               az devcenter admin environment-type delete --dev-center-name "Contoso" --name "{environmentTypeName}" \
--resource-group "rg1"
"""

helps['devcenter admin environment-type wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the devcenter environment-type is met.
    examples:
      - name: Pause executing next line of CLI script until the devcenter environment-type is successfully deleted.
        text: |-
               az devcenter admin environment-type wait --dev-center-name "Contoso" --name "{environmentTypeName}" \
--resource-group "rg1" --deleted
"""

helps['devcenter admin project-environment-type'] = """
    type: group
    short-summary: Manage environment types for a given Project
"""

helps['devcenter admin project-environment-type list'] = """
    type: command
    short-summary: "Lists all environment types configured for this project."
    examples:
      - name: EnvironmentTypes_ListByProject
        text: |-
               az devcenter admin project-environment-type list --project-name "Contoso" --resource-group "rg1"
      - name: EnvironmentTypes_ListByDevCenter
        text: |-
               az devcenter project-environment-type list --dev-center-name "Contoso" --resource-group "rg1"
"""

helps['devcenter admin project-environment-type show'] = """
    type: command
    short-summary: "Gets an environment type for a Project."
    examples:
      - name: EnvironmentTypes_Get
        text: |-
               az devcenter admin project-environment-type show --dev-center-name "Contoso" --name "{environmentTypeName}" \
--resource-group "rg1"
"""

helps['devcenter admin project-environment-type create'] = """
    type: command
    short-summary: "Create an environment type for a Project."
    examples:
      - name: EnvironmentTypes_CreateOrUpdate
        text: |-
               az devcenter admin environment-type create --description "Developer/Testing environment" --dev-center-name \
"Contoso" --name "{environmentTypeName}" --resource-group "rg1"
"""

helps['devcenter admin project-environment-type update'] = """
    type: command
    short-summary: "Partially updates an environment type for a Project."
    examples:
      - name: EnvironmentTypes_Update
        text: |-
               az devcenter admin project-environment-type update --description "Updated description" --dev-center-name "Contoso" \
--name "{environmentTypeName}" --resource-group "rg1"
"""

helps['devcenter admin project-environment-type delete'] = """
    type: command
    short-summary: "Deletes an environment type in a Project."
    examples:
      - name: EnvironmentTypes_Delete
        text: |-
               az devcenter admin project-environment-type delete --dev-center-name "Contoso" --name "{environmentTypeName}" \
--resource-group "rg1"
"""

helps['devcenter admin project-environment-type wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the devcenter environment-type is met.
    examples:
      - name: Pause executing next line of CLI script until the devcenter environment-type is successfully deleted.
        text: |-
               az devcenter admin project-environment-type wait --dev-center-name "Contoso" --name "{environmentTypeName}" \
--resource-group "rg1" --deleted
"""

helps['devcenter admin catalog'] = """
    type: group
    short-summary: Manage catalog with devcenter
"""

helps['devcenter admin catalog list'] = """
    type: command
    short-summary: "Lists catalogs for a devcenter."
    examples:
      - name: Catalogs_ListByDevCenter
        text: |-
               az devcenter admin catalog list --dev-center-name "Contoso" --resource-group "rg1"
"""

helps['devcenter admin catalog show'] = """
    type: command
    short-summary: "Gets a catalog."
    examples:
      - name: Catalogs_Get
        text: |-
               az devcenter admin catalog show --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
"""

helps['devcenter admin catalog create'] = """
    type: command
    short-summary: "Create a catalog."
    parameters:
      - name: --git-hub
        short-summary: "Properties for a GitHub catalog type."
        long-summary: |
            Usage: --git-hub uri=XX branch=XX secret-identifier=XX path=XX

            uri: Git URI.
            branch: Git branch.
            secret-identifier: A reference to the Key Vault secret containing a security token to authenticate to a \
Git repository.
            path: The folder where the catalog items can be found inside the repository.
      - name: --ado-git
        short-summary: "Properties for an Azure DevOps catalog type."
        long-summary: |
            Usage: --ado-git uri=XX branch=XX secret-identifier=XX path=XX

            uri: Git URI.
            branch: Git branch.
            secret-identifier: A reference to the Key Vault secret containing a security token to authenticate to a \
Git repository.
            path: The folder where the catalog items can be found inside the repository.
    examples:
      - name: Catalogs_CreateOrUpdateAdo
        text: |-
               az devcenter admin catalog create --ado-git path="/templates" branch="main" secret-identifier="https://contosokv\
.vault.azure.net/secrets/CentralRepoPat" uri="https://contoso@dev.azure.com/contoso/contosoOrg/_git/centralrepo-fakecon\
toso" --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
      - name: Catalogs_CreateOrUpdateGitHub
        text: |-
               az devcenter admin catalog create --git-hub path="/templates" branch="main" secret-identifier="https://contosokv\
.vault.azure.net/secrets/CentralRepoPat" uri="https://github.com/Contoso/centralrepo-fake.git" --name "{catalogName}" \
--dev-center-name "Contoso" --resource-group "rg1"
"""

helps['devcenter admin catalog update'] = """
    type: command
    short-summary: "Partially updates a catalog."
    parameters:
      - name: --git-hub
        short-summary: "Properties for a GitHub catalog type."
        long-summary: |
            Usage: --git-hub uri=XX branch=XX secret-identifier=XX path=XX

            uri: Git URI.
            branch: Git branch.
            secret-identifier: A reference to the Key Vault secret containing a security token to authenticate to a \
Git repository.
            path: The folder where the catalog items can be found inside the repository.
      - name: --ado-git
        short-summary: "Properties for an Azure DevOps catalog type."
        long-summary: |
            Usage: --ado-git uri=XX branch=XX secret-identifier=XX path=XX

            uri: Git URI.
            branch: Git branch.
            secret-identifier: A reference to the Key Vault secret containing a security token to authenticate to a \
Git repository.
            path: The folder where the catalog items can be found inside the repository.
    examples:
      - name: Catalogs_Update
        text: |-
               az devcenter admin catalog update --git-hub path="/environments" --name "{catalogName}" --dev-center-name \
"Contoso" --resource-group "rg1"
"""

helps['devcenter admin catalog delete'] = """
    type: command
    short-summary: "Deletes a catalog resource."
    examples:
      - name: Catalogs_Delete
        text: |-
               az devcenter admin catalog delete --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
"""

helps['devcenter admin catalog sync'] = """
    type: command
    short-summary: "Syncs templates for a template source."
    examples:
      - name: Catalogs_Sync
        text: |-
               az devcenter admin catalog sync --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
"""

helps['devcenter admin catalog wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the devcenter catalog is met.
    examples:
      - name: Pause executing next line of CLI script until the devcenter catalog is successfully created.
        text: |-
               az devcenter admin catalog wait --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1" \
--created
      - name: Pause executing next line of CLI script until the devcenter catalog is successfully updated.
        text: |-
               az devcenter admin catalog wait --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1" \
--updated
      - name: Pause executing next line of CLI script until the devcenter catalog is successfully deleted.
        text: |-
               az devcenter admin catalog wait --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1" \
--deleted
"""

helps['devcenter admin devbox-definition'] = """
    type: group
    short-summary: Manage Dev Box definition with devcenter
"""

helps['devcenter admin devbox-definition list'] = """
    type: command
    short-summary: "List Dev Box definitions for a devcenter."
    examples:
      - name: DevBoxDefinitions_ListByDevCenter
        text: |-
               az devcenter admin devbox-definition list --dev-center-name "Contoso" --resource-group "rg1"
"""

helps['devcenter admin devbox-definition show'] = """
    type: command
    short-summary: "Gets a Dev Box definition."
    examples:
      - name: DevBoxDefinitions_Get
        text: |-
               az devcenter admin devbox-definition show --name "WebDevBox" --dev-center-name "Contoso" --resource-group \
"rg1"
"""

helps['devcenter admin devbox-definition create'] = """
    type: command
    short-summary: "Create a Dev Box definition."
    parameters:
      - name: --image-reference
        short-summary: "Image reference information."
        long-summary: |
            Usage: --image-reference id=XX

            id: Image resource ID.
    examples:
      - name: DevBoxDefinitions_Create
        text: |-
               az devcenter admin devbox-definition create --location "centralus" --image-reference \
id="/subscriptions/0ac520ee-14c0-480f-b6c9-0a90c58ffff/resourceGroups/Example/providers/Microsoft.DevCenter/galleries/con\
tosogallery/images/exampleImage/version/1.0.0" --dev-box-definition-name "WebDevBox" --dev-center-name "Contoso" \
--resource-group "rg1"
"""

helps['devcenter admin devbox-definition update'] = """
    type: command
    short-summary: "Partially updates a Dev Box definition."
    parameters:
      - name: --image-reference
        short-summary: "Image reference information."
        long-summary: |
            Usage: --image-reference

            id: Image resource ID.
    examples:
      - name: DevBoxDefinitions_Patch
        text: |-
               az devcenter admin devbox-definition update --image-reference id="/subscriptions/0ac520ee-14c0-480f-b6c9-0a90c5\
8ffff/resourceGroups/Example/providers/Microsoft.DevCenter/galleries/contosogallery/images/exampleImage/version/2.0.0" \
--dev-box-definition-name "WebDevBox" --dev-center-name "Contoso" --resource-group "rg1"
"""

helps['devcenter admin devbox-definition delete'] = """
    type: command
    short-summary: "Deletes a Dev Box definition."
    examples:
      - name: DevBoxDefinitions_Delete
        text: |-
               az devcenter admin devbox-definition delete --name "WebDevBox" --dev-center-name "Contoso" --resource-group \
"rg1"
"""

helps['devcenter admin devbox-definition wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the devcenter admin devbox-definition is met.
    examples:
      - name: Pause executing next line of CLI script until the devcenter admin devbox-definition is successfully created.
        text: |-
               az devcenter admin devbox-definition wait --name "WebDevBox" --dev-center-name "Contoso" --resource-group \
"rg1" --created
      - name: Pause executing next line of CLI script until the devcenter admin devbox-definition is successfully updated.
        text: |-
               az devcenter admin devbox-definition wait --name "WebDevBox" --dev-center-name "Contoso" --resource-group \
"rg1" --updated
      - name: Pause executing next line of CLI script until the devcenter admin devbox-definition is successfully deleted.
        text: |-
               az devcenter admin devbox-definition wait --name "WebDevBox" --dev-center-name "Contoso" --resource-group \
"rg1" --deleted
"""

helps['devcenter admin usage'] = """
    type: group
    short-summary: Manage usage with devcenter
"""

helps['devcenter admin usage list'] = """
    type: command
    short-summary: "Lists the current usages and limits in this location for the provided subscription."
    examples:
      - name: listUsages
        text: |-
               az devcenter usage list --location "westus"
"""

helps['devcenter admin sku'] = """
    type: group
    short-summary: Manage sku with devcenter
"""

helps['devcenter admin sku list'] = """
    type: command
    short-summary: "Lists the Microsoft.SKUs available in a subscription."
    examples:
      - name: Skus_ListBySubscription
        text: |-
               az devcenter admin sku list
"""

helps['devcenter admin pool'] = """
    type: group
    short-summary: Manage pool with devcenter
"""

helps['devcenter admin pool list'] = """
    type: command
    short-summary: "Lists pools for a project."
    examples:
      - name: Pools_ListByProject
        text: |-
               az devcenter admin pool list --project-name "{projectName}" --resource-group "rg1"
"""

helps['devcenter admin pool show'] = """
    type: command
    short-summary: "Gets a machine pool."
    examples:
      - name: Pools_Get
        text: |-
               az devcenter admin pool show --name "{poolName}" --project-name "{projectName}" --resource-group "rg1"
"""

helps['devcenter admin pool create'] = """
    type: command
    short-summary: "Create a machine pool."
    examples:
      - name: Pools_CreateOrUpdate
        text: |-
               az devcenter pool create --location "centralus" --dev-box-definition-name "WebDevBox" \
--network-connection-name "Network1-westus2" --pool-name "{poolName}" --project-name "{projectName}" --resource-group \
"rg1" --license-type Windows_Client --local-administrator Enabled
"""

helps['devcenter admin pool update'] = """
    type: command
    short-summary: "Partially updates a machine pool."
    examples:
      - name: Pools_Update
        text: |-
               az devcenter pool update --dev-box-definition-name "WebDevBox2" --pool-name "{poolName}" --project-name \
"{projectName}" --resource-group "rg1"
"""

helps['devcenter admin pool delete'] = """
    type: command
    short-summary: "Deletes a machine pool."
    examples:
      - name: Pools_Delete
        text: |-
               az devcenter admin pool delete --name "poolName" --project-name "{projectName}" --resource-group "rg1"
"""

helps['devcenter admin pool wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the devcenter pool is met.
    examples:
      - name: Pause executing next line of CLI script until the devcenter pool is successfully created.
        text: |-
               az devcenter admin pool wait --name "{poolName}" --project-name "{projectName}" --resource-group "rg1" \
--created
      - name: Pause executing next line of CLI script until the devcenter pool is successfully updated.
        text: |-
               az devcenter admin pool wait --name "{poolName}" --project-name "{projectName}" --resource-group "rg1" \
--updated
      - name: Pause executing next line of CLI script until the devcenter pool is successfully deleted.
        text: |-
               az devcenter admin pool wait --name "{poolName}" --project-name "{projectName}" --resource-group "rg1" \
--deleted
"""

helps['devcenter admin schedule'] = """
    type: group
    short-summary: Manage schedule with devcenter
"""

helps['devcenter admin schedule list'] = """
    type: command
    short-summary: "Lists schedules for a pool."
    examples:
      - name: Schedules_ListByPool
        text: |-
               az devcenter admin schedule list --pool-name "DevPool" --project-name "TestProject" --resource-group "rg1"
"""

helps['devcenter admin schedule show'] = """
    type: command
    short-summary: "Gets a schedule resource."
    examples:
      - name: Schedules_GetByPool
        text: |-
               az devcenter admin schedule show --pool-name "DevPool" --project-name "TestProject" --resource-group "rg1" \
--name "autoShutdown"
"""

helps['devcenter admin schedule create'] = """
    type: command
    short-summary: "Create a Schedule."
    examples:
      - name: Schedules_CreateDailyShutdownPoolSchedule
        text: |-
               az devcenter admin schedule create --state "Enabled" --time "17:30" --time-zone "America/Los_Angeles" \
--pool-name "DevPool" --project-name "DevProject" --resource-group "rg1" --name "autoShutdown"
"""

helps['devcenter admin schedule update'] = """
    type: command
    short-summary: "Partially updates a Scheduled."
    examples:
      - name: Schedules_Update
        text: |-
               az devcenter admin schedule update --time "18:00" --pool-name "DevPool" --project-name "TestProject" \
--resource-group "rg1" --name "autoShutdown"
"""

helps['devcenter admin schedule delete'] = """
    type: command
    short-summary: "Deletes a Scheduled."
    examples:
      - name: Schedules_Delete
        text: |-
               az devcenter admin schedule delete --pool-name "DevPool" --project-name "TestProject" --resource-group "rg1" \
--name "autoShutdown"
"""

helps['devcenter admin schedule wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the devcenter admin schedule is met.
    examples:
      - name: Pause executing next line of CLI script until the devcenter admin schedule is successfully created.
        text: |-
               az devcenter admin schedule wait --pool-name "DevPool" --project-name "TestProject" --resource-group "rg1" \
--name "autoShutdown" --created
      - name: Pause executing next line of CLI script until the devcenter admin schedule is successfully updated.
        text: |-
               az devcenter admin schedule wait --pool-name "DevPool" --project-name "TestProject" --resource-group "rg1" \
--name "autoShutdown" --updated
      - name: Pause executing next line of CLI script until the devcenter admin schedule is successfully deleted.
        text: |-
               az devcenter admin schedule wait --pool-name "DevPool" --project-name "TestProject" --resource-group "rg1" \
--name "autoShutdown" --deleted
"""


helps['devcenter admin network-connection'] = """
    type: group
    short-summary: Manage network setting with devcenter
"""

helps['devcenter admin network-connection list'] = """
    type: command
    short-summary: "Lists network settings in a resource group And Lists network settings in a subscription."
    examples:
      - name: NetworkConnections_ListByResourceGroup
        text: |-
               az devcenter admin network-connection list --resource-group "rg1"
      - name: NetworkConnections_ListBySubscription
        text: |-
               az devcenter admin network-connection list
"""

helps['devcenter admin network-connection show'] = """
    type: command
    short-summary: "Gets a network settings resource."
    examples:
      - name: NetworkConnections_Get
        text: |- 
               az devcenter admin network-connection show --name "{networkSettingName}" --resource-group "rg1"
"""

helps['devcenter admin network-connection create'] = """
    type: command
    short-summary: "Create a Network Settings resource."
    examples:
      - name: NetworkConnections_CreateHybridJoined
        text: |-
               az devcenter admin network-connection create --location "centralus" --domain-join-type "HybridAzureADJoin" \
--domain-name "mydomaincontroller.local" --domain-password "Password value for user" --domain-username \
"testuser@mydomaincontroller.local" --networking-resource-group-id "/subscriptions/00000000-0000-0000-0000-000000000000\
/resourceGroups/ExampleRG" --subnet-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/ExampleRG/pr\
oviders/Microsoft.Network/virtualNetworks/ExampleVNet/subnets/default" --name "{networkSettingName}" --resource-group \
"rg1"
      - name: NetworkConnections_CreateAzureJoined
        text: |-
               az devcenter admin network-connection create --location "centralus" --domain-join-type "AzureADJoin" \
--networking-resource-group-name "NetworkInterfacesRG" --subnet-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/ExampleRG/pr\
oviders/Microsoft.Network/virtualNetworks/ExampleVNet/subnets/default" --name "{networkSettingName}" --resource-group \
"rg1"
"""

helps['devcenter admin network-connection update'] = """
    type: command
    short-summary: "Partially updates Network Settings."
    examples:
      - name: NetworkConnections_Update
        text: |-
               az devcenter admin network-connection update --domain-password "New Password value for user" --name \
"{networkSettingName}" --resource-group "rg1"
"""

helps['devcenter admin network-connection delete'] = """
    type: command
    short-summary: "Deletes a Network Settings resource."
    examples:
      - name: NetworkConnections_Delete
        text: |-
               az devcenter admin network-connection delete --name "{networkSettingName}" --resource-group "rg1"
"""

helps['devcenter admin network-connection show-health-detail'] = """
    type: command
    short-summary: "Gets health check status details."
    examples:
      - name: NetworkConnections_GetHealthDetails
        text: |-
               az devcenter admin network-connection show-health-detail --name "{networkSettingName}" --resource-group "rg1"
"""

helps['devcenter admin network-connection wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the devcenter network-setting is met.
    examples:
      - name: Pause executing next line of CLI script until the devcenter network-setting is successfully created.
        text: |-
               az devcenter admin network-connection wait --name "{networkSettingName}" --resource-group "rg1" --created
      - name: Pause executing next line of CLI script until the devcenter network-setting is successfully updated.
        text: |-
               az devcenter admin network-connection wait --name "{networkSettingName}" --resource-group "rg1" --updated
      - name: Pause executing next line of CLI script until the devcenter network-setting is successfully deleted.
        text: |-
               az devcenter admin network-connection wait --name "{networkSettingName}" --resource-group "rg1" --deleted
"""

helps['devcenter admin gallery'] = """
    type: group
    short-summary: Manage gallery with devcenter
"""

helps['devcenter admin gallery list'] = """
    type: command
    short-summary: "Lists galleries for a devcenter."
    examples:
      - name: Galleries_ListByDevCenter
        text: |-
               az devcenter gallery list --dev-center-name "Contoso" --resource-group "rg1"
"""

helps['devcenter admin gallery show'] = """
    type: command
    short-summary: "Gets a gallery."
    examples:
      - name: Galleries_Get
        text: |-
               az devcenter gallery show --dev-center-name "Contoso" --name "{galleryName}" --resource-group "rg1"
"""

helps['devcenter admin gallery create'] = """
    type: command
    short-summary: "Create a gallery."
    examples:
      - name: Galleries_CreateOrUpdate
        text: |-
               az devcenter gallery create --gallery-resource-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/prov\
iders/Microsoft.Compute/galleries/{galleryName}" --dev-center-name "Contoso" --name "{galleryName}" --resource-group \
"rg1"
"""

helps['devcenter admin gallery update'] = """
    type: command
    short-summary: "Update a gallery."
"""

helps['devcenter admin gallery delete'] = """
    type: command
    short-summary: "Deletes a gallery resource."
    examples:
      - name: Galleries_Delete
        text: |-
               az devcenter gallery delete --dev-center-name "Contoso" --name "{galleryName}" --resource-group "rg1"
"""

helps['devcenter admin gallery wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the devcenter gallery is met.
    examples:
      - name: Pause executing next line of CLI script until the devcenter gallery is successfully created.
        text: |-
               az devcenter gallery wait --dev-center-name "Contoso" --name "{galleryName}" --resource-group "rg1" \
--created
      - name: Pause executing next line of CLI script until the devcenter gallery is successfully updated.
        text: |-
               az devcenter gallery wait --dev-center-name "Contoso" --name "{galleryName}" --resource-group "rg1" \
--updated
      - name: Pause executing next line of CLI script until the devcenter gallery is successfully deleted.
        text: |-
               az devcenter gallery wait --dev-center-name "Contoso" --name "{galleryName}" --resource-group "rg1" \
--deleted
"""

helps['devcenter admin image'] = """
    type: group
    short-summary: Manage image with devcenter
"""

helps['devcenter admin image list'] = """
    type: command
    short-summary: "Lists images for a gallery. And Lists images for a devcenter."
    examples:
      - name: Images_ListByGallery
        text: |-
               az devcenter image list --dev-center-name "Contoso" --gallery-name "DevGallery" --resource-group "rg1"
      - name: Images_ListByDevCenter
        text: |-
               az devcenter image list --dev-center-name "Contoso" --resource-group "rg1"
"""

helps['devcenter admin image show'] = """
    type: command
    short-summary: "Gets a gallery image."
    examples:
      - name: Images_Get
        text: |-
               az devcenter image show --dev-center-name "Contoso" --gallery-name "DefaultDevGallery" --name \
"{imageName}" --resource-group "rg1"
"""

helps['devcenter admin image-version'] = """
    type: group
    short-summary: Manage image version with devcenter
"""

helps['devcenter admin image-version list'] = """
    type: command
    short-summary: "Lists versions for an image."
    examples:
      - name: ImageVersions_ListByImage
        text: |-
               az devcenter image-version list --dev-center-name "Contoso" --gallery-name "DefaultDevGallery" \
--image-name "Win11" --resource-group "rg1"
"""

helps['devcenter admin image-version show'] = """
    type: command
    short-summary: "Gets an image version."
    examples:
      - name: Versions_Get
        text: |-
               az devcenter image-version show --dev-center-name "Contoso" --gallery-name "DefaultDevGallery" \
--image-name "Win11" --resource-group "rg1" --version-name "{versionName}"
"""