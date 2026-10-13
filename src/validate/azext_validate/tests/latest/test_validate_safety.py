# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access
"""Safety tests (S1-S10). Each runs through the real CLI entry point."""

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from azure.cli.core import telemetry

from azext_validate import _engine, _extmeta
from azext_validate.tests.latest import _fake_metadata
from azext_validate.tests.latest._base import (NETWORK_ATTEMPTS as _NETWORK_ATTEMPTS, TempStore as _TempStore,
                                               ValidateTestBase as SafetyTestBase, block_network, run_validate,
                                               unblock_network)


def setUpModule():  # S3: no network for the whole module
    block_network()


def tearDownModule():
    unblock_network()


class TestS1NeverRuns(SafetyTestBase):
    def test_handlers_and_jobs_never_called(self):
        from azure.cli.core.commands import AzCliCommand, AzCliCommandInvoker
        from azure.cli.core import util as core_util
        called = []
        real_call = AzCliCommand.__call__
        real_run_job = AzCliCommandInvoker._run_job

        def guarded_call(self, *a, **k):
            if self.name != 'validate':
                called.append(self.name)
                raise AssertionError('handler called: ' + self.name)
            return real_call(self, *a, **k)

        def guarded_run_job(self, expanded_arg, cmd_copy):
            if cmd_copy.name != 'validate':
                called.append('job:' + cmd_copy.name)
                raise AssertionError('job run: ' + cmd_copy.name)
            return real_run_job(self, expanded_arg, cmd_copy)

        with mock.patch.object(AzCliCommand, '__call__', guarded_call), \
                mock.patch.object(AzCliCommandInvoker, '_run_job', guarded_run_job), \
                mock.patch.object(core_util, 'run_az_cmd', side_effect=AssertionError('run_az_cmd')) as run_az:
            code, doc, _ = run_validate('--command', 'az group delete -n rg1 --yes',
                                        'az vm delete -g rg1 -n vm1 --yes',
                                        'az storage account delete -n acct1 -g rg1 --yes')
        self.assertEqual(code, 0)
        self.assertEqual(called, [])
        run_az.assert_not_called()
        self.assertEqual([r['status'] for r in doc['results']], ['valid'] * 3)


class TestS2NeverInstalls(SafetyTestBase):
    def test_no_dynamic_install_for_missing_extension(self):
        import azure.cli.core.extension.dynamic_install as dyn
        import azure.cli.core.extension.operations as ext_ops
        from azure.cli.core import util as core_util
        from azure.cli.core.extension import EXTENSIONS_DIR
        before = sorted(os.listdir(EXTENSIONS_DIR)) if os.path.isdir(EXTENSIONS_DIR) else []
        fake_tree = mock.Mock(data={'graph': {'query': 'resource-graph'}})
        fake_tree.get = lambda k, d=None: {'graph': {'query': 'resource-graph'}}.get(k, d)
        with mock.patch.dict(os.environ, {'AZURE_EXTENSION_USE_DYNAMIC_INSTALL': 'yes_without_prompt',
                                          'AZURE_EXTENSION_RUN_AFTER_DYNAMIC_INSTALL': 'true'}), \
                mock.patch.object(dyn, '_get_extension_command_tree',
                                  return_value={'graph': {'query': 'resource-graph'}}), \
                mock.patch.object(ext_ops, 'add_extension') as add_ext, \
                mock.patch.object(core_util, 'run_az_cmd') as run_az:
            code, doc, _ = run_validate('--command', "az graph query -q 'Resources | take 1'")
        self.assertEqual(code, 0)
        add_ext.assert_not_called()
        run_az.assert_not_called()
        self.assertEqual(_engine.BLOCKED_CALLS, [])
        after = sorted(os.listdir(EXTENSIONS_DIR)) if os.path.isdir(EXTENSIONS_DIR) else []
        self.assertEqual(before, after)
        # Network is blocked and nothing is cached, so the extension command can't be checked.
        self.assertEqual(doc['results'][0]['status'], 'unchecked')


class TestS3Network(SafetyTestBase):
    def test_valid_core_commands_never_touch_network(self):
        code, doc, _ = run_validate('--command', 'az vm create -g rg -n vm --image Ubuntu2204',
                                    'az group list --query "[].name"', 'az group delete -n rg')
        self.assertEqual(code, 0)
        self.assertEqual([r['status'] for r in doc['results']], ['valid'] * 3)
        self.assertEqual(_NETWORK_ATTEMPTS, [])

    def test_rejected_core_command_only_asks_allowed_hosts(self):
        # Core rejects --sizee; the extension index is consulted (an extension might add it). With the
        # network down the core verdict stands, with a warning.
        code, doc, _ = run_validate('--command', 'az vm create -g rg -n vm --image Ubuntu2204 --sizee x')
        self.assertEqual(code, 0)
        r = doc['results'][0]
        self.assertEqual(r['status'], 'invalid')
        self.assertIn('ExtensionIndexUnavailable', [w['code'] for w in r['warnings']])
        self.assertTrue({h for h, _ in _NETWORK_ATTEMPTS} <= _extmeta.ALLOWED_HOSTS, _NETWORK_ATTEMPTS)

    def test_extension_command_unchecked_when_metadata_unavailable(self):
        code, doc, _ = run_validate('--command', "az graph query -q 'x'")
        self.assertEqual(doc['results'][0]['status'], 'unchecked')
        self.assertIn(doc['results'][0]['reason']['code'], ('ExtensionIndexUnavailable', 'MetadataUnavailable'))

    def test_extension_command_checked_with_fake_metadata_server(self):
        index = {'graph': {'query': 'resource-graph'}}
        meta = {'module_name': 'resource-graph', 'name': 'resource-graph', 'commands': {}, 'sub_groups': {
            'graph': {'name': 'graph', 'commands': {'graph query': {'name': 'graph query', 'parameters': [
                {'name': 'graph_query', 'options': ['--graph-query', '--q', '-q'], 'required': True},
                {'name': 'first', 'options': ['--first'], 'type': 'int'}]}}, 'sub_groups': {}}}}
        session = _fake_metadata.FakeSession({
            _extmeta.INDEX_URL: index,
            _extmeta.META_BASE_URL + '/ext-resource-graph/version_list.txt':
                'az_resource-graph_meta_2.1.0.json\naz_resource-graph_meta_2.1.1.json\n',
            _extmeta.META_BASE_URL + '/ext-resource-graph/az_resource-graph_meta_2.1.1.json': meta,
        })
        _TempStore.fake_session = session
        try:
            code, doc, _ = run_validate('--command', "az graph query -q 'x'", "az graph query -q 'x' --first abc",
                                        'az graph qery -q x')
        finally:
            _TempStore.fake_session = None
        self.assertEqual(code, 0)
        self.assertEqual([r['status'] for r in doc['results']], ['valid', 'invalid', 'invalid'])
        self.assertEqual(doc['results'][1]['errors'][0]['code'], 'InvalidValue')
        self.assertEqual(doc['results'][2]['errors'][0]['suggestions'], ['az graph query'])
        from urllib.parse import urlparse
        self.assertTrue({urlparse(u).hostname for u in session.urls} <= _extmeta.ALLOWED_HOSTS, session.urls)
        self.assertEqual(_NETWORK_ATTEMPTS, [])


class TestS4Files(SafetyTestBase):
    def test_named_files_and_stdin_never_read(self):
        sentinel = 'SENTINEL-' + os.urandom(8).hex()
        path = os.path.join(self.tmp, 'secret.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump([{'name': sentinel, 'addressPrefix': '10.0.0.0/24'}], f)
        opened = []
        real_open = open

        def recording_open(file, *a, **k):
            result = real_open(file, *a, **k)
            if isinstance(file, (str, os.PathLike)) and os.path.abspath(os.fspath(file)) == os.path.abspath(path):
                opened.append(file)
            return result

        cwd = os.getcwd()
        os.chdir(self.tmp)
        try:
            with mock.patch('builtins.open', recording_open), mock.patch('io.open', recording_open):
                code, doc, text = run_validate(
                    '--command',
                    'az deployment group create -g rg --template-file main.bicep --parameters @secret.json',
                    'az keyvault secret set --vault-name v -n s --value @-',
                    'az network vnet create -g rg -n vnet --subnets secret.json',
                    'az network vnet create -g rg -n vnet --subnets @' + path)
        finally:
            os.chdir(cwd)
        self.assertEqual(code, 0)
        self.assertEqual(opened, [])
        self.assertNotIn(sentinel, text)
        self.assertEqual([r['status'] for r in doc['results']], ['valid'] * 4)


class TestS5NoPrompt(unittest.TestCase):
    def test_no_stdin_read_or_prompt(self):
        # stdin is a pipe that is never written or closed: any read or prompt would hang.
        proc = subprocess.Popen([sys.executable, '-m', 'azure.cli', 'validate', '--command',
                                 'az keyvault secret set --vault-name v -n s --value @-',
                                 'az group delete -n rg', '-o', 'json'],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            out, _ = proc.communicate(timeout=120)
        finally:
            if proc.poll() is None:
                proc.kill()
        doc = json.loads(out)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual([r['status'] for r in doc['results']], ['valid', 'valid'])
        self.assertEqual([w['code'] for w in doc['results'][1]['warnings']], ['PromptsForConfirmation'])


class TestSandbox(unittest.TestCase):
    def test_working_directory_listed_not_read(self):
        # `python -m azure.cli` puts the working directory on sys.path; loading modules may list it.
        from azext_validate import _sandbox
        tmp = tempfile.mkdtemp(prefix='azvalidate-cwd-')
        cfg = tempfile.mkdtemp(prefix='azvalidate-cfg-')
        cwd = os.getcwd()
        try:
            with open(os.path.join(tmp, 'secret.txt'), 'w', encoding='utf-8') as f:
                f.write('x')
            os.chdir(tmp)
            with mock.patch.object(sys, 'path', [''] + sys.path):
                with _sandbox.guard('load', cfg) as g:
                    self.assertIn('secret.txt', os.listdir(os.getcwd()))
                    with self.assertRaises(_sandbox.SandboxViolation):
                        open('secret.txt', encoding='utf-8')  # pylint: disable=consider-using-with
                self.assertEqual([e for e, _ in g.violations], ['open'])
                with _sandbox.guard('parse', cfg):
                    with self.assertRaises(_sandbox.SandboxViolation):
                        os.listdir(os.getcwd())
        finally:
            os.chdir(cwd)
            shutil.rmtree(tmp, ignore_errors=True)
            shutil.rmtree(cfg, ignore_errors=True)

    def test_metadata_threads_are_exempt(self):
        import threading
        from azext_validate import _sandbox
        results = []

        def worker(exempt):
            if exempt:
                _sandbox.exempt_thread()
            try:
                os.listdir(os.path.expanduser('~'))
                results.append((exempt, 'allowed'))
            except _sandbox.SandboxViolation:
                results.append((exempt, 'blocked'))
        with _sandbox.guard('parse', tempfile.gettempdir()) as g:
            for exempt in (True, False):
                t = threading.Thread(target=worker, args=(exempt,))
                t.start()
                t.join()
        self.assertEqual(results, [(True, 'allowed'), (False, 'blocked')])
        self.assertEqual(len(g.violations), 1)


class TestS7SideEffects(SafetyTestBase):
    def test_no_command_logs_or_history_for_checked_commands(self):
        from azure.cli.core._environment import get_config_dir
        cfg = get_config_dir()
        log_dir = os.path.join(cfg, 'commands')
        before = set(os.listdir(log_dir)) if os.path.isdir(log_dir) else set()
        history = os.path.join(cfg, 'recommendation', 'cmd_history.log')
        # `next` (if installed) keeps only the last 30 lines, so start from one known line and restore the
        # file afterwards; otherwise old lines dropping off the front would hide new ones.
        sentinel = json.dumps({'command': 'azvalidate-test-sentinel'})
        saved = None
        if os.path.exists(history):
            with open(history, 'rb') as f:
                saved = f.read()
            with open(history, 'w', encoding='utf-8') as f:
                f.write(sentinel)
        try:
            with open(os.path.join(cfg, 'config'), encoding='utf-8') as f:
                config_before = f.read()
            run_validate('--command', 'az vm create -g rg -n vm --image Ubuntu2204', 'az storage account list')
            after = set(os.listdir(log_dir)) if os.path.isdir(log_dir) else set()
            new = sorted(after - before)
            self.assertTrue(all('.validate.' in n for n in new), new)
            lines = []
            if os.path.exists(history):
                with open(history, encoding='utf-8') as f:
                    lines = [x for x in f.read().splitlines() if x.strip()]
            if saved is not None:
                self.assertEqual(lines[:1], [sentinel])
                lines = lines[1:]
            # `next` logs the outer `az validate` call like any az call; never the checked ones.
            for line in lines:
                self.assertEqual(json.loads(line).get('command'), 'validate', line)
            with open(os.path.join(cfg, 'config'), encoding='utf-8') as f:
                self.assertEqual(config_before, f.read())
        finally:
            if saved is not None:
                with open(history, 'wb') as f:
                    f.write(saved)


class TestS8Telemetry(SafetyTestBase):
    def test_only_validate_recorded(self):
        secret_words = ['craete', 'Standard_LRSS', 'sizee', 'jmespathbad', 'vm1name']
        cases = ['az vm craete -g rg -n vm1name',
                 'az storage account create -n a -g b --sku Standard_LRSS',
                 'az vm create -n vm1name --sizee 3',
                 "az vm list --query '[jmespathbad'"]
        for case in cases:
            telemetry._session = telemetry.TelemetrySession()
            code, doc, _ = run_validate('--command', case)
            self.assertEqual(code, 0)
            s = telemetry._session
            self.assertEqual(s.raw_command, 'validate')
            self.assertEqual(s.command, 'validate')
            self.assertEqual(s.exceptions, [])
            self.assertEqual(s.error_type, 'None')
            self.assertNotEqual(s.result, 'Failure')
            self.assertTrue(set(s.parameters) <= {'--command', '-o'}, s.parameters)
            dump = repr(vars(s))
            for w in secret_words:
                self.assertNotIn(w, dump)


class TestS9NoValueEcho(SafetyTestBase):
    def test_secret_values_not_echoed(self):
        secrets = ['Pa55w0rd-SECRET-1', 'SECRET-CLIENT-2', 'SECRETSKU3', 'SECRET4', 'SECRETSIZE5',
                   '-Xy9SECRET6z', '-Pa55SECRET7', '-SECRET8sas']
        err = io.StringIO()
        with mock.patch('sys.stderr', err):
            code, doc, text = run_validate(
                '--command',
                'az vm create -g rg -n vm --image Ubuntu2204 --admin-password ' + secrets[0],
                'az vm create -g rg -n vm --image Ubuntu2204 --client-secret ' + secrets[1],
                'az storage account create -n a -g b --sku ' + secrets[2],
                'az vm create -g rg -n vm --image Ubuntu2204 --count ' + secrets[3],
                'az vm create -g rg -n vm --image Ubuntu2204 --sizee ' + secrets[4],
                # Values starting with '-' look like options to argparse.
                'az keyvault secret set --vault-name v -n s --value ' + secrets[5],
                'az vm create -g rg -n vm --image Ubuntu2204 --admin-password ' + secrets[6],
                'az vm create -g rg -n vm --image Ubuntu2204 --client-secret ' + secrets[7])
        self.assertEqual(code, 0)
        for s in secrets:
            self.assertNotIn(s, text)
            self.assertNotIn(s, err.getvalue())
        self.assertEqual([e['code'] for e in doc['results'][5]['errors']], ['MissingValue'])


class TestS10Bounded(SafetyTestBase):
    def test_hanging_metadata_server_is_bounded(self):
        class HangingSession:
            def get(self, url, **_kwargs):
                time.sleep(60)

        _TempStore.fake_session = HangingSession()
        start = time.monotonic()
        try:
            with mock.patch.object(_extmeta, 'TOTAL_BUDGET_SECONDS', 3):
                code, doc, _ = run_validate('--command', "az graph query -q 'x'",
                                            'az vm create -g rg -n vm --image Ubuntu2204 --sizee x')
        finally:
            _TempStore.fake_session = None
        elapsed = time.monotonic() - start
        self.assertEqual(code, 0)
        self.assertLess(elapsed, 20)
        self.assertEqual([r['status'] for r in doc['results']], ['unchecked', 'invalid'])


class TestIsolation(SafetyTestBase):
    def test_inner_output_and_query_do_not_change_result(self):
        code, doc, text = run_validate('--command', "az vm list -o tsv --query '[].name'",
                                       'az group show -n rg -o table')
        self.assertEqual(code, 0)
        self.assertTrue(text.lstrip().startswith('{'))
        self.assertEqual(doc['summary']['valid'], 2)


if __name__ == '__main__':
    unittest.main()
