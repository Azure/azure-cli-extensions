# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=protected-access
"""Published command metadata: uninstalled extensions and overlays.

Every response comes from a fake server with synthetic metadata; the network is blocked."""

import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

from azext_validate import _extmeta, _sandbox, _validator
from azext_validate.tests.latest import _fake_metadata
from azext_validate.tests.latest._base import TempStore, ValidateTestBase, block_network, run_validate, unblock_network

_EXT_URL = _extmeta.META_BASE_URL

_GRAPH = {'module_name': 'resource-graph', 'name': 'resource-graph', 'commands': {'graph query': {
    'name': 'graph query', 'parameters': [
        {'name': 'graph_query', 'options': ['--graph-query', '--q', '-q'], 'required': True},
        {'name': 'first', 'options': ['--first'], 'type': 'int'},
        {'name': 'skip_token', 'options': ['--skip-token'], 'type': 'string'},
        {'name': 'mode', 'options': ['--mode'], 'choices': ['Fast', 'Full']},
        {'name': 'allow_partial', 'options': ['--allow-partial'], 'type': 'bool', 'nargs': '?',
         'choices': ['false', 'true']},
        {'name': 'include_hidden', 'options': ['--include-hidden'], 'type': 'bool'}]}, 'graph build': {
    'name': 'graph build', 'parameters': [
        {'name': 'registry_name', 'options': ['--registry', '-r'], 'required': True},
        {'name': 'tag', 'options': ['--tag', '-t']},
        {'name': 'no_push', 'options': ['--no-push']},
        {'name': 'quiet', 'options': ['--quiet'], 'type': 'bool'},
        {'name': 'source_location', 'required': True}]}, 'graph old': {
    'name': 'graph old', 'deprecate_info': {'target': 'graph old', 'redirect': 'graph query'}, 'parameters': [
        {'name': 'graph_query', 'options': ['--graph-query', '-q'], 'required': True}]}}, 'sub_groups': {}}
_AKS_PREVIEW = {'module_name': 'aks-preview', 'name': 'aks-preview', 'commands': {'aks create': {
    'name': 'aks create', 'parameters': [
        {'name': 'resource_group_name', 'options': ['--resource-group', '-g'], 'required': True},
        {'name': 'name', 'options': ['--name', '-n'], 'required': True},
        {'name': 'node_count', 'options': ['--node-count', '-c'], 'type': 'int'},
        {'name': 'preview_count', 'options': ['--preview-count', '-j'], 'type': 'int',
         'options_deprecate_info': [{'target': '--preview-cnt', 'redirect': '--preview-count'}]},
        {'name': 'preview_tier', 'options': ['--preview-tier', '--tier-preview'], 'choices': ['Basic', 'Premium'],
         'options_deprecate_info': [{'target': '--tier-preview', 'redirect': '--preview-tier'}]},
        {'name': 'enable_preview_feature', 'options': ['--enable-preview-feature']}]}}, 'sub_groups': {}}
_INDEX = {'graph': {'query': 'resource-graph', 'build': 'resource-graph', 'old': 'resource-graph'},
          'aks': {'create': 'aks-preview'}}


def _responses(**extra):
    responses = {
        _extmeta.INDEX_URL: _INDEX,
        _EXT_URL + '/ext-resource-graph/version_list.txt':
            'az_resource-graph_meta_2.1.0.json\naz_resource-graph_meta_2.2.0b1.json\naz_resource-graph_meta_2.1.1.json\n',
        _EXT_URL + '/ext-resource-graph/az_resource-graph_meta_2.1.1.json': _GRAPH,
        _EXT_URL + '/ext-resource-graph/az_resource-graph_meta_2.1.0.json': _GRAPH,
        _EXT_URL + '/ext-aks-preview/version_list.txt': 'az_aks-preview_meta_9.0.0b1.json\n',
        _EXT_URL + '/ext-aks-preview/az_aks-preview_meta_9.0.0b1.json': _AKS_PREVIEW,
    }
    responses.update(extra)
    return responses


def setUpModule():
    block_network()


def tearDownModule():
    unblock_network()


class MetadataTestBase(ValidateTestBase):
    responses = None

    def setUp(self):
        super().setUp()
        self.session = _fake_metadata.FakeSession(self.responses if self.responses is not None else _responses())
        TempStore.fake_session = self.session

    def tearDown(self):
        TempStore.fake_session = None
        super().tearDown()

    def one(self, command, *extra):
        code, doc, _ = run_validate('--command', command, *extra)
        self.assertEqual(code, 0)
        return doc, doc['results'][0]


class TestUninstalledExtensions(MetadataTestBase):
    def test_latest_stable_version_is_used(self):
        doc, r = self.one("az graph query -q 'x' --first 5")
        self.assertEqual((r['status'], r['source'], r['requiresExtension']),
                         ('valid', 'extension:resource-graph', 'resource-graph'))
        self.assertEqual(doc['versions']['extensionMetadata'], {'resource-graph': '2.1.1'})
        self.assertEqual([i['code'] for i in r['info']], ['ExtensionNotInstalled', 'MetadataLimits'])

    def test_offline_without_cache(self):
        _, r = self.one("az graph query -q 'x'", '--offline')
        self.assertEqual(r['status'], 'unchecked')
        self.assertEqual(self.session.urls, [])

    def test_overlay_resolves_extension_parameter(self):
        _, r = self.one('az aks create -g rg -n a --enable-preview-feature')
        self.assertEqual((r['status'], r['source'], r['requiresExtension']), ('valid', 'core', 'aks-preview'))
        self.assertEqual([w['code'] for w in r['warnings']], ['RequiresExtension'])
        self.assertEqual(r['warnings'][0]['parameters'], ['--enable-preview-feature'])

    def test_overlay_keeps_value_errors(self):
        _, r = self.one('az aks create -g rg -n a --enable-preview-feature --node-count abc')
        self.assertEqual(r['status'], 'invalid')
        self.assertEqual([e['code'] for e in r['errors']], ['InvalidValue'])

    def test_overlay_checks_values_of_extension_only_options(self):
        # Core rejects options only the extension has, so it can't check their values; metadata's verdict stands.
        for command, code, param in (('az aks create -g rg -n a --preview-count', 'MissingValue', '--preview-count'),
                                     ('az aks create -g rg -n a -j abc', 'InvalidValue', '--preview-count'),
                                     ('az aks create -g rg -n a -jabc', 'InvalidValue', '--preview-count'),
                                     ('az aks create -g rg -n a -jabc --enable-preview-feature', 'InvalidValue',
                                      '--preview-count'),
                                     ('az aks create -g rg -n a --enable-preview-feature -jabc', 'InvalidValue',
                                      '--preview-count'),
                                     ('az aks create -g rg -n a --preview-cnt abc', 'InvalidValue', '--preview-count'),
                                     ('az aks create -g rg -n a --preview-t Gold', 'InvalidChoice', '--preview-tier')):
            _, r = self.one(command)
            self.assertEqual((r['status'], r['source'], r['requiresExtension']), ('invalid', 'core', 'aks-preview'),
                             command)
            self.assertEqual([(e['code'], e['parameter']) for e in r['errors']], [(code, param)], command)
            self.assertEqual([w['code'] for w in r['warnings']], ['RequiresExtension'])
        _, r = self.one('az aks create -g rg -n a -j 3 --preview-tier premium')
        self.assertEqual((r['status'], r['requiresExtension']), ('valid', 'aks-preview'))
        # A deprecated name may also be listed in options; its abbreviation is still unique.
        _, r = self.one('az aks create -g rg -n a --tier-p Basic')
        self.assertEqual((r['status'], r['requiresExtension']), ('valid', 'aks-preview'))
        # An option neither knows stays an error, even where metadata may read it as a missing value.
        _, r = self.one('az aks create -g rg -n a --preview-count --bogus')
        self.assertEqual([(e['code'], e.get('parameter') or e.get('parameters')) for e in r['errors']],
                         [('UnrecognizedArgument', ['--bogus']), ('MissingValue', '--preview-count')])
        self.assertEqual(r['warnings'][0]['parameters'], ['--preview-count'])
        # argparse counts option strings, so a prefix of two names of one parameter is ambiguous.
        _, r = self.one('az aks create -g rg -n a --preview-c 3')
        self.assertEqual([(e['code'], e.get('parameters')) for e in r['errors']],
                         [('UnrecognizedArgument', ['--preview-c'])])

    def test_installed_extension_not_rechecked(self):
        with mock.patch.object(_validator.Validator, 'installed_extensions', return_value={'resource-graph': '2.1.0'}):
            _, r = self.one("az graph query -q 'x'")
        # The local parse already had every installed extension; its verdict stands.
        self.assertEqual(r['status'], 'invalid')
        self.assertFalse([u for u in self.session.urls if '/ext-' in u])

    def test_value_checked_from_metadata(self):
        _, r = self.one("az graph query -q 'x' --first abc")
        self.assertEqual((r['status'], r['source']), ('invalid', 'extension:resource-graph'))
        self.assertEqual([(e['code'], e['parameter']) for e in r['errors']], [('InvalidValue', '--first')])

    def test_typed_option_needs_value(self):
        # Metadata shows these options take a value, so a missing one is reported the way core reports it.
        _, core = self.one('az vm create -g rg -n vm --image x --count')
        self.assertEqual([(e['code'], e['parameter']) for e in core['errors']], [('MissingValue', '--count')])
        for command, param in (("az graph query -q 'x' --first", '--first'),
                               ("az graph query -q 'x' --skip-token", '--skip-token'),
                               ("az graph query -q 'x' --mode", '--mode')):
            _, r = self.one(command)
            self.assertEqual((r['status'], r['source']), ('invalid', 'extension:resource-graph'), command)
            self.assertEqual([(e['code'], e['parameter']) for e in r['errors']], [('MissingValue', param)])
            self.assertEqual(r['errors'][0]['message'], core['errors'][0]['message'].replace('--count', param))
        _, core = self.one('az group create -n rg -l')
        _, r = self.one('az graph query -q')
        self.assertEqual([e['code'] for e in r['errors']], [e['code'] for e in core['errors']])
        self.assertEqual(r['errors'][0]['parameter'], '--graph-query')

    def test_flags_need_no_value(self):
        for command in ("az graph query -q 'x' --allow-partial", "az graph query -q 'x' --allow-partial false",
                        "az graph query -q 'x' --include-hidden", "az graph query --include-hidden -q 'x'",
                        'az graph build -r reg --no-push .'):
            _, r = self.one(command)
            self.assertEqual((r['status'], r['source']), ('valid', 'extension:resource-graph'), command)

    def test_flag_before_positional(self):
        # Metadata doesn't say --no-push is a flag, so it may take the positional '.' as its value.
        _, r = self.one('az graph build -r reg -t app:v1 --no-push .')
        self.assertEqual(r['status'], 'valid', r)
        self.assertIn('MetadataLimits', [i['code'] for i in r['info']])
        # A bool option without nargs may be a flag too.
        _, r = self.one('az graph build -r reg --quiet .')
        self.assertEqual(r['status'], 'valid', r)
        # Without an option that might be a flag, a missing positional is still reported.
        _, r = self.one('az graph build -r reg')
        self.assertEqual([(e['code'], e['parameters']) for e in r['errors']],
                         [('MissingRequiredArgument', ['<SOURCE_LOCATION>'])])

    def test_subcommand_list_skips_deprecated(self):
        _, r = self.one('az graph zzzz -q x')
        self.assertEqual((r['status'], r['source']), ('invalid', 'extension:resource-graph'))
        self.assertEqual(r['errors'][0]['suggestions'], ['az graph build', 'az graph query'])

    def test_bad_cache_file_is_ignored(self):
        os.makedirs(os.path.join(self.tmp, 'cache'), exist_ok=True)
        with open(os.path.join(self.tmp, 'cache', 'ext-resource-graph.json'), 'w', encoding='utf-8') as f:
            json.dump({'commands': {}}, f)
        _, r = self.one("az graph query -q 'x'")
        self.assertEqual(r['status'], 'valid')


# Commands of synthetic extensions that can't be installed anywhere (machines may have real extensions).
_SYNTH = {'module_name': 'azv-synth', 'name': 'azv-synth', 'commands': {'azvsynth query': {
    'name': 'azvsynth query', 'parameters': [{'name': 'first', 'options': ['--first'], 'type': 'int'}]}},
    'sub_groups': {}}

_PROBE_LOADER = """
from azure.cli.core import AzCommandsLoader


class ProbeLoader(AzCommandsLoader):
    def load_command_table(self, args):
        with open({outside!r}, encoding='utf-8') as f:
            f.read()
        return self.command_table

    def load_arguments(self, command):
        pass


COMMAND_LOADER_CLS = ProbeLoader
"""

_TEMPDIR_LOADER = """
import tempfile

from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands import AzCliCommand


def _thing():
    return None


class ProbeLoader(AzCommandsLoader):
    def load_command_table(self, args):
        tempfile.gettempdir()
        self.command_table['azvprobe thing'] = AzCliCommand(self, 'azvprobe thing', _thing)
        return self.command_table

    def load_arguments(self, command):
        pass


COMMAND_LOADER_CLS = ProbeLoader
"""

_INDEX_SESSIONS = ('INDEX', 'EXTENSION_INDEX', 'HELP_INDEX', 'EXTENSION_HELP_INDEX')


class _BlockedLoadBase(MetadataTestBase):
    """An installed extension reads a file outside the sandbox while loading, as one preinstalled in some
    environments does. Core loads every installed extension for a top-level command it doesn't know."""
    responses = _responses(**{
        _extmeta.INDEX_URL: dict(_INDEX, azvsynth={'query': 'azv-synth'}, azvmissing={'list': 'azv-missing'},
                                 azvprobe={'thing': 'azvprobe'}),
        _EXT_URL + '/ext-azv-synth/version_list.txt': 'az_azv-synth_meta_1.0.0.json\n',
        _EXT_URL + '/ext-azv-synth/az_azv-synth_meta_1.0.0.json': _SYNTH})
    # Core's own index of installed extensions, as a normal az run would have saved it.
    local_index = {'azvprobe': ['azext_azvprobe'], 'validate': ['azext_validate']}
    probe_loader = _PROBE_LOADER

    def setUp(self):
        super().setUp()
        from azure.cli.core import __version__ as cli_version, extension as ext_mod
        from azure.cli.core import _session
        from azure.cli.core._session import EXTENSION_INDEX, Session
        self.outside = tempfile.mkdtemp(prefix='azvalidate-outside-')
        secret = os.path.join(self.outside, 'probe.txt')
        with open(secret, 'w', encoding='utf-8') as f:
            f.write('PROBE-SENTINEL')
        sys_dir = os.path.join(self.tmp, 'sys-extensions')
        pkg = os.path.join(sys_dir, 'azvprobe', 'azext_azvprobe')
        os.makedirs(pkg)
        os.makedirs(os.path.join(sys_dir, 'azvprobe', 'azvprobe-0.0.1.dist-info'))
        with open(os.path.join(pkg, '__init__.py'), 'w', encoding='utf-8') as f:
            f.write(self.probe_loader.format(outside=secret))
        with open(os.path.join(pkg, 'azext_metadata.json'), 'w', encoding='utf-8') as f:
            json.dump({'azext.minCliCoreVersion': '2.0.0'}, f)
        with open(os.path.join(sys_dir, 'azvprobe', 'azvprobe-0.0.1.dist-info', 'METADATA'), 'w',
                  encoding='utf-8') as f:
            f.write('Metadata-Version: 2.1\nName: azvprobe\nVersion: 0.0.1\n')
        self.saved = []

        index_sessions = {id(getattr(_session, n)): n for n in _INDEX_SESSIONS if hasattr(_session, n)}

        def spy_save(session):  # never writes the real config dir; records saves after a blocked operation
            guard = _sandbox._state.guard
            if guard is not None and guard.violations:
                self.saved.append(index_sessions.get(id(session), os.path.basename(session.filename or '')))
        self.extension_index = EXTENSION_INDEX
        self.patches = [mock.patch.object(ext_mod, 'EXTENSIONS_SYS_DIR', sys_dir),
                        mock.patch.object(Session, 'save', spy_save),
                        mock.patch.object(EXTENSION_INDEX, 'load', lambda *_a, **_k: None),
                        mock.patch.object(EXTENSION_INDEX, 'data', {
                            'version': cli_version, 'cloudProfile': 'latest',
                            'commandIndex': json.loads(json.dumps(self.local_index))})]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        sys.modules.pop('azext_azvprobe', None)
        sys.path[:] = [x for x in sys.path if 'sys-extensions' not in x]
        shutil.rmtree(self.outside, ignore_errors=True)
        super().tearDown()


class TestBlockedExtensionLoad(_BlockedLoadBase):
    def test_uninstalled_extension_commands_still_checked(self):
        code, doc, text = run_validate('--command', 'az azvsynth query --first abc', 'az azvmissing list',
                                       'az azvprobe thing', 'az vm craete -g rg')
        self.assertEqual(code, 0)
        got = [(r['status'], ([e['code'] for e in r['errors']] or [r.get('reason', {}).get('code')])[0])
               for r in doc['results']]
        self.assertEqual(got, [('invalid', 'InvalidValue'),          # checked against published metadata
                               ('unchecked', 'ExtensionNotPublished'),
                               ('unchecked', 'InternalError'),       # the installed extension that didn't load
                               ('invalid', 'UnknownCommand')])       # core commands don't load extensions
        self.assertEqual(doc['results'][0]['source'], 'extension:azv-synth')
        self.assertNotIn('PROBE-SENTINEL', text)

    def test_no_partial_index_saved_or_kept(self):
        before = json.dumps(self.extension_index.data, sort_keys=True)
        run_validate('--command', 'az azvmissing list')
        self.assertFalse([n for n in self.saved if n in _INDEX_SESSIONS], self.saved)
        self.assertEqual(json.dumps(self.extension_index.data, sort_keys=True), before)


class TestBlockedExtensionInCoreGroup(_BlockedLoadBase):
    """The blocked extension adds commands to a core group; a partial index must not hide that later."""
    local_index = {'vm': ['azext_azvprobe'], 'validate': ['azext_validate']}

    def test_later_command_in_same_run(self):
        _, doc, _ = run_validate('--command', 'az azvmissing list', 'az vm azvprobe-cmd')
        r = doc['results'][1]
        self.assertEqual((r['status'], r['reason']['code']), ('unchecked', 'InternalError'))


class TestExtensionUsingTempdir(_BlockedLoadBase):
    """An installed extension calls tempfile.gettempdir() while loading, as some do at import time. On first
    use tempfile creates and deletes a probe file, which the sandbox would block."""
    probe_loader = _TEMPDIR_LOADER

    def test_checked_locally(self):
        with mock.patch.object(tempfile, 'tempdir', None):
            _, doc, _ = run_validate('--command', 'az azvprobe thing')
        r = doc['results'][0]
        self.assertEqual((r['status'], r.get('source')), ('valid', 'extension:azvprobe'), r)

    def test_no_usable_temp_directory(self):
        missing = os.path.join(self.tmp, 'no-such-dir')
        with mock.patch.object(tempfile, 'tempdir', None), \
                mock.patch.object(tempfile, '_candidate_tempdir_list', lambda: [missing]):
            code, doc, _ = run_validate('--command', 'az vm list')
        self.assertEqual((code, doc['results'][0]['status']), (0, 'valid'))


class TestBlockedExtensionNamedDifferently(_BlockedLoadBase):
    """The public index names another extension for a command the blocked (unpublished) one provides."""
    responses = _responses(**{_extmeta.INDEX_URL: dict(_INDEX, azvprobe={'thing': 'resource-graph'})})

    def test_stays_unchecked(self):
        _, doc, _ = run_validate('--command', 'az azvprobe thing')
        r = doc['results'][0]
        self.assertEqual((r['status'], r['reason']['code']), ('unchecked', 'InternalError'))


class TestVersionPicking(unittest.TestCase):
    def test_latest_stable_else_latest_preview(self):
        listing = 'az_x_meta_1.0.0.json az_x_meta_1.1.0b1.json az_x_meta_1.0.1.json az_y_meta_9.0.0.json'
        self.assertEqual(_extmeta._pick_version('x', listing)[0], '1.0.1')
        self.assertEqual(_extmeta._pick_version('x', 'az_x_meta_1.1.0b1.json az_x_meta_1.1.0b2.json')[0], '1.1.0b2')


if __name__ == '__main__':
    unittest.main()
