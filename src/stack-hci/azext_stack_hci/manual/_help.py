# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-many-lines

from knack.help_files import helps

helps['stack-hci'] = """
    type: group
    short-summary: Manage Azure Stack HCI
"""

helps['stack-hci extension create'] = """
    type: command
    short-summary: "Create Extension for HCI cluster."
    examples:
      - name: Create Arc Extension
        text: |-
               az stack-hci extension create --arc-setting-name "default" --cluster-name "myCluster" --type \
"MicrosoftMonitoringAgent" --protected-settings '{\\"workspaceKey\\":\\"xx\\"}' --publisher "Microsoft.Compute" \
--settings '{\\"workspaceId\\":\\"xx\\"}' --type-handler-version "1.10" --name "MicrosoftMonitoringAgent" \
--resource-group "test-rg"
"""
