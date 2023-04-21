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
    short-summary: "Creates a dev box."
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
      - name: DevBoxes_StartDevBox
        text: |-
               az devcenter dev dev-box start --name "MyDevBox" --dev-center-name "{devCenterName}" \
               --project-name "{projectName}" --user-id "me"
"""

helps[
    "devcenter dev dev-box restart"
] = """
    type: command
    short-summary: "Restarts a Dev Box."
    examples:
      - name: DevBoxes_StartDevBox
        text: |-
               az devcenter dev dev-box restart --name "MyDevBox" --dev-center-name "{devCenterName}" \
               --project-name "{projectName}" --user-id "me"
"""

helps[
    "devcenter dev dev-box stop"
] = """
    type: command
    short-summary: "Stops a dev box."
    examples:
      - name: DevBoxes_StopDevBox
        text: |-
               az devcenter dev dev-box stop --name "MyDevBox" --dev-center-name "{devCenterName}" \
               --project-name "{projectName}" --user-id "me" --hibernate "true"
"""

helps[
    "devcenter dev dev-box list-action"
] = """
    type: command
    short-summary: "Lists actions on a Dev Box."
    examples:
      - name: DevBoxes_ListActions
        text: |-
               az devcenter dev dev-box list-action --dev-center-name "{devCenterName}" \
--project-name "{projectName}" --name "myDevBox" --user-id "me"
"""

helps[
    "devcenter dev dev-box delay-action"
] = """
    type: command
    short-summary: "Delays an action."
    examples:
      - name: DevBoxes_DelayAction
        text: |-
               az devcenter dev dev-box delay-action --dev-center-name "{devCenterName}" \
--project-name "{projectName}" --delay-time "04:30" --name "myDevBox" \
--action-name "schedule-default" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box delay-all-actions"
] = """
    type: command
    short-summary: "Delays all actions."
    examples:
      - name: DevBoxes_DelayActions
        text: |-
               az devcenter dev dev-box delay-all-actions --dev-center-name "{devCenterName}" \
--project-name "{projectName}" --delay-time "04:30" --name "myDevBox" \
--user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box show-action"
] = """
    type: command
    short-summary: "Gets an action."
    examples:
      - name: DevBoxes_GetAction
        text: |-
               az devcenter dev dev-box show-action --dev-center-name "{devCenterName}" \
--project-name "{projectName}" --name "myDevBox" --action-name \
"schedule-default" --user-id "me"
"""

helps[
    "devcenter dev dev-box skip-action"
] = """
    type: command
    short-summary: "Skips an action."
    examples:
      - name: DevBoxes_SkipAction
        text: |-
               az devcenter dev dev-box skip-action --dev-center-name "{devCenterName}" \
--project-name "{projectName}" --name "myDevBox" --action-name \
"schedule-default" --user-id "me"
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
    short-summary: "Lists the environments for a project or lists the environments for a user within a project."
    examples:
      - name: Environments_ListByProject
        text: |-
              az devcenter dev environment list --dev-center-name "{devCenterName}" \
--project-name "{projectName}"
      - name: Environments_ListEnvironmentsByUser
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
      - name: Environments_CreateByEnvironmentDefinition
        text: |-
               az devcenter dev environment create --dev-center-name "{devCenterName}" --project-name "{projectName}" \
--catalog-name "main" --environment-definition-name "helloworld" --environment-type "DevTest" --parameters "{\\"functionAppRuntime\\":\\"node\
\\",\\"storageAccountType\\":\\"Standard_LRS\\"}" --name "mydevenv" --user-id "me"
"""

helps[
    "devcenter dev environment update"
] = """
    type: command
    short-summary: "Updates an environment."
    examples:
      - name: Environments_UpdateByEnvironmentDefinition
        text: |-
               az devcenter dev environment update --dev-center-name "{devCenterName}" --project-name "{projectName}" \
--name "mydevenv" --user-id "me" --parameters "{\\"functionAppRuntime\\":\\"node\
\\",\\"storageAccountType\\":\\"Standard_LRS\\"}"
"""

helps[
    "devcenter dev environment delete"
] = """
    type: command
    short-summary: "Deletes an environment and all its associated resources."
    examples:
      - name: Environments_Delete
        text: |-
              az devcenter dev environment delete --dev-center-name "{devCenterName}"  \
              --name "{environmentName}" --project-name "{projectName}" --user-id "{userId}"
"""

helps[
    "devcenter dev catalog"
] = """
    type: group
    short-summary: Manage catalog with devcenter
"""

helps[
    "devcenter dev catalog list"
] = """
    type: command
    short-summary: "Lists all of the catalogs available for a project."
    examples:
      - name: Environments_ListCatalogsByProject
        text: |-
               az devcenter dev catalog list --dev-center-name "{devCenterName}" \
               --project-name "{projectName}"
"""

helps[
    "devcenter dev catalog show"
] = """
    type: command
    short-summary: "Gets the specified catalog within the project."
    examples:
      - name: Environments_GetCatalog
        text: |-
               az devcenter dev catalog show --dev-center-name "{devCenterName}" \
               --project-name "{projectName}" --catalog-name "foo"
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
    "devcenter dev environment-definition"
] = """
    type: group
    short-summary: Manage environment definition with devcenter
"""

helps[
    "devcenter dev environment-definition list"
] = """
    type: command
    short-summary: "Lists all environment definitions available within a catalog. And Lists all environment \
definitions available for a project."
    examples:
      - name: Environments_ListEnvironmentDefinitionsByCatalog
        text: |-
               az devcenter dev environment-definition list --dev-center-name "{devCenterName}"  \
--project-name "{projectName}" --catalog-name "myCatalog"
      - name: Environments_ListEnvironmentDefinitions
        text: |-
               az devcenter dev environment-definition list --dev-center-name "{devCenterName}"  \
--project-name "{projectName}"
"""

helps[
    "devcenter dev environment-definition show"
] = """
    type: command
    short-summary: "Get an environment definition from a catalog."
    examples:
      - name: Environments_GetEnvironmentDefinition
        text: |-
               az devcenter dev environment-definition show --dev-center-name "{devCenterName}"  \
--project-name "{projectName}" --catalog-name "myCatalog" --definition-name "foo"
"""
