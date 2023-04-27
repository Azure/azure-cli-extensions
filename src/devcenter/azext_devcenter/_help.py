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
    short-summary: "Manages devcenter developer resources."
"""
helps[
    "devcenter dev project"
] = """
    type: group
    short-summary: Manage projects.
"""

helps[
    "devcenter dev project list"
] = """
    type: command
    short-summary: "Lists all projects."
    examples:
      - name: List
        text: |-
               az devcenter dev project list --dev-center-name "ContosoDevCenter"
"""

helps[
    "devcenter dev project show"
] = """
    type: command
    short-summary: "Gets a project."
    examples:
      - name: Get
        text: |-
               az devcenter dev project show --dev-center-name "ContosoDevCenter" \
--name "DevProject"
"""

helps[
    "devcenter dev pool"
] = """
    type: group
    short-summary: Manage pools.
"""

helps[
    "devcenter dev pool list"
] = """
    type: command
    short-summary: "Lists available pools."
    examples:
      - name: List
        text: |-
               az devcenter dev pool list --dev-center-name "ContosoDevCenter" \
--project-name "DevProject"
"""

helps[
    "devcenter dev pool show"
] = """
    type: command
    short-summary: "Gets a pool."
    examples:
      - name: Get
        text: |-
               az devcenter dev pool show --dev-center-name "ContosoDevCenter" --name \
"DevPool" --project-name "DevProject"
"""

helps[
    "devcenter dev schedule"
] = """
    type: group
    short-summary: Manage schedules.
"""

helps[
    "devcenter dev schedule show"
] = """
    type: command
    short-summary: "Gets a schedule."
    examples:
      - name: Get
        text: |-
               az devcenter dev schedule show --dev-center-name "ContosoDevCenter" \
--pool-name "DevPool" --project-name "DevProject"
"""

helps[
    "devcenter dev dev-box"
] = """
    type: group
    short-summary: Manage dev boxes.
"""

helps[
    "devcenter dev dev-box list"
] = """
    type: command
    short-summary: "Lists dev boxes for a user, lists dev boxes in the dev center for a \
project and user, or lists dev boxes that the caller has access to in the dev center."
    examples:
      - name: List by user and project
        text: |-
               az devcenter dev dev-box list --dev-center-name "ContosoDevCenter" \
--project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
      - name: List by user
        text: |-
               az devcenter dev dev-box list --dev-center-name "ContosoDevCenter" \
--user-id "00000000-0000-0000-0000-000000000000"
      - name: List
        text: |-
               az devcenter dev dev-box list --dev-center-name "ContosoDevCenter"
"""

helps[
    "devcenter dev dev-box show"
] = """
    type: command
    short-summary: "Gets a dev box."
    examples:
      - name: Get
        text: |-
               az devcenter dev dev-box show --name "MyDevBox" --dev-center-name "ContosoDevCenter" \
               --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box create"
] = """
    type: command
    short-summary: "Creates a dev box."
    examples:
      - name: Create
        text: |-
               az devcenter dev dev-box create --pool-name "LargeDevWorkStationPool" --name "MyDevBox" --dev-center-name \
"ContosoDevCenter" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box delete"
] = """
    type: command
    short-summary: "Deletes a dev box."
    examples:
      - name: Delete
        text: |-
               az devcenter dev dev-box delete --name "MyDevBox" --dev-center-name "ContosoDevCenter"  \
               --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box show-remote-connection"
] = """
    type: command
    short-summary: "Gets remote connection info."
    examples:
      - name: Get remote connection
        text: |-
               az devcenter dev dev-box show-remote-connection --name "MyDevBox" --dev-center-name "ContosoDevCenter" \
               --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box start"
] = """
    type: command
    short-summary: "Starts a dev box."
    examples:
      - name: Start
        text: |-
               az devcenter dev dev-box start --name "MyDevBox" --dev-center-name "ContosoDevCenter" \
               --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box restart"
] = """
    type: command
    short-summary: "Restarts a dev box."
    examples:
      - name: Restart
        text: |-
               az devcenter dev dev-box restart --name "MyDevBox" --dev-center-name "ContosoDevCenter" \
               --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box stop"
] = """
    type: command
    short-summary: "Stops a dev box."
    examples:
      - name: Stop
        text: |-
               az devcenter dev dev-box stop --name "MyDevBox" --dev-center-name "ContosoDevCenter" \
               --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000" --hibernate "true"
"""

helps[
    "devcenter dev dev-box list-action"
] = """
    type: command
    short-summary: "Lists actions on a dev box."
    examples:
      - name: List actions
        text: |-
               az devcenter dev dev-box list-action --dev-center-name "ContosoDevCenter" \
--project-name "DevProject" --name "myDevBox" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box delay-action"
] = """
    type: command
    short-summary: "Delays an action."
    examples:
      - name: Delay action
        text: |-
               az devcenter dev dev-box delay-action --dev-center-name "ContosoDevCenter" \
--project-name "DevProject" --delay-time "04:30" --name "myDevBox" \
--action-name "schedule-default" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box delay-all-actions"
] = """
    type: command
    short-summary: "Delays all actions."
    examples:
      - name: Delay all actions
        text: |-
               az devcenter dev dev-box delay-all-actions --dev-center-name "ContosoDevCenter" \
--project-name "DevProject" --delay-time "04:30" --name "myDevBox" \
--user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box show-action"
] = """
    type: command
    short-summary: "Gets an action."
    examples:
      - name: Get action
        text: |-
               az devcenter dev dev-box show-action --dev-center-name "ContosoDevCenter" \
--project-name "DevProject" --name "myDevBox" --action-name \
"schedule-default" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box skip-action"
] = """
    type: command
    short-summary: "Skips an action."
    examples:
      - name: Skip action
        text: |-
               az devcenter dev dev-box skip-action --dev-center-name "ContosoDevCenter" \
--project-name "DevProject" --name "myDevBox" --action-name \
"schedule-default" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev environment"
] = """
    type: group
    short-summary: Manage environments.
"""

helps[
    "devcenter dev environment list"
] = """
    type: command
    short-summary: "Lists the environments for a project or lists the environments for a user within a project."
    examples:
      - name: List by project
        text: |-
              az devcenter dev environment list --dev-center-name "ContosoDevCenter" \
--project-name "DevProject"
      - name: List by user and project
        text: |-
               az devcenter dev environment list --dev-center-name "ContosoDevCenter" \
--project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev environment show"
] = """
    type: command
    short-summary: "Gets an environment."
    examples:
      - name: Get
        text: |-
              az devcenter dev environment show --dev-center-name "ContosoDevCenter" \
--name "mydevenv" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev environment create"
] = """
    type: command
    short-summary: "Create an environment."
    examples:
      - name: Create
        text: |-
               az devcenter dev environment create --dev-center-name "ContosoDevCenter" --project-name "DevProject" \
--catalog-name "main" --environment-definition-name "helloworld" --environment-type "DevTest" --parameters "{\\"functionAppRuntime\\":\\"node\
\\",\\"storageAccountType\\":\\"Standard_LRS\\"}" --name "mydevenv" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev environment update"
] = """
    type: command
    short-summary: "Updates an environment."
    examples:
      - name: Update
        text: |-
               az devcenter dev environment update --dev-center-name "ContosoDevCenter" --project-name "DevProject" \
--name "mydevenv" --user-id "00000000-0000-0000-0000-000000000000" --parameters "{\\"functionAppRuntime\\":\\"node\
\\",\\"storageAccountType\\":\\"Standard_LRS\\"}"
"""

helps[
    "devcenter dev environment delete"
] = """
    type: command
    short-summary: "Deletes an environment and all its associated resources."
    examples:
      - name: Delete
        text: |-
              az devcenter dev environment delete --dev-center-name "ContosoDevCenter"  \
              --name "mydevenv" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev catalog"
] = """
    type: group
    short-summary: Manage catalogs.
"""

helps[
    "devcenter dev catalog list"
] = """
    type: command
    short-summary: "Lists all of the catalogs available for a project."
    examples:
      - name: List
        text: |-
               az devcenter dev catalog list --dev-center-name "ContosoDevCenter" \
               --project-name "DevProject"
"""

helps[
    "devcenter dev catalog show"
] = """
    type: command
    short-summary: "Gets the specified catalog within the project."
    examples:
      - name: Get
        text: |-
               az devcenter dev catalog show --dev-center-name "ContosoDevCenter" \
               --project-name "DevProject" --catalog-name "foo"
"""

helps[
    "devcenter dev environment-type"
] = """
    type: group
    short-summary: Manage environment types.
"""

helps[
    "devcenter dev environment-type list"
] = """
    type: command
    short-summary: "Lists all environment types configured for a project."
    examples:
      - name: List
        text: |-
               az devcenter dev environment-type list --dev-center-name "ContosoDevCenter"  \
              --project-name "DevProject"
"""

helps[
    "devcenter dev environment-definition"
] = """
    type: group
    short-summary: Manage environment definitions.
"""

helps[
    "devcenter dev environment-definition list"
] = """
    type: command
    short-summary: "Lists all environment definitions available within a catalog or lists all environment \
definitions available for a project."
    examples:
      - name: List by catalog
        text: |-
               az devcenter dev environment-definition list --dev-center-name "ContosoDevCenter"  \
--project-name "DevProject" --catalog-name "myCatalog"
      - name: List
        text: |-
               az devcenter dev environment-definition list --dev-center-name "ContosoDevCenter"  \
--project-name "DevProject"
"""

helps[
    "devcenter dev environment-definition show"
] = """
    type: command
    short-summary: "Get an environment definition from a catalog."
    examples:
      - name: Get
        text: |-
               az devcenter dev environment-definition show --dev-center-name "ContosoDevCenter"  \
--project-name "DevProject" --catalog-name "myCatalog" --definition-name "foo"
"""
