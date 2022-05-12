# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long, too-many-statements, bare-except
# from azure.cli.core.commands import CliCommandType
# from msrestazure.tools import is_valid_resource_id, parse_resource_id
from azext_containerapp._client_factory import ex_handler_factory
from ._validators import validate_ssh


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


def transform_revision_output(rev):
    props = ['name', 'active', 'createdTime', 'trafficWeight', 'healthState', 'provisioningState', 'replicas']
    result = {k: rev['properties'][k] for k in rev['properties'] if k in props}

    if 'name' in rev:
        result['name'] = rev['name']

    if 'fqdn' in rev['properties']['template']:
        result['fqdn'] = rev['properties']['template']['fqdn']

    return result


def transform_revision_list_output(revs):
    return [transform_revision_output(r) for r in revs]


def load_command_table(self, _):
    with self.command_group('containerapp', is_preview=True) as g:
        g.custom_show_command('show', 'show_containerapp', table_transformer=transform_containerapp_output)
        g.custom_command('list', 'list_containerapp', table_transformer=transform_containerapp_list_output)
        g.custom_command('create', 'create_containerapp', supports_no_wait=True, exception_handler=ex_handler_factory(), table_transformer=transform_containerapp_output)
        g.custom_command('update', 'update_containerapp', supports_no_wait=True, exception_handler=ex_handler_factory(), table_transformer=transform_containerapp_output)
        g.custom_command('delete', 'delete_containerapp', supports_no_wait=True, confirmation=True, exception_handler=ex_handler_factory())
        g.custom_command('exec', 'containerapp_ssh', validator=validate_ssh)
        g.custom_command('up', 'containerapp_up', supports_no_wait=False, exception_handler=ex_handler_factory())
        g.custom_command('browse', 'open_containerapp_in_browser')

    with self.command_group('containerapp replica', is_preview=True) as g:
        g.custom_show_command('show', 'get_replica')  # TODO implement the table transformer
        g.custom_command('list', 'list_replicas')

    with self.command_group('containerapp logs', is_preview=True) as g:
        g.custom_show_command('show', 'stream_containerapp_logs', validator=validate_ssh)

    with self.command_group('containerapp env') as g:
        g.custom_show_command('show', 'show_managed_environment')
        g.custom_command('list', 'list_managed_environments')
        g.custom_command('create', 'create_managed_environment', supports_no_wait=True, exception_handler=ex_handler_factory())
        g.custom_command('delete', 'delete_managed_environment', supports_no_wait=True, confirmation=True, exception_handler=ex_handler_factory())

    with self.command_group('containerapp env dapr-component') as g:
        g.custom_command('list', 'list_dapr_components')
        g.custom_show_command('show', 'show_dapr_component')
        g.custom_command('set', 'create_or_update_dapr_component')
        g.custom_command('remove', 'remove_dapr_component')

    with self.command_group('containerapp identity') as g:
        g.custom_command('assign', 'assign_managed_identity', supports_no_wait=True, exception_handler=ex_handler_factory())
        g.custom_command('remove', 'remove_managed_identity', supports_no_wait=True, exception_handler=ex_handler_factory())
        g.custom_show_command('show', 'show_managed_identity')

    with self.command_group('containerapp github-action') as g:
        g.custom_command('add', 'create_or_update_github_action', exception_handler=ex_handler_factory())
        g.custom_show_command('show', 'show_github_action', exception_handler=ex_handler_factory())
        g.custom_command('delete', 'delete_github_action', exception_handler=ex_handler_factory())

    with self.command_group('containerapp revision') as g:
        g.custom_command('activate', 'activate_revision')
        g.custom_command('deactivate', 'deactivate_revision')
        g.custom_command('list', 'list_revisions', table_transformer=transform_revision_list_output, exception_handler=ex_handler_factory())
        g.custom_command('restart', 'restart_revision')
        g.custom_show_command('show', 'show_revision', table_transformer=transform_revision_output, exception_handler=ex_handler_factory())
        g.custom_command('copy', 'copy_revision', exception_handler=ex_handler_factory())
        g.custom_command('set-mode', 'set_revision_mode', exception_handler=ex_handler_factory())

    with self.command_group('containerapp revision label') as g:
        g.custom_command('add', 'add_revision_label')
        g.custom_command('remove', 'remove_revision_label')

    with self.command_group('containerapp ingress') as g:
        g.custom_command('enable', 'enable_ingress', exception_handler=ex_handler_factory())
        g.custom_command('disable', 'disable_ingress', exception_handler=ex_handler_factory())
        g.custom_show_command('show', 'show_ingress')

    with self.command_group('containerapp ingress traffic') as g:
        g.custom_command('set', 'set_ingress_traffic', exception_handler=ex_handler_factory())
        g.custom_show_command('show', 'show_ingress_traffic')

    with self.command_group('containerapp registry') as g:
        g.custom_command('set', 'set_registry', exception_handler=ex_handler_factory())
        g.custom_show_command('show', 'show_registry')
        g.custom_command('list', 'list_registry')
        g.custom_command('remove', 'remove_registry', exception_handler=ex_handler_factory())

    with self.command_group('containerapp secret') as g:
        g.custom_command('list', 'list_secrets')
        g.custom_show_command('show', 'show_secret')
        g.custom_command('remove', 'remove_secrets', exception_handler=ex_handler_factory())
        g.custom_command('set', 'set_secrets', exception_handler=ex_handler_factory())

    with self.command_group('containerapp dapr') as g:
        g.custom_command('enable', 'enable_dapr', exception_handler=ex_handler_factory())
        g.custom_command('disable', 'disable_dapr', exception_handler=ex_handler_factory())
