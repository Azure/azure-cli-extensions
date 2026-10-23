# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from types import SimpleNamespace
import traceback
from unittest import mock

import pytest

from azure.cli.core import get_default_cli
from azure.cli.command_modules.vm._validators import _validate_admin_password
from azure.cli.core.commands.validators import validate_tags
from azure.cli.core.azclierror import InvalidArgumentValueError
from knack.util import CLIError
from azext_vm_repair.vm_creation import create_repair_vm
from azext_vm_repair.exceptions import AzCommandError
from azext_vm_repair._validators import validate_vm_password


@pytest.mark.parametrize('unmanaged,validate', [(False, True), (False, False), (True, True), (True, False)])
def test_core_creation_prepares_arguments_and_calls_registered_handler(tmp_path, unmanaged, validate):
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
        create_repair_vm(SimpleNamespace(cli_ctx=context), arguments, validate=validate)

    assert context.invocation is original_invocation
    assert dict(context._event_handlers) == original_handlers
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
