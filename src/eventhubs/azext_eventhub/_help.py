# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['eventhubs'] = """
    type: group
    short-summary: Manage Azure Event Hubs namespace, eventhub, consumergroup and Geo Recovery configuration - Alias
"""

helps['eventhubs namespace'] = """
    type: group
    short-summary: Manage Azure Event Hubs namespace and authorizationrule
"""

helps['eventhubs namespace authorizationrule'] = """
    type: group
    short-summary: Manage Azure Event Hubs AuthorizationRule for Namespace
"""

helps['eventhubs namespace authorizationrule keys'] = """
    type: group
    short-summary: Manage Azure Event Hubs AuthorizationRule connection strings for Namespace
"""

helps['eventhubs eventhub'] = """
    type: group
    short-summary: Manage Azure Event Hubs eventhub and authorization-rule
"""

helps['eventhubs eventhub authorizationrule'] = """
    type: group
    short-summary: Manage Azure Service Bus AuthorizationRule for Eventhub
"""

helps['eventhubs eventhub authorizationrule keys'] = """
    type: group
    short-summary: Manage Azure AuthorizationRule connection strings for Eventhub
"""

helps['eventhubs consumergroup'] = """
    type: group
    short-summary: Manage Azure Event Hubs consumergroup
"""

helps['eventhubs georecovery-alias'] = """
    type:  group
    short-summary: Manage Azure Event Hubs Geo Recovery configuration Alias
"""

helps['eventhubs georecovery-alias authorizationrule'] = """
    type: group
    short-summary: Manage Azure Event Hubs AuthorizationRule for Geo Recovery configuration Alias
"""

helps['eventhubs georecovery-alias authorizationrule keys'] = """
    type: group
    short-summary: Manage Azure Event Hubs AuthorizationRule connection strings for Geo Recovery configuration Alias
"""

helps['eventhubs namespace exists'] = """
    type: command
    short-summary: check for the availability of the given name for the Namespace
    examples:
        - name: Create a new topic.
          text: az eventhubs namespace exists --name mynamespace
"""

helps['eventhubs namespace create'] = """
    type: command
    short-summary: Creates the Event Hubs Namespace
    examples:
        - name: Create a new namespace.
          text: az eventhubs namespace create --resource-group myresourcegroup --name mynamespace --location westus
           --tags tag1=value1 tag2=value2 --sku-name Standard --sku-tier Standard --is-auto-inflate-enabled False --maximum-throughput-units 30
"""

helps['eventhubs namespace show'] = """
    type: command
    short-summary: shows the Event Hubs Namespace Details
    examples:
        - name: shows the Namespace details.
          text: az eventhubs namespace show --resource-group myresourcegroup --name mynamespace
"""

helps['eventhubs namespace list'] = """
    type: command
    short-summary: Lists the Event Hubs Namespaces
    examples:
        - name: List the Event Hubs Namespaces by resource group.
          text: az eventhubs namespace list --resource-group myresourcegroup
        - name: Get the Namespaces by Subscription.
          text: az eventhubs namespace list
"""

helps['eventhubs namespace delete'] = """
    type: command
    short-summary: Deletes the Namespaces
    examples:
        - name: Deletes the Namespace
          text: az eventhubs namespace delete --resource-group myresourcegroup --name mynamespace
"""

helps['eventhubs namespace authorizationrule create'] = """
    type: command
    short-summary: Creates AuthorizationRule for the given Namespace
    examples:
        - name: Creates Authorization rules
          text: az eventhubs namespace authorizationrule create --resource-group myresourcegroup --namespace-name mynamespace --name myauthorule --access-rights Send Listen
"""

helps['eventhubs namespace authorizationrule show'] = """
    type: command
    short-summary: Shows the details of AuthorizationRule
    examples:
        - name: Shows the details of AuthorizationRule
          text: az eventhubs namespace authorizationrule show --resource-group myresourcegroup --namespace-name mynamespace --name myauthorule
"""

helps['eventhubs namespace authorizationrule list'] = """
    type: command
    short-summary: Shows the list of AuthorizationRule by Namespace
    examples:
        - name: Shows the list of AuthorizationRule by Namespace
          text: az eventhubs namespace authorizationrule show --resource-group myresourcegroup --namespace-name mynamespace
"""

helps['eventhubs namespace authorizationrule keys list'] = """
    type: command
    short-summary: Shows the connection strings for namespace
    examples:
        - name: Shows the connectionstrings of AuthorizationRule for the namespace.
          text: az eventhubs namespace authorizationrule list-keys --resource-group myresourcegroup --namespace-name mynamespace --name myauthorule
"""

helps['eventhubs namespace authorizationrule keys renew'] = """
    type: command
    short-summary: Regenerate the connectionstrings of AuthorizationRule for the namespace.
    examples:
        - name: Regenerate the connectionstrings of AuthorizationRule for the namespace.
          text: az eventhubs namespace authorizationrule regenerate-keys --resource-group myresourcegroup
           --namespace-name mynamespace --name myauthorule --key PrimaryKey
"""

helps['eventhubs namespace authorizationrule delete'] = """
    type: command
    short-summary: Deletes the AuthorizationRule of the namespace.
    examples:
        - name: Deletes the AuthorizationRule of the namespace.
          text: az eventhubs namespace authorizationrule delete --resource-group myresourcegroup --namespace-name mynamespace --name myauthorule
"""

helps['eventhubs eventhub create'] = """
    type: command
    short-summary: Creates the Event Hubs Eventhub
    examples:
        - name: Create a new Eventhub.
          text: az eventhubs eventhub create --resource-group myresourcegroup --namespace-name mynamespace --name myeventhub --message-retention-in-days 4 ---partition-count 15
"""

helps['eventhubs eventhub show'] = """
    type: command
    short-summary: shows the Eventhub Details
    examples:
        - name: Shows the Eventhub details.
          text: az eventhubs eventhub show --resource-group myresourcegroup --namespace-name mynamespace --name myeventhub
"""

helps['eventhubs eventhub list'] = """
    type: command
    short-summary: List the EventHub by Namepsace
    examples:
        - name: Get the Eventhubs by Namespace.
          text: az eventhubs eventhub list --resource-group myresourcegroup --namespace-name mynamespace
"""

helps['eventhubs eventhub delete'] = """
    type: command
    short-summary: Deletes the Eventhub
    examples:
        - name: Deletes the Eventhub
          text: az eventhubs eventhub delete --resource-group myresourcegroup --namespace-name mynamespace --name myeventhub
"""

helps['eventhubs eventhub authorizationrule create'] = """
    type: command
    short-summary: Creates Authorization rule for the given Eventhub
    examples:
        - name: Creates Authorization rules
          text: az eventhubs eventhub authorizationrule create --resource-group myresourcegroup --namespace-name mynamespace --event-hub-name myeventhub --name myauthorule --access-rights Listen
"""

helps['eventhubs eventhub authorizationrule show'] = """
    type: command
    short-summary: shows the details of AuthorizationRule
    examples:
        - name: shows the details of AuthorizationRule
          text: az eventhubs eventhub authorizationrule show --resource-group myresourcegroup --namespace-name mynamespace --event-hub-name myeventhub --name myauthorule
"""

helps['eventhubs eventhub authorizationrule list'] = """
    type: command
    short-summary: shows the list of AuthorizationRule by Eventhub
    examples:
        - name: shows the list of AuthorizationRule by Eventhub
          text: az eventhubs eventhub authorizationrule show --resource-group myresourcegroup --namespace-name mynamespace --event-hub-name myeventhub
"""

helps['eventhubs eventhub authorizationrule  keys list'] = """
    type: command
    short-summary: Shows the connectionstrings of AuthorizationRule for the Eventhub.
    examples:
        - name: Shows the connectionstrings of AuthorizationRule for the eventhub.
          text: az eventhubs eventhub authorizationrule list-keys --resource-group myresourcegroup --namespace-name mynamespace --event-hub-name myeventhub --name myauthorule
"""

helps['eventhubs eventhub authorizationrule  keys renew'] = """
    type: command
    short-summary: Regenerate the connectionstrings of AuthorizationRule for the namespace.
    examples:
        - name: Regenerate the connectionstrings of AuthorizationRule for the namespace.
          text: az eventhubs eventhub authorizationrule regenerate-keys --resource-group myresourcegroup --namespace-name mynamespace --event-hub-name myeventhub --name myauthorule --key PrimaryKey
"""

helps['eventhubs eventhub authorizationrule delete'] = """
    type: command
    short-summary: Deletes the AuthorizationRule of the Eventhub.
    examples:
        - name: Deletes the AuthorizationRule of the Eventhub.
          text: az eventhubs eventhub authorizationrule delete --resource-group myresourcegroup --namespace-name mynamespace --event-hub-name myeventhub --name myauthorule
"""

helps['eventhubs consumergroup create'] = """
    type: command
    short-summary: Creates the EventHub ConsumerGroup
    examples:
        - name: Create a new ConsumerGroup.
          text: az eventhubs consumergroup create --resource-group myresourcegroup --namespace-name mynamespace --event-hub-name myeventhub --name myconsumergroup
"""

helps['eventhubs consumergroup show'] = """
    type: command
    short-summary: Shows the ConsumerGroup Details
    examples:
        - name: Shows the ConsumerGroup details.
          text: az eventhubs consumergroup show --resource-group myresourcegroup --namespace-name mynamespace --event-hub-name myeventhub --name myconsumergroup
"""

helps['eventhubs consumergroup list'] = """
    type: command
    short-summary: List the ConsumerGroup by Eventhub
    examples:
        - name: Shows the ConsumerGroup by Eventhub.
          text: az eventhubs consumergroup get --resource-group myresourcegroup --namespace-name mynamespace --event-hub-name myeventhub
"""

helps['eventhubs consumergroup delete'] = """
    type: command
    short-summary: Deletes the ConsumerGroup
    examples:
        - name: Deletes the ConsumerGroup
          text: az eventhubs consumergroup delete --resource-group myresourcegroup --namespace-name mynamespace --event-hub-name myeventhub --name myconsumergroup
"""

helps['eventhubs georecovery-alias exists'] = """
    type: command
    short-summary: Check the availability of the Geo Recovery - Alias Name
    examples:
        - name: Check the availability of the Geo Recovery configuration - Alias Name
          text: az eventhubs georecovery-alias check-name-availability --resource-group myresourcegroup --namespace-name primarynamespace --alias myaliasname
"""

helps['eventhubs georecovery-alias create'] = """
    type: command
    short-summary: Creates a Geo Recovery - Alias for the give Namespace
    examples:
        - name: Creats Geo Recovery configuration - Alias for the give Namespace
          text: az eventhubs georecovery-alias create  --resource-group myresourcegroup --namespace-name primarynamespace --alias myaliasname --partner-namespace resourcearmid
"""

helps['eventhubs georecovery-alias show'] = """
    type: command
    short-summary: shows details of Geo Recovery configuration - Alias for Primay or Secondary Namespace
    examples:
        - name: Shows details of Geo Recovery configuration - Alias  of the Primary Namespace
          text: az eventhubs georecovery-alias show  --resource-group myresourcegroup --namespace-name primarynamespace --alias myaliasname
        - name: Shows details of Geo Recovery configuration - Alias  of the Secondary Namespace
          text: az eventhubs georecovery-alias show  --resource-group myresourcegroup --namespace-name secondarynamespace --alias myaliasname
"""

helps['eventhubs georecovery-alias authorizationrule show'] = """
    type: command
    short-summary: Shows the details of Event Hubs Geo Recovery Alias and Namespace AuthorizationRule
    examples:
        - name: Shows the details AuthorizationRule by Event Hubs Namespace
          text: az eventhubs georecovery-alias authorizationrule show --resource-group myresourcegroup --namespace-name mynamespace
"""

helps['eventhubs georecovery-alias authorizationrule list'] = """
    type: command
    short-summary: Shows the list of AuthorizationRule by Event Hubs Namespace
    examples:
        - name: Shows the list of AuthorizationRule by Event Hubs Namespace
          text: az eventhubs georecovery-alias authorizationrule list --resource-group myresourcegroup --namespace-name mynamespace
"""

helps['eventhubs georecovery-alias authorizationrule keys list'] = """
    type: command
    short-summary: Shows the connection strings of AuthorizationRule for the Event Hubs Namespace
    examples:
        - name: Shows the connection strings of AuthorizationRule for the namespace.
          text: az eventhubs georecovery-alias authorizationrule keys list --resource-group myresourcegroup --namespace-name mynamespace --name myauthorule
"""

helps['eventhubs georecovery-alias break-pair'] = """
    type: command
    short-summary: Disables the Geo Recovery and stops replicating changes from primary to secondary namespaces
    examples:
        - name:  Disables the Geo Recovery and stops replicating changes from primary to secondary namespaces
          text: az eventhubs georecovery-alias break-pair  --resource-group myresourcegroup --namespace-name primarynamespace --alias myaliasname
"""

helps['eventhubs georecovery-alias fail-over'] = """
    type: command
    short-summary: Invokes Geo Recovery configuration - Alias to point to the secondary namespace
    examples:
        - name:  Invokes GEO DR failover and reconfigure the alias to point to the secondary namespace
          text: az eventhubs georecovery-alias fail-over  --resource-group myresourcegroup --namespace-name secondarynamespace --alias myaliasname
"""

helps['eventhubs georecovery-alias delete'] = """
    type: command
    short-summary: Delete Geo Recovery - Alias
    examples:
        - name: Delete Geo Recovery configuration - Alias
          text: az eventhubs georecovery-alias delete  --resource-group myresourcegroup --namespace-name secondarynamespace --alias myaliasname
"""
