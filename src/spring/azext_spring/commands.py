# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_spring._utils import handle_asc_exception

from ._client_factory import (cf_spring,
                              cf_config_servers, cf_eureka_servers)
from ._transformers import (transform_spring_table_output,
                            transform_app_table_output,
                            transform_spring_deployment_output,
                            transform_spring_certificate_output,
                            transform_spring_custom_domain_output,
                            transform_application_configuration_service_output,
                            transform_service_registry_output,
                            transform_spring_cloud_gateway_output,
                            transform_dev_tool_portal_output,
                            transform_live_view_output,
                            transform_api_portal_output,
                            transform_application_accelerator_output,
                            transform_predefined_accelerator_output,
                            transform_customized_accelerator_output,
                            transform_build_output,
                            transform_build_result_output,
                            transform_apm_output,
                            transform_apm_type_output,
                            transform_container_registry_output,
                            transform_support_server_versions_output)
from ._validators import validate_app_insights_command_not_supported_tier
from ._marketplace import (transform_marketplace_plan_output)
from ._validators_enterprise import (validate_gateway_update, validate_api_portal_update, validate_dev_tool_portal,
                                     validate_customized_accelerator, validate_pattern_for_show_acs_configs)
from .managed_components.validators_managed_component import (validate_component_logs, validate_component_list, validate_instance_list)
from ._app_managed_identity_validator import (validate_app_identity_remove_or_warning,
                                              validate_app_identity_assign_or_warning)


# pylint: disable=too-many-statements
def load_command_table(self, _):
    spring_routing_util = CliCommandType(
        operations_tmpl='azext_spring.spring_instance#{}',
        client_factory=cf_spring
    )

    app_command = CliCommandType(
        operations_tmpl='azext_spring.app#{}',
        client_factory=cf_spring
    )

    app_managed_identity_command = CliCommandType(
        operations_tmpl='azext_spring.app_managed_identity#{}',
        client_factory=cf_spring
    )

    service_registry_cmd_group = CliCommandType(
        operations_tmpl='azext_spring.service_registry#{}',
        client_factory=cf_spring
    )

    build_service_cmd_group = CliCommandType(
        operations_tmpl="azext_spring._build_service#{}",
        client_factory=cf_spring
    )

    buildpack_binding_cmd_group = CliCommandType(
        operations_tmpl="azext_spring.buildpack_binding#{}",
        client_factory=cf_spring
    )

    apm_cmd_group = CliCommandType(
        operations_tmpl="azext_spring.apm#{}",
        client_factory=cf_spring
    )

    application_configuration_service_cmd_group = CliCommandType(
        operations_tmpl='azext_spring.application_configuration_service#{}',
        client_factory=cf_spring
    )

    application_live_view_cmd_group = CliCommandType(
        operations_tmpl='azext_spring.application_live_view#{}',
        client_factory=cf_spring
    )

    dev_tool_portal_cmd_group = CliCommandType(
        operations_tmpl='azext_spring.dev_tool_portal#{}',
        client_factory=cf_spring
    )

    gateway_cmd_group = CliCommandType(
        operations_tmpl='azext_spring.gateway#{}',
        client_factory=cf_spring
    )

    gateway_custom_domain_cmd_group = CliCommandType(
        operations_tmpl='azext_spring.gateway#{}',
        client_factory=cf_spring
    )

    gateway_route_config_cmd_group = CliCommandType(
        operations_tmpl='azext_spring.gateway#{}',
        client_factory=cf_spring
    )

    api_portal_cmd_group = CliCommandType(
        operations_tmpl='azext_spring.api_portal#{}',
        client_factory=cf_spring
    )

    api_portal_custom_domain_cmd_group = CliCommandType(
        operations_tmpl='azext_spring.api_portal#{}',
        client_factory=cf_spring
    )

    application_accelerator_cmd_group = CliCommandType(
        operations_tmpl='azext_spring.application_accelerator#{}',
        client_factory=cf_spring
    )

    managed_component_cmd_group = CliCommandType(
        operations_tmpl='azext_spring.managed_components.managed_component_operations#{}',
        client_factory=cf_spring
    )

    with self.command_group('spring', custom_command_type=spring_routing_util,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('create', 'spring_create', supports_no_wait=True)
        g.custom_command('list-marketplace-plan', 'spring_list_marketplace_plan',
                         is_preview=True,
                         table_transformer=transform_marketplace_plan_output)
        g.custom_command('list-support-server-versions', 'spring_list_support_server_versions',
                         is_preview=True,
                         table_transformer=transform_support_server_versions_output)

    with self.command_group('spring', client_factory=cf_spring,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('update', 'spring_update', supports_no_wait=True)
        g.custom_command('delete', 'spring_delete', supports_no_wait=True)
        g.custom_command('start', 'spring_start', supports_no_wait=True)
        g.custom_command('stop', 'spring_stop', supports_no_wait=True)
        g.custom_command('list', 'spring_list', table_transformer=transform_spring_table_output)
        g.custom_show_command('show', 'spring_get', table_transformer=transform_spring_table_output)
        g.custom_command('flush-virtualnetwork-dns-settings', 'spring_flush_vnet_dns_setting', is_preview=True, supports_no_wait=True)

    with self.command_group('spring test-endpoint', client_factory=cf_spring,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('enable ', 'enable_test_endpoint')
        g.custom_show_command('disable ', 'disable_test_endpoint')
        g.custom_command('renew-key', 'regenerate_keys')
        g.custom_command('list', 'list_keys')

    with self.command_group('spring eureka-server', client_factory=cf_eureka_servers,
                            exception_handler=handle_asc_exception) as g:
        g.custom_show_command('show', 'eureka_get')
        g.custom_command('enable', 'eureka_enable')
        g.custom_command('disable', 'eureka_disable')

    with self.command_group('spring config-server', client_factory=cf_config_servers,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('set', 'config_set', supports_no_wait=True)
        g.custom_command('clear', 'config_delete')
        g.custom_show_command('show', 'config_get')
        g.custom_command('enable', 'config_enable')
        g.custom_command('disable', 'config_disable')

    with self.command_group('spring config-server git', client_factory=cf_config_servers,
                            supports_local_cache=True, exception_handler=handle_asc_exception) as g:
        g.custom_command('set', 'config_git_set')
        g.custom_command('repo add', 'config_repo_add')
        g.custom_command('repo remove', 'config_repo_delete')
        g.custom_command('repo update', 'config_repo_update')
        g.custom_command('repo list', 'config_repo_list')

    with self.command_group('spring app', custom_command_type=app_command,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('create', 'app_create')
        g.custom_command('update', 'app_update', supports_no_wait=True)

    with self.command_group('spring app', client_factory=cf_spring,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('set-deployment', 'app_set_deployment',
                         supports_no_wait=True)
        g.custom_command('unset-deployment', 'app_unset_deployment',
                         supports_no_wait=True)
        g.custom_command('scale', 'app_scale', supports_no_wait=True)
        g.custom_command('show-deploy-log', 'app_get_build_log')
        g.custom_command('delete', 'app_delete')
        g.custom_command('list', 'app_list',
                         table_transformer=transform_app_table_output)
        g.custom_show_command(
            'show', 'app_get', table_transformer=transform_app_table_output)
        g.custom_command('start', 'app_start', supports_no_wait=True)
        g.custom_command('stop', 'app_stop', supports_no_wait=True)
        g.custom_command('restart', 'app_restart', supports_no_wait=True)
        g.custom_command('logs', 'app_tail_log')
        g.custom_command('append-persistent-storage', 'app_append_persistent_storage')
        g.custom_command('append-loaded-public-certificate', 'app_append_loaded_public_certificate')
        g.custom_command('connect', 'app_connect')
        g.custom_command('enable-remote-debugging', 'deployment_enable_remote_debugging', supports_no_wait=True)
        g.custom_command('disable-remote-debugging', 'deployment_disable_remote_debugging', supports_no_wait=True)
        g.custom_command('get-remote-debugging-config', 'deployment_get_remote_debugging')

    with self.command_group('spring app identity', custom_command_type=app_managed_identity_command,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('assign', 'app_identity_assign', validator=validate_app_identity_assign_or_warning)
        g.custom_command('remove', 'app_identity_remove', validator=validate_app_identity_remove_or_warning)
        g.custom_command('force-set', 'app_identity_force_set')
        g.custom_show_command('show', 'app_identity_show')

    with self.command_group('spring app log', client_factory=cf_spring,
                            deprecate_info=g.deprecate(redirect='az spring app logs', hide=True),
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('tail', 'app_tail_log')

    with self.command_group('spring app', custom_command_type=app_command, client_factory=cf_spring,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('deploy', 'app_deploy', supports_no_wait=True)

    with self.command_group('spring app deployment', custom_command_type=app_command, client_factory=cf_spring,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('create', 'deployment_create', supports_no_wait=True)

    with self.command_group('spring app deployment', client_factory=cf_spring,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('list', 'deployment_list',
                         table_transformer=transform_spring_deployment_output)
        g.custom_show_command(
            'show', 'deployment_get', table_transformer=transform_spring_deployment_output)
        g.custom_command('delete', 'deployment_delete', supports_no_wait=True)
        g.custom_command('generate-heap-dump', 'deployment_generate_heap_dump')
        g.custom_command('generate-thread-dump', 'deployment_generate_thread_dump')
        g.custom_command('start-jfr', 'deployment_start_jfr')

    with self.command_group('spring app binding', client_factory=cf_spring,
                            exception_handler=handle_asc_exception, deprecate_info=self.deprecate(
                                target='spring app binding',
                                redirect='spring connection', hide=True)) as g:
        g.custom_command('list', 'binding_list')
        g.custom_show_command('show', 'binding_get')
        g.custom_command('cosmos add', 'binding_cosmos_add')
        g.custom_command('cosmos update', 'binding_cosmos_update')
        g.custom_command('mysql add', 'binding_mysql_add')
        g.custom_command('mysql update', 'binding_mysql_update')
        g.custom_command('redis add', 'binding_redis_add')
        g.custom_command('redis update', 'binding_redis_update')
        g.custom_show_command('remove', 'binding_remove')

    with self.command_group('spring storage', client_factory=cf_spring,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('list', 'storage_list')
        g.custom_show_command('show', 'storage_get')
        g.custom_command('add', 'storage_add')
        g.custom_command('update', 'storage_update')
        g.custom_command('remove', 'storage_remove')
        g.custom_command('list-persistent-storage', "storage_list_persistent_storage", table_transformer=transform_app_table_output)

    with self.command_group('spring certificate', client_factory=cf_spring,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('add', 'certificate_add')
        g.custom_command('update', 'certificate_update')
        g.custom_show_command('show', 'certificate_show', table_transformer=transform_spring_certificate_output)
        g.custom_command('list', 'certificate_list', table_transformer=transform_spring_certificate_output)
        g.custom_command('remove', 'certificate_remove')
        g.custom_command('list-reference-app', 'certificate_list_reference_app', table_transformer=transform_app_table_output)

    with self.command_group('spring app custom-domain', client_factory=cf_spring,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('bind', 'domain_bind')
        g.custom_show_command('show', 'domain_show', table_transformer=transform_spring_custom_domain_output)
        g.custom_command('list', 'domain_list', table_transformer=transform_spring_custom_domain_output)
        g.custom_command('update', 'domain_update')
        g.custom_command('unbind', 'domain_unbind')

    with self.command_group('spring app-insights',
                            client_factory=cf_spring,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('update', 'app_insights_update', supports_no_wait=True)
        g.custom_show_command('show', 'app_insights_show',
                              validator=validate_app_insights_command_not_supported_tier)

    with self.command_group('spring service-registry',
                            custom_command_type=service_registry_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_show_command('show', 'service_registry_show',
                              table_transformer=transform_service_registry_output)
        g.custom_command('bind', 'service_registry_bind')
        g.custom_command('unbind', 'service_registry_unbind')
        g.custom_command('create', 'service_registry_create', table_transformer=transform_service_registry_output)
        g.custom_command('delete', 'service_registry_delete', confirmation=True)

    with self.command_group('spring dev-tool',
                            custom_command_type=dev_tool_portal_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_show_command('show', 'show',
                              table_transformer=transform_dev_tool_portal_output)
        g.custom_command('create', 'create', table_transformer=transform_dev_tool_portal_output, validator=validate_dev_tool_portal, supports_no_wait=True)
        g.custom_command('update', 'update', table_transformer=transform_dev_tool_portal_output, validator=validate_dev_tool_portal, supports_no_wait=True)
        g.custom_command('delete', 'delete', supports_no_wait=True, confirmation=True)

    with self.command_group('spring application-live-view',
                            custom_command_type=application_live_view_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_show_command('show', 'show',
                              table_transformer=transform_live_view_output)
        g.custom_command('create', 'create', table_transformer=transform_live_view_output, supports_no_wait=True)
        g.custom_command('delete', 'delete', supports_no_wait=True, confirmation=True)

    with self.command_group('spring application-configuration-service',
                            custom_command_type=application_configuration_service_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('clear', 'application_configuration_service_clear')
        g.custom_show_command('show', 'application_configuration_service_show',
                              table_transformer=transform_application_configuration_service_output)
        g.custom_command('bind', 'application_configuration_service_bind')
        g.custom_command('unbind', 'application_configuration_service_unbind')
        g.custom_command('create', 'application_configuration_service_create', table_transformer=transform_application_configuration_service_output)
        g.custom_command('update', 'application_configuration_service_update', table_transformer=transform_application_configuration_service_output)
        g.custom_command('delete', 'application_configuration_service_delete', confirmation=True)

    with self.command_group('spring application-configuration-service config',
                            custom_command_type=application_configuration_service_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_show_command('show', 'application_configuration_service_config_show', validator=validate_pattern_for_show_acs_configs)

    with self.command_group('spring application-configuration-service git repo',
                            custom_command_type=application_configuration_service_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('add', 'application_configuration_service_git_add')
        g.custom_command('update', 'application_configuration_service_git_update')
        g.custom_command('remove', 'application_configuration_service_git_remove')
        g.custom_command('list', 'application_configuration_service_git_list')

    with self.command_group('spring gateway',
                            custom_command_type=gateway_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_show_command('show', 'gateway_show', table_transformer=transform_spring_cloud_gateway_output)
        g.custom_command('update', 'gateway_update', validator=validate_gateway_update, supports_no_wait=True)
        g.custom_command('clear', 'gateway_clear', supports_no_wait=True)
        g.custom_command('create', 'gateway_create', table_transformer=transform_spring_cloud_gateway_output)
        g.custom_command('delete', 'gateway_delete', confirmation=True)
        g.custom_command('restart', 'gateway_restart', confirmation='Are you sure you want to perform this operation?', supports_no_wait=True)
        g.custom_command('sync-cert', 'gateway_sync_cert', confirmation='Your gateway will be restarted to use the latest certificate.\n' +
                         'Are you sure you want to perform this operation?', supports_no_wait=True)

    with self.command_group('spring gateway custom-domain',
                            custom_command_type=gateway_custom_domain_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_show_command('show', 'gateway_custom_domain_show',
                              table_transformer=transform_spring_custom_domain_output)
        g.custom_command('list', 'gateway_custom_domain_list',
                         table_transformer=transform_spring_custom_domain_output)
        g.custom_command('bind', 'gateway_custom_domain_update')
        g.custom_command('unbind', 'gateway_custom_domain_unbind')
        g.custom_command('update', 'gateway_custom_domain_update')

    with self.command_group('spring gateway route-config',
                            custom_command_type=gateway_route_config_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_show_command('show', 'gateway_route_config_show')
        g.custom_command('list', 'gateway_route_config_list')
        g.custom_command('create', 'gateway_route_config_create')
        g.custom_command('update', 'gateway_route_config_update')
        g.custom_command('remove', 'gateway_route_config_remove')

    with self.command_group('spring api-portal',
                            custom_command_type=api_portal_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_show_command('show', 'api_portal_show', table_transformer=transform_api_portal_output)
        g.custom_command('update', 'api_portal_update', validator=validate_api_portal_update)
        g.custom_command('clear', 'api_portal_clear')
        g.custom_command('create', 'api_portal_create', table_transformer=transform_api_portal_output)
        g.custom_command('delete', 'api_portal_delete', confirmation=True)

    with self.command_group('spring api-portal custom-domain',
                            custom_command_type=api_portal_custom_domain_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_show_command('show', 'api_portal_custom_domain_show',
                              table_transformer=transform_spring_custom_domain_output)
        g.custom_command('list', 'api_portal_custom_domain_list',
                         table_transformer=transform_spring_custom_domain_output)
        g.custom_command('bind', 'api_portal_custom_domain_update')
        g.custom_command('unbind', 'api_portal_custom_domain_unbind')
        g.custom_command('update', 'api_portal_custom_domain_update')

    with self.command_group('spring application-accelerator',
                            custom_command_type=application_accelerator_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_show_command('show', 'application_accelerator_show', table_transformer=transform_application_accelerator_output)
        g.custom_command('create', 'application_accelerator_create', table_transformer=transform_application_accelerator_output, supports_no_wait=True)
        g.custom_command('delete', 'application_accelerator_delete', supports_no_wait=True, confirmation=True)

    with self.command_group('spring application-accelerator predefined-accelerator',
                            custom_command_type=application_accelerator_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('list', 'predefined_accelerator_list', table_transformer=transform_predefined_accelerator_output)
        g.custom_show_command('show', 'predefined_accelerator_show', table_transformer=transform_predefined_accelerator_output)
        g.custom_command('disable', 'predefined_accelerator_disable', supports_no_wait=True)
        g.custom_command('enable', 'predefined_accelerator_enable', supports_no_wait=True)

    with self.command_group('spring application-accelerator customized-accelerator',
                            custom_command_type=application_accelerator_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('list', 'customized_accelerator_list', table_transformer=transform_customized_accelerator_output)
        g.custom_show_command('show', 'customized_accelerator_show', table_transformer=transform_customized_accelerator_output)
        g.custom_command('create', 'customized_accelerator_upsert', supports_no_wait=True, validator=validate_customized_accelerator)
        g.custom_command('update', 'customized_accelerator_upsert', supports_no_wait=True, validator=validate_customized_accelerator)
        g.custom_command('sync-cert', 'customized_accelerator_sync_cert', supports_no_wait=True, table_transformer=transform_customized_accelerator_output)
        g.custom_command('delete', 'customized_accelerator_delete', supports_no_wait=True)

    with self.command_group('spring apm',
                            custom_command_type=apm_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('create', 'create_or_update_apm', supports_no_wait=True)
        g.custom_command('update', 'create_or_update_apm', supports_no_wait=True)
        g.custom_show_command('show', 'apm_show')
        g.custom_command('list', 'apm_list', table_transformer=transform_apm_output)
        g.custom_command('delete', 'apm_delete', confirmation=True, supports_no_wait=True)
        g.custom_command('list-support-types', 'list_support_apm_types', table_transformer=transform_apm_type_output)
        g.custom_command('list-enabled-globally', 'list_apms_enabled_globally')
        g.custom_command('enable-globally', 'enable_apm_globally', supports_no_wait=True)
        g.custom_command('disable-globally', 'disable_apm_globally', supports_no_wait=True)

    with self.command_group('spring build-service builder',
                            custom_command_type=build_service_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('create', 'create_or_update_builder', supports_no_wait=True)
        g.custom_command('update', 'create_or_update_builder', supports_no_wait=True)
        g.custom_show_command('show', 'builder_show')
        g.custom_show_command('show-deployments', 'builder_show_deployments')
        g.custom_command('delete', 'builder_delete', supports_no_wait=True, confirmation=True)

    with self.command_group('spring build-service builder buildpack-binding',
                            custom_command_type=buildpack_binding_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('create', 'create_or_update_buildpack_binding')
        g.custom_command('set', 'create_or_update_buildpack_binding')
        g.custom_show_command('show', 'buildpack_binding_show')
        g.custom_command('list', 'buildpack_binding_list')
        g.custom_command('delete', 'buildpack_binding_delete', confirmation=True)

    with self.command_group('spring container-registry',
                            custom_command_type=build_service_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('create', 'create_or_update_container_registry', supports_no_wait=True)
        g.custom_command('update', 'create_or_update_container_registry', supports_no_wait=True)
        g.custom_show_command('show', 'container_registry_show')
        g.custom_show_command('list', 'container_registry_list', table_transformer=transform_container_registry_output)
        g.custom_command('delete', 'container_registry_delete', supports_no_wait=True, confirmation=True)

    with self.command_group('spring build-service build',
                            custom_command_type=build_service_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('create', 'create_or_update_build', supports_no_wait=True)
        g.custom_command('update', 'create_or_update_build', supports_no_wait=True)
        g.custom_show_command('show', 'build_show')
        g.custom_show_command('list', 'build_list', table_transformer=transform_build_output)
        g.custom_command('delete', 'build_delete', supports_no_wait=True, confirmation=True)

    with self.command_group('spring build-service build result',
                            custom_command_type=build_service_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_show_command('show', 'build_result_show')
        g.custom_show_command('list', 'build_result_list', table_transformer=transform_build_result_output)

    with self.command_group('spring build-service',
                            custom_command_type=build_service_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('update', 'update_build_service', supports_no_wait=True)
        g.custom_show_command('show', 'build_service_show')

    with self.command_group('spring component',
                            custom_command_type=managed_component_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('logs', 'managed_component_logs', validator=validate_component_logs)
        g.custom_command('list', 'managed_component_list', validator=validate_component_list)

    with self.command_group('spring component instance',
                            custom_command_type=managed_component_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('list', 'managed_component_instance_list', validator=validate_instance_list)

    with self.command_group('spring', exception_handler=handle_asc_exception):
        pass
