# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['sb'] = """
    type: group
    short-summary: Manage Azure ServiceBus namespace, queue, topic, subscription, rule and alias (Disaster Recovery Configuration)

    """

helps['sb namespace'] = """
    type: group
    short-summary: Manage Azure ServiceBus namespace and authorization-rule

    """

helps['sb queue'] = """
    type: group
    short-summary: Manage Azure ServiceBus queue and authorization-rule

    """

helps['sb topic'] = """
    type: group
    short-summary: Manage Azure ServiceBus topic and authorization-rule

    """

helps['sb subscription'] = """
    type: group
    short-summary: Manage Azure ServiceBus Subscription

    """

helps['sb rule'] = """
    type: group
    short-summary: Manage Azure ServiceBus rule

    """

helps['sb alias'] = """
    type: group
    short-summary: Manage Azure ServiceBus Alias (Disaster Recovery Configuration)

    """

helps['sb namespace check-name-availability'] = """
    type: command
    short-summary: check for the availability of the given name for the Namespace
    examples:
        - name: Create a new topic.
          text: az sb namespace check_name_availability --name mynamespace

    """

helps['sb namespace create'] = """
    type: command
    short-summary: Creates the ServiceBus Namespace
    examples:
        - name: Create a new namespace.
          text: helps['az sb namespace create --resource-group myresourcegroup --name mynamespace --location westus
           --tags ['tag1: value1', 'tag2: value2'] --sku-name Standard --sku-tier Standard']

    """

helps['sb namespace show'] = """
    type: command
    short-summary: shows the Namespace Details
    examples:
        - name: shows the Namespace details.
          text: helps['az sb namespace show --resource-group myresourcegroup --name mynamespace']

    """

helps['sb namespace list'] = """
    type: command
    short-summary: List the Namespaces by ResourceGroup or By subscription
    examples:
        - name: Get the Namespaces by resource Group.
          text: helps['az sb namespace list --resource-group myresourcegroup']
        - name: Get the Namespaces by Subscription.
          text: helps['az sb namespace list']

    """

helps['sb namespace delete'] = """
    type: command
    short-summary: Deletes the Namespaces
    examples:
        - name: Deletes the Namespace
          text: helps['az sb namespace delete --resource-group myresourcegroup --name mynamespace']

    """

helps['sb namespace authorizationrule create'] = """
    type: command
    short-summary: Creates Authorization rule for the given Namespace
    examples:
        - name: Creates Authorization rules
          text: helps['az sb namespace authorizationrule create --resource-group myresourcegroup --namespace-name mynamespace
           --name myauthorule --access-rights [Send, Listen]']

    """

helps['sb namespace authorizationrule get'] = """
    type: command
    short-summary: Shows the details of AuthorizatioRule
    examples:
        - name: Shows the details of AuthorizatioRule
          text: helps['az sb namespace authorizationrule show --resource-group myresourcegroup --namespace-name mynamespace
           --name myauthorule']

    """

helps['sb namespace authorizationrule list'] = """
    type: command
    short-summary: Shows the list of AuthorizatioRule by Namespace
    examples:
        - name: Shows the list of AuthorizatioRule by Namespace
          text: helps['az sb namespace authorizationrule show --resource-group myresourcegroup --namespace-name mynamespace']

    """

helps['sb namespace authorizationrule list-keys'] = """
    type: command
    short-summary: Shows the connectionstrings of AuthorizatioRule for the namespace
    examples:
        - name: Shows the connectionstrings of AuthorizatioRule for the namespace.
          text: helps['az sb namespace authorizationrule list-keys --resource-group myresourcegroup --namespace-name mynamespace
           --name myauthorule']

    """

helps['sb namespace authorizationrule regenerate-keys'] = """
    type: command
    short-summary: Regenerate the connectionstrings of AuthorizatioRule for the namespace.
    examples:
        - name: Regenerate the connectionstrings of AuthorizatioRule for the namespace.
          text: helps['az sb namespace authorizationrule regenerate-keys --resource-group myresourcegroup
           --namespace-name mynamespace --name myauthorule --key PrimaryKey']

    """

helps['sb namespace authorizationrule delete'] = """
    type: command
    short-summary: Deletes the AuthorizatioRule of the namespace.
    examples:
        - name: Deletes the AuthorizatioRule of the namespace.
          text: helps['az sb namespace authorizationrule delete --resource-group myresourcegroup --namespace-name mynamespace
           --name myauthorule']

    """

helps['sb queue create'] = """
    type: command
    short-summary: Creates the ServiceBus Queue
    examples:
        - name: Create a new queue.
          text: helps['az sb queue create --resource-group myresourcegroup --namespace-name mynamespace --name myqueue']

    """

helps['sb queue show'] = """
    type: command
    short-summary: shows the Queue Details
    examples:
        - name: Shows the Queue details.
          text: helps['az sb queue show --resource-group myresourcegroup --namespace-name mynamespace --name myqueue']

    """

helps['sb queue list'] = """
    type: command
    short-summary: List the Queueby Namepsace
    examples:
        - name: Get the Queues by Namespace.
          text: helps['az sb queue list --resource-group myresourcegroup --namespace-name mynamespace']

    """

helps['sb queue delete'] = """
    type: command
    short-summary: Deletes the Queue
    examples:
        - name: Deletes the queue
          text: helps['az sb queue delete --resource-group myresourcegroup --namespace-name mynamespace --name myqueue']

    """

helps['sb queue authorizationrule create'] = """
    type: command
    short-summary: Creates Authorization rule for the given Queue
    examples:
        - name: Creates Authorization rules
          text: helps['az sb queue authorizationrule create --resource-group myresourcegroup --namespace-name mynamespace
           --queue-name myqueue
           --name myauthorule --access-rights [Listen]']

    """

helps['sb queue authorizationrule show'] = """
    type: command
    short-summary: shows the details of AuthorizatioRule
    examples:
        - name: shows the details of AuthorizatioRule
          text: helps['az sb queue authorizationrule show --resource-group myresourcegroup --namespace-name mynamespace
           --queue-name myqueue
           --name myauthorule']

    """

helps['sb queue authorizationrule list'] = """
    type: command
    short-summary: shows the list of AuthorizatioRule by Queue
    examples:
        - name: shows the list of AuthorizatioRule by Queue
          text: helps['az sb queue authorizationrule show --resource-group myresourcegroup --namespace-name mynamespace
           --queue-name myqueue']

    """

helps['sb queue authorizationrule list-keys'] = """
    type: command
    short-summary: Shows the connectionstrings of AuthorizatioRule for the Queue.
    examples:
        - name: Shows the connectionstrings of AuthorizatioRule for the queue.
          text: helps['az sb queue authorizationrule list-keys --resource-group myresourcegroup --namespace-name mynamespace
           --queue-name myqueue
           --name myauthorule']

    """

helps['sb queue authorizationrule regenerate-keys'] = """
    type: command
    short-summary: Regenerate the connectionstrings of AuthorizatioRule for the namespace.
    examples:
        - name: Regenerate the connectionstrings of AuthorizatioRule for the namespace.
          text: helps['az sb queue authorizationrule regenerate-keys --resource-group myresourcegroup --namespace-name mynamespace
           --queue-name myqueue
           --name myauthorule --key PrimaryKey']

    """

helps['sb queue authorizationrule delete'] = """
    type: command
    short-summary: Deletes the AuthorizatioRule of the Queue.
    examples:
        - name: Deletes the AuthorizatioRule of the queue.
          text: helps['az sb queue authorizationrule delete --resource-group myresourcegroup --namespace-name mynamespace
           --queue-name myqueue
           --name myauthorule']

    """

helps['sb topic create'] = """
    type: command
    short-summary: Creates the ServiceBus Topic
    examples:
        - name: Create a new queue.
          text: helps['az sb topic create --resource-group myresourcegroup --namespace-name mynamespace --name {topicname}']

    """

helps['sb topic show'] = """
    type: command
    short-summary: Shows the Topic Details
    examples:
        - name: Shows the Topic details.
          text: helps['az sb topic get --resource-group myresourcegroup --namespace-name mynamespace --name {topicname}']

    """

helps['sb topic list'] = """
    type: command
    short-summary: List the Topic by Namepsace
    examples:
        - name: Get the Topics by Namespace.
          text: helps['az sb topic list --resource-group myresourcegroup --namespace-name mynamespace']

    """

helps['sb topic delete'] = """
    type: command
    short-summary: Deletes the Topic
    examples:
        - name: Deletes the topic
          text: helps['az sb topic delete --resource-group myresourcegroup --namespace-name mynamespace --name {topicname}']

    """

helps['sb topic authorizationrule create'] = """
    type: command
    short-summary: Creates Authorization rule for the given Topic
    examples:
        - name: Creates Authorization rules
          text: helps['az sb topic authorizationrule create --resource-group myresourcegroup --namespace-name mynamespace
           --topic-name {topicname} --name myauthorule --access-rights [Send, Listen]']

    """

helps['sb topic authorizationrule show'] = """
    type: command
    short-summary: Shows the details of AuthorizatioRule
    examples:
        - name: Shows the details of AuthorizatioRule
          text: helps['az sb topic authorizationrule get --resource-group myresourcegroup --namespace-name mynamespace
           --topic-name {topicname}
           --name myauthorule']

    """

helps['sb topic authorizationrule list'] = """
    type: command
    short-summary: Gets the list of AuthorizatioRule by Topic
    examples:
        - name: Gets the list of AuthorizatioRule by Topic
          text: helps['az sb topic authorizationrule get --resource-group myresourcegroup --namespace-name mynamespace
           --topic-name {topicname}']

    """

helps['sb topic authorizationrule list-keys'] = """
    type: command
    short-summary: shows the connectionstrings of AuthorizatioRule for the Topic.
    examples:
        - name: Gets the connectionstrings of AuthorizatioRule for the topic.
          text: helps['az sb topic authorizationrule listkeys --resource-group myresourcegroup --namespace-name mynamespace
           --topic-name {topicname}
           --name myauthorule']

    """

helps['sb topic authorizationrule regenerate-keys'] = """
    type: command
    short-summary: Regenerate the connectionstrings of AuthorizatioRule for the Topic.
    examples:
        - name: Regenerate the connectionstrings of AuthorizatioRule for the Topic.
          text: helps['az sb topic authorizationrule regenerate_keys --resource-group myresourcegroup --namespace-name mynamespace
           --topic-name {topicname}
           --name myauthorule --regeneratekey PrimaryKey']

    """

helps['sb topic authorizationrule delete'] = """
    type: command
    short-summary: Deletes the AuthorizatioRule of the Topic.
    examples:
        - name: Deletes the AuthorizatioRule of the topic
          text: helps['az sb topic authorizationrule delete --resource-group myresourcegroup --namespace-name mynamespace
           --topic-name {topicname}
           --name myauthorule']

    """
helps['sb subscription create'] = """
    type: command
    short-summary: Creates the ServiceBus Subscription
    examples:
        - name: Create a new Subscription.
          text: helps['az sb subscription create --resource-group myresourcegroup --namespace-name mynamespace
           --topic-name {topicname} --name {subscriptionname}']

    """

helps['sb subscription show'] = """
    type: command
    short-summary: Shows the Subscription Details
    examples:
        - name: Shows the Subscription details.
          text: helps['az sb subscription get --resource-group myresourcegroup --namespace-name mynamespace
           --topic-name {topicname} --name {subscriptionname}']

    """

helps['sb subscription list'] = """
    type: command
    short-summary: List the Subscription by Topic
    examples:
        - name: Shows the Subscription by Topic.
          text: helps['az sb subscription list --resource-group myresourcegroup --namespace-name mynamespace']

    """

helps['sb subscription delete'] = """
    type: command
    short-summary: Deletes the Subscription
    examples:
        - name: Deletes the Subscription
          text: helps['az sb subscription delete --resource-group myresourcegroup --namespace-name mynamespace
           --topic-name {topicname} --name {subscriptionname}']

    """

helps['sb rule create'] = """
    type: command
    short-summary: Creates the ServiceBus Rule for Subscription
    examples:
        - name: Create a new Rule.
          text: helps['az sb rule create --resource-group myresourcegroup --namespace-name mynamespace --topic-name {topicname}
           --subscription-name {subscriptionname} --name {rulename} --filter-sql-expression {sqlexpression}']

    """

helps['sb rule show'] = """
    type: command
    short-summary: Shows the Rule Details
    examples:
        - name: Shows the Rule details.
          text: helps['az sb rule show --resource-group myresourcegroup --namespace-name mynamespace --topic-name {topicname}
           --subscription-name {subscriptionname} --name {rulename}']

    """

helps['sb rule list'] = """
    type: command
    short-summary: List the Rule by Subscription
    examples:
        - name: Shows the Rule by Subscription.
          text: helps['az sb rule list --resource-group myresourcegroup --namespace-name mynamespace
           --subscription-name {subscriptionname}']

    """

helps['sb rule delete'] = """
    type: command
    short-summary: Deletes the Rule
    examples:
        - name: Deletes the Rule
          text: helps['az sb rule delete --resource-group myresourcegroup --namespace-name mynamespace --topic-name {topicname}
           --subscription-name {subscriptionname} --name {rulename}']

    """

helps['sb alias check_name_availability'] = """
    type: command
    short-summary: Check the availability of the Alias (Geo DR Configuration) Name
    examples:
        - name: Check the availability of the Alias (Geo DR Configuration) Name
          text: helps['az sb alias check_name_availability --resource-group myresourcegroup --namespace-name primarynamespace
           --alias myaliasname']

    """

helps['sb alias create'] = """
    type: command
    short-summary: Creats Alias (Geo DR Configuration) for the give Namespace
    examples:
        - name: Creats Alias (Geo DR Configuration) for the give Namespace
          text: helps['az sb alias create  --resource-group myresourcegroup --namespace-name primarynamespace
           --alias myaliasname --partner-namespace {id}']

    """

helps['sb alias show'] = """
    type: command
    short-summary: shows details of Alias (Geo DR Configuration) for Primay/Secondary Namespace
    examples:
        - name:  show details of Alias (Geo DR Configuration)  of the Primary Namespace
          text: helps['az sb alias show  --resource-group myresourcegroup --namespace-name primarynamespace
           --alias myaliasname']
        - name:  Get details of Alias (Geo DR Configuration)  of the Secondary Namespace
           text: helps['az sb alias show  --resource-group myresourcegroup --namespace-name secondarynamespace
           --alias myaliasname']

    """

helps['sb alias break-pairing'] = """
    type: command
    short-summary: Disables the Disaster Recovery and stops replicating changes from primary to secondary namespaces
    examples:
        - name:  Disables the Disaster Recovery and stops replicating changes from primary to secondary namespaces
          text: helps['az sb alias break-pairing  --resource-group myresourcegroup --namespace-name primarynamespace
           --alias myaliasname']

    """

helps['sb alias fail-over'] = """
    type: command
    short-summary: Envokes GEO DR failover and reconfigure the alias to point to the secondary namespace
    examples:
        - name:  Envokes GEO DR failover and reconfigure the alias to point to the secondary namespace
          text: helps['az sb alias fail-over  --resource-group myresourcegroup --namespace-name secondarynamespace
           --alias myaliasname']

    """

helps['sb alias delete'] = """
    type: command
    short-summary: Delete Alias(Disaster Recovery configuration) request accepted
    examples:
        - name:  Delete Alias(Disaster Recovery configuration) request accepted
          text: helps['az sb alias delete  --resource-group myresourcegroup --namespace-name secondarynamespace
           --alias myaliasname']

    """
