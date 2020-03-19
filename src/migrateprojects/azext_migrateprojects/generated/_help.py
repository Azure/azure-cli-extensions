# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from knack.help_files import helps


helps['migrateprojects database-instance'] = """
    type: group
    short-summary: migrateprojects database-instance
"""

helps['migrateprojects database-instance show'] = """
    type: command
    short-summary: Gets a database instance in the migrate project.
    examples:
      - name: DatabaseInstances_Get
        text: |-
               az migrateprojects database-instance show --database-instance-name "myinstance"
               --migrate-project-name "project01" --resource-group "myResourceGroup"
"""

helps['migrateprojects database-instance enumerate-database-instance'] = """
    type: command
    short-summary: Gets a list of database instances in the migrate project.
    examples:
      - name: DatabaseInstances_List
        text: |-
               az migrateprojects database-instance enumerate-database-instance --migrate-project-name
               "project01" --resource-group "myResourceGroup"
"""

helps['migrateprojects database'] = """
    type: group
    short-summary: migrateprojects database
"""

helps['migrateprojects database show'] = """
    type: command
    short-summary: Gets a database in the migrate project.
    examples:
      - name: Databases_Get
        text: |-
               az migrateprojects database show --database-name "mydb" --migrate-project-name
               "project01" --resource-group "myResourceGroup"
"""

helps['migrateprojects database enumerate-database'] = """
    type: command
    short-summary: Gets a list of databases in the migrate project.
    examples:
      - name: Databases_List
        text: |-
               az migrateprojects database enumerate-database --migrate-project-name "project01"
               --resource-group "myResourceGroup"
"""

helps['migrateprojects event'] = """
    type: group
    short-summary: migrateprojects event
"""

helps['migrateprojects event show'] = """
    type: command
    short-summary: Gets an event in the migrate project.
    examples:
      - name: MigrateEvents_Get
        text: |-
               az migrateprojects event show --event-name "MigrateEvent01" --migrate-project-name
               "project01" --resource-group "myResourceGroup"
"""

helps['migrateprojects event delete'] = """
    type: command
    short-summary: Delete the migrate event. Deleting non-existent migrate event is a no-operation.
    examples:
      - name: MigrateEvents_Delete
        text: |-
               az migrateprojects event delete --event-name "MigrateEvent01" --migrate-project-name
               "project01" --resource-group "myResourceGroup"
"""

helps['migrateprojects event enumerate-event'] = """
    type: command
    short-summary: Gets a list of events in the migrate project.
    examples:
      - name: MigrateEvents_List
        text: |-
               az migrateprojects event enumerate-event --migrate-project-name "project01"
               --resource-group "myResourceGroup"
"""

helps['migrateprojects machine'] = """
    type: group
    short-summary: migrateprojects machine
"""

helps['migrateprojects machine show'] = """
    type: command
    short-summary: Gets a machine in the migrate project.
    examples:
      - name: Machines_Get
        text: |-
               az migrateprojects machine show --machine-name "vm1" --migrate-project-name "project01"
               --resource-group "myResourceGroup"
"""

helps['migrateprojects machine enumerate-machine'] = """
    type: command
    short-summary: Gets a list of machines in the migrate project.
    examples:
      - name: Machines_List
        text: |-
               az migrateprojects machine enumerate-machine --migrate-project-name "project01"
               --resource-group "myResourceGroup"
"""

helps['migrateprojects migrate-project'] = """
    type: group
    short-summary: migrateprojects migrate-project
"""

helps['migrateprojects migrate-project show'] = """
    type: command
    short-summary: Method to get a migrate project.
    examples:
      - name: MigrateProjects_Get
        text: |-
               az migrateprojects migrate-project show --migrate-project-name "project01"
               --resource-group "myResourceGroup"
"""

helps['migrateprojects migrate-project delete'] = """
    type: command
    short-summary: Delete the migrate project. Deleting non-existent project is a no-operation.
    examples:
      - name: MigrateProjects_Delete
        text: |-
               az migrateprojects migrate-project delete --migrate-project-name "project01"
               --resource-group "myResourceGroup"
"""

helps['migrateprojects migrate-project put-migrate-project'] = """
    type: command
    short-summary: Method to create or update a migrate project.
    examples:
      - name: MigrateProjects_Put
        text: |-
               az migrateprojects migrate-project put-migrate-project --e-tag
               "\\"b701c73a-0000-0000-0000-59c12ff00000\\"" --location "Southeast Asia" --properties "{}"
               --migrate-project-name "project01" --resource-group "myResourceGroup"
"""

helps['migrateprojects migrate-project patch-migrate-project'] = """
    type: command
    short-summary: Update a migrate project with specified name. Supports partial updates, for example only tags can be provided.
    examples:
      - name: MigrateProjects_Patch
        text: |-
               az migrateprojects migrate-project patch-migrate-project --e-tag
               "\\"b701c73a-0000-0000-0000-59c12ff00000\\"" --location "Southeast Asia" --properties
               "{\\"registeredTools\\":[\\"ServerMigration\\"]}" --migrate-project-name "project01"
               --resource-group "myResourceGroup"
"""

helps['migrateprojects migrate-project register-tool'] = """
    type: command
    short-summary: Registers a tool with the migrate project.
    examples:
      - name: MigrateProjects_RegisterTool
        text: |-
               az migrateprojects migrate-project register-tool --tool "ServerMigration"
               --migrate-project-name "project01" --resource-group "myResourceGroup"
"""

helps['migrateprojects migrate-project refresh-migrate-project-summary'] = """
    type: command
    short-summary: Refresh the summary of the migrate project.
    examples:
      - name: MigrateProjects_RefreshSummary
        text: |-
               az migrateprojects migrate-project refresh-migrate-project-summary --goal "Servers"
               --migrate-project-name "project01" --resource-group "myResourceGroup"
"""

helps['migrateprojects solution'] = """
    type: group
    short-summary: migrateprojects solution
"""

helps['migrateprojects solution show'] = """
    type: command
    short-summary: Gets a solution in the migrate project.
    examples:
      - name: Solutions_Get
        text: |-
               az migrateprojects solution show --migrate-project-name "project01" --resource-group
               "myResourceGroup" --solution-name "dbsolution"
"""

helps['migrateprojects solution delete'] = """
    type: command
    short-summary: Delete the solution. Deleting non-existent project is a no-operation.
    examples:
      - name: Solutions_Delete
        text: |-
               az migrateprojects solution delete --migrate-project-name "project01" --resource-group
               "myResourceGroup" --solution-name "smssolution"
"""

helps['migrateprojects solution put-solution'] = """
    type: command
    short-summary: Creates a solution in the migrate project.
    examples:
      - name: Solutions_Put
        text: |-
               az migrateprojects solution put-solution --migrate-project-name "project01"
               --resource-group "myResourceGroup" --properties
               "{\\"goal\\":\\"Databases\\",\\"purpose\\":\\"Assessment\\",\\"tool\\":\\"DataMigrationAssistant\\"}"
               --solution-name "dbsolution"
"""

helps['migrateprojects solution patch-solution'] = """
    type: command
    short-summary: Update a solution with specified name. Supports partial updates, for example only tags can be provided.
    examples:
      - name: Solutions_Patch
        text: |-
               az migrateprojects solution patch-solution --migrate-project-name "project01"
               --resource-group "myResourceGroup" --properties "{\\"status\\":\\"Active\\"}" --solution-name
               "dbsolution"
"""

helps['migrateprojects solution get-config'] = """
    type: command
    short-summary: Gets the config for the solution in the migrate project.
    examples:
      - name: Solutions_GetConfig
        text: |-
               az migrateprojects solution get-config --migrate-project-name "project01"
               --resource-group "myResourceGroup" --solution-name "smssolution"
"""

helps['migrateprojects solution cleanup-solution-data'] = """
    type: command
    short-summary: Cleanup the solution data in the migrate project.
    examples:
      - name: Solutions_CleanupData
        text: |-
               az migrateprojects solution cleanup-solution-data --migrate-project-name "project01"
               --resource-group "myResourceGroup" --solution-name "smssolution"
"""

helps['migrateprojects solution enumerate-solution'] = """
    type: command
    short-summary: Gets the list of solutions in the migrate project.
    examples:
      - name: Solutions_List
        text: |-
               az migrateprojects solution enumerate-solution --migrate-project-name "project01"
               --resource-group "myResourceGroup"
"""
