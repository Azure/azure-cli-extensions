# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

test_data_source = {
    "access": "proxy",
    "jsonData": {
        "azureAuthType": "msi",
        "subscriptionId": ""
    },
    "name": "Test Azure Monitor Data Source",
    "type": "grafana-azure-monitor-datasource"
}

test_notification_channel = {
    "name": "Test Teams Notification Channel",
    "settings": {
        "url": "https://test.webhook.office.com/IncomingWebhook/"
    },
    "type": "teams"
}

test_dashboard = {
    "dashboard": {
        "title": "Test Dashboard",
    }
}
