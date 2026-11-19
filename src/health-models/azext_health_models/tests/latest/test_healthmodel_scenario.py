# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import shlex

from azure.core.exceptions import ResourceNotFoundError
from azure.cli.testsdk import *


class HealthModelScenarioTest(ScenarioTest):
    FILTER_HEADERS = ScenarioTest.FILTER_HEADERS + ['x-ms-operation-identifier']

    @ResourceGroupPreparer(name_prefix='cli_test_healthmodel_crud', location='centralus')
    def test_healthmodel_crud_cycle(self, resource_group):
        self.kwargs.update({
            'rg': resource_group,
            'model': self.create_random_name('clihm', 24),
            'location': 'centralus',
        })

        self.cmd('monitor health-models create -g {rg} -n {model} -l {location}', checks=[
            self.check('name', '{model}'),
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('location', '{location}')
        ])
        self.cmd('monitor health-models wait -g {rg} -n {model} --created --interval 5 --timeout 300')
        self.cmd('monitor health-models show -g {rg} -n {model}', checks=[
            self.check('name', '{model}')
        ])
        self.cmd('monitor health-models update -g {rg} -n {model} '
                 '--tags "{{scenario:examples,environment:demo}}"', checks=[
            self.check('tags.scenario', 'examples'),
            self.check('tags.environment', 'demo')
        ])
        self.cmd('monitor health-models list -g {rg}', checks=[
            self.check('length(@)', 1),
            self.check('[0].name', '{model}')
        ])

        self.cmd('monitor health-models entity show -g {rg} --health-model-name {model} -n {model}', checks=[
            self.check('name', '{model}')
        ])
        self.cmd('monitor health-models entity update -g {rg} --health-model-name {model} -n {model} '
                 '--canvas-position "{{x:0,y:0}}"', checks=[
            self.check('properties.canvasPosition.x', 0),
            self.check('properties.canvasPosition.y', 0)
        ])
        entities = [self.create_random_name('client', 24) for _ in range(3)]
        positions = set()
        for index, entity in enumerate(entities):
            x = 250 * index
            display_name = ['Web frontend', 'Background worker', 'Data storage'][index]
            self.kwargs.update({'entity': entity, 'display_name': display_name, 'x': x,
                                'relationship': self.create_random_name('clirel', 24),
                                'relationship_label': 'Checkout depends on frontend' if index == 0 else 'Root to child'})
            self.cmd('monitor health-models entity create -g {rg} --health-model-name {model} -n {entity} '
                     '--display-name "{display_name}" --canvas-position "{{x:{x},y:200}}"', checks=[
                self.check('name', '{entity}'),
                self.check('properties.displayName', display_name),
                self.check('properties.impact', 'Standard'),
                self.check('properties.canvasPosition.x', x),
                self.check('properties.canvasPosition.y', 200)
            ])
            self.cmd('monitor health-models relationship create -g {rg} --health-model-name {model} '
                     '-n {relationship} --parent-entity-name {model} --child-entity-name {entity} '
                     '--display-name "{relationship_label}"', checks=[
                self.check('properties.parentEntityName', '{model}'),
                self.check('properties.childEntityName', '{entity}'),
                self.check('properties.displayName', '{relationship_label}')
            ])
            if index == 0:
                self.cmd('monitor health-models entity wait -g {rg} --health-model-name {model} -n {entity} '
                         '--exists --interval 5 --timeout 300')
                self.cmd('monitor health-models relationship wait -g {rg} --health-model-name {model} '
                         '-n {relationship} --exists --interval 5 --timeout 300')
            self.cmd('monitor health-models relationship show -g {rg} --health-model-name {model} '
                     '-n {relationship}', checks=[
                self.check('properties.parentEntityName', '{model}'),
                self.check('properties.childEntityName', '{entity}')
            ])
            self.kwargs['relationship_label'] = 'Frontend dependency' if index == 0 else 'Connected top-level entity'
            self.cmd('monitor health-models relationship update -g {rg} --health-model-name {model} '
                     '-n {relationship} --display-name "{relationship_label}"', checks=[
                self.check('properties.displayName', '{relationship_label}')
            ])
            shown = self.cmd('monitor health-models entity show -g {rg} --health-model-name {model} '
                             '-n {entity}').get_output_in_json()
            position = shown['properties']['canvasPosition']
            positions.add((position['x'], position['y']))
        self.assertEqual(len(positions), len(entities))
        self.assertNotIn((0, 0), positions)
        self.kwargs.update({'parent': entities[0], 'api': self.create_random_name('cliapi', 24),
                            'api_relationship': self.create_random_name('clirel', 24)})
        self.cmd('monitor health-models entity update -g {rg} --health-model-name {model} -n {model} '
                 '--signal-groups "{{dependencies:{{aggregation-type:WorstOf}}}}"', checks=[
            self.check('properties.signalGroups.dependencies.aggregationType', 'WorstOf')
        ])
        self.cmd('monitor health-models entity create -g {rg} --health-model-name {model} -n {api} '
                 '--display-name "Frontend API" --canvas-position "{{x:0,y:400}}"')
        self.cmd('monitor health-models relationship create -g {rg} --health-model-name {model} '
                 '-n {api_relationship} --parent-entity-name {parent} --child-entity-name {api}', checks=[
            self.check('properties.parentEntityName', '{parent}'),
            self.check('properties.childEntityName', '{api}')
        ])
        self.cmd('monitor health-models entity update -g {rg} --health-model-name {model} -n {api} '
                 '--canvas-position "{{x:0,y:400}}"', checks=[
            self.check('properties.canvasPosition.x', 0),
            self.check('properties.canvasPosition.y', 400)
        ])
        self.cmd('monitor health-models entity show -g {rg} --health-model-name {model} -n {api}', checks=[
            self.check('properties.displayName', 'Frontend API'),
            self.check('properties.canvasPosition.x', 0),
            self.check('properties.canvasPosition.y', 400)
        ])
        self.cmd('monitor health-models relationship list -g {rg} --health-model-name {model}', checks=[
            self.check('length(@)', len(entities) + 1)
        ])
        self.kwargs['entity'] = entities[0]
        self.cmd('monitor health-models entity show -g {rg} --health-model-name {model} -n {entity}', checks=[
            self.check('name', '{entity}')
        ])
        self.cmd('monitor health-models entity list -g {rg} --health-model-name {model}', checks=[
            self.check('length(@)', len(entities) + 2)
        ])
        self.cmd('monitor health-models entity add-data-annotation -g {rg} --health-model-name {model} '
                 '--entity-name {entity} --description "Frontend deployment" '
                 '--annotation-details "{{environment:demo,deploymentId:release-001}}"', checks=[
            self.check('description', 'Frontend deployment'),
            self.check('annotationDetails.environment', 'demo'),
            self.check('annotationDetails.deploymentId', 'release-001')
        ])
        self.cmd('monitor health-models entity ingest-health-report -g {rg} --health-model-name {model} '
                 '--entity-name {entity} --signal-name availability --health-state Healthy '
                 '--value 100 --expires-in-minutes 60 --additional-context "Synthetic availability check"')
        for signal, value, state in [('primary', 100, 'Healthy'), ('backup', 80, 'Degraded'),
                                     ('canary', 100, 'Healthy')]:
            self.kwargs.update({'signal': signal, 'value': value, 'state': state})
            self.cmd('monitor health-models entity ingest-health-report -g {rg} --health-model-name {model} '
                     '--entity-name {entity} --signal-name {signal} --value {value} --health-state {state} '
                     '--expires-in-minutes 60')
        groups = [
            {'name': 'redundancy', 'aggregation-type': 'BestOf', 'members': ['primary', 'backup']},
            {'name': 'quorum', 'aggregation-type': 'MinHealthy', 'unit': 'Absolute',
             'unhealthy-threshold': 1, 'degraded-threshold': 2, 'members': ['primary', 'backup', 'canary'],
             'ignore-unknown': False},
            {'name': 'failure-budget', 'aggregation-type': 'MaxNotHealthy', 'unit': 'Percentage',
             'unhealthy-threshold': 60, 'degraded-threshold': 30, 'members': ['primary', 'backup', 'canary'],
             'ignore-unknown': False},
        ]
        for group in groups:
            self.kwargs['aggregation'] = shlex.quote(json.dumps([group]))
            if group['aggregation-type'] == 'MinHealthy':
                self.kwargs['aggregation'] = (
                    '"[{name:quorum,aggregation-type:MinHealthy,unit:Absolute,unhealthy-threshold:1,'
                    'degraded-threshold:2,members:[primary,backup,canary],ignore-unknown:false}]"'
                )
            self.cmd('monitor health-models entity update -g {rg} --health-model-name {model} -n {entity} '
                     '--signal-aggregation-groups {aggregation}', checks=[
                self.check('properties.signalAggregationGroups[0].name', group['name']),
                self.check('properties.signalAggregationGroups[0].aggregationType', group['aggregation-type']),
                self.check('properties.signalAggregationGroups[0].members', group['members'])
            ])
        self.cmd('monitor health-models entity show -g {rg} --health-model-name {model} -n {entity}', checks=[
            self.check('properties.signalAggregationGroups[0].unit', 'Percentage'),
            self.check('properties.signalAggregationGroups[0].ignoreUnknown', False)
        ])
        self.cmd('monitor health-models entity get-history -g {rg} --health-model-name {model} '
                 '--entity-name {entity} --top 10', checks=[
            self.check('entityName', '{entity}'),
            self.check('type(history)', 'array')
        ])
        self.cmd('monitor health-models entity get-signal-history -g {rg} --health-model-name {model} '
                 '--entity-name {entity} --signal-name availability --top 10', checks=[
            self.check('entityName', '{entity}')
        ])
        self.cmd('monitor health-models entity get-data-annotations -g {rg} --health-model-name {model} '
                 '--entity-name {entity}', checks=[
            self.check('annotations[0].description', 'Frontend deployment'),
            self.check('annotations[0].annotationDetails.environment', 'demo')
        ])
        relationships = self.cmd('monitor health-models relationship list -g {rg} '
                                 '--health-model-name {model}').get_output_in_json()
        for relationship in relationships:
            self.kwargs['relationship'] = relationship['name']
            self.cmd('monitor health-models relationship delete -g {rg} --health-model-name {model} '
                     '-n {relationship} --yes')
        for entity in entities + [self.kwargs['api']]:
            self.kwargs['entity'] = entity
            self.cmd('monitor health-models entity delete -g {rg} --health-model-name {model} -n {entity} --yes')

        self.cmd('monitor health-models delete -g {rg} -n {model} --yes')
        with self.assertRaisesRegex(ResourceNotFoundError, 'ResourceNotFound'):
            self.cmd('monitor health-models show -g {rg} -n {model}')

    @ResourceGroupPreparer(name_prefix='cli_test_healthmodel_signals', location='uksouth')
    @StorageAccountPreparer(name_prefix='clihm', location='uksouth', kind='StorageV2', sku='Standard_LRS')
    def test_healthmodel_signal_auth_discovery(self, resource_group, storage_account):
        self.kwargs.update({
            'rg': resource_group,
            'storage': storage_account,
            'model': self.create_random_name('clihm', 24),
            'identity': self.create_random_name('climi', 24),
            'entity': self.create_random_name('client', 24),
            'auth': self.create_random_name('cliauth', 24),
            'rule': self.create_random_name('clirule', 24),
        })
        identity = self.cmd('identity create -g {rg} -n {identity} -l uksouth').get_output_in_json()
        self.kwargs['identity_id'] = identity['id']
        model = self.cmd('monitor health-models create -g {rg} -n {model} -l uksouth --mi-system-assigned '
                         '--mi-user-assigned "[{identity_id}]" --tags "{{scenario:examples}}"', checks=[
            self.check('name', '{model}'),
            self.check('properties.provisioningState', 'Succeeded')
        ]).get_output_in_json()
        resource_group_info = self.cmd('group show -g {rg}').get_output_in_json()
        self.kwargs.update({'principal': model['identity']['principalId'], 'scope': resource_group_info['id'],
                            'assignment': self.create_guid()})
        self.cmd('role assignment create --assignee-object-id {principal} --assignee-principal-type ServicePrincipal '
                 '--role Reader --scope {scope} --name {assignment}', checks=[
            self.check('principalId', '{principal}'),
            self.check('scope', '{scope}')
        ])
        identities = self.cmd('monitor health-models identity show -g {rg} -n {model}').get_output_in_json()
        self.assertIn('SystemAssigned', identities['type'])
        self.kwargs['identity_id'] = next(
            resource_id for resource_id in identities['userAssignedIdentities']
            if resource_id.casefold() == identity['id'].casefold()
        )
        self.cmd('monitor health-models identity assign -g {rg} -n {model} '
                 '--system-assigned --user-assigned {identity_id}')
        self.cmd('monitor health-models identity wait -g {rg} -n {model} --exists --interval 5 --timeout 300')
        self.cmd('monitor health-models authentication-setting create -g {rg} --health-model-name {model} '
                 '-n {auth} --display-name "Model identity" '
                 '--managed-identity "{{managed-identity-name:SystemAssigned}}"', checks=[
            self.check('properties.authenticationKind', 'ManagedIdentity'),
            self.check('properties.managedIdentityName', 'SystemAssigned')
        ])
        self.cmd('monitor health-models authentication-setting wait -g {rg} --health-model-name {model} '
                 '-n {auth} --exists --interval 5 --timeout 300')
        self.cmd('monitor health-models authentication-setting show -g {rg} --health-model-name {model} '
                 '-n {auth}', checks=[
            self.check('properties.displayName', 'Model identity')
        ])
        self.cmd('monitor health-models authentication-setting update -g {rg} --health-model-name {model} '
                 '-n {auth} --display-name "Telemetry identity"', checks=[
            self.check('properties.displayName', 'Telemetry identity')
        ])
        self.cmd('monitor health-models authentication-setting list -g {rg} --health-model-name {model}', checks=[
            self.check('length(@)', 1)
        ])
        definitions = [
            ('storage-availability', 'AzureResourceMetric', '--azure-resource-metric',
             {'metric-namespace': 'Microsoft.Storage/storageAccounts', 'metric-name': 'Availability',
              'aggregation-type': 'Average', 'time-grain': 'PT1H'}, 'Percent',
             {'degraded-rule': {'operator': 'LessThan', 'threshold': 99.9},
              'unhealthy-rule': {'operator': 'LessThan', 'threshold': 99}}),
            ('request-failures', 'LogAnalyticsQuery', '--log-analytics-query',
             {'query-text': 'AppRequests | summarize failures=countif(Success == false)',
              'value-column-name': 'failures', 'time-grain': 'PT5M'}, 'Count',
             {'degraded-rule': {'operator': 'GreaterThan', 'threshold': 1},
              'unhealthy-rule': {'operator': 'GreaterThan', 'threshold': 5}}),
            ('scrape-availability', 'PrometheusMetricsQuery', '--prometheus-metrics-query',
             {'query-text': 'up', 'time-grain': 'PT1M'}, 'Count',
             {'unhealthy-rule': {'operator': 'LessThan', 'threshold': 1}}),
        ]
        for definition, signal_kind, option, configuration, unit, rules in definitions:
            self.kwargs.update({
                'definition': definition,
                'option': option,
                'configuration': shlex.quote(json.dumps(configuration)),
                'unit': unit,
                'rules': shlex.quote(json.dumps(rules)),
                'signal_display_name': 'Reusable signal',
            })
            if signal_kind == 'AzureResourceMetric':
                self.kwargs.update({
                    'signal_display_name': 'Storage availability',
                    'configuration': (
                        '"{metric-namespace:Microsoft.Storage/storageAccounts,metric-name:Availability,'
                        'aggregation-type:Average,time-grain:PT1H}"'
                    ),
                    'rules': (
                        '"{degraded-rule:{operator:LessThan,threshold:99.9},'
                        'unhealthy-rule:{operator:LessThan,threshold:99}}"'
                    ),
                })
            self.cmd('monitor health-models signal-definition create -g {rg} --health-model-name {model} '
                     '-n {definition} {option} {configuration} --display-name "{signal_display_name}" '
                     '--refresh-interval PT1M --data-unit {unit} --evaluation-rules {rules}', checks=[
                self.check('properties.signalKind', signal_kind),
                self.check('properties.displayName', '{signal_display_name}'),
                self.check('properties.dataUnit', unit),
                self.check('properties.evaluationRules.unhealthyRule.threshold', rules['unhealthy-rule']['threshold'])
            ])
            if signal_kind == 'AzureResourceMetric':
                self.cmd('monitor health-models signal-definition wait -g {rg} --health-model-name {model} '
                         '-n {definition} --exists --interval 5 --timeout 300')
            self.cmd('monitor health-models signal-definition show -g {rg} --health-model-name {model} '
                     '-n {definition}', checks=[
                self.check('properties.signalKind', signal_kind)
            ])
            self.cmd('monitor health-models signal-definition update -g {rg} --health-model-name {model} '
                     '-n {definition} --display-name "Updated reusable signal" --refresh-interval PT5M', checks=[
                self.check('properties.displayName', 'Updated reusable signal'),
                self.check('properties.refreshInterval', 'PT5M')
            ])
        self.kwargs.update({
            'definition': 'storage-availability',
            'rules': ('"{degraded-rule:{operator:LessThan,threshold:99.8},'
                      'unhealthy-rule:{operator:LessThan,threshold:98}}"'),
        })
        self.cmd('monitor health-models signal-definition update -g {rg} --health-model-name {model} '
                 '-n {definition} --evaluation-rules {rules}', checks=[
            self.check('properties.evaluationRules.degradedRule.threshold', 99.8),
            self.check('properties.evaluationRules.unhealthyRule.threshold', 98)
        ])
        self.cmd('monitor health-models signal-definition list -g {rg} --health-model-name {model}', checks=[
            self.check('length(@)', len(definitions))
        ])
        storage = self.cmd('storage account show -g {rg} -n {storage}').get_output_in_json()
        self.kwargs['signal_groups'] = shlex.quote(json.dumps({
            'azure-resource': {
                'authentication-setting': self.kwargs['auth'],
                'azure-resource-id': storage['id'],
                'signals': [{'name': 'availability', 'signal-definition-name': 'storage-availability'}],
            }
        }))
        self.cmd('monitor health-models entity create -g {rg} --health-model-name {model} -n {entity} '
                 '--display-name "Storage account" --canvas-position "{{x:0,y:200}}"', checks=[
            self.check('properties.displayName', 'Storage account'),
        ])
        self.cmd('monitor health-models entity update -g {rg} --health-model-name {model} -n {entity} '
                 '--signal-groups {signal_groups}', checks=[
            self.check('properties.signalGroups.azureResource.azureResourceId', storage['id']),
            self.check('properties.signalGroups.azureResource.signals[0].signalDefinitionName', 'storage-availability')
        ])
        self.kwargs['relationship'] = self.create_random_name('clirel', 24)
        self.cmd('monitor health-models relationship create -g {rg} --health-model-name {model} '
                 '-n {relationship} --parent-entity-name {model} --child-entity-name {entity}', checks=[
            self.check('properties.parentEntityName', '{model}'),
            self.check('properties.childEntityName', '{entity}')
        ])
        recommendations = self.cmd('monitor health-models entity get-signal-recommendations -g {rg} '
                                   '--health-model-name {model} --entity-name {entity}').get_output_in_json()
        for stream in ('recommendedSignals', 'recommendedConfigurations'):
            self.assertIsInstance(recommendations[stream], list)
            for recommendation in recommendations[stream]:
                self.assertIn(recommendation['configuration']['signalKind'],
                              ('AzureResourceMetric', 'LogAnalyticsQuery', 'PrometheusMetricsQuery'))
                self.assertTrue(recommendation['signalId'])
        self.kwargs['subscription_id'] = self.get_subscription_id()
        self.cmd('monitor health-models discovery-rule create -g {rg} --health-model-name {model} -n {rule} '
                 '--display-name "Storage discovery" --authentication-setting {auth} '
                 "--specification \"{{resource-graph-query:{{resource-graph-query:'resources | "
                 "where subscriptionId == '/{subscription_id}'/ | where resourceGroup == '/{rg}'/ | "
                 "where type =~ '/microsoft.storage/storageaccounts'/'}}}}\" --discover-relationships Disabled "
                 '--add-recommended-signals Disabled --add-resource-health-signal Disabled', checks=[
            self.check('properties.specification.kind', 'ResourceGraphQuery'),
            self.check('properties.displayName', 'Storage discovery'),
            self.check('properties.specification.resourceGraphQuery',
                       "resources | where subscriptionId == '{subscription_id}' | where resourceGroup == '{rg}' | "
                       "where type =~ 'microsoft.storage/storageaccounts'")
        ])
        self.cmd('monitor health-models discovery-rule wait -g {rg} --health-model-name {model} '
                 '-n {rule} --exists --interval 5 --timeout 300')
        self.cmd('monitor health-models discovery-rule show -g {rg} --health-model-name {model} -n {rule}', checks=[
            self.check('properties.authenticationSetting', '{auth}')
        ])
        self.cmd('monitor health-models discovery-rule update -g {rg} --health-model-name {model} -n {rule} '
                 '--display-name "Scoped storage discovery"', checks=[
            self.check('properties.displayName', 'Scoped storage discovery')
        ])
        self.cmd('monitor health-models discovery-rule list -g {rg} --health-model-name {model}', checks=[
            self.check('length(@)', 1)
        ])
        rule = self.cmd('monitor health-models discovery-rule show -g {rg} --health-model-name {model} '
                        '-n {rule}').get_output_in_json()
        self.assertTrue(rule['properties']['entityName'])
        self.kwargs.update({'rule_entity': rule['properties']['entityName'],
                            'rule_relationship': self.create_random_name('clirel', 24)})
        self.cmd('monitor health-models entity wait -g {rg} --health-model-name {model} '
                 '-n {rule_entity} --exists --interval 5 --timeout 300')
        self.cmd('monitor health-models relationship create -g {rg} --health-model-name {model} '
                 '-n {rule_relationship} --parent-entity-name {model} --child-entity-name {rule_entity}', checks=[
            self.check('properties.parentEntityName', '{model}'),
            self.check('properties.childEntityName', '{rule_entity}')
        ])
        self.cmd('monitor health-models relationship show -g {rg} --health-model-name {model} '
                 '-n {rule_relationship}', checks=[
            self.check('properties.parentEntityName', '{model}'),
            self.check('properties.childEntityName', '{rule_entity}')
        ])
        self.cmd('monitor health-models relationship delete -g {rg} --health-model-name {model} '
                 '-n {rule_relationship} --yes')
        self.cmd('monitor health-models discovery-rule delete -g {rg} --health-model-name {model} -n {rule} --yes')
        self.cmd('monitor health-models relationship delete -g {rg} --health-model-name {model} '
                 '-n {relationship} --yes')
        self.cmd('monitor health-models entity delete -g {rg} --health-model-name {model} -n {entity} --yes')
        for definition, _, _, _, _, _ in definitions:
            self.kwargs['definition'] = definition
            self.cmd('monitor health-models signal-definition delete -g {rg} --health-model-name {model} '
                     '-n {definition} --yes')
        self.cmd('monitor health-models authentication-setting delete -g {rg} --health-model-name {model} '
                 '-n {auth} --yes')
        self.cmd('monitor health-models identity remove -g {rg} -n {model} --user-assigned {identity_id}')
        identities = self.cmd('monitor health-models identity show -g {rg} -n {model}').get_output_in_json()
        self.assertNotIn(self.kwargs['identity_id'], identities.get('userAssignedIdentities', {}))
        self.cmd('monitor health-models delete -g {rg} -n {model} --yes')

    def test_healthmodel_list_recorded(self):
        self.cmd('monitor health-models list', checks=[self.check('type(@)', 'array')])
