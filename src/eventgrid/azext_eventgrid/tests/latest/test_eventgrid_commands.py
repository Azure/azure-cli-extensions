# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer


class EventGridNamespaceTests(ScenarioTest):
    @ResourceGroupPreparer(name_prefix='test_eventgrid_namespace', location='eastus')
    def test_namespace(self):
        self.kwargs.update({
            'namespace': self.create_random_name('name', 10)
        })

        self.cmd('eventgrid namespace create -g {rg} -n {namespace}', checks=[
            self.check('resourceGroup', '{rg}'),
            self.check('name', '{namespace}'),
            self.check('sku.capacity', 1),
            self.check('sku.name', 'Standard')
        ])
        self.cmd('eventgrid namespace update -g {rg} -n {namespace} --tags "{{tag:test}}" --sku "{{name:standard,capacity:2}}" --topic-spaces-configuration "{{maximumSessionExpiryInHours:1}}"', checks=[
            self.check('resourceGroup', '{rg}'),
            self.check('name', '{namespace}'),
            self.check('sku.capacity', 2),
            self.check('sku.name', 'Standard'),
            self.check('tags.tag', 'test'),
            self.check('topicSpacesConfiguration.maximumClientSessionsPerAuthenticationName', 1),
            self.check('topicSpacesConfiguration.maximumSessionExpiryInHours', 1),
            self.check('topicSpacesConfiguration.state', 'Disabled')
        ])
        self.cmd('eventgrid namespace show -g {rg} -n {namespace}', checks=[
            self.check('resourceGroup', '{rg}'),
            self.check('name', '{namespace}'),
            self.check('sku.capacity', 2),
            self.check('sku.name', 'Standard'),
            self.check('tags.tag', 'test'),
            self.check('topicSpacesConfiguration.maximumClientSessionsPerAuthenticationName', 1),
            self.check('topicSpacesConfiguration.maximumSessionExpiryInHours', 1),
            self.check('topicSpacesConfiguration.state', 'Disabled')
        ])
        self.cmd('eventgrid namespace list -g {rg}', checks=[
            self.check('[0].resourceGroup', '{rg}'),
            self.check('[0].name', '{namespace}'),
            self.check('[0].sku.capacity', 2),
            self.check('[0].sku.name', 'Standard'),
            self.check('[0].tags.tag', 'test'),
            self.check('[0].topicSpacesConfiguration.maximumClientSessionsPerAuthenticationName', 1),
            self.check('[0].topicSpacesConfiguration.maximumSessionExpiryInHours', 1),
            self.check('[0].topicSpacesConfiguration.state', 'Disabled')
        ])
        self.cmd('eventgrid namespace delete -g {rg} -n {namespace} -y')

    @ResourceGroupPreparer(name_prefix='test_eventgrid_namespace_client_and_client_group', location='eastus')
    def test_namespace_client_and_client_group(self):
        self.kwargs.update({
            'namespace': self.create_random_name('name', 10),
            'client': self.create_random_name('client', 15),
            'client_group': self.create_random_name('group', 15)
        })

        self.cmd('eventgrid namespace create -g {rg} -n {namespace} --topic-spaces-configuration "{{maximumSessionExpiryInHours:1,state:enabled}}"', checks=[
            self.check('name', '{namespace}'),
            self.check('sku.capacity', 1),
            self.check('sku.name', 'Standard'),
            self.check('topicSpacesConfiguration.maximumClientSessionsPerAuthenticationName', 1),
            self.check('topicSpacesConfiguration.maximumSessionExpiryInHours', 1),
            self.check('topicSpacesConfiguration.state', 'Enabled')
        ])
        self.cmd('eventgrid namespace client create -g {rg} --namespace-name {namespace} -n {client}  --attributes "{{\'room\':\'345\',\'floor\':5}}" --client-certificate-authentication "{{validationScheme:SubjectMatchesAuthenticationName}}"', checks=[
            self.check('name', '{client}'),
            self.check('attributes.floor', 5),
            self.check('attributes.room', '345'),
            self.check('clientCertificateAuthentication.validationScheme', 'SubjectMatchesAuthenticationName')
        ])
        self.cmd('eventgrid namespace client update -g {rg} --namespace-name {namespace} -n {client}  --attributes "{{\'room\':\'456\',\'floor\':6}}" --description test', checks=[
            self.check('name', '{client}'),
            self.check('attributes.floor', 6),
            self.check('attributes.room', '456'),
            self.check('clientCertificateAuthentication.validationScheme', 'SubjectMatchesAuthenticationName'),
            self.check('description', 'test')
        ])
        self.cmd('eventgrid namespace client show -g {rg} --namespace-name {namespace} -n {client}', checks=[
            self.check('name', '{client}'),
            self.check('attributes.floor', 6),
            self.check('attributes.room', '456'),
            self.check('clientCertificateAuthentication.validationScheme', 'SubjectMatchesAuthenticationName'),
            self.check('description', 'test')
        ])
        self.cmd('eventgrid namespace client list -g {rg} --namespace-name {namespace}', checks=[
            self.check('[0].name', '{client}'),
            self.check('[0].attributes.floor', 6),
            self.check('[0].attributes.room', '456'),
            self.check('[0].clientCertificateAuthentication.validationScheme', 'SubjectMatchesAuthenticationName'),
            self.check('[0].description', 'test')
        ])
        self.cmd('eventgrid namespace client-group create -g {rg} --namespace-name {namespace} -n {client_group} --description test --group-query "attributes.floor = 6"', checks=[
            self.check('name', '{client_group}'),
            self.check('description', 'test'),
            self.check('query', 'attributes.floor = 6')
        ])
        self.cmd('eventgrid namespace client-group update -g {rg} --namespace-name {namespace} -n {client_group} --description test1 --group-query "attributes.floor = 7"', checks=[
            self.check('name', '{client_group}'),
            self.check('description', 'test1'),
            self.check('query', 'attributes.floor = 7')
        ])
        self.cmd('eventgrid namespace client-group show -g {rg} --namespace-name {namespace} -n {client_group}', checks=[
            self.check('name', '{client_group}'),
            self.check('description', 'test1'),
            self.check('query', 'attributes.floor = 7')
        ])
        self.cmd('eventgrid namespace client-group list -g {rg} --namespace-name {namespace}', checks=[
            self.check('[1].name', '{client_group}'),
            self.check('[1].description', 'test1'),
            self.check('[1].query', 'attributes.floor = 7')
        ])
        self.cmd('eventgrid namespace client-group delete -g {rg} --namespace-name {namespace} -n {client_group} -y')
        self.cmd('eventgrid namespace client delete -g {rg} -n {client} --namespace-name {namespace} -y')

    @ResourceGroupPreparer(name_prefix='test_eventgrid_topic', location='eastus')
    def test_topic(self):
        self.kwargs.update({
            'namespace': self.create_random_name('name', 10),
            'topic': self.create_random_name('topic', 15),
            'topic_space': self.create_random_name('space', 15),
            'event_subscription': self.create_random_name('sub', 10)
        })

        self.cmd('eventgrid namespace create -g {rg} -n {namespace} --topic-spaces-configuration "{{maximumSessionExpiryInHours:1,state:enabled}}"', checks=[
            self.check('resourceGroup', '{rg}'),
            self.check('name', '{namespace}'),
            self.check('sku.capacity', 1),
            self.check('sku.name', 'Standard'),
            self.check('topicSpacesConfiguration.maximumClientSessionsPerAuthenticationName', 1),
            self.check('topicSpacesConfiguration.maximumSessionExpiryInHours', 1),
            self.check('topicSpacesConfiguration.state', 'Enabled')
        ])
        self.cmd('eventgrid namespace topic create -g {rg} -n {topic} --namespace-name {namespace} --event-retention-in-days 1 --publisher-type custom', checks=[
            self.check('name', '{topic}'),
            self.check('eventRetentionInDays', 1),
            self.check('publisherType', 'Custom')
        ])
        self.cmd('eventgrid namespace topic update -g {rg} -n {topic} --namespace-name {namespace} --event-retention-in-days 1 --input-schema CloudEventSchemaV1_0', checks=[
            self.check('name', '{topic}'),
            self.check('eventRetentionInDays', 1),
            self.check('publisherType', 'Custom'),
            self.check('inputSchema', 'CloudEventSchemaV1_0')
        ])
        self.cmd('eventgrid namespace topic show -g {rg} -n {topic} --namespace-name {namespace}', checks=[
            self.check('name', '{topic}'),
            self.check('eventRetentionInDays', 1),
            self.check('publisherType', 'Custom'),
            self.check('inputSchema', 'CloudEventSchemaV1_0')
        ])
        self.cmd('eventgrid namespace topic list -g {rg} --namespace-name {namespace}', checks=[
            self.check('[0].name', '{topic}'),
            self.check('[0].eventRetentionInDays', 1),
            self.check('[0].publisherType', 'Custom'),
            self.check('[0].inputSchema', 'CloudEventSchemaV1_0')
        ])
        self.cmd('eventgrid namespace topic-space create -g {rg} --namespace-name {namespace} -n {topic_space} --description test --topic-templates [\'name=topicspace\']', checks=[
            self.check('name', '{topic_space}'),
            self.check('description', 'test'),
            self.check('topicTemplates[0]', 'name=topicspace')
        ])
        self.cmd('eventgrid namespace topic-space update -g {rg} --namespace-name {namespace} -n {topic_space} --description test1', checks=[
            self.check('name', '{topic_space}'),
            self.check('description', 'test1'),
            self.check('topicTemplates[0]', 'name=topicspace')
        ])
        self.cmd('eventgrid namespace topic-space show -g {rg} --namespace-name {namespace} -n {topic_space}', checks=[
            self.check('name', '{topic_space}'),
            self.check('topicTemplates[0]', 'name=topicspace')
        ])
        self.cmd('eventgrid namespace topic-space list -g {rg} --namespace-name {namespace}', checks=[
            self.check('[0].name', '{topic_space}'),
            self.check('[0].topicTemplates[0]', 'name=topicspace')
        ])

        self.cmd('eventgrid namespace topic event-subscription create -g {rg} --topic-name {topic} -n {event_subscription} --namespace-name {namespace} --delivery-configuration "{{deliveryMode:Queue,queue:{{receiveLockDurationInSeconds:60,maxDeliveryCount:4,eventTimeToLive:P1D}}}}"', checks=[
            self.check('name', '{event_subscription}'),
            self.check('deliveryConfiguration.deliveryMode', 'Queue'),
            self.check('deliveryConfiguration.queue.eventTimeToLive', 'P1D'),
            self.check('deliveryConfiguration.queue.maxDeliveryCount', 4),
            self.check('deliveryConfiguration.queue.receiveLockDurationInSeconds', 60)
        ])
        self.cmd('eventgrid namespace topic event-subscription update -g {rg} --topic-name {topic} -n {event_subscription} --namespace-name {namespace} --delivery-configuration "{{deliveryMode:Queue,queue:{{receiveLockDurationInSeconds:70,maxDeliveryCount:5,eventTimeToLive:P1D}}}}" --filters-configuration "{{includedEventTypes:[\'All\']}}"', checks=[
            self.check('name', '{event_subscription}'),
            self.check('deliveryConfiguration.deliveryMode', 'Queue'),
            self.check('deliveryConfiguration.queue.eventTimeToLive', 'P1D'),
            self.check('deliveryConfiguration.queue.maxDeliveryCount', 5),
            self.check('deliveryConfiguration.queue.receiveLockDurationInSeconds', 70),
            self.check('filtersConfiguration.includedEventTypes[0]', 'All')
        ])
        self.cmd('eventgrid namespace topic event-subscription show -g {rg} --topic-name {topic} -n {event_subscription} --namespace-name {namespace}', checks=[
            self.check('name', '{event_subscription}'),
            self.check('deliveryConfiguration.deliveryMode', 'Queue'),
            self.check('deliveryConfiguration.queue.eventTimeToLive', 'P1D'),
            self.check('deliveryConfiguration.queue.maxDeliveryCount', 5),
            self.check('deliveryConfiguration.queue.receiveLockDurationInSeconds', 70),
            self.check('filtersConfiguration.includedEventTypes[0]', 'All')
        ])
        self.cmd('eventgrid namespace topic event-subscription list -g {rg} --topic-name {topic} --namespace-name {namespace}', checks=[
            self.check('[0].name', '{event_subscription}'),
            self.check('[0].deliveryConfiguration.deliveryMode', 'Queue'),
            self.check('[0].deliveryConfiguration.queue.eventTimeToLive', 'P1D'),
            self.check('[0].deliveryConfiguration.queue.maxDeliveryCount', 5),
            self.check('[0].deliveryConfiguration.queue.receiveLockDurationInSeconds', 70),
            self.check('[0].filtersConfiguration.includedEventTypes[0]', 'All')
        ])
        self.cmd('eventgrid namespace topic event-subscription delete -g {rg} --topic-name {topic} -n {event_subscription} --namespace-name {namespace} -y')
        self.cmd('eventgrid namespace topic-space delete -g {rg} --namespace-name {namespace} -n {topic_space} -y')
        self.cmd('eventgrid namespace topic delete -g {rg} -n {topic} --namespace-name {namespace} -y')

    @ResourceGroupPreparer(name_prefix='test_eventgrid_permission_binding', location='eastus')
    def test_permission_binding(self):
        self.kwargs.update({
            'namespace': self.create_random_name('name', 10),
            'topic_space': self.create_random_name('space', 15),
            'client_group': self.create_random_name('group', 15),
            'permission_binding': self.create_random_name('per', 10)
        })

        self.cmd('eventgrid namespace create -g {rg} -n {namespace} --topic-spaces-configuration "{{maximumSessionExpiryInHours:1,state:enabled}}"', checks=[
            self.check('resourceGroup', '{rg}'),
            self.check('name', '{namespace}'),
            self.check('sku.capacity', 1),
            self.check('sku.name', 'Standard'),
            self.check('topicSpacesConfiguration.maximumClientSessionsPerAuthenticationName', 1),
            self.check('topicSpacesConfiguration.maximumSessionExpiryInHours', 1),
            self.check('topicSpacesConfiguration.state', 'Enabled')
        ])
        self.cmd('eventgrid namespace topic-space create -g {rg} --namespace-name {namespace} -n {topic_space} --description test --topic-templates [\'name=topicspace\']', checks=[
            self.check('name', '{topic_space}'),
            self.check('description', 'test'),
            self.check('topicTemplates[0]', 'name=topicspace')
        ])
        self.cmd('eventgrid namespace client-group create -g {rg} --namespace-name {namespace} -n {client_group} --description test --group-query "attributes.floor = 6"', checks=[
            self.check('resourceGroup', '{rg}'),
            self.check('name', '{client_group}'),
            self.check('description', 'test'),
            self.check('query', 'attributes.floor = 6')
        ])
        self.cmd('eventgrid namespace permission-binding create -g {rg} --namespace-name {namespace} -n {permission_binding} --client-group-name {client_group} --permission publisher --topic-space-name {topic_space}', checks=[
            self.check('clientGroupName', '{client_group}'),
            self.check('name', '{permission_binding}'),
            self.check('permission', 'Publisher'),
            self.check('topicSpaceName', '{topic_space}')
        ])
        self.cmd('eventgrid namespace permission-binding update -g {rg} --namespace-name {namespace} -n {permission_binding} --client-group-name {client_group} --topic-space-name {topic_space} --description test', checks=[
            self.check('clientGroupName', '{client_group}'),
            self.check('name', '{permission_binding}'),
            self.check('permission', 'Publisher'),
            self.check('topicSpaceName', '{topic_space}')
        ])
        self.cmd('eventgrid namespace permission-binding show -g {rg} --namespace-name {namespace} -n {permission_binding}', checks=[
            self.check('clientGroupName', '{client_group}'),
            self.check('name', '{permission_binding}'),
            self.check('permission', 'Publisher'),
            self.check('topicSpaceName', '{topic_space}')
        ])
        self.cmd('eventgrid namespace permission-binding list -g {rg} --namespace-name {namespace}', checks=[
            self.check('[0].clientGroupName', '{client_group}'),
            self.check('[0].name', '{permission_binding}'),
            self.check('[0].permission', 'Publisher'),
            self.check('[0].topicSpaceName', '{topic_space}')
        ])
        self.cmd('eventgrid namespace permission-binding delete -g {rg} --namespace-name {namespace} -n {permission_binding} -y')
