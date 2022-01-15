# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['grafana'] = """
    type: group
    short-summary: Commands to manage Azure Managed Workspace for Grafana.
"""

helps['grafana create'] = """
    type: command
    short-summary: Create a Azure Managed Workspace for Grafana.
"""

helps['grafana list'] = """
    type: command
    short-summary: List Azure Managed Workspace for Grafana.
"""

helps['grafana delete'] = """
    type: command
    short-summary: Delete a Azure Managed Workspace for Grafana.
"""

helps['grafana show'] = """
    type: command
    short-summary: Show details of a Azure Managed Workspace for Grafana.
"""

helps['grafana update'] = """
     type: command
     short-summary: Update a Azure Managed Workspace for Grafana.
 """

helps['grafana show'] = """
    type: command
    short-summary: Show details of a Azure Managed Workspace for Grafana.
"""

helps['grafana data-source'] = """
    type: group
    short-summary: Commands to manage data sources of an instance.
"""

helps['grafana data-source create'] = """
    type: group
    short-summary: Create a data source.
"""

helps['grafana data-source list'] = """
    type: group
    short-summary: List all data sources of an instance.
"""

helps['grafana dashboard'] = """
    type: group
    short-summary: Commands to manage dashboards of an instance.
"""

helps['grafana dashboard create'] = """
    type: group
    short-summary: Create a new dashboard.
    examples:
        - name: Create a dashboard with definition in a json file. For quick start, clone from the output of "az grafana dashboard show", remove "id" and "uid", and apply changes.
          text: |
            az grafana dashboard create -g MyResourceGroup -n MyGrafana --dashboard-definition @c:\\temp\\dashboard.json
"""

helps['grafana dashboard update'] = """
    type: group
    short-summary: Update a new dashboard.
    examples:
        - name: Update a dashboard with definition in a json file. For quick start, get existing configuration from "az grafana dashboard show", and apply changes.
                "version" field need to be updated, and "overwrite" field should be true.
          text: |
            az grafana dashboard update -g MyResourceGroup -n MyGrafana --dashboard-definition @c:\\temp\\dashboard.json
"""

helps['grafana dashboard list'] = """
    type: group
    short-summary: List all dashboards of an instance.
    examples:
        - name: Find the dashboard for K8s API Server and retrieve the unique identifier(in order to invoke "az grafana dashboard show" command)
          text: |
           az grafana dashboard list -g MyResourceGroup -n MyGrafana --query "[?contains(@.title, 'API server')].uid"
"""

helps['grafana dashboard show'] = """
    type: group
    short-summary: show the detail of a dashboard.
    examples:
        - name: Get details of a dashboard specified by an unique identifier(use "az grafana dashboard list" command to retrieve the uid)
          text: |
           az grafana dashboard show -g MyResourceGroup -n MyGrafana --uid VdrOA7jGz
        - name: Get home dashboard
          text: |
           az grafana dashboard show -g MyResourceGroup -n MyGrafana --show-home-dashboard
"""

helps['grafana dashboard delete'] = """
    type: group
    short-summary: delete a dashboard
    examples:
        - name: Delete a dashboard specified by an unique identifier(use "az grafana dashboard list" command to retrieve the uid)
          text: |
           az grafana dashboard delete -g MyResourceGroup -n MyGrafana --uid VdrOA7jGz
"""
