# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
import unittest
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer
from knack.util import CLIError


class EventGridTests(ScenarioTest):
    @unittest.skip('Will be re-enabled once global operations are enabled for 2020-01-01-preview API version')
    def test_topic_types(self):

        self.kwargs.update({
            'topic_type_name': 'Microsoft.Resources.Subscriptions'
        })

        self.cmd('az eventgrid topic-type list', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/topicTypes')
        ])
        self.cmd('az eventgrid topic-type show --name {topic_type_name}', checks=[
            self.check('type', 'Microsoft.EventGrid/topicTypes'),
            self.check('name', self.kwargs['topic_type_name'])
        ])
        self.cmd('az eventgrid topic-type list-event-types --name {topic_type_name}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/topicTypes/eventTypes')
        ])

    @ResourceGroupPreparer()
    def test_create_domain(self, resource_group):
        endpoint_url = 'https://devexpfuncappdestination.azurewebsites.net/runtime/webhooks/EventGrid?functionName=EventGridTrigger1&code=<HIDDEN>'
        endpoint_baseurl = 'https://devexpfuncappdestination.azurewebsites.net/runtime/webhooks/EventGrid'

        domain_name = self.create_random_name(prefix='cli', length=40)
        domain_name2 = self.create_random_name(prefix='cli', length=40)
        domain_name3 = self.create_random_name(prefix='cli', length=40)
        domain_name4 = self.create_random_name(prefix='cli', length=40)

        domain_topic_name1 = self.create_random_name(prefix='cli', length=40)
        domain_topic_name2 = self.create_random_name(prefix='cli', length=40)

        event_subscription_name = self.create_random_name(prefix='cli', length=40)

        self.kwargs.update({
            'domain_name': domain_name,
            'domain_name2': domain_name2,
            'domain_name3': domain_name3,
            'domain_name4': domain_name4,
            'domain_topic_name1': domain_topic_name1,
            'domain_topic_name2': domain_topic_name2,
            'location': 'centraluseuap',
            'event_subscription_name': event_subscription_name,
            'endpoint_url': endpoint_url,
            'endpoint_baseurl': endpoint_baseurl
        })

        self.kwargs['resource_id'] = self.cmd('az eventgrid domain create --name {domain_name} --resource-group {rg} --location {location}', checks=[
            self.check('type', 'Microsoft.EventGrid/domains'),
            self.check('name', self.kwargs['domain_name']),
            self.check('provisioningState', 'Succeeded'),
        ]).get_output_in_json()['id']

        self.cmd('az eventgrid domain show --name {domain_name} --resource-group {rg}', checks=[
            self.check('type', 'Microsoft.EventGrid/domains'),
            self.check('name', self.kwargs['domain_name']),
        ])

        # Test various failure conditions
        # Input mappings cannot be provided when input schema is not customeventschema
        with self.assertRaises(CLIError):
            self.cmd('az eventgrid domain create --name {domain_name2} --resource-group {rg} --location {location} --input-schema eventgridschema --input-mapping-fields domain=mydomainField')

        # Input mappings must be provided when input schema is customeventschema
        with self.assertRaises(CLIError):
            self.cmd('az eventgrid domain create --name {domain_name2} --resource-group {rg} --location {location} --input-schema customeventschema')

        self.cmd('az eventgrid domain create --name {domain_name2} --resource-group {rg} --location {location} --input-schema CloudEventSchemaV1_0', checks=[
            self.check('type', 'Microsoft.EventGrid/domains'),
            self.check('name', self.kwargs['domain_name2']),
            self.check('provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid domain create --name {domain_name3} --resource-group {rg} --location {location} --input-schema Customeventschema --input-mapping-fields domain=mydomainField eventType=myEventTypeField topic=myTopic --input-mapping-default-values subject=DefaultSubject dataVersion=1.0', checks=[
            self.check('type', 'Microsoft.EventGrid/domains'),
            self.check('name', self.kwargs['domain_name3']),
            self.check('provisioningState', 'Succeeded'),
        ])

        outputdomain = self.cmd('az eventgrid domain create --name {domain_name4} --resource-group {rg} --location {location} --allow-traffic-from-all-ips False --inbound-ip-rules 19.12.43.90/102 allow --inbound-ip-rules 19.12.43.70/81 allow').get_output_in_json()
        self.check(outputdomain['type'], 'Microsoft.EventGrid/domains')
        self.check(outputdomain['name'], self.kwargs['domain_name4'])
        self.check(outputdomain['allowTrafficFromAllIps'], 'False')
        self.check(outputdomain['inboundIpRules'][0], '19.12.43.90/102')
        self.check(outputdomain['inboundIpRules'][1], '19.12.43.70/81')
        self.check(outputdomain['provisioningState'], 'Succeeded')

        self.cmd('az eventgrid domain update --name {domain_name} --resource-group {rg} --tags Dept=IT', checks=[
            self.check('name', self.kwargs['domain_name']),
            self.check('tags', {'Dept': 'IT'}),
        ])

        self.cmd('az eventgrid domain list --resource-group {rg}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/domains'),
            self.check('[0].name', self.kwargs['domain_name']),
            self.check('[0].provisioningState', 'Succeeded')
        ])

        out2 = self.cmd('az eventgrid domain list --resource-group {rg} --odata-query "name eq \'{domain_name}\'"').get_output_in_json()
        self.assertIsNotNone(out2[0]['type'])
        self.assertIsNotNone(out2[0]['name'])
        self.check(out2[0]['type'], 'Microsoft.EventGrid/domains')
        self.check(out2[0]['name'], self.kwargs['domain_name'])
        self.check(out2[0]['provisioningState'], 'Succeeded')

        output = self.cmd('az eventgrid domain key list --name {domain_name} --resource-group {rg}').get_output_in_json()
        self.assertIsNotNone(output['key1'])
        self.assertIsNotNone(output['key2'])

        output = self.cmd('az eventgrid domain key regenerate --name {domain_name} --resource-group {rg} --key-name key1').get_output_in_json()
        self.assertIsNotNone(output['key1'])
        self.assertIsNotNone(output['key2'])

        self.cmd('az eventgrid domain key regenerate --name {domain_name} --resource-group {rg} --key-name key2').get_output_in_json()
        self.assertIsNotNone(output['key1'])
        self.assertIsNotNone(output['key2'])

        # Event subscriptions to domain with All for --included-event-types.

        self.cmd('az eventgrid event-subscription create --resource-id {resource_id} --name {event_subscription_name} --endpoint \"{endpoint_url}\" --included-event-types All', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl'])
        ])

        self.cmd('az eventgrid event-subscription show --resource-id {resource_id} --name {event_subscription_name}', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
        ])

        self.cmd('az eventgrid event-subscription show --resource-id {resource_id} --name {event_subscription_name} --include-full-endpoint-url', checks=[
            self.check('destination.endpointUrl', self.kwargs['endpoint_url']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl'])
        ])

        self.cmd('az eventgrid event-subscription update --resource-id {resource_id} --name {event_subscription_name} --endpoint \"{endpoint_url}\"', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl'])
        ])

        self.cmd('az eventgrid event-subscription list --source-resource-id {resource_id}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])
        self.cmd('az eventgrid event-subscription delete --resource-id {resource_id} --name {event_subscription_name}')

        # Event subscriptions to a domain topic
        self.kwargs.update({
            'domain_topic_resource_id': self.kwargs['resource_id'] + "/topics/" + self.kwargs['domain_topic_name1']
        })

        self.cmd('az eventgrid event-subscription create --resource-id {domain_topic_resource_id} --name {event_subscription_name} --endpoint \"{endpoint_url}\"', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl'])
        ])

        self.cmd('az eventgrid event-subscription show --resource-id {domain_topic_resource_id} --name {event_subscription_name}', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
        ])

        # Create domain topics under domain

        self.kwargs['resource_id_domain_topic2'] = self.cmd('az eventgrid domain topic create --resource-group {rg} --domain-name {domain_name} --name {domain_topic_name2}', checks=[
            self.check('type', 'Microsoft.EventGrid/domains/topics'),
            self.check('name', self.kwargs['domain_topic_name2']),
            self.check('provisioningState', 'Succeeded')
        ])

        self.cmd('az eventgrid domain topic show --resource-group {rg} --domain-name {domain_name} --name {domain_topic_name2}', checks=[
            self.check('type', 'Microsoft.EventGrid/domains/topics'),
            self.check('name', self.kwargs['domain_topic_name2']),
            self.check('provisioningState', 'Succeeded')
        ])

        # Now that an event subscription to a domain topic has been created, it would have internally resulted in creation of
        # the corresponding auto-managed domain topic. Hence, we should now be able to list the set of domain topics under the domain.
        # In the future, we can expand this to support CRUD operations for domain topics (i.e. manual management of domain topics) directly.
        self.cmd('az eventgrid domain topic list --resource-group {rg} --domain-name {domain_name}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/domains/topics')
        ])

        self.cmd('az eventgrid domain topic list --resource-group {rg} --domain-name {domain_name} --odata-query "name ne \'{domain_topic_name2}\'"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/domains/topics')
        ])

        self.cmd('az eventgrid domain topic show --resource-group {rg} --domain-name {domain_name} --name {domain_topic_name1}', checks=[
            self.check('type', 'Microsoft.EventGrid/domains/topics'),
            self.check('id', self.kwargs['domain_topic_resource_id']),
            self.check('name', self.kwargs['domain_topic_name1']),
        ])

        self.cmd('az eventgrid event-subscription show --resource-id {domain_topic_resource_id} --name {event_subscription_name} --include-full-endpoint-url', checks=[
            self.check('destination.endpointUrl', self.kwargs['endpoint_url']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl'])
        ])

        self.cmd('az eventgrid event-subscription update --resource-id {domain_topic_resource_id} --name {event_subscription_name} --endpoint \"{endpoint_url}\"', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl'])
        ])

        self.cmd('az eventgrid event-subscription list --source-resource-id {domain_topic_resource_id}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --source-resource-id {domain_topic_resource_id} --odata-query "CONTAINS(name, \'{event_subscription_name}\')"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription delete --resource-id {domain_topic_resource_id} --name {event_subscription_name}')

        self.cmd('az eventgrid domain topic delete --domain-name {domain_name} --name {domain_topic_name1} --resource-group {rg}')
        self.cmd('az eventgrid domain topic delete --domain-name {domain_name} --name {domain_topic_name2} --resource-group {rg}')

        self.cmd('az eventgrid domain delete --name {domain_name} --resource-group {rg}')
        self.cmd('az eventgrid domain delete --name {domain_name2} --resource-group {rg}')
        self.cmd('az eventgrid domain delete --name {domain_name3} --resource-group {rg}')

    @ResourceGroupPreparer()
    def test_create_topic(self, resource_group):
        endpoint_url = 'https://devexpfuncappdestination.azurewebsites.net/runtime/webhooks/EventGrid?functionName=EventGridTrigger1&code=<HIDDEN>'
        endpoint_baseurl = 'https://devexpfuncappdestination.azurewebsites.net/runtime/webhooks/EventGrid'

        topic_name = self.create_random_name(prefix='cli', length=40)
        topic_name2 = self.create_random_name(prefix='cli', length=40)
        topic_name3 = self.create_random_name(prefix='cli', length=40)
        topic_name4 = self.create_random_name(prefix='cli', length=40)
        event_subscription_name = self.create_random_name(prefix='cli', length=40)

        self.kwargs.update({
            'topic_name': topic_name,
            'topic_name2': topic_name2,
            'topic_name3': topic_name3,
            'topic_name4': topic_name4,
            'location': 'centraluseuap',
            'event_subscription_name': event_subscription_name,
            'endpoint_url': endpoint_url,
            'endpoint_baseurl': endpoint_baseurl
        })

        scope = self.cmd('az eventgrid topic create --name {topic_name} --resource-group {rg} --location {location}', checks=[
            self.check('type', 'Microsoft.EventGrid/topics'),
            self.check('name', self.kwargs['topic_name']),
            self.check('provisioningState', 'Succeeded'),
        ]).get_output_in_json()['id']

        self.cmd('az eventgrid topic show --name {topic_name} --resource-group {rg}', checks=[
            self.check('type', 'Microsoft.EventGrid/topics'),
            self.check('name', self.kwargs['topic_name']),
        ])

        self.kwargs.update({
            'scope': scope,
        })

        # Test various failure conditions

        # Input mappings cannot be provided when input schema is not customeventschema
        with self.assertRaises(CLIError):
            self.cmd('az eventgrid topic create --name {topic_name2} --resource-group {rg} --location {location} --input-schema eventgridschema --input-mapping-fields topic=myTopicField')

        # Input mappings must be provided when input schema is customeventschema
        with self.assertRaises(CLIError):
            self.cmd('az eventgrid topic create --name {topic_name2} --resource-group {rg} --location {location} --input-schema customeventschema')

        self.cmd('az eventgrid topic create --name {topic_name2} --resource-group {rg} --location {location} --input-schema CloudEventSchemaV1_0', checks=[
            self.check('type', 'Microsoft.EventGrid/topics'),
            self.check('name', self.kwargs['topic_name2']),
            self.check('provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid topic create --name {topic_name3} --resource-group {rg} --location {location} --input-schema Customeventschema --input-mapping-fields topic=myTopicField eventType=myEventTypeField --input-mapping-default-values subject=DefaultSubject dataVersion=1.0', checks=[
            self.check('type', 'Microsoft.EventGrid/topics'),
            self.check('name', self.kwargs['topic_name3']),
            self.check('provisioningState', 'Succeeded'),
        ])

        outputtopic = self.cmd('az eventgrid topic create --name {topic_name4} --resource-group {rg} --location {location} --allow-traffic-from-all-ips False --inbound-ip-rules 19.12.43.90/102 allow --inbound-ip-rules 19.12.43.70/81 allow').get_output_in_json()
        self.check(outputtopic['type'], 'Microsoft.EventGrid/topics')
        self.check(outputtopic['name'], self.kwargs['topic_name4'])
        self.check(outputtopic['allowTrafficFromAllIps'], 'False')
        self.check(outputtopic['inboundIpRules'][0], '19.12.43.90/102')
        self.check(outputtopic['inboundIpRules'][1], '19.12.43.70/81')
        self.check(outputtopic['provisioningState'], 'Succeeded')

        self.cmd('az eventgrid topic update --name {topic_name} --resource-group {rg} --tags Dept=IT', checks=[
            self.check('name', self.kwargs['topic_name']),
            self.check('tags', {'Dept': 'IT'}),
        ])

        self.cmd('az eventgrid topic list --resource-group {rg}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/topics'),
            self.check('[0].name', self.kwargs['topic_name']),
        ])

        self.cmd('az eventgrid topic list --resource-group {rg} --odata-query "name eq \'{topic_name}\'"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/topics'),
            self.check('[0].name', self.kwargs['topic_name']),
        ])

        output = self.cmd('az eventgrid topic key list --name {topic_name} --resource-group {rg}').get_output_in_json()
        self.assertIsNotNone(output['key1'])
        self.assertIsNotNone(output['key2'])

        output = self.cmd('az eventgrid topic key regenerate --name {topic_name} --resource-group {rg} --key-name key1').get_output_in_json()
        self.assertIsNotNone(output['key1'])
        self.assertIsNotNone(output['key2'])

        self.cmd('az eventgrid topic key regenerate --name {topic_name} --resource-group {rg} --key-name key2').get_output_in_json()
        self.assertIsNotNone(output['key1'])
        self.assertIsNotNone(output['key2'])

        self.cmd('az eventgrid event-subscription create --source-resource-id {scope} --name {event_subscription_name} --endpoint \"{endpoint_url}\"', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl'])
        ])

        self.cmd('az eventgrid event-subscription show --source-resource-id {scope} --name {event_subscription_name}', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
        ])

        self.cmd('az eventgrid event-subscription show --source-resource-id {scope} --name {event_subscription_name} --include-full-endpoint-url', checks=[
            self.check('destination.endpointUrl', self.kwargs['endpoint_url']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl'])
        ])

        self.cmd('az eventgrid event-subscription update --source-resource-id {scope} --name {event_subscription_name} --endpoint \"{endpoint_url}\"', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl'])
        ])

        self.cmd('az eventgrid event-subscription list --source-resource-id {scope}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --source-resource-id {scope} --odata-query "name eq \'{event_subscription_name}\'"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --topic-type Microsoft.EventGrid.Topics --location {location}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --topic-type Microsoft.EventGrid.Topics --location {location} --odata-query "CONTAINS(name,\'{event_subscription_name}\')"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription delete --source-resource-id {scope} --name {event_subscription_name}')

# TESTS FOR DEPRECATED ARGUMENTS
# Using TopicName and ResourceGroup combination
        self.cmd('az eventgrid event-subscription create --topic-name {topic_name} -g {rg} --name {event_subscription_name} --endpoint \"{endpoint_url}\"', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl'])
        ])

        self.cmd('az eventgrid event-subscription show --topic-name {topic_name} -g {rg} --name {event_subscription_name}', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
        ])

        self.cmd('az eventgrid event-subscription show --topic-name {topic_name} -g {rg} --name {event_subscription_name} --include-full-endpoint-url', checks=[
            self.check('destination.endpointUrl', self.kwargs['endpoint_url']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl'])
        ])

        self.cmd('az eventgrid event-subscription update --topic-name {topic_name} -g {rg} --name {event_subscription_name} --endpoint \"{endpoint_url}\"', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl'])
        ])

        self.cmd('az eventgrid event-subscription list --topic-name {topic_name} --resource-group {rg}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription delete --topic-name {topic_name} -g {rg} --name {event_subscription_name}')
# END OF Using TopicName and ResourceGroup combination

# Using --resource-id approach
        self.cmd('az eventgrid event-subscription create --resource-id {scope} --name {event_subscription_name} --endpoint \"{endpoint_url}\"', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl'])
        ])

        self.cmd('az eventgrid event-subscription show --resource-id {scope} --name {event_subscription_name}', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
        ])

        self.cmd('az eventgrid event-subscription show --resource-id {scope} --name {event_subscription_name} --include-full-endpoint-url', checks=[
            self.check('destination.endpointUrl', self.kwargs['endpoint_url']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl'])
        ])

        self.cmd('az eventgrid event-subscription update --resource-id {scope} --name {event_subscription_name} --endpoint \"{endpoint_url}\"', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl'])
        ])

        self.cmd('az eventgrid event-subscription list --resource-id {scope}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --resource-id {scope} --odata-query "CONTAINS(name,\'{event_subscription_name}\')"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --topic-type Microsoft.EventGrid.Topics --location {location}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --topic-type Microsoft.EventGrid.Topics --location {location} --odata-query "CONTAINS(name,\'{event_subscription_name}\')"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription delete --resource-id {scope} --name {event_subscription_name}')
# END of using --resource-id approach

# END OF DEPRECATED ARGUMENTS
        self.cmd('az eventgrid topic delete --name {topic_name} --resource-group {rg}')

    @ResourceGroupPreparer()
    @unittest.skip('Will be re-enabled once global operations are enabled for 2020-01-01-preview API version')
    def test_create_event_subscriptions_to_arm_resource_group(self, resource_group):
        event_subscription_name = 'eventsubscription2'
        endpoint_url = 'https://devexpfuncappdestination.azurewebsites.net/runtime/webhooks/EventGrid?functionName=EventGridTrigger1&code=<HIDDEN>'
        endpoint_baseurl = 'https://devexpfuncappdestination.azurewebsites.net/runtime/webhooks/EventGrid'

        scope = self.cmd('az group show -n {} -ojson'.format(resource_group)).get_output_in_json()['id']

        self.kwargs.update({
            'event_subscription_name': event_subscription_name,
            'endpoint_url': endpoint_url,
            'endpoint_baseurl': endpoint_baseurl,
            'scope': scope
        })

        self.cmd('az eventgrid event-subscription create --source-resource-id {scope} --name {event_subscription_name} --endpoint \"{endpoint_url}\" --subject-begins-with mysubject_prefix', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl']),
        ])

        self.cmd('az eventgrid event-subscription show --source-resource-id {scope} --name {event_subscription_name}', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('filter.subjectBeginsWith', 'mysubject_prefix')
        ])
        self.cmd('az eventgrid event-subscription show --source-resource-id {scope} --include-full-endpoint-url --name {event_subscription_name}', checks=[
            self.check('destination.endpointUrl', self.kwargs['endpoint_url']),
        ])

        self.cmd('az eventgrid event-subscription update --source-resource-id {scope} --name {event_subscription_name}  --endpoint \"{endpoint_url}\" --subject-ends-with .jpg', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl']),
            self.check('filter.subjectEndsWith', '.jpg'),
        ])

        self.cmd('az eventgrid event-subscription list --source-resource-id {scope}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --source-resource-id {scope} --odata-query "name eq \'{event_subscription_name}\'"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --topic-type Microsoft.Resources.ResourceGroups --location global', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --topic-type Microsoft.Resources.ResourceGroups --location global --odata-query "name eq \'{event_subscription_name}\'"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --location global --resource-group {rg}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --location global --resource-group {rg} --odata-query "name eq \'{event_subscription_name}\'"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription delete --source-resource-id {scope} --name {event_subscription_name}')

# TESTS FOR DEPRECATED ARGUMENTS
# --resource-id
        self.cmd('az eventgrid event-subscription create --resource-id {scope} --name {event_subscription_name} --endpoint \"{endpoint_url}\" --subject-begins-with mysubject_prefix', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl']),
        ])

        self.cmd('az eventgrid event-subscription show --resource-id {scope} --name {event_subscription_name}', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('filter.subjectBeginsWith', 'mysubject_prefix')
        ])
        self.cmd('az eventgrid event-subscription show --resource-id {scope} --include-full-endpoint-url --name {event_subscription_name}', checks=[
            self.check('destination.endpointUrl', self.kwargs['endpoint_url']),
        ])

        self.cmd('az eventgrid event-subscription update --resource-id {scope} --name {event_subscription_name}  --endpoint \"{endpoint_url}\" --subject-ends-with .jpg', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl']),
            self.check('filter.subjectEndsWith', '.jpg'),
        ])

        self.cmd('az eventgrid event-subscription list --resource-id {scope}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --resource-id {scope} --odata-query "name eq \'{event_subscription_name}\'"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --topic-type Microsoft.Resources.ResourceGroups --location global', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --topic-type Microsoft.Resources.ResourceGroups --location global --odata-query "name eq \'{event_subscription_name}\'"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --location global --resource-group {rg}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --location global --resource-group {rg} --odata-query "name eq \'{event_subscription_name}\'"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription delete --resource-id {scope} --name {event_subscription_name}')
# end --resource-id
# --resource-group
        self.cmd('az eventgrid event-subscription create -g {rg} --name {event_subscription_name} --endpoint \"{endpoint_url}\" --subject-begins-with mysubject_prefix', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl'])
        ])

        self.cmd('az eventgrid event-subscription show -g {rg} --name {event_subscription_name}', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('filter.subjectBeginsWith', 'mysubject_prefix')
        ])
        self.cmd('az eventgrid event-subscription show --include-full-endpoint-url --resource-group {rg} --name {event_subscription_name}', checks=[
            self.check('destination.endpointUrl', self.kwargs['endpoint_url']),
        ])

        self.cmd('az eventgrid event-subscription update -g {rg} --name {event_subscription_name}  --endpoint \"{endpoint_url}\" --subject-ends-with .jpg', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl']),
            self.check('filter.subjectEndsWith', '.jpg'),
        ])

        self.cmd('az eventgrid event-subscription list --location global -g {rg}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --location global -g {rg} --odata-query "name eq \'{event_subscription_name}\'"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription delete --resource-group {rg} --name {event_subscription_name}')

# end --resource-group
# END OF TESTS FOR DEPRECATED ARGUMENTS

    @ResourceGroupPreparer(name_prefix='clieventgridrg', location='centraluseuap')
    @StorageAccountPreparer(name_prefix='clieventgrid', location='centraluseuap')
    def test_create_event_subscriptions_to_resource(self, resource_group, resource_group_location, storage_account):
        event_subscription_name = self.create_random_name(prefix='cli', length=40)
        endpoint_url = 'https://devexpfuncappdestination.azurewebsites.net/runtime/webhooks/EventGrid?functionName=EventGridTrigger1&code=<HIDDEN>'
        endpoint_baseurl = 'https://devexpfuncappdestination.azurewebsites.net/runtime/webhooks/EventGrid'

        self.kwargs.update({
            'event_subscription_name': event_subscription_name,
            'location': 'centraluseuap',
            'endpoint_url': endpoint_url,
            'endpoint_baseurl': endpoint_baseurl
        })

        self.kwargs['source_resource_id'] = self.cmd('storage account create -g {rg} -n {sa} --sku Standard_LRS -l {location}').get_output_in_json()['id']
        self.cmd('az storage account update -g {rg} -n {sa} --set kind=StorageV2')

        self.cmd('az eventgrid event-subscription create --source-resource-id {source_resource_id} --name {event_subscription_name} --endpoint \"{endpoint_url}\"', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
        ])

        self.cmd('az eventgrid event-subscription show --source-resource-id {source_resource_id} --name {event_subscription_name}', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
        ])
        self.cmd('az eventgrid event-subscription show --include-full-endpoint-url --resource-id {source_resource_id} --name {event_subscription_name}', checks=[
            self.check('destination.endpointUrl', self.kwargs['endpoint_url']),
        ])

        self.cmd('az eventgrid event-subscription update --source-resource-id {source_resource_id} --name {event_subscription_name} --endpoint \"{endpoint_url}\" --subject-ends-with .jpg', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl']),
            self.check('filter.subjectEndsWith', '.jpg')
        ])

        self.cmd('az eventgrid event-subscription list --source-resource-id {source_resource_id}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --topic-type Microsoft.Storage.StorageAccounts --location {location}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --topic-type Microsoft.Storage.StorageAccounts --location {location} --resource-group {rg}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --location {location} --resource-group {rg}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --location {location}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --source-resource-id {source_resource_id} --odata-query "CONTAINS(name,\'{event_subscription_name}\')"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --topic-type Microsoft.Storage.StorageAccounts --location {location} --odata-query "CONTAINS(name,\'{event_subscription_name}\')"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --topic-type Microsoft.Storage.StorageAccounts --location {location} --resource-group {rg} --odata-query "CONTAINS(name,\'{event_subscription_name}\')"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --location {location} --resource-group {rg} --odata-query "name eq \'{event_subscription_name}\'"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --location {location} --odata-query "name eq \'{event_subscription_name}\'"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription delete --source-resource-id {source_resource_id} --name {event_subscription_name}')

# TESTS FOR DEPRECATED ARGUMENTS

        self.kwargs['resource_id'] = self.cmd('az storage account show -g {rg} -n {sa}').get_output_in_json()['id']

        self.cmd('az eventgrid event-subscription create --resource-id {resource_id} --name {event_subscription_name} --endpoint \"{endpoint_url}\"', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
        ])

        self.cmd('az eventgrid event-subscription show --resource-id {resource_id} --name {event_subscription_name}', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
        ])
        self.cmd('az eventgrid event-subscription show --include-full-endpoint-url --resource-id {resource_id} --name {event_subscription_name}', checks=[
            self.check('destination.endpointUrl', self.kwargs['endpoint_url']),
        ])

        self.cmd('az eventgrid event-subscription update --resource-id {resource_id} --name {event_subscription_name} --endpoint \"{endpoint_url}\" --subject-ends-with .jpg', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl']),
            self.check('filter.subjectEndsWith', '.jpg')
        ])

        self.cmd('az eventgrid event-subscription list --resource-id {resource_id}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --topic-type Microsoft.Storage.StorageAccounts --location {location}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --topic-type Microsoft.Storage.StorageAccounts --location {location} --resource-group {rg}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --location {location} --resource-group {rg}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --location {location}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --resource-id {resource_id} --odata-query "CONTAINS(name,\'{event_subscription_name}\')"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --topic-type Microsoft.Storage.StorageAccounts --location {location} --odata-query "CONTAINS(name,\'{event_subscription_name}\')"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --topic-type Microsoft.Storage.StorageAccounts --location {location} --resource-group {rg} --odata-query "name eq \'{event_subscription_name}\'"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --location {location} --resource-group {rg} --odata-query "name eq \'{event_subscription_name}\'"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --location {location} --odata-query "name eq \'{event_subscription_name}\'"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription delete --resource-id {resource_id} --name {event_subscription_name}')
        self.cmd('az storage account delete -y -g {rg} -n {sa}')
# END OF TESTS FOR DEPRECATED ARGUMENTS

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='clieventgrid', location='centraluseuap')
    def test_create_event_subscriptions_with_filters(self, resource_group):
        event_subscription_name = 'eventsubscription2'
        endpoint_url = 'https://devexpfuncappdestination.azurewebsites.net/runtime/webhooks/EventGrid?functionName=EventGridTrigger1&code=<HIDDEN>'
        endpoint_baseurl = 'https://devexpfuncappdestination.azurewebsites.net/runtime/webhooks/EventGrid?functionName=EventGridTrigger1'

        subject_ends_with = 'mysubject_suffix'
        event_type_1 = 'blobCreated'
        event_type_2 = 'blobUpdated'
        label_1 = 'Finance'
        label_2 = 'HR'

        self.kwargs.update({
            'event_subscription_name': event_subscription_name,
            'endpoint_url': endpoint_url,
            'endpoint_baseurl': endpoint_baseurl,
            'subject_ends_with': subject_ends_with,
            'event_type_1': event_type_1,
            'event_type_2': event_type_2,
            'label_1': label_1,
            'location': 'centraluseuap',
            'label_2': label_2
        })

        self.kwargs['source_resource_id'] = self.cmd('storage account create -g {rg} -n {sa} --sku Standard_LRS -l {location}').get_output_in_json()['id']
        self.cmd('az storage account update -g {rg} -n {sa} --set kind=StorageV2')

        self.cmd('az eventgrid event-subscription create --source-resource-id {source_resource_id} --name {event_subscription_name} --endpoint \"{endpoint_url}\" --subject-ends-with {subject_ends_with} --included-event-types {event_type_1} {event_type_2} --subject-case-sensitive --labels {label_1} {label_2}')

        # TODO: Add a verification that filter.isSubjectCaseSensitive is true after resolving why it shows as null in the response
        self.cmd('az eventgrid event-subscription show --source-resource-id {source_resource_id} --name {event_subscription_name}', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('filter.subjectEndsWith', self.kwargs['subject_ends_with']),
            self.check('filter.includedEventTypes[0]', self.kwargs['event_type_1']),
            self.check('filter.includedEventTypes[1]', self.kwargs['event_type_2']),
            self.check('labels[0]', self.kwargs['label_1']),
            self.check('labels[1]', self.kwargs['label_2']),
        ])

        self.cmd('az eventgrid event-subscription show --include-full-endpoint-url --source-resource-id {source_resource_id} --name {event_subscription_name}', checks=[
            self.check('destination.endpointUrl', self.kwargs['endpoint_url']),
        ])

        self.cmd('az eventgrid event-subscription list --source-resource-id {source_resource_id}', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription list --source-resource-id {source_resource_id} --odata-query "CONTAINS(name,\'{event_subscription_name}\')"', checks=[
            self.check('[0].type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('[0].provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription delete --source-resource-id {source_resource_id} --name {event_subscription_name}')
        self.cmd('az storage account delete -y -g {rg} -n {sa}')

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='clieventgrid', location='centraluseuap')
    def test_create_event_subscriptions_with_20180501_features(self, resource_group):
        event_subscription_name1 = 'CliTestEventsubscription1'
        event_subscription_name2 = 'CliTestEventsubscription2'
        event_subscription_name3 = 'CliTestEventsubscription3'
        storagequeue_endpoint_id = '/subscriptions/5b4b650e-28b9-4790-b3ab-ddbd88d727c4/resourceGroups/DevExpRg/providers/Microsoft.Storage/storageAccounts/devexpstg/queueServices/default/queues/stogqueuedestination'
        deadletter_endpoint_id = '/subscriptions/5b4b650e-28b9-4790-b3ab-ddbd88d727c4/resourceGroups/DevExpRg/providers/Microsoft.Storage/storageAccounts/devexpstg/blobServices/default/containers/dlq'
        hybridconnection_endpoint_id = '/subscriptions/5b4b650e-28b9-4790-b3ab-ddbd88d727c4/resourceGroups/DevExpRg/providers/Microsoft.Relay/namespaces/DevExpRelayNamespace/hybridConnections/hydbridconnectiondestination'
        servicebusqueue_endpoint_id = '/subscriptions/5b4b650e-28b9-4790-b3ab-ddbd88d727c4/resourceGroups/DevExpRg/providers/Microsoft.ServiceBus/namespaces/devexpservicebus/queues/devexpdestination'

        self.kwargs.update({
            'event_subscription_name1': event_subscription_name1,
            'event_subscription_name2': event_subscription_name2,
            'event_subscription_name3': event_subscription_name3,
            'storagequeue_endpoint_id': storagequeue_endpoint_id,
            'deadletter_endpoint_id': deadletter_endpoint_id,
            'hybridconnection_endpoint_id': hybridconnection_endpoint_id,
            'location': 'centraluseuap',
            'servicebusqueue_endpoint_id': servicebusqueue_endpoint_id,
        })

        self.kwargs['source_resource_id'] = self.cmd('storage account create -g {rg} -n {sa} --sku Standard_LRS -l {location}').get_output_in_json()['id']
        self.cmd('az storage account update -g {rg} -n {sa} --set kind=StorageV2')

        # Failure cases
        # Invalid Event TTL value
        with self.assertRaises(CLIError):
            self.cmd('az eventgrid event-subscription create --source-resource-id {source_resource_id} --name {event_subscription_name1} --endpoint-type storagequeue --endpoint {storagequeue_endpoint_id} --event-ttl 2000 --deadletter-endpoint {deadletter_endpoint_id}')

        # Invalid max delivery attempts value
        with self.assertRaises(CLIError):
            self.cmd('az eventgrid event-subscription create --source-resource-id {source_resource_id} --name {event_subscription_name1} --endpoint-type storagequeue --endpoint {storagequeue_endpoint_id} --max-delivery-attempts 31 --deadletter-endpoint {deadletter_endpoint_id}')

        # Create a storage queue destination based event subscription with cloud event schema as the delivery schema
        self.cmd('az eventgrid event-subscription create  --source-resource-id {source_resource_id} --name {event_subscription_name1} --endpoint-type stoRAgequeue --endpoint {storagequeue_endpoint_id} --event-delivery-schema cloudeventschemav1_0 --deadletter-endpoint {deadletter_endpoint_id} --subject-begins-with SomeRandomText1 --subject-ends-with SomeRandomText2')

        self.cmd('az eventgrid event-subscription show --source-resource-id {source_resource_id} --name {event_subscription_name1}', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
        ])

        # Create a hybridconnection destination based event subscription with default eventgrid event schema as the delivery schema
        self.cmd('az eventgrid event-subscription create --source-resource-id {source_resource_id} --name {event_subscription_name2} --endpoint-type HybRidConnection --endpoint {hybridconnection_endpoint_id} --deadletter-endpoint {deadletter_endpoint_id} --max-delivery-attempts 20 --event-ttl 1000 --subject-begins-with SomeRandomText1 --subject-ends-with SomeRandomText2')

        self.cmd('az eventgrid event-subscription show  --source-resource-id {source_resource_id} --name {event_subscription_name2}', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
        ])

        # Create a servicebusqueue destination based event subscription with default eventgrid event schema as the delivery schema
        self.cmd('az eventgrid event-subscription create --source-resource-id {source_resource_id} --name {event_subscription_name3} --endpoint-type SErvIcEBusQueUE --endpoint {servicebusqueue_endpoint_id} --deadletter-endpoint {deadletter_endpoint_id} --max-delivery-attempts 10 --event-ttl 1200  --subject-begins-with SomeRandomText1 --subject-ends-with SomeRandomText2')

        self.cmd('az eventgrid event-subscription show  --source-resource-id {source_resource_id} --name {event_subscription_name3}', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription delete  --source-resource-id {source_resource_id} --name {event_subscription_name1}')
        self.cmd('az eventgrid event-subscription delete  --source-resource-id {source_resource_id} --name {event_subscription_name2}')
        self.cmd('az eventgrid event-subscription delete  --source-resource-id {source_resource_id} --name {event_subscription_name3}')
        self.cmd('az storage account delete -y -g {rg} -n {sa}')

    @ResourceGroupPreparer(name_prefix='clieventgridrg', location='centraluseuap')
    @StorageAccountPreparer(name_prefix='clieventgrid', location='centraluseuap')
    def test_create_event_subscriptions_with_20200101_features(self, resource_group):
        event_subscription_name1 = 'CliTestEventsubscription1'
        event_subscription_name2 = 'CliTestEventsubscription2'
        event_subscription_name3 = 'CliTestEventsubscription3'
        servicebustopic_endpoint_id = '/subscriptions/5b4b650e-28b9-4790-b3ab-ddbd88d727c4/resourceGroups/DevExpRg/providers/Microsoft.ServiceBus/namespaces/devexpservicebus/topics/devexptopic1'
        azurefunction_endpoint_id_cloudevent = '/subscriptions/5b4b650e-28b9-4790-b3ab-ddbd88d727c4/resourceGroups/DevExpRg/providers/Microsoft.Web/sites/eventgridclitestapp/functions/EventGridTrigger1'
        endpoint_url = 'https://devexpfuncappdestination.azurewebsites.net/runtime/webhooks/EventGrid?functionName=EventGridTrigger1&code=<HIDDEN>'
        endpoint_baseurl = 'https://devexpfuncappdestination.azurewebsites.net/runtime/webhooks/EventGrid'
        azure_active_directory_tenant_id = '00000000-0000-0000-0000-000000000000'
        azure_active_directory_application_id_or_uri = '00000000-0000-0000-0000-000000000000'

        self.kwargs.update({
            'event_subscription_name1': event_subscription_name1,
            'event_subscription_name2': event_subscription_name2,
            'event_subscription_name3': event_subscription_name3,
            'servicebustopic_endpoint_id': servicebustopic_endpoint_id,
            'azurefunction_endpoint_id_cloudevent': azurefunction_endpoint_id_cloudevent,
            'endpoint_url': endpoint_url,
            'endpoint_baseurl': endpoint_baseurl,
            'azure_active_directory_tenant_id': azure_active_directory_tenant_id,
            'azure_active_directory_application_id_or_uri': azure_active_directory_application_id_or_uri,
            'location': 'centraluseuap',
        })

        self.kwargs['source_resource_id'] = self.cmd('storage account create -g {rg} -n {sa} --sku Standard_LRS -l {location}').get_output_in_json()['id']
        self.cmd('az storage account update -g {rg} -n {sa} --set kind=StorageV2')

        # Create a servicebustopic destination based event subscription with CloudEvent 1.0 as the delivery schema
        self.cmd('az eventgrid event-subscription create --source-resource-id {source_resource_id} --name {event_subscription_name1} --endpoint-type SErvIcEBusTOPic --endpoint {servicebustopic_endpoint_id} --subject-begins-with SomeRandomText1 --event-delivery-schema CloudEVENTSchemaV1_0')

        # Create an AzureFunction destination based event subscription with additional batching parameters
        self.cmd('az eventgrid event-subscription create --source-resource-id {source_resource_id} --name {event_subscription_name2} --endpoint-type azUREFunction --endpoint {azurefunction_endpoint_id_cloudevent} --subject-begins-with SomeRandomText1 --max-events-per-batch 10 --preferred-batch-size-in-kilobytes 128')

        # Create an Webhook destination based event subscription with azure active directory settings
        self.cmd('az eventgrid event-subscription create --source-resource-id {source_resource_id} --name {event_subscription_name3} --endpoint-type webhook --endpoint \"{endpoint_url}\" --subject-begins-with SomeRandomText1 --max-events-per-batch 10 --preferred-batch-size-in-kilobytes 128 --azure-active-directory-tenant-id \"{azure_active_directory_tenant_id}\" --azure-active-directory-application-id-or-uri \"{azure_active_directory_application_id_or_uri}\"')

        self.cmd('az eventgrid event-subscription show  --source-resource-id {source_resource_id} --name {event_subscription_name1}', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription show  --source-resource-id {source_resource_id} --name {event_subscription_name2}', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
        ])

        self.cmd('az eventgrid event-subscription show  --source-resource-id {source_resource_id} --name {event_subscription_name3}', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
        ])
        self.cmd('az eventgrid event-subscription delete  --source-resource-id {source_resource_id} --name {event_subscription_name1}')
        self.cmd('az eventgrid event-subscription delete  --source-resource-id {source_resource_id} --name {event_subscription_name2}')
        self.cmd('az eventgrid event-subscription delete  --source-resource-id {source_resource_id} --name {event_subscription_name3}')
        self.cmd('az storage account delete -y -g {rg} -n {sa}')

    @ResourceGroupPreparer()
    def test_advanced_filters(self, resource_group):
        endpoint_url = 'https://devexpfuncappdestination.azurewebsites.net/runtime/webhooks/EventGrid?functionName=EventGridTrigger1&code=<HIDDEN>'
        endpoint_baseurl = 'https://devexpfuncappdestination.azurewebsites.net/runtime/webhooks/EventGrid'

        topic_name = self.create_random_name(prefix='cli', length=40)
        event_subscription_name = self.create_random_name(prefix='cli', length=40)

        self.kwargs.update({
            'topic_name': topic_name,
            'location': 'centraluseuap',
            'event_subscription_name': event_subscription_name,
            'endpoint_url': endpoint_url,
            'endpoint_baseurl': endpoint_baseurl
        })

        self.cmd('az eventgrid topic create --name {topic_name} --resource-group {rg} --location {location}', checks=[
            self.check('type', 'Microsoft.EventGrid/topics'),
            self.check('name', self.kwargs['topic_name']),
            self.check('provisioningState', 'Succeeded'),
        ])

        scope = self.cmd('az eventgrid topic show --name {topic_name} --resource-group {rg} -ojson').get_output_in_json()['id']

        self.kwargs.update({
            'scope': scope
        })

        # Error cases
        with self.assertRaises(CLIError):
            # No operator/values provided
            self.cmd('az eventgrid event-subscription create --source-resource-id {scope} --name {event_subscription_name} --endpoint {endpoint_url} --advanced-filter eventType')

        with self.assertRaises(CLIError):
            # No filter value provided
            self.cmd('az eventgrid event-subscription create --source-resource-id {scope}  --name {event_subscription_name} --endpoint {endpoint_url} --advanced-filter data.key2 NumberIn')

        with self.assertRaises(CLIError):
            # Invalid operator type provided
            self.cmd('az eventgrid event-subscription create --source-resource-id {scope} --name {event_subscription_name} --endpoint {endpoint_url} --advanced-filter data.key2 FooNumberLessThan 2 3')

        with self.assertRaises(CLIError):
            # Multiple values provided for a single value filter
            self.cmd('az eventgrid event-subscription create --source-resource-id {scope} --name {event_subscription_name} --endpoint {endpoint_url} --advanced-filter data.key2 NumberLessThan 2 3')

        # One advanced filter for NumberIn operator
        self.cmd('az eventgrid event-subscription create --source-resource-id {scope}  --name {event_subscription_name} --endpoint \"{endpoint_url}\" --advanced-filter data.key2 NumberIn 2 3 4 100 200', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl'])
        ])

        # Two advanced filters for NumberIn, StringIn operators
        self.cmd('az eventgrid event-subscription create --source-resource-id {scope} --name {event_subscription_name} --endpoint \"{endpoint_url}\" --advanced-filter data.key1 NumberIn 2 3 4 100 200 --advanced-filter data.key2 StringIn 2 3 4 100 200', checks=[
            self.check('type', 'Microsoft.EventGrid/eventSubscriptions'),
            self.check('provisioningState', 'Succeeded'),
            self.check('name', self.kwargs['event_subscription_name']),
            self.check('destination.endpointBaseUrl', self.kwargs['endpoint_baseurl'])
        ])

        self.cmd('az eventgrid event-subscription delete --source-resource-id {scope} --name {event_subscription_name}')
        self.cmd('az eventgrid topic delete --name {topic_name} --resource-group {rg}')
