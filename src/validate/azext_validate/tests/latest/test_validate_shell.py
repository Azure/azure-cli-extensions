# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Bash and PowerShell scripts: finding az commands without running anything."""

import unittest

from azext_validate import _extmeta, _shell
from azext_validate.tests.latest import _fake_metadata
from azext_validate.tests.latest._base import TempStore, ValidateTestBase, block_network, run_validate, unblock_network

BASH = '''#!/bin/bash
# create things
RG=rg1   # a comment
az group create -n $RG \\
   -l westus
for i in 1 2 3; do
  az vm create -g "$RG" -n "vm$i" --image Ubuntu2204
done
ID=$(az vm show -g $RG -n vm1 --query id -o tsv)
if [ -n "$ID" ]; then echo "$ID" | grep x; fi
NAME=`az group shw -n $RG --query name -o tsv`
echo done
'''

POWERSHELL = '''# PowerShell
$rg = "rg1"
az group create -n $rg `
   -l westus
foreach ($i in 1..3) {
  az vm create -g $rg -n "vm$i" --image Ubuntu2204
}
$id = az vm show -g $rg -n vm1 --query id -o tsv
$name = (az group shw -n $rg --query name -o tsv)
if ($id) { Write-Host $id }
Write-Output "done"
'''


def setUpModule():
    block_network()


def tearDownModule():
    unblock_network()


class TestScan(unittest.TestCase):
    def test_bash_positions(self):
        r = _shell.scan(BASH, 'bash')
        self.assertEqual([(' '.join(w.text for w in i.words[:2]), i.line, i.column) for i in r.invocations],
                         [('group create', 4, 1), ('vm create', 7, 3), ('vm show', 9, 6), ('group shw', 11, 7)])
        self.assertEqual(r.other_commands, 4)

    def test_powershell_positions(self):
        r = _shell.scan(POWERSHELL, 'powershell')
        self.assertEqual([(' '.join(w.text for w in i.words[:2]), i.line, i.column) for i in r.invocations],
                         [('group create', 3, 1), ('vm create', 6, 3), ('vm show', 8, 7), ('group shw', 9, 10)])

    def test_nothing_is_expanded(self):
        r = _shell.scan('az group create -n "$(whoami)" -l $LOC', 'bash')
        words = r.invocations[0].words
        self.assertEqual([w.text for w in words], ['group', 'create', '-n', '$(whoami)', '-l', '$LOC'])
        self.assertTrue(words[3].is_placeholder and words[5].is_placeholder)

    def test_unsupported_constructs(self):
        cases = [
            ('bash', 'az group list <<EOF\nx\nEOF', 'heredoc'),
            ('bash', 'az group list <<< x', 'herestring'),
            ('powershell', 'az group create @params', 'splatting'),
            ('powershell', 'az --% group list', 'stop-parsing'),
        ]
        for dialect, text, construct in cases:
            with self.subTest(text=text):
                r = _shell.scan(text, dialect)
                self.assertEqual([u.construct for u in r.invocations[0].unsupported], [construct])
        for dialect, text, construct in [('bash', 'diff <(az group list) x', 'process-substitution'),
                                         ('powershell', "$s = @'\naz group list\n'@", 'here-string'),
                                         ('powershell', "$a = @('x','y')", 'array-or-hashtable')]:
            with self.subTest(text=text):
                self.assertEqual([u.construct for u in _shell.scan(text, dialect).unsupported], [construct])

    def test_unbalanced_quotes(self):
        with self.assertRaises(_shell.ShellSyntaxError) as cm:
            _shell.scan('az group list\naz group create -n "rg -l westus', 'bash')
        self.assertEqual((cm.exception.line, cm.exception.column), (2, 20))

    def test_scan_before_error_inside_substitution(self):
        # The error inside "$(...)" is reported after the '(' opener; recovery still stops at the last ';'.
        text = 'az group list; echo "$(az vm list; az x -n "y)"'
        with self.assertRaises(_shell.ShellSyntaxError) as cm:
            _shell.scan(text, 'bash')
        found = _shell.scan_before_error(text, cm.exception, 'bash')
        self.assertEqual([[w.text for w in i.words] for i in found.invocations], [['group', 'list']])


class TestScripts(ValidateTestBase):
    def setUp(self):
        super().setUp()
        TempStore.fake_session = _fake_metadata.FakeSession({_extmeta.INDEX_URL: {}})

    def tearDown(self):
        TempStore.fake_session = None
        super().tearDown()

    def script(self, text, shell):
        code, doc, _ = run_validate('--script', text, shell=shell)
        self.assertEqual(code, 0)
        return doc

    def test_bash_script(self):
        doc = self.script(BASH, 'bash')
        self.assertEqual([(r['line'], r['status']) for r in doc['results']],
                         [(4, 'valid'), (7, 'valid'), (9, 'valid'), (11, 'invalid')])
        self.assertEqual(doc['results'][3]['errors'][0]['suggestions'], ['az group show'])
        self.assertEqual([n['code'] for n in doc['notes']], ['IgnoredCommands'])

    def test_powershell_script(self):
        doc = self.script(POWERSHELL, 'powershell')
        self.assertEqual([(r['line'], r['status']) for r in doc['results']],
                         [(3, 'valid'), (6, 'valid'), (8, 'valid'), (9, 'invalid')])

    def test_unsupported_syntax_is_unchecked(self):
        doc = self.script('az group create -n rg -l westus <<EOF\nx\nEOF\naz group list', 'bash')
        self.assertEqual([r['status'] for r in doc['results']], ['unchecked', 'valid'])
        self.assertEqual(doc['results'][0]['reason']['code'], 'UnsupportedShellSyntax')
        doc = self.script("$s = @'\naz group list\n'@\naz group list", 'powershell')
        self.assertEqual([r['status'] for r in doc['results']], ['valid'])
        self.assertEqual([n['code'] for n in doc['notes']], ['UnsupportedShellSyntax'])

    def test_syntax_error_still_checks_earlier_commands(self):
        doc = self.script('az group list\naz group create -n "rg -l westus', 'bash')
        self.assertEqual([r['status'] for r in doc['results']], ['valid', 'invalid'])
        err = doc['results'][1]['errors'][0]
        self.assertEqual((err['code'], err['line'], err['column']), ('ShellSyntax', 2, 20))

    def test_syntax_error_keeps_complete_commands_on_its_line(self):
        secret = 'Sup3rS3cretVa1ue'
        for shell, text in (('bash', 'az group list; az group create -n "unterminated ' + secret),
                            ('bash', 'az group list && az group create -n "unterminated ' + secret),
                            ('powershell', "az group list; az group create -n 'unterminated " + secret)):
            for mode in ('--script', '--command'):
                code, doc, out = run_validate(mode, text, shell=shell)
                self.assertEqual(code, 0)
                self.assertEqual([(r['status'], r.get('commandName')) for r in doc['results']],
                                 [('valid', 'group list'), ('invalid', None)], (shell, mode, text))
                err = doc['results'][1]['errors'][0]
                self.assertEqual((err['code'], err['line'], err['column']),
                                 ('ShellSyntax', 1, text.index('unterminated')))
                self.assertNotIn(secret, out)

    def test_no_az_commands(self):
        doc = self.script('echo hello\nls -la', 'bash')
        self.assertEqual(doc['results'], [])
        self.assertEqual([n['code'] for n in doc['notes']], ['NoAzCommands'])


if __name__ == '__main__':
    unittest.main()
