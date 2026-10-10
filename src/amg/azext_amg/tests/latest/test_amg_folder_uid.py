# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
import json
import unittest
from unittest import mock

from azure.cli.core.azclierror import ArgumentUsageError

from azext_amg import custom, dashboard_v2, migrate, restore, utils


class FolderUidTests(unittest.TestCase):
    def test_folder_uid_from_metadata_or_payload(self):
        cases = [
            ({'meta': {'folderUid': 'nested-folder', 'folderId': 0}}, 'nested-folder'),
            ({'folderUid': 'panel-folder'}, 'panel-folder'),
            ({'folderUid': 'target', 'meta': {'folderUid': 'source'}}, 'target'),
            ({'folderUid': None, 'meta': {'folderUid': 'source'}}, 'source'),
            ({'folderUid': '', 'meta': {'folderUid': 'source'}}, ''),
            ({'meta': {'folderUid': '', 'folderUrl': '/dashboards/f/source/title'}}, ''),
            ({'meta': {'folderUid': 'general'}}, ''),
            ({'folderUid': 'general'}, ''),
            ({'meta': {'folderId': 0}}, ''),
            ({}, ''),
        ]
        for content, expected in cases:
            with self.subTest(content=content):
                self.assertEqual(dashboard_v2.dashboard_folder_uid(content), expected)

    def test_folder_uid_from_legacy_folder_url(self):
        cases = [
            ('/dashboards/f/nested-folder/title', 'nested-folder'),
            ('dashboards/f/nested-folder/title', 'nested-folder'),
            ('https://grafana.example/grafana/dashboards/f/nested-folder/title', 'nested-folder'),
            ('/dashboards/f/nested-folder', 'nested-folder'),
            ('/dashboards/f/nested-folder?orgId=1', 'nested-folder'),
            ('/dashboards/f/general/general', ''),
            ('/dashboards', ''),
            ('https://grafana.example/grafana/dashboards/?orgId=1', ''),
            ('', ''),
        ]
        for folder_url, expected in cases:
            with self.subTest(folder_url=folder_url):
                content = {'meta': {'folderUrl': folder_url}}
                self.assertEqual(dashboard_v2.dashboard_folder_uid(content), expected)

    def test_invalid_folder_metadata_is_rejected(self):
        cases = [
            {'meta': 'invalid'},
            {'meta': None},
            {'meta': []},
            {'meta': 0},
            {'folderUid': 42},
            {'meta': {'folderUid': 42}},
            {'meta': {'folderUrl': 42}},
            {'meta': {'folderUrl': '/dashboards/f/'}},
            {'meta': {'folderUrl': '/not-a-folder'}},
            {'meta': {'folderUrl': '/not-a-folder?next=/dashboards/f/nested-folder/title'}},
            {'meta': {'folderUrl': 'https://[invalid/dashboards/f/nested-folder/title'}},
            {'folderId': 42},
            {'meta': {'folderId': 42}},
        ]
        for content in cases:
            with self.subTest(content=content):
                with self.assertRaises(ArgumentUsageError):
                    dashboard_v2.dashboard_folder_uid(content)

    def test_dynamic_folder_annotation_is_unchanged(self):
        for folder_uid in ('nested-folder', 'general', ''):
            with self.subTest(folder_uid=folder_uid):
                content = {
                    'apiVersion': 'dashboard.grafana.app/v2',
                    'kind': 'Dashboard',
                    'metadata': {'annotations': {'grafana.app/folder': folder_uid}},
                    'spec': {'title': 'Dynamic', 'elements': {}},
                }
                self.assertEqual(dashboard_v2.dashboard_folder_uid(content), folder_uid)


class DashboardFolderTests(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.multiple(
            custom, _try_load_dashboard_definition=mock.DEFAULT, _find_folder=mock.DEFAULT,
            list_data_sources=mock.DEFAULT, _send_request=mock.DEFAULT)
        self.mocks = patcher.start()
        self.addCleanup(patcher.stop)
        self.mocks['_find_folder'].return_value = {'uid': 'nested-folder', 'title': 'Nested'}
        self.mocks['list_data_sources'].return_value = [{'type': 'prometheus', 'uid': 'destination-ds'}]
        self.mocks['_send_request'].return_value = mock.Mock(content=b'{"uid": "dashboard"}')
        self.definition = {
            'dashboard': {
                'title': 'Classic',
                'panels': [],
                '__inputs': [{'name': 'DS_PROMETHEUS', 'type': 'datasource', 'pluginId': 'prometheus'}],
            },
        }
        self.mocks['_try_load_dashboard_definition'].return_value = self.definition

    def test_import_uses_uid_only_folder_response(self):
        self.definition['folderId'] = 42
        custom.import_dashboard(None, 'workspace', self.definition, folder='Nested',
                                resource_group_name='rg', overwrite=True, api_key_or_token='test-token')

        self.mocks['_find_folder'].assert_called_once_with(
            None, 'rg', 'workspace', 'Nested', api_key_or_token='test-token')
        payload = self.mocks['_send_request'].call_args.args[5]
        self.assertEqual(payload['folderUid'], 'nested-folder')
        self.assertNotIn('folderId', payload)
        self.assertTrue(payload['overwrite'])
        self.assertEqual(payload['inputs'][0]['value'], 'destination-ds')

    def test_import_resolves_legacy_folder_id_from_uid(self):
        self.definition.update({'folderId': 42, 'folderUid': 'nested-folder'})
        custom.import_dashboard(None, 'workspace', self.definition)

        payload = self.mocks['_send_request'].call_args.args[5]
        self.assertEqual(payload['folderUid'], 'nested-folder')
        self.assertNotIn('folderId', payload)
        self.mocks['_find_folder'].assert_not_called()

    def test_import_rejects_numeric_only_folder_id(self):
        self.definition['folderId'] = 42
        with self.assertRaises(ArgumentUsageError):
            custom.import_dashboard(None, 'workspace', self.definition)
        self.mocks['_send_request'].assert_not_called()

    def test_import_preserves_default_folder_behavior(self):
        custom.import_dashboard(None, 'workspace', self.definition)
        payload = self.mocks['_send_request'].call_args.args[5]
        self.assertNotIn('folderId', payload)
        self.assertNotIn('folderUid', payload)

    def test_classic_writes_normalize_legacy_root_folder(self):
        for write_dashboard in (custom.import_dashboard, custom._create_dashboard):
            with self.subTest(write_dashboard=write_dashboard.__name__):
                definition = copy.deepcopy(self.definition)
                definition['folderId'] = 0
                self.mocks['_try_load_dashboard_definition'].return_value = definition
                write_dashboard(None, 'workspace', definition)
                payload = self.mocks['_send_request'].call_args.args[5]
                self.assertEqual(payload['folderUid'], '')
                self.assertNotIn('folderId', payload)

    def test_create_overrides_stale_folder_id(self):
        for folder_uid in ('nested-folder', ''):
            with self.subTest(folder_uid=folder_uid):
                definition = copy.deepcopy(self.definition)
                definition.update({'folderId': 42, 'folderUid': 'old-folder'})
                custom._create_dashboard(None, 'workspace', definition, folder_uid=folder_uid)
                payload = self.mocks['_send_request'].call_args.args[5]
                self.assertEqual(payload['folderUid'], folder_uid)
                self.assertNotIn('folderId', payload)

    def test_create_resolves_legacy_folder_id_from_uid(self):
        definition = copy.deepcopy(self.definition)
        definition.update({'folderId': 42, 'meta': {'folderUid': 'nested-folder'}})
        custom._create_dashboard(None, 'workspace', definition)
        payload = self.mocks['_send_request'].call_args.args[5]
        self.assertEqual(payload['folderUid'], 'nested-folder')
        self.assertNotIn('folderId', payload)

    def test_create_rejects_numeric_only_folder_id(self):
        definition = copy.deepcopy(self.definition)
        definition['folderId'] = 42
        with self.assertRaises(ArgumentUsageError):
            custom._create_dashboard(None, 'workspace', definition)
        self.mocks['_send_request'].assert_not_called()

    def test_import_dynamic_dashboard_keeps_uid_annotation_path(self):
        definition = {'title': 'Dynamic', 'elements': {}}
        self.mocks['_try_load_dashboard_definition'].return_value = definition
        with mock.patch.object(custom, '_get_grafana_request_context', return_value=('url', {})), \
                mock.patch.object(custom, 'require_dashboard_v2_api_version', return_value='v2'), \
                mock.patch.object(custom, 'create_dashboard_v2') as create_v2:
            custom.import_dashboard(None, 'workspace', definition, folder='Nested', overwrite=True)
        create_v2.assert_called_once_with(
            'url', {}, definition, 'v2', folder_uid='nested-folder', overwrite=True)
        self.mocks['list_data_sources'].assert_not_called()
        self.mocks['_send_request'].assert_not_called()


class RestoreFolderTests(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.multiple(
            restore, send_grafana_post=mock.DEFAULT, send_grafana_get=mock.DEFAULT,
            send_grafana_patch=mock.DEFAULT, print_styled_text=mock.DEFAULT)
        self.mocks = patcher.start()
        self.addCleanup(patcher.stop)
        self.mocks['send_grafana_post'].return_value = (200, {})
        self.mocks['send_grafana_patch'].return_value = (200, {})
        mapping = mock.patch.dict(restore.uid_mapping, {}, clear=True)
        mapping.start()
        self.addCleanup(mapping.stop)
        folder_lookup = mock.patch.object(
            utils, 'get_folder', side_effect=AssertionError('Numeric folder-ID lookup must not run'))
        folder_lookup.start()
        self.addCleanup(folder_lookup.stop)
        self.dashboard = {'uid': 'dashboard', 'title': 'Classic', 'panels': []}
        self.panel = {'uid': 'panel', 'name': 'Library panel', 'kind': 1, 'model': {}, 'folderId': 42}

    def test_restore_dashboard_preserves_folder_uid(self):
        cases = [
            ({'folderUid': 'nested-folder', 'folderId': 0}, 'nested-folder'),
            ({'folderUid': '', 'folderId': 0}, ''),
            ({'folderUrl': '/dashboards/f/nested-folder/title'}, 'nested-folder'),
            ({'folderUrl': '/dashboards'}, ''),
        ]
        for metadata, expected in cases:
            with self.subTest(metadata=metadata):
                content = {'dashboard': copy.deepcopy(self.dashboard), 'meta': metadata}
                self.assertTrue(restore.create_dashboard('url', content, {}, overwrite=True))
                payload = json.loads(self.mocks['send_grafana_post'].call_args.args[1])
                self.assertEqual(payload['folderUid'], expected)
                self.assertNotIn('folderId', payload)
                self.assertEqual(payload['dashboard'], self.dashboard)

    def test_restore_rejects_unresolvable_folder(self):
        content = {'dashboard': self.dashboard, 'meta': {'folderId': 42}}
        with self.assertRaises(ArgumentUsageError):
            restore.create_dashboard('url', content, {}, overwrite=True)
        self.mocks['send_grafana_post'].assert_not_called()

    def test_restore_library_panel_preserves_folder_uid(self):
        cases = [
            ({'meta': {'folderUid': 'nested-folder'}}, 'nested-folder'),
            ({'folderUid': 'nested-folder'}, 'nested-folder'),
            ({'meta': {'folderUid': ''}}, ''),
            ({'meta': {'folderUrl': '/dashboards/f/nested-folder/title'}}, 'nested-folder'),
            ({'meta': {'folderUrl': '/dashboards'}}, ''),
        ]
        for folder_metadata, expected in cases:
            with self.subTest(folder_metadata=folder_metadata):
                panel = copy.deepcopy(self.panel)
                panel.update(folder_metadata)
                self.assertTrue(restore.create_library_panel('url', panel, {}, overwrite=True))
                payload = json.loads(self.mocks['send_grafana_post'].call_args.args[1])
                self.assertEqual(payload['folderUid'], expected)
                self.assertNotIn('folderId', payload)

    def test_library_panel_overwrite_updates_folder_uid(self):
        self.mocks['send_grafana_post'].return_value = (400, {'message': 'name or UID already exists'})
        self.mocks['send_grafana_get'].return_value = (200, {'result': {'version': 7}})
        for folder_uid in ('nested-folder', ''):
            with self.subTest(folder_uid=folder_uid):
                panel = copy.deepcopy(self.panel)
                panel['meta'] = {'folderUid': folder_uid}
                self.assertTrue(restore.create_library_panel('url', panel, {}, overwrite=True))
                payload = json.loads(self.mocks['send_grafana_patch'].call_args.args[1])
                self.assertEqual(payload['folderUid'], folder_uid)
                self.assertEqual(payload['version'], 7)
                self.assertNotIn('folderId', payload)

    def test_library_panel_without_overwrite_does_not_patch(self):
        self.mocks['send_grafana_post'].return_value = (400, {'message': 'name or UID already exists'})
        panel = copy.deepcopy(self.panel)
        panel['meta'] = {'folderUid': 'nested-folder'}
        self.assertFalse(restore.create_library_panel('url', panel, {}, overwrite=False))
        self.mocks['send_grafana_patch'].assert_not_called()

    def test_restore_dynamic_dashboard_preserves_folder_annotation(self):
        content = {
            'apiVersion': 'dashboard.grafana.app/v2',
            'kind': 'Dashboard',
            'metadata': {'name': 'dynamic', 'annotations': {'grafana.app/folder': 'nested-folder'}},
            'spec': {'title': 'Dynamic', 'elements': {}},
        }
        with mock.patch.object(restore, 'require_dashboard_v2_api_version', return_value='v2'), \
                mock.patch.object(restore, 'create_dashboard_v2') as create_v2:
            self.assertTrue(restore.create_dashboard('url', content, {}, overwrite=True))
        create_v2.assert_called_once_with('url', {}, content, 'v2', overwrite=True)
        self.assertEqual(content['metadata']['annotations']['grafana.app/folder'], 'nested-folder')
        self.mocks['send_grafana_post'].assert_not_called()

    def test_migration_uses_uid_based_restore_for_dashboard_and_library_panel(self):
        dashboard = {
            'dashboard': dict(self.dashboard, panels=[{'libraryPanel': {'uid': 'panel'}}]),
            'meta': {'folderUid': 'nested-folder', 'folderTitle': 'Nested'},
        }
        panel = copy.deepcopy(self.panel)
        panel['meta'] = {'folderUid': 'nested-folder', 'folderName': 'Nested'}
        with mock.patch.object(migrate, 'check_library_panel_exists', return_value=False), \
                mock.patch.object(migrate, 'check_dashboard_exists', return_value=False):
            result = migrate._migrate_library_panels_and_dashboards(
                [dashboard], [panel], 'url', {}, dry_run=False, overwrite=True)

        self.assertEqual(result[0], {'Nested': ['Library panel']})
        self.assertEqual(result[2], {'Nested': ['Classic']})
        self.assertEqual(self.mocks['send_grafana_post'].call_count, 2)
        for call in self.mocks['send_grafana_post'].call_args_list:
            payload = json.loads(call.args[1])
            self.assertEqual(payload['folderUid'], 'nested-folder')
            self.assertNotIn('folderId', payload)

    def test_migration_filters_library_panels_using_canonical_folder_uid(self):
        panels = [
            {'uid': 'nested', 'folderUid': 'nested-folder', 'meta': {'folderName': 'Nested'}},
            {'uid': 'root', 'meta': {'folderUid': 'general', 'folderName': 'General'}},
            {'uid': 'other', 'meta': {'folderUid': 'other-folder', 'folderName': 'Other'}},
            {'uid': 'legacy', 'meta': {'folderUrl': '/dashboards/f/nested-folder/title'}},
        ]
        source_folders = [({'uid': 'nested-folder', 'title': 'Nested'}, {})]
        for excluded_folders, selected in ((None, [panels[0], panels[1], panels[3]]),
                                            (['General'], [panels[0], panels[3]])):
            with self.subTest(excluded_folders=excluded_folders), mock.patch.multiple(
                    migrate, get_all_datasources=mock.Mock(return_value=[]),
                    get_all_folders=mock.Mock(side_effect=[source_folders, []]),
                    get_all_dashboards=mock.Mock(return_value=[]),
                    get_all_library_panels=mock.Mock(return_value=panels),
                    get_all_snapshots=mock.Mock(return_value=[]),
                    get_all_annotations=mock.Mock(return_value=[]),
                    _migrate_datasources=mock.Mock(return_value=([], [])),
                    _migrate_folders=mock.Mock(return_value=([], [])),
                    _migrate_library_panels_and_dashboards=mock.DEFAULT,
                    _migrate_snapshots=mock.Mock(return_value=({}, {})),
                    _migrate_annotations=mock.Mock(return_value=([], [])),
                    print_styled_text=mock.DEFAULT) as patched:
                patched['_migrate_library_panels_and_dashboards'].return_value = ({}, {}, {}, {})
                migrate.migrate('source', {}, 'destination', {}, dry_run=True, overwrite=False,
                                folders_to_exclude=excluded_folders)
                self.assertEqual(
                    patched['_migrate_library_panels_and_dashboards'].call_args.args[1], selected)


if __name__ == '__main__':
    unittest.main()
