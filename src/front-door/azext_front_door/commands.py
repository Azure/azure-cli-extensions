# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType

from .custom import (
    list_frontdoor_resource_property, get_frontdoor_resource_property_entry, delete_frontdoor_resource_property_entry)
from ._client_factory import cf_frontdoor, cf_fd_endpoints, cf_waf_policies, cf_fd_rules_engines


# pylint: disable=too-many-locals, too-many-statements
def load_command_table(self, _):

    # frontdoor_custom = CliCommandType(operations_tmpl='azext_front_door.custom#{}')

    frontdoor_sdk = CliCommandType(
        operations_tmpl='azext_front_door.vendored_sdks.operations._front_doors_operations#FrontDoorsOperations.{}',
        client_factory=cf_frontdoor
    )

    # fd_backend_pool_sdk = CliCommandType(
    #     operations_tmpl='azext_front_door.vendored_sdks.operations.backend_pools_operations#BackendPoolsOperations.{}',
    #     client_factory=cf_fd_backend_pools
    # )

    fd_endpoint_sdk = CliCommandType(
        operations_tmpl='azext_front_door.vendored_sdks.operations._endpoints_operations#EndpointsOperations.{}',
        client_factory=cf_fd_endpoints
    )

    # fd_frontend_endpoint_sdk = CliCommandType(
    #     operations_tmpl='azext_front_door.vendored_sdks.operations.frontend_endpoints_operations#FrontendEndpointsOperations.{}',
    #     client_factory=cf_fd_frontend_endpoints
    # )

    # fd_probe_sdk = CliCommandType(
    #     operations_tmpl='azext_front_door.vendored_sdks.operations.health_probe_settings_operations#HealthProbeSettingsOperations.{}',
    #     client_factory=cf_fd_probes
    # )

    # fd_load_balancing_sdk = CliCommandType(
    #     operations_tmpl='azext_front_door.vendored_sdks.operations.load_balancing_settings_operations#LoadBalancingSettingsOperations.{}',
    #     client_factory=cf_fd_load_balancing
    # )

    # fd_routing_rule_sdk = CliCommandType(
    #     operations_tmpl='azext_front_door.vendored_sdks.operations.routing_rules_operations#RoutingRulesOperations.{}',
    #     client_factory=cf_fd_routing_rules
    # )

    rules_engine_sdk = CliCommandType(
        operations_tmpl='azext_front_door.vendored_sdks.operations._rules_engines_operations#RulesEnginesOperations.{}',
        client_factory=cf_fd_rules_engines
    )

    waf_policy_sdk = CliCommandType(
        operations_tmpl='azext_front_door.vendored_sdks.operations._policies_operations#PoliciesOperations.{}',
        client_factory=cf_waf_policies
    )

    # region Frontdoors
    with self.command_group('network front-door', frontdoor_sdk) as g:
        g.show_command('show')
        g.custom_command('create', 'create_front_door', supports_no_wait=True)
        g.command('delete', 'delete', supports_no_wait=True)
        g.custom_command('list', 'list_front_doors')
        g.generic_update_command('update', custom_func_name='update_front_door', setter_arg_name='front_door_parameters')
        g.command('check-custom-domain', 'validate_custom_domain')

    with self.command_group('network front-door', fd_endpoint_sdk) as g:
        g.command('purge-endpoint', 'purge_content')

    property_map = {
        'backend_pools': 'backend-pool',
        'frontend_endpoints': 'frontend-endpoint',
        'health_probe_settings': 'probe',
        'load_balancing_settings': 'load-balancing',
        'routing_rules': 'routing-rule'
    }
    for subresource, alias in property_map.items():
        with self.command_group('network front-door {}'.format(alias), frontdoor_sdk) as g:
            g.custom_command('create', 'create_fd_{}'.format(subresource))
            g.custom_command('list', list_frontdoor_resource_property('front_doors', subresource))
            g.custom_show_command('show', get_frontdoor_resource_property_entry('front_doors', subresource))
            g.custom_command('delete', delete_frontdoor_resource_property_entry('front_doors', subresource))

    with self.command_group('network front-door probe', frontdoor_sdk) as g:
        g.custom_command('update', 'update_fd_health_probe_settings')

    with self.command_group('network front-door load-balancing', frontdoor_sdk) as g:
        g.generic_update_command('update', custom_func_name='update_fd_load_balancing_settings',
                                 setter_arg_name='front_door_parameters',
                                 child_collection_prop_name='load_balancing_settings')

    with self.command_group('network front-door backend-pool backend', frontdoor_sdk) as g:
        g.custom_command('add', 'add_fd_backend')
        g.custom_command('list', 'list_fd_backends')
        g.custom_command('remove', 'remove_fd_backend')

    with self.command_group('network front-door frontend-endpoint', frontdoor_sdk) as g:
        g.custom_command('create', 'create_fd_frontend_endpoints')
        g.custom_command('list', 'list_fd_frontend_endpoints')
        g.custom_show_command('show', 'get_fd_frontend_endpoints')
    #   g.generic_update_command('update', custom_func_name='update_fd_frontend_endpoints')
        g.custom_command('disable-https', 'configure_fd_frontend_endpoint_disable_https')
        g.custom_command('enable-https', 'configure_fd_frontend_endpoint_enable_https')

    with self.command_group('network front-door routing-rule', frontdoor_sdk) as g:
        g.generic_update_command('update', custom_func_name='update_fd_routing_rule',
                                 setter_arg_name='front_door_parameters',
                                 child_collection_prop_name='routing_rules')

    # with self.command_group('network front-door probe', frontdoor_sdk) as g:
    #     g.custom_command('create', 'create_fd_probe')
    #     g.command('delete', 'delete')
    #     g.command('list', 'list_by_front_door')
    #     g.show_command('show', 'get')
    #     g.generic_update_command('update', custom_func_name='update_fd_probe')

    # with self.command_group('network front-door load-balancing', frontdoor_sdk) as g:
    #     g.custom_command('create', 'create_fd_load_balancing_settings')
    #     g.command('delete', 'delete')
    #     g.command('list', 'list_by_front_door')
    #     g.show_command('show', 'get')
    #     g.generic_update_command('update', custom_func_name='update_fd_load_balancing_settings')

    # with self.command_group('network front-door routing-rule', frontdoor_sdk) as g:
    #     g.custom_command('create', 'create_fd_routing_rule')
    #     g.command('delete', 'delete')
    #     g.command('list', 'list_by_front_door')
    #     g.show_command('show', 'get')
    #     g.generic_update_command('update', custom_func_name='update_fd_routing_rule')
    # endregion

    # region WafPolicy
    with self.command_group('network front-door waf-policy', waf_policy_sdk) as g:
        g.custom_command('create', 'create_waf_policy')
        g.command('delete', 'delete')
        g.command('list', 'list')
        g.show_command('show')
        g.generic_update_command('update', custom_func_name='update_waf_policy')

    with self.command_group('network front-door waf-policy managed-rules', waf_policy_sdk) as g:
        g.custom_command('add', 'add_azure_managed_rule_set')
        g.custom_command('remove', 'remove_azure_managed_rule_set')
        g.custom_command('list', 'list_azure_managed_rule_set')

    with self.command_group('network front-door waf-policy managed-rules override', waf_policy_sdk) as g:
        g.custom_command('add', 'add_override_azure_managed_rule_set')
        g.custom_command('remove', 'remove_override_azure_managed_rule_set')
        g.custom_command('list', 'list_override_azure_managed_rule_set')

    with self.command_group('network front-door waf-policy managed-rules exclusion', waf_policy_sdk) as g:
        g.custom_command('add', 'add_exclusion_azure_managed_rule_set')
        g.custom_command('remove', 'remove_exclusion_azure_managed_rule_set')
        g.custom_command('list', 'list_exclusion_azure_managed_rule_set')

    with self.command_group('network front-door waf-policy managed-rule-definition', waf_policy_sdk) as g:
        g.custom_command('list', 'list_managed_rules_definitions')

    with self.command_group('network front-door waf-policy rule', waf_policy_sdk, supports_local_cache=True, model_path='azext_front_door.vendored_sdks.models') as g:
        g.custom_command('create', 'create_wp_custom_rule')
        g.custom_command('update', 'update_wp_custom_rule')
        g.custom_command('delete', 'delete_wp_custom_rule')
        g.custom_command('list', 'list_wp_custom_rules')
        g.custom_show_command('show', 'show_wp_custom_rule')

    with self.command_group('network front-door waf-policy rule match-condition', waf_policy_sdk, supports_local_cache=True, model_path='azext_front_door.vendored_sdks.models') as g:
        g.custom_command('add', 'add_custom_rule_match_condition')
        g.custom_command('remove', 'remove_custom_rule_match_condition')
        g.custom_command('list', 'list_custom_rule_match_conditions')
    # endregion

    # region RulesEngine

    with self.command_group('network front-door rules-engine', rules_engine_sdk) as g:
        g.show_command('show', 'get')
        g.command('list', 'list_by_front_door')
        g.command('delete', 'delete')

    with self.command_group('network front-door rules-engine rule', rules_engine_sdk) as g:
        g.custom_command('create', 'create_rules_engine_rule')
        g.custom_command('delete', 'delete_rules_engine_rule')
        g.custom_show_command('show', 'show_rules_engine_rule')
        g.custom_command('list', 'list_rules_engine_rule')
        g.custom_command('update', 'update_rules_engine_rule')

    with self.command_group('network front-door rules-engine rule condition', rules_engine_sdk) as g:
        g.custom_command('add', 'add_rules_engine_condition')
        g.custom_command('remove', 'remove_rules_engine_condition')
        g.custom_command('list', 'list_rules_engine_condition')

    with self.command_group('network front-door rules-engine rule action', rules_engine_sdk) as g:
        g.custom_command('add', 'add_rules_engine_action')
        g.custom_command('remove', 'remove_rules_engine_action')
        g.custom_command('list', 'list_rules_engine_action')
    # endregion
