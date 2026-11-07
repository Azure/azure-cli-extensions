# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Offline regressions for stable migration requests, polling, and access policies."""

import unittest
from unittest.mock import Mock

from azure.cli.core.aaz._command_ctx import AAZCommandCtx
from azure.cli.core.mock import DummyCli

from azext_redisenterprise.custom import ClusterUnlink, MigrationStart, MigrationUndo, MigrationUnlink
from azext_redisenterprise.aaz.latest.redisenterprise.migration import Show, Validate
from azext_redisenterprise.aaz.latest.redisenterprise.database.access_policy_assignment import (
    Create as AssignmentCreate,
)


class MigrationStartFlattenArgsTest(unittest.TestCase):

    def test_flat_args_registered_and_object_hidden(self):
        schema = MigrationStart._build_arguments_schema()

        # The four source properties are exposed as individual top-level arguments.
        for name in ("source_resource_id", "skip_data_migration", "switch_dns", "force_migrate"):
            arg = getattr(schema, name, None)
            self.assertIsNotNone(arg, "expected flat argument '{}' to be registered".format(name))
            self.assertTrue(arg._registered, "flat argument '{}' should be registered".format(name))

        # The three properties that are always applicable stay required at the CLI layer.
        for name in ("source_resource_id", "skip_data_migration", "switch_dns"):
            self.assertTrue(getattr(schema, name)._required,
                            "flat argument '{}' should be required".format(name))
        self.assertFalse(schema.force_migrate._required,
                         "force_migrate should be optional")

        # The original object wrapper is no longer surfaced on the command line.
        self.assertFalse(schema.azure_cache_for_redis._registered,
                         "--azure-cache-for-redis should be hidden after flattening")
        self.assertFalse(schema.azure_cache_for_redis._required,
                         "hidden --azure-cache-for-redis should not be required")

    def test_flat_options_have_expected_names(self):
        schema = MigrationStart._build_arguments_schema()
        expected = {
            "source_resource_id": "--source-resource-id",
            "skip_data_migration": "--skip-data-migration",
            "switch_dns": "--switch-dns",
            "force_migrate": "--force-migrate",
        }
        for name, option in expected.items():
            self.assertIn(option, getattr(schema, name)._options,
                          "argument '{}' should expose option '{}'".format(name, option))

    def _operation(self, command_type, operation_name, arguments):
        cli = DummyCli()
        command = command_type(cli_ctx=cli)
        command.ctx = AAZCommandCtx(
            cli_ctx=cli,
            schema=command.get_arguments_schema(),
            command_args={
                'subscription': '00000000-0000-0000-0000-000000000000',
                'resource_group': 'rg',
                'cluster_name': 'target',
                'no_wait': False,
                **arguments,
            },
        )
        command.ctx._clients['MgmtClient'] = Mock()
        command.ctx.format_args()
        command.pre_operations()
        return getattr(command, operation_name)(ctx=command.ctx)

    def test_flat_args_serialize_under_properties_including_false(self):
        source = ('/subscriptions/00000000-0000-0000-0000-000000000000/'
                  'resourceGroups/rg/providers/Microsoft.Cache/redis/source')
        for skip_data, switch_dns, force in ((True, True, True), (False, False, False)):
            with self.subTest(skip_data=skip_data, switch_dns=switch_dns, force=force):
                operation = self._operation(MigrationStart, 'MigrationsStart', {
                    'source_resource_id': source,
                    'skip_data_migration': skip_data,
                    'switch_dns': switch_dns,
                    'force_migrate': force,
                })
                self.assertEqual(operation.content, {
                    'properties': {
                        'sourceType': 'AzureCacheForRedis',
                        'sourceResourceId': source,
                        'skipDataMigration': skip_data,
                        'switchDns': switch_dns,
                        'forceMigrate': force,
                    },
                })

    def test_optional_force_is_omitted_from_migration_request(self):
        operation = self._operation(MigrationStart, 'MigrationsStart', {
            'source_resource_id': '/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Cache/redis/source',
            'skip_data_migration': True,
            'switch_dns': True,
        })
        self.assertNotIn('forceMigrate', operation.content['properties'])

    def test_validation_preserves_false_and_default_omission(self):
        source = '/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Cache/redis/source'
        operation = self._operation(Validate, 'MigrationsValidate', {
            'source_resource_id': source, 'skip_data_migration': False,
        })
        self.assertEqual(operation.content, {'sourceResourceId': source, 'skipDataMigration': False})
        operation = self._operation(Validate, 'MigrationsValidate', {'source_resource_id': source})
        self.assertEqual(operation.content, {'sourceResourceId': source})

    def test_undo_serializes_optional_rollback_reason(self):
        operation = self._operation(MigrationUndo, 'MigrationsUndo', {'rollback_reason': 'testing'})
        self.assertEqual(operation.content, {'rollbackReason': 'testing'})
        operation = self._operation(MigrationUndo, 'MigrationsUndo', {})
        self.assertNotIn('rollbackReason', operation.content or {})

    def test_stable_access_policy_request_preserves_policy_and_user(self):
        arguments = {
            'database_name': 'default',
            'access_policy_assignment_name': 'assignment',
            'object_id': '11111111-1111-1111-1111-111111111111',
        }
        operation = self._operation(AssignmentCreate, 'AccessPolicyAssignmentCreateUpdate', {
            **arguments, 'access_policy_name': 'default',
        })
        self.assertEqual(operation.content, {
            'properties': {
                'accessPolicyName': 'default',
                'user': {'objectId': arguments['object_id']},
            },
        })

    def test_bodyless_actions_deserialize_final_resource_and_preserve_no_wait(self):
        for command_type, operation_name in (
                (MigrationUndo, 'MigrationsUndo'),
                (MigrationUnlink, 'MigrationsUnlinkMigratedEndpoint'),
                (ClusterUnlink, 'ClustersUnlinkMigratedEndpoint')):
            for no_wait in (False, True):
                with self.subTest(command=command_type.__name__, no_wait=no_wait):
                    operation = self._operation(command_type, operation_name, {'no_wait': no_wait})
                    operation.make_request = Mock()
                    operation.client.send_request.return_value.http_response.status_code = 202
                    operation()
                    args, kwargs = operation.client.build_lro_polling.call_args
                    self.assertEqual(bool(args[0]), no_wait)
                    self.assertIsNone(args[2](Mock()))
                    self.assertEqual(kwargs['lro_options'], {'final-state-via': 'location'})

    def test_bodyless_actions_do_not_swallow_http_failures(self):
        for command_type, operation_name in (
                (MigrationUndo, 'MigrationsUndo'),
                (MigrationUnlink, 'MigrationsUnlinkMigratedEndpoint'),
                (ClusterUnlink, 'ClustersUnlinkMigratedEndpoint')):
            with self.subTest(command=command_type.__name__):
                operation = self._operation(command_type, operation_name, {})
                operation.make_request = Mock()
                response = operation.client.send_request.return_value.http_response
                response.status_code = 409
                operation.on_error = Mock(side_effect=RuntimeError('conflict'))
                with self.assertRaisesRegex(RuntimeError, 'conflict'):
                    operation()
                operation.on_error.assert_called_once_with(response)
                operation.client.build_lro_polling.assert_not_called()

    def test_migration_response_preserves_nullable_status_and_rollback_deadline(self):
        operation = self._operation(Show, 'MigrationsGet', {})
        operation.ctx.set_var('instance', {
            'properties': {
                'sourceType': 'AzureCacheForRedis',
                'statusDetails': None,
                'rollbackEligibleUntil': '2026-10-30T12:00:00Z',
                'provisioningState': 'Unlinked',
            },
        }, schema_builder=operation._build_schema_on_200)
        result = Show.deserialize_output(operation.ctx.vars.instance)
        self.assertIsNone(result['properties']['statusDetails'])
        self.assertEqual(result['properties']['rollbackEligibleUntil'], '2026-10-30T12:00:00Z')
        self.assertEqual(result['properties']['provisioningState'], 'Unlinked')


if __name__ == "__main__":
    unittest.main()
