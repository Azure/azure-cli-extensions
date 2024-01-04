# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

helps['mysql flexible-server connect'] = """
type: command
short-summary: Connect to a flexible server.
example:
  - name: Connect to a flexible server using administrator username and password. Default database is used if not specified.
    text: az mysql flexible-server connect -n testServer -u username -p password -d flexibleserverdb
  - name: Connect to a flexible server and run queries interactively.
    text: az mysql flexible-server connect -n testServer -u username --interactive
"""

helps['postgres flexible-server connect'] = """
type: command
short-summary: Connect to a flexible server.
example:
  - name: Connect to a flexible server using administrator username and password. Default database is used if not specified.
    text: az postgres flexible-server connect -n testServer -u username -p password -d postgres
  - name: Connect to a flexible server and run queries interactively.
    text: az postgres flexible-server connect -n testServer -u username --interactive
"""

helps['mysql flexible-server execute'] = """
type: command
short-summary: Connect to a flexible server.
example:
  - name: Connect to a flexible server and execute a query with results outputted in a table.
    text: az mysql flexible-server execute -n testServer -u username -p password --querytext "select host, user from mysql.user;" --output table
  - name: Connect to a flexible server and execute a sql file.
    text: az mysql flexible-server execute -n testServer -u username -p password --file-path path_to_sql_file
"""

helps['postgres flexible-server execute'] = """
type: command
short-summary: Connect to a flexible server.
example:
  - name: Connect to a flexible server and execute a query with results outputted in a table.
    text: az postgres flexible-server execute -n testServer -u username -p password --querytext "select * from pg_user;" --output table
  - name: Connect to a flexible server and execute a sql file.
    text: az mysql flexible-server execute -n testServer -u username -p password --file-path path_to_sql_file
"""
