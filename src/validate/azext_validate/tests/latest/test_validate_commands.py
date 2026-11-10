# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access
"""Behaviour of az validate through the real CLI entry point, with the installed Azure CLI's parser."""

import io
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

from azure.cli.core import get_default_cli

from azext_validate import _extmeta
from azext_validate.tests.latest import _fake_metadata
from azext_validate.tests.latest._base import TempStore, ValidateTestBase, block_network, run_validate, unblock_network

# An extension index without the commands below, so local verdicts stand without any network.
_INDEX = {'graph': {'query': 'resource-graph'}}


def setUpModule():
    block_network()


def tearDownModule():
    unblock_network()


class CommandTestBase(ValidateTestBase):
    def setUp(self):
        super().setUp()
        TempStore.fake_session = _fake_metadata.FakeSession({_extmeta.INDEX_URL: _INDEX})

    def tearDown(self):
        TempStore.fake_session = None
        super().tearDown()

    def check(self, *commands, shell=None):
        code, doc, _ = run_validate('--command', *commands, shell=shell)
        self.assertEqual(code, 0)
        return doc

    def one(self, command, shell=None):
        doc = self.check(command, shell=shell)
        self.assertEqual(len(doc['results']), 1, doc)
        return doc['results'][0]

    def assertCodes(self, result, *codes):
        self.assertEqual([e['code'] for e in result['errors']], list(codes), result)


class TestValidCommands(CommandTestBase):
    def test_valid_forms(self):
        doc = self.check(
            'az group create -n rg --loc westus',                      # abbreviated parameter
            'az group list -o table --query "[].name" --subscription sub1 --only-show-errors --debug',
            'az vm show --ids /subscriptions/0000/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm1',
            'az network vnet create -g rg -n v --address-prefixes 10.0.0.0/16 10.1.0.0/16',
            'az acr build -r reg --image app:v1 .')                    # positional argument
        self.assertEqual([r['status'] for r in doc['results']], ['valid'] * 5)
        self.assertEqual(doc['status'], 'valid')
        self.assertTrue(doc['isValid'])
        self.assertEqual(doc['results'][0]['parameters'], ['--resource-group', '--location'])

    def test_missing_name_without_ids(self):
        r = self.one('az vm show -g rg')
        self.assertCodes(r, 'MissingRequiredArgument')
        self.assertEqual(r['errors'][0]['parameters'], ['--name'])
        self.assertEqual(r['errors'][0]['alternatives'], ['--ids'])

    def test_missing_name_without_ids_aaz(self):
        # AAZ commands default unset arguments to an "undefined" marker, which core's own check misses.
        r = self.one('az network vnet show -g rg')
        self.assertCodes(r, 'MissingRequiredArgument')
        self.assertEqual(r['errors'][0]['parameters'], ['--name'])
        self.assertEqual(self.one('az network vnet show -g rg -n v')['status'], 'valid')

    def test_help_and_yes(self):
        r = self.one('az vm create --help')
        self.assertEqual((r['status'], r['kind']), ('valid', 'help'))
        self.assertEqual([w['code'] for w in self.one('az group delete -n rg')['warnings']], ['PromptsForConfirmation'])
        self.assertEqual(self.one('az group delete -n rg --yes')['warnings'], [])

    def test_status_warnings(self):
        self.assertIn('DeprecatedCommand', [w['code'] for w in self.one(
            'az acr repository show-manifests -n reg --repository r')['warnings']])
        self.assertIn('Preview', [w['code'] for w in self.one('az acr manifest list -r reg -n repo')['warnings']])
        r = self.one('az vmss create -g rg -n s --image x --storage-caching ReadOnly')
        self.assertEqual(r['status'], 'valid')
        self.assertIn('DeprecatedArgument', [w['code'] for w in r['warnings']])


class TestErrorCodes(CommandTestBase):
    def test_command_errors(self):
        r = self.one('az vm craete -g rg -n vm')
        self.assertCodes(r, 'UnknownCommand')
        self.assertEqual(r['errors'][0]['suggestions'], ['az vm create'])
        # No close match in a small group: its subcommands are listed.
        r = self.one('az vm application remove -g rg -n vm')
        self.assertCodes(r, 'UnknownCommand')
        self.assertEqual(r['errors'][0]['suggestions'], ['az vm application list', 'az vm application set'])
        self.assertEqual(self.one('az vm zzzzzz')['errors'][0].get('suggestions'), None)
        # The top-level table is only partly loaded, so its few entries are not listed.
        self.assertEqual(self.one('az json-to-tsv --query x')['errors'][0].get('suggestions'), None)
        # An option before the command words: core keeps one example per group, so nothing is listed.
        r = self.one('az --only-show-errors group show -n rg')
        self.assertCodes(r, 'UnknownCommand')
        self.assertEqual(r['errors'][0].get('suggestions'), None)
        self.assertCodes(self.one('az vm'), 'MissingSubcommand')

    def test_subcommand_list_dropped_when_extensions_may_add(self):
        # No extension index: an extension that isn't installed may add subcommands, so no list.
        TempStore.fake_session = _fake_metadata.FakeSession({})
        r = self.one('az vm application remove -g rg -n vm')
        self.assertEqual((r['status'], r['reason']['code']), ('unchecked', 'ExtensionIndexUnavailable'))
        self.assertEqual([(w['code'], w.get('suggestions')) for w in r['warnings']], [('UnknownCommand', None)])
        # The index says an extension adds a subcommand to the group: core's list is incomplete.
        TempStore.fake_session = _fake_metadata.FakeSession(
            {_extmeta.INDEX_URL: {'vm': {'application': {'reboot': 'synthetic-ext'}}}})
        r = self.one('az vm application remove -g rg -n vm')
        self.assertCodes(r, 'UnknownCommand')
        self.assertEqual(r['errors'][0].get('suggestions'), None)
        self.assertCodes(self.one('ls -la'), 'NotAzCommand')

    def test_parameter_errors(self):
        cases = [
            ('az vm create -g rg -n vm --image x --sizee y', ['UnrecognizedArgument'], '--sizee'),
            ('az vm create -g rg -n vm --image x --admin y', ['AmbiguousArgument', 'UnrecognizedArgument'], '--admin'),
            ('az group create -n rg', ['MissingRequiredArgument'], '--location'),
            ('az group create -n rg -l', ['MissingValue', 'MissingRequiredArgument'], '--location'),
            ('az vm create -g rg -n vm --image x --generate-ssh-keys=yes', ['UnexpectedValue'], '--generate-ssh-keys'),
            ('az vm create -g rg -n vm --image x --count abc', ['InvalidValue'], '--count'),
            ('az storage account create -n a -g rg --sku Bad', ['InvalidChoice'], '--sku'),
            ("az vm list --query '[jmespathbad'", ['InvalidQuery'], '--query'),
            ('az vm show --ids badid', ['InvalidValue'], '--ids'),
        ]
        for command, codes, param in cases:
            with self.subTest(command=command):
                r = self.one(command)
                self.assertEqual(r['status'], 'invalid')
                self.assertCodes(r, *codes)
                first = r['errors'][0]
                self.assertIn(param, [first.get('parameter')] + list(first.get('parameters') or []))

    def test_several_errors_reported(self):
        r = self.one('az storage account create -n a -g rg --sku Bad --kind Nope --sizee 1')
        self.assertEqual(sorted(e['code'] for e in r['errors']), ['InvalidChoice', 'InvalidChoice',
                                                                 'UnrecognizedArgument'])

    def test_value_starting_with_dash(self):
        r = self.one('az vm create -g rg -n vm --image x --admin-password -Abc123')
        self.assertCodes(r, 'MissingValue')
        # The advice must not put '=' straight after a secret-looking name (log redactors would hide it).
        self.assertEqual(r['errors'][0]['message'], "--admin-password needs a value. If the value starts with '-', "
                         "join it to --admin-password with '=' instead of a space.")
        self.assertEqual(self.one('az vm create -g rg -n vm --image x --admin-password=-Abc123')['status'], 'valid')

    def test_rare_argparse_messages(self):
        # No core command uses these argparse paths today; check the classification directly.
        from azext_validate._engine import _classify_argparse_message
        finding = _classify_argparse_message('argument --a: not allowed with argument --b', None)
        self.assertEqual(finding['code'], 'MutuallyExclusiveArguments')

    def test_placeholder_command_name(self):
        r = self.one('az $CMD list')
        self.assertEqual(r['status'], 'unchecked')
        self.assertEqual(r['reason']['code'], 'PlaceholderCommandName')


class TestPlaceholders(CommandTestBase):
    """D4: a placeholder value counts as valid and is listed; a real value is checked normally."""

    def test_placeholders_are_valid_and_listed(self):
        cases = [
            ('az disk create -g <rg> -n "$DISK" --size-gb <size>', {'--resource-group': '<rg>', '--name': '$DISK',
                                                                     '--size-gb': '<size>'}),
            ('az disk create -g rg -n d --size-gb 10 --sku "<SKU NAME>"', {'--sku': '<SKU NAME>'}),
            ('az disk create -g rg -n d --size-gb 10 --sku "<Premium_LRS|Standard_LRS>"',
             {'--sku': '<Premium_LRS|Standard_LRS>'}),
            ('az disk create -g ${RG} -n $DISK --size-gb 10 --sku $SKU', {'--resource-group': '${RG}',
                                                                         '--name': '$DISK', '--sku': '$SKU'}),
            ('az disk create -g "$(az group show -n x --query name -o tsv)" -n d --size-gb 10',
             {'--resource-group': '$(...)'}),
        ]
        for command, expected in cases:
            with self.subTest(command=command):
                doc = self.check(command)
                r = doc['results'][0]
                self.assertEqual(r['status'], 'valid', r)
                self.assertEqual({p['parameter']: p.get('placeholder') for p in r['placeholders']}, expected)

    def test_real_values_still_checked(self):
        self.assertCodes(self.one('az disk create -g rg -n d --size-gb ten'), 'InvalidValue')
        self.assertCodes(self.one('az disk create -g rg -n d --size-gb 10 --sku Bad_SKU'), 'InvalidChoice')

    def test_nested_command_is_checked(self):
        doc = self.check('az disk create -g "$(az group shw -n x)" -n d --size-gb 10')
        self.assertEqual([r['status'] for r in doc['results']], ['valid', 'invalid'])
        self.assertCodes(doc['results'][1], 'UnknownCommand')

    def test_file_values_are_not_read(self):
        r = self.one('az deployment group create -g rg --template-file main.bicep --parameters @params.json')
        self.assertEqual(r['status'], 'valid')
        self.assertEqual(r['placeholders'], [{'parameter': '--parameters', 'placeholder': '@...'}])
        self.assertEqual([i['code'] for i in r['info']], ['ValueNotChecked'])

    def test_unquoted_placeholder_warning(self):
        r = self.one('az group create -n <rg> -l westus')
        self.assertEqual(r['status'], 'valid')
        self.assertEqual([w['code'] for w in r['warnings']], ['UnquotedPlaceholder'])


class TestOutput(CommandTestBase):
    def test_schema_and_exit_code(self):
        code, doc, _ = run_validate('--command', 'az group list', 'az group create -n rg')
        self.assertEqual(code, 0)
        self.assertEqual(doc['schemaVersion'], '1.0')
        self.assertEqual((doc['status'], doc['isValid']), ('invalid', False))
        self.assertEqual(doc['summary'], {'commands': 2, 'valid': 1, 'invalid': 1, 'unchecked': 0})
        self.assertEqual(set(doc['versions']), {'azureCli', 'validate'})
        for r in doc['results']:
            self.assertTrue({'index', 'line', 'column', 'status', 'errors', 'warnings'} <= set(r))
        self.assertEqual([r['index'] for r in doc['results']], [0, 1])

    def test_ascii_only(self):
        _, _, text = run_validate('--command', 'az group create -n rg -l westus --tags owner=Zoë')
        text.encode('ascii')

    def test_table_and_tsv_outputs(self):
        for fmt in ('table', 'tsv', 'yaml', 'jsonc'):
            with self.subTest(fmt=fmt):
                out = io.StringIO()
                code = get_default_cli().invoke(['validate', '--command', 'az group create -n rg', '-o', fmt],
                                                out_file=out)
                self.assertEqual(code, 0)
                self.assertIn('invalid', out.getvalue())

    def test_json_when_default_output_is_table(self):
        with mock.patch.dict(os.environ, {'AZURE_CORE_OUTPUT': 'table'}):
            code, doc, _ = run_validate('--command', 'az group list')
        self.assertEqual(code, 0)
        self.assertEqual(doc['status'], 'valid')


class TestFileInput(CommandTestBase):
    def setUp(self):
        super().setUp()
        self.dir = tempfile.mkdtemp(prefix='azvalidate-files-')

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)
        super().tearDown()

    def write(self, name, text):
        path = os.path.join(self.dir, name)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        return path

    def test_shell_inferred_from_file_name(self):
        # Backtick continuation is PowerShell; in Bash it's an unclosed command substitution.
        text = 'az group create -n rg `\n  -l westus\n'
        for name, expected in (('a.ps1', 'valid'), ('a.psm1', 'valid'), ('a.sh', 'invalid'), ('a.txt', 'invalid')):
            with self.subTest(name=name):
                code, doc, _ = run_validate('--file', self.write(name, text))
                self.assertEqual(code, 0)
                self.assertEqual(doc['status'], expected, doc)

    def test_utf16_powershell_file(self):
        # Windows PowerShell 5.1 `Out-File` writes UTF-16 with a byte-order mark.
        path = os.path.join(self.dir, 'utf16.ps1')
        with open(path, 'w', encoding='utf-16') as f:
            f.write('az group create -n rg `\n  -l westus\naz group shw -n rg\n')
        _, doc, _ = run_validate('--file', path)
        self.assertEqual([(r['line'], r['status']) for r in doc['results']], [(1, 'valid'), (3, 'invalid')])

    def test_explicit_shell_wins(self):
        path = self.write('a.ps1', 'az group create -n rg `\n  -l westus\n')
        _, doc, _ = run_validate('--file', path, shell='bash')
        self.assertEqual(doc['status'], 'invalid')
        path = self.write('b.sh', 'az group create -n rg `\n  -l westus\n')
        _, doc, _ = run_validate('--file', path, shell='powershell')
        self.assertEqual(doc['status'], 'valid')

    def test_lines_and_bom(self):
        path = self.write('deploy.sh', '\ufeff# comment\nRG=rg1\naz group create -n $RG -l westus\n'
                                       'az storage account create -n a -g $RG --sku Bad\n')
        _, doc, _ = run_validate('--file', path)
        self.assertEqual([(r['line'], r['status']) for r in doc['results']], [(3, 'valid'), (4, 'invalid')])

    def test_output_file(self):
        out_path = os.path.join(self.dir, 'result.json')
        code, doc, text = run_validate('--command', 'az group create -n rg', '--output-file', out_path)
        self.assertEqual(code, 0)
        with open(out_path, 'rb') as f:
            raw = f.read()
        raw.decode('ascii')
        self.assertEqual(json.loads(raw), doc)
        self.assertEqual(doc['status'], 'invalid')
        self.assertTrue(text.lstrip().startswith('{'))

    def test_usage_errors(self):
        out = io.StringIO()
        cli = get_default_cli()
        self.assertNotEqual(cli.invoke(['validate', '--file', os.path.join(self.dir, 'missing.sh')], out_file=out), 0)
        path = self.write('a.sh', 'az group list\n')
        self.assertNotEqual(cli.invoke(['validate', '--command', 'az group list', '--file', path], out_file=out), 0)
        self.assertNotEqual(cli.invoke(['validate'], out_file=out), 0)
        self.assertNotEqual(cli.invoke(['validate', '--command', 'az group list', '--output-file',
                                        os.path.join(self.dir, 'no-such-dir', 'r.json')], out_file=out), 0)


if __name__ == '__main__':
    unittest.main()
