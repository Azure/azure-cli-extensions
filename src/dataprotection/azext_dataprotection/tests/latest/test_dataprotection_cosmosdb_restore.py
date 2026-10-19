# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Offline Cosmos ILR contract (handoff C01-C09, I01-I06, P01-P05).

These tests exercise the real manual entry points and shared permission helpers.
They are not service acceptance or HTTP-serialization tests. Synthetic identifiers
are intentionally unrelated to any fixture subscription. No login is required.
"""

from copy import deepcopy
import json
import socket
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import requests

from azure.cli.core.azclierror import (
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
    RequiredArgumentMissingError,
)
# Match the command loader's helper-first import order (the legacy modules refer
# to each other). Importing custom first does not represent the public CLI path.
from azext_dataprotection.manual import helpers as helper
from azext_dataprotection.manual import custom, cosmosdb


SUB = '/subscriptions/00000000-0000-0000-0000-000000000001'
RG = SUB + '/resourceGroups/restore-tests'
TARGET = RG + '/providers/Microsoft.DocumentDB/databaseAccounts/empty-target'
UAMI = RG + '/providers/Microsoft.ManagedIdentity/userAssignedIdentities/restore-identity'
OTHER_UAMI = RG + '/providers/Microsoft.ManagedIdentity/userAssignedIdentities/other-identity'
BI = RG + '/providers/Microsoft.DataProtection/backupVaults/vault/backupInstances/instance'
SAMI_PRINCIPAL = '00000000-0000-0000-0000-000000000002'
UAMI_PRINCIPAL = '00000000-0000-0000-0000-000000000003'
OTHER_PRINCIPAL = '00000000-0000-0000-0000-000000000004'
ROLE_ID = SUB + '/providers/Microsoft.Authorization/roleDefinitions/00000000-0000-0000-0000-000000000005'
RP = 'synthetic-committed-recovery-point'
LOCATION = 'eastasia'
PIT = '2026-10-01T00:00:00Z'
ERRORS = (InvalidArgumentValueError, RequiredArgumentMissingError, MutuallyExclusiveArgumentError)
CONFIGURE = custom.dataprotection_backup_instance_initialize_restoreconfig
ITEM = custom.restore_initialize_for_item_recovery
FULL = custom.restore_initialize_for_data_recovery


def forbidden(*args, **kwargs):
    raise AssertionError('Unexpected network, authentication, inventory, or Azure operation')


@pytest.fixture(autouse=True)
def zero_network(monkeypatch):
    """Fail closed, including code which bypasses the requests transport."""
    monkeypatch.setattr(requests.sessions.Session, 'request', forbidden)
    monkeypatch.setattr(socket.socket, 'connect', forbidden)
    monkeypatch.setattr(custom, 'get_mgmt_service_client', forbidden)
    monkeypatch.setattr(helper, 'get_mgmt_service_client', forbidden)
    monkeypatch.setattr(custom, 'BackupVaultGet', forbidden)
    monkeypatch.setattr(custom, 'list_role_assignments', forbidden)
    monkeypatch.setattr(custom, 'create_role_assignment', forbidden)
    monkeypatch.setattr(helper, 'list_role_assignments', forbidden)
    monkeypatch.setattr(helper, 'create_role_assignment', forbidden)
    monkeypatch.setattr(custom, 'prompt_y_n', forbidden)
    monkeypatch.setattr(custom.time, 'sleep', forbidden)
    monkeypatch.setattr(helper.backupcenter_helper, 'get_selected_subscription', forbidden)
    from azext_dataprotection.aaz.latest.dataprotection import backup_instance
    monkeypatch.setattr(backup_instance, 'Show', forbidden)


@pytest.fixture
def cmd():
    # Any attempt to use this as a real CLI context must fail rather than log in.
    return SimpleNamespace(cli_ctx=SimpleNamespace(), command_kwargs={})


def config(names=None, wire=False):
    """Independent golden configuration, not output from the code under test."""
    names = ['DB1/col1', 'Db1/col2', 'db2'] if names is None else names
    if wire:
        return {'objectType': 'GenericRestoreDatasourceCriteria', 'resourceSelectors': {
            'objectType': 'ResourceListSelectionCriteria', 'resourceIdentifiers': deepcopy(names)}}
    return {'object_type': 'GenericRestoreDatasourceCriteria', 'resource_selectors': {
        'object_type': 'ResourceListSelectionCriteria', 'resource_identifiers': deepcopy(names)}}


def datasource(resource_id=TARGET, datasource_type='Microsoft.DocumentDB/databaseAccounts',
               resource_type='Microsoft.DocumentDB/databaseAccounts', uri=None):
    return {'object_type': 'Datasource', 'datasource_type': datasource_type,
            'resource_id': resource_id, 'resource_uri': resource_id if uri is None else uri,
            'resource_name': resource_id.split('/')[-1], 'resource_type': resource_type,
            'resource_location': LOCATION}


def expected_request(item=True, identity=None):
    target = {'object_type': 'ItemLevelRestoreTargetInfo' if item else 'RestoreTargetInfo',
              'restore_location': LOCATION, 'recovery_option': 'FailIfExists',
              'datasource_info': datasource()}
    if item:
        target['restore_criteria'] = [config()]
    request = {'object_type': 'AzureBackupRecoveryPointBasedRestoreRequest',
               'recovery_point_id': RP, 'source_data_store_type': 'VaultStore',
               'restore_target_info': target}
    if identity is not None:
        request['identity_details'] = identity
    return request


def initialize(cmd, **overrides):
    args = dict(cmd=cmd, datasource_type='AzureCosmosDB', source_datastore='VaultStore',
                restore_location=LOCATION, target_resource_id=TARGET,
                recovery_point_id=RP, restore_configuration=config())
    args.update(overrides)
    return ITEM(**args)


VALID_SELECTIONS = [
    ['db1'], ['db1/col1'], ['db1/col1', 'db1/col2'], ['db1', 'db2'],
    ['DB1/col1', 'Db1/col2', 'db2'], ['DB1', 'db1'], ['DB1', 'db1/col'],
    ['db1', 'db10/col'], ['db1/COL', 'db1/col'],
    ['db*', 'db{1}/col,2', 'comma,name', '{literal}'],
    [' db ', ' db/ col ', 'db /col'],
    ['é', 'e\u0301', '数据库/容器', 'Δ/😀'],
    ['ß', 'ss', 'İ', 'i', 'Σ', 'σ', 'ς'],
    ['db%2Fname', 'db%23/col%3F', 'db+name/col%20name'],
    ['z', 'A/Two', 'a/one', 'middle'],
    ['db\u200d/col\u200b', 'db\u2028/col\u2029'],
    ['db{}'.format(i) for i in range(50)],
]


@pytest.mark.parametrize('names', VALID_SELECTIONS)
def test_C01_C02_C03_C08_config_and_initializer_preserve_literal_selection(cmd, names):
    before = deepcopy(names)
    actual = CONFIGURE('AzureCosmosDB', resource_identifiers=names)
    assert actual == config(names)
    assert names == before
    assert actual['resource_selectors']['resource_identifiers'] is not names
    request = initialize(cmd, restore_configuration=actual)
    expected = expected_request()
    expected['restore_target_info']['restore_criteria'] = [config(names)]
    assert request == expected
    assert actual == config(names)


BAD_SELECTIONS = [
    None, [], 'db/col', ('db',), {'db': 'col'}, 1, False,
    [None], [1], [True], [{}], [[]], [''], [' '], ['\u00a0'],
    ['/db'], ['db/'], ['db//col'], ['db/col/item'], [' /col'], ['db/ '],
    ['db\\col'], ['db?/col'], ['db#/col'], ['db/col\\'], ['db/col?'], ['db/col#'],
    ['db', 'db'], ['db/col', 'db/col'], ['db', 'db/col'], ['db/col', 'db'],
    ['db*', 'db*/{col}'], ['db*/{col}', 'db*'],
    [' db ', ' db /col'], [' db /col', ' db '],
    ['db{}'.format(i) for i in range(51)],
]


@pytest.mark.parametrize('names', BAD_SELECTIONS)
@pytest.mark.parametrize('entrypoint', ['config', 'item'])
def test_C02_C04_C05_C06_C07_invalid_selection_rejected(cmd, names, entrypoint):
    original = deepcopy(names)
    with pytest.raises(ERRORS) as exc:
        if entrypoint == 'config':
            CONFIGURE('AzureCosmosDB', resource_identifiers=names)
        else:
            initialize(cmd, restore_configuration=config(names) if names is not None else {
                'object_type': 'GenericRestoreDatasourceCriteria', 'resource_selectors': {
                    'object_type': 'ResourceListSelectionCriteria', 'resource_identifiers': None}})
    assert str(exc.value)
    assert names == original


# Unicode Cc comprises U+0000..001F and U+007F..009F (65, not just ASCII).
CC = [chr(i) for i in list(range(32)) + list(range(127, 160))]


@pytest.mark.parametrize('control', CC, ids=lambda c: 'U+{:04X}'.format(ord(c)))
@pytest.mark.parametrize('position', ['database', 'container'])
@pytest.mark.parametrize('entrypoint', ['config', 'item'])
def test_C07_every_unicode_control_rejected(cmd, control, position, entrypoint):
    name = 'd{}b/col'.format(control) if position == 'database' else 'db/c{}ol'.format(control)
    with pytest.raises(ERRORS):
        if entrypoint == 'config':
            CONFIGURE('AzureCosmosDB', resource_identifiers=['valid', name, 'another'])
        else:
            initialize(cmd, restore_configuration=config(['valid', name, 'another']))


FOREIGN_CONFIG_OPTIONS = [
    'excluded_resource_types', 'included_resource_types', 'excluded_namespaces',
    'included_namespaces', 'label_selectors', 'persistent_volume_restore_mode',
    'include_cluster_scope_resources', 'namespace_mappings', 'conflict_policy',
    'restore_hook_references', 'staging_resource_group_id', 'staging_storage_account_id',
    'resource_modifier_reference', 'resource_name_overrides',
]


@pytest.mark.parametrize('option', FOREIGN_CONFIG_OPTIONS)
@pytest.mark.parametrize('value', [False, '', [], {}, 'explicit-value'])
def test_C09_foreign_config_options_reject_explicit_false_and_empty(option, value):
    with pytest.raises(InvalidArgumentValueError):
        CONFIGURE('AzureCosmosDB', resource_identifiers=['db'], **{option: value})


@pytest.mark.parametrize('option', [
    'container_list', 'from_prefix_pattern', 'to_prefix_pattern', 'vaulted_blob_prefix_pattern',
])
@pytest.mark.parametrize('value', [False, '', [], {}, ['container1']])
def test_C09_blob_inputs_never_fall_through_for_cosmos(cmd, option, value):
    with pytest.raises(InvalidArgumentValueError):
        initialize(cmd, **{option: value})


def malformed_configs():
    values = [None, [], [config()], [[config()]], '', '[]', json.dumps(config()),
              False, 0, {}, {'restoreCriteria': [config()]},
              {'object_type': 'GenericRestoreDatasourceCriteria'},
              {'resource_selectors': config()['resource_selectors']}]
    for wrong in [None, '', 'genericRestoreDatasourceCriteria', 'ItemPathBasedRestoreCriteria',
                  'KubernetesClusterRestoreCriteria', [], {}, False]:
        value = config()
        value['object_type'] = wrong
        values.append(value)
    for wrong in [None, [], [config()['resource_selectors']], 'db/col', False, 1, {}]:
        value = config()
        value['resource_selectors'] = wrong
        values.append(value)
    for wrong in [None, '', 'resourcelistselectioncriteria', 'PrefixSelectionCriteria', [], {}]:
        value = config()
        value['resource_selectors']['object_type'] = wrong
        values.append(value)
    value = config()
    del value['resource_selectors']['resource_identifiers']
    values.append(value)
    for wrong in [{'db': 'renamed'}, [], '', False, 1, 'rename']:
        value = config()
        value['resource_selectors']['resource_name_overrides'] = wrong
        values.append(value)
    for path, key, extra in [
            ('root', 'extra', {}), ('selector', 'extra', {}),
            ('root', 'objectType', 'GenericRestoreDatasourceCriteria'),
            ('root', 'resourceSelectors', {}),
            ('selector', 'objectType', 'ResourceListSelectionCriteria'),
            ('selector', 'resourceIdentifiers', ['db']),
            ('selector', 'resourceNameOverrides', {'db': 'renamed'})]:
        value = config()
        node = value if path == 'root' else value['resource_selectors']
        node[key] = extra
        values.append(value)
    return values


@pytest.mark.parametrize('value', malformed_configs())
def test_I02_initializer_revalidates_malformed_configs_without_mutating(cmd, value):
    before = deepcopy(value)
    with pytest.raises(ERRORS):
        initialize(cmd, restore_configuration=value)
    assert value == before


@pytest.mark.parametrize('wire', [False, True])
@pytest.mark.parametrize('overrides', [None, {}])
def test_I01_supported_json_config_aliases_and_empty_optional_overrides(cmd, wire, overrides):
    value = config(wire=wire)
    selector = value['resourceSelectors' if wire else 'resource_selectors']
    selector['resourceNameOverrides' if wire else 'resource_name_overrides'] = overrides
    # Model the saved UTF-8 JSON roundtrip without creating any other file.
    value = json.loads(json.dumps(value, ensure_ascii=False))
    before = deepcopy(value)
    assert initialize(cmd, restore_configuration=value) == expected_request()
    assert value == before


def test_I02_mutated_helper_output_cannot_bypass_revalidation(cmd):
    value = CONFIGURE('AzureCosmosDB', resource_identifiers=['db/col'])
    value['resource_selectors']['resource_identifiers'].append('db')
    with pytest.raises(InvalidArgumentValueError):
        initialize(cmd, restore_configuration=value)


def test_C05_config_missing_identifiers_and_I02_item_missing_configuration(cmd):
    with pytest.raises(RequiredArgumentMissingError):
        CONFIGURE('AzureCosmosDB')
    with pytest.raises(RequiredArgumentMissingError):
        ITEM(cmd, 'AzureCosmosDB', 'VaultStore', LOCATION,
             target_resource_id=TARGET, recovery_point_id=RP)


@pytest.mark.parametrize('bad', [None, 42, '', ' ', 'db/col/item', 'db/col#'])
def test_C05_C06_invalid_entry_among_valid_entries_is_not_partially_accepted(cmd, bad):
    names = ['valid1/col', bad, 'valid2']
    with pytest.raises(ERRORS):
        CONFIGURE('AzureCosmosDB', resource_identifiers=names)
    with pytest.raises(ERRORS):
        initialize(cmd, restore_configuration=config(names))


BAD_TARGETS = [
    None, '', ' ', False, 1, [], {}, 'https://account.documents.azure.com/',
    TARGET + '/', TARGET + '/sqlDatabases/db', TARGET + '/sqlDatabases/db/containers/col',
    TARGET + '?api-version=2026-06-01', TARGET + '#fragment', TARGET + '\\child',
    BI, TARGET.replace('databaseAccounts', 'sqlDatabases'),
    TARGET.replace('00000000-0000-0000-0000-000000000001', 'not-a-guid'),
    TARGET.replace('/restore-tests/', '/ /'), TARGET.replace('/empty-target', '/ '),
    TARGET.replace('Microsoft.DocumentDB', 'Microsoft.Compute'),
    TARGET + '\u0085', TARGET + '/extra/child',
]


@pytest.mark.parametrize('target', BAD_TARGETS)
def test_I04_account_target_is_validated_before_shared_lookup(cmd, monkeypatch, target):
    resolver = Mock(side_effect=forbidden)
    monkeypatch.setattr(helper, 'validate_and_set_datasource_id_in_restore_request', resolver)
    with pytest.raises(ERRORS):
        initialize(cmd, target_resource_id=target)
    resolver.assert_not_called()


@pytest.mark.parametrize('target', [TARGET, TARGET.upper()])
def test_I04_target_arm_id_case_preserved(cmd, target):
    actual = initialize(cmd, target_resource_id=target)
    assert actual['restore_target_info']['datasource_info']['resource_id'] == target
    assert actual['restore_target_info']['datasource_info']['resource_uri'] == target


@pytest.mark.parametrize('overrides', [
    {'source_datastore': 'OperationalStore'}, {'source_datastore': 'ArchiveStore'},
    {'point_in_time': PIT, 'recovery_point_id': None}, {'point_in_time': PIT},
    {'recovery_point_id': None}, {'backup_instance_id': BI, 'target_resource_id': None},
    {'backup_instance_id': BI}, {'backup_instance_id': ''},
])
def test_I03_modes_stores_and_bi_reject_before_shared_lookup(cmd, monkeypatch, overrides):
    resolver = Mock(side_effect=forbidden)
    monkeypatch.setattr(helper, 'validate_and_set_datasource_id_in_restore_request', resolver)
    with pytest.raises(ERRORS):
        initialize(cmd, **overrides)
    resolver.assert_not_called()


IDENTITIES = [
    (None, None, None), (True, None, {'useSystemAssignedIdentity': True}),
    (None, UAMI, {'useSystemAssignedIdentity': False, 'userAssignedIdentityArmUrl': UAMI}),
    (False, UAMI, {'useSystemAssignedIdentity': False, 'userAssignedIdentityArmUrl': UAMI}),
]


@pytest.mark.parametrize('system,uami,expected', IDENTITIES)
@pytest.mark.parametrize('item', [False, True])
def test_I05_I06_full_and_item_exact_identity_request(cmd, system, uami, expected, item):
    args = dict(cmd=cmd, datasource_type='AzureCosmosDB', source_datastore='VaultStore',
                restore_location=LOCATION, target_resource_id=TARGET, recovery_point_id=RP,
                use_system_assigned_identity=system, user_assigned_identity_arm_url=uami)
    if item:
        args['restore_configuration'] = config()
    assert (ITEM if item else FULL)(**args) == expected_request(item, expected)


@pytest.mark.parametrize('value', [config(), {}, [], False, '', config(wire=True)])
def test_I05_full_recovery_rejects_any_explicit_selection_config(cmd, value):
    with pytest.raises(InvalidArgumentValueError):
        FULL(cmd, 'AzureCosmosDB', 'VaultStore', LOCATION, target_resource_id=TARGET,
             recovery_point_id=RP, restore_configuration=value)


INVALID_IDENTITIES = [(False, None), (True, UAMI)]
INVALID_IDENTITIES += [(value, None) for value in ['true', 'false', 0, 1, [], {}]]
INVALID_IDENTITIES += [(None, value) for value in [
    '', ' ', [], {}, False, 1, 'identity', TARGET, UAMI + '/', UAMI + '?q=1',
    UAMI + '#fragment', UAMI + '/child/x', UAMI + '\u0000',
    UAMI.replace('00000000-0000-0000-0000-000000000001', 'not-guid'),
]]


@pytest.mark.parametrize('system,uami', INVALID_IDENTITIES)
@pytest.mark.parametrize('item', [False, True])
def test_I06_invalid_cosmos_identity_never_silently_disappears(cmd, system, uami, item):
    args = dict(target_resource_id=TARGET, recovery_point_id=RP,
                use_system_assigned_identity=system, user_assigned_identity_arm_url=uami)
    if item:
        args['restore_configuration'] = config()
    with pytest.raises(ERRORS):
        (ITEM if item else FULL)(cmd, 'AzureCosmosDB', 'VaultStore', LOCATION, **args)


def vault(snake=False):
    return {'location': LOCATION, 'identity': {
        'type': 'SystemAssigned, UserAssigned',
        'principal_id' if snake else 'principalId': SAMI_PRINCIPAL,
        'user_assigned_identities' if snake else 'userAssignedIdentities': {
            OTHER_UAMI: {'principal_id' if snake else 'principalId': OTHER_PRINCIPAL},
            UAMI: {'principal_id' if snake else 'principalId': UAMI_PRINCIPAL},
        }}}


@pytest.mark.parametrize('snake', [False, True])
@pytest.mark.parametrize('selected,expected', [
    (None, SAMI_PRINCIPAL), (UAMI, UAMI_PRINCIPAL), (UAMI.upper(), UAMI_PRINCIPAL),
    (OTHER_UAMI, OTHER_PRINCIPAL),
])
def test_P01_P02_P05_actual_strict_vault_identity_aliases_and_exact_attachment(snake, selected, expected):
    value = vault(snake)
    before = deepcopy(value)
    assert cosmosdb.get_vault_identity(value, selected) == expected
    assert value == before


def invalid_vault_cases():
    cases = [(v, UAMI) for v in [None, [], '', {}, {'identity': None}, {'identity': []}]]
    for selected in [None, UAMI]:
        for identity_type in [None, '', 'None', [], False]:
            value = vault()
            value['identity']['type'] = identity_type
            cases.append((value, selected))
    cases.extend([(vault(), UAMI + '-missing'), (vault(), '')])
    value = vault()
    value['identity']['userAssignedIdentities'][UAMI.upper()] = {'principalId': OTHER_PRINCIPAL}
    cases.append((value, UAMI))
    for attachments in [None, [], {}, 'invalid']:
        value = vault()
        value['identity']['userAssignedIdentities'] = attachments
        cases.append((value, UAMI))
    for principal in [None, '', ' ', [], {}, False, 42]:
        for selected in [None, UAMI]:
            value = vault()
            node = value['identity'] if selected is None else value['identity']['userAssignedIdentities'][UAMI]
            node['principalId'] = principal
            cases.append((value, selected))
    for attachment in [None, [], '', {}, {'principal_id': UAMI_PRINCIPAL, 'principalId': OTHER_PRINCIPAL}]:
        value = vault()
        value['identity']['userAssignedIdentities'][UAMI] = attachment
        cases.append((value, UAMI))
    value = vault()
    del value['identity']['principalId']
    cases.append((value, None))
    value = vault()
    value['identity']['type'] = 'SystemAssigned'
    cases.append((value, UAMI))
    value = vault()
    value['identity']['type'] = 'UserAssigned'
    cases.append((value, None))
    return cases


@pytest.mark.parametrize('value,selected', invalid_vault_cases())
def test_P01_P02_invalid_selected_identity_fails_closed_without_fallback(value, selected):
    before = deepcopy(value)
    with pytest.raises(InvalidArgumentValueError):
        cosmosdb.get_vault_identity(value, selected)
    assert value == before


@pytest.fixture
def permissions(monkeypatch):
    """Mock only actual vault/role boundaries; keep reconciliation/RBAC logic real."""
    state = SimpleNamespace(vault=vault(), existing=[], writes=[])

    class VaultGet:
        def __init__(self, cli_ctx):
            state.context = cli_ctx

        def __call__(self, command_args):
            state.vault_calls.append(deepcopy(command_args))
            return deepcopy(state.vault)

    state.vault_calls = []

    def list_roles(cmd, **kwargs):
        state.read_calls.append(deepcopy(kwargs))
        # Existing/inherited matches are supplied at the real list boundary.
        return deepcopy(state.existing or state.writes)

    def create_role(cmd, **kwargs):
        state.writes.append(deepcopy(kwargs))
        return SimpleNamespace(type='Microsoft.Authorization/roleAssignments', name='synthetic-assignment',
                               role_definition_id=ROLE_ID, principal_id=kwargs['assignee'],
                               scope=kwargs['scope'], principal_type='ServicePrincipal')

    state.read_calls = []
    state.prompt = Mock(return_value=True)
    state.sleep = Mock()
    monkeypatch.setattr(custom, 'BackupVaultGet', VaultGet)
    monkeypatch.setattr(helper, 'list_role_assignments', list_roles)
    monkeypatch.setattr(helper, 'create_role_assignment', create_role)
    monkeypatch.setattr(custom, 'prompt_y_n', state.prompt)
    monkeypatch.setattr(custom.time, 'sleep', state.sleep)
    return state


def grant(cmd, request, **overrides):
    args = dict(cmd=cmd, resource_group_name='restore-tests', datasource_type='AzureCosmosDB',
                vault_name='vault', operation='Restore', permissions_scope='Resource',
                restore_request_object=request, yes=True)
    args.update(overrides)
    return custom.dataprotection_backup_instance_update_msi_permissions(**args)


def permission_request(shape, identity=None):
    value = expected_request(identity=identity)
    if shape == 'wire':
        # Independent JSON shape rather than relying on the production converter.
        value = {'objectType': 'AzureBackupRecoveryPointBasedRestoreRequest',
                 'recoveryPointId': RP, 'sourceDataStoreType': 'VaultStore',
                 'restoreTargetInfo': {'objectType': 'ItemLevelRestoreTargetInfo',
                                       'recoveryOption': 'FailIfExists', 'restoreLocation': LOCATION,
                                       'datasourceInfo': {'objectType': 'Datasource',
                                                          'datasourceType': 'Microsoft.DocumentDB/databaseAccounts',
                                                          'resourceID': TARGET, 'resourceName': 'empty-target'},
                                       'restoreCriteria': [config(wire=True)]}}
        if identity is not None:
            value['identityDetails'] = deepcopy(identity)
    elif shape == 'snake-identity' and identity is not None:
        value['identity_details'] = {
            'use_system_assigned_identity': identity['useSystemAssignedIdentity']}
        if 'userAssignedIdentityArmUrl' in identity:
            value['identity_details']['user_assigned_identity_arm_url'] = identity['userAssignedIdentityArmUrl']
    return value


@pytest.mark.parametrize('shape', ['client', 'wire', 'snake-identity'])
@pytest.mark.parametrize('request_identity,flag,principal', [
    (None, None, SAMI_PRINCIPAL), (None, UAMI, UAMI_PRINCIPAL),
    ({'useSystemAssignedIdentity': True}, None, SAMI_PRINCIPAL),
    ({'useSystemAssignedIdentity': False, 'userAssignedIdentityArmUrl': UAMI}, None, UAMI_PRINCIPAL),
    ({'useSystemAssignedIdentity': False, 'userAssignedIdentityArmUrl': UAMI}, UAMI.upper(), UAMI_PRINCIPAL),
    ({'userAssignedIdentityArmUrl': UAMI, 'useSystemAssignedIdentity': False}, UAMI, UAMI_PRINCIPAL),
])
def test_P03_P05_permissions_use_request_identity_and_preserve_supported_shapes(
        cmd, permissions, shape, request_identity, flag, principal):
    value = permission_request(shape, request_identity)
    before = deepcopy(value)
    result = grant(cmd, value, user_assigned_identity_arm_url=flag)
    assert permissions.vault_calls == [{'resource_group': 'restore-tests', 'vault_name': 'vault'}]
    assert permissions.read_calls == [dict(assignee=principal, role='Cosmos DB Operator',
                                           scope=TARGET, include_inherited=True)]
    assert permissions.writes == [dict(assignee=principal, role='Cosmos DB Operator', scope=TARGET)]
    assert result == [{'ResourceType': 'Microsoft.Authorization/roleAssignments',
                       'Name': 'synthetic-assignment', 'Properties': {
                           'roleDefinitionId': ROLE_ID, 'principalId': principal,
                           'scope': TARGET, 'principalType': 'ServicePrincipal'}}]
    permissions.sleep.assert_called_once_with(60)
    permissions.prompt.assert_not_called()
    assert value == before


@pytest.mark.parametrize('shape', ['client', 'wire'])
@pytest.mark.parametrize('identity,flag', [
    ({'useSystemAssignedIdentity': True}, UAMI),
    ({'useSystemAssignedIdentity': False, 'userAssignedIdentityArmUrl': UAMI}, OTHER_UAMI),
    ({'useSystemAssignedIdentity': False}, None), ({}, None),
    ({'useSystemAssignedIdentity': True, 'userAssignedIdentityArmUrl': UAMI}, None),
    ({'useSystemAssignedIdentity': 'false', 'userAssignedIdentityArmUrl': UAMI}, None),
    ({'useSystemAssignedIdentity': False, 'userAssignedIdentityArmUrl': ''}, None),
    ({'useSystemAssignedIdentity': True, 'extra': True}, None),
    ({'userAssignedIdentityArmUrl': UAMI}, None),
    ({'useSystemAssignedIdentity': None, 'userAssignedIdentityArmUrl': UAMI}, None),
    ({'useSystemAssignedIdentity': True, 'userAssignedIdentityArmUrl': None}, None),
    ({'use_system_assigned_identity': None, 'user_assigned_identity_arm_url': UAMI}, None),
    ({'use_system_assigned_identity': True, 'user_assigned_identity_arm_url': None}, None),
    ({'useSystemAssignedIdentity': True}, ''),
    ({'useSystemAssignedIdentity': True}, ' '),
    ({'useSystemAssignedIdentity': True}, TARGET),
])
def test_P03_identity_mismatch_and_invalid_selection_have_zero_reads_or_writes(
        cmd, permissions, shape, identity, flag):
    value = permission_request(shape, identity)
    before = deepcopy(value)
    with pytest.raises(ERRORS):
        grant(cmd, value, user_assigned_identity_arm_url=flag)
    assert permissions.vault_calls == permissions.read_calls == permissions.writes == []
    permissions.sleep.assert_not_called()
    assert value == before


@pytest.mark.parametrize('value', [None, [], '', 'restore_target_info',
                                  ['restore_target_info'], False, 1, {},
                                  {'restore_target_info': None}, {'restore_target_info': []},
                                  {'restore_target_info': {'datasource_info': []}},
                                  {'restore_target_info': {'datasource_info': 'resource_id'}},
                                  {'restoreTargetInfo': {'datasourceInfo': {}}}])
def test_P05_malicious_request_root_shapes_are_usage_errors_not_python_exceptions(cmd, permissions, value):
    with pytest.raises(ERRORS):
        grant(cmd, value)
    assert permissions.vault_calls == permissions.read_calls == permissions.writes == []


@pytest.mark.parametrize('mutation', ['wrong-datasource', 'bad-target', 'duplicate-root',
                                     'duplicate-target', 'duplicate-datasource', 'duplicate-identity'])
def test_P05_conflicting_schema_aliases_and_wrong_targets_rejected_locally(cmd, permissions, mutation):
    value = expected_request(identity={'useSystemAssignedIdentity': True})
    target = value['restore_target_info']
    if mutation == 'wrong-datasource':
        target['datasource_info']['datasource_type'] = 'Microsoft.Compute/disks'
    elif mutation == 'bad-target':
        target['datasource_info']['resource_id'] = TARGET + '/sqlDatabases/db'
    elif mutation == 'duplicate-root':
        value['restoreTargetInfo'] = deepcopy(target)
    elif mutation == 'duplicate-target':
        target['datasourceInfo'] = deepcopy(target['datasource_info'])
    elif mutation == 'duplicate-datasource':
        target['datasource_info']['resourceID'] = TARGET
    else:
        value['identity_details']['use_system_assigned_identity'] = True
    before = deepcopy(value)
    with pytest.raises(ERRORS):
        grant(cmd, value)
    assert permissions.vault_calls == permissions.read_calls == permissions.writes == []
    assert value == before


@pytest.mark.parametrize('identity', [None, False, [], '', 'useSystemAssignedIdentity', 1])
def test_P05_invalid_identity_object_shape_rejects_before_vault(cmd, permissions, identity):
    value = expected_request()
    value['identity_details'] = identity
    with pytest.raises(ERRORS):
        grant(cmd, value)
    assert permissions.vault_calls == permissions.read_calls == permissions.writes == []


def test_P01_permission_command_uses_strict_resolver_without_sami_fallback(cmd, permissions):
    # SAMI is healthy, but the selected UAMI has no principal. The command must
    # fail before either role boundary, not silently authorize SAMI instead.
    permissions.vault['identity']['userAssignedIdentities'][UAMI] = {}
    value = expected_request(identity={
        'useSystemAssignedIdentity': False, 'userAssignedIdentityArmUrl': UAMI})
    with pytest.raises(InvalidArgumentValueError):
        grant(cmd, value)
    assert len(permissions.vault_calls) == 1
    assert permissions.read_calls == permissions.writes == []
    permissions.sleep.assert_not_called()


def test_P05_permission_normalization_preserves_opaque_user_maps(cmd, permissions):
    value = expected_request()
    value['restore_target_info']['restore_criteria'][0]['opaque_map'] = {
        'DB_name/Col_Name': {'User_Key': ['Keep_Case', False, {}]}}
    before = deepcopy(value)
    grant(cmd, value)
    assert value == before


def test_permissions_declined_confirmation_does_not_read_vault_or_roles(cmd, permissions):
    permissions.prompt.return_value = False
    assert grant(cmd, expected_request(), yes=False) is None
    permissions.prompt.assert_called_once()
    assert permissions.vault_calls == permissions.read_calls == permissions.writes == []
    permissions.sleep.assert_not_called()


@pytest.mark.parametrize('scope,expected_scope', [
    ('Resource', TARGET), ('ResourceGroup', RG), ('Subscription', SUB),
])
@pytest.mark.parametrize('existing_scope', [None, TARGET, RG, SUB])
@pytest.mark.parametrize('selected,principal', [(None, SAMI_PRINCIPAL), (UAMI, UAMI_PRINCIPAL)])
def test_P04_roles_are_idempotent_narrow_and_include_inherited_matches(
        cmd, permissions, scope, expected_scope, existing_scope, selected, principal):
    if existing_scope is not None:
        permissions.existing = [{'principalId': principal, 'scope': existing_scope,
                                 'roleDefinitionName': 'Cosmos DB Operator'}]
    identity = {'useSystemAssignedIdentity': True} if selected is None else {
        'useSystemAssignedIdentity': False, 'userAssignedIdentityArmUrl': selected}
    value = expected_request(identity=identity)
    first = grant(cmd, value, permissions_scope=scope)
    second = grant(cmd, value, permissions_scope=scope)
    assert second == []
    assert permissions.read_calls == [dict(assignee=principal, role='Cosmos DB Operator',
                                           scope=TARGET, include_inherited=True)] * 2
    if existing_scope is None:
        assert len(first) == 1
        assert permissions.writes == [dict(assignee=principal, role='Cosmos DB Operator', scope=expected_scope)]
        permissions.sleep.assert_called_once_with(60)
    else:
        assert first == []
        assert permissions.writes == []
        permissions.sleep.assert_not_called()


@pytest.mark.parametrize('selected', [None, UAMI])
def test_noncosmos_public_shared_vault_identity_baseline(selected):
    assert helper.get_vault_identity(vault(), selected) == (
        SAMI_PRINCIPAL if selected is None else UAMI_PRINCIPAL)


def test_regression_shared_identity_false_only_stays_legacy_empty_object():
    assert helper.get_identity_details(False, None) == {}


@pytest.mark.parametrize('target', [TARGET + '/sqlDatabases/database', 'legacy-unvalidated-target'])
def test_I05_full_cosmos_target_validation_not_incidentally_hardened(cmd, target):
    # ILR's new account-shape restriction is not a global target-ID policy.
    result = FULL(cmd, 'AzureCosmosDB', 'VaultStore', LOCATION,
                  target_resource_id=target, recovery_point_id=RP)
    assert result['restore_target_info']['object_type'] == 'RestoreTargetInfo'
    assert result['restore_target_info']['datasource_info']['resource_id'] == target
    assert 'restore_criteria' not in result['restore_target_info']


@pytest.mark.parametrize('selected,principal', [(None, SAMI_PRINCIPAL), (UAMI, UAMI_PRINCIPAL)])
def test_noncosmos_permission_command_retains_existing_shared_identity_helper(
        cmd, permissions, monkeypatch, selected, principal):
    target = RG + '/providers/Microsoft.DBforMySQL/flexibleServers/mysql-target'
    request = expected_request(item=False)
    request['restore_target_info']['datasource_info']['resource_id'] = target
    shared = Mock(wraps=helper.get_vault_identity)
    monkeypatch.setattr(helper, 'get_vault_identity', shared)
    monkeypatch.setattr(cosmosdb, 'get_vault_identity', forbidden)
    grant(cmd, request, datasource_type='AzureDatabaseForMySQL',
          target_storage_account_id=RG + '/providers/Microsoft.Storage/storageAccounts/staging',
          user_assigned_identity_arm_url=selected)
    shared.assert_called_once_with(permissions.vault, selected)
    assert all(call['assignee'] == principal for call in permissions.read_calls + permissions.writes)
    assert permissions.writes == [dict(assignee=principal, role='Storage Blob Data Contributor',
                                       scope=RG + '/providers/Microsoft.Storage/storageAccounts/staging')]


@pytest.mark.parametrize('count', [1, 2, 51])
def test_regression_esan_multiple_ids_trim_and_keep_literal_override_maps(cmd, count):
    names = ['vol_{}'.format(i) for i in range(count)]
    supplied = [' ' + name + ' ' for name in names]
    overrides = {names[0]: ' Target_Name '}
    before = deepcopy((supplied, overrides))
    actual = CONFIGURE('AzureElasticSAN', resource_identifiers=supplied,
                       resource_name_overrides=overrides)
    expected = config(names)
    expected['resource_selectors']['resource_name_overrides'] = overrides
    assert actual == expected
    assert (supplied, overrides) == before
    result = FULL(cmd, 'AzureElasticSAN', 'OperationalStore', LOCATION,
                  target_resource_id=RG + '/providers/Microsoft.ElasticSan/elasticSans/san/volumeGroups/vg',
                  recovery_point_id=RP, restore_configuration=actual)
    assert result['restore_target_info']['object_type'] == 'ItemLevelRestoreTargetInfo'
    assert result['restore_target_info']['restore_criteria'] == [expected]


def test_regression_esan_arm_id_source_and_override_name():
    volume = RG + '/providers/Microsoft.ElasticSan/elasticSans/san/volumeGroups/vg/volumes/Source_Name'
    actual = CONFIGURE('AzureElasticSAN', resource_identifiers=[' ' + volume + ' ', 'Second_Name'],
                       resource_name_overrides={'Source_Name': 'Target_Name'})
    assert actual == {'object_type': 'GenericRestoreDatasourceCriteria', 'resource_selectors': {
        'object_type': 'ResourceListSelectionCriteria', 'resource_identifiers': [volume, 'Second_Name'],
        'resource_name_overrides': {'Source_Name': 'Target_Name'}}}


@pytest.mark.parametrize('vaulted', [False, True])
@pytest.mark.parametrize('explicit', [False, True])
def test_regression_aks_exact_config_defaults_filters_hooks_staging_and_maps(cmd, vaulted, explicit):
    args = {}
    if vaulted:
        args.update(staging_resource_group_id=RG,
                    staging_storage_account_id=RG + '/providers/Microsoft.Storage/storageAccounts/staging')
    if explicit:
        args.update(excluded_resource_types=['secrets'], included_resource_types=['deployments'],
                    excluded_namespaces=['excluded'], included_namespaces=['Source_NS'],
                    label_selectors=['App_Name=Test'], persistent_volume_restore_mode='RestoreWithoutVolumeData',
                    include_cluster_scope_resources=False, namespace_mappings={'Source_NS': 'Target_NS'},
                    conflict_policy='Patch', restore_hook_references=[{'name': 'Hook_Name', 'namespace': 'Source_NS'}],
                    resource_modifier_reference={'CustomerResourceName': 'Keep_Me'})
    before = deepcopy(args)
    actual = CONFIGURE('AzureKubernetesService', **args)
    expected = {key: args.get(key) for key in [
        'excluded_resource_types', 'included_resource_types', 'excluded_namespaces', 'included_namespaces',
        'label_selectors', 'namespace_mappings', 'restore_hook_references', 'staging_resource_group_id',
        'staging_storage_account_id', 'resource_modifier_reference']}
    expected.update(object_type='KubernetesClusterVaultTierRestoreCriteria' if vaulted else 'KubernetesClusterRestoreCriteria',
                    persistent_volume_restore_mode=args.get('persistent_volume_restore_mode', 'RestoreWithVolumeData'),
                    include_cluster_scope_resources=args.get('include_cluster_scope_resources', True),
                    conflict_policy=args.get('conflict_policy', 'Skip'))
    assert actual == expected
    for initializer in [FULL, ITEM]:
        result = initializer(cmd, 'AzureKubernetesService', 'VaultStore' if vaulted else 'OperationalStore',
                             LOCATION, target_resource_id=RG + '/providers/Microsoft.ContainerService/managedClusters/target',
                             recovery_point_id=RP, restore_configuration=actual)
        assert result['restore_target_info']['restore_criteria'] == [expected]
        assert result['restore_target_info']['object_type'] == 'ItemLevelRestoreTargetInfo'
    assert args == before


@pytest.mark.parametrize('option', ['staging_resource_group_id', 'staging_storage_account_id'])
def test_regression_aks_staging_pair_still_required(option):
    with pytest.raises(InvalidArgumentValueError):
        CONFIGURE('AzureKubernetesService', **{option: RG})


@pytest.mark.parametrize('workload', ['AzureBlob', 'AzureDataLakeStorage'])
@pytest.mark.parametrize('vaulted', [False, True])
def test_regression_blob_adls_criteria_snapshot(workload, vaulted):
    # ADLS currently supports vaulted initialization only; its shared criteria
    # helper still preserves the operational range branch, without enabling PIT.
    actual = helper.get_resource_criteria_list(workload, None, ['container1', '$web'],
                                               None, None, RP if vaulted else None, None)
    if vaulted:
        assert actual == [{'object_type': 'ItemPathBasedRestoreCriteria', 'item_path': name,
                           'is_path_relative_to_backup_item': True} for name in ['container1', '$web']]
    else:
        assert actual == [{'object_type': 'RangeBasedItemLevelRestoreCriteria',
                           'min_matching_value': name, 'max_matching_value': name + '-0'}
                          for name in ['container1', '$web']]


@pytest.mark.parametrize('workload,store,rp,pit', [
    ('AzureBlob', 'OperationalStore', None, PIT),
    ('AzureBlob', 'VaultStore', RP, None), ('AzureDataLakeStorage', 'VaultStore', RP, None),
])
def test_regression_blob_adls_initializer_snapshot(cmd, workload, store, rp, pit):
    target = RG + '/providers/Microsoft.Storage/storageAccounts/storage'
    result = ITEM(cmd, workload, store, LOCATION, target_resource_id=target,
                  recovery_point_id=rp, point_in_time=pit, container_list=['container1'])
    info = datasource(target, 'Microsoft.Storage/storageAccounts/' + (
        'blobServices' if workload == 'AzureBlob' else 'adlsBlobServices'), 'Microsoft.Storage/storageAccounts')
    set_info = dict(info, object_type='DatasourceSet')
    criterion = ({'object_type': 'ItemPathBasedRestoreCriteria', 'item_path': 'container1',
                  'is_path_relative_to_backup_item': True} if rp else {
                      'object_type': 'RangeBasedItemLevelRestoreCriteria',
                      'min_matching_value': 'container1', 'max_matching_value': 'container1-0'})
    assert result == {'object_type': 'AzureBackupRecoveryPointBasedRestoreRequest' if rp else
                      'AzureBackupRecoveryTimeBasedRestoreRequest',
                      'recovery_point_id' if rp else 'recovery_point_time': rp or pit,
                      'source_data_store_type': store, 'restore_target_info': {
                          'object_type': 'ItemLevelRestoreTargetInfo', 'restore_location': LOCATION,
                          'recovery_option': 'FailIfExists', 'datasource_info': info,
                          'datasource_set_info': set_info, 'restore_criteria': [criterion]}}


@pytest.mark.parametrize('workload', ['AzureBlob', 'AzureDataLakeStorage'])
def test_regression_prefix_ranges_and_vaulted_prefix_rename_keep_arrays(workload):
    assert helper.get_resource_criteria_list(workload, None, None, ['abc/a'], ['abc/z'], None, None) == [
        {'object_type': 'RangeBasedItemLevelRestoreCriteria', 'min_matching_value': 'abc/a',
         'max_matching_value': 'abc/z'}]
    pattern = {'containers': [{'name': 'container1', 'prefixmatch': ['Case_Name/', 'db/col'],
                                'renameto': 'Target_Name'},
                               {'name': 'container2', 'renameto': 'Another_Name'}]}
    before = deepcopy(pattern)
    assert helper.get_resource_criteria_list(workload, None, None, None, None, RP, pattern) == [
        {'object_type': 'ItemPathBasedRestoreCriteria', 'item_path': 'container1',
         'is_path_relative_to_backup_item': True, 'sub_item_path_prefix': ['Case_Name/', 'db/col'],
         'rename_to': 'Target_Name'},
        {'object_type': 'ItemPathBasedRestoreCriteria', 'item_path': 'container2',
         'is_path_relative_to_backup_item': True, 'rename_to': 'Another_Name'}]
    assert pattern == before


@pytest.mark.parametrize('vaulted,count,valid', [(False, 10, True), (False, 11, False),
                                               (True, 1000, True), (True, 1001, False)])
def test_regression_blob_container_limits(vaulted, count, valid):
    containers = ['container{}'.format(i) for i in range(count)]
    if valid:
        assert len(helper.get_resource_criteria_list('AzureBlob', None, containers,
                                                     None, None, RP if vaulted else None, None)) == count
    else:
        with pytest.raises(InvalidArgumentValueError):
            helper.get_resource_criteria_list('AzureBlob', None, containers,
                                              None, None, RP if vaulted else None, None)


def test_regression_blob_mutual_exclusion_and_adls_no_pit(cmd):
    with pytest.raises(MutuallyExclusiveArgumentError):
        helper.get_resource_criteria_list('AzureBlob', None, ['container1'], ['abc'], ['xyz'], None, None)
    with pytest.raises(InvalidArgumentValueError):
        ITEM(cmd, 'AzureDataLakeStorage', 'VaultStore', LOCATION, target_resource_id=TARGET,
             point_in_time=PIT, container_list=['container1'])


LEGACY_IDENTITIES = IDENTITIES + [(False, None, None)]


@pytest.mark.parametrize('system,uami,expected_identity', LEGACY_IDENTITIES)
@pytest.mark.parametrize('flow', ['disk-full', 'blob-item-pit', 'aks-full', 'oss-full', 'oss-files',
                                  'pgflex-files', 'mysql-files', 'disk-backup'])
def test_regression_all_shared_initializer_identity_combinations(
        cmd, system, uami, expected_identity, flow):
    identity = dict(use_system_assigned_identity=system, user_assigned_identity_arm_url=uami)
    disk = RG + '/providers/Microsoft.Compute/disks/target'
    postgres = RG + '/providers/Microsoft.DBforPostgreSQL/servers/server/databases/database'
    if flow == 'disk-full':
        result = FULL(cmd, 'AzureDisk', 'OperationalStore', LOCATION, target_resource_id=disk,
                      recovery_point_id=RP, **identity)
        assert result['restore_target_info'] == {
            'object_type': 'RestoreTargetInfo', 'restore_location': LOCATION, 'recovery_option': 'FailIfExists',
            'datasource_info': datasource(disk, 'Microsoft.Compute/disks', 'Microsoft.Compute/disks')}
    elif flow == 'blob-item-pit':
        result = ITEM(cmd, 'AzureBlob', 'OperationalStore', LOCATION,
                      target_resource_id=RG + '/providers/Microsoft.Storage/storageAccounts/storage',
                      point_in_time=PIT, container_list=['container1'], **identity)
        assert result['object_type'] == 'AzureBackupRecoveryTimeBasedRestoreRequest'
    elif flow == 'aks-full':
        aks_config = CONFIGURE('AzureKubernetesService')
        result = FULL(cmd, 'AzureKubernetesService', 'OperationalStore', LOCATION,
                      target_resource_id=RG + '/providers/Microsoft.ContainerService/managedClusters/target',
                      recovery_point_id=RP, restore_configuration=aks_config, **identity)
        assert result['restore_target_info']['restore_criteria'] == [aks_config]
    elif flow == 'oss-full':
        result = FULL(cmd, 'AzureDatabaseForPostgreSQL', 'VaultStore', LOCATION,
                      target_resource_id=postgres, recovery_point_id=RP,
                      secret_store_type='AzureKeyVault', secret_store_uri='https://vault.invalid/secrets/restore',
                      **identity)
        assert result['restore_target_info'] == {
            'object_type': 'RestoreTargetInfo', 'restore_location': LOCATION, 'recovery_option': 'FailIfExists',
            'datasource_info': datasource(postgres, 'Microsoft.DBforPostgreSQL/servers/databases',
                                           'Microsoft.DBforPostgreSQL/servers/databases', uri=''),
            'datasource_set_info': {'object_type': 'DatasourceSet',
                                    'datasource_type': 'Microsoft.DBforPostgreSQL/servers/databases',
                                    'resource_name': 'server', 'resource_type': 'Microsoft.DBforPostgreSQL/servers',
                                    'resource_uri': '', 'resource_id': postgres.rsplit('/databases/', 1)[0],
                                    'resource_location': LOCATION},
            'datasource_auth_credentials': {'object_type': 'SecretStoreBasedAuthCredentials',
                                            'secret_store_resource': {'uri': 'https://vault.invalid/secrets/restore',
                                                                      'value': None, 'secret_store_type': 'AzureKeyVault'}}}
    elif flow.endswith('-files'):
        workload = {'oss-files': 'AzureDatabaseForPostgreSQL',
                    'pgflex-files': 'AzureDatabaseForPostgreSQLFlexibleServer',
                    'mysql-files': 'AzureDatabaseForMySQL'}[flow]
        result = custom.restore_initialize_for_data_recovery_as_files(
            'https://storage.invalid/container', 'Restore_Prefix', workload, 'ArchiveStore', LOCATION,
            target_resource_id=RG + '/providers/Microsoft.Storage/storageAccounts/target',
            recovery_point_id=RP, rehydration_priority='High', rehydration_duration=15, **identity)
        assert result['object_type'] == 'AzureBackupRestoreWithRehydrationRequest'
        assert result['rehydration_retention_duration'] == 'P15D'
        assert result['restore_target_info'] == {
            'object_type': 'RestoreFilesTargetInfo', 'restore_location': LOCATION, 'recovery_option': 'FailIfExists',
            'target_details': {'url': 'https://storage.invalid/container', 'file_prefix': 'Restore_Prefix',
                               'restore_target_location_type': 'AzureBlobs',
                               'target_resource_arm_id': RG + '/providers/Microsoft.Storage/storageAccounts/target'}}
    else:
        result = custom.dataprotection_backup_instance_initialize(
            'AzureDisk', disk, LOCATION,
            RG + '/providers/Microsoft.DataProtection/backupVaults/vault/backupPolicies/policy',
            snapshot_resource_group_name='snapshots', **identity)['properties']
    if expected_identity is None:
        assert 'identity_details' not in result
    else:
        assert result['identity_details'] == expected_identity


@pytest.mark.parametrize('flow', ['full', 'item', 'files', 'backup'])
def test_regression_shared_initializers_still_reject_true_with_uami(cmd, flow):
    identity = dict(use_system_assigned_identity=True, user_assigned_identity_arm_url=UAMI)
    with pytest.raises(MutuallyExclusiveArgumentError):
        if flow == 'full':
            FULL(cmd, 'AzureDisk', 'OperationalStore', LOCATION, target_resource_id=TARGET,
                 recovery_point_id=RP, **identity)
        elif flow == 'item':
            ITEM(cmd, 'AzureBlob', 'OperationalStore', LOCATION, target_resource_id=TARGET,
                 point_in_time=PIT, container_list=['container1'], **identity)
        elif flow == 'files':
            custom.restore_initialize_for_data_recovery_as_files(
                'https://storage.invalid/container', 'prefix', 'AzureDatabaseForPostgreSQL',
                'VaultStore', LOCATION, recovery_point_id=RP, **identity)
        else:
            custom.dataprotection_backup_instance_initialize(
                'AzureDisk', RG + '/providers/Microsoft.Compute/disks/disk', LOCATION,
                RG + '/providers/Microsoft.DataProtection/backupVaults/vault/backupPolicies/policy',
                snapshot_resource_group_name='snapshots', **identity)