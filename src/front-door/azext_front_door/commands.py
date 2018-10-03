# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType

from .custom import (
    list_frontdoor_resource_property, get_frontdoor_resource_property_entry, delete_frontdoor_resource_property_entry)
from ._client_factory import cf_frontdoor, cf_fd_endpoints, cf_waf_policies


# pylint: disable=too-many-locals, too-many-statements
def load_command_table(self, _):

    frontdoor_custom = CliCommandType(operations_tmpl='azext_front_door.custom#{}')

    frontdoor_sdk = CliCommandType(
        operations_tmpl='azext_front_door.vendored_sdks.operations.front_doors_operations#FrontDoorsOperations.{}',
        client_factory=cf_frontdoor
    )

    # fd_backend_pool_sdk = CliCommandType(
    #     operations_tmpl='azext_front_door.vendored_sdks.operations.backend_pools_operations#BackendPoolsOperations.{}',
    #     client_factory=cf_fd_backend_pools
    # )

    fd_endpoint_sdk = CliCommandType(
        operations_tmpl='azext_front_door.vendored_sdks.operations.endpoints_operations#EndpointsOperations.{}',
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

    waf_policy_sdk = CliCommandType(
        operations_tmpl='azext_front_door.vendored_sdks.operations.policies_operations#PoliciesOperations.{}',
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
        with self.command_group('network front-door {}'.format(alias), frontdoor_custom) as g:
            g.command('create', 'create_fd_{}'.format(subresource))
            g.command('list', list_frontdoor_resource_property('front_doors', subresource))
            g.show_command('show', get_frontdoor_resource_property_entry('front_doors', subresource))
            g.command('delete', delete_frontdoor_resource_property_entry('front_doors', subresource))

    # with self.command_group('network front-door backend-pool', fd_backend_pool_sdk) as g:
    #     g.custom_command('create', 'create_fd_backend_pool')
    #     g.command('delete', 'delete')
    #     g.command('list', 'list_by_front_door')
    #     g.show_command('show', 'get')
    #     g.generic_update_command('update', custom_func_name='update_fd_backend_pool')

    with self.command_group('network front-door backend-pool backend', frontdoor_sdk) as g:
        g.custom_command('add', 'add_fd_backend')
        g.custom_command('list', 'list_fd_backends')
        g.custom_command('remove', 'remove_fd_backend')

    # with self.command_group('network front-door frontend-endpoint', frontdoor_sdk) as g:
    #     g.custom_command('create', 'create_fd_frontend_endpoint')
    #     g.command('delete', 'delete')
    #     g.command('list', 'list_by_front_door')
    #     g.show_command('show', 'get')
    #     g.generic_update_command('update', custom_func_name='update_fd_frontend_endpoint')
    #     g.custom_command('configure-https', 'configure_fd_frontend_endpoint_https')

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
    with self.command_group('network waf-policy', waf_policy_sdk) as g:
        g.custom_command('create', 'create_waf_policy')
        g.command('delete', 'delete')
        g.command('list', 'list')
        g.show_command('show')
        g.generic_update_command('update', custom_func_name='update_waf_policy')
        g.custom_command('set-managed-ruleset', 'set_azure_managed_rule_set')

    with self.command_group('network waf-policy custom-rule', waf_policy_sdk) as g:
        g.custom_command('create', 'create_wp_custom_rule')
        g.custom_command('delete', 'delete_wp_custom_rule')
        g.custom_command('list', 'list_wp_custom_rules')
        g.custom_command('show', 'show_wp_custom_rule')
    # endregion
