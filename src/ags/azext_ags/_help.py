# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['grafana'] = """
    type: group
    short-summary: Commands to manage Azure Managed Dashboard for Grafanas.
"""

helps['grafana create'] = """
    type: command
    short-summary: Create a Azure Managed Dashboard for Grafana.
"""

helps['grafana list'] = """
    type: command
    short-summary: List Azure Managed Dashboard for Grafanas.
"""

helps['grafana delete'] = """
    type: command
    short-summary: Delete a Azure Managed Dashboard for Grafana.
"""

helps['grafana show'] = """
    type: command
    short-summary: Show details of a Azure Managed Dashboard for Grafana.
"""

# helps['grafana update'] = """
#     type: command
#     short-summary: Update a Azure Managed Dashboard for Grafana.
# """

helps['grafana show'] = """
    type: command
    short-summary: Show details of a Azure Managed Dashboard for Grafana.
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
"""

helps['grafana dashboard list'] = """
    type: group
    short-summary: List all dashboards of an instance.
"""

helps['grafana dashboard show'] = """
    type: group
    short-summary: show the detail of a dashboard.
"""

helps['grafana dashboard delete'] = """
    type: group
    short-summary: delete a dashboard
"""