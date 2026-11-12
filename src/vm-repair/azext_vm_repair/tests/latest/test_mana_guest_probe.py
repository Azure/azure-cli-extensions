# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import ast
import os
import re
import unittest
from unittest.mock import patch

from azext_vm_repair import repair_utils
from azext_vm_repair.exceptions import AzCommandError


UNKNOWN = {'hardware': 'unknown', 'driver': 'unknown', 'source': 'skipped'}
PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SETUP_PY = os.path.join(os.path.dirname(PACKAGE_ROOT), 'setup.py')
PROBE_SCRIPTS = ('linux-mana-driver-probe.sh', 'win-mana-driver-probe.ps1')


class ManaProbeOutputParsingTests(unittest.TestCase):

    def test_reported_values_are_returned(self):
        cases = [
            ('mana', 'present'), ('mana', 'missing'), ('mellanox', 'present'),
            ('mellanox', 'unknown'), ('none', 'missing'), ('unknown', 'unknown')
        ]
        for hardware, driver in cases:
            with self.subTest(hardware=hardware, driver=driver):
                stdout = 'VMREPAIR_MANA_PROBE hardware={} driver={}'.format(hardware, driver)
                self.assertEqual({'hardware': hardware, 'driver': driver},
                                 repair_utils._parse_mana_probe_output(stdout))

    def test_surrounding_output_is_ignored(self):
        stdout = 'Enable succeeded:\n[stdout]\n  VMREPAIR_MANA_PROBE hardware=mana driver=missing  \n\n'
        self.assertEqual({'hardware': 'mana', 'driver': 'missing'},
                         repair_utils._parse_mana_probe_output(stdout))

    def test_unrecognized_output_is_rejected(self):
        cases = [
            None, '', 'no marker here',
            'VMREPAIR_MANA_PROBE hardware=mana',
            'VMREPAIR_MANA_PROBE hardware=intel driver=present',
            'VMREPAIR_MANA_PROBE hardware=mana driver=yes',
            'VMREPAIR_MANA_PROBE hardware=mana driver=present extra=value',
            'VMREPAIR_MANA_PROBE driver=present hardware=mana hardware=none',
            'VMREPAIR_MANA_PROBE hardware=mana driver=present\nVMREPAIR_MANA_PROBE hardware=none driver=missing',
            'prefix VMREPAIR_MANA_PROBE hardware=mana driver=present',
        ]
        for stdout in cases:
            with self.subTest(stdout=stdout):
                self.assertIsNone(repair_utils._parse_mana_probe_output(stdout))


class CheckGuestManaDriverTests(unittest.TestCase):

    @patch('azext_vm_repair.repair_utils._invoke_run_command')
    def test_probe_results_are_reported(self, invoke):
        cases = [
            ('mana', 'present'), ('mana', 'missing'), ('mellanox', 'present'), ('none', 'missing')
        ]
        for hardware, driver in cases:
            with self.subTest(hardware=hardware, driver=driver):
                invoke.return_value = (
                    'VMREPAIR_MANA_PROBE hardware={} driver={}'.format(hardware, driver), '')
                self.assertEqual(
                    {'hardware': hardware, 'driver': driver, 'source': 'run-command'},
                    repair_utils._check_guest_mana_driver('vm', 'rg', True))

    @patch('azext_vm_repair.repair_utils._invoke_run_command',
           return_value=('VMREPAIR_MANA_PROBE hardware=none driver=missing', ''))
    def test_os_specific_probe_runs_without_parameters(self, invoke):
        for is_linux, script in ((True, PROBE_SCRIPTS[0]), (False, PROBE_SCRIPTS[1])):
            with self.subTest(is_linux=is_linux):
                repair_utils._check_guest_mana_driver('vm', 'rg', is_linux)
                invoke.assert_called_with(script, 'vm', 'rg', is_linux)

    @patch('azext_vm_repair.repair_utils._invoke_run_command')
    def test_run_command_failures_are_unknown(self, invoke):
        failures = [
            AzCommandError('The VM agent is not ready or the operation timed out.'),
            KeyError('value'), IndexError('list index out of range'),
            ValueError('Expecting value'), TypeError('NoneType'),
            repair_utils.InvalidArgumentValueError('unsupported character')
        ]
        for failure in failures:
            with self.subTest(failure=type(failure).__name__):
                invoke.side_effect = failure
                self.assertEqual(UNKNOWN, repair_utils._check_guest_mana_driver('vm', 'rg', False))

    @patch('azext_vm_repair.repair_utils._invoke_run_command', return_value=('unexpected output', ''))
    def test_unreadable_output_is_unknown_not_missing(self, _):
        self.assertEqual({'hardware': 'unknown', 'driver': 'unknown', 'source': 'run-command'},
                         repair_utils._check_guest_mana_driver('vm', 'rg', True))


class ManaProbeScriptTests(unittest.TestCase):

    def _script(self, name):
        with open(os.path.join(PACKAGE_ROOT, 'scripts', name), encoding='utf-8') as handle:
            return handle.read()

    def test_probe_scripts_are_packaged(self):
        with open(SETUP_PY, encoding='utf-8') as handle:
            tree = ast.parse(handle.read())
        packaged = {
            node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        for name in PROBE_SCRIPTS:
            with self.subTest(script=name):
                self.assertTrue(os.path.isfile(os.path.join(PACKAGE_ROOT, 'scripts', name)))
                self.assertIn('scripts/' + name, packaged)

    def test_probe_scripts_emit_the_parsed_marker(self):
        for name in PROBE_SCRIPTS:
            with self.subTest(script=name):
                self.assertIn('VMREPAIR_MANA_PROBE hardware=', self._script(name))

    def test_probe_scripts_take_no_input_and_are_read_only(self):
        forbidden = {
            PROBE_SCRIPTS[0]: ('$1', '$@', '$*', 'modprobe', 'rmmod', 'insmod', 'dracut',
                               'update-initramfs', 'ip link set', 'curl', 'wget', 'tee '),
            PROBE_SCRIPTS[1]: ('param(', '$args', 'Set-', 'Enable-', 'Disable-', 'Remove-',
                               'Install-', 'Restart-', 'Invoke-WebRequest', 'Invoke-Expression',
                               'pnputil', 'Out-File', 'Add-Content')
        }
        for name, tokens in forbidden.items():
            content = self._script(name)
            for token in tokens:
                with self.subTest(script=name, token=token):
                    self.assertNotIn(token, content)
        # The Linux probe may only discard output; it must never write to a file.
        commands = '\n'.join(line for line in self._script(PROBE_SCRIPTS[0]).splitlines()
                             if not line.lstrip().startswith('#'))
        self.assertIsNone(re.search(r'>>?\s*(?!/dev/null\b)[\w/$"]', commands))


if __name__ == '__main__':
    unittest.main()
