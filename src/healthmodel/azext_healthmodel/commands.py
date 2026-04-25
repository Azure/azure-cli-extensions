# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_healthmodel._client_factory import (
    cf_health_models,
    cf_entities,
    cf_signal_definitions,
    cf_relationships,
    cf_authentication_settings,
    cf_discovery_rules,
)


def load_command_table(self, _):

    with self.command_group(
        'healthmodel',
        client_factory=cf_health_models,
        is_preview=True,
    ) as g:
        g.custom_command('create', 'health_model_create', supports_no_wait=True)
        g.custom_show_command('show', 'health_model_show')
        g.custom_command('list', 'health_model_list')
        g.custom_command('update', 'health_model_update', supports_no_wait=True)
        g.custom_command('delete', 'health_model_delete', supports_no_wait=True, confirmation=True)

    with self.command_group(
        'healthmodel entity',
        client_factory=cf_entities,
        is_preview=True,
    ) as g:
        g.custom_command('create', 'entity_create', supports_no_wait=True)
        g.custom_show_command('show', 'entity_show')
        g.custom_command('list', 'entity_list')
        g.custom_command('delete', 'entity_delete', supports_no_wait=True, confirmation=True)
        g.custom_command('get-history', 'entity_get_history')
        g.custom_command('get-signal-history', 'entity_get_signal_history')
        g.custom_command('ingest', 'entity_ingest')

    with self.command_group(
        'healthmodel signal-definition',
        client_factory=cf_signal_definitions,
        is_preview=True,
    ) as g:
        g.custom_command('create', 'signal_definition_create', supports_no_wait=True)
        g.custom_show_command('show', 'signal_definition_show')
        g.custom_command('list', 'signal_definition_list')
        g.custom_command('delete', 'signal_definition_delete', supports_no_wait=True, confirmation=True)

    with self.command_group(
        'healthmodel relationship',
        client_factory=cf_relationships,
        is_preview=True,
    ) as g:
        g.custom_command('create', 'relationship_create', supports_no_wait=True)
        g.custom_show_command('show', 'relationship_show')
        g.custom_command('list', 'relationship_list')
        g.custom_command('delete', 'relationship_delete', supports_no_wait=True, confirmation=True)

    with self.command_group(
        'healthmodel auth-setting',
        client_factory=cf_authentication_settings,
        is_preview=True,
    ) as g:
        g.custom_command('create', 'auth_setting_create', supports_no_wait=True)
        g.custom_show_command('show', 'auth_setting_show')
        g.custom_command('list', 'auth_setting_list')
        g.custom_command('delete', 'auth_setting_delete', supports_no_wait=True, confirmation=True)

    with self.command_group(
        'healthmodel discovery-rule',
        client_factory=cf_discovery_rules,
        is_preview=True,
    ) as g:
        g.custom_command('create', 'discovery_rule_create', supports_no_wait=True)
        g.custom_show_command('show', 'discovery_rule_show')
        g.custom_command('list', 'discovery_rule_list')
        g.custom_command('delete', 'discovery_rule_delete', supports_no_wait=True, confirmation=True)
