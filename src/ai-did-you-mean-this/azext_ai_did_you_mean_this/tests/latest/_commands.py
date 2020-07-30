# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import namedtuple
from enum import Enum

from azext_ai_did_you_mean_this._parameter import (
    GLOBAL_PARAM_SHORTHAND_LOOKUP_TBL,
    GLOBAL_PARAM_LOOKUP_TBL,
    GLOBAL_PARAM_BLOCKLIST
)

GLOBAL_PARAMS = set(param for param in GLOBAL_PARAM_LOOKUP_TBL if param.startswith('--'))
GLOBAL_PARAM_WHITELIST = GLOBAL_PARAMS.difference(GLOBAL_PARAM_BLOCKLIST)
GLOBAL_PARAM_LIST = tuple(GLOBAL_PARAMS) + tuple(GLOBAL_PARAM_SHORTHAND_LOOKUP_TBL.keys())

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

GROUP_CREATE_ARGS = Arguments(
    actual=['-l', '-n', '--manag', '--tag', '--s'],
    expected=['--location', '--resource-group', '--managed-by', '--tags', '--subscription']
)


def add_global_args(args, global_args=GLOBAL_PARAM_LIST):
    expected_global_args = list(GLOBAL_PARAM_WHITELIST)
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
    GROUP_CREATE = CliCommand(
        module='group',
        command='group create',
        args=add_global_args(GROUP_CREATE_ARGS)
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
