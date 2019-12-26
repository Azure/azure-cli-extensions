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
    short-summary: Creates/Updates a service namespace. Once created, this namespace's resource manifest is immutable. This operation is idempotent.
    examples:
      - name: Creates a namespace
        text: |-
               az notificationhubs namespace create --resource-group "5ktrial" --namespace-name \\
               "nh-sdk-ns" --location "South Central US" --sku-name "Standard" --sku-tier "Standard"
"""

helps['notificationhubs namespace update'] = """
    type: command
    short-summary: Creates/Updates a service namespace. Once created, this namespace's resource manifest is immutable. This operation is idempotent.
    examples:
      - name: Updates the namespace
        text: |-
               az notificationhubs namespace update --resource-group "5ktrial" --namespace-name \\
               "nh-sdk-ns" --sku-name "Standard" --sku-tier "Standard"
"""

helps['notificationhubs namespace delete'] = """
    type: command
    short-summary: Deletes an existing namespace. This operation also removes all associated notificationHubs under the namespace.
    examples:
      - name: Deletes the namespace
        text: |-
               az notificationhubs namespace delete --resource-group "5ktrial" --namespace-name \\
               "nh-sdk-ns"
"""

helps['notificationhubs namespace show'] = """
    type: command
    short-summary: Returns the description for the specified namespace.
    examples:
      - name: Gets namespace info
        text: |-
               az notificationhubs namespace show --resource-group "5ktrial" --namespace-name \\
               "nh-sdk-ns"
"""

helps['notificationhubs namespace list'] = """
    type: command
    short-summary: Lists available namespaces.
    examples:
      - name: Lists available namespaces within a resourceGroup
        text: |-
               az notificationhubs namespace list --resource-group "5ktrial"
      - name: Lists all the available namespaces within the subscription irrespective of the resourceGroups
        text: |-
               az notificationhubs namespace list
"""

helps['notificationhubs namespace check_availability'] = """
    type: command
    short-summary: Checks the availability of the given service namespace across all Azure subscriptions. This is useful because the domain name is created based on the service namespace name.
    examples:
      - name: Checks name availability of namespace
        text: |-
               az notificationhubs namespace check_availability --name "my-test-space"
"""

helps['notificationhubs namespace authorization_rule'] = """
    type: group
    short-summary: Commands to manage notificationhubs namespace authorization rule.
"""

helps['notificationhubs namespace authorization_rule list_keys'] = """
    type: command
    short-summary: Gets the Primary and Secondary ConnectionStrings to the namespace
    examples:
      - name: Lists keys of the namesapce authorization rule
        text: |-
               az notificationhubs namespace authorization_rule list_keys --resource-group "5ktrial" --namespace-name \\
               "nh-sdk-ns" --name "RootManageSharedAccessKey"
"""

helps['notificationhubs namespace authorization_rule regenerate_keys'] = """
    type: command
    short-summary: Regenerates the Primary/Secondary Keys to the Namespace Authorization Rule
    examples:
      - name: Regenerates keys of the namesapce authorization rule
        text: |-
               az notificationhubs namespace authorization_rule regenerate_keys --resource-group "5ktrial" --namespace-name \\
               "nh-sdk-ns" --name "RootManageSharedAccessKey" --policy-key "Secondary Key"
"""

helps['notificationhubs namespace authorization_rule show'] = """
    type: command
    short-summary: Gets an authorization rule for a namespace by name.
    examples:
      - name: Shows namespace authorization rule info
        text: |-
               az notificationhubs namespace authorization_rule show --resource-group "5ktrial" \\
               --namespace-name "nh-sdk-ns" --name "RootManageSharedAccessKey"
"""

helps['notificationhubs namespace authorization_rule list'] = """
    type: command
    short-summary: List the authorization rules for a namespace.
    examples:
      - name: Lists authorization rules of the namespace
        text: |-
               az notificationhubs namespace authorization_rule list --resource-group "5ktrial" \\
               --namespace-name "nh-sdk-ns"
"""

helps['notificationhubs namespace authorization_rule create'] = """
    type: command
    short-summary: Creates an authorization rule for a namespace
    examples:
      - name: Creates a namespace authorization rule
        text: |-
               az notificationhubs namespace authorization_rule create --resource-group \\
               "5ktrial" --namespace-name "nh-sdk-ns" --name "sdk-AuthRules-1788" --rights "Listen"
"""

helps['notificationhubs namespace authorization_rule delete'] = """
    type: command
    short-summary: Deletes a namespace authorization rule
    examples:
      - name: Deletes a namespace authorization rule
        text: |-
               az notificationhubs namespace authorization_rule delete --resource-group "5ktrial" \\
               --namespace-name "nh-sdk-ns" --name "RootManageSharedAccessKey"
"""

helps['notificationhubs'] = """
    type: group
    short-summary: Manage Notification Hubs.
"""

helps['notificationhubs create'] = """
    type: command
    short-summary: Creates/Update a NotificationHub in a namespace.
    examples:
      - name: Creates a Notification Hub
        text: |-
               az notificationhubs create --resource-group "5ktrial" --namespace-name "nh-sdk-ns" \\
               --notification-hub-name "nh-sdk-hub" --location "South Central US" --sku-name "Free"
"""

helps['notificationhubs update'] = """
    type: command
    short-summary: Creates/Update a NotificationHub in a namespace.
    examples:
      - name: Updates the Notification Hub
        text: |-
               az notificationhubs update --resource-group "sdkresourceGroup" --namespace-name \\
               "nh-sdk-ns" --notification-hub-name "sdk-notificationHubs-8708"
"""

helps['notificationhubs delete'] = """
    type: command
    short-summary: Deletes a notification hub associated with a namespace.
    examples:
      - name: Deletes a notification hub
        text: |-
               az notificationhubs delete --resource-group "5ktrial" --namespace-name "nh-sdk-ns" \\
               --notification-hub-name "nh-sdk-hub"
"""

helps['notificationhubs show'] = """
    type: command
    short-summary: Lists the notification hubs associated with a namespace.
    examples:
      - name: Shows the Notification Hub info
        text: |-
               az notificationhubs show --resource-group "5ktrial" --namespace-name "nh-sdk-ns" \\
               --notification-hub-name "nh-sdk-hub"
"""

helps['notificationhubs list'] = """
    type: command
    short-summary: Lists the notification hubs associated with a namespace.
    examples:
      - name: Lists the notification hubs
        text: |-
               az notificationhubs list --resource-group "5ktrial" --namespace-name "nh-sdk-ns"
"""

helps['notificationhubs check_availability'] = """
    type: command
    short-summary: Checks the availability of the given notificationHub in a namespace.
    examples:
      - name: Checks the availability of the given notificationHub name
        text: |-
               az notificationhubs check_availability --resource-group "5ktrial" \\
               --namespace-name "locp-newns" --notification-hub-name "nh-sdk-hub"
"""

helps['notificationhubs authorization_rule'] = """
    type: group
    short-summary: Commands to manage notificationhubs authorization rule.
"""

helps['notificationhubs authorization_rule regenerate_keys'] = """
    type: command
    short-summary: Regenerates the Primary/Secondary Keys to the NotificationHub Authorization Rule
    examples:
      - name: Regenerates the Notification Hub authorization rule
        text: |-
               az notificationhubs authorization_rule regenerate_keys --resource-group "5ktrial" --namespace-name \\
               "nh-sdk-ns" --notification-hub-name "nh-sdk-hub" --name \\
               "DefaultListenSharedAccessSignature" --policy-key "Secondary Key"
"""

helps['notificationhubs credential list'] = """
    type: command
    short-summary: Lists the PNS Credentials associated with a notification hub .
    examples:
      - name: Lists the PNS Credentials
        text: |-
               az notificationhubs credential list --resource-group "5ktrial" --namespace-name \\
               "nh-sdk-ns" --notification-hub-name "nh-sdk-hub"
"""

helps['notificationhubs authorization_rule list_keys'] = """
    type: command
    short-summary: Gets the Primary and Secondary ConnectionStrings to the NotificationHub
    examples:
      - name: List connectionStrings of the authorization rule
        text: |-
               az notificationhubs authorization_rule list_keys --resource-group "5ktrial" --namespace-name "nh-sdk-ns" \\
               --notification-hub-name "nh-sdk-hub" --name "sdk-AuthRules-5800"
"""

helps['notificationhubs test_send'] = """
    type: command
    short-summary: test send a push notification
    examples:
      - name: debug send notification
        text: |-
               az notificationhubs test_send --resource-group "5ktrial" --namespace-name \\
               "nh-sdk-ns" --notification-hub-name "nh-sdk-hub" --notification-format gcm \\
               --payload "{\\\"data\\\":{\\\"message\\\":\\\"test notification\\\"}}"
"""

helps['notificationhubs authorization_rule list'] = """
    type: command
    short-summary: Lists the authorization rules for a NotificationHub.
    examples:
      - name: Lists authorization rules
        text: |-
               az notificationhubs authorization_rule list --resource-group "5ktrial" \\
               --namespace-name "nh-sdk-ns" --notification-hub-name "nh-sdk-hub"
"""

helps['notificationhubs authorization_rule show'] = """
    type: command
    short-summary: Gets an authorization rule for a NotificationHub by name.
    examples:
      - name: Shows the authorization rule information
        text: |-
               az notificationhubs authorization_rule show --resource-group "5ktrial" \\
               --namespace-name "nh-sdk-ns" --notification-hub-name "nh-sdk-hub" --name \\
               "DefaultListenSharedAccessSignature"
"""

helps['notificationhubs authorization_rule create'] = """
    type: command
    short-summary: Creates/Updates an authorization rule for a NotificationHub
    examples:
      - name: Creates an authorization rule
        text: |-
               az notificationhubs authorization_rule create --resource-group "5ktrial" \\
               --namespace-name "nh-sdk-ns" --notification-hub-name "nh-sdk-hub" --name \\
               "DefaultListenSharedAccessSignature" --rights "Listen"
"""

helps['notificationhubs authorization_rule delete'] = """
    type: command
    short-summary: Deletes a notificationHub authorization rule
    examples:
      - name: Deletes the authorization rule
        text: |-
               az notificationhubs authorization_rule delete --resource-group "5ktrial" \\
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
    short-summary: Updates the Google GCM/FCM API key.
    examples:
      - name: Updates gcm key
        text: |-
               az notificationhubs credential gcm update --resource-group "5ktrial" \\
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
