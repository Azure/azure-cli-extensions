# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest import mock

from azext_cosmosdb_preview.custom import cli_cosmosdb_sql_container_update
from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb import models
from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb._utils.serialization import Serializer
from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.models import (
    ComputedProperty,
    ContainerPartitionKey,
    IncludedPath,
    IndexingPolicy,
    SqlContainerGetPropertiesResource,
    SqlContainerGetResults,
)


class CosmosdbSqlContainerUpdateTest(unittest.TestCase):
    def setUp(self):
        self.computed_properties = [
            ComputedProperty(name='normalizedName', query='SELECT VALUE UPPER(c.name) FROM c'),
            ComputedProperty(name='nameLength', query='SELECT VALUE LENGTH(c.name) FROM c'),
        ]
        self.resource = SqlContainerGetPropertiesResource(
            id='container',
            partition_key=ContainerPartitionKey(paths=['/pk'], kind='Hash'),
            indexing_policy=IndexingPolicy(
                indexing_mode='consistent', included_paths=[IncludedPath(path='/*')]),
            default_ttl=-1,
            computed_properties=self.computed_properties,
        )
        self.client = mock.Mock()
        self.client.get_sql_container.return_value = SqlContainerGetResults(resource=self.resource)

    def _update(self, **kwargs):
        result = cli_cosmosdb_sql_container_update(
            self.client, 'resource-group', 'account', 'database', 'container', **kwargs)

        self.client.get_sql_container.assert_called_once_with(
            'resource-group', 'account', 'database', 'container')
        update = self.client.begin_create_update_sql_container
        update.assert_called_once()
        parameters = update.call_args.args[-1]
        update.assert_called_once_with(
            'resource-group', 'account', 'database', 'container', parameters)
        self.assertIs(result, update.return_value)
        serializer = Serializer({name: model for name, model in vars(models).items() if isinstance(model, type)})
        payload = serializer.body(parameters, 'SqlContainerCreateUpdateParameters')['properties']['resource']
        self.assertEqual(payload['id'], self.resource.id)
        self.assertEqual(payload['partitionKey'], self.resource.partition_key.serialize())
        return payload

    def test_indexing_update_preserves_computed_properties(self):
        indexing_policy = {
            'indexingMode': 'consistent',
            'includedPaths': [{'path': '/normalizedName/?'}, {'path': '/nameLength/?'}],
        }

        payload = self._update(indexing_policy=indexing_policy)

        self.assertEqual(payload['indexingPolicy'], indexing_policy)
        self.assertEqual(
            payload['computedProperties'], [prop.serialize() for prop in self.computed_properties])
        self.assertEqual(payload['defaultTtl'], -1)
        self.assertEqual(self.resource.indexing_policy.included_paths[0].path, '/*')

    def test_non_indexing_updates_preserve_computed_properties(self):
        for argument, field in [('default_ttl', 'defaultTtl'), ('analytical_storage_ttl', 'analyticalStorageTtl')]:
            with self.subTest(argument=argument):
                self.client.reset_mock()

                payload = self._update(**{argument: 3600})

                self.assertEqual(payload[field], 3600)
                self.assertEqual(payload['indexingPolicy'], self.resource.indexing_policy.serialize())
                self.assertEqual(
                    payload['computedProperties'], [prop.serialize() for prop in self.computed_properties])

    def test_update_without_computed_properties(self):
        for computed_properties in [None, []]:
            with self.subTest(computed_properties=computed_properties):
                self.client.reset_mock()
                self.resource.computed_properties = computed_properties

                payload = self._update(default_ttl=3600)

                self.assertEqual(payload['defaultTtl'], 3600)
                self.assertEqual(payload['indexingPolicy'], self.resource.indexing_policy.serialize())
                if computed_properties is None:
                    self.assertNotIn('computedProperties', payload)
                else:
                    self.assertEqual(payload['computedProperties'], [])
