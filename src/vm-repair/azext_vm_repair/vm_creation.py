# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from copy import copy, deepcopy

from azure.cli.core import MainCommandsLoader
from azure.cli.core.commands import AzCliCommandInvoker
from azure.cli.core.parser import AzCliCommandParser
from azure.cli.core._help import AzCliHelp
from azure.cli.core.azclierror import InvalidArgumentValueError
from knack.util import CLIError

from .exceptions import AzCommandError


class _RepairCreateParser(AzCliCommandParser):
    def error(self, message):
        raise InvalidArgumentValueError(message)


def create_repair_vm(cmd, arguments, validate=False):
    """Prepare core VM-create arguments without starting another CLI or process."""
    cli_ctx = copy(cmd.cli_ctx)
    cli_ctx.data = dict(cmd.cli_ctx.data)
    invocation = AzCliCommandInvoker(
        cli_ctx=cli_ctx, commands_loader_cls=MainCommandsLoader, parser_cls=_RepairCreateParser,
        help_cls=AzCliHelp)
    cli_ctx.invocation = invocation
    invocation.data['command_string'] = 'vm create'
    loader = invocation.commands_loader
    loader.load_command_table(['vm', 'create'])
    command = loader.command_table['vm create']
    loader.command_table = {'vm create': command}
    loader.load_arguments('vm create')
    invocation.parser.load_command_table(loader)

    tokens = ['vm', 'create']
    for name, value in arguments.items():
        if value is None or name in ('tags', 'admin_password', 'admin_username'):
            continue
        option = '--' + name.replace('_', '-')
        if isinstance(value, dict):
            tokens.append(option)
            tokens.extend('{}={}'.format(key, item) for key, item in value.items())
        elif isinstance(value, list):
            tokens.append(option)
            tokens.extend(str(item) for item in value)
        elif isinstance(value, bool) and name == 'use_unmanaged_disk':
            if value:
                tokens.append(option)
        else:
            tokens.append('{}={}'.format(option, value))
    if validate:
        tokens.append('--validate')
    try:
        namespace = invocation.parser.parse_args(tokens)
        for name in ('tags', 'admin_password', 'admin_username'):
            if name in arguments:
                setattr(namespace, name, deepcopy(arguments[name]))
        namespace.cmd = namespace._cmd = command  # pylint: disable=protected-access
        invocation._validation(namespace)  # pylint: disable=protected-access
        return invocation._run_job(namespace, command)  # pylint: disable=protected-access
    except CLIError as error:
        message = str(error)
        for name in ('admin_password', 'admin_username'):
            if arguments.get(name):
                message = message.replace(arguments[name], '********')
        raise AzCommandError(message) from None
