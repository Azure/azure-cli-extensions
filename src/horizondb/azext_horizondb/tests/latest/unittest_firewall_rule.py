# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from unittest import TestCase
from unittest.mock import patch

from azure.cli.core import get_default_cli
from azure.cli.core.aaz import AAZCommand
from azure.cli.core.azclierror import InvalidArgumentValueError
from azext_horizondb import HorizonDBCommandsLoader
from azext_horizondb.aaz.latest.horizondb.cluster.pool.firewall_rule import Create, Delete, Show, Update, Wait


class FirewallRuleTests(TestCase):

    def setUp(self):
        http_client = patch(
            'azure.cli.core.aaz._command_ctx.AAZCommandCtx.get_http_client',
            side_effect=AssertionError('Unit tests must not use Azure credentials or HTTP clients.')
        )
        http_client.start()
        self.addCleanup(http_client.stop)
        self.loader = HorizonDBCommandsLoader(cli_ctx=get_default_cli())
        self.args = {
            'subscription': '00000000-0000-0000-0000-000000000001',
            'resource_group': 'test-rg',
            'cluster_name': 'test-cluster',
            'pool_name': 'test-pool',
        }

    def _name_args(self, command_type, name):
        args = dict(self.args, firewall_rule_name=name)
        if command_type is Create:
            args.update(start_ip_address='203.0.113.10', end_ip_address='203.0.113.10')
        return args

    def test_accepts_valid_firewall_rule_names(self):
        for command_type in [Create, Update, Show, Delete, Wait]:
            schema = command_type.get_arguments_schema()
            # AAZ stores regex constraints as metadata; format_args enforces lengths only.
            pattern = schema.firewall_rule_name._fmt._pattern  # pylint: disable=protected-access
            for name in ['a', 'Allow_Office.1-rule_', 'a' * 80]:
                with self.subTest(command=command_type.__name__, name=name):
                    command = command_type(loader=self.loader)
                    args = self._name_args(command_type, name)
                    AAZCommand._handler(command, args)  # pylint: disable=protected-access
                    self.assertRegex(name, pattern)
                    self.assertEqual(command.ctx.args.firewall_rule_name.to_serialized_data(), name)

    def test_create_validates_ipv4_range_before_request(self):
        name = 'horizondb cluster pool firewall-rule create'
        command = self.loader.load_command_table(name.split())[name]
        for start, end, error in [
                ('2001:db8::1', '203.0.113.10', '--start-ip-address'),
                ('203.0.113.10', '256.0.0.1', '--end-ip-address'),
                ('203.0.113.10', '203.0.113.9', 'greater than or equal')]:
            with self.subTest(start=start, end=end), self.assertRaisesRegex(InvalidArgumentValueError, error):
                command(command_args=dict(self.args, firewall_rule_name='office', start_ip_address=start,
                                          end_ip_address=end, no_wait=True))

    def test_create_warns_about_effective_access(self):
        name = 'horizondb cluster pool firewall-rule create'
        command = self.loader.load_command_table(name.split())[name]
        for end, message in [('0.0.0.0', 'from all Azure resources'),
                             ('0.0.0.10', "from '0.0.0.0' to '0.0.0.10'")]:
            with self.subTest(end=end), patch.object(command, 'FirewallRulesCreateOrReplace'), \
                    self.assertLogs(level='WARNING') as logs:
                command(command_args=dict(self.args, firewall_rule_name='office', start_ip_address='0.0.0.0',
                                          end_ip_address=end, no_wait=True))
                self.assertIn(message, logs.output[-1])

    def test_update_validates_merged_range_before_put(self):
        name = 'horizondb cluster pool firewall-rule update'
        command = self.loader.load_command_table(name.split())[name]
        args = dict(self.args, firewall_rule_name='office', end_ip_address='203.0.113.9', no_wait=True)

        def load_existing():
            command.ctx.set_var('instance', {'properties': {
                'startIpAddress': '203.0.113.10', 'endIpAddress': '203.0.113.12',
            }}, schema_builder=Update.FirewallRulesGet._build_schema_on_200)  # pylint: disable=protected-access

        with patch.object(command, 'FirewallRulesGet') as get, \
                patch.object(command, 'FirewallRulesCreateOrReplace') as put:
            get.return_value.side_effect = load_existing
            with self.assertRaisesRegex(InvalidArgumentValueError, 'greater than or equal'):
                command(command_args=args)
            put.assert_not_called()
            args['end_ip_address'] = '203.0.113.10'
            with self.assertLogs(level='WARNING') as logs:
                command(command_args=args)
            self.assertIn("from '203.0.113.10' to '203.0.113.10'", logs.output[-1])
            put.assert_called_once()

    def test_firewall_rule_name_pattern_rejects_invalid_names(self):
        for command_type in [Create, Update, Show, Delete, Wait]:
            schema = command_type.get_arguments_schema()
            pattern = schema.firewall_rule_name._fmt._pattern  # pylint: disable=protected-access
            for name in ['', '_rule', 'rule.', 'rule-', 'rule/name', 'a' * 81]:
                with self.subTest(command=command_type.__name__, name=name):
                    self.assertNotRegex(name, pattern)

    def test_rejects_firewall_rule_names_longer_than_80_characters(self):
        for command_type in [Create, Update, Show, Delete, Wait]:
            with self.subTest(command=command_type.__name__):
                command = command_type(loader=self.loader)
                args = self._name_args(command_type, 'a' * 81)
                with self.assertRaises(InvalidArgumentValueError):
                    AAZCommand._handler(command, args)  # pylint: disable=protected-access
