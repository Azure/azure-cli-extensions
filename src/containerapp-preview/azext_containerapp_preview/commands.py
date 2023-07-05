# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.command_modules.appservice.commands import ex_handler_factory

from ._constants import GA_CONTAINERAPP_EXTENSION_NAME
from ._utils import (_get_or_add_extension)


def transform_containerapp_output(app):
    props = ['name', 'location', 'resourceGroup', 'provisioningState']
    result = {k: app[k] for k in app if k in props}

    try:
        result['fqdn'] = app['properties']['configuration']['ingress']['fqdn']
    except:
        result['fqdn'] = None

    return result


def transform_containerapp_list_output(apps):
    return [transform_containerapp_output(a) for a in apps]


def load_command_table(self, args):
    # Only the containerapp related commands can ask the user to install the containerapp extension with target version
    if len(args) > 0 and args[0] == GA_CONTAINERAPP_EXTENSION_NAME:
        if not _get_or_add_extension(self, GA_CONTAINERAPP_EXTENSION_NAME):
            return

    with self.command_group('containerapp') as g:
        g.custom_show_command('show', 'show_containerapp', table_transformer=transform_containerapp_output, is_preview=True)
        g.custom_command('list', 'list_containerapp', table_transformer=transform_containerapp_list_output, is_preview=True)
        g.custom_command('delete', 'delete_containerapp', supports_no_wait=True, confirmation=True, exception_handler=ex_handler_factory(), is_preview=True)
        g.custom_command('delete', 'delete_containerapp', supports_no_wait=True, confirmation=True, exception_handler=ex_handler_factory())
        g.custom_command('create', 'create_containerapp', supports_no_wait=True, exception_handler=ex_handler_factory(), table_transformer=transform_containerapp_output, is_preview=True)
