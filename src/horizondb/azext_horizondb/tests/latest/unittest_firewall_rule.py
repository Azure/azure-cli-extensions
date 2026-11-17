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

    def test_accepts_valid_firewall_rule_names(self):
        for command_type in [Create, Update, Show, Delete, Wait]:
            schema = command_type.get_arguments_schema()
            # AAZ stores regex constraints as metadata; format_args enforces lengths only.
            pattern = schema.firewall_rule_name._fmt._pattern  # pylint: disable=protected-access
            for name in ['a', 'Allow_Office.1-rule_', 'a' * 80]:
                with self.subTest(command=command_type.__name__, name=name):
                    command = command_type(loader=self.loader)
                    args = dict(self.args, firewall_rule_name=name)
                    AAZCommand._handler(command, args)  # pylint: disable=protected-access
                    self.assertRegex(name, pattern)
                    self.assertEqual(command.ctx.args.firewall_rule_name.to_serialized_data(), name)

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
                args = dict(self.args, firewall_rule_name='a' * 81)
                with self.assertRaises(InvalidArgumentValueError):
                    AAZCommand._handler(command, args)  # pylint: disable=protected-access
