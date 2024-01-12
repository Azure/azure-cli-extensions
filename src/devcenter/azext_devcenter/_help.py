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
    short-summary: "Manage devcenter developer resources."
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
    short-summary: "List all projects."
    examples:
      - name: List using dev center
        text: |-
               az devcenter dev project list --dev-center-name "ContosoDevCenter"
      - name: List using endpoint
        text: |-
               az devcenter dev project list --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/"
"""

helps[
    "devcenter dev project show"
] = """
    type: command
    short-summary: "Get a project."
    examples:
      - name: Get using dev center
        text: |-
               az devcenter dev project show --dev-center-name "ContosoDevCenter" \
--name "DevProject"
      - name: Get using endpoint
        text: |-
               az devcenter dev project show --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
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
    short-summary: "List available pools."
    examples:
      - name: List using dev center
        text: |-
               az devcenter dev pool list --dev-center-name "ContosoDevCenter" \
--project-name "DevProject"
      - name: List using end point
        text: |-
               az devcenter dev pool list --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--project-name "DevProject"
"""

helps[
    "devcenter dev pool show"
] = """
    type: command
    short-summary: "Get a pool."
    examples:
      - name: Get using dev center
        text: |-
               az devcenter dev pool show --dev-center-name "ContosoDevCenter" --name \
"DevPool" --project-name "DevProject"
      - name: Get using endpoint
        text: |-
               az devcenter dev pool show --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" --name \
"DevPool" --project-name "DevProject"
"""

helps[
    "devcenter dev schedule"
] = """
    type: group
    short-summary: Manage schedules.
"""

helps[
    "devcenter dev schedule list"
] = """
    type: command
    short-summary: "List schedules."
    examples:
      - name: List schedules by project using dev center
        text: |-
               az devcenter dev schedule list --dev-center-name "ContosoDevCenter" \
--project-name "DevProject"
      - name: List schedules by project using endpoint
        text: |-
               az devcenter dev schedule list --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--project-name "DevProject"
      - name: List schedules by pool using dev center
        text: |-
               az devcenter dev schedule list --dev-center-name "ContosoDevCenter" \
--pool-name "DevPool" --project-name "DevProject"
      - name: List schedules by pool using endpoint
        text: |-
               az devcenter dev schedule list --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--pool-name "DevPool" --project-name "DevProject"
"""

helps[
    "devcenter dev schedule show"
] = """
    type: command
    short-summary: "Get a schedule."
    examples:
      - name: Get using dev center
        text: |-
               az devcenter dev schedule show --dev-center-name "ContosoDevCenter" \
--pool-name "DevPool" --project-name "DevProject"
      - name: Get using endpoint
        text: |-
               az devcenter dev schedule show --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
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
    short-summary: "List dev boxes for a user, list dev boxes in the dev center for a \
project and user, or list dev boxes that the caller has access to in the dev center."
    examples:
      - name: List all dev boxes in the dev center
        text: |-
               az devcenter dev dev-box list --dev-center-name "ContosoDevCenter"
      - name: List all dev boxes in the dev center using endpoint
        text: |-
               az devcenter dev dev-box list --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/"
      - name: List by user using dev center
        text: |-
               az devcenter dev dev-box list --dev-center-name "ContosoDevCenter" \
--user-id "00000000-0000-0000-0000-000000000000"
      - name: List by user using endpoint
        text: |-
               az devcenter dev dev-box list --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--user-id "00000000-0000-0000-0000-000000000000"
      - name: List by user and project using dev center
        text: |-
               az devcenter dev dev-box list --dev-center-name "ContosoDevCenter" \
--project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
      - name: List by user and project using endpoint
        text: |-
               az devcenter dev dev-box list --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box show"
] = """
    type: command
    short-summary: "Get a dev box."
    examples:
      - name: Get using dev center
        text: |-
               az devcenter dev dev-box show --name "MyDevBox" --dev-center-name "ContosoDevCenter" \
               --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
      - name: Get using endpoint
        text: |-
               az devcenter dev dev-box show --name "MyDevBox" --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box create"
] = """
    type: command
    short-summary: "Create a dev box."
    examples:
      - name: Create using dev center
        text: |-
               az devcenter dev dev-box create --pool-name "LargeDevWorkStationPool" --name "MyDevBox" --dev-center-name \
"ContosoDevCenter" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
      - name: Create using endpoint
        text: |-
               az devcenter dev dev-box create --pool-name "LargeDevWorkStationPool" --name "MyDevBox" --endpoint \
"https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box delete"
] = """
    type: command
    short-summary: "Delete a dev box."
    examples:
      - name: Delete using dev center
        text: |-
               az devcenter dev dev-box delete --name "MyDevBox" --dev-center-name "ContosoDevCenter" \
               --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
      - name: Delete using endpoint
        text: |-
               az devcenter dev dev-box delete --name "MyDevBox" --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box show-remote-connection"
] = """
    type: command
    short-summary: "Get remote connection info."
    examples:
      - name: Get remote connection using dev center
        text: |-
               az devcenter dev dev-box show-remote-connection --name "MyDevBox" --dev-center-name "ContosoDevCenter" \
--project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
      - name: Get remote connection using dev center
        text: |-
               az devcenter dev dev-box show-remote-connection --name "MyDevBox" --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box start"
] = """
    type: command
    short-summary: "Start a dev box."
    examples:
      - name: Start using dev center
        text: |-
               az devcenter dev dev-box start --name "MyDevBox" --dev-center-name "ContosoDevCenter" \
               --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
      - name: Start using endpoint
        text: |-
               az devcenter dev dev-box start --name "MyDevBox" --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box restart"
] = """
    type: command
    short-summary: "Restart a dev box."
    examples:
      - name: Restart using dev center
        text: |-
               az devcenter dev dev-box restart --name "MyDevBox" --dev-center-name "ContosoDevCenter" \
               --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
      - name: Restart using endpoint
        text: |-
               az devcenter dev dev-box restart --name "MyDevBox" --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box repair"
] = """
    type: command
    short-summary: "Attempts automated repair steps to resolve common problems on a Dev Box. The dev box may restart during this operation."
    examples:
      - name: Repair using dev center
        text: |-
               az devcenter dev dev-box repair --name "MyDevBox" --dev-center-name "ContosoDevCenter" \
               --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
      - name: Repair using endpoint
        text: |-
               az devcenter dev dev-box repair --name "MyDevBox" --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box stop"
] = """
    type: command
    short-summary: "Stop a dev box."
    examples:
      - name: Stop using dev center
        text: |-
               az devcenter dev dev-box stop --name "MyDevBox" --dev-center-name "ContosoDevCenter" \
               --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
      - name: Stop using endpoint
        text: |-
               az devcenter dev dev-box stop --name "MyDevBox" --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box list-action"
] = """
    type: command
    short-summary: "List actions on a dev box."
    examples:
      - name: List actions using dev center
        text: |-
               az devcenter dev dev-box list-action --dev-center-name "ContosoDevCenter" \
--project-name "DevProject" --name "myDevBox" --user-id "00000000-0000-0000-0000-000000000000"
      - name: List actions using endpoint
        text: |-
               az devcenter dev dev-box list-action --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--project-name "DevProject" --name "myDevBox" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box delay-action"
] = """
    type: command
    short-summary: "Delay an action."
    examples:
      - name: Delay action using dev center
        text: |-
               az devcenter dev dev-box delay-action --dev-center-name "ContosoDevCenter" \
--project-name "DevProject" --delay-time "04:30" --name "myDevBox" \
--action-name "schedule-default" --user-id "00000000-0000-0000-0000-000000000000"
      - name: Delay action using endpoint
        text: |-
               az devcenter dev dev-box delay-action --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--project-name "DevProject" --delay-time "04:30" --name "myDevBox" \
--action-name "schedule-default" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box delay-all-actions"
] = """
    type: command
    short-summary: "Delay all actions."
    examples:
      - name: Delay all actions using dev center
        text: |-
               az devcenter dev dev-box delay-all-actions --dev-center-name "ContosoDevCenter" \
--project-name "DevProject" --delay-time "04:30" --name "myDevBox" \
--user-id "00000000-0000-0000-0000-000000000000"
      - name: Delay all actions using endpoint
        text: |-
               az devcenter dev dev-box delay-all-actions --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--project-name "DevProject" --delay-time "04:30" --name "myDevBox" \
--user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box list-operation"
] = """
    type: command
    short-summary: "Lists operations on the dev box which have occurred within the past 90 days."
    examples:
      - name: List operations using dev center
        text: |-
               az devcenter dev dev-box list-operation --dev-center-name "ContosoDevCenter" \
--project-name "DevProject" --name "myDevBox" --user-id "00000000-0000-0000-0000-000000000000"
      - name: List operations using endpoint
        text: |-
               az devcenter dev dev-box list-operation --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--project-name "DevProject" --name "myDevBox" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box show-operation"
] = """
    type: command
    short-summary: "Get an operation on a dev box."
    examples:
      - name: Get operation using dev center
        text: |-
               az devcenter dev dev-box show-operation --dev-center-name "ContosoDevCenter" \
--project-name "DevProject" --name "myDevBox" --operation-id \
"f5dbdfab-fa0e-4831-8d13-25359aa5e680" --user-id "00000000-0000-0000-0000-000000000000"
      - name: Get operation using endpoint
        text: |-
               az devcenter dev dev-box show-operation --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--project-name "DevProject" --name "myDevBox" --operation-id \
"f5dbdfab-fa0e-4831-8d13-25359aa5e680" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box show-action"
] = """
    type: command
    short-summary: "Get an action."
    examples:
      - name: Get action using dev center
        text: |-
               az devcenter dev dev-box show-action --dev-center-name "ContosoDevCenter" \
--project-name "DevProject" --name "myDevBox" --action-name \
"schedule-default" --user-id "00000000-0000-0000-0000-000000000000"
      - name: Get action using endpoint
        text: |-
               az devcenter dev dev-box show-action --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--project-name "DevProject" --name "myDevBox" --action-name \
"schedule-default" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev dev-box skip-action"
] = """
    type: command
    short-summary: "Skip an action."
    examples:
      - name: Skip action using dev center
        text: |-
               az devcenter dev dev-box skip-action --dev-center-name "ContosoDevCenter" \
--project-name "DevProject" --name "myDevBox" --action-name \
"schedule-default" --user-id "00000000-0000-0000-0000-000000000000"
      - name: Skip action using endpoint
        text: |-
               az devcenter dev dev-box skip-action --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
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
    short-summary: "List the environments for a project or list the environments for a user within a project."
    examples:
      - name: List by project using dev center
        text: |-
              az devcenter dev environment list --dev-center-name "ContosoDevCenter" \
--project-name "DevProject"
      - name: List by project using endpoint
        text: |-
              az devcenter dev environment list --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--project-name "DevProject"
      - name: List by user and project using dev center
        text: |-
               az devcenter dev environment list --dev-center-name "ContosoDevCenter" \
--project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
      - name: List by user and project using endpoint
        text: |-
               az devcenter dev environment list --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev environment show"
] = """
    type: command
    short-summary: "Get an environment."
    examples:
      - name: Get using dev center
        text: |-
              az devcenter dev environment show --dev-center-name "ContosoDevCenter" \
--name "mydevenv" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
    examples:
      - name: Get using endpoint
        text: |-
              az devcenter dev environment show --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--name "mydevenv" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev environment create"
] = """
    type: command
    short-summary: "Create an environment."
    examples:
      - name: Create using dev center
        text: |-
               az devcenter dev environment create --dev-center-name "ContosoDevCenter" --project-name "DevProject" \
--catalog-name "main" --environment-definition-name "helloworld" --environment-type "DevTest" --parameters "{\\"functionAppRuntime\\":\\"node\
\\",\\"storageAccountType\\":\\"Standard_LRS\\"}" --name "mydevenv" --user-id "00000000-0000-0000-0000-000000000000"
      - name: Create using endpoint
        text: |-
               az devcenter dev environment create --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" --project-name "DevProject" \
--catalog-name "main" --environment-definition-name "helloworld" --environment-type "DevTest" --parameters "{\\"functionAppRuntime\\":\\"node\
\\",\\"storageAccountType\\":\\"Standard_LRS\\"}" --name "mydevenv" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev environment update"
] = """
    type: command
    short-summary: "Update an environment."
    examples:
      - name: Update using dev center
        text: |-
               az devcenter dev environment update --dev-center-name "ContosoDevCenter" --project-name "DevProject" \
--name "mydevenv" --user-id "00000000-0000-0000-0000-000000000000" --parameters "{\\"functionAppRuntime\\":\\"node\
\\",\\"storageAccountType\\":\\"Standard_LRS\\"}"
      - name: Update using endpoint
        text: |-
               az devcenter dev environment update --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" --project-name "DevProject" \
--name "mydevenv" --user-id "00000000-0000-0000-0000-000000000000" --parameters "{\\"functionAppRuntime\\":\\"node\
\\",\\"storageAccountType\\":\\"Standard_LRS\\"}"
"""

helps[
    "devcenter dev environment deploy"
] = """
    type: command
    short-summary: "Update an environment."
    examples:
      - name: Update using dev center
        text: |-
               az devcenter dev environment deploy --dev-center-name "ContosoDevCenter" --project-name "DevProject" \
--name "mydevenv" --user-id "00000000-0000-0000-0000-000000000000" --parameters "{\\"functionAppRuntime\\":\\"node\
\\",\\"storageAccountType\\":\\"Standard_LRS\\"}"
      - name: Update using endpoint
        text: |-
               az devcenter dev environment deploy --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" --project-name "DevProject" \
--name "mydevenv" --user-id "00000000-0000-0000-0000-000000000000" --parameters "{\\"functionAppRuntime\\":\\"node\
\\",\\"storageAccountType\\":\\"Standard_LRS\\"}"
"""

helps[
    "devcenter dev environment delete"
] = """
    type: command
    short-summary: "Delete an environment and all its associated resources."
    examples:
      - name: Delete using dev center
        text: |-
              az devcenter dev environment delete --dev-center-name "ContosoDevCenter"  \
--name "mydevenv" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
      - name: Delete using endpoint
        text: |-
              az devcenter dev environment delete --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
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
    short-summary: "List all of the catalogs available for a project."
    examples:
      - name: List using dev center
        text: |-
               az devcenter dev catalog list --dev-center-name "ContosoDevCenter" \
--project-name "DevProject"
      - name: List using endpoint
        text: |-
               az devcenter dev catalog list --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--project-name "DevProject"
"""

helps[
    "devcenter dev catalog show"
] = """
    type: command
    short-summary: "Get the specified catalog within the project."
    examples:
      - name: Get using dev center
        text: |-
               az devcenter dev catalog show --dev-center-name "ContosoDevCenter" \
--project-name "DevProject" --catalog-name "foo"
      - name: Get using endpoint
        text: |-
               az devcenter dev catalog show --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
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
    short-summary: "List all environment types configured for a project."
    examples:
      - name: List using dev center
        text: |-
               az devcenter dev environment-type list --dev-center-name "ContosoDevCenter" \
--project-name "DevProject"
      - name: List using endpoint
        text: |-
               az devcenter dev environment-type list --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
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
    short-summary: "List all environment definitions available within a catalog or list all environment \
definitions available for a project."
    examples:
      - name: List using dev center
        text: |-
               az devcenter dev environment-definition list --dev-center-name "ContosoDevCenter" \
--project-name "DevProject"
      - name: List using endpoint
        text: |-
               az devcenter dev environment-definition list --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--project-name "DevProject"
      - name: List by catalog using dev center
        text: |-
               az devcenter dev environment-definition list --dev-center-name "ContosoDevCenter" \
--project-name "DevProject" --catalog-name "myCatalog"
      - name: List by catalog using endpoint
        text: |-
               az devcenter dev environment-definition list --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--project-name "DevProject" --catalog-name "myCatalog"
"""

helps[
    "devcenter dev environment-definition show"
] = """
    type: command
    short-summary: "Get an environment definition from a catalog."
    examples:
      - name: Get using dev center
        text: |-
               az devcenter dev environment-definition show --dev-center-name "ContosoDevCenter" \
--project-name "DevProject" --catalog-name "myCatalog" --definition-name "foo"
      - name: Get using endpoint
        text: |-
               az devcenter dev environment-definition show --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--project-name "DevProject" --catalog-name "myCatalog" --definition-name "foo"
"""

helps[
    "devcenter dev environment list-operation"
] = """
    type: command
    short-summary: "Lists operations on the environment which have occurred within the past 90 days."
    examples:
      - name: List using dev center
        text: |-
              az devcenter dev environment list-operation --dev-center-name "ContosoDevCenter" \
--name "mydevenv" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
    examples:
      - name: List using endpoint
        text: |-
              az devcenter dev environment list-operation --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--name "mydevenv" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev environment show-operation"
] = """
    type: command
    short-summary: "Gets an environment action result."
    examples:
      - name: Get using dev center
        text: |-
              az devcenter dev environment show-operation --dev-center-name "ContosoDevCenter" \
--name "mydevenv" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000" --operation-id \
"f5dbdfab-fa0e-4831-8d13-25359aa5e680"
    examples:
      - name: Get using endpoint
        text: |-
              az devcenter dev environment show-operation --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--name "mydevenv" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000" --operation-id "f5dbdfab-fa0e-4831-8d13-25359aa5e680"
"""

helps[
    "devcenter dev environment show-logs-by-operation"
] = """
    type: command
    short-summary: "Gets the logs for an operation on an environment."
    examples:
      - name: Get using dev center
        text: |-
              az devcenter dev environment show-logs-by-operation --dev-center-name "ContosoDevCenter" \
--name "mydevenv" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000" --operation-id \
"f5dbdfab-fa0e-4831-8d13-25359aa5e680"
    examples:
      - name: Get using endpoint
        text: |-
              az devcenter dev environment show-logs-by-operation --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--name "mydevenv" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000" --operation-id "f5dbdfab-fa0e-4831-8d13-25359aa5e680"
"""

helps[
    "devcenter dev environment show-action"
] = """
    type: command
    short-summary: "Retrieve a specific environment action."
    examples:
      - name: Get using dev center
        text: |-
              az devcenter dev environment show-action --dev-center-name "ContosoDevCenter" \
--name "mydevenv" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000" --action-name \
"myEnv-Delete"
    examples:
      - name: Get using endpoint
        text: |-
              az devcenter dev environment show-action --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--name "mydevenv" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000" --action-name "myEnv-Delete"
"""

helps[
    "devcenter dev environment list-action"
] = """
    type: command
    short-summary: "List specific environment actions."
    examples:
      - name: List using dev center
        text: |-
              az devcenter dev environment list-action --dev-center-name "ContosoDevCenter" \
--name "mydevenv" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
    examples:
      - name: List using endpoint
        text: |-
              az devcenter dev environment list-action --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--name "mydevenv" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev environment delay-action"
] = """
    type: command
    short-summary: "Delay an environment action."
    examples:
      - name: Delay using dev center
        text: |-
              az devcenter dev environment delay-action --dev-center-name "ContosoDevCenter" \
--name "mydevenv" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000" --action-name \
"myEnv-Delete" --delay-time "04:30"
    examples:
      - name: Delay using endpoint
        text: |-
              az devcenter dev environment delay-action --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--name "mydevenv" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000" --action-name "myEnv-Delete" --delay-time "04:30"
"""

helps[
    "devcenter dev environment skip-action"
] = """
    type: command
    short-summary: "Skip a specific environment action."
    examples:
      - name: Skip using dev center
        text: |-
              az devcenter dev environment skip-action --dev-center-name "ContosoDevCenter" \
--name "mydevenv" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000" --action-name \
"myEnv-Delete"
    examples:
      - name: Skip using endpoint
        text: |-
              az devcenter dev environment skip-action --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--name "mydevenv" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000" --action-name "myEnv-Delete"
"""

helps[
    "devcenter dev environment show-outputs"
] = """
    type: command
    short-summary: "Gets outputs from the environment."
    examples:
      - name: Get using dev center
        text: |-
              az devcenter dev environment show-outputs --dev-center-name "ContosoDevCenter" \
--name "mydevenv" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
    examples:
      - name: Get using endpoint
        text: |-
              az devcenter dev environment show-outputs --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--name "mydevenv" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000"
"""

helps[
    "devcenter dev environment update-expiration-date"
] = """
    type: command
    short-summary: "Update the environment expiration"
    examples:
      - name: Get using dev center
        text: |-
              az devcenter dev environment update-expiration-date --dev-center-name "ContosoDevCenter" \
--name "mydevenv" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000" --expiration "2025-11-30T22:35:00+00:00"
    examples:
      - name: Get using endpoint
        text: |-
              az devcenter dev environment update-expiration-date --endpoint "https://8a40af38-3b4c-4672-a6a4-5e964b1870ed-contosodevcenter.centralus.devcenter.azure.com/" \
--name "mydevenv" --project-name "DevProject" --user-id "00000000-0000-0000-0000-000000000000" --expiration "2025-11-30T22:35:00+00:00"
"""
