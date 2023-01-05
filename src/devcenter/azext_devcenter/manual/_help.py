# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

helps[
    "devcenter admin"
] = """
    type: group
    short-summary: "Manages devcenter admin resources"
"""

helps[
    "devcenter dev"
] = """
    type: group
    short-summary: "Manages devcenter developer resources"
"""
helps[
    "devcenter dev project"
] = """
    type: group
    short-summary: Manage project with devcenter
"""

helps[
    "devcenter dev project list"
] = """
    type: command
    short-summary: "Lists all projects."
    examples:
      - name: Project_ListByDevCenter
        text: |-
               az devcenter dev project list --dev-center-name "{devCenterName}"
"""

helps[
    "devcenter dev project show"
] = """
    type: command
    short-summary: "Gets a project."
    examples:
      - name: Project_Get
        text: |-
               az devcenter dev project show --dev-center-name "{devCenterName}" \
--name "{projectName}"
"""

helps[
    "devcenter dev pool"
] = """
    type: group
    short-summary: Manage pool with devcenter
"""

helps[
    "devcenter dev pool list"
] = """
    type: command
    short-summary: "Lists available pools."
    examples:
      - name: listPools
        text: |-
               az devcenter dev pool list --dev-center-name "{devCenterName}" \
--project-name "{projectName}"
"""

helps[
    "devcenter dev pool show"
] = """
    type: command
    short-summary: "Gets a pool."
    examples:
      - name: Pools_Get
        text: |-
               az devcenter dev pool show --dev-center-name "{devCenterName}" --name \
"{poolName}" --project-name "{projectName}"
"""

helps[
    "devcenter dev schedule"
] = """
    type: group
    short-summary: Manage schedule with devcenter
"""

helps[
    "devcenter dev schedule list"
] = """
    type: command
    short-summary: "Lists available schedules for a pool."
    examples:
      - name: listSchedules
        text: |-
               az devcenter dev schedule list --dev-center-name "{devCenterName}" \
--pool-name "{poolName}" --project-name "{projectName}"
"""

helps[
    "devcenter dev schedule show"
] = """
    type: command
    short-summary: "Gets a schedule."
    examples:
      - name: Schedule_Get
        text: |-
               az devcenter dev schedule show --dev-center-name "{devCenterName}" \
--pool-name "{poolName}" --project-name "{projectName}" --name "{scheduleName}"
"""

helps[
    "devcenter dev dev-box"
] = """
    type: group
    short-summary: Manage dev box with devcenter
"""

helps[
    "devcenter dev dev-box list"
] = """
    type: command
    short-summary: "Lists dev boxes in the project for a particular user, lists dev boxes in the dev center for a \
particular user, or lists dev boxes that the caller has access to in the dev center."
    examples:
      - name: DevBox_ListByUserByProject
        text: |-
               az devcenter dev dev-box list --dev-center-name "{devCenterName}" \
--project-name "{projectName}" --user-id "me"
      - name: DevBox_ListByUser
        text: |-
               az devcenter dev dev-box list --dev-center-name "{devCenterName}" \
--user-id "me"
      - name: DevBox_List
        text: |-
               az devcenter dev dev-box list --dev-center-name "{devCenterName}"
"""

helps[
    "devcenter dev dev-box show"
] = """
    type: command
    short-summary: "Gets a dev box."
    examples:
      - name: getDevBoxForUser
        text: |-
               az devcenter dev dev-box show --name "MyDevBox" --dev-center-name "{devCenterName}" \
               --project-name "{projectName}" --user-id "me"
"""

helps[
    "devcenter dev dev-box create"
] = """
    type: command
    short-summary: "Creates or updates a dev box."
    examples:
      - name: createDevBox
        text: |-
               az devcenter dev dev-box create --pool-name "LargeDevWorkStationPool" --name "MyDevBox" --dev-center-name \
"{devCenterName}" --project-name "{projectName}" --user-id "me"
"""

helps[
    "devcenter dev dev-box delete"
] = """
    type: command
    short-summary: "Deletes a dev box."
    examples:
      - name: deleteDevBox
        text: |-
               az devcenter dev dev-box delete --name "MyDevBox" --dev-center-name "{devCenterName}"  \
               --project-name "{projectName}" --user-id "me"
"""

helps[
    "devcenter dev dev-box show-remote-connection"
] = """
    type: command
    short-summary: "Gets Connection info."
    examples:
      - name: DevBox_GetRemoteConnection
        text: |-
               az devcenter dev dev-box show-remote-connection --name "MyDevBox" --dev-center-name "{devCenterName}" \
               --project-name "{projectName}" --user-id "me"
"""

helps[
    "devcenter dev dev-box start"
] = """
    type: command
    short-summary: "Starts a dev box."
    examples:
      - name: startDevBoxForUser
        text: |-
               az devcenter dev dev-box start --name "MyDevBox" --dev-center-name "{devCenterName}" \
               --project-name "{projectName}" --user-id "me"
"""

helps[
    "devcenter dev dev-box stop"
] = """
    type: command
    short-summary: "Stops a dev box."
    examples:
      - name: stopDevBoxForUser
        text: |-
               az devcenter dev dev-box stop --name "MyDevBox" --dev-center-name "{devCenterName}" \
               --project-name "{projectName}" --user-id "me"
"""

helps[
    "devcenter dev environment"
] = """
    type: group
    short-summary: Manage environment with devcenter
"""

helps[
    "devcenter dev environment list"
] = """
    type: command
    short-summary: "Lists the environments for a project."
    examples:
      - name: Environments_ListByProject
        text: |-
              az devcenter dev environment list --dev-center-name "{devCenterName}" \
--project-name "{projectName}"
"""

helps[
    "devcenter dev environment show"
] = """
    type: command
    short-summary: "Gets an environment."
    examples:
      - name: Environments_Get
        text: |-
              az devcenter dev environment show --dev-center-name "{devCenterName}" \
--name "{environmentName}" --project-name "{projectName}" --user-id "{userId}"
"""

helps[
    "devcenter dev environment create"
] = """
    type: command
    short-summary: "Create an environment."
    examples:
      - name: Environments_CreateByCatalogItem
        text: |-
              az devcenter dev environment create --description "Personal Dev Environment" --catalog-item-name \
"helloworld" --catalog-name "main" --environment-type "DevTest" --parameters "{\\"functionAppRuntime\\":\\"node\\",\\"s\
torageAccountType\\":\\"Standard_LRS\\"}" --dev-center-name "{devCenterName}" \
--name "{environmentName}" --project-name "{projectName}" --user-id "{userId}"
      - name: Environments_CreateWithAutoExpire
        text: |-
              az devcenter dev environment create --description "Personal Dev Environment" --catalog-item-name \
"helloworld" --catalog-name "main" --environment-type "DevTest" --parameters "{\\"functionAppRuntime\\":\\"node\\",\\"s\
torageAccountType\\":\\"Standard_LRS\\"}" --scheduled-tasks "{\\"autoExpire\\":{\\"type\\":\\"AutoExpire\\",\\"startTim\
e\\":\\"2022-01-01T00:01:00Z\\"}}" --dev-center-name "{devCenterName}" --name \
"{environmentName}" --project-name "{projectName}" --user-id "{userId}"
"""

helps[
    "devcenter dev environment update"
] = """
    type: command
    short-summary: "Partially updates an environment."
    examples:
      - name: Environments_Update
        text: |-
              az devcenter dev environment update --description "Personal Dev Environment 2" --dev-center-name "{devCenterName}" \
              --name "{environmentName}" --project-name "{projectName}" --user-id "{userId}"
"""

helps[
    "devcenter dev environment delete"
] = """
    type: command
    short-summary: "Deletes an environment and all it's associated resources."
    examples:
      - name: Environments_Delete
        text: |-
              az devcenter dev environment delete --dev-center-name "{devCenterName}"  \
              --name "{environmentName}" --project-name "{projectName}" --user-id "{userId}"
"""

helps[
    "devcenter dev environment custom-action"
] = """
    type: command
    short-summary: "Executes a custom action."
    examples:
      - name: Environments_CustomAction
        text: |-
              az devcenter dev environment custom-action --action-id "someCustomActionId" --parameters \
"{\\"functionAppRuntime\\":\\"node\\",\\"storageAccountType\\":\\"Standard_LRS\\"}" --name "{environmentName}" \
--project-name "myProject" --user-id "me" --dev-center-name "{devCenterName}"
"""

helps[
    "devcenter dev environment delete-action"
] = """
    type: command
    short-summary: "Executes a delete action."
    examples:
      - name: Environments_DeleteAction
        text: |-
              az devcenter dev environment delete-action --action-id "delete" --parameters "{\\"functionAppRuntime\\":\\"n\
ode\\",\\"storageAccountType\\":\\"Standard_LRS\\"}" --name "{environmentName}" --project-name "myProject" --user-id \
"me" --dev-center-name "{devCenterName}"
"""

helps[
    "devcenter dev environment deploy-action"
] = """
    type: command
    short-summary: "Executes a deploy action."
    examples:
      - name: Environments_DeployAction
        text: |-
              az devcenter dev environment deploy-action --action-id "deploy" --parameters "{\\"functionAppRuntime\\":\\"n\
ode\\",\\"storageAccountType\\":\\"Standard_LRS\\"}" --name "{environmentName}" --project-name "myProject" --user-id \
"me" --dev-center-name "{devCenterName}"
"""

helps[
    "devcenter dev environment list-by-project"
] = """
    type: command
    short-summary: "Lists the environments for a project and user."
    examples:
      - name: Environments_ListByProject
        text: |-
              az devcenter dev environment list-by-project --dev-center-name "{devCenterName}"  \
              --project-name "{projectName}" --user-id "{userId}"
"""

helps[
    "devcenter dev environment wait"
] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the devcenter environment is met.
    examples:
      - name: Pause executing next line of CLI script until the devcenter environment is successfully created.
        text: |-
              az devcenter dev environment wait --dev-center-name "{devCenterName}" \
--name "{environmentName}" --project-name "{projectName}" --user-id "{userId}" --created
      - name: Pause executing next line of CLI script until the devcenter environment is successfully updated.
        text: |-
              az devcenter dev environment wait --dev-center-name "{devCenterName}" \
--name "{environmentName}" --project-name "{projectName}" --user-id "{userId}" --updated
      - name: Pause executing next line of CLI script until the devcenter environment is successfully deleted.
        text: |-
              az devcenter dev environment wait --dev-center-name "{devCenterName}" \
--name "{environmentName}" --project-name "{projectName}" --user-id "{userId}" --deleted
"""

helps[
    "devcenter dev artifact"
] = """
    type: group
    short-summary: Manage artifact with devcenter
"""

helps[
    "devcenter dev artifact list"
] = """
    type: command
    short-summary: "Lists the artifacts for an environment at a specified path, or returns the file at the path. And \
Lists the artifacts for an environment."
    examples:
      - name: Artifacts_Get
        text: |-
               az devcenter dev artifact list --artifact-path "{artifactPath}" --dev-center-name "{devCenterName}" \
               --environment-name "{environmentName}" --project-name "{projectName}" \
--user-id "{userId}"
      - name: Artifacts_ListByEnvironment
        text: |-
               az devcenter dev artifact list --dev-center-name "{devCenterName}" \
--environment-name "{environmentName}" --project-name "{projectName}" --user-id "{userId}"
"""

helps[
    "devcenter dev catalog-item"
] = """
    type: group
    short-summary: Manage catalog item with devcenter
"""

helps[
    "devcenter dev catalog-item list"
] = """
    type: command
    short-summary: "Lists latest version of all catalog items available for a project."
    examples:
      - name: CatalogItems_ListByProject
        text: |-
               az devcenter dev catalog-item list --dev-center-name "{devCenterName}" \
               --project-name "{projectName}"
"""

helps[
    "devcenter dev catalog-item"
] = """
    type: group
    short-summary: Manage catalog item with devcenter
"""

helps[
    "devcenter dev catalog-item show"
] = """
    type: command
    short-summary: "Get a catalog item from a project."
    examples:
      - name: CatalogItems_Get
        text: |-
               az devcenter dev catalog-item show --dev-center-name "{devCenterName}" \
               --project-name "{projectName}" --catalog-item-id "{catalogItemId}"
"""

helps[
    "devcenter dev catalog-item-version"
] = """
    type: group
    short-summary: Manage catalog item version with devcenter
"""

helps[
    "devcenter dev catalog-item-version list"
] = """
    type: command
    short-summary: "List all versions of a catalog item from a project."
    examples:
      - name: CatalogItemVersions_ListByProject
        text: |-
               az devcenter dev catalog-item-version list --dev-center-name "{devCenterName}"  \
                --project-name "{projectName}" --catalog-item-id "{catalogItemId}"
"""

helps[
    "devcenter dev catalog-item-version show"
] = """
    type: command
    short-summary: "Get a specific catalog item version from a project."
    examples:
      - name: CatalogItemVersion_Get
        text: |-
               az devcenter dev catalog-item-version show --dev-center-name "{devCenterName}"  \
               --project-name "{projectName}" --catalog-item-id "{catalogItemId}"
"""

helps[
    "devcenter dev environment-type"
] = """
    type: group
    short-summary: Manage environment type with devcenter
"""

helps[
    "devcenter dev environment-type list"
] = """
    type: command
    short-summary: "Lists all environment types configured for a project."
    examples:
      - name: EnvironmentType_ListByProject
        text: |-
               az devcenter dev environment-type list --dev-center-name "{devCenterName}"  \
              --project-name "{projectName}"
"""

helps[
    "devcenter dev notification-setting show"
] = """
    type: command
    short-summary: "Gets notification settings for user in the project."
    examples:
      - name: DevCenter_GetNotificationSettings
        text: |-
               az devcenter dev notification-setting show --user-id "me"
"""

helps[
    "devcenter dev notification-setting create"
] = """
    type: command
    short-summary: "Creates or updates notification settings."
    parameters:
      - name: --email-notification
        short-summary: "The email notification"
        long-summary: |
            Usage: --email-notification enabled=XX recipients=XX cc=XX

            enabled: Required. If email notification is enabled
            recipients: The recipients of the email notification
            cc: The cc of the email notification
      - name: --webhook-notification
        short-summary: "The webhook notification"
        long-summary: |
            Usage: --webhook-notification enabled=XX url=XX

            enabled: Required. If webhook notification is enabled
            url: The url of the webhook
    examples:
      - name: DevCenter_CreateNotificationSettings
        text: |-
               az devcenter dev notification-setting create --culture "en-us" --enabled false --boolean-enabled \
true --email-notification cc="stubcc@domain.com" enabled=true recipients="stubrecipient@domain.com" \
--webhook-notification enabled=false url="https://fake.domain/url/hook" --user-id "me"
"""

helps[
    "devcenter dev notification-setting list-allowed-culture"
] = """
    type: command
    short-summary: "Lists allowed culture codes for notification settings."
    examples:
      - name: DevCenter_ListNotificationSettingsAllowedCultures
        text: |-
               devcenter dev notification-setting list-allowed-culture --user-id "me"
"""

# control plane
helps[
    "devcenter"
] = """
    type: group
    short-summary: Manage Microsoft Dev Box and Azure Deployment Environments
"""

helps[
    "devcenter admin devcenter"
] = """
    type: group
    short-summary: Manage dev center with devcenter
"""

helps[
    "devcenter admin devcenter list"
] = """
    type: command
    short-summary: "Lists all dev centers in a resource group or lists all dev centers in a subscription."
    examples:
      - name: DevCenters_ListByResourceGroup
        text: |-
               az devcenter admin devcenter list --resource-group "rg1"
      - name: DevCenters_ListBySubscription
        text: |-
               az devcenter admin devcenter list
"""

helps[
    "devcenter admin devcenter show"
] = """
    type: command
    short-summary: "Gets a devcenter."
    examples:
      - name: DevCenters_Get
        text: |-
               az devcenter admin devcenter show --name "Contoso" --resource-group "rg1"
"""

helps[
    "devcenter admin devcenter create"
] = """
    type: command
    short-summary: "Create a devcenter resource."
    examples:
      - name: DevCenters_Create
        text: |-
               az devcenter admin devcenter create --location "eastus" --tags CostCode="12345" --name "Contoso" \
--resource-group "rg1"
      - name: DevCenters_CreateWithUserIdentity
        text: |-
               az devcenter admin devcenter create --identity-type "UserAssigned" --user-assigned-identities \
"{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/identityGroup/providers/Microsoft.ManagedIdenti\
ty/userAssignedIdentities/testidentity1\\":{}}" --location "eastus" --tags CostCode="12345" --name "Contoso" \
--resource-group "rg1"
"""

helps[
    "devcenter admin devcenter update"
] = """
    type: command
    short-summary: "Partially updates a devcenter."
    examples:
      - name: DevCenters_Update
        text: |-
               az devcenter admin devcenter update --tags CostCode="12345" --name "Contoso" --resource-group "rg1"
"""

helps[
    "devcenter admin devcenter delete"
] = """
    type: command
    short-summary: "Deletes a devcenter."
    examples:
      - name: DevCenters_Delete
        text: |-
               az devcenter admin devcenter delete --name "Contoso" --resource-group "rg1"
"""

helps[
    "devcenter admin devcenter wait"
] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the devcenter dev-center is met.
    examples:
      - name: Pause executing next line of CLI script until the devcenter dev-center is successfully created.
        text: |-
               az devcenter admin devcenter wait --name "Contoso" --resource-group "rg1" --created
      - name: Pause executing next line of CLI script until the devcenter dev-center is successfully updated.
        text: |-
               az devcenter admin devcenter wait --name "Contoso" --resource-group "rg1" --updated
      - name: Pause executing next line of CLI script until the devcenter dev-center is successfully deleted.
        text: |-
               az devcenter admin devcenter wait --name "Contoso" --resource-group "rg1" --deleted
"""

helps[
    "devcenter admin project"
] = """
    type: group
    short-summary: Manage project with devcenter
"""

helps[
    "devcenter admin project list"
] = """
    type: command
    short-summary: "Lists all projects in the resource group or lists all projects in the subscription."
    examples:
      - name: Projects_ListByResourceGroup
        text: |-
               az devcenter admin project list --resource-group "rg1"
      - name: Projects_ListBySubscription
        text: |-
               az devcenter admin project list
"""

helps[
    "devcenter admin project show"
] = """
    type: command
    short-summary: "Gets a specific project."
    examples:
      - name: Projects_Get
        text: |-
               az devcenter admin project show --name "{projectName}" --resource-group "rg1"
"""

helps[
    "devcenter admin project create"
] = """
    type: command
    short-summary: "Create a project."
    examples:
      - name: Projects_CreateOrUpdate
        text: |-
               az devcenter admin project create --location "eastus" --description "This is my first project." \
--dev-center-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.DevCenter/devcenters/{devCenterNa\
me}" --tags CostCenter="R&D" --name "{projectName}" --resource-group "rg1"
"""

helps[
    "devcenter admin project update"
] = """
    type: command
    short-summary: "Partially updates a project."
    examples:
      - name: Projects_Update
        text: |-
               az devcenter admin project update --description "This is my first project." --tags CostCenter="R&D" --name \
"{projectName}" --resource-group "rg1"
"""

helps[
    "devcenter admin project delete"
] = """
    type: command
    short-summary: "Deletes a project resource."
    examples:
      - name: Projects_Delete
        text: |-
               az devcenter admin project delete --name "{projectName}" --resource-group "rg1"
"""

helps[
    "devcenter admin project wait"
] = """
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

helps[
    "devcenter admin attached-network"
] = """
    type: group
    short-summary: Manage attached network with devcenter
"""

helps[
    "devcenter admin attached-network list"
] = """
    type: command
    short-summary: "Lists the attached network connections for a project or lists the attached network connections for \
a DevCenter."
    examples:
      - name: AttachedNetworks_ListByProject
        text: |-
               az devcenter admin attached-network list --project-name "{projectName}" --resource-group "rg1"
      - name: AttachedNetworks_ListByDevCenter
        text: |-
               az devcenter admin attached-network list --dev-center-name "Contoso" --resource-group "rg1"
"""

helps[
    "devcenter admin attached-network show"
] = """
    type: command
    short-summary: "Gets an attached network connection."
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

helps[
    "devcenter admin attached-network create"
] = """
    type: command
    short-summary: "Create an attached network connection."
    examples:
      - name: AttachedNetworks_Create
        text: |-
               az devcenter admin attached-network create --attached-network-connection-name "{attachedNetworkConnectionName}" \
--network-connection-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/providers/Microsoft.DevCenter/networ\
kConnections/{networkConnectionName}" --dev-center-name "Contoso" --resource-group "rg1"
"""

helps[
    "devcenter admin attached-network update"
] = """
    type: command
    short-summary: "Update an attached network connection."
"""

helps[
    "devcenter admin attached-network delete"
] = """
    type: command
    short-summary: "Detach a network connection."
    examples:
      - name: AttachedNetworks_Delete
        text: |-
               az devcenter admin attached-network delete --attached-network-connection-name "{attachedNetworkConnectionName}" \
--dev-center-name "Contoso" --resource-group "rg1"
"""

helps[
    "devcenter admin attached-network wait"
] = """
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

helps[
    "devcenter admin environment-type"
] = """
    type: group
    short-summary: Manage environment type with devcenter
"""

helps[
    "devcenter admin environment-type list"
] = """
    type: command
    short-summary: "Lists all environment types configured for this project. And Lists environment types for the \
devcenter."
    examples:
      - name: EnvironmentTypes_ListByDevCenter
        text: |-
               az devcenter admin environment-type list --dev-center-name "Contoso" --resource-group "rg1"
"""

helps[
    "devcenter admin environment-type show"
] = """
    type: command
    short-summary: "Gets an environment type."
    examples:
      - name: EnvironmentTypes_Get
        text: |-
               az devcenter admin environment-type show --dev-center-name "Contoso" --name "{environmentTypeName}" \
--resource-group "rg1"
"""

helps[
    "devcenter admin environment-type create"
] = """
    type: command
    short-summary: "Create an environment type."
    examples:
      - name: EnvironmentTypes_CreateOrUpdate
        text: |-
               az devcenter admin environment-type create --tags Owner="superuser" --dev-center-name \
"Contoso" --name "{environmentTypeName}" --resource-group "rg1"
"""

helps[
    "devcenter admin environment-type update"
] = """
    type: command
    short-summary: "Partially updates an environment type."
    examples:
      - name: EnvironmentTypes_Update
        text: |-
               az devcenter admin environment-type update --tags Owner="superuser" --dev-center-name "Contoso" \
--name "{environmentTypeName}" --resource-group "rg1"
"""

helps[
    "devcenter admin environment-type delete"
] = """
    type: command
    short-summary: "Deletes an environment type."
    examples:
      - name: EnvironmentTypes_Delete
        text: |-
               az devcenter admin environment-type delete --dev-center-name "Contoso" --name "{environmentTypeName}" \
--resource-group "rg1"
"""

helps[
    "devcenter admin project-environment-type"
] = """
    type: group
    short-summary: Manage environment types for a given project
"""

helps[
    "devcenter admin project-environment-type list"
] = """
    type: command
    short-summary: "Lists environment types for a project."
    examples:
      - name: ProjectEnvironmentTypes_List
        text: |-
               az devcenter admin project-environment-type list --project-name "ContosoProj" --resource-group "rg1"
"""

helps[
    "devcenter admin project-environment-type show"
] = """
    type: command
    short-summary: "Gets a project environment type."
    examples:
      - name: ProjectEnvironmentTypes_Get
        text: |-
               az devcenter admin project-environment-type show --environment-type-name "{environmentTypeName}" \
--project-name "ContosoProj" --resource-group "rg1"
"""

helps[
    "devcenter admin project-environment-type create"
] = """
    type: command
    short-summary: "Create a project environment type."
    examples:
      - name: ProjectEnvironmentTypes_CreateOrUpdate
        text: |-
               az devcenter admin project-environment-type create --identity-type "UserAssigned" --user-assigned-identities \
"{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/identityGroup/providers/Microsoft.ManagedIdenti\
ty/userAssignedIdentities/testidentity1\\":{}}" --roles "{\\"4cbf0b6c-e750-441c-98a7-10da8387e4d6\\":{}}" \
--deployment-target-id "/subscriptions/00000000-0000-0000-0000-000000000000" --status "Enabled" \
--user-role-assignments "{\\"e45e3m7c-176e-416a-b466-0c5ec8298f8a\\":{\\"roles\\":{\\"4cbf0b6c-e750-441c-98a7-10da8387e\
4d6\\":{}}}}" --tags CostCenter="RnD" --environment-type-name "{environmentTypeName}" --project-name "ContosoProj" \
--resource-group "rg1"
"""

helps[
    "devcenter admin project-environment-type update"
] = """
    type: command
    short-summary: "Partially updates a project environment type."
    examples:
      - name: ProjectEnvironmentTypes_Update
        text: |-
               az devcenter admin project-environment-type update --identity-type "UserAssigned" --user-assigned-identities \
"{\\"/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/identityGroup/providers/Microsoft.ManagedIdenti\
ty/userAssignedIdentities/testidentity1\\":{}}" --deployment-target-id "/subscriptions/00000000-0000-0000-0000-00000000\
0000" --status "Enabled" --user-role-assignments "{\\"e45e3m7c-176e-416a-b466-0c5ec8298f8a\\":{\\"roles\\":{\\"4cbf0b6c\
-e750-441c-98a7-10da8387e4d6\\":{}}}}" --tags CostCenter="RnD" --environment-type-name "{environmentTypeName}" \
--project-name "ContosoProj" --resource-group "rg1"
"""


helps[
    "devcenter admin project-environment-type delete"
] = """
    type: command
    short-summary: "Deletes a project environment type."
    examples:
      - name: ProjectEnvironmentTypes_Delete
        text: |-
               az devcenter admin project-environment-type delete --environment-type-name "{environmentTypeName}" \
--project-name "ContosoProj" --resource-group "rg1"
"""

helps[
    "devcenter admin project-allowed-environment-type"
] = """
    type: group
    short-summary: Manage project allowed environment type with devcenter
"""

helps[
    "devcenter admin project-allowed-environment-type list"
] = """
    type: command
    short-summary: "Lists allowed environment types for a project."
    examples:
      - name: ProjectAllowedEnvironmentTypes_List
        text: |-
               az devcenter admin project-allowed-environment-type list --project-name "Contoso" --resource-group "rg1"
"""

helps[
    "devcenter admin project-allowed-environment-type show"
] = """
    type: command
    short-summary: "Gets an allowed environment type."
    examples:
      - name: ProjectAllowedEnvironmentTypes_Get
        text: |-
               az devcenter admin project-allowed-environment-type show --environment-type-name "{environmentTypeName}" \
--project-name "Contoso" --resource-group "rg1"
"""


helps[
    "devcenter admin catalog"
] = """
    type: group
    short-summary: Manage catalog with devcenter
"""

helps[
    "devcenter admin catalog list"
] = """
    type: command
    short-summary: "Lists catalogs for a devcenter."
    examples:
      - name: Catalogs_ListByDevCenter
        text: |-
               az devcenter admin catalog list --dev-center-name "Contoso" --resource-group "rg1"
"""

helps[
    "devcenter admin catalog show"
] = """
    type: command
    short-summary: "Gets a catalog."
    examples:
      - name: Catalogs_Get
        text: |-
               az devcenter admin catalog show --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
"""

helps[
    "devcenter admin catalog create"
] = """
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

helps[
    "devcenter admin catalog update"
] = """
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

helps[
    "devcenter admin catalog delete"
] = """
    type: command
    short-summary: "Deletes a catalog resource."
    examples:
      - name: Catalogs_Delete
        text: |-
               az devcenter admin catalog delete --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
"""

helps[
    "devcenter admin catalog sync"
] = """
    type: command
    short-summary: "Syncs templates for a template source."
    examples:
      - name: Catalogs_Sync
        text: |-
               az devcenter admin catalog sync --name "{catalogName}" --dev-center-name "Contoso" --resource-group "rg1"
"""

helps[
    "devcenter admin catalog wait"
] = """
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

helps[
    "devcenter admin devbox-definition"
] = """
    type: group
    short-summary: Manage dev box definition with devcenter
"""

helps[
    "devcenter admin devbox-definition list"
] = """
    type: command
    short-summary: "List dev box definitions for a dev center or for a project."
    examples:
      - name: DevBoxDefinitions_ListByDevCenter
        text: |-
               az devcenter admin devbox-definition list --dev-center-name "Contoso" --resource-group "rg1"
      - name: DevBoxDefinitions_ListByProject
        text: |-
               az devcenter admin devbox-definition list --project-name "ContosoProject" --resource-group "rg1"
"""

helps[
    "devcenter admin devbox-definition show"
] = """
    type: command
    short-summary: "Gets a dev box definition for a dev center or for a project."
    examples:
      - name: DevBoxDefinitions_Get
        text: |-
               az devcenter admin devbox-definition show --name "WebDevBox" --dev-center-name "Contoso" --resource-group \
"rg1"
      - name: DevBoxDefinitions_GetByProject
        text: |-
               az devcenter admin devbox-definition show --name "WebDevBox" --project-name "ContosoProject" \
--resource-group "rg1"
"""

helps[
    "devcenter admin devbox-definition create"
] = """
    type: command
    short-summary: "Create a dev box definition."
    parameters:
      - name: --image-reference
        short-summary: "Image reference information"
        long-summary: |
            Usage: --image-reference id=XX publisher=XX offer=XX sku=XX

            id: Image ID, or Image version ID. When Image ID is provided, its latest version will be used.
            publisher: The image publisher.
            offer: The image offer.
            sku: The image sku.
      - name: --sku
        short-summary: "The SKU for Dev Boxes created using this definition"
        long-summary: |
            Usage: --sku name=XX tier=XX size=XX family=XX capacity=XX

            name: Required. The name of the SKU. Ex - P3. It is typically a letter+number code
            tier: This field is required to be implemented by the Resource Provider if the service has more than one \
tier, but is not required on a PUT.
            size: The SKU size. When the name field is the combination of tier and some other value, this would be the \
standalone code.
            family: If the service has different generations of hardware, for the same SKU, then that can be captured \
here.
            capacity: If the SKU supports scale out/in then the capacity integer should be included. If scale out/in \
is not possible for the resource this may be omitted.
    examples:
      - name: DevBoxDefinitions_Create
        text: |-
               az devcenter admin devbox-definition create --location "eastus" --hibernate-support "Enabled" \
--image-reference id="/subscriptions/0ac520ee-14c0-480f-b6c9-0a90c58ffff/resourceGroups/Example/providers/Microsoft.Dev\
Center/devcenters/Contoso/galleries/contosogallery/images/exampleImage/version/1.0.0" --os-storage-type "SSD_1024" \
--sku name="Preview" --name "WebDevBox" --dev-center-name "Contoso" --resource-group "rg1"
"""

helps[
    "devcenter admin devbox-definition update"
] = """
    type: command
    short-summary: "Partially updates a dev box definition."
    parameters:
      - name: --image-reference
        short-summary: "Image reference information."
        long-summary: |
            Usage: --image-reference id=XX publisher=XX offer=XX sku=XX

            id: Image ID, or Image version ID. When Image ID is provided, its latest version will be used.
            publisher: The image publisher.
            offer: The image offer.
            sku: The image sku.
      - name: --sku
        short-summary: "The SKU for Dev Boxes created using this definition."
        long-summary: |
            Usage: --sku name=XX tier=XX size=XX family=XX capacity=XX

            name: Required. The name of the SKU. Ex - P3. It is typically a letter+number code
            tier: This field is required to be implemented by the Resource Provider if the service has more than one \
tier, but is not required on a PUT.
            size: The SKU size. When the name field is the combination of tier and some other value, this would be the \
standalone code.
            family: If the service has different generations of hardware, for the same SKU, then that can be captured \
here.
            capacity: If the SKU supports scale out/in then the capacity integer should be included. If scale out/in \
is not possible for the resource this may be omitted.
    examples:
      - name: DevBoxDefinitions_Patch
        text: |-
               az devcenter admin devbox-definition update --image-reference id="/subscriptions/0ac520ee-14c0-480f-b6c9-0a90\
c58ffff/resourceGroups/Example/providers/Microsoft.DevCenter/devcenters/Contoso/galleries/contosogallery/images/example\
Image/version/2.0.0" --name "WebDevBox" --dev-center-name "Contoso" --resource-group "rg1"
"""

helps[
    "devcenter admin devbox-definition delete"
] = """
    type: command
    short-summary: "Deletes a dev box definition."
    examples:
      - name: DevBoxDefinitions_Delete
        text: |-
               az devcenter admin devbox-definition delete --name "WebDevBox" --dev-center-name "Contoso" --resource-group \
"rg1"
"""

helps[
    "devcenter admin devbox-definition wait"
] = """
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

helps[
    "devcenter admin usage"
] = """
    type: group
    short-summary: Manage usage with devcenter
"""

helps[
    "devcenter admin usage list"
] = """
    type: command
    short-summary: "Lists the current usages and limits in this location for the provided subscription."
    examples:
      - name: listUsages
        text: |-
               az devcenter admin usage list --location "westus"
"""

helps[
    "devcenter admin check-name-availability"
] = """
    type: group
    short-summary: Manage check name availability with devcenter.
"""

helps[
    "devcenter admin check-name-availability execute"
] = """
    type: command
    short-summary: "Check the availability of name for resource."
    examples:
      - name: NameAvailability
        text: |-
               az devcenter check-name-availability execute --name "name1" --type "Microsoft.DevCenter/devcenters"
"""

helps[
    "devcenter admin operation-statuses"
] = """
    type: group
    short-summary: Manage operation statuses with devcenter
"""

helps[
    "devcenter admin operation-statuses show"
] = """
    type: command
    short-summary: "Gets the current status of an async operation."
    examples:
      - name: Get OperationStatus
        text: |-
               az devcenter admin operation-statuses show --operation-id "{operationId}" --location "{location}"
"""

helps[
    "devcenter admin sku"
] = """
    type: group
    short-summary: Manage sku with devcenter
"""

helps[
    "devcenter admin sku list"
] = """
    type: command
    short-summary: "Lists the Microsoft.DevCenter SKUs available in a subscription."
    examples:
      - name: Skus_ListBySubscription
        text: |-
               az devcenter admin sku list
"""


helps[
    "devcenter admin pool"
] = """
    type: group
    short-summary: Manage pool with devcenter
"""

helps[
    "devcenter admin pool list"
] = """
    type: command
    short-summary: "Lists pools for a project."
    examples:
      - name: Pools_ListByProject
        text: |-
               az devcenter admin pool list --project-name "{projectName}" --resource-group "rg1"
"""

helps[
    "devcenter admin pool show"
] = """
    type: command
    short-summary: "Gets a dev box pool."
    examples:
      - name: Pools_Get
        text: |-
               az devcenter admin pool show --name "{poolName}" --project-name "{projectName}" --resource-group "rg1"
"""

helps[
    "devcenter admin pool create"
] = """
    type: command
    short-summary: "Create a dev box pool."
    examples:
      - name: Pools_CreateOrUpdate
        text: |-
               az devcenter admin pool create --location "eastus" --devbox-definition-name "WebDevBox" \
--network-connection-name "Network1-westus2" --pool-name "{poolName}" --project-name "{projectName}" --resource-group \
"rg1" --license-type Windows_Client --local-administrator Enabled
"""

helps[
    "devcenter admin pool update"
] = """
    type: command
    short-summary: "Partially updates a dev box pool."
    examples:
      - name: Pools_Update
        text: |-
               az devcenter admin pool update --devbox-definition-name "WebDevBox2" --pool-name "{poolName}" --project-name \
"{projectName}" --resource-group "rg1"
"""

helps[
    "devcenter admin pool delete"
] = """
    type: command
    short-summary: "Deletes a dev box pool."
    examples:
      - name: Pools_Delete
        text: |-
               az devcenter admin pool delete --name "poolName" --project-name "{projectName}" --resource-group "rg1"
"""

helps[
    "devcenter admin pool wait"
] = """
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

helps[
    "devcenter admin schedule"
] = """
    type: group
    short-summary: Manage schedule with devcenter
"""

helps[
    "devcenter admin schedule show"
] = """
    type: command
    short-summary: "Gets a schedule."
    examples:
      - name: Schedules_GetByPool
        text: |-
               az devcenter admin schedule show --pool-name "DevPool" --project-name "TestProject" --resource-group "rg1"
"""

helps[
    "devcenter admin schedule create"
] = """
    type: command
    short-summary: "Create a schedule."
    examples:
      - name: Schedules_CreateDailyShutdownPoolSchedule
        text: |-
               az devcenter admin schedule create --state "Enabled" --time "17:30" --time-zone "America/Los_Angeles" \
--pool-name "DevPool" --project-name "DevProject" --resource-group "rg1"
"""

helps[
    "devcenter admin schedule update"
] = """
    type: command
    short-summary: "Partially updates a schedule."
    examples:
      - name: Schedules_Update
        text: |-
               az devcenter admin schedule update --time "18:00" --pool-name "DevPool" --project-name "TestProject" \
--resource-group "rg1"
"""

helps[
    "devcenter admin schedule delete"
] = """
    type: command
    short-summary: "Deletes a schedule."
    examples:
      - name: Schedules_Delete
        text: |-
               az devcenter admin schedule delete --pool-name "DevPool" --project-name "TestProject" --resource-group "rg1"
"""

helps[
    "devcenter admin schedule wait"
] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the devcenter admin schedule is met.
    examples:
      - name: Pause executing next line of CLI script until the devcenter admin schedule is successfully created.
        text: |-
               az devcenter admin schedule wait --pool-name "DevPool" --project-name "TestProject" --resource-group "rg1" \
--created
      - name: Pause executing next line of CLI script until the devcenter admin schedule is successfully updated.
        text: |-
               az devcenter admin schedule wait --pool-name "DevPool" --project-name "TestProject" --resource-group "rg1" \
--updated
      - name: Pause executing next line of CLI script until the devcenter admin schedule is successfully deleted.
        text: |-
               az devcenter admin schedule wait --pool-name "DevPool" --project-name "TestProject" --resource-group "rg1" \
--deleted
"""


helps[
    "devcenter admin network-connection"
] = """
    type: group
    short-summary: Manage network connection with devcenter
"""

helps[
    "devcenter admin network-connection list"
] = """
    type: command
    short-summary: "Lists network connection in a resource group or in a subscription."
    examples:
      - name: NetworkConnections_ListByResourceGroup
        text: |-
               az devcenter admin network-connection list --resource-group "rg1"
      - name: NetworkConnections_ListBySubscription
        text: |-
               az devcenter admin network-connection list
"""

helps[
    "devcenter admin network-connection show"
] = """
    type: command
    short-summary: "Gets a network connection."
    examples:
      - name: NetworkConnections_Get
        text: |-
               az devcenter admin network-connection show --name "{networkConnectionName}" --resource-group "rg1"
"""

helps[
    "devcenter admin network-connection create"
] = """
    type: command
    short-summary: "Create a network connection."
    examples:
      - name: NetworkConnections_CreateHybridJoined
        text: |-
               az devcenter admin network-connection create --location "eastus" --domain-join-type "HybridAzureADJoin" \
--domain-name "mydomaincontroller.local" --domain-password "Password value for user" --domain-username \
"testuser@mydomaincontroller.local" --subnet-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/ExampleRG/pr\
oviders/Microsoft.Network/virtualNetworks/ExampleVNet/subnets/default" --name "{networkConnectionName}" --resource-group \
"rg1"
      - name: NetworkConnections_CreateAzureJoined
        text: |-
               az devcenter admin network-connection create --location "eastus" --domain-join-type "AzureADJoin" \
--networking-resource-group-name "NetworkInterfacesRG" --subnet-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/ExampleRG/pr\
oviders/Microsoft.Network/virtualNetworks/ExampleVNet/subnets/default" --name "{networkConnectionName}" --resource-group \
"rg1"
"""

helps[
    "devcenter admin network-connection update"
] = """
    type: command
    short-summary: "Partially updates a network connection."
    examples:
      - name: NetworkConnections_Update
        text: |-
               az devcenter admin network-connection update --domain-password "New Password value for user" --name \
"{networkConnectionName}" --resource-group "rg1"
"""

helps[
    "devcenter admin network-connection delete"
] = """
    type: command
    short-summary: "Deletes a network connection."
    examples:
      - name: NetworkConnections_Delete
        text: |-
               az devcenter admin network-connection delete --name "{networkConnectionName}" --resource-group "rg1"
"""

helps[
    "devcenter admin network-connection list-health-detail"
] = """
    type: command
    short-summary: "Lists health check status details."
    examples:
      - name: NetworkConnections_ListHealthDetails
        text: |-
               az devcenter admin network-connection list-health-detail --network-connection-name "uswest3network" --resource-group "rg1"
"""

helps[
    "devcenter admin network-connection run-health-check"
] = """
    type: command
    short-summary: "Triggers a new health check run. The execution and health check result can be tracked via the \
network Connection health check details."
    examples:
      - name: NetworkConnections_RunHealthChecks
        text: |-
               az devcenter admin network-connection run-health-check --name "uswest3network" --resource-group "rg1"
"""

helps[
    "devcenter admin network-connection show-health-detail"
] = """
    type: command
    short-summary: "Gets health check status details."
    examples:
      - name: NetworkConnections_GetHealthDetails
        text: |-
               az devcenter admin network-connection show-health-detail --name "{networkConnectionName}" --resource-group "rg1"
"""

helps[
    "devcenter admin network-connection wait"
] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the devcenter network-connection is met.
    examples:
      - name: Pause executing next line of CLI script until the devcenter network-connection is successfully created.
        text: |-
               az devcenter admin network-connection wait --name "{networkConnectionName}" --resource-group "rg1" --created
      - name: Pause executing next line of CLI script until the devcenter network-connection is successfully updated.
        text: |-
               az devcenter admin network-connection wait --name "{networkConnectionName}" --resource-group "rg1" --updated
      - name: Pause executing next line of CLI script until the devcenter network-connection is successfully deleted.
        text: |-
               az devcenter admin network-connection wait --name "{networkConnectionName}" --resource-group "rg1" --deleted
"""

helps[
    "devcenter admin gallery"
] = """
    type: group
    short-summary: Manage gallery with devcenter
"""

helps[
    "devcenter admin gallery list"
] = """
    type: command
    short-summary: "Lists galleries for a devcenter."
    examples:
      - name: Galleries_ListByDevCenter
        text: |-
               az devcenter admin gallery list --dev-center-name "Contoso" --resource-group "rg1"
"""

helps[
    "devcenter admin gallery show"
] = """
    type: command
    short-summary: "Gets a gallery."
    examples:
      - name: Galleries_Get
        text: |-
               az devcenter admin gallery show --dev-center-name "Contoso" --name "{galleryName}" --resource-group "rg1"
"""

helps[
    "devcenter admin gallery create"
] = """
    type: command
    short-summary: "Create a gallery."
    examples:
      - name: Galleries_CreateOrUpdate
        text: |-
               az devcenter admin gallery create --gallery-resource-id "/subscriptions/{subscriptionId}/resourceGroups/rg1/prov\
iders/Microsoft.Compute/galleries/{galleryName}" --dev-center-name "Contoso" --name "{galleryName}" --resource-group \
"rg1"
"""

helps[
    "devcenter admin gallery update"
] = """
    type: command
    short-summary: "Update a gallery."
"""

helps[
    "devcenter admin gallery delete"
] = """
    type: command
    short-summary: "Deletes a gallery resource."
    examples:
      - name: Galleries_Delete
        text: |-
               az devcenter admin gallery delete --dev-center-name "Contoso" --name "{galleryName}" --resource-group "rg1"
"""

helps[
    "devcenter admin gallery wait"
] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the devcenter gallery is met.
    examples:
      - name: Pause executing next line of CLI script until the devcenter gallery is successfully created.
        text: |-
               az devcenter admin gallery wait --dev-center-name "Contoso" --name "{galleryName}" --resource-group "rg1" \
--created
      - name: Pause executing next line of CLI script until the devcenter gallery is successfully updated.
        text: |-
               az devcenter admin gallery wait --dev-center-name "Contoso" --name "{galleryName}" --resource-group "rg1" \
--updated
      - name: Pause executing next line of CLI script until the devcenter gallery is successfully deleted.
        text: |-
               az devcenter admin gallery wait --dev-center-name "Contoso" --name "{galleryName}" --resource-group "rg1" \
--deleted
"""

helps[
    "devcenter admin image"
] = """
    type: group
    short-summary: Manage image with devcenter
"""

helps[
    "devcenter admin image list"
] = """
    type: command
    short-summary: "Lists images for a gallery. And Lists images for a devcenter."
    examples:
      - name: Images_ListByGallery
        text: |-
               az devcenter admin image list --dev-center-name "Contoso" --gallery-name "DevGallery" --resource-group "rg1"
      - name: Images_ListByDevCenter
        text: |-
               az devcenter admin image list --dev-center-name "Contoso" --resource-group "rg1"
"""

helps[
    "devcenter admin image show"
] = """
    type: command
    short-summary: "Gets a gallery image."
    examples:
      - name: Images_Get
        text: |-
               az devcenter admin image show --dev-center-name "Contoso" --gallery-name "DefaultDevGallery" --name \
"{imageName}" --resource-group "rg1"
"""

helps[
    "devcenter admin image-version"
] = """
    type: group
    short-summary: Manage image version with devcenter
"""

helps[
    "devcenter admin image-version list"
] = """
    type: command
    short-summary: "Lists versions for an image."
    examples:
      - name: ImageVersions_ListByImage
        text: |-
               az devcenter admin image-version list --dev-center-name "Contoso" --gallery-name "DefaultDevGallery" \
--image-name "Win11" --resource-group "rg1"
"""

helps[
    "devcenter admin image-version show"
] = """
    type: command
    short-summary: "Gets an image version."
    examples:
      - name: Versions_Get
        text: |-
               az devcenter admin image-version show --dev-center-name "Contoso" --gallery-name "DefaultDevGallery" \
--image-name "Win11" --resource-group "rg1" --version-name "{versionName}"
"""
