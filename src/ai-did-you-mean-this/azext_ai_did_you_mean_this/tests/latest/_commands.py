# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import namedtuple
from enum import Enum

GLOBAL_ARGS = set(('--debug', '--verbose', '--help', '--only-show-errors', '--output', '--query'))
GLOBAL_ARG_BLACKLIST = set(('--debug', '--verbose'))
GLOBAL_ARG_WHITELIST = GLOBAL_ARGS.difference(GLOBAL_ARG_BLACKLIST)
GLOBAL_ARGS_SHORTHAND_MAP = {'-h': '--help', '-o': '--output'}
GLOBAL_ARG_LIST = tuple(GLOBAL_ARGS) + tuple(GLOBAL_ARGS_SHORTHAND_MAP.keys())

Arguments = namedtuple('Arguments', ['actual', 'expected'])
CliCommand = namedtuple('CliCommand', ['module', 'command', 'args'])


def get_expected_args(args):
    return [arg for arg in args if arg.startswith('--')]


VM_MODULE_ARGS = ['-g', '--name', '-n', '--resource-group', '--subscription']
VM_MODULE_EXPECTED_ARGS = get_expected_args(VM_MODULE_ARGS)

VM_SHOW_ARGS = Arguments(
    actual=VM_MODULE_ARGS,
    expected=VM_MODULE_EXPECTED_ARGS
)

_VM_CREATE_ARGS = ['--zone', '-z', '--vmss', '--location', '-l', '--nsg', '--subnet']

VM_CREATE_ARGS = Arguments(
    actual=VM_MODULE_ARGS + _VM_CREATE_ARGS,
    expected=VM_MODULE_EXPECTED_ARGS + get_expected_args(_VM_CREATE_ARGS)
)

ACCOUNT_ARGS = Arguments(
    actual=[],
    expected=[]
)

ACCOUNT_SET_ARGS = Arguments(
    actual=['-s', '--subscription'],
    expected=['--subscription']
)

EXTENSION_LIST_ARGS = Arguments(
    actual=['--foo', '--bar'],
    expected=[]
)

AI_DID_YOU_MEAN_THIS_VERSION_ARGS = Arguments(
    actual=['--baz'],
    expected=[]
)

KUSTO_CLUSTER_CREATE_ARGS = Arguments(
    actual=['-l', '-g', '--no-wait'],
    expected=['--location', '--resource-group', '--no-wait']
)


def add_global_args(args, global_args=GLOBAL_ARG_LIST):
    expected_global_args = list(GLOBAL_ARG_WHITELIST)
    args.actual.extend(global_args)
    args.expected.extend(expected_global_args)
    return args


class AzCommandType(Enum):
    VM_SHOW = CliCommand(
        module='vm',
        command='vm show',
        args=add_global_args(VM_SHOW_ARGS)
    )
    VM_CREATE = CliCommand(
        module='vm',
        command='vm create',
        args=add_global_args(VM_CREATE_ARGS)
    )
    ACCOUNT = CliCommand(
        module='account',
        command='account',
        args=add_global_args(ACCOUNT_ARGS)
    )
    ACCOUNT_SET = CliCommand(
        module='account',
        command='account set',
        args=add_global_args(ACCOUNT_SET_ARGS)
    )
    EXTENSION_LIST = CliCommand(
        module='extension',
        command='extension list',
        args=add_global_args(EXTENSION_LIST_ARGS)
    )
    AI_DID_YOU_MEAN_THIS_VERSION = CliCommand(
        module='ai-did-you-mean-this',
        command='ai-did-you-mean-this version',
        args=add_global_args(AI_DID_YOU_MEAN_THIS_VERSION_ARGS)
    )
    KUSTO_CLUSTER_CREATE = CliCommand(
        module='kusto',
        command='kusto cluster create',
        args=add_global_args(KUSTO_CLUSTER_CREATE_ARGS)
    )

    def __init__(self, module, command, args):
        self._expected_args = list(sorted(args.expected))
        self._args = args.actual
        self._module = module
        self._command = command

    @property
    def parameters(self):
        return self._args

    @property
    def expected_parameters(self):
        return ','.join(self._expected_args)

    @property
    def module(self):
        return self._module

    @property
    def command(self):
        return self._command


def get_commands():
    return list({command_type.command for command_type in AzCommandType})
