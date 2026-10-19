# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Offline public-command contracts, captured after real AAZ HTTP serialization.

No recordings, cached accounts, test authentication, tokens, or Azure resources.
Expected JSON is authored here, never derived with the production converter.
The compatibility fixtures deliberately freeze the legacy mapping-key behavior;
they do not claim that behavior is correct for the service.
"""

from contextlib import ExitStack, redirect_stderr, redirect_stdout
from copy import deepcopy
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlsplit

from azure.cli.core import MainCommandsLoader
from azure.cli.core.cloud import AZURE_PUBLIC_CLOUD
from azure.cli.core.commands import ExtensionCommandSource
from azure.cli.core.mock import DummyCli
from azure.core.pipeline import PipelineContext, PipelineResponse
from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.pipeline.transport import HttpRequest, HttpResponse

from azext_dataprotection import DataProtectionClientCommandsLoader
# The legacy modules refer to each other. Use the real loader's helper-first
# import order, not a custom-first import which introduces a circular import.
from azext_dataprotection.manual import helpers as helper
from azext_dataprotection.manual import custom


SUBSCRIPTION = '11111111-1111-1111-1111-111111111111'
TENANT = '22222222-2222-2222-2222-222222222222'
AUX_TENANT = '33333333-3333-3333-3333-333333333333'
RG = '/subscriptions/' + SUBSCRIPTION + '/resourceGroups/restore-tests'
PROVIDER = RG + '/providers/Microsoft.DataProtection'
INSTANCE = PROVIDER + '/backupVaults/vault/backupInstances/instance'
TARGET = RG + '/providers/Microsoft.DocumentDB/databaseAccounts/empty-target'
UAMI = RG + '/providers/Microsoft.ManagedIdentity/userAssignedIdentities/restore-identity'
OTHER_UAMI = RG + '/providers/Microsoft.ManagedIdentity/userAssignedIdentities/other-identity'
SAMI_PRINCIPAL = '44444444-4444-4444-4444-444444444444'
UAMI_PRINCIPAL = '55555555-5555-5555-5555-555555555555'
ROLE_ID = '/subscriptions/' + SUBSCRIPTION + '/providers/Microsoft.Authorization/roleDefinitions/' + TENANT
LOCATION = 'eastasia'
SECONDARY = 'southeastasia'
RECOVERY_POINT = 'synthetic-committed-recovery-point'
POINT_IN_TIME = '2026-10-01T00:00:00'
SELECTORS = ['Z_last', 'DB/Col', 'db/col', 'wild*/{literal}, value',
             '数据库/容器', 'é', 'e\u0301', ' db / col ', 'comma,name']
ACCOUNT = {
    'id': SUBSCRIPTION, 'tenantId': TENANT, 'name': 'Offline command contract',
    'state': 'Enabled', 'isDefault': True, 'environmentName': 'AzureCloud',
    'user': {'name': 'offline@example.invalid', 'type': 'user'},
}
JOB = {'objectType': 'OperationJobExtendedInfo', 'jobId': 'offline-job'}
IDENTITIES = (
    ('omitted', [], None),
    ('system', ['--mi-system-assigned', 'true'], {'useSystemAssignedIdentity': True}),
    ('user-alone', ['--uami', UAMI],
     {'useSystemAssignedIdentity': False, 'userAssignedIdentityArmUrl': UAMI}),
    ('user-false', ['--uami', UAMI, '--mi-system-assigned', 'false'],
     {'useSystemAssignedIdentity': False, 'userAssignedIdentityArmUrl': UAMI}),
)


def golden_config(wire=False, names=None):
    names = deepcopy(SELECTORS if names is None else names)
    if wire:
        return {'objectType': 'GenericRestoreDatasourceCriteria', 'resourceSelectors': {
            'objectType': 'ResourceListSelectionCriteria', 'resourceIdentifiers': names}}
    return {'object_type': 'GenericRestoreDatasourceCriteria', 'resource_selectors': {
        'object_type': 'ResourceListSelectionCriteria', 'resource_identifiers': names}}


def golden_datasource(resource_id=TARGET, wire=False, resource_type='Microsoft.DocumentDB/databaseAccounts',
                      datasource_type='Microsoft.DocumentDB/databaseAccounts', uri=None, is_set=False):
    """Explicit client and wire schema, independent of all production helpers."""
    uri = resource_id if uri is None else uri
    if wire:
        return {'objectType': 'DatasourceSet' if is_set else 'Datasource',
                'datasourceType': datasource_type, 'resourceID': resource_id,
                'resourceName': resource_id.split('/')[-1], 'resourceType': resource_type,
                'resourceUri': uri, 'resourceLocation': LOCATION}
    return {'object_type': 'DatasourceSet' if is_set else 'Datasource',
            'datasource_type': datasource_type, 'resource_id': resource_id,
            'resource_name': resource_id.split('/')[-1], 'resource_type': resource_type,
            'resource_uri': uri, 'resource_location': LOCATION}


def golden_restore(item=True, identity=None, wire=False, names=None):
    if wire:
        target = {'objectType': 'ItemLevelRestoreTargetInfo' if item else 'RestoreTargetInfo',
                  'restoreLocation': LOCATION, 'recoveryOption': 'FailIfExists',
                  'datasourceInfo': golden_datasource(wire=True)}
        if item:
            target['restoreCriteria'] = [golden_config(wire=True, names=names)]
        result = {'objectType': 'AzureBackupRecoveryPointBasedRestoreRequest',
                  'recoveryPointId': RECOVERY_POINT, 'sourceDataStoreType': 'VaultStore',
                  'restoreTargetInfo': target}
        if identity is not None:
            result['identityDetails'] = deepcopy(identity)
        return result
    target = {'object_type': 'ItemLevelRestoreTargetInfo' if item else 'RestoreTargetInfo',
              'restore_location': LOCATION, 'recovery_option': 'FailIfExists',
              'datasource_info': golden_datasource()}
    if item:
        target['restore_criteria'] = [golden_config(names=names)]
    result = {'object_type': 'AzureBackupRecoveryPointBasedRestoreRequest',
              'recovery_point_id': RECOVERY_POINT, 'source_data_store_type': 'VaultStore',
              'restore_target_info': target}
    if identity is not None:
        result['identity_details'] = deepcopy(identity)
    return result


class ExtensionOnlyLoader(MainCommandsLoader):
    """Keep core argument orchestration without installed extension discovery."""

    def load_command_table(self, args):
        self.command_table.clear()
        self.command_group_table.clear()
        self.cmd_to_loader_map.clear()
        self.loaders.clear()
        loader = DataProtectionClientCommandsLoader(cli_ctx=self.cli_ctx)
        table = loader.load_command_table(args)
        self.loaders.append(loader)
        self.command_table.update(table)
        self.command_group_table.update(loader.command_group_table)
        self.cmd_to_loader_map.update({name: [loader] for name in table})
        for command in table.values():
            command.command_source = ExtensionCommandSource(
                extension_name='dataprotection', overrides_command=False, preview=True, experimental=False)
        return self.command_table


class NeverTokenCredential:
    def __init__(self):
        self.get_token = Mock(side_effect=AssertionError('Token acquisition is forbidden'))


class JsonHttpResponse(HttpResponse):
    def __init__(self, request, status, payload):
        super().__init__(request, None)
        self.status_code = status
        self.reason = {200: 'OK', 202: 'Accepted'}[status]
        # No polling headers: sync fixtures finish immediately, never live-poll.
        self.headers = {'Content-Type': 'application/json'}
        self.content_type = 'application/json'
        self._body = json.dumps(payload, ensure_ascii=False).encode('utf-8')

    def body(self):
        return self._body

    def text(self, encoding=None):
        return self._body.decode(encoding or 'utf-8')


class PublicCommandTransportCase(unittest.TestCase):
    """Reusable public parser -> manual handler -> AAZ -> HttpRequest harness."""

    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.directory = self.stack.enter_context(tempfile.TemporaryDirectory())
        self.stack.enter_context(patch.dict(os.environ, {
            'AZURE_CONFIG_DIR': self.directory,
            'AZURE_CORE_COLLECT_TELEMETRY': 'no',
            'AZURE_CORE_CHECK_VERSION': 'no',
            'AZURE_EXTENSION_USE_DYNAMIC_INSTALL': 'no',
            'AZURE_TEST_RUN_LIVE': 'false',
        }))
        # DummyCli imports this constant inside __init__; never copy user caches.
        self.start_patch('azure.cli.core._config.GLOBAL_CONFIG_DIR', new=self.directory)
        cloud = deepcopy(AZURE_PUBLIC_CLOUD)
        # The cloud constant has no profile until ordinary CLI startup sets one.
        cloud.profile = 'latest'
        self.start_patch('azure.cli.core.cloud.get_active_cloud',
                         return_value=cloud)
        # Invalid-command suggestions are unrelated to restore and otherwise
        # contact Aladdin even when telemetry is disabled. Keep all IO guards.
        self.start_patch('azure.cli.core.command_recommender.CommandRecommender.provide_recommendations',
                         return_value=[])
        self.start_patch('azure.cli.core.util.handle_version_update')
        self.start_patch('azure.cli.core.util.show_updates_available')
        self.start_patch('azure.cli.core._profile.Profile.load_cached_subscriptions',
                         return_value=[deepcopy(ACCOUNT)])
        self.start_patch('azure.cli.core._profile.Profile.get_subscription',
                         return_value=deepcopy(ACCOUNT))
        self.credential = NeverTokenCredential()
        self.login = self.start_patch('azure.cli.core._profile.Profile.get_login_credentials',
                                     return_value=(self.credential, SUBSCRIPTION, TENANT))
        self.guards = [self.start_patch(target, side_effect=AssertionError('Forbidden IO: ' + target))
                       for target in (
                           'requests.sessions.Session.request',
                           'socket.socket.connect', 'socket.socket.connect_ex',
                           'socket.create_connection', 'socket.getaddrinfo',
                           'socket.gethostbyname', 'socket.gethostbyname_ex',
                           'azure.cli.core._profile.Profile.get_raw_token',
                           'azext_dataprotection.manual.custom.get_mgmt_service_client',
                           'azext_dataprotection.manual.helpers.get_mgmt_service_client',
                           'azext_dataprotection.manual.custom.BackupVaultGet',
                           'azext_dataprotection.manual.helpers.list_role_assignments',
                           'azext_dataprotection.manual.helpers.create_role_assignment',
                           'azext_dataprotection.manual.custom.list_role_assignments',
                           'azext_dataprotection.manual.custom.create_role_assignment',
                           'azext_dataprotection.manual.backupcenter_helper.get_selected_subscription',
                       )]
        self.pending = []
        self.requests = []
        self.send = self.start_patch('azure.cli.core.aaz._client.AAZBaseClient.send_request',
                                    autospec=True, side_effect=self.capture_request)

    def start_patch(self, target, **kwargs):
        return self.stack.enter_context(patch(target, **kwargs))

    def tearDown(self):
        self.assertEqual(self.pending, [], 'Expected HTTP request was not issued')
        self.credential.get_token.assert_not_called()
        for guard in self.guards:
            guard.assert_not_called()

    def capture_request(self, client, request, stream=False, **kwargs):
        # This boundary receives the actual serialized azure.core HttpRequest;
        # do not replace AAZ content, make_request, handlers or LRO construction.
        self.assertIsInstance(request, HttpRequest)
        self.requests.append(request)
        self.assertTrue(self.pending, 'Unexpected HTTP (including LRO polling): ' + request.url)
        path, api_version, body, status = self.pending.pop(0)
        url = urlsplit(request.url)
        self.assertEqual(request.method, 'POST')
        self.assertEqual((url.scheme, url.netloc), ('https', 'management.azure.com'))
        self.assertEqual(url.path, path)
        self.assertEqual(parse_qs(url.query), {'api-version': [api_version]})
        self.assertEqual(url.fragment, '')
        self.assertEqual(request.headers['Content-Type'], 'application/json')
        self.assertEqual(request.headers['Accept'], 'application/json')
        self.assertNotIn('Authorization', request.headers)
        self.assertIsInstance(request.body, (str, bytes, bytearray))
        self.assertEqual(json.loads(request.body), body)
        response = JsonHttpResponse(request, status, deepcopy(JOB))
        context = PipelineContext(None, stream=stream)
        # Ordinarily populated by ContentDecodePolicy in the bypassed pipeline.
        context[ContentDecodePolicy.CONTEXT_NAME] = deepcopy(JOB)
        return PipelineResponse(request, response, context)

    def invoke(self, argv, success=True):
        stdout, stderr = io.StringIO(), io.StringIO()
        cli = DummyCli(commands_loader_cls=ExtensionOnlyLoader)
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                code = cli.invoke(list(argv), out_file=stdout)
            except SystemExit as ex:
                # Argparse exits normally for help and rejects malformed JSON.
                code = ex.code
        if success:
            self.assertEqual(code or 0, 0, stdout.getvalue() + stderr.getvalue())
        else:
            self.assertNotEqual(code or 0, 0, 'Invalid public command was accepted: ' + repr(argv))
        return stdout.getvalue()

    def invoke_json(self, argv):
        return json.loads(self.invoke([*argv, '--output', 'json']))

    def invoke_local_json(self, argv):
        logins, sends = self.login.call_count, self.send.call_count
        result = self.invoke_json(argv)
        self.assertEqual(self.login.call_count, logins, 'Local construction must not discover credentials')
        self.assertEqual(self.send.call_count, sends, 'Local construction must not contact Azure')
        return result

    def json_argument(self, value, from_file=False):
        if not from_file:
            return json.dumps(value, ensure_ascii=False)
        path = Path(self.directory) / 'restore configuration 数据.json'
        path.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')
        return '@' + str(path)

    def configuration(self, names=None):
        names = SELECTORS if names is None else names
        return self.invoke_local_json(['dataprotection', 'backup-instance', 'initialize-restoreconfig',
                                       '--datasource-type', 'AzureCosmosDB', '--resource-identifiers', *names])

    def initializer_args(self, item=True, identity_args=(), configuration=None, from_file=False):
        args = ['dataprotection', 'backup-instance', 'restore',
                'initialize-for-item-recovery' if item else 'initialize-for-data-recovery',
                '--datasource-type', 'AzureCosmosDB', '--source-datastore', 'VaultStore',
                '--restore-location', LOCATION, '--target-resource-id', TARGET,
                '--recovery-point-id', RECOVERY_POINT, *identity_args]
        if item:
            args.extend(['--restore-configuration', self.json_argument(
                golden_config() if configuration is None else configuration, from_file)])
        return args

    def restore(self, verb, request, expected, no_wait=True, from_file=False,
                extra=(), path=None, api_version='2026-06-01', name_flag='-n'):
        validating = verb == 'validate-for-restore'
        path = path or INSTANCE + ('/validateRestore' if validating else '/restore')
        self.pending.append((path, api_version, deepcopy(expected), 202 if no_wait else 200))
        before = deepcopy(request)
        count = len(self.requests)
        args = ['dataprotection', 'backup-instance', *verb.split(),
                '-g', 'restore-tests', '--vault-name', 'vault', name_flag, 'instance',
                '--restore-request-object', self.json_argument(request, from_file), *extra,
                '--output', 'json']
        if no_wait:
            args.append('--no-wait')
        output = self.invoke(args)
        self.assertEqual(len(self.requests), count + 1, 'No polling/lookup HTTP is permitted')
        self.assertEqual(request, before, 'Serialization mutated the caller-owned fixture')
        if no_wait:
            self.assertEqual(output.strip(), '')
        else:
            self.assertEqual(json.loads(output), JOB)

    def assert_local_rejection(self, argv):
        count = self.send.call_count
        logins = self.login.call_count
        self.invoke(argv, success=False)
        self.assertEqual(self.send.call_count, count, 'Local rejection must precede HTTP')
        self.assertEqual(self.login.call_count, logins, 'Local rejection must precede client credentials')


class CosmosRestoreCommandTests(PublicCommandTransportCase):
    def test_config_initialize_permission_validate_trigger_identity_matrix(self):
        """Both restore modes, four identity choices, inline and UTF-8 @file."""
        config = self.configuration()
        self.assertEqual(config, golden_config())
        original_config = deepcopy(config)
        for item in (False, True):
            for identity_name, identity_args, identity in IDENTITIES:
                for from_file in (False, True):
                    with self.subTest(item=item, identity=identity_name, file=from_file):
                        request = self.invoke_local_json(self.initializer_args(
                            item, identity_args, configuration=config, from_file=from_file))
                        self.assertEqual(request, golden_restore(item, identity))
                        target = request['restore_target_info']
                        self.assertEqual(target['datasource_info']['resource_id'], TARGET)
                        self.assertEqual(target['datasource_info']['resource_uri'], TARGET)
                        self.assertNotIn('datasource_set_info', target)
                        self.assertNotIn('datasource_auth_credentials', target)
                        if identity is None:
                            self.assertNotIn('identity_details', request)
                        if item:
                            self.assertEqual(len(target['restore_criteria']), 1)
                            self.assertIsInstance(target['restore_criteria'][0]['resource_selectors'], dict)
                        else:
                            self.assertNotIn('restore_criteria', target)
                        self.assert_permissions(request, identity, from_file=from_file)
                        expected = golden_restore(item, identity, wire=True)
                        # Reuse the SAME request repeatedly, through both real command paths.
                        for _ in range(2):
                            self.restore('validate-for-restore', request,
                                         {'restoreRequestObject': expected}, from_file=from_file)
                            self.restore('restore trigger', request, expected, from_file=from_file)
                        self.assertEqual(config, original_config)

    def assert_permissions(self, request, identity=None, from_file=False, extra=()):
        """Patch vault/role IO only, preserving reconciliation and real RBAC logic."""
        principal = UAMI_PRINCIPAL if identity and identity.get('userAssignedIdentityArmUrl') else SAMI_PRINCIPAL
        vault = {'location': LOCATION, 'identity': {
            'type': 'SystemAssigned, UserAssigned', 'principalId': SAMI_PRINCIPAL,
            'userAssignedIdentities': {
                OTHER_UAMI: {'principalId': TENANT}, UAMI: {'principalId': UAMI_PRINCIPAL}}}}
        vault_get = Mock(return_value=deepcopy(vault))
        # Existing inherited grant: no writes and no propagation delay required.
        list_roles = Mock(return_value=[{'id': 'synthetic-existing-assignment'}])
        create_role = Mock(side_effect=AssertionError('Existing grant must not be recreated'))
        before = deepcopy(request)
        with patch.object(custom, 'BackupVaultGet', return_value=vault_get), \
                patch.object(helper, 'list_role_assignments', list_roles), \
                patch.object(helper, 'create_role_assignment', create_role), \
                patch.object(custom.time, 'sleep') as sleep, \
                patch.object(custom, 'prompt_y_n') as prompt:
            result = self.invoke_json([
                'dataprotection', 'backup-instance', 'update-msi-permissions',
                '-g', 'restore-tests', '--vault-name', 'vault', '--operation', 'Restore',
                '--permissions-scope', 'Resource', '--datasource-type', 'AzureCosmosDB',
                '--restore-request-object', self.json_argument(request, from_file), '--yes', *extra])
            self.assertEqual(result, [])
            vault_get.assert_called_once_with(command_args={'resource_group': 'restore-tests', 'vault_name': 'vault'})
            list_roles.assert_called_once()
            self.assertEqual(list_roles.call_args.kwargs, {
                'assignee': principal, 'role': 'Cosmos DB Operator', 'scope': TARGET, 'include_inherited': True})
            create_role.assert_not_called()
            sleep.assert_not_called()
            prompt.assert_not_called()
        self.assertEqual(request, before)

    def test_native_permission_wire_shape_and_case_insensitive_uami_flag(self):
        identity = IDENTITIES[2][2]
        self.assert_permissions(golden_restore(identity=identity, wire=True), identity,
                                from_file=True, extra=['--uami', UAMI.upper()])

    def test_permission_legacy_fallback_does_not_insert_identity_into_restore(self):
        for selected in (None, IDENTITIES[2][2]):
            request = golden_restore()
            self.assert_permissions(request, selected, extra=['--uami', UAMI] if selected else [])
            self.assertNotIn('identity_details', request)
            self.restore('restore trigger', request, golden_restore(wire=True))

    def test_permission_invalid_identity_or_target_fails_before_vault_and_roles(self):
        requests = []
        for identity in ({}, {'useSystemAssignedIdentity': False},
                         {'useSystemAssignedIdentity': True, 'userAssignedIdentityArmUrl': UAMI},
                         {'userAssignedIdentityArmUrl': UAMI},
                         {'useSystemAssignedIdentity': None, 'userAssignedIdentityArmUrl': UAMI},
                         {'useSystemAssignedIdentity': True, 'userAssignedIdentityArmUrl': None},
                         {'userAssignedIdentityArmUrl': TARGET}):
            requests.append((golden_restore(identity=identity), []))
        requests.append((golden_restore(identity=IDENTITIES[1][2]), ['--uami', UAMI]))
        requests.append((golden_restore(identity=IDENTITIES[2][2]), ['--uami', OTHER_UAMI]))
        bad_target = golden_restore()
        bad_target['restore_target_info']['datasource_info']['resource_id'] = TARGET + '/sqlDatabases/db'
        requests.append((bad_target, []))
        for request, extra in requests:
            with self.subTest(request=request, extra=extra):
                self.assert_local_rejection([
                    'dataprotection', 'backup-instance', 'update-msi-permissions',
                    '-g', 'restore-tests', '--vault-name', 'vault', '--operation', 'Restore',
                    '--permissions-scope', 'Resource', '--datasource-type', 'AzureCosmosDB',
                    '--restore-request-object', self.json_argument(request), '--yes', *extra])

    def test_synchronous_200_and_no_wait_202_use_real_lro_without_polling(self):
        for item in (False, True):
            request = self.invoke_json(self.initializer_args(item))
            expected = golden_restore(item, wire=True)
            for no_wait in (False, True):
                for verb in ('validate-for-restore', 'restore trigger'):
                    with self.subTest(item=item, no_wait=no_wait, verb=verb):
                        self.restore(verb, request, {'restoreRequestObject': expected}
                                     if verb == 'validate-for-restore' else expected, no_wait=no_wait)

    def test_wire_configuration_aliases_and_empty_overrides_are_normalized(self):
        for from_file in (False, True):
            for wire in (False, True):
                for empty in (None, {}):
                    with self.subTest(file=from_file, wire=wire, overrides=empty):
                        config = golden_config(wire)
                        config['resourceSelectors' if wire else 'resource_selectors'][
                            'resourceNameOverrides' if wire else 'resource_name_overrides'] = empty
                        before = deepcopy(config)
                        request = self.invoke_json(self.initializer_args(configuration=config, from_file=from_file))
                        self.assertEqual(request, golden_restore())
                        self.restore('restore trigger', request, golden_restore(wire=True))
                        self.assertEqual(config, before)

    def test_single_database_containers_case_distinctions_and_fifty_selector_boundary(self):
        for names in (['database'], ['database/container'], ['DB', 'db/container'],
                      ['db/Col', 'db/col'], ['db{}'.format(i) for i in range(50)]):
            with self.subTest(names=names):
                config = self.configuration(names)
                self.assertEqual(config, golden_config(names=names))
                request = self.invoke_json(self.initializer_args(configuration=config, from_file=True))
                self.assertEqual(request, golden_restore(names=names))
                expected = golden_restore(wire=True, names=names)
                self.restore('validate-for-restore', request, {'restoreRequestObject': expected})
                self.restore('restore trigger', request, expected)

    def test_malformed_json_and_missing_restore_request_reject_before_transport(self):
        for verb in ('validate-for-restore', 'restore trigger'):
            args = ['dataprotection', 'backup-instance', *verb.split(),
                    '-g', 'restore-tests', '--vault-name', 'vault', '-n', 'instance', '--no-wait']
            self.assert_local_rejection(args)
            self.assert_local_rejection([*args, '--restore-request-object', '{invalid-json'])

    def test_invalid_selectors_are_local_and_never_partially_accepted(self):
        bad_selections = [[], [''], [' '], ['db', 'db'], ['db', 'db/col'], ['db/col', 'db'],
                          ['/db'], ['db/'], ['db//col'], ['db/col/item'], ['db\\col'],
                          ['db?/col'], ['db#/col'], ['db\u0000/col'], ['db/col\u0085'],
                          ['db{}'.format(i) for i in range(51)]]
        for names in bad_selections:
            with self.subTest(names=names):
                self.assert_local_rejection([
                    'dataprotection', 'backup-instance', 'initialize-restoreconfig',
                    '--datasource-type', 'AzureCosmosDB', '--resource-identifiers', *names])
                self.assert_local_rejection(self.initializer_args(configuration=golden_config(names=names)))
        self.assert_local_rejection(['dataprotection', 'backup-instance', 'initialize-restoreconfig',
                                     '--datasource-type', 'AzureCosmosDB'])

    def test_mutated_configuration_is_revalidated_through_public_parser(self):
        config = self.configuration(['db/col'])
        mutations = [[], [config], {}, {'restoreCriteria': [config]}]
        bad = deepcopy(config)
        bad['resource_selectors']['resource_identifiers'].append('db')
        mutations.append(bad)
        for key, value in [('object_type', 'ItemPathBasedRestoreCriteria'),
                           ('resource_selectors', [config['resource_selectors']]),
                           ('objectType', 'GenericRestoreDatasourceCriteria'), ('unexpected', True)]:
            bad = deepcopy(config)
            bad[key] = value
            mutations.append(bad)
        for key, value in [('resource_identifiers', []), ('resource_identifiers', ['db', 'db']),
                           ('resource_identifiers', [1]), ('resource_identifiers', 'db/col'),
                           ('object_type', 'PrefixSelectionCriteria'),
                           ('resource_name_overrides', {'db': 'renamed'}),
                           ('resourceIdentifiers', ['db']), ('extra', {})]:
            bad = deepcopy(config)
            bad['resource_selectors'][key] = value
            mutations.append(bad)
        for bad in mutations:
            for from_file in (False, True):
                with self.subTest(config=bad, file=from_file):
                    before = deepcopy(bad)
                    self.assert_local_rejection(self.initializer_args(configuration=bad, from_file=from_file))
                    self.assertEqual(bad, before)

    def test_invalid_item_targets_and_full_item_identity_flags_are_local(self):
        for target in ('', ' ', 'https://account.documents.azure.com/', TARGET + '/',
                       TARGET + '/sqlDatabases/db', TARGET + '?q=1', INSTANCE,
                       TARGET.replace(SUBSCRIPTION, 'not-a-guid')):
            with self.subTest(target=target):
                args = self.initializer_args()
                args[args.index('--target-resource-id') + 1] = target
                self.assert_local_rejection(args)
        for item in (False, True):
            for identity in (['--mi-system-assigned', 'false'],
                             ['--mi-system-assigned', 'true', '--uami', UAMI],
                             ['--uami', ''], ['--uami', TARGET], ['--uami', UAMI + '/child']):
                with self.subTest(item=item, identity=identity):
                    self.assert_local_rejection(self.initializer_args(item, identity))
        args = self.initializer_args()
        index = args.index('--target-resource-id')
        del args[index:index + 2]
        self.assert_local_rejection(args)
        self.assert_local_rejection([*args, '--backup-instance-id', INSTANCE])
        self.assert_local_rejection([*self.initializer_args(), '--backup-instance-id', INSTANCE])

    def test_invalid_store_mode_foreign_options_and_missing_configuration_are_local(self):
        args = self.initializer_args()
        index = args.index('--restore-configuration')
        self.assert_local_rejection(args[:index])
        for store in ('OperationalStore', 'ArchiveStore'):
            bad = list(args)
            bad[bad.index('--source-datastore') + 1] = store
            self.assert_local_rejection(bad)
        bad = list(args)
        index = bad.index('--recovery-point-id')
        del bad[index:index + 2]
        self.assert_local_rejection([*bad, '--point-in-time', POINT_IN_TIME])
        self.assert_local_rejection([*args, '--container-list', 'container-one'])
        self.assert_local_rejection([*self.initializer_args(False), '--restore-configuration',
                                     self.json_argument(golden_config())])
        for extra in (['--include-cluster-scope', 'false'], ['--namespace-mappings', '{}'],
                      ['--name-overrides', '{}']):
            self.assert_local_rejection([
                'dataprotection', 'backup-instance', 'initialize-restoreconfig',
                '--datasource-type', 'AzureCosmosDB', '--resource-identifiers', 'db', *extra])

    def test_existing_identity_and_backup_instance_name_aliases(self):
        for item in (False, True):
            for flag in ('--mi-system-assigned', '--use-system-identity', '--use-system-assigned-identity'):
                self.assertEqual(self.invoke_json(self.initializer_args(item, [flag, 'true'])),
                                 golden_restore(item, IDENTITIES[1][2]))
            for flag in ('--mi-user-assigned', '--user-assigned-identity-arm-url', '--uami'):
                self.assertEqual(self.invoke_json(self.initializer_args(item, [flag, UAMI])),
                                 golden_restore(item, IDENTITIES[2][2]))
        for flag in ('-n', '--name', '--backup-instance-name'):
            for verb in ('validate-for-restore', 'restore trigger'):
                expected = golden_restore(wire=True)
                self.restore(verb, golden_restore(), {'restoreRequestObject': expected}
                             if verb == 'validate-for-restore' else expected, name_flag=flag)

    def test_public_help_loads_without_authentication_or_transport(self):
        count = self.login.call_count
        for command in ('initialize-restoreconfig', 'restore initialize-for-item-recovery',
                        'restore initialize-for-data-recovery', 'update-msi-permissions',
                        'validate-for-restore', 'restore trigger'):
            with self.subTest(command=command):
                output = self.invoke(['dataprotection', 'backup-instance', *command.split(), '--help'])
                self.assertIn('--', output)
        self.send.assert_not_called()
        self.assertEqual(self.login.call_count, count)

    def test_cross_region_native_envelopes_keep_2025_07_01_contract(self):
        # Existing PostgreSQL Flexible Server restore-as-files, NOT Cosmos CRR.
        # The target location is coherent with the secondary-region endpoint.
        source = {'id': INSTANCE, 'properties': {'backupInstanceExtendedProperties': {
            'protectedPrimaryRegion': LOCATION, 'protectedSecondaryRegion': SECONDARY}}}
        with patch.object(helper, 'get_backup_instance_from_resourcegraph', return_value=source) as lookup:
            for _, identity_args, identity in IDENTITIES[:2]:
                target_storage = RG + '/providers/Microsoft.Storage/storageAccounts/secondarytarget'
                target_url = 'https://secondarytarget.blob.core.windows.net/restores'
                request = self.invoke_local_json([
                    'dataprotection', 'backup-instance', 'restore', 'initialize-for-data-recovery-as-files',
                    '--datasource-type', 'AzureDatabaseForPostgreSQLFlexibleServer',
                    '--source-datastore', 'VaultStore', '--restore-location', SECONDARY,
                    '--recovery-point-id', RECOVERY_POINT, '--target-resource-id', target_storage,
                    '--target-blob-container-url', target_url, '--target-file-name', 'restore-prefix', *identity_args])
                expected = {
                    'objectType': 'AzureBackupRecoveryPointBasedRestoreRequest',
                    'recoveryPointId': RECOVERY_POINT, 'sourceDataStoreType': 'VaultStore',
                    'restoreTargetInfo': {
                        'objectType': 'RestoreFilesTargetInfo', 'restoreLocation': SECONDARY,
                        'recoveryOption': 'FailIfExists', 'targetDetails': {
                            'url': target_url, 'filePrefix': 'restore-prefix',
                            'restoreTargetLocationType': 'AzureBlobs', 'targetResourceArmId': target_storage}}}
                if identity is not None:
                    expected['identityDetails'] = identity
                for verb, suffix in (('validate-for-restore', 'validateCrossRegionRestore'),
                                     ('restore trigger', 'crossRegionRestore')):
                    for no_wait in (False, True):
                        with self.subTest(identity=identity, verb=verb, no_wait=no_wait):
                            self.restore(verb, request, {
                                'objectType': 'ValidateRestoreRequestObject' if verb == 'validate-for-restore'
                                else 'AzureBackupRecoveryPointBasedRestoreRequest',
                                'restoreRequestObject': expected,
                                'crossRegionRestoreDetails': {
                                    'sourceBackupInstanceId': INSTANCE, 'sourceRegion': LOCATION}},
                                no_wait=no_wait, extra=['--use-secondary-region', 'true'],
                                path=PROVIDER + '/locations/' + SECONDARY + '/' + suffix,
                                api_version='2025-07-01')
            self.assertEqual(lookup.call_count, 8)
            for call in lookup.call_args_list:
                self.assertEqual(call.args[1:], ('restore-tests', 'vault', 'instance'))

    def test_resource_guard_full_uri_and_auxiliary_tenant_are_forwarded(self):
        operation = (RG + '/providers/Microsoft.DataProtection/resourceGuards/guard/'
                     'dppRestoreRequests/default')
        expected = golden_restore(wire=True)
        expected['resourceGuardOperationRequests'] = [operation]
        self.restore('restore trigger', golden_restore(), expected,
                     extra=['--resource-guard-operation-requests', operation, '--tenant-id', AUX_TENANT])
        self.assertTrue(self.login.call_args_list)
        self.assertTrue(any(call.kwargs.get('aux_tenants') == [AUX_TENANT]
                            for call in self.login.call_args_list), self.login.call_args_list)
        # Auxiliary authorization headers belong to the bypassed bearer policy;
        # the actual Profile argument, not a fabricated token/header, is asserted.


class NonCosmosRestoreCompatibilityTests(PublicCommandTransportCase):
    def assert_compatibility(self, request, expected):
        original = deepcopy(request)
        for _ in range(2):
            self.restore('validate-for-restore', request, {'restoreRequestObject': expected})
            self.restore('restore trigger', request, expected)
        self.assertEqual(request, original)

    def initialize_workload(self, workload, target, store='VaultStore', item=True, extra=(), pit=False):
        return self.invoke_json([
            'dataprotection', 'backup-instance', 'restore',
            'initialize-for-item-recovery' if item else 'initialize-for-data-recovery',
            '--datasource-type', workload, '--source-datastore', store,
            '--target-resource-id', target, '--restore-location', LOCATION,
            *(['--point-in-time', POINT_IN_TIME] if pit else ['--recovery-point-id', RECOVERY_POINT]), *extra])

    def storage_expected(self, datasource_type, criteria, pit=False):
        target = RG + '/providers/Microsoft.Storage/storageAccounts/storage-target'
        result = {
            'objectType': 'AzureBackupRecoveryTimeBasedRestoreRequest' if pit
            else 'AzureBackupRecoveryPointBasedRestoreRequest',
            'sourceDataStoreType': 'OperationalStore' if pit else 'VaultStore',
            'restoreTargetInfo': {
                'objectType': 'ItemLevelRestoreTargetInfo', 'restoreLocation': LOCATION,
                'recoveryOption': 'FailIfExists',
                'datasourceInfo': golden_datasource(target, wire=True,
                                                    resource_type='Microsoft.Storage/storageAccounts',
                                                    datasource_type=datasource_type),
                'datasourceSetInfo': golden_datasource(target, wire=True, is_set=True,
                                                       resource_type='Microsoft.Storage/storageAccounts',
                                                       datasource_type=datasource_type),
                'restoreCriteria': deepcopy(criteria)}}
        if pit:
            # The public datetime_type parser emits seven fractional digits + Z.
            result['recoveryPointTime'] = '2026-10-01T00:00:00.0000000Z'
        else:
            result['recoveryPointId'] = RECOVERY_POINT
        return result

    def test_blob_point_in_time_and_vault_native_transport(self):
        target = RG + '/providers/Microsoft.Storage/storageAccounts/storage-target'
        for pit in (False, True):
            with self.subTest(pit=pit):
                request = self.initialize_workload('AzureBlob', target, pit=pit,
                                                   store='OperationalStore' if pit else 'VaultStore',
                                                   extra=['--container-list', 'container-one', 'container-two'])
                criteria = ([{'objectType': 'RangeBasedItemLevelRestoreCriteria',
                              'minMatchingValue': name, 'maxMatchingValue': name + '-0'}
                             for name in ('container-one', 'container-two')] if pit else
                            [{'objectType': 'ItemPathBasedRestoreCriteria', 'itemPath': name,
                              'isPathRelativeToBackupItem': True} for name in ('container-one', 'container-two')])
                self.assert_compatibility(request, self.storage_expected(
                    'Microsoft.Storage/storageAccounts/blobServices', criteria, pit))

    def test_adls_vault_prefix_and_rename_native_transport(self):
        target = RG + '/providers/Microsoft.Storage/storageAccounts/storage-target'
        pattern = {'containers': [{'name': 'filesystem-one', 'prefixmatch': ['Dir_A/', '数据库/'],
                                   'renameto': 'filesystem-two'}]}
        request = self.initialize_workload('AzureDataLakeStorage', target,
                                          extra=['--vaulted-blob-prefix', self.json_argument(pattern)])
        self.assert_compatibility(request, self.storage_expected(
            'Microsoft.Storage/storageAccounts/adlsBlobServices', [{
                'objectType': 'ItemPathBasedRestoreCriteria', 'itemPath': 'filesystem-one',
                'isPathRelativeToBackupItem': True, 'subItemPathPrefix': ['Dir_A/', '数据库/'],
                'renameTo': 'filesystem-two'}]))

    def test_aks_populated_set_and_legacy_namespace_mapping_wire_behavior(self):
        target = RG + '/providers/Microsoft.ContainerService/managedClusters/target-cluster'
        config = {'object_type': 'KubernetesClusterRestoreCriteria',
                  'included_namespaces': ['source_ns'], 'include_cluster_scope_resources': False,
                  'persistent_volume_restore_mode': 'RestoreWithVolumeData',
                  'namespace_mappings': {'source_ns': 'target_ns'}}
        request = self.initialize_workload('AzureKubernetesService', target, store='OperationalStore',
                                          extra=['--restore-configuration', self.json_argument(config)])
        expected = {
            'objectType': 'AzureBackupRecoveryPointBasedRestoreRequest',
            'recoveryPointId': RECOVERY_POINT, 'sourceDataStoreType': 'OperationalStore',
            'restoreTargetInfo': {
                'objectType': 'ItemLevelRestoreTargetInfo', 'restoreLocation': LOCATION,
                'recoveryOption': 'FailIfExists',
                'datasourceInfo': golden_datasource(target, wire=True,
                                                    resource_type='Microsoft.ContainerService/managedclusters',
                                                    datasource_type='Microsoft.ContainerService/managedClusters'),
                'datasourceSetInfo': golden_datasource(target, wire=True, is_set=True,
                                                       resource_type='Microsoft.ContainerService/managedclusters',
                                                       datasource_type='Microsoft.ContainerService/managedClusters'),
                'restoreCriteria': [{
                    'objectType': 'KubernetesClusterRestoreCriteria', 'includedNamespaces': ['source_ns'],
                    'includeClusterScopeResources': False, 'persistentVolumeRestoreMode': 'RestoreWithVolumeData',
                    # Known existing converter defect: caller-owned map KEYS are transformed,
                    # but literal VALUES are not. Freeze, do not fix, in this Cosmos change.
                    'namespaceMappings': {'sourceNs': 'target_ns'}}]}}
        self.assert_compatibility(request, expected)

    def test_elastic_san_generic_selection_and_legacy_override_mapping_wire_behavior(self):
        target = RG + '/providers/Microsoft.ElasticSan/elasticSans/target-san/volumeGroups/target-group'
        config = {'object_type': 'GenericRestoreDatasourceCriteria', 'resource_selectors': {
            'object_type': 'ResourceListSelectionCriteria', 'resource_identifiers': ['volume_one', 'volume_two'],
            'resource_name_overrides': {'volume_one': 'restored_one'}}}
        request = self.initialize_workload('AzureElasticSAN', target, store='OperationalStore',
                                          extra=['--restore-configuration', self.json_argument(config)])
        parent = target.rsplit('/volumeGroups/', 1)[0]
        expected = {
            'objectType': 'AzureBackupRecoveryPointBasedRestoreRequest',
            'recoveryPointId': RECOVERY_POINT, 'sourceDataStoreType': 'OperationalStore',
            'restoreTargetInfo': {
                'objectType': 'ItemLevelRestoreTargetInfo', 'restoreLocation': LOCATION,
                'recoveryOption': 'FailIfExists',
                'datasourceInfo': golden_datasource(target, wire=True,
                                                    resource_type='Microsoft.ElasticSan/elasticSans/volumeGroups',
                                                    datasource_type='Microsoft.ElasticSan/elasticSans/volumeGroups'),
                'datasourceSetInfo': golden_datasource(parent, wire=True, is_set=True, uri='',
                                                       resource_type='Microsoft.ElasticSan/elasticSans',
                                                       datasource_type='Microsoft.ElasticSan/elasticSans/volumeGroups'),
                'restoreCriteria': [{
                    'objectType': 'GenericRestoreDatasourceCriteria', 'resourceSelectors': {
                        'objectType': 'ResourceListSelectionCriteria',
                        'resourceIdentifiers': ['volume_one', 'volume_two'],
                        # Same pre-existing map-key risk as AKS, not Cosmos name normalization.
                        'resourceNameOverrides': {'volumeOne': 'restored_one'}}}]}}
        self.assert_compatibility(request, expected)

    def test_oss_populated_secret_store_credentials_and_datasource_set_native_transport(self):
        target = RG + '/providers/Microsoft.DBforPostgreSQL/servers/target-server/databases/target-db'
        secret_uri = 'https://synthetic-vault.vault.azure.net/secrets/restore-password/version'
        request = self.initialize_workload('AzureDatabaseForPostgreSQL', target, item=False,
                                          extra=['--secret-store-type', 'AzureKeyVault',
                                                 '--secret-store-uri', secret_uri])
        parent = target.rsplit('/databases/', 1)[0]
        expected = {
            'objectType': 'AzureBackupRecoveryPointBasedRestoreRequest',
            'recoveryPointId': RECOVERY_POINT, 'sourceDataStoreType': 'VaultStore',
            'restoreTargetInfo': {
                'objectType': 'RestoreTargetInfo', 'restoreLocation': LOCATION,
                'recoveryOption': 'FailIfExists',
                'datasourceInfo': golden_datasource(target, wire=True, uri='',
                                                    resource_type='Microsoft.DBforPostgreSQL/servers/databases',
                                                    datasource_type='Microsoft.DBforPostgreSQL/servers/databases'),
                'datasourceSetInfo': golden_datasource(parent, wire=True, is_set=True, uri='',
                                                       resource_type='Microsoft.DBforPostgreSQL/servers',
                                                       datasource_type='Microsoft.DBforPostgreSQL/servers/databases'),
                'datasourceAuthCredentials': {
                    'objectType': 'SecretStoreBasedAuthCredentials',
                    'secretStoreResource': {'uri': secret_uri, 'value': None, 'secretStoreType': 'AzureKeyVault'}}}}
        self.assert_compatibility(request, expected)