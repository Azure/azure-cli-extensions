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

helps['notificationhubs namespace list'] = """
    type: command
    short-summary: Lists all of the available NotificationHubs REST API operations.
    examples:
      - name: OperationsList
        text: |-
               az notificationhubs namespace list
"""

helps['notificationhubs namespace'] = """
    type: group
    short-summary: Commands to manage notificationhubs namespace.
"""

helps['notificationhubs namespace create'] = """
    type: command
    short-summary: Creates/Updates a service namespace. Once created, this namespace's resource manifest is immutable. This operation is idempotent.
    examples:
      - name: NameSpaceCreate
        text: |-
               az notificationhubs namespace create --resource-group "5ktrial" --namespace-name \\
               "nh-sdk-ns" --location "South Central US" --sku-name "Standard" --sku-tier "Standard"
"""

helps['notificationhubs namespace update'] = """
    type: command
    short-summary: Creates/Updates a service namespace. Once created, this namespace's resource manifest is immutable. This operation is idempotent.
    examples:
      - name: NameSpaceUpdate
        text: |-
               az notificationhubs namespace update --resource-group "5ktrial" --namespace-name \\
               "nh-sdk-ns" --sku-name "Standard" --sku-tier "Standard"
"""

helps['notificationhubs namespace delete'] = """
    type: command
    short-summary: Deletes an existing namespace. This operation also removes all associated notificationHubs under the namespace.
    examples:
      - name: NameSpaceDelete
        text: |-
               az notificationhubs namespace delete --resource-group "5ktrial" --namespace-name \\
               "nh-sdk-ns"
"""

helps['notificationhubs namespace show'] = """
    type: command
    short-summary: Returns the description for the specified namespace.
    examples:
      - name: NameSpaceGet
        text: |-
               az notificationhubs namespace show --resource-group "5ktrial" --namespace-name \\
               "nh-sdk-ns"
"""

helps['notificationhubs namespace list'] = """
    type: command
    short-summary: Lists the available namespaces within a resourceGroup.
    examples:
      - name: NameSpaceListByResourceGroup
        text: |-
               az notificationhubs namespace list --resource-group "5ktrial"
      - name: NameSpaceList
        text: |-
               az notificationhubs namespace list
"""

helps['notificationhubs namespace check_availability'] = """
    type: command
    short-summary: Checks the availability of the given service namespace across all Azure subscriptions. This is useful because the domain name is created based on the service namespace name.
    examples:
      - name: NameSpaceCheckNameAvailability
        text: |-
               az notificationhubs namespace check_availability
"""

helps['notificationhubs namespace list_keys'] = """
    type: command
    short-summary: Gets the Primary and Secondary ConnectionStrings to the namespace 
    examples:
      - name: NameSpaceAuthorizationRuleListKey
        text: |-
               az notificationhubs namespace list_keys --resource-group "5ktrial" --namespace-name \\
               "nh-sdk-ns" --name "RootManageSharedAccessKey"
"""

helps['notificationhubs namespace regenerate_keys'] = """
    type: command
    short-summary: Regenerates the Primary/Secondary Keys to the Namespace Authorization Rule
    examples:
      - name: NameSpaceAuthorizationRuleRegenerateKey
        text: |-
               az notificationhubs namespace regenerate_keys --resource-group "5ktrial" --namespace-name \\
               "nh-sdk-ns" --name "RootManageSharedAccessKey"
"""

helps['notificationhubs namespace get_authorization_rule'] = """
    type: command
    short-summary: Gets an authorization rule for a namespace by name.
    examples:
      - name: NameSpaceAuthorizationRuleGet
        text: |-
               az notificationhubs namespace get_authorization_rule --resource-group "5ktrial" \\
               --namespace-name "nh-sdk-ns" --name "RootManageSharedAccessKey"
"""

helps['notificationhubs namespace list_authorization_rules'] = """
    type: command
    short-summary: Gets the authorization rules for a namespace.
    examples:
      - name: NameSpaceAuthorizationRuleListAll
        text: |-
               az notificationhubs namespace list_authorization_rules --resource-group "5ktrial" \\
               --namespace-name "nh-sdk-ns"
"""

helps['notificationhubs namespace create_or_update_authorization_rule'] = """
    type: command
    short-summary: Creates an authorization rule for a namespace
    examples:
      - name: NameSpaceAuthorizationRuleCreate
        text: |-
               az notificationhubs namespace create_or_update_authorization_rule --resource-group \\
               "5ktrial" --namespace-name "nh-sdk-ns" --name "sdk-AuthRules-1788"
"""

helps['notificationhubs namespace delete_authorization_rule'] = """
    type: command
    short-summary: Deletes a namespace authorization rule
    examples:
      - name: NameSpaceAuthorizationRuleDelete
        text: |-
               az notificationhubs namespace delete_authorization_rule --resource-group "5ktrial" \\
               --namespace-name "nh-sdk-ns" --name "RootManageSharedAccessKey"
"""

helps['notificationhubs hub'] = """
    type: group
    short-summary: Commands to manage notificationhubs hub.
"""

helps['notificationhubs hub create'] = """
    type: command
    short-summary: Creates/Update a NotificationHub in a namespace.
    examples:
      - name: NotificationHubCreate
        text: |-
               az notificationhubs hub create --resource-group "5ktrial" --namespace-name "nh-sdk-ns" \\
               --notification-hub-name "nh-sdk-hub"
"""

helps['notificationhubs hub update'] = """
    type: command
    short-summary: Creates/Update a NotificationHub in a namespace.
    examples:
      - name: NotificationHubPatch
        text: |-
               az notificationhubs hub update --resource-group "sdkresourceGroup" --namespace-name \\
               "nh-sdk-ns" --notification-hub-name "sdk-notificationHubs-8708"
"""

helps['notificationhubs hub delete'] = """
    type: command
    short-summary: Deletes a notification hub associated with a namespace.
    examples:
      - name: NotificationHubDelete
        text: |-
               az notificationhubs hub delete --resource-group "5ktrial" --namespace-name "nh-sdk-ns" \\
               --notification-hub-name "nh-sdk-hub"
"""

helps['notificationhubs hub show'] = """
    type: command
    short-summary: Lists the notification hubs associated with a namespace.
    examples:
      - name: NotificationHubGet
        text: |-
               az notificationhubs hub show --resource-group "5ktrial" --namespace-name "nh-sdk-ns" \\
               --notification-hub-name "nh-sdk-hub"
"""

helps['notificationhubs hub list'] = """
    type: command
    short-summary: Lists the notification hubs associated with a namespace.
    examples:
      - name: NotificationHubListByNameSpace
        text: |-
               az notificationhubs hub list --resource-group "5ktrial" --namespace-name "nh-sdk-ns"
"""

helps['notificationhubs hub check_notification_hub_availability'] = """
    type: command
    short-summary: Checks the availability of the given notificationHub in a namespace.
    examples:
      - name: notificationHubCheckNameAvailability
        text: |-
               az notificationhubs hub check_notification_hub_availability --resource-group "5ktrial" \\
               --namespace-name "locp-newns"
"""

helps['notificationhubs hub regenerate_keys'] = """
    type: command
    short-summary: Regenerates the Primary/Secondary Keys to the NotificationHub Authorization Rule
    examples:
      - name: NotificationHubAuthorizationRuleRegenrateKey
        text: |-
               az notificationhubs hub regenerate_keys --resource-group "5ktrial" --namespace-name \\
               "nh-sdk-ns" --notification-hub-name "nh-sdk-hub" --name \\
               "DefaultListenSharedAccessSignature"
"""

helps['notificationhubs hub get_pns_credentials'] = """
    type: command
    short-summary: Lists the PNS Credentials associated with a notification hub .
    examples:
      - name: notificationHubPnsCredentials
        text: |-
               az notificationhubs hub get_pns_credentials --resource-group "5ktrial" --namespace-name \\
               "nh-sdk-ns" --notification-hub-name "nh-sdk-hub"
"""

helps['notificationhubs hub list_keys'] = """
    type: command
    short-summary: Gets the Primary and Secondary ConnectionStrings to the NotificationHub 
    examples:
      - name: NotificationHubAuthorizationRuleListKey
        text: |-
               az notificationhubs hub list_keys --resource-group "5ktrial" --namespace-name "nh-sdk-ns" \\
               --notification-hub-name "nh-sdk-hub" --name "sdk-AuthRules-5800"
"""

helps['notificationhubs hub debug_send'] = """
    type: command
    short-summary: test send a push notification
    examples:
      - name: debugsend
        text: |-
               az notificationhubs hub debug_send --resource-group "5ktrial" --namespace-name \\
               "nh-sdk-ns" --notification-hub-name "nh-sdk-hub"
"""

helps['notificationhubs hub list_authorization_rules'] = """
    type: command
    short-summary: Gets the authorization rules for a NotificationHub.
    examples:
      - name: NotificationHubAuthorizationRuleListAll
        text: |-
               az notificationhubs hub list_authorization_rules --resource-group "5ktrial" \\
               --namespace-name "nh-sdk-ns" --notification-hub-name "nh-sdk-hub"
"""

helps['notificationhubs hub get_authorization_rule'] = """
    type: command
    short-summary: Gets an authorization rule for a NotificationHub by name.
    examples:
      - name: NotificationHubAuthorizationRuleGet
        text: |-
               az notificationhubs hub get_authorization_rule --resource-group "5ktrial" \\
               --namespace-name "nh-sdk-ns" --notification-hub-name "nh-sdk-hub" --name \\
               "DefaultListenSharedAccessSignature"
"""

helps['notificationhubs hub create_or_update_authorization_rule'] = """
    type: command
    short-summary: Creates/Updates an authorization rule for a NotificationHub
    examples:
      - name: NotificationHubAuthorizationRuleCreate
        text: |-
               az notificationhubs hub create_or_update_authorization_rule --resource-group "5ktrial" \\
               --namespace-name "nh-sdk-ns" --notification-hub-name "nh-sdk-hub" --name \\
               "DefaultListenSharedAccessSignature"
"""

helps['notificationhubs hub delete_authorization_rule'] = """
    type: command
    short-summary: Deletes a notificationHub authorization rule
    examples:
      - name: NotificationHubAuthorizationRuleDelete
        text: |-
               az notificationhubs hub delete_authorization_rule --resource-group "5ktrial" \\
               --namespace-name "nh-sdk-ns" --notification-hub-name "nh-sdk-hub" --name \\
               "DefaultListenSharedAccessSignature"
"""
