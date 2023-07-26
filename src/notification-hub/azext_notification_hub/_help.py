# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['notification-hub test-send'] = """
    type: command
    short-summary: test send a push notification
    examples:
      - name: test send notification with message body
        text: |-
               az notification-hub test-send --resource-group MyResourceGroup --namespace-name \\
               my-namespace --notification-hub-name my-hub --notification-format gcm \\
               --message "test notification"
      - name: test send notification from file
        text: |-
               az notification-hub test-send --resource-group MyResourceGroup --namespace-name \\
               my-namespace --notification-hub-name my-hub --notification-format gcm \\
               --payload @path/to/file
      - name: test send notification with json string
        text: |-
               az notification-hub test-send --resource-group MyResourceGroup --namespace-name \\
               my-namespace --notification-hub-name my-hub --notification-format gcm \\
               --payload "{\\\"data\\\":{\\\"message\\\":\\\"test notification\\\"}}"
"""
