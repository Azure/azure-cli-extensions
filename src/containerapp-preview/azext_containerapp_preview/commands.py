# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.command_modules.appservice.commands import ex_handler_factory


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


# This method cannot directly rely on GA resources.
# When the switch core.use_command_index is turned off, possibly unrelated commands may also trigger unnecessary loads.
# It will throw a warning if the GA resource does not exist.
def load_command_table(self, _):

    with self.command_group('containerapp') as g:
        g.custom_show_command('show', 'show_containerapp', table_transformer=transform_containerapp_output, is_preview=True)
        g.custom_command('list', 'list_containerapp', table_transformer=transform_containerapp_list_output, is_preview=True)
        g.custom_command('delete', 'delete_containerapp', supports_no_wait=True, confirmation=True, exception_handler=ex_handler_factory(), is_preview=True)
        g.custom_command('create', 'create_containerapp', supports_no_wait=True, exception_handler=ex_handler_factory(), table_transformer=transform_containerapp_output, is_preview=True)
