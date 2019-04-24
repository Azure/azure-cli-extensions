# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps


helps['mysql up'] = """
    type: command
    short-summary: Set up an Azure Database for MySQL server and configurations.
    examples:
        - name: Ensure that a Azure Database for MySQL server is up and running and configured for immediate use.
          text: az mysql up
        - name: To override default names, provide parameters indicating desired values/existing resources.
          text: az mysql up -g MyResourceGroup -s MyServer -d MyDatabase -u MyUsername -p MyPassword
"""

helps['postgres up'] = """
    type: command
    short-summary: Set up an Azure Database for PostgreSQL server and configurations.
    examples:
        - name: Ensure that a Azure Database for PostgreSQL server is up and running and configured for immediate use.
          text: az postgres up
        - name: To override default names, provide parameters indicating desired values/existing resources.
          text: az postgres up -g MyResourceGroup -s MyServer -d MyDatabase -u MyUsername -p MyPassword
"""

helps['sql up'] = """
    type: command
    short-summary: Set up an Azure Database for SQL server and configurations.
    examples:
        - name: Ensure that a Azure Database for SQL server is up and running and configured for immediate use.
          text: az sql up
        - name: To override default names, provide parameters indicating desired values/existing resources.
          text: az sql up -g MyResourceGroup -s MyServer -d MyDatabase -u MyUsername -p MyPassword
"""

helps['mysql down'] = """
    type: command
    short-summary: Delete the MySQL server and its cached information.
    examples:
        - name: Delete the server and the cached data, aside from the resource group.
          text: az mysql down
        - name: Delete the resource group and the full cache.
          text: az mysql down --delete-group
"""

helps['postgres down'] = """
    type: command
    short-summary: Delete the PostgreSQL server and its cached information.
    examples:
        - name: Delete the server and the cached data, aside from the resource group.
          text: az postgres down
        - name: Delete the resource group and the full cache.
          text: az postgres down --delete-group
"""

helps['sql down'] = """
    type: command
    short-summary: Delete the SQL server and its cached information.
    examples:
        - name: Delete the server and the cached data, aside from the resource group.
          text: az sql down
        - name: Delete the resource group and the full cache.
          text: az sql down --delete-group
"""

helps['mysql show-connection-string'] = """
    type: command
    short-summary: Show the connection strings for a MySQL server database.
"""

helps['postgres show-connection-string'] = """
    type: command
    short-summary: Show the connection strings for a PostgreSQL server database.
"""
