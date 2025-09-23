# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['grafana backup'] = """
    type: command
    short-summary: Backup an Azure Managed Grafana instance's content to an archive.
    examples:
        - name: backup dashboards under 2 folders (data sources are included to enable name remapping when restore dashboards to another workspace)
          text: |
            az grafana backup -g MyResourceGroup -n MyGrafana -d c:\\temp --folders-to-include "Prod" "Compute Gateway" --components datasources dashboards folders
        - name: backup dashboards and skip a few folders
          text: |
            az grafana backup -g MyResourceGroup -n MyGrafana -d c:\\temp  --folders-to-exclude General "Azure Monitor" --components datasources dashboards folders

"""

helps['grafana restore'] = """
    type: command
    short-summary: Restore an Azure Managed Grafana instance from an archive.
    examples:
       - name: Restore dashboards. If they are under folders, include "folders" in the components list; use "--remap-data-sources" so CLI will update dashboards to point to same data sources at target workspace
         text: |
           az grafana restore -g MyResourceGroup -n MyGrafana --archive-file backup\\dashboards\\ServiceHealth-202307051036.tar.gz --components dashboards folders --remap-data-sources
"""

helps['grafana migrate'] = """
    type: command
    short-summary: Migrate an existing Grafana instance to an Azure Managed Grafana instance.
    examples:
       - name: Migrate dashboards and folders from a local Grafana instance to an Azure Managed Grafana instance.
         text: |
           az grafana migrate -g MyResourceGroup -n MyGrafana -s http://localhost:3000 -t YourServiceTokenOrAPIKey
"""


helps['grafana data-source'] = """
    type: group
    short-summary: Commands to manage data sources of an instance.
"""

helps['grafana data-source create'] = """
    type: command
    short-summary: Create a data source.
    examples:
        - name: create an Azure Monitor data source using Managed Identity
          text: |
            az grafana data-source create -n MyGrafana --definition '{
              "access": "proxy",
              "jsonData": {
                "azureAuthType": "msi",
                "subscriptionId": "3a7edf7d-1488-4017-a908-111111111111"
              },
              "name": "Azure Monitor-3",
              "type": "grafana-azure-monitor-datasource"
            }'
        - name: create an Azure Monitor data source using App Registration
          text: |
            az grafana data-source create -n MyGrafana --definition '{
              "name": "Azure Monitor-2",
              "type": "grafana-azure-monitor-datasource",
              "access": "proxy",
              "jsonData": {
                "subscriptionId": "3a7edf7d-1488-4017-a908-111111111111",
                "azureAuthType": "clientsecret",
                "cloudName": "azuremonitor",
                "tenantId": "72f988bf-86f1-41af-91ab-111111111111",
                "clientId": "fb31a2f5-9122-4be9-9705-111111111111"
              },
              "secureJsonData": { "clientSecret": "verySecret" }
            }'
        - name: create an Azure Data Explorer data source using Managed Identity
          text: |
            az grafana data-source create -n MyGrafana --definition '{
              "name": "Azure Data Explorer Datasource-2",
              "type": "grafana-azure-data-explorer-datasource",
              "access": "proxy",
              "jsonData": {
                "dataConsistency": "strongconsistency",
                "clusterUrl": "https://mykusto.westcentralus.kusto.windows.net"
              }
            }'
        - name: create an Azure Data Explorer data source using App Registration
          text: |
            az grafana data-source create -n MyGrafana --definition '{
              "name": "Azure Data Explorer Datasource-1",
              "type": "grafana-azure-data-explorer-datasource",
              "access": "proxy",
              "jsonData": {
                "clusterUrl": "https://mykusto.westcentralus.kusto.windows.net",
                "azureCredentials": {
                  "authType": "clientsecret",
                  "azureCloud": "AzureCloud",
                  "tenantId": "72f988bf-86f1-41af-91ab-111111111111",
                  "clientId": "fb31a2f5-9122-4be9-9705-111111111111"
                }
              },
              "secureJsonData": { "azureClientSecret": "verySecret" }
            }'
        - name: create an Azure Managed Prometheus data source using App Registration
          text: |
            az grafana data-source create -n MyGrafana --definition '{
              "name": "Azure Managed Prometheus-1",
              "type": "prometheus",
              "access": "proxy",
              "url": "https://myprom-abcd.westcentralus.prometheus.monitor.azure.com",
              "jsonData": {
                "httpMethod": "POST",
                "azureCredentials": {
                  "authType": "clientsecret",
                  "azureCloud": "AzureCloud",
                  "tenantId": "72f988bf-86f1-41af-91ab-111111111111",
                  "clientId": "fb31a2f5-9122-4be9-9705-111111111111"
                },
                "timeInterval": "30s"
              },
              "secureJsonData": { "azureClientSecret": "verySecret" }
            }'
        - name: create an Azure Managed Prometheus data source using managed identity
          text: |
            az grafana data-source create -n MyGrafana --definition '{
              "name": "Azure Managed Prometheus-1",
              "type": "prometheus",
              "access": "proxy",
              "url": "https://myprom-jryu.westcentralus.prometheus.monitor.azure.com",
              "jsonData": {
                "httpMethod": "POST",
                "azureCredentials": { "authType": "msi" }
              }
            }'
        - name: create an Azure SQL data source
          text: |
            az grafana data-source create -n MyGrafana --definition '{
              "access": "proxy",
              "database": "testdb",
              "jsonData": {
                "authenticationType": "SQL Server Authentication",
                "encrypt": "false"
              },
              "secureJsonData": {
                "password": "verySecretPassword"
              },
              "name": "Microsoft SQL Server",
              "type": "mssql",
              "url": "testsql.database.windows.net",
              "user": "admin1"
            }'
"""

helps['grafana data-source update'] = """
    type: command
    short-summary: Update a data source.
"""

helps['grafana data-source show'] = """
    type: command
    short-summary: Get the details of a data source
"""

helps['grafana data-source delete'] = """
    type: command
    short-summary: Delete a data source
"""

helps['grafana data-source list'] = """
    type: command
    short-summary: List all data sources of an instance.
"""

helps['grafana data-source query'] = """
    type: command
    short-summary: Query a data source having backend implementation
"""

helps['grafana notification-channel'] = """
    type: group
    short-summary: Commands to manage notification channels of an instance.
    long-summary: As part of Grafana legacy alerting, this command group only works with Grafana 10 and below.
"""

helps['grafana notification-channel list'] = """
    type: command
    short-summary: List all notification channels of an instance.
"""

helps['grafana notification-channel show'] = """
    type: command
    short-summary: Get the details of a notification channel
"""

helps['grafana notification-channel create'] = """
    type: command
    short-summary: Create a notification channel.
    examples:
        - name: create a notification channel for Teams
          text: |
            az grafana notification-channel create -n MyGrafana --definition '{
              "name": "Teams",
              "settings": {
                "uploadImage": true,
                "url": "https://webhook.office.com/IncomingWebhook/"
               },
              "type": "teams"
            }'
"""

helps['grafana notification-channel update'] = """
    type: command
    short-summary: Update a notification channel.
"""

helps['grafana notification-channel delete'] = """
    type: command
    short-summary: Delete a notification channel.
"""

helps['grafana notification-channel test'] = """
    type: command
    short-summary: Test a notification channel.
"""

helps['grafana dashboard'] = """
    type: group
    short-summary: Commands to manage dashboards of an instance.
"""

helps['grafana dashboard create'] = """
    type: command
    short-summary: Create a new dashboard.
    examples:
        - name: Create a dashboard with definition in a json file. For quick start, clone from the output of "az grafana dashboard show", remove "id" and "uid", and apply changes.
          text: |
            az grafana dashboard create -g MyResourceGroup -n MyGrafana --title "My dashboard" --folder folder1 --definition '{
              "dashboard": {
                "annotations": {
                    ...
                },
                "panels": {
                    ...
                }
              },
              "message": "Create a new test dashboard"
            }'
"""

helps['grafana dashboard update'] = """
    type: command
    short-summary: Update a dashboard.
    examples:
        - name: Update a dashboard with definition in a json file. For quick start, get existing configuration from "az grafana dashboard show", and apply changes.
                "version" field need to be updated, and "overwrite" field should be true.
          text: |
            az grafana dashboard update -g MyResourceGroup -n MyGrafana --definition @c:\\temp\\dashboard.json
"""

helps['grafana dashboard import'] = """
    type: command
    short-summary: Import a dashboard.
    long-summary: CLI command will fill in required parameters for data sources if configured
    examples:
        - name: import the dashboard of "AKS Container Insights" from Grafana gallery.
          text: |
            az grafana dashboard import -g MyResourceGroup -n MyGrafana --definition 12180
        - name: import a dashboard from a file.
          text: |
             az grafana dashboard import -g MyResourceGroup -n MyGrafana --definition @c:\\temp\\dashboard.json
"""

helps['grafana dashboard list'] = """
    type: command
    short-summary: List all dashboards of an instance.
    examples:
        - name: Find the dashboard for K8s API Server and retrieve the unique identifier(in order to invoke "az grafana dashboard show" command)
          text: |
           az grafana dashboard list -g MyResourceGroup -n MyGrafana --query "[?contains(@.title, 'API server')].uid"
"""

helps['grafana dashboard show'] = """
    type: command
    short-summary: Get the details of a dashboard.
    examples:
        - name: Get details of a dashboard specified by an unique identifier(use "az grafana dashboard list" command to retrieve the uid)
          text: |
           az grafana dashboard show -g MyResourceGroup -n MyGrafana --dashboard VdrOA7jGz
"""

helps['grafana dashboard delete'] = """
    type: command
    short-summary: Delete a dashboard.
    examples:
        - name: Delete a dashboard specified by an unique identifier(use "az grafana dashboard list" command to retrieve the uid)
          text: |
           az grafana dashboard delete -g MyResourceGroup -n MyGrafana --dashboard VdrOA7jGz
"""

helps['grafana dashboard sync'] = """
    type: command
    short-summary: Sync Azure Managed Grafana dashboards from one instance to another instance. Library panels within the dashboards will be automatically included in the sync. Note, dashboards with "Provisioned" state will be skipped due to being read-only
    examples:
        - name: Sync only dashboards under a few folders
          text: |
            az grafana dashboard sync --source /subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/workspaces/providers/Microsoft.Dashboard/grafana/source --destination /subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/workspaces/providers/Microsoft.Dashboard/grafana/destination --folders-to-include "Azure Monitor Container Insights" "Azure Monitor"
        - name: Sync a single dashboard
          text: |
            az grafana dashboard sync --source /subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/workspaces/providers/Microsoft.Dashboard/grafana/source --destination /subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/workspaces/providers/Microsoft.Dashboard/grafana/destination --folders-to-include "MyFolder" --dashboards-to-include "My Service Health"
        - name: Preview the sync
          text: |
            az grafana dashboard sync --source /subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/workspaces/providers/Microsoft.Dashboard/grafana/source --destination /subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/workspaces/providers/Microsoft.Dashboard/grafana/destination --dry-run
"""

helps['grafana folder'] = """
    type: group
    short-summary: Commands to manage folders of an instance.
"""

helps['grafana folder create'] = """
    type: command
    short-summary: Create a new folder.
    examples:
        - name: Create a folder with title.
          text: az grafana folder create -g MyResourceGroup -n MyGrafana --title "My Folder"
"""

helps['grafana folder show'] = """
    type: command
    short-summary: Get the details of a folder.
"""

helps['grafana folder list'] = """
    type: command
    short-summary: List all folders of an instance.
"""

helps['grafana folder update'] = """
    type: command
    short-summary: Update a folder.
"""

helps['grafana folder delete'] = """
    type: command
    short-summary: Delete a folder.
"""

helps['grafana user'] = """
    type: group
    short-summary: Commands to manage users of an instance.
"""

helps['grafana user actual-user'] = """
    type: command
    short-summary: Get the details of the current user.
"""

helps['grafana user list'] = """
    type: command
    short-summary: List users.
"""

helps['grafana user show'] = """
    type: command
    short-summary: Get the details of a user.
"""

helps['grafana api-key'] = """
    type: group
    short-summary: Commands to manage API keys.
    long-summary: API keys are deprecated by Grafana Labs and will not be supported in Grafana 12 and above. Please use service accounts instead.
"""

helps['grafana api-key create'] = """
    type: command
    short-summary: Create a new API key.
    examples:
        - name: Create a new API key.
          text: az grafana api-key create -g myResourceGroup -n myGrafana --key myKey
"""

helps['grafana api-key list'] = """
    type: command
    short-summary: List existing API keys.
"""

helps['grafana api-key delete'] = """
    type: command
    short-summary: Delete an API key.
"""

helps['grafana service-account'] = """
    type: group
    short-summary: Commands to manage service accounts.
"""

helps['grafana service-account create'] = """
    type: command
    short-summary: Create a new service account.
    examples:
        - name: Create a service account with admin role
          text: |
           az grafana service-account create -g myResourceGroup -n myGrafana --service-account myAccount --role admin
"""

helps['grafana service-account update'] = """
    type: command
    short-summary: Update a service account.
    examples:
        - name: disable a service account
          text: |
           az grafana service-account update -g myResourceGroup -n myGrafana --service-account myAccount --is-disabled true
"""

helps['grafana service-account show'] = """
    type: command
    short-summary: Get the details of a service account.
"""

helps['grafana service-account list'] = """
    type: command
    short-summary: List existing service accounts.
"""

helps['grafana service-account delete'] = """
    type: command
    short-summary: Delete a service account.
"""

helps['grafana service-account token'] = """
    type: group
    short-summary: Commands to manage service account tokens.
"""

helps['grafana service-account token create'] = """
    type: command
    short-summary: Create a new service account token.
    examples:
        - name: create a service account token lasting 1 day
          text: |
           az grafana service-account token create -g myResourceGroup -n myGrafana --service-account myAccount --token myToken --time-to-live 1d
"""

helps['grafana service-account token list'] = """
    type: command
    short-summary: List existing service account tokens.
"""

helps['grafana service-account token delete'] = """
    type: command
    short-summary: Delete a service account token.
"""

helps['grafana integrations'] = """
    type: group
    short-summary: Commands to manage integrations of a Grafana instance.
"""

helps['grafana integrations monitor'] = """
    type: group
    short-summary: Commands to manage Azure Monitor workspace integrations of a Grafana instance.
"""

helps['grafana integrations monitor add'] = """
    type: command
    short-summary: Link an Azure Monitor workspace to a Grafana instance.
    examples:
        - name: Link an Azure Monitor workspace to a Grafana instance.
          text: az grafana integrations monitor add -g MyResourceGroup -n MyGrafana --monitor-rg-name MyMonitorResourceGroup --monitor-name MyMonitor
"""

helps['grafana integrations monitor list'] = """
    type: command
    short-summary: List all Azure Monitor workspaces linked to a Grafana instance.
"""

helps['grafana integrations monitor delete'] = """
    type: command
    short-summary: Unlink an Azure Monitor workspace from a Grafana instance.
"""
