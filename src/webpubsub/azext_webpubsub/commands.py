# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azure.cli.core.util import empty_on_404
from ._client_factory import (cf_webpubsub, cf_webpubsubhub, cf_webpubsubhub_usage, cf_webpubsub_replicas)
from ._exception_handler import exception_handler


def load_command_table(self, _):

    webpubsub_general_utils = CliCommandType(
        operations_tmpl='azext_webpubsub.custom#{}',
        client_factory=cf_webpubsub
    )

    webpubsub_key_utils = CliCommandType(
        operations_tmpl='azext_webpubsub.key#{}',
        client_factory=cf_webpubsub
    )

    webpubsub_network_utils = CliCommandType(
        operations_tmpl='azext_webpubsub.network#{}',
        client_factory=cf_webpubsub
    )

    webpubsub_hub_utils = CliCommandType(
        operations_tmpl='azext_webpubsub.eventhandler#{}',
        client_factory=cf_webpubsubhub
    )

    webpubsub_client_utils = CliCommandType(
        operations_tmpl='azext_webpubsub.client#{}',
        client_factory=cf_webpubsub
    )

    webpubsub_service_utils = CliCommandType(
        operations_tmpl='azext_webpubsub.service#{}',
        client_factory=cf_webpubsub
    )

    webpubsub_usage_utils = CliCommandType(
        operations_tmpl='azext_webpubsub.custom#{}',
        client_factory=cf_webpubsubhub_usage
    )

    webpubsub_replica_utils = CliCommandType(
        operations_tmpl='azext_webpubsub.replica#{}',
        client_factory=cf_webpubsub_replicas
    )

    with self.command_group('webpubsub', webpubsub_general_utils) as g:
        g.command('create', 'webpubsub_create', exception_handler=exception_handler)
        g.command('delete', 'webpubsub_delete')
        g.command('list', 'webpubsub_list')
        g.show_command('show', 'webpubsub_show', exception_handler=empty_on_404)
        g.command('restart', 'webpubsub_restart', exception_handler=empty_on_404)
        g.generic_update_command('update', getter_name='webpubsub_get',
                                 setter_name='webpubsub_set',
                                 custom_func_name='update_webpubsub', exception_handler=exception_handler)
        g.command('list-usage', 'webpubsub_usage', command_type=webpubsub_usage_utils)
        g.command('list-skus', 'webpubsub_skus')

    with self.command_group('webpubsub key', webpubsub_key_utils) as g:
        g.show_command('show', 'webpubsub_key_list')
        g.command('regenerate', 'webpubsub_key_regenerate')

    with self.command_group('webpubsub network-rule', webpubsub_network_utils) as g:
        g.show_command('show', 'list_network_rules')
        g.command('update', 'update_network_rules')

    with self.command_group('webpubsub hub', webpubsub_hub_utils) as g:
        g.command('delete', 'hub_delete')
        g.generic_update_command('update', getter_name='get_hub', setter_name='set_hub', custom_func_name='update', custom_func_type=webpubsub_hub_utils, exception_handler=exception_handler)
        g.command('create', 'hub_create', exception_handler=exception_handler)
        g.show_command('show', 'hub_show', exception_handler=empty_on_404)
        g.command('list', 'hub_list')

    with self.command_group('webpubsub client', webpubsub_client_utils) as g:
        g.command('start', 'start_client')

    with self.command_group('webpubsub service', webpubsub_service_utils) as g:
        g.command('broadcast', 'broadcast')

    with self.command_group('webpubsub service connection', webpubsub_service_utils) as g:
        g.command('exist', 'check_connection_exists')
        g.command('close', 'close_connection')
        g.command('send', 'send_connection')

    with self.command_group('webpubsub service group', webpubsub_service_utils) as g:
        g.command('add-connection', 'add_connection_to_group')
        g.command('remove-connection', 'remove_connection_from_group')
        g.command('send', 'send_group')
        g.command('add-user', 'add_user_to_group')
        g.command('remove-user', 'remove_user_from_group')

    with self.command_group('webpubsub service user', webpubsub_service_utils) as g:
        g.command('send', 'send_user')
        g.command('exist', 'check_user_exists')

    with self.command_group('webpubsub service permission', webpubsub_service_utils) as g:
        g.command('grant', 'grant_permission')
        g.command('revoke', 'revoke_permission')
        g.command('check', 'check_permission')

    with self.command_group('webpubsub replica', webpubsub_replica_utils) as g:
        g.command('create', 'webpubsub_replica_create')
        g.command('list', 'webpubsub_replica_list')
        g.show_command('show', 'webpubsub_replica_show', exception_handler=empty_on_404)
        g.show_command('delete', 'webpubsub_replica_delete')
