#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Check format of service_name.json. Command and AzureServiceName are required. Others are optional.
Each highest level command group should have reference in service_name.json.
"""
import json

from azure.cli.core import MainCommandsLoader, AzCli
from azure.cli.core._help import AzCliHelp, CliCommandHelpFile
from azure.cli.core.commands import AzCliCommandInvoker, ExtensionCommandSource
from azure.cli.core.parser import AzCliCommandParser
from knack.help import GroupHelpFile


def get_extension_help_files(cli_ctx):

    # 1. Create invoker and load command table and arguments. Remember to turn off applicability check.
    invoker = cli_ctx.invocation_cls(cli_ctx=cli_ctx, commands_loader_cls=cli_ctx.commands_loader_cls,
                                     parser_cls=cli_ctx.parser_cls, help_cls=cli_ctx.help_cls)
    cli_ctx.invocation = invoker

    invoker.commands_loader.skip_applicability = True
    cmd_table = invoker.commands_loader.load_command_table(None)

    #   turn off applicability check for all loaders
    for loaders in invoker.commands_loader.cmd_to_loader_map.values():
        for loader in loaders:
            loader.skip_applicability = True

    #   filter the command table to only get commands from extensions
    cmd_table = {k: v for k, v in cmd_table.items() if isinstance(v.command_source, ExtensionCommandSource)}
    invoker.commands_loader.command_table = cmd_table
    print('FOUND {} command(s) from the extension.'.format(len(cmd_table)))

    for cmd_name in cmd_table:
        invoker.commands_loader.load_arguments(cmd_name)

    invoker.parser.load_command_table(invoker.commands_loader)

    # 2. Now load applicable help files
    parser_keys = []
    parser_values = []
    sub_parser_keys = []
    sub_parser_values = []
    _store_parsers(invoker.parser, parser_keys, parser_values, sub_parser_keys, sub_parser_values)
    for cmd, parser in zip(parser_keys, parser_values):
        if cmd not in sub_parser_keys:
            sub_parser_keys.append(cmd)
            sub_parser_values.append(parser)
    help_ctx = cli_ctx.help_cls(cli_ctx=cli_ctx)
    help_files = []
    for cmd, parser in zip(sub_parser_keys, sub_parser_values):
        try:
            help_file = GroupHelpFile(help_ctx, cmd, parser) if _is_group(parser) \
                else CliCommandHelpFile(help_ctx, cmd, parser)
            help_file.load(parser)
            help_files.append(help_file)
        except Exception as ex:
            print("Skipped '{}' due to '{}'".format(cmd, ex))
    help_files = sorted(help_files, key=lambda x: x.command)
    return help_files


def _store_parsers(parser, parser_keys, parser_values, sub_parser_keys, sub_parser_values):
    for s in parser.subparsers.values():
        parser_keys.append(_get_parser_name(s))
        parser_values.append(s)
        if _is_group(s):
            for c in s.choices.values():
                sub_parser_keys.append(_get_parser_name(c))
                sub_parser_values.append(c)
                _store_parsers(c, parser_keys, parser_values, sub_parser_keys, sub_parser_values)


def _get_parser_name(s):
    return (s._prog_prefix if hasattr(s, '_prog_prefix') else s.prog)[3:]


def _is_group(parser):
    return getattr(parser, '_subparsers', None) is not None \
        or getattr(parser, 'choices', None) is not None


def check():
    az_cli = AzCli(cli_name='az',
                   commands_loader_cls=MainCommandsLoader,
                   invocation_cls=AzCliCommandInvoker,
                   parser_cls=AzCliCommandParser,
                   help_cls=AzCliHelp)
    help_files = get_extension_help_files(az_cli)
    # High command represents left most word in a command, e.g., vm, disk.
    high_command_set = set()
    for help_file in help_files:
        if help_file.command:
            high_command_set.add(help_file.command.split()[0])
    print('high_command_set:')
    print(high_command_set)

    # Load and check service_name.json
    with open('src/service_name.json') as f:
        service_names = json.load(f)
    print('Verifying src/service_name.json')
    service_name_map = {}
    for service_name in service_names:
        command = service_name['Command']
        service = service_name['AzureServiceName']
        if not command.startswith('az '):
            raise Exception('{} does not start with az!'.format(command))
        if not service:
            raise Exception('AzureServiceName of {} is empty!'.format(command))
        service_name_map[command[3:]] = service
    print('service_name_map:')
    print(service_name_map)

    # Check existence in service_name.json
    for high_command in high_command_set:
        if high_command not in service_name_map:
            raise Exception('No entry of {} in service_name.json. Please add one to the file.'.format(high_command))


if __name__ == "__main__":
    check()
