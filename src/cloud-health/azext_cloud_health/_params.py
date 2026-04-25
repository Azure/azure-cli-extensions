# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.parameters import (
    get_location_type,
    tags_type,
)
from azure.cli.core.commands.validators import get_default_location_from_resource_group


def _load_shared_arguments(self):
    with self.argument_context('cloud-health') as c:
        c.argument('resource_group_name', options_list=['--resource-group', '-g'],
                   help='Name of resource group.')
        c.argument('health_model_name', options_list=['--health-model-name', '--model'],
                   help='Name of the health model.')


def _load_health_model_arguments(self):
    with self.argument_context('cloud-health health-model') as c:
        c.argument('health_model_name', options_list=['--name', '-n'],
                   help='Name of the health model.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx),
                   validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)

    with self.argument_context('cloud-health health-model create') as c:
        c.argument('identity_type', options_list=['--identity-type'],
                   help='Type of managed identity. Allowed: None, SystemAssigned, UserAssigned, '
                        '"SystemAssigned,UserAssigned".')

    with self.argument_context('cloud-health health-model update') as c:
        c.argument('identity_type', options_list=['--identity-type'],
                   help='Type of managed identity.')

    with self.argument_context('cloud-health health-model list') as c:
        c.argument('resource_group_name', options_list=['--resource-group', '-g'],
                   help='Name of resource group. Omit to list across the subscription.')


def _load_entity_arguments(self):
    with self.argument_context('cloud-health entity') as c:
        c.argument('entity_name', options_list=['--name', '-n'],
                   help='Name of the entity.')

    with self.argument_context('cloud-health entity create') as c:
        c.argument('display_name', help='Display name of the entity.')
        c.argument('impact', help='Impact level: Standard, Limited, or Suppressed.')
        c.argument('health_objective', type=float,
                   help='Health objective percentage (0-100).')
        c.argument('icon_name', help='Icon name for the entity.')
        c.argument('canvas_x', type=float, help='Canvas X position.')
        c.argument('canvas_y', type=float, help='Canvas Y position.')
        c.argument('tags', tags_type)

    with self.argument_context('cloud-health entity get-history') as c:
        c.argument('start_at', help='Start time (ISO 8601). Defaults to 24h ago.')
        c.argument('end_at', help='End time (ISO 8601). Defaults to now.')

    with self.argument_context('cloud-health entity get-signal-history') as c:
        c.argument('signal_name', help='Name of the signal to get history for.')
        c.argument('start_at', help='Start time (ISO 8601).')
        c.argument('end_at', help='End time (ISO 8601).')

    with self.argument_context('cloud-health entity ingest') as c:
        c.argument('signal_name', help='Name of the signal to ingest health report for.')
        c.argument('health_state', help='Health state: Healthy, Degraded, Unhealthy, Unknown.')
        c.argument('value', type=float, help='Signal value.')
        c.argument('expires_in_minutes', type=int, help='Expiry in minutes (default 60).')
        c.argument('additional_context', help='Additional context string.')


def _load_signal_definition_arguments(self):
    with self.argument_context('cloud-health signal-definition') as c:
        c.argument('signal_definition_name', options_list=['--name', '-n'],
                   help='Name of the signal definition.')

    with self.argument_context('cloud-health signal-definition create') as c:
        c.argument('signal_kind', help='Signal kind: AzureResourceMetric, LogAnalyticsQuery, '
                                       'PrometheusMetricsQuery.')
        c.argument('display_name', help='Display name.')
        c.argument('refresh_interval', help='Refresh interval: PT1M, PT5M, PT10M, PT30M, PT1H, PT2H.')
        c.argument('data_unit', help='Data unit label.')
        c.argument('body', help='JSON body for the full signal definition properties. '
                                'Use for complex configurations.')


def _load_relationship_arguments(self):
    with self.argument_context('cloud-health relationship') as c:
        c.argument('relationship_name', options_list=['--name', '-n'],
                   help='Name of the relationship.')

    with self.argument_context('cloud-health relationship create') as c:
        c.argument('parent_entity_name', help='Name of the parent entity.')
        c.argument('child_entity_name', help='Name of the child entity.')
        c.argument('display_name', help='Display name of the relationship.')
        c.argument('tags', tags_type)


def _load_auth_setting_arguments(self):
    with self.argument_context('cloud-health auth-setting') as c:
        c.argument('authentication_setting_name', options_list=['--name', '-n'],
                   help='Name of the authentication setting.')

    with self.argument_context('cloud-health auth-setting create') as c:
        c.argument('authentication_kind', help='Authentication kind. Currently: ManagedIdentity.')
        c.argument('managed_identity_name',
                   help='Managed identity name ("SystemAssigned" or full resource ID).')
        c.argument('display_name', help='Display name.')


def _load_discovery_rule_arguments(self):
    with self.argument_context('cloud-health discovery-rule') as c:
        c.argument('discovery_rule_name', options_list=['--name', '-n'],
                   help='Name of the discovery rule.')

    with self.argument_context('cloud-health discovery-rule create') as c:
        c.argument('authentication_setting', help='Name of the authentication setting to use.')
        c.argument('discover_relationships', help='Enable relationship discovery: Enabled or Disabled.')
        c.argument('add_recommended_signals', help='Add recommended signals: Enabled or Disabled.')
        c.argument('specification_kind', help='Discovery specification kind: '
                                              'ResourceGraphQuery or ApplicationInsightsTopology.')
        c.argument('resource_graph_query', help='Resource Graph (KQL) query. '
                                                'Required when specification_kind is ResourceGraphQuery.')
        c.argument('display_name', help='Display name.')


def load_arguments(self, _):
    _load_shared_arguments(self)
    _load_health_model_arguments(self)
    _load_entity_arguments(self)
    _load_signal_definition_arguments(self)
    _load_relationship_arguments(self)
    _load_auth_setting_arguments(self)
    _load_discovery_rule_arguments(self)
