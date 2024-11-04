# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import json
from os.path import expanduser
from docutils import nodes
from docutils.statemachine import ViewList
from docutils.parsers.rst import Directive
from sphinx.util.nodes import nested_parse_with_titles

from knack.help_files import helps

from knack.help import GroupHelpFile
from azure.cli.core import MainCommandsLoader, AzCli
from azure.cli.core.commands import AzCliCommandInvoker, ExtensionCommandSource
from azure.cli.core.parser import AzCliCommandParser
from azure.cli.core._help import AzCliHelp, CliCommandHelpFile, ArgumentGroupRegistry

USER_HOME = expanduser('~')


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

class AzHelpGenDirective(Directive):
    def make_rst(self):
        INDENT = '   '
        DOUBLEINDENT = INDENT * 2

        az_cli = AzCli(cli_name='az',
               commands_loader_cls=MainCommandsLoader,
               invocation_cls=AzCliCommandInvoker,
               parser_cls=AzCliCommandParser,
               help_cls=AzCliHelp)
        help_files = get_extension_help_files(az_cli)

        for help_file in help_files:
            is_command = isinstance(help_file, CliCommandHelpFile)
            yield '.. cli{}:: {}'.format('command' if is_command else 'group', help_file.command if help_file.command else 'az') #it is top level group az if command is empty
            yield ''
            yield '{}:summary: {}'.format(INDENT, help_file.short_summary)
            yield '{}:description: {}'.format(INDENT, help_file.long_summary)
            if help_file.deprecate_info:
                yield '{}:deprecated: {}'.format(INDENT, help_file.deprecate_info._get_message(help_file.deprecate_info))
            yield ''

            if is_command and help_file.parameters:
               group_registry = ArgumentGroupRegistry([p.group_name for p in help_file.parameters if p.group_name]) 

               for arg in sorted(help_file.parameters,
                                key=lambda p: group_registry.get_group_priority(p.group_name)
                                + str(not p.required) + p.name):
                    yield '{}.. cliarg:: {}'.format(INDENT, arg.name)
                    yield ''
                    yield '{}:required: {}'.format(DOUBLEINDENT, arg.required)
                    if arg.deprecate_info:
                        yield '{}:deprecated: {}'.format(DOUBLEINDENT, arg.deprecate_info._get_message(arg.deprecate_info))
                    short_summary = arg.short_summary or ''
                    possible_values_index = short_summary.find(' Possible values include')
                    short_summary = short_summary[0:possible_values_index
                                                if possible_values_index >= 0 else len(short_summary)]
                    short_summary = short_summary.strip()
                    yield '{}:summary: {}'.format(DOUBLEINDENT, short_summary)
                    yield '{}:description: {}'.format(DOUBLEINDENT, arg.long_summary)
                    if arg.choices:
                        yield '{}:values: {}'.format(DOUBLEINDENT, ', '.join(sorted([str(x) for x in arg.choices])))
                    if arg.default and arg.default != argparse.SUPPRESS:
                        try:
                            if arg.default.startswith(USER_HOME):
                                arg.default = arg.default.replace(USER_HOME, '~').replace('\\', '/')
                        except Exception:
                            pass
                        try:
                            arg.default = arg.default.replace("\\", "\\\\")
                        except Exception:
                            pass
                        yield '{}:default: {}'.format(DOUBLEINDENT, arg.default)
                    if arg.value_sources:
                        yield '{}:source: {}'.format(DOUBLEINDENT, ', '.join(_get_populator_commands(arg)))
                    yield ''
            yield ''
            if len(help_file.examples) > 0:
               for e in help_file.examples:
                  fields = _get_example_fields(e)
                  yield '{}.. cliexample:: {}'.format(INDENT, fields['summary'])
                  yield ''
                  yield DOUBLEINDENT + fields['command'].replace("\\", "\\\\")
                  yield ''

    def run(self):
        node = nodes.section()
        node.document = self.state.document
        result = ViewList()
        for line in self.make_rst():
            result.append(line, '<azhelpgen>')

        nested_parse_with_titles(self.state, result, node)
        return node.children

def setup(app):
    app.add_directive('azhelpgen', AzHelpGenDirective)


def _store_parsers(parser, parser_keys, parser_values, sub_parser_keys, sub_parser_values):
    for s in parser.subparsers.values():
        parser_keys.append(_get_parser_name(s))
        parser_values.append(s)
        if _is_group(s):
            for c in s.choices.values():
                sub_parser_keys.append(_get_parser_name(c))
                sub_parser_values.append(c)
                _store_parsers(c, parser_keys, parser_values, sub_parser_keys, sub_parser_values)

def _is_group(parser):
    return getattr(parser, '_subparsers', None) is not None \
        or getattr(parser, 'choices', None) is not None

def _get_parser_name(s):
    return (s._prog_prefix if hasattr(s, '_prog_prefix') else s.prog)[3:]


def _get_populator_commands(param):
    commands = []
    for value_source in param.value_sources:
        try:
            commands.append(value_source["link"]["command"])
        except TypeError:  # old value_sources are strings
            commands.append(value_source)
        except KeyError:  # new value_sources are dicts
            continue
    return commands

def _get_example_fields(ex):
    res = {}
    try:
        res['summary'] = ex.short_summary
        res['command'] = ex.command
    except AttributeError:
        res['summary'] = ex.name
        res['command'] = ex.text

    return res