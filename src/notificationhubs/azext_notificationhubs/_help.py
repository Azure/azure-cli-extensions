# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['notificationhubs namespace'] = """
    type: group
    short-summary: Commands to manage notificationhubs namespace.
"""

helps['notificationhubs namespace'] = """
    type: group
    short-summary: Commands to manage notificationhubs namespace.
"""

helps['notificationhubs namespace create'] = """
    type: command
    short-summary: Create a service namespace. Once created, this namespace's resource manifest is immutable. This operation is idempotent.
    examples:
      - name: Create a namespace
        text: |-
               az notificationhubs namespace create --resource-group MyResourceGroup --name \\
               "nh-sdk-ns" --location "South Central US" --sku "Standard"
"""

helps['notificationhubs namespace update'] = """
    type: command
    short-summary: Update a service namespace. The namespace's resource manifest is immutable and cannot be modified.
    examples:
      - name: Update the namespace
        text: |-
               az notificationhubs namespace update --resource-group MyResourceGroup --name \\
               "nh-sdk-ns" --sku "Standard"
"""

helps['notificationhubs namespace delete'] = """
    type: command
    short-summary: Delete an existing namespace. This operation also removes all associated notificationHubs under the namespace.
    examples:
      - name: Delete the namespace
        text: |-
               az notificationhubs namespace delete --resource-group MyResourceGroup --name \\
               "nh-sdk-ns"
"""

helps['notificationhubs namespace show'] = """
    type: command
    short-summary: Return the description for the specified namespace.
    examples:
      - name: Show namespace info
        text: |-
               az notificationhubs namespace show --resource-group MyResourceGroup --name \\
               "nh-sdk-ns"
"""

helps['notificationhubs namespace list'] = """
    type: command
    short-summary: List available namespaces.
    examples:
      - name: List available namespaces within a resourceGroup
        text: |-
               az notificationhubs namespace list --resource-group MyResourceGroup
      - name: List all the available namespaces within the subscription irrespective of the resourceGroups
        text: |-
               az notificationhubs namespace list
"""

helps['notificationhubs namespace check-availability'] = """
    type: command
    short-summary: Check the availability of the given service namespace across all Azure subscriptions. This is useful because the domain name is created based on the service namespace name.
    examples:
      - name: Check name availability of namespace
        text: |-
               az notificationhubs namespace check-availability --name "my-test-space"
"""

helps['notificationhubs namespace wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the Notification Hub Namesapce is met.
    examples:
        - name: Pause executing next line of CLI script until the Notification Hub Namesapce is successfully provisioned.
          text: az notificationhubs namespace wait --resource-group MyResourceGroup --name \\
               "nh-sdk-ns" --created
"""

helps['notificationhubs namespace authorization-rule'] = """
    type: group
    short-summary: Commands to manage notificationhubs namespace authorization rule.
"""

helps['notificationhubs namespace authorization-rule list-keys'] = """
    type: command
    short-summary: List the Primary and Secondary ConnectionStrings to the namespace
    examples:
      - name: List keys of the namesapce authorization rule
        text: |-
               az notificationhubs namespace authorization-rule list-keys --resource-group MyResourceGroup --namespace-name \\
               "nh-sdk-ns" --name "RootManageSharedAccessKey"
"""

helps['notificationhubs namespace authorization-rule regenerate-keys'] = """
    type: command
    short-summary: Regenerate the Primary/Secondary Keys to the Namespace Authorization Rule
    examples:
      - name: Regenerate keys of the namesapce authorization rule
        text: |-
               az notificationhubs namespace authorization-rule regenerate-keys --resource-group MyResourceGroup --namespace-name \\
               "nh-sdk-ns" --name "RootManageSharedAccessKey" --policy-key "Secondary Key"
"""

helps['notificationhubs namespace authorization-rule show'] = """
    type: command
    short-summary: Show an authorization rule for a namespace by name.
    examples:
      - name: Show namespace authorization rule info
        text: |-
               az notificationhubs namespace authorization-rule show --resource-group MyResourceGroup \\
               --namespace-name "nh-sdk-ns" --name "RootManageSharedAccessKey"
"""

helps['notificationhubs namespace authorization-rule list'] = """
    type: command
    short-summary: List the authorization rules for a namespace.
    examples:
      - name: List authorization rules of the namespace
        text: |-
               az notificationhubs namespace authorization-rule list --resource-group MyResourceGroup \\
               --namespace-name "nh-sdk-ns"
"""

helps['notificationhubs namespace authorization-rule create'] = """
    type: command
    short-summary: Create an authorization rule for a namespace
    examples:
      - name: Create a namespace authorization rule
        text: |-
               az notificationhubs namespace authorization-rule create --resource-group \\
               MyResourceGroup --namespace-name "nh-sdk-ns" --name "sdk-AuthRules-1788" --rights "Listen"
"""

helps['notificationhubs namespace authorization-rule delete'] = """
    type: command
    short-summary: Delete a namespace authorization rule
    examples:
      - name: Delete a namespace authorization rule
        text: |-
               az notificationhubs namespace authorization-rule delete --resource-group MyResourceGroup \\
               --namespace-name "nh-sdk-ns" --name "RootManageSharedAccessKey"
"""

helps['notificationhubs'] = """
    type: group
    short-summary: Manage Notification Hubs.
"""

helps['notificationhubs create'] = """
    type: command
    short-summary: Create a NotificationHub in a namespace.
    examples:
      - name: Create a Notification Hub
        text: |-
               az notificationhubs create --resource-group MyResourceGroup --namespace-name "nh-sdk-ns" \\
               --name "nh-sdk-hub" --location "South Central US" --sku "Free"
"""

helps['notificationhubs update'] = """
    type: command
    short-summary: Update a NotificationHub in a namespace.
    examples:
      - name: Update the Notification Hub
        text: |-
               az notificationhubs update --resource-group "sdkresourceGroup" --namespace-name \\
               "nh-sdk-ns" --name "sdk-notificationHubs-8708"
"""

helps['notificationhubs delete'] = """
    type: command
    short-summary: Delete a notification hub associated with a namespace.
    examples:
      - name: Delete a notification hub
        text: |-
               az notificationhubs delete --resource-group MyResourceGroup --namespace-name "nh-sdk-ns" \\
               --name "nh-sdk-hub"
"""

helps['notificationhubs show'] = """
    type: command
    short-summary: Show the notification hub information.
    examples:
      - name: Show the Notification Hub info
        text: |-
               az notificationhubs show --resource-group MyResourceGroup --namespace-name "nh-sdk-ns" \\
               --name "nh-sdk-hub"
"""

helps['notificationhubs list'] = """
    type: command
    short-summary: List the notification hubs associated with a namespace.
    examples:
      - name: List the notification hubs
        text: |-
               az notificationhubs list --resource-group MyResourceGroup --namespace-name "nh-sdk-ns"
"""

helps['notificationhubs check-availability'] = """
    type: command
    short-summary: Check the availability of the given notificationHub in a namespace.
    examples:
      - name: Check the availability of the given notificationHub name
        text: |-
               az notificationhubs check-availability --resource-group MyResourceGroup \\
               --namespace-name "locp-newns" --name "nh-sdk-hub"
"""

helps['notificationhubs authorization-rule'] = """
    type: group
    short-summary: Commands to manage notificationhubs authorization rule.
"""

helps['notificationhubs authorization-rule regenerate-keys'] = """
    type: command
    short-summary: Regenerate the Primary/Secondary Keys to the NotificationHub Authorization Rule
    examples:
      - name: Regenerate the Notification Hub authorization rule
        text: |-
               az notificationhubs authorization-rule regenerate-keys --resource-group MyResourceGroup --namespace-name \\
               "nh-sdk-ns" --notification-hub-name "nh-sdk-hub" --name \\
               "DefaultListenSharedAccessSignature" --policy-key "Secondary Key"
"""

helps['notificationhubs credential list'] = """
    type: command
    short-summary: List the PNS Credentials associated with a notification hub .
    examples:
      - name: List the PNS Credentials
        text: |-
               az notificationhubs credential list --resource-group MyResourceGroup --namespace-name \\
               "nh-sdk-ns" --notification-hub-name "nh-sdk-hub"
"""

helps['notificationhubs authorization-rule list-keys'] = """
    type: command
    short-summary: List the Primary and Secondary ConnectionStrings to the NotificationHub
    examples:
      - name: List connectionStrings of the authorization rule
        text: |-
               az notificationhubs authorization-rule list-keys --resource-group MyResourceGroup --namespace-name "nh-sdk-ns" \\
               --notification-hub-name "nh-sdk-hub" --name "sdk-AuthRules-5800"
"""

helps['notificationhubs test-send'] = """
    type: command
    short-summary: test send a push notification
    examples:
      - name: test send notification with message body
        text: |-
               az notificationhubs test-send --resource-group MyResourceGroup --namespace-name \\
               "nh-sdk-ns" --notification-hub-name "nh-sdk-hub" --notification-format gcm \\
               --message "test notification"
      - name: test send notification from file
        text: |-
               az notificationhubs test-send --resource-group MyResourceGroup --namespace-name \\
               "nh-sdk-ns" --notification-hub-name "nh-sdk-hub" --notification-format gcm \\
               --payload @path/to/file
      - name: test send notification with json string
        text: |-
               az notificationhubs test-send --resource-group MyResourceGroup --namespace-name \\
               "nh-sdk-ns" --notification-hub-name "nh-sdk-hub" --notification-format gcm \\
               --payload "{\\\"data\\\":{\\\"message\\\":\\\"test notification\\\"}}"
"""

helps['notificationhubs authorization-rule list'] = """
    type: command
    short-summary: List the authorization rules for a NotificationHub.
    examples:
      - name: List authorization rules
        text: |-
               az notificationhubs authorization-rule list --resource-group MyResourceGroup \\
               --namespace-name "nh-sdk-ns" --notification-hub-name "nh-sdk-hub"
"""

helps['notificationhubs authorization-rule show'] = """
    type: command
    short-summary: Show an authorization rule for a NotificationHub by name.
    examples:
      - name: Show the authorization rule information
        text: |-
               az notificationhubs authorization-rule show --resource-group MyResourceGroup \\
               --namespace-name "nh-sdk-ns" --notification-hub-name "nh-sdk-hub" --name \\
               "DefaultListenSharedAccessSignature"
"""

helps['notificationhubs authorization-rule create'] = """
    type: command
    short-summary: Create an authorization rule for a NotificationHub
    examples:
      - name: Create an authorization rule
        text: |-
               az notificationhubs authorization-rule create --resource-group MyResourceGroup \\
               --namespace-name "nh-sdk-ns" --notification-hub-name "nh-sdk-hub" --name \\
               "DefaultListenSharedAccessSignature" --rights "Listen"
"""

helps['notificationhubs authorization-rule delete'] = """
    type: command
    short-summary: Delete a notificationHub authorization rule
    examples:
      - name: Delete the authorization rule
        text: |-
               az notificationhubs authorization-rule delete --resource-group MyResourceGroup \\
               --namespace-name "nh-sdk-ns" --notification-hub-name "nh-sdk-hub" --name \\
               "DefaultListenSharedAccessSignature"
"""

helps['notificationhubs credential'] = """
    type: group
    short-summary: Commands to manage notificationhubs credential.
"""
helps['notificationhubs credential gcm'] = """
    type: group
    short-summary: Commands to manage notificationhubs credential for Google(GCM/FCM).
"""

helps['notificationhubs credential adm'] = """
    type: group
    short-summary: Commands to manage notificationhubs credential for Amazon(ADM).
"""

helps['notificationhubs credential apns'] = """
    type: group
    short-summary: Commands to manage notificationhubs credential for Apple(APNS).
"""

helps['notificationhubs credential baidu'] = """
    type: group
    short-summary: Commands to manage notificationhubs credential for Baidu(Andrioid China).
"""

helps['notificationhubs credential mpns'] = """
    type: group
    short-summary: Commands to manage notificationhubs credential for Windows Phone(MPNS).
"""

helps['notificationhubs credential wns'] = """
    type: group
    short-summary: Commands to manage notificationhubs credential for Windows(WNS).
"""

helps['notificationhubs credential gcm update'] = """
    type: command
    short-summary: Update the Google GCM/FCM API key.
    examples:
      - name: Update gcm key
        text: |-
               az notificationhubs credential gcm update --resource-group MyResourceGroup \\
               --namespace-name "nh-sdk-ns" --notification-hub-name "nh-sdk-hub" --google-api-key \\
               "xxxxxxxxx"
"""

helps['notificationhubs credential adm update'] = """
    type: command
    short-summary: Update credential for Amazon(ADM).
"""

helps['notificationhubs credential apns update'] = """
    type: command
    short-summary: Update credential for Apple(APNS).
    examples:
      - name: Update APNS certificate
        text: |-
               az notificationhubs credential apns update --namespace-name "nh-sdk-ns" \\
               --notification-hub-name "nh-sdk-hub" --apns-certificate "/path/to/certificate" \\
               --certificate-key "xxxxxx"
"""

helps['notificationhubs credential baidu update'] = """
    type: command
    short-summary: Update credential for Baidu(Andrioid China).
"""

helps['notificationhubs credential mpns update'] = """
    type: command
    short-summary: Update credential for Windows Phone(MPNS).
"""

helps['notificationhubs credential wns update'] = """
    type: command
    short-summary: Update credential for Windows(WNS).
"""
