# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

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
    "devcenter dev dev-box list-upcoming-action"
] = """
    type: command
    short-summary: "Lists upcoming actions on a Dev Box."
    examples:
      - name: DevBoxes_ListUpcomingActions
        text: |-
               az devcenter dev dev-box list-upcoming-action --dev-center-name "{devCenterName}" \
--project-name "{projectName}" --name "myDevBox" --user-id "me"
"""

helps[
    "devcenter dev dev-box delay-upcoming-action"
] = """
    type: command
    short-summary: "Delays an Upcoming Action."
    examples:
      - name: DevBoxes_DelayUpcomingAction
        text: |-
               az devcenter dev dev-box delay-upcoming-action --dev-center-name "{devCenterName}" \
--project-name "{projectName}" --delay-time "04:30" --name "myDevBox" \
--upcoming-action-id "cae4d1f4-94b8-75f2-406d-5f00ae4c1da7 --user-id "00000000-0000-0000-0000-000000000000""
"""

helps[
    "devcenter dev dev-box show-upcoming-action"
] = """
    type: command
    short-summary: "Gets an Upcoming Action."
    examples:
      - name: DevBoxes_GetUpcomingAction
        text: |-
               az devcenter dev dev-box show-upcoming-action --dev-center-name "{devCenterName}" \
--project-name "{projectName}" --name "myDevBox" --upcoming-action-id \
"cae4d1f4-94b8-75f2-406d-5f00ae4c1da7" --user-id "me"
"""

helps[
    "devcenter dev dev-box skip-upcoming-action"
] = """
    type: command
    short-summary: "Skips an Upcoming Action."
    examples:
      - name: DevBoxes_SkipUpcomingAction
        text: |-
               az devcenter dev dev-box skip-upcoming-action --dev-center-name "{devCenterName}" \
--project-name "{projectName}" --name "myDevBox" --upcoming-action-id \
"cae4d1f4-94b8-75f2-406d-5f00ae4c1da7" --user-id "me"
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
--project-name "{projectName}" --user-id "me"
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
               --project-name "{projectName}" --catalog-item-id "{catalogItemId}" --version "1.0.0"
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
    "devcenter dev notification-setting"
] = """
    type: group
    short-summary: Manage notification setting with devcenter
"""

helps[
    "devcenter dev notification-setting show"
] = """
    type: command
    short-summary: "Gets notification settings for user in the project."
    examples:
      - name: DevCenter_GetNotificationSettings
        text: |-
               az devcenter dev notification-setting show --dev-center-name "{devCenterName}"  \
              --project-name "{projectName}" --user-id "me"
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
               az devcenter dev notification-setting create --dev-center-name "{devCenterName}"  \
--project-name "{projectName}" --culture "en-us" --enabled false --boolean-enabled \
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
              az devcenter dev notification-setting list-allowed-culture --dev-center-name "{devCenterName}"  \
--project-name "{projectName}" --user-id "me"
"""
