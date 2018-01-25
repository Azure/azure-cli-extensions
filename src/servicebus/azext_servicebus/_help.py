# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['servicebus'] = """
    type: group
    short-summary: Manage Azure Service Bus namespace, queue, topic, subscription, rule and geo disaster recovery configuration - alias
"""

helps['servicebus namespace'] = """
    type: group
    short-summary: Manage Azure Service Bus Namespace
"""

helps['servicebus namespace authorizationrule'] = """
    type: group
    short-summary: Manage Azure Service Bus Namespace AuthorizationRule
"""

helps['servicebus namespace authorizationrule keys'] = """
    type: group
    short-summary: Manage Azure AuthorizationRule connection strings for Namespace
"""

helps['servicebus queue'] = """
    type: group
    short-summary: Manage Azure Service Bus Queue and authorizationrule
"""

helps['servicebus queue authorizationrule'] = """
    type: group
    short-summary: Manage Azure Service Bus Queue AuthorizationRule
"""

helps['servicebus queue authorizationrule keys'] = """
    type: group
    short-summary: Manage Azure AuthorizationRule connection strings for Service Bus Queue
"""

helps['servicebus topic'] = """
    type: group
    short-summary: Manage Azure Service Bus Topic and authorizationrule
"""

helps['servicebus topic authorizationrule'] = """
    type: group
    short-summary: Manage Azure Service Bus Topic AuthorizationRule
"""

helps['servicebus topic authorizationrule keys'] = """
    type: group
    short-summary: Manage Azure AuthorizationRule connection strings for Service Bus Topic
"""

helps['servicebus subscription'] = """
    type: group
    short-summary: Manage Azure Service Bus Subscription
"""

helps['servicebus rule'] = """
    type: group
    short-summary: Manage Azure Service Bus Rule
"""

helps['servicebus georecovery-alias'] = """
    type: group
    short-summary: Manage Azure Service Bus Geo Disaster Recovery Configuration - Alias
"""

helps['servicebus georecovery-alias authorizationrule'] = """
    type: group
    short-summary: Manage Azure Service Bus AuthorizationRule for Namespace with GeoDRAlias
"""

helps['servicebus georecovery-alias authorizationrule keys'] = """
    type: group
    short-summary: Manage Azure AuthorizationRule connection strings for Service Bus Namespace
"""

helps['servicebus namespace exists'] = """
    type: command
    short-summary: check for the availability of the given name for the Namespace
    examples:
        - name: check for the availability of mynamespace for the Namespace
          text: az servicebus namespace exists --name mynamespace
"""

helps['servicebus namespace create'] = """
    type: command
    short-summary: Creates a Service Bus Namespace
    examples:
        - name: Create a Service Bus Namespace.
          text: az servicebus namespace create --resource-group myresourcegroup --name mynamespace --location westus
           --tags tag1=value1 tag2=value2 --sku-name Standard --sku-tier Standard
"""

helps['servicebus namespace show'] = """
    type: command
    short-summary: Shows the Service Bus Namespace details
    examples:
        - name: shows the Namespace details.
          text: az servicebus namespace show --resource-group myresourcegroup --name mynamespace
"""

helps['servicebus namespace list'] = """
    type: command
    short-summary: List the Service Bus Namespaces
    examples:
        - name: Get the Service Bus Namespaces by resource group
          text: az servicebus namespace list --resource-group myresourcegroup
        - name: Get the Service Bus Namespaces by Subscription.
          text: az servicebus namespace list
"""

helps['servicebus namespace delete'] = """
    type: command
    short-summary: Deletes the Service Bus Namespace
    examples:
        - name: Deletes the Service Bus Namespace
          text: az servicebus namespace delete --resource-group myresourcegroup --name mynamespace
"""

helps['servicebus namespace authorizationrule create'] = """
    type: command
    short-summary: Creates Authorizationrule for the given Service Bus Namespace
    examples:
        - name: Creates Authorizationrule 'myauthorule' for the given Service Bus Namespace 'mynamepsace' in resourcegroup
          text: az servicebus namespace authorizationrule create --resource-group myresourcegroup --namespace-name mynamespace
           --name myauthorule --access-rights Send Listen
"""

helps['servicebus namespace authorizationrule show'] = """
    type: command
    short-summary: Shows the details of Service Bus Namespace AuthorizationRule
    examples:
        - name: Shows the details of Service Bus Namespace AuthorizationRule
          text: az servicebus namespace authorizationrule show --resource-group myresourcegroup --namespace-name mynamespace
           --name myauthorule
"""

helps['servicebus namespace authorizationrule list'] = """
    type: command
    short-summary: Shows the list of AuthorizationRule by Service Bus Namespace
    examples:
        - name: Shows the list of AuthorizationRule by Service Bus Namespace
          text: az servicebus namespace authorizationrule show --resource-group myresourcegroup --namespace-name mynamespace
"""

helps['servicebus namespace authorizationrule keys list'] = """
    type: command
    short-summary: Shows the connection strings of AuthorizationRule for the Service Bus Namespace
    examples:
        - name: Shows the connection strings of AuthorizationRule for the namespace.
          text: az servicebus namespace authorizationrule list-keys --resource-group myresourcegroup --namespace-name mynamespace
           --name myauthorule
"""

helps['servicebus namespace authorizationrule keys renew'] = """
    type: command
    short-summary: Regenerate the connection strings of AuthorizationRule for the Service Bus Namespace.
    examples:
        - name: Regenerate the connection strings of AuthorizationRule for the Service Bus Namespace.
          text: az servicebus namespace authorizationrule regenerate-keys --resource-group myresourcegroup
           --namespace-name mynamespace --name myauthorule --key PrimaryKey
"""

helps['servicebus namespace authorizationrule delete'] = """
    type: command
    short-summary: Deletes the AuthorizationRule of the Service Bus Namespace.
    examples:
        - name: Deletes the AuthorizationRule of the Service Bus Namespace.
          text: az servicebus namespace authorizationrule delete --resource-group myresourcegroup --namespace-name mynamespace
           --name myauthorule
"""

helps['servicebus queue create'] = """
    type: command
    short-summary: Creates the Service Bus Queue
    examples:
        - name: Creates Service Bus Queue.
          text: az servicebus queue create --resource-group myresourcegroup --namespace-name mynamespace --name myqueue
"""

helps['servicebus queue show'] = """
    type: command
    short-summary: shows the Service Bus Queue Details
    examples:
        - name: Shows the Service Bus Queue Details
          text: az servicebus queue show --resource-group myresourcegroup --namespace-name mynamespace --name myqueue
"""

helps['servicebus queue list'] = """
    type: command
    short-summary: List the Queue by Service Bus Namepsace
    examples:
        - name: Get the Queues by Service Bus Namespace.
          text: az servicebus queue list --resource-group myresourcegroup --namespace-name mynamespace
"""

helps['servicebus queue delete'] = """
    type: command
    short-summary: Deletes the Service Bus Queue
    examples:
        - name: Deletes the queue
          text: az servicebus queue delete --resource-group myresourcegroup --namespace-name mynamespace --name myqueue
"""

helps['servicebus queue authorizationrule create'] = """
    type: command
    short-summary: Creates Authorization rule for the given Service Bus Queue
    examples:
        - name: Creates Authorization rules for Queue
          text: az servicebus queue authorizationrule create --resource-group myresourcegroup --namespace-name mynamespace
           --queue-name myqueue --name myauthorule --access-rights Listen
"""

helps['servicebus queue authorizationrule show'] = """
    type: command
    short-summary: shows the details of AuthorizationRule
    examples:
        - name: shows the details of AuthorizationRule
          text: az servicebus queue authorizationrule show --resource-group myresourcegroup --namespace-name mynamespace
           --queue-name myqueue --name myauthorule
"""

helps['servicebus queue authorizationrule list'] = """
    type: command
    short-summary: shows the list of AuthorizationRule by Queue
    examples:
        - name: shows the list of AuthorizationRule by Queue
          text: az servicebus queue authorizationrule show --resource-group myresourcegroup --namespace-name mynamespace
           --queue-name myqueue
"""

helps['servicebus queue authorizationrule keys list'] = """
    type: command
    short-summary: Shows the connection strings of AuthorizationRule for the Queue.
    examples:
        - name: Shows the connection strings of AuthorizationRule for the queue.
          text: az servicebus queue authorizationrule list-keys --resource-group myresourcegroup --namespace-name mynamespace
           --queue-name myqueue --name myauthorule
"""

helps['servicebus queue authorizationrule keys renew'] = """
    type: command
    short-summary: Regenerate the connection strings of AuthorizationRule for the namespace.
    examples:
        - name: Regenerate the connection strings of AuthorizationRule for the namespace.
          text: az servicebus queue authorizationrule regenerate-keys --resource-group myresourcegroup --namespace-name mynamespace
           --queue-name myqueue --name myauthorule --key PrimaryKey
"""

helps['servicebus queue authorizationrule delete'] = """
    type: command
    short-summary: Deletes the AuthorizationRule of the Queue.
    examples:
        - name: Deletes the AuthorizationRule of the queue.
          text: az servicebus queue authorizationrule delete --resource-group myresourcegroup --namespace-name mynamespace
           --queue-name myqueue --name myauthorule
"""

helps['servicebus topic create'] = """
    type: command
    short-summary: Creates the Service Bus Topic
    examples:
        - name: Create a new queue.
          text: az servicebus topic create --resource-group myresourcegroup --namespace-name mynamespace --name mytopic
"""

helps['servicebus topic show'] = """
    type: command
    short-summary: Shows the Service Bus Topic Details
    examples:
        - name: Shows the Topic details.
          text: az servicebus topic show --resource-group myresourcegroup --namespace-name mynamespace --name mytopic
"""

helps['servicebus topic list'] = """
    type: command
    short-summary: List the Topic by Service Bus Namepsace
    examples:
        - name: Get the Topics by Namespace.
          text: az servicebus topic list --resource-group myresourcegroup --namespace-name mynamespace
"""

helps['servicebus topic delete'] = """
    type: command
    short-summary: Deletes the Service Bus Topic
    examples:
        - name: Deletes the topic
          text: az servicebus topic delete --resource-group myresourcegroup --namespace-name mynamespace --name mytopic
"""

helps['servicebus topic authorizationrule create'] = """
    type: command
    short-summary: Creates AuthorizationRule for the given Service Bus Topic
    examples:
        - name: Creates Authorization rules
          text: az servicebus topic authorizationrule create --resource-group myresourcegroup --namespace-name mynamespace
           --topic-name mytopic --name myauthorule --access-rights Send Listen
"""

helps['servicebus topic authorizationrule show'] = """
    type: command
    short-summary: Shows the details of AuthorizationRule
    examples:
        - name: Shows the details of AuthorizationRule
          text: az servicebus topic authorizationrule get --resource-group myresourcegroup --namespace-name mynamespace
           --topic-name mytopic --name myauthorule
"""

helps['servicebus topic authorizationrule list'] = """
    type: command
    short-summary: shows list of AuthorizationRule by Topic
    examples:
        - name: shows list of AuthorizationRule by Topic
          text: az servicebus topic authorizationrule get --resource-group myresourcegroup --namespace-name mynamespace
           --topic-name mytopic
"""

helps['servicebus topic authorizationrule keys list'] = """
    type: command
    short-summary: shows connection strings of AuthorizationRule for the Topic.
    examples:
        - name: shows connection strings of AuthorizationRule for the topic.
          text: az servicebus topic authorizationrule listkeys --resource-group myresourcegroup --namespace-name mynamespace
           --topic-name mytopic --name myauthorule
"""

helps['servicebus topic authorizationrule keys renew'] = """
    type: command
    short-summary: Regenerate the connection strings of AuthorizationRule for the Topic.
    examples:
        - name: Regenerate Primary/Secondary key of connection string for the Topic.
          text: az servicebus topic authorizationrule regenerate_keys --resource-group myresourcegroup --namespace-name mynamespace
           --topic-name mytopic --name myauthorule --key PrimaryKey
"""

helps['servicebus topic authorizationrule delete'] = """
    type: command
    short-summary: Deletes the AuthorizationRule of the Topic.
    examples:
        - name: Deletes the AuthorizationRule of the topic
          text: az servicebus topic authorizationrule delete --resource-group myresourcegroup --namespace-name mynamespace
           --topic-name mytopic --name myauthorule
"""

helps['servicebus subscription create'] = """
    type: command
    short-summary: Creates the ServiceBus Subscription
    examples:
        - name: Create a new Subscription.
          text: az servicebus subscription create --resource-group myresourcegroup --namespace-name mynamespace
           --topic-name mytopic --name mysubscription

    """

helps['servicebus subscription show'] = """
    type: command
    short-summary: Shows Service Bus Subscription Details
    examples:
        - name: Shows the Subscription details.
          text: az servicebus subscription get --resource-group myresourcegroup --namespace-name mynamespace
           --topic-name mytopic --name mysubscription
"""

helps['servicebus subscription list'] = """
    type: command
    short-summary: List the Subscription by Service Bus Topic
    examples:
        - name: Shows the Subscription by Service Bus Topic.
          text: az servicebus subscription list --resource-group myresourcegroup --namespace-name mynamespace
"""

helps['servicebus subscription delete'] = """
    type: command
    short-summary: Deletes the Service Bus Subscription
    examples:
        - name: Deletes the Subscription
          text: az servicebus subscription delete --resource-group myresourcegroup --namespace-name mynamespace
           --topic-name mytopic --name mysubscription
"""

helps['servicebus rule create'] = """
    type: command
    short-summary: Creates the ServiceBus Rule for Subscription
    examples:
        - name: Creates Rule.
          text: az servicebus rule create --resource-group myresourcegroup --namespace-name mynamespace --topic-name mytopic
           --subscription-name mysubscription --name myrule --filter-sql-expression mysqlexpression
"""

helps['servicebus rule show'] = """
    type: command
    short-summary: Shows Rule Details
    examples:
        - name: Shows the Rule details.
          text: az servicebus rule show --resource-group myresourcegroup --namespace-name mynamespace --topic-name mytopic
           --subscription-name mysubscription --name myrule
"""

helps['servicebus rule list'] = """
    type: command
    short-summary: List the Rule by Subscription
    examples:
        - name: Shows the Rule by Subscription.
          text: az servicebus rule list --resource-group myresourcegroup --namespace-name mynamespace
           --subscription-name mysubscription
"""

helps['servicebus rule delete'] = """
    type: command
    short-summary: Deletes the Rule
    examples:
        - name: Deletes the Rule
          text: az servicebus rule delete --resource-group myresourcegroup --namespace-name mynamespace --topic-name mytopic
           --subscription-name mysubscription --name myrule
"""

helps['servicebus georecovery-alias exists'] = """
    type: command
    short-summary: Checks if Geo Recovery Alias Name is available
    examples:
        - name: Check the availability of the Geo Disaster Recovery configuration - Alias Name
          text: az servicebus georecovery-alias exists --resource-group myresourcegroup --namespace-name primarynamespace
           --alias myaliasname
"""

helps['servicebus georecovery-alias create'] = """
    type: command
    short-summary: Creates Service Bus Geo Recovery Alias for the give Namespace
    examples:
        - name: Creates Geo Disaster Recovery configuration - Alias for the give Namespace
          text: az servicebus georecovery-alias create  --resource-group myresourcegroup --namespace-name primarynamespace
           --alias myaliasname --partner-namespace armresourceid
"""

helps['servicebus georecovery-alias show'] = """
    type: command
    short-summary: shows details of Service Bus Geo Recovery Alias for Primay/Secondary Namespace
    examples:
        - name:  show details of Alias (Geo DR Configuration)  of the Primary Namespace
          text: az servicebus georecovery-alias show  --resource-group myresourcegroup --namespace-name primarynamespace
           --alias myaliasname
        - name:  Get details of Alias (Geo DR Configuration)  of the Secondary Namespace
           text: az servicebus georecovery-alias show  --resource-group myresourcegroup --namespace-name secondarynamespace
           --alias myaliasname
"""

helps['servicebus georecovery-alias authorizationrule list'] = """
    type: command
    short-summary: Shows the list of AuthorizationRule by Service Bus Namespace
    examples:
        - name: Shows the list of AuthorizationRule by Service Bus Namespace
          text: az servicebus georecovery-alias authorizationrule show --resource-group myresourcegroup --namespace-name mynamespace
"""

helps['servicebus georecovery-alias authorizationrule keys list'] = """
    type: command
    short-summary: Shows the connection strings of AuthorizationRule for the Service Bus Namespace
    examples:
        - name: Shows the connection strings of AuthorizationRule for the namespace.
          text: az servicebus georecovery-alias authorizationrule keys list --resource-group myresourcegroup --namespace-name mynamespace
           --name myauthorule
"""

helps['servicebus georecovery-alias break-pairing'] = """
    type: command
    short-summary: Disables Service Bus Geo Recovery Alias and stops replicating changes from primary to secondary namespaces
    examples:
        - name:  Disables the Disaster Recovery and stops replicating changes from primary to secondary namespaces
          text: az servicebus georecovery-alias break-pairing  --resource-group myresourcegroup --namespace-name primarynamespace
           --alias myaliasname
"""

helps['servicebus georecovery-alias fail-over'] = """
    type: command
    short-summary: Invokes Service Bus Geo Recovery Alias failover and re-configure the alias to point to the secondary namespace
    examples:
        - name:  Invokes Geo Disaster Recovery  failover and reconfigure the alias to point to the secondary namespace
          text: az servicebus georecovery-alias fail-over  --resource-group myresourcegroup --namespace-name secondarynamespace
           --alias myaliasname
"""

helps['servicebus georecovery-alias delete'] = """
    type: command
    short-summary: Delete Service Bus Geo Recovery Alias request accepted
    examples:
        - name:  Delete Alias(Disaster Recovery configuration) request accepted
          text: az servicebus georecovery-alias delete  --resource-group myresourcegroup --namespace-name secondarynamespace
           --alias myaliasname
"""
