# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import logging
from types import SimpleNamespace
import traceback
from unittest import mock

import pytest
import requests

from azure.cli.core import MainCommandsLoader, get_default_cli
from azure.cli.command_modules.vm._validators import _validate_admin_password
from azure.cli.command_modules.vm._template_builder import StorageProfile
from azure.cli.command_modules.vm import _vm_utils
from azure.cli.core.commands.validators import validate_tags
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.sdk.policies import SafeNetworkTraceLoggingPolicy
from azure.core.credentials import AccessToken
from azure.core.pipeline.transport import HttpTransport
from azure.core.rest._requests_basic import RestRequestsTransportResponse
from azure.mgmt.resource.resources import ResourceManagementClient
from knack.events import EVENT_INVOKER_POST_PARSE_ARGS
from knack.util import CLIError
from azext_vm_repair.vm_creation import create_repair_vm
from azext_vm_repair.exceptions import AzCommandError
from azext_vm_repair._validators import validate_vm_password


@pytest.fixture(autouse=True)
def isolated_cli_config(monkeypatch, tmp_path):
    monkeypatch.setattr('azure.cli.core._config.GLOBAL_CONFIG_DIR', str(tmp_path / 'config'))
    monkeypatch.setenv('AZURE_CONFIG_DIR', str(tmp_path / 'config'))
    monkeypatch.setenv('AZURE_EXTENSION_DIR', str(tmp_path / 'extensions'))
    monkeypatch.setattr('azure.cli.core.extension.get_extensions', lambda: [])


@pytest.mark.parametrize('use_command_index', [True, False], ids=['indexed', 'full-loader'])
@pytest.mark.parametrize('unmanaged,validate', [(False, True), (False, False), (True, True), (True, False)])
def test_core_creation_prepares_arguments_and_calls_registered_handler(
        tmp_path, monkeypatch, unmanaged, validate, use_command_index):
    monkeypatch.setenv('AZURE_CORE_USE_COMMAND_INDEX', str(use_command_index).lower())
    context = get_default_cli()
    original_invocation = context.invocation
    original_handlers = {event: list(handlers) for event, handlers in context._event_handlers.items()}
    cloud_init = tmp_path / 'cloud init.txt'
    cloud_init.write_text('#cloud-config\n', encoding='utf-8')
    arguments = {
        'resource_group': 'repair-rg', 'name': 'repair-vm', 'image': 'Ubuntu2204',
        'admin_username': 'repairuser', 'admin_password': "Password 123\"%!&'\\",
        'tags': {'owner': "R&D O'Brien", 'empty': ''}, 'public_ip_address': '',
        'size': 'Standard_D2s_v3', 'zone': '1', 'disk_controller_type': 'SCSI',
        'security_type': 'Standard', 'use_unmanaged_disk': unmanaged,
        'enable_secure_boot': False, 'enable_vtpm': False, 'storage_sku': 'Standard_LRS',
        'custom_data': str(cloud_init),
    }
    captured = {}
    loaded_commands = {}
    load_command_table = MainCommandsLoader.load_command_table

    def load(loader, args):
        table = load_command_table(loader, args)
        loaded_commands.update(table)
        return table

    monkeypatch.setattr(MainCommandsLoader, 'load_command_table', load)

    def handler(command_args):
        captured.update(command_args)
        assert command_args['cmd'].name == 'vm create'
        return {'id': '/subscriptions/sub/resourceGroups/repair-rg/providers/Microsoft.Compute/virtualMachines/vm'}

    def prepare(cmd, namespace):
        validate_tags(namespace)
        for os_type in ('Linux', 'Windows'):
            _validate_admin_password(namespace.admin_password, os_type)
            validate_vm_password(namespace.admin_password, os_type == 'Linux')
        namespace.disk_info = {'os': {'storageAccountType': 'Standard_LRS'}}
    with mock.patch('azure.cli.command_modules.vm.commands.process_vm_create_namespace', prepare), \
            mock.patch('azure.cli.core.commands.command_operation.CommandOperation.handler', side_effect=handler):
        result = create_repair_vm(SimpleNamespace(cli_ctx=context), arguments, validate=validate)

    assert result['id'].endswith('/virtualMachines/vm')
    assert ('storage account create' in loaded_commands) is not use_command_index
    assert context.invocation is original_invocation
    assert dict(context._event_handlers) == original_handlers
    assert captured['vm_name'] == arguments['name']
    assert captured['resource_group_name'] == arguments['resource_group']
    assert captured['admin_password'] == arguments['admin_password']
    assert captured['tags'] == arguments['tags']
    assert captured['public_ip_address'] == ''
    assert captured['use_unmanaged_disk'] == unmanaged
    assert captured['validate'] == validate
    assert captured['disk_info']['os']['storageAccountType'] == 'Standard_LRS'
    assert captured['zone'] == ['1']
    assert captured['disk_controller_type'] == 'SCSI'
    assert captured['security_type'] == 'Standard'
    assert captured['enable_secure_boot'] is False
    assert captured['enable_vtpm'] is False
    assert captured['storage_sku'] == ['Standard_LRS']
    assert captured['custom_data'] == arguments['custom_data'] == str(cloud_init)


@pytest.mark.parametrize('failure_stage', [None, 'load', 'arguments', 'validation'],
                         ids=['success', 'load-error', 'argument-error', 'validation-error'])
def test_core_creation_isolates_parent_event_handlers(monkeypatch, failure_stage):
    monkeypatch.setenv('AZURE_CORE_USE_COMMAND_INDEX', 'false')
    context = get_default_cli()
    existing_handler = mock.Mock()
    added_handler = mock.Mock()
    context.register_event(EVENT_INVOKER_POST_PARSE_ARGS, existing_handler)
    original_invocation = context.invocation
    original_data = context.data
    original_values = dict(original_data)
    original_registry = context._event_handlers
    original_lists = dict(original_registry)
    original_handlers = {event: list(handlers) for event, handlers in original_registry.items()}
    children = []
    load_command_table = MainCommandsLoader.load_command_table

    def load(loader, args):
        children.append(loader.cli_ctx)
        table = load_command_table(loader, args)
        loader.cli_ctx.register_event(EVENT_INVOKER_POST_PARSE_ARGS, added_handler)
        loader.cli_ctx.register_event('Repair.Test.NewEvent', added_handler)
        loader.cli_ctx.data['repair_only'] = True
        if failure_stage == 'load':
            raise CLIError('repair setup failed')
        return table

    def prepare(cmd, namespace):
        if failure_stage == 'validation':
            raise InvalidArgumentValueError('invalid repair settings')

    monkeypatch.setattr(MainCommandsLoader, 'load_command_table', load)
    arguments = {'resource_group': 'rg', 'name': 'repair', 'image': 'Ubuntu2204'}
    if failure_stage == 'arguments':
        arguments['invalid_repair_option'] = 'invalid'
    vm_id = '/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/repair-vm'
    with mock.patch('azure.cli.command_modules.vm.commands.process_vm_create_namespace', prepare), \
            mock.patch('azure.cli.core.commands.command_operation.CommandOperation.handler',
                       return_value={'id': vm_id}) as deploy:
        if failure_stage:
            expected_error = CLIError if failure_stage == 'load' else AzCommandError
            with pytest.raises(expected_error):
                create_repair_vm(SimpleNamespace(cli_ctx=context), arguments)
            deploy.assert_not_called()
        else:
            assert create_repair_vm(SimpleNamespace(cli_ctx=context), arguments)['id'] == vm_id
            deploy.assert_called_once()

    assert context.invocation is original_invocation
    assert context.data is original_data
    assert context.data == original_values
    assert context._event_handlers is original_registry
    assert dict(original_registry) == original_handlers
    assert len(children) == 1
    child = children[0]
    assert child.data is not original_data
    assert child._event_handlers is not original_registry
    for event, handlers in original_lists.items():
        assert original_registry[event] is handlers
        assert child._event_handlers[event] is not handlers
    assert child._event_handlers[EVENT_INVOKER_POST_PARSE_ARGS][-2] is existing_handler
    assert child._event_handlers[EVENT_INVOKER_POST_PARSE_ARGS][-1] is added_handler
    assert child._event_handlers['Repair.Test.NewEvent'] == [added_handler]


def test_core_creation_validation_failure_does_not_deploy():
    def reject(cmd, namespace):
        raise InvalidArgumentValueError('invalid repair settings')

    with mock.patch('azure.cli.command_modules.vm.commands.process_vm_create_namespace', reject), \
            mock.patch('azure.cli.core.commands.AzCliCommandInvoker._run_job') as deploy:
        with pytest.raises(AzCommandError, match='invalid repair settings'):
            create_repair_vm(SimpleNamespace(cli_ctx=get_default_cli()), {
                'resource_group': 'rg', 'name': 'repair', 'image': 'Ubuntu2204'})
    deploy.assert_not_called()


@pytest.mark.parametrize('during_validation', [True, False])
def test_core_creation_redacts_credentials_from_errors(during_validation):
    arguments = {
        'resource_group': 'rg', 'name': 'repair', 'image': 'Ubuntu2204',
        'admin_username': 'private-user', 'admin_password': "Private password\"%!&'\\",
    }
    error = CLIError('failed for {} using {}'.format(
        arguments['admin_username'], arguments['admin_password']))
    validator = mock.Mock(side_effect=error if during_validation else None)
    with mock.patch('azure.cli.command_modules.vm.commands.process_vm_create_namespace', validator), \
            mock.patch('azure.cli.core.commands.command_operation.CommandOperation.handler',
                       side_effect=error) as handler:
        with pytest.raises(AzCommandError) as raised:
            create_repair_vm(SimpleNamespace(cli_ctx=get_default_cli()), arguments)
    if during_validation:
        handler.assert_not_called()
    else:
        handler.assert_called_once()
    rendered = ''.join(traceback.format_exception(raised.value))
    assert arguments['admin_username'] not in rendered
    assert arguments['admin_password'] not in rendered
    assert '********' in str(raised.value)


@pytest.mark.parametrize('unmanaged,level,validate,fail_request', [
    (False, logging.INFO, True, False),
    (False, logging.DEBUG, True, False),
    (True, logging.DEBUG, True, False),
    (False, logging.DEBUG, False, False),
    (True, logging.DEBUG, False, False),
    (True, logging.DEBUG, True, True),
    (True, logging.DEBUG, False, True),
], ids=['managed-verbose', 'managed-validation-debug', 'unmanaged-validation-debug',
        'managed-deployment-debug', 'unmanaged-deployment-debug',
        'failed-validation', 'failed-deployment'])
def test_real_core_creation_does_not_log_credentials(
        monkeypatch, caplog, unmanaged, level, validate, fail_request):
    password = 'Validation password "quoted" \\ secret!234'
    arguments = {
        'resource_group': 'repair-rg', 'name': 'repair-vm',
        'image': 'Win2022Datacenter', 'admin_username': 'repairuser',
        'admin_password': password, 'use_unmanaged_disk': unmanaged,
    }
    transport = mock.Mock(spec=HttpTransport)
    client = ResourceManagementClient(
        mock.Mock(spec=['get_token'], get_token=mock.Mock(return_value=AccessToken('test-token', 2 ** 63))),
        'sub', transport=transport, logging_policy=SafeNetworkTraceLoggingPolicy())
    sent = []

    def send(request, **_kwargs):
        body = json.loads(request.body)
        sent.append((request.method, request.url, body))
        network_logger.warning('Repair HTTP warning remains visible')
        # Echo secure parameters to cover response logging as well as request logging.
        response_body = {'properties': {
            'provisioningState': 'Succeeded', 'parameters': body['properties']['parameters']}}
        if fail_request:
            response_body['error'] = {'code': 'InvalidTemplateDeployment', 'message': 'ARM request failed'}
        response = requests.Response()
        response.status_code = 400 if fail_request else 200
        response.headers['Content-Type'] = 'application/json'
        response._content = json.dumps(response_body).encode('utf-8')  # pylint: disable=protected-access
        response._content_consumed = True  # pylint: disable=protected-access
        return RestRequestsTransportResponse(request=request, internal_response=response, block_size=4096)

    transport.send.side_effect = send

    def prepare(cmd, namespace):
        namespace.disk_info = {'os': {'storageAccountType': 'Standard_LRS'}}
        namespace.storage_profile = StorageProfile.SAPirImage if unmanaged else StorageProfile.ManagedPirImage
        namespace.storage_account = 'repairsa'
        namespace.location = 'westus'
        namespace.os_type = 'Windows'
        namespace.nics = [{'id': '/subscriptions/sub/resourceGroups/repair-rg/'
                           'providers/Microsoft.Network/networkInterfaces/repair-nic'}]
        _vm_utils.logger.warning('Repair validation warning remains visible')

    monkeypatch.setattr('azure.cli.command_modules.vm.commands.process_vm_create_namespace', prepare)
    monkeypatch.setattr('azure.cli.command_modules.vm.custom.get_subscription_id', lambda _: 'sub')
    monkeypatch.setattr(
        'azure.cli.command_modules.vm.custom.get_mgmt_service_client',
        mock.Mock(return_value=client))
    monkeypatch.setattr('azure.cli.command_modules.vm.custom.get_vm_details', mock.Mock(return_value={
        'id': '/subscriptions/sub/resourceGroups/repair-rg/providers/Microsoft.Compute/virtualMachines/repair-vm'}))
    caplog.set_level(level, logger='cli')
    network_logger = logging.getLogger('cli.azure.cli.core.sdk.policies')
    original_filters = {logger: list(logger.filters) for logger in (_vm_utils.logger, network_logger)}

    if fail_request:
        with pytest.raises(AzCommandError, match='ARM request failed'):
            create_repair_vm(SimpleNamespace(cli_ctx=get_default_cli()), arguments, validate=validate)
    else:
        create_repair_vm(SimpleNamespace(cli_ctx=get_default_cli()), arguments, validate=validate)

    assert len(sent) == 1
    method, url, deployment = sent[0]
    assert method == ('POST' if validate else 'PUT')
    assert ('/validate?' in url) == validate
    assert deployment['properties']['parameters']['adminPassword']['value'] == password
    assert password not in caplog.text
    assert json.dumps(password)[1:-1] not in caplog.text
    assert 'Request body:' not in caplog.text
    assert 'Response content:' not in caplog.text
    assert 'Repair validation warning remains visible' in caplog.text
    assert 'Repair HTTP warning remains visible' in caplog.text
    for logger, filters in original_filters.items():
        assert logger.filters == filters
    _vm_utils.log_pprint_template({'after_validation': 'logging restored'})
    assert 'logging restored' in caplog.text
    caplog.set_level(logging.DEBUG, logger=network_logger.name)
    fail_request = False
    client.deployments.begin_validate('repair-rg', 'after-repair', {
        'properties': {'mode': 'Incremental', 'template': {}, 'parameters': {}}})
    assert 'Request body:' in caplog.text
    assert 'Response content:' in caplog.text
