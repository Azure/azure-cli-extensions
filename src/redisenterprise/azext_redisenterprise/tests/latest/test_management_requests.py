# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Offline regressions for migration requests, polling, ACLs, and firewall rules."""

import unittest
from unittest.mock import Mock, patch

from azure.cli.core.aaz import AAZUndefined
from azure.cli.core.aaz._command_ctx import AAZCommandCtx
from azure.cli.core.azclierror import MutuallyExclusiveArgumentError
from azure.cli.core.mock import DummyCli

from azext_redisenterprise.custom import (
    ClusterUnlink, MigrationStart, MigrationUndo, MigrationUnlink,
    RedisEnterpriseUpdate, redisenterprise_create,
)
from azext_redisenterprise.aaz.latest.redisenterprise import Create as ClusterCreate
from azext_redisenterprise.aaz.latest.redisenterprise.migration import Show, Validate
from azext_redisenterprise.aaz.latest.redisenterprise.database.access_policy_assignment import (
    Create as AssignmentCreate,
    Show as AssignmentShow,
    Update as AssignmentUpdate,
)


class ManagementRequestsTest(unittest.TestCase):

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

    def test_custom_acl_create_does_not_require_deprecated_policy(self):
        operation = self._operation(AssignmentCreate, 'AccessPolicyAssignmentCreateUpdate', {
            'database_name': 'default',
            'access_policy_assignment_name': 'reader',
            'object_id': '11111111-1111-1111-1111-111111111111',
            'access_string': '+@read ~cache:*',
        })
        self.assertEqual(operation.content['properties'], {
            'accessString': '+@read ~cache:*',
            'user': {'objectId': '11111111-1111-1111-1111-111111111111'},
        })

    def test_acl_update_preserves_user_and_does_not_send_provisioning_error(self):
        operation = self._operation(AssignmentUpdate, 'AccessPolicyAssignmentCreateUpdate', {
            'database_name': 'default',
            'access_policy_assignment_name': 'reader',
            'access_string': '+get ~cache:*',
        })
        operation.ctx.set_var('instance', {
            'properties': {
                'accessPolicyName': 'default',
                'accessString': '+@read ~cache:*',
                'user': {'objectId': '11111111-1111-1111-1111-111111111111'},
                'provisioningError': {'code': 'InvalidACL', 'message': 'Invalid access string'},
            },
        }, schema_builder=AssignmentUpdate.AccessPolicyAssignmentGet._build_schema_on_200)
        AssignmentUpdate.InstanceUpdateByJson(ctx=operation.ctx)()
        self.assertEqual(operation.content['properties'], {
            'accessPolicyName': 'default',
            'accessString': '+get ~cache:*',
            'user': {'objectId': '11111111-1111-1111-1111-111111111111'},
        })
        result = AssignmentShow.deserialize_output(operation.ctx.vars.instance, client_flatten=False)
        self.assertEqual(result['properties']['provisioningError']['code'], 'InvalidACL')

    def test_cluster_create_serializes_firewall_rules_and_empty_set(self):
        rules = [
            {'name': 'office', 'source-address-prefix': '203.0.113.0/24'},
            {'name': 'azure', 'source-address-prefix': 'AzureCloud'},
        ]
        for supplied in (None, [], rules):
            with self.subTest(rules=supplied):
                operation = self._operation(ClusterCreate, 'RedisEnterpriseCreate', {
                    'location': 'eastus2euap', 'sku': 'Balanced_B1',
                    'public_network_access': 'Enabled', 'firewall_rules': supplied,
                })
                properties = operation.content['properties']
                if supplied is None:
                    self.assertNotIn('firewallRules', properties)
                else:
                    self.assertEqual(properties['firewallRules'], [
                        {'name': rule['name'], 'sourceAddressPrefix': rule['source-address-prefix']}
                        for rule in supplied
                    ])

    def test_custom_create_forwards_firewall_rules_with_and_without_database(self):
        rules = [{'name': 'office', 'source-address-prefix': '203.0.113.1'}]
        for no_database in (False, True):
            with self.subTest(no_database=no_database):
                with patch.object(ClusterCreate, '__call__', return_value=None) as create:
                    with patch('azext_redisenterprise.aaz.latest.redisenterprise.database.Create.__call__'):
                        redisenterprise_create(
                            Mock(cli_ctx=DummyCli()), 'rg', 'cache', 'eastus2euap', 'Balanced_B1',
                            public_network_access='Enabled', firewall_rules=rules, no_database=no_database,
                        )
                        self.assertEqual(create.call_args.kwargs['command_args']['firewall_rules'], rules)

    def test_firewall_update_patches_only_changed_fields_and_clears_empty_array(self):
        initial = {
            'location': 'eastus2euap',
            'sku': {'name': 'Balanced_B1'},
            'identity': {
                'type': 'SystemAssigned, UserAssigned',
                'principalId': '11111111-1111-1111-1111-111111111111',
                'tenantId': '22222222-2222-2222-2222-222222222222',
                'userAssignedIdentities': {
                    '/subscriptions/sub/resourceGroups/rg/providers/'
                    'Microsoft.ManagedIdentity/userAssignedIdentities/cache': {
                        'clientId': '33333333-3333-3333-3333-333333333333',
                        'principalId': '44444444-4444-4444-4444-444444444444',
                    },
                },
            },
            'properties': {
                'publicNetworkAccess': 'Enabled',
                'firewallRules': [{'name': 'old', 'sourceAddressPrefix': '203.0.113.1'}],
                'encryption': {'customerManagedKeyEncryption': {
                    'keyEncryptionKeyUrl': 'https://example.vault.azure.net/keys/key/version',
                }},
            },
        }
        for rules in (AAZUndefined, None, [], [{'name': 'new', 'source-address-prefix': '198.51.100.0/24'}]):
            with self.subTest(rules=rules):
                operation = self._operation(RedisEnterpriseUpdate, 'RedisEnterpriseCreate', {
                    'firewall_rules': rules,
                } if rules is not AAZUndefined else {})
                operation.ctx.set_var('instance', initial,
                                      schema_builder=RedisEnterpriseUpdate.RedisEnterpriseGet._build_schema_on_200)
                command = RedisEnterpriseUpdate(cli_ctx=operation.ctx.cli_ctx)
                command.ctx = operation.ctx
                command.pre_instance_update(operation.ctx.vars.instance)
                command.InstanceUpdateByJson(ctx=operation.ctx)()
                command.post_instance_update(operation.ctx.vars.instance)
                if rules is AAZUndefined:
                    self.assertEqual(operation.method, 'PUT')
                    self.assertEqual(operation.content['properties']['firewallRules'],
                                     initial['properties']['firewallRules'])
                else:
                    self.assertEqual(operation.method, 'PATCH')
                    self.assertEqual(operation.content, {'properties': {'firewallRules': [
                        {'name': rule['name'], 'sourceAddressPrefix': rule['source-address-prefix']}
                        for rule in rules
                    ] if rules is not None else None}})

    def test_firewall_update_rejects_generic_removals(self):
        for rules in (AAZUndefined, None, [], [{'name': 'office', 'source-address-prefix': '203.0.113.1'}]):
            with self.subTest(rules=rules):
                arguments = {'generic_update_args': {'actions': [('remove', ['tags'])]}}
                if rules is AAZUndefined:
                    operation = self._operation(RedisEnterpriseUpdate, 'RedisEnterpriseCreate', arguments)
                    self.assertEqual(operation.method, 'PUT')
                else:
                    arguments['firewall_rules'] = rules
                    with self.assertRaisesRegex(MutuallyExclusiveArgumentError,
                                                '--firewall-rules cannot be combined with --remove'):
                        self._operation(RedisEnterpriseUpdate, 'RedisEnterpriseCreate', arguments)

    def test_disabling_public_access_patches_only_supplied_properties(self):
        operation = self._operation(RedisEnterpriseUpdate, 'RedisEnterpriseCreate', {
            'public_network_access': 'Disabled',
            'firewall_rules': [],
        })
        operation.ctx.set_var('instance', {
            'location': 'eastus2euap',
            'sku': {'name': 'Balanced_B1'},
            'properties': {
                'publicNetworkAccess': 'Enabled',
                'firewallRules': [{'name': 'office', 'sourceAddressPrefix': '203.0.113.1'}],
            },
        }, schema_builder=RedisEnterpriseUpdate.RedisEnterpriseGet._build_schema_on_200)
        command = RedisEnterpriseUpdate(cli_ctx=operation.ctx.cli_ctx)
        command.ctx = operation.ctx
        command.pre_instance_update(operation.ctx.vars.instance)
        command.InstanceUpdateByJson(ctx=operation.ctx)()
        command.post_instance_update(operation.ctx.vars.instance)
        self.assertEqual(operation.method, 'PATCH')
        self.assertEqual(operation.content, {
            'properties': {'publicNetworkAccess': 'Disabled', 'firewallRules': []},
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
