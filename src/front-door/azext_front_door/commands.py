# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType

from .custom import (
    list_frontdoor_resource_property, get_frontdoor_resource_property_entry, delete_frontdoor_resource_property_entry)
from ._client_factory import (
    cf_frontdoor, cf_fd_endpoints, cf_fd_rules_engines, cf_front_door_name_availability)


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

    # waf_policy_sdk = CliCommandType(
    #     operations_tmpl='azext_front_door.vendored_sdks.operations._policies_operations#PoliciesOperations.{}',
    #     client_factory=cf_waf_policies
    # )

    fd_frontdoor_custom_sdk = CliCommandType(
        operations_tmpl='azext_front_door.custom#{}',
        client_factory=cf_fd_endpoints)

    # region Frontdoors
    with self.command_group('network front-door', frontdoor_sdk) as g:
        g.show_command('show')
        g.custom_command('create', 'create_front_door', supports_no_wait=True)
        g.command('delete', 'begin_delete', supports_no_wait=True)
        g.custom_command('list', 'list_front_doors')
        g.generic_update_command('update', custom_func_name='update_front_door', setter_arg_name='front_door_parameters', setter_name="begin_create_or_update")
        g.custom_command('check-custom-domain', 'validate_custom_domain', client_factory=cf_frontdoor)
        g.custom_command('check-name-availability', 'check_front_door_name_availability', client_factory=cf_front_door_name_availability)
        g.wait_command('wait')

    with self.command_group('network front-door', fd_endpoint_sdk) as g:
        g.custom_command('purge-endpoint', 'purge_endpoint', client_factory=cf_fd_endpoints)

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
                                 setter_name="begin_create_or_update",
                                 setter_arg_name='front_door_parameters',
                                 child_collection_prop_name='load_balancing_settings')

    with self.command_group('network front-door backend-pool backend', frontdoor_sdk) as g:
        g.custom_command('add', 'add_fd_backend')
        g.custom_command('update', 'update_fd_backend')
        g.custom_command('list', 'list_fd_backends')
        g.custom_command('remove', 'remove_fd_backend')

    with self.command_group('network front-door frontend-endpoint', frontdoor_sdk) as g:
        g.custom_command('create', 'create_fd_frontend_endpoints')
        g.custom_command('list', 'list_fd_frontend_endpoints')
        g.custom_show_command('show', 'get_fd_frontend_endpoints')
    #   g.generic_update_command('update', custom_func_name='update_fd_frontend_endpoints')
        g.custom_command('disable-https', 'configure_fd_frontend_endpoint_disable_https')
        g.custom_command('enable-https', 'configure_fd_frontend_endpoint_enable_https')

        g.wait_command('wait', getter_name="get_fd_frontend_endpoints", getter_type=fd_frontdoor_custom_sdk)

    with self.command_group('network front-door routing-rule', frontdoor_sdk) as g:
        g.generic_update_command('update', custom_func_name='update_fd_routing_rule',
                                 setter_name="begin_create_or_update",
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
    # with self.command_group('network front-door waf-policy', waf_policy_sdk) as g:
    #     g.custom_command('create', 'create_waf_policy')
    #     g.command('delete', 'begin_delete')
    #     g.command('list', 'list')
    #     g.show_command('show')
    #     g.generic_update_command('update', custom_func_name='update_waf_policy', setter_name="begin_create_or_update")
    from .custom_waf import (
        WafPolicyCreate, WafPolicyUpdate,
        AddAzureManagedRuleSet, RemoveAzureManagedRuleSet, ListAzureManagedRuleSet,
        AddOverrideAzureManagedRuleSet, RemoveOverrideAzureManagedRuleSet, ListOverrideAzureManagedRuleSet,
        AddExclusionAzureManagedRuleSet, RemoveExclusionAzureManagedRuleSet, ListExclusionAzureManagedRuleSet,
        CreateCustomRule, UpdateCustomRule, DeleteCustomRule, ListCustomRules, ShowCustomRule,
        AddCustomRuleMatchCondition, RemoveCustomRuleMatchCondition, ListCustomRuleMatchConditions
    )
    self.command_table['network front-door waf-policy create'] = WafPolicyCreate(loader=self)
    self.command_table['network front-door waf-policy update'] = WafPolicyUpdate(loader=self)

    # Register command groups for waf-policy subcommands
    with self.command_group('network front-door waf-policy managed-rules'):
        pass
    with self.command_group('network front-door waf-policy managed-rules exclusion'):
        pass
    with self.command_group('network front-door waf-policy managed-rules override'):
        pass
    with self.command_group('network front-door waf-policy rule'):
        pass
    with self.command_group('network front-door waf-policy rule match-condition'):
        pass

    # Managed rules commands
    self.command_table['network front-door waf-policy managed-rules add'] = AddAzureManagedRuleSet(loader=self)
    self.command_table['network front-door waf-policy managed-rules remove'] = RemoveAzureManagedRuleSet(loader=self)
    self.command_table['network front-door waf-policy managed-rules list'] = ListAzureManagedRuleSet(loader=self)

    # Managed rules override commands
    self.command_table['network front-door waf-policy managed-rules override add'] = AddOverrideAzureManagedRuleSet(loader=self)
    self.command_table['network front-door waf-policy managed-rules override remove'] = RemoveOverrideAzureManagedRuleSet(loader=self)
    self.command_table['network front-door waf-policy managed-rules override list'] = ListOverrideAzureManagedRuleSet(loader=self)

    # Managed rules exclusion commands
    self.command_table['network front-door waf-policy managed-rules exclusion add'] = AddExclusionAzureManagedRuleSet(loader=self)
    self.command_table['network front-door waf-policy managed-rules exclusion remove'] = RemoveExclusionAzureManagedRuleSet(loader=self)
    self.command_table['network front-door waf-policy managed-rules exclusion list'] = ListExclusionAzureManagedRuleSet(loader=self)

    # Custom rules commands
    self.command_table['network front-door waf-policy rule create'] = CreateCustomRule(loader=self)
    self.command_table['network front-door waf-policy rule update'] = UpdateCustomRule(loader=self)
    self.command_table['network front-door waf-policy rule delete'] = DeleteCustomRule(loader=self)
    self.command_table['network front-door waf-policy rule list'] = ListCustomRules(loader=self)
    self.command_table['network front-door waf-policy rule show'] = ShowCustomRule(loader=self)

    # Custom rule match condition commands
    self.command_table['network front-door waf-policy rule match-condition add'] = AddCustomRuleMatchCondition(loader=self)
    self.command_table['network front-door waf-policy rule match-condition remove'] = RemoveCustomRuleMatchCondition(loader=self)
    self.command_table['network front-door waf-policy rule match-condition list'] = ListCustomRuleMatchConditions(loader=self)
    # endregion

    # region RulesEngine

    with self.command_group('network front-door rules-engine', rules_engine_sdk) as g:
        g.show_command('show', 'get')
        g.command('list', 'list_by_front_door')
        g.command('delete', 'begin_delete')

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
