# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import ast
import importlib
import inspect
import pathlib
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from azure.cli.core.aaz import AAZCommand, AAZHttpOperation
from azure.cli.core.aaz._field_value import AAZObject

from azext_health_models.aaz.latest.monitor.health_models.entity._create import Create as EntityCreate
from azext_health_models.aaz.latest.monitor.health_models.entity._get_signal_recommendations import (
    GetSignalRecommendations,
)
from azext_health_models.aaz.latest.monitor.health_models._list import List


class HealthModelGATest(unittest.TestCase):
    def test_all_operation_api_versions(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        count = 0
        for path in sorted((root / 'aaz').rglob('*.py')):
            module_name = 'azext_health_models.' + '.'.join(path.relative_to(root).with_suffix('').parts)
            module = importlib.import_module(module_name)
            for _, command in inspect.getmembers(module, inspect.isclass):
                if command.__module__ != module_name or not issubclass(command, AAZCommand):
                    continue
                for _, operation in inspect.getmembers(command, inspect.isclass):
                    if not issubclass(operation, AAZHttpOperation):
                        continue
                    with self.subTest(command=command.__name__, operation=operation.__name__):
                        context = SimpleNamespace(get_http_client=Mock(), args=Mock())
                        self.assertEqual(operation(context).query_parameters['api-version'], '2026-11-01')
                    count += 1
        self.assertGreater(count, 46)

    def test_no_preview_decorators(self):
        root = pathlib.Path(__file__).resolve().parents[2] / 'aaz'
        for path in sorted(root.rglob('*.py')):
            with self.subTest(path=path.relative_to(root)):
                tree = ast.parse(path.read_text(encoding='utf-8'))
                for node in ast.walk(tree):
                    if isinstance(node, ast.keyword) and node.arg == 'is_preview':
                        self.assertFalse(ast.literal_eval(node.value))

    def test_recommendation_configuration_round_trip(self):
        configurations = [
            {
                'signalKind': 'AzureResourceMetric', 'metricNamespace': 'Microsoft.Compute/virtualMachines',
                'metricName': 'Percentage CPU', 'aggregationType': 'Average', 'timeGrain': 'PT5M',
                'dimensionFilter': 'instance eq frontend',
            },
            {
                'signalKind': 'LogAnalyticsQuery', 'queryText': 'Heartbeat | count', 'timeGrain': 'PT5M',
                'valueColumnName': 'Count', 'requiredTables': ['Heartbeat'],
                'requiredDiagnosticSettingCategories': ['AuditEvent'],
            },
            {
                'signalKind': 'PrometheusMetricsQuery', 'queryText': 'sum(up)', 'timeGrain': 'PT5M',
                'requiredMetrics': ['up'], 'requiredScrapeTargets': ['frontend'],
            },
        ]
        schema = GetSignalRecommendations.EntitiesGetSignalRecommendations._build_schema_on_200()
        for configuration in configurations:
            for stream in ('recommendedSignals', 'recommendedConfigurations'):
                with self.subTest(kind=configuration['signalKind'], stream=stream):
                    payload = {'recommendedSignals': [], 'recommendedConfigurations': []}
                    payload[stream] = [{
                        'signalId': 'availability',
                        'configuration': configuration,
                        'evaluationRules': {
                            'unhealthyRule': {'operator': 'LowerThan', 'threshold': 1.0},
                        },
                    }]
                    value = AAZObject(schema, schema.process_data(payload))
                    self.assertEqual(AAZCommand.deserialize_output(value), payload)

    def test_entity_aggregation_groups_round_trip(self):
        payload = {
            'name': 'frontend',
            'properties': {
                'displayName': 'Frontend',
                'signalAggregationGroups': [{
                    'name': 'availability', 'aggregationType': 'MinHealthy', 'unhealthyThreshold': 2,
                    'unit': 'Absolute',
                    'members': ['replica1', 'replica2', 'replica3'], 'ignoreUnknown': True,
                }],
            },
        }
        schema = EntityCreate.EntitiesCreateOrUpdate._build_schema_on_200_201()
        value = AAZObject(schema, schema.process_data(payload))
        self.assertEqual(AAZCommand.deserialize_output(value), payload)

    def test_removed_look_back_window(self):
        root = pathlib.Path(__file__).resolve().parents[2] / 'aaz'
        for path in sorted(root.rglob('*.py')):
            with self.subTest(path=path.relative_to(root)):
                text = path.read_text(encoding='utf-8')
                self.assertNotIn('lookBackWindow', text)
                self.assertNotIn('look_back_window', text)

    def test_list_output_shapes(self):
        operations = (List.HealthModelsListBySubscription, List.HealthModelsListByResourceGroup)
        for operation in operations:
            schema = operation._build_schema_on_200()
            for value in ([], [{'name': 'frontend', 'location': 'centralus'}]):
                for next_link in (None, 'https://management.azure.com/next?api-version=2026-11-01'):
                    with self.subTest(operation=operation.__name__, value=value, next_link=next_link):
                        payload = {'value': value}
                        if next_link is not None:
                            payload['nextLink'] = next_link
                        result = AAZObject(schema, schema.process_data(payload))
                        self.assertEqual(AAZCommand.deserialize_output(result), payload)
