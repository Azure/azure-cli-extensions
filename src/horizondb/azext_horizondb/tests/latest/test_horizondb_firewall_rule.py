# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from argparse import Namespace
from unittest import mock

from knack.util import CLIError
from azure.cli.core.azclierror import ArgumentUsageError, InvalidArgumentValueError

from azext_horizondb.utils.validators import (
    public_access_validator,
    ip_address_validator,
    _validate_ip,
    _validate_ranges_in_ip,
    _valid_range,
    _validate_start_and_end_ip_address_order,
)
from azext_horizondb.utils._network import (
    DEFAULT_POOL_NAME,
    parse_public_access_input,
    resolve_public_access_range,
    _get_user_confirmation,
)
from azext_horizondb.commands.firewall_rule_commands import (
    _generate_firewall_rule_name,
    create_firewall_rule,
    horizondb_firewall_rule_create,
    horizondb_firewall_rule_update,
    horizondb_firewall_rule_list,
)
from azext_horizondb.commands.custom_commands import (
    _resolve_public_access_range_for_command,
)


class HorizonDBPublicAccessValidatorTests(unittest.TestCase):

    def test_public_access_valid_keywords(self):
        for value in ['Enabled', 'Disabled', 'All', 'None', 'enabled', 'disabled']:
            public_access_validator(Namespace(public_access=value))

    def test_public_access_valid_single_ip(self):
        public_access_validator(Namespace(public_access='12.12.12.12'))

    def test_public_access_valid_range(self):
        public_access_validator(Namespace(public_access='12.12.12.0-12.12.12.255'))

    def test_public_access_none_value_is_noop(self):
        # An unset value (None) should not raise.
        public_access_validator(Namespace(public_access=None))

    def test_public_access_invalid_keyword(self):
        with self.assertRaises(CLIError):
            public_access_validator(Namespace(public_access='sometimes'))

    def test_public_access_invalid_ip_octet(self):
        with self.assertRaises(CLIError):
            public_access_validator(Namespace(public_access='999.0.0.1'))

    def test_public_access_reversed_range_raises(self):
        with self.assertRaises(ArgumentUsageError):
            public_access_validator(Namespace(public_access='12.12.12.255-12.12.12.0'))


class HorizonDBIpAddressValidatorTests(unittest.TestCase):

    def test_valid_start_and_end(self):
        ip_address_validator(Namespace(start_ip_address='1.1.1.1', end_ip_address='2.2.2.2'))

    def test_invalid_ip_raises(self):
        with self.assertRaises(CLIError):
            ip_address_validator(Namespace(start_ip_address='1.1.1', end_ip_address=None))

    def test_reversed_order_raises(self):
        with self.assertRaises(ArgumentUsageError):
            ip_address_validator(Namespace(start_ip_address='2.2.2.2', end_ip_address='1.1.1.1'))

    def test_only_start_ip_valid(self):
        ip_address_validator(Namespace(start_ip_address='1.1.1.1', end_ip_address=None))

    def test_range_value_in_single_ip_field_raises_clierror(self):
        # A dash-separated range is invalid for the single-IP start/end fields and must surface a
        # clean CLIError rather than a raw ValueError.
        with self.assertRaises(CLIError):
            ip_address_validator(Namespace(start_ip_address='1.1.1.1-2.2.2.2', end_ip_address='3.3.3.3'))


class HorizonDBIpHelpersTests(unittest.TestCase):

    def test_valid_range(self):
        self.assertTrue(_valid_range('0'))
        self.assertTrue(_valid_range('255'))
        self.assertFalse(_valid_range('256'))
        self.assertFalse(_valid_range('-1'))
        self.assertFalse(_valid_range('abc'))

    def test_validate_ranges_in_ip(self):
        self.assertTrue(_validate_ranges_in_ip('192.168.0.1'))
        self.assertFalse(_validate_ranges_in_ip('192.168.0'))
        self.assertFalse(_validate_ranges_in_ip('192.168.0.256'))

    def test_validate_ip_single_and_range(self):
        self.assertTrue(_validate_ip('10.0.0.1'))
        self.assertTrue(_validate_ip('10.0.0.1-10.0.0.5'))
        self.assertFalse(_validate_ip('10.0.0.1-10.0.0.5-10.0.0.9'))

    def test_start_end_order_ok(self):
        _validate_start_and_end_ip_address_order('10.0.0.1', '10.0.0.5')

    def test_start_end_order_bad(self):
        with self.assertRaises(ArgumentUsageError):
            _validate_start_and_end_ip_address_order('10.0.0.5', '10.0.0.1')


class HorizonDBParsePublicAccessTests(unittest.TestCase):

    def test_single_ip(self):
        self.assertEqual(parse_public_access_input('10.0.0.1'), ('10.0.0.1', '10.0.0.1'))

    def test_range(self):
        self.assertEqual(parse_public_access_input('10.0.0.1-10.0.0.9'), ('10.0.0.1', '10.0.0.9'))

    def test_none(self):
        self.assertEqual(parse_public_access_input(None), (None, None))

    def test_too_many_parts(self):
        with self.assertRaises(InvalidArgumentValueError):
            parse_public_access_input('10.0.0.1-10.0.0.9-10.0.0.20')


class HorizonDBResolvePublicAccessRangeTests(unittest.TestCase):

    def test_all(self):
        self.assertEqual(resolve_public_access_range('All', yes=True), ('0.0.0.0', '255.255.255.255'))

    def test_none_and_disabled(self):
        self.assertEqual(resolve_public_access_range('None', yes=True), (-1, -1))
        self.assertEqual(resolve_public_access_range('Disabled', yes=True), (-1, -1))

    def test_single_ip(self):
        self.assertEqual(resolve_public_access_range('10.0.0.1', yes=True), ('10.0.0.1', '10.0.0.1'))

    def test_range(self):
        self.assertEqual(resolve_public_access_range('10.0.0.1-10.0.0.9', yes=True),
                         ('10.0.0.1', '10.0.0.9'))

    @mock.patch('azext_horizondb.utils._network.get')
    def test_enabled_resolves_client_ip(self, mock_get):
        response = mock.MagicMock()
        response.text = '13.13.13.13'
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        self.assertEqual(resolve_public_access_range('Enabled', yes=True),
                         ('13.13.13.13', '13.13.13.13'))

    @mock.patch('azext_horizondb.utils._network.get')
    def test_enabled_detection_failure_raises(self, mock_get):
        mock_get.side_effect = Exception('network down')
        with self.assertRaises(CLIError):
            resolve_public_access_range('Enabled', yes=True)


class HorizonDBFirewallRuleNameTests(unittest.TestCase):

    def test_allow_all_name(self):
        name = _generate_firewall_rule_name('0.0.0.0', '255.255.255.255')
        self.assertTrue(name.startswith('AllowAll_'))

    def test_single_ip_name(self):
        name = _generate_firewall_rule_name('10.0.0.1', '10.0.0.1')
        self.assertTrue(name.startswith('FirewallIPAddress_'))

    def test_range_name(self):
        name = _generate_firewall_rule_name('10.0.0.1', '10.0.0.9')
        self.assertTrue(name.startswith('FirewallIPAddress_'))


class HorizonDBFirewallRuleCommandTests(unittest.TestCase):

    def test_create_defaults_end_ip_to_start_and_targets_default_pool(self):
        client = mock.MagicMock()
        create_firewall_rule(cmd=None, client=client, resource_group_name='rg',
                             cluster_name='c', start_ip_address='10.0.0.1', end_ip_address=None,
                             firewall_rule_name='rule1')

        _, kwargs = client.begin_create_or_update.call_args
        self.assertEqual(kwargs['pool_name'], DEFAULT_POOL_NAME)
        self.assertEqual(kwargs['firewall_rule_name'], 'rule1')
        resource = kwargs['resource']
        self.assertEqual(resource.properties.start_ip_address, '10.0.0.1')
        self.assertEqual(resource.properties.end_ip_address, '10.0.0.1')

    def test_create_requires_at_least_one_ip(self):
        client = mock.MagicMock()
        with self.assertRaises(ArgumentUsageError):
            create_firewall_rule(cmd=None, client=client, resource_group_name='rg',
                                 cluster_name='c', start_ip_address=None, end_ip_address=None)

    def test_command_create_passes_description(self):
        client = mock.MagicMock()
        horizondb_firewall_rule_create(cmd=None, client=client, resource_group_name='rg',
                                       cluster_name='c', firewall_rule_name='rule1',
                                       start_ip_address='10.0.0.1', end_ip_address='10.0.0.9',
                                       description='corp network')
        _, kwargs = client.begin_create_or_update.call_args
        self.assertEqual(kwargs['resource'].properties.description, 'corp network')
        self.assertEqual(kwargs['resource'].properties.end_ip_address, '10.0.0.9')

    def test_list_targets_default_pool(self):
        client = mock.MagicMock()
        horizondb_firewall_rule_list(cmd=None, client=client, resource_group_name='rg', cluster_name='c')
        _, kwargs = client.list.call_args
        self.assertEqual(kwargs['pool_name'], DEFAULT_POOL_NAME)

    def test_update_merges_existing_values(self):
        client = mock.MagicMock()
        existing = mock.MagicMock()
        existing.properties.start_ip_address = '10.0.0.1'
        existing.properties.end_ip_address = '10.0.0.5'
        existing.properties.description = 'old'
        client.get.return_value = existing

        horizondb_firewall_rule_update(cmd=None, client=client, resource_group_name='rg',
                                       cluster_name='c', firewall_rule_name='r',
                                       end_ip_address='10.0.0.9')

        _, kwargs = client.begin_create_or_update.call_args
        self.assertEqual(kwargs['pool_name'], DEFAULT_POOL_NAME)
        self.assertEqual(kwargs['resource'].properties.start_ip_address, '10.0.0.1')
        self.assertEqual(kwargs['resource'].properties.end_ip_address, '10.0.0.9')
        self.assertEqual(kwargs['resource'].properties.description, 'old')

    def test_update_inverted_merged_range_raises(self):
        # Changing only the start IP such that the merged range inverts must fail client-side.
        client = mock.MagicMock()
        existing = mock.MagicMock()
        existing.properties.start_ip_address = '10.0.0.1'
        existing.properties.end_ip_address = '10.0.0.5'
        existing.properties.description = None
        client.get.return_value = existing

        with self.assertRaises(ArgumentUsageError):
            horizondb_firewall_rule_update(cmd=None, client=client, resource_group_name='rg',
                                           cluster_name='c', firewall_rule_name='r',
                                           start_ip_address='200.0.0.0')
        client.begin_create_or_update.assert_not_called()


class HorizonDBResolvePublicAccessForCommandTests(unittest.TestCase):

    def test_unset_and_empty_return_none(self):
        self.assertIsNone(_resolve_public_access_range_for_command(None, yes=True, is_update=False))
        self.assertIsNone(_resolve_public_access_range_for_command('', yes=True, is_update=False))

    def test_disabled_and_none_return_none(self):
        self.assertIsNone(_resolve_public_access_range_for_command('Disabled', yes=True, is_update=True))
        self.assertIsNone(_resolve_public_access_range_for_command('None', yes=True, is_update=False))

    def test_all_returns_full_range(self):
        self.assertEqual(_resolve_public_access_range_for_command('All', yes=True, is_update=False),
                         ('0.0.0.0', '255.255.255.255'))

    def test_single_ip_returns_pair(self):
        self.assertEqual(_resolve_public_access_range_for_command('10.0.0.1', yes=True, is_update=False),
                         ('10.0.0.1', '10.0.0.1'))


class HorizonDBUserConfirmationTests(unittest.TestCase):

    def test_yes_short_circuits(self):
        self.assertTrue(_get_user_confirmation('proceed?', yes=True))

    @mock.patch('azext_horizondb.utils._network.prompt_y_n')
    def test_eoferror_becomes_clierror(self, mock_prompt):
        mock_prompt.side_effect = EOFError()
        with self.assertRaises(CLIError):
            _get_user_confirmation('proceed?', yes=False)


if __name__ == '__main__':
    unittest.main()
