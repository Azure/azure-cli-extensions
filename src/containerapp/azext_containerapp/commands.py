# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from msrestazure.tools import is_valid_resource_id, parse_resource_id
from azext_containerapp._client_factory import ex_handler_factory


def transform_containerapp_output(app):
    props = ['name', 'location', 'resourceGroup', 'provisioningState']
    result = {k: app[k] for k in app if k in props}

    try:
        result['fqdn'] = app['properties']['configuration']['ingress']['fqdn']
    except Exception:
        result['fqdn'] = None

    return result


def transform_containerapp_list_output(apps):
    return [transform_containerapp_output(a) for a in apps]


def transform_revision_output(rev):
    props = ['name', 'replicas', 'active', 'createdTime']
    result = {k: rev[k] for k in rev if k in props}

    if 'latestRevisionFqdn' in rev['template']:
        result['fqdn'] = rev['template']['latestRevisionFqdn']

    return result


def transform_revision_list_output(revs):
    return [transform_revision_output(r) for r in revs]


def load_command_table(self, _):
    with self.command_group('containerapp') as g:
        g.custom_command('show', 'show_containerapp', table_transformer=transform_containerapp_output)
        g.custom_command('list', 'list_containerapp', table_transformer=transform_containerapp_list_output)
        g.custom_command('create', 'create_containerapp', supports_no_wait=True, exception_handler=ex_handler_factory())
        g.custom_command('scale', 'scale_containerapp', supports_no_wait=True, exception_handler=ex_handler_factory())
        g.custom_command('update', 'update_containerapp', supports_no_wait=True, exception_handler=ex_handler_factory())
        g.custom_command('delete', 'delete_containerapp', supports_no_wait=True, exception_handler=ex_handler_factory())


    with self.command_group('containerapp env') as g:
        g.custom_command('show', 'show_managed_environment')
        g.custom_command('list', 'list_managed_environments')
        g.custom_command('create', 'create_managed_environment', supports_no_wait=True, exception_handler=ex_handler_factory())
        # g.custom_command('update', 'update_managed_environment', supports_no_wait=True, exception_handler=ex_handler_factory())
        g.custom_command('delete', 'delete_managed_environment', supports_no_wait=True, confirmation=True, exception_handler=ex_handler_factory())

    with self.command_group('containerapp github-action') as g:
        g.custom_command('add', 'create_or_update_github_action', exception_handler=ex_handler_factory())
        g.custom_command('show', 'show_github_action',  exception_handler=ex_handler_factory())
        g.custom_command('delete', 'delete_github_action',  exception_handler=ex_handler_factory())

    with self.command_group('containerapp revision') as g:
        g.custom_command('activate', 'activate_revision')
        g.custom_command('deactivate', 'deactivate_revision')
        g.custom_command('list', 'list_revisions', table_transformer=transform_revision_list_output, exception_handler=ex_handler_factory())
        g.custom_command('restart', 'restart_revision')
        g.custom_command('show', 'show_revision', table_transformer=transform_revision_output, exception_handler=ex_handler_factory())
        g.custom_command('copy', 'copy_revision', exception_handler=ex_handler_factory())

    with self.command_group('containerapp revision mode') as g:
        g.custom_command('set', 'set_revision_mode', exception_handler=ex_handler_factory())

    with self.command_group('containerapp ingress') as g:
        g.custom_command('enable', 'enable_ingress', exception_handler=ex_handler_factory())
        g.custom_command('disable', 'disable_ingress', exception_handler=ex_handler_factory())
        g.custom_command('show', 'show_ingress')
    
    with self.command_group('containerapp ingress traffic') as g:
        g.custom_command('set', 'set_ingress_traffic', exception_handler=ex_handler_factory())
        g.custom_command('show', 'show_ingress_traffic')

    with self.command_group('containerapp registry') as g:
        g.custom_command('set', 'set_registry', exception_handler=ex_handler_factory())
        g.custom_command('show', 'show_registry')
        g.custom_command('list', 'list_registry')
        g.custom_command('delete', 'delete_registry', exception_handler=ex_handler_factory())

    with self.command_group('containerapp secret') as g:
        g.custom_command('list', 'list_secrets')
        g.custom_command('show', 'show_secret')
        g.custom_command('delete', 'delete_secrets', exception_handler=ex_handler_factory())
        g.custom_command('set', 'set_secrets', exception_handler=ex_handler_factory())
