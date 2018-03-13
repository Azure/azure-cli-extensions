# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long,no-self-use,too-many-public-methods

import unittest

from knack.util import CLIError

from azext_alias.argument import (
    get_placeholders,
    normalize_placeholders,
    build_pos_args_table,
    render_template,
    check_runtime_errors
)


class TestArgument(unittest.TestCase):

    def test_get_placeholders(self):
        self.assertListEqual(['arg_1', 'arg_2'], get_placeholders('{{ arg_1 }} {{ arg_2 }}'))

    def test_get_placeholders_with_numbers(self):
        self.assertListEqual(['_0', '_1'], get_placeholders('{{ 0 }} {{ 1 }}'))

    def test_get_placeholders_with_strings_and_numbers(self):
        self.assertListEqual(['_0', '_1', 'arg_1', 'arg_2'], get_placeholders('{{ 0 }} {{ 1 }} {{ arg_1 }} {{ arg_2 }}'))

    def test_get_placeholders_duplicate(self):
        with self.assertRaises(CLIError):
            get_placeholders('{{ arg_1 }} {{ arg_1 }}', check_duplicates=True)

    def test_get_placeholders_no_opening_bracket(self):
        with self.assertRaises(CLIError):
            get_placeholders('arg_1 }}')

    def test_get_placeholders_double_opening_bracket(self):
        with self.assertRaises(CLIError):
            get_placeholders('{{ {{ arg_1')

    def test_get_placeholders_double_closing_bracket(self):
        with self.assertRaises(CLIError):
            get_placeholders('{{ arg_1 }} }}')

    def test_get_placeholders_no_closing_bracket(self):
        with self.assertRaises(CLIError):
            get_placeholders('{{ arg_1 ')

    def test_normalize_placeholders(self):
        self.assertEqual('"{{ arg_1 }}" "{{ arg_2 }}"', normalize_placeholders('{{ arg_1 }} {{ arg_2 }}', inject_quotes=True))

    def test_normalize_placeholders_number(self):
        self.assertEqual('"{{_0}}" "{{_1}}"', normalize_placeholders('{{ 0 }} {{ 1 }}', inject_quotes=True))

    def test_normalize_placeholders_no_quotes(self):
        self.assertEqual('{{_0}} {{_1}}', normalize_placeholders('{{ 0 }} {{ 1 }}'))

    def test_normalize_placeholders_number_no_quotes(self):
        self.assertEqual('{{_0}} {{_1}}', normalize_placeholders('{{ 0 }} {{ 1 }}'))

    def test_build_pos_args_table(self):
        expected = {
            'arg_1': 'test_1',
            'arg_2': 'test_2'
        }
        self.assertDictEqual(expected, build_pos_args_table('{{ arg_1 }} {{ arg_2 }}', ['test_1', 'test_2'], 0))

    def test_build_pos_args_table_with_spaces(self):
        expected = {
            '_0': '{\\"test\\": \\"test\\"}',
            'arg_1': 'test1 test2',
            'arg_2': 'arg with spaces',
            'arg_3': '\\"azure cli\\"'
        }
        self.assertDictEqual(expected, build_pos_args_table('{{ 0 }} {{ arg_1 }} {{ arg_2 }} {{ arg_3 }}', ['{"test": "test"}', 'test1 test2', 'arg with spaces', '"azure cli"'], 0))

    def test_build_pos_args_table_not_enough_arguments(self):
        with self.assertRaises(CLIError):
            build_pos_args_table('{{ arg_1 }} {{ arg_2 }}', ['test_1', 'test_2'], 1)

    def test_render_template(self):
        pos_args_table = {
            'arg_1': 'test_1',
            'arg_2': 'test_2'
        }
        self.assertListEqual(['test_1', 'test_2'], render_template('{{ arg_1 }} {{ arg_2 }}', pos_args_table))

    def test_render_template_pos_arg_with_spaces(self):
        pos_args_table = {
            'arg_1': '{\\"test\\": \\"test\\"}',
            'arg_2': 'argument with spaces'
        }
        self.assertListEqual(['{"test": "test"}', 'argument with spaces'], render_template('{{ arg_1 }} {{ arg_2 }}', pos_args_table))

    def test_render_template_split_arg(self):
        pos_args_table = {
            'arg_1': 'argument with spaces'
        }
        self.assertListEqual(['argument'], render_template('{{ arg_1.split()[0] }}', pos_args_table))

    def test_render_template_upper(self):
        pos_args_table = {
            'arg_1': 'argument with spaces'
        }
        self.assertListEqual(['argument with spaces'.upper()], render_template('{{ arg_1.upper() }}', pos_args_table))

    def test_render_template_error(self):
        with self.assertRaises(CLIError):
            pos_args_table = {
                'arg_1': 'test_1',
                'arg_2': 'test_2'
            }
            render_template('{{ arg_1 }} {{ arg_2 }', pos_args_table)

    def test_check_runtime_errors_no_error(self):
        pos_args_table = {
            'arg_1': 'test_1',
            'arg_2': 'test_2'
        }
        check_runtime_errors('{{ arg_1.split("_")[0] }} {{ arg_2.split("_")[1] }}', pos_args_table)

    def test_check_runtime_errors_has_error(self):
        with self.assertRaises(CLIError):
            pos_args_table = {
                'arg_1': 'test_1',
                'arg_2': 'test_2'
            }
            check_runtime_errors('{{ arg_1.split("_")[2] }} {{ arg_2.split("_")[1] }}', pos_args_table)


if __name__ == '__main__':
    unittest.main()
