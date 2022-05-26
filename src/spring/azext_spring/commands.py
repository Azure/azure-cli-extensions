# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_spring._utils import handle_asc_exception

from ._client_factory import (cf_spring_20220501preview,
                              cf_spring_20220301preview,
                              cf_spring_20220101preview,
                              cf_spring_20201101preview,
                              cf_config_servers)
from ._transformers import (transform_spring_table_output,
                            transform_app_table_output,
                            transform_spring_deployment_output,
                            transform_spring_certificate_output,
                            transform_spring_custom_domain_output,
                            transform_application_configuration_service_output,
                            transform_service_registry_output,
                            transform_spring_cloud_gateway_output,
                            transform_api_portal_output)
from ._marketplace import (transform_marketplace_plan_output)
from ._validators_enterprise import (validate_gateway_update, validate_api_portal_update)
from ._app_managed_identity_validator import (validate_app_identity_remove_or_warning,
                                              validate_app_identity_assign_or_warning)


# pylint: disable=too-many-statements
def load_command_table(self, _):
    spring_routing_util = CliCommandType(
        operations_tmpl='azext_spring.spring_instance#{}',
        client_factory=cf_spring_20220501preview
    )

    app_command = CliCommandType(
        operations_tmpl='azext_spring.app#{}',
        client_factory=cf_spring_20220501preview
    )

    app_managed_identity_command = CliCommandType(
        operations_tmpl='azext_spring.app_managed_identity#{}',
        client_factory=cf_spring_20220301preview
    )

    service_registry_cmd_group = CliCommandType(
        operations_tmpl='azext_spring.service_registry#{}',
        client_factory=cf_spring_20220101preview
    )

    builder_cmd_group = CliCommandType(
        operations_tmpl="azext_spring._build_service#{}",
        client_factory=cf_spring_20220101preview
    )

    buildpack_binding_cmd_group = CliCommandType(
        operations_tmpl="azext_spring.buildpack_binding#{}",
        client_factory=cf_spring_20220101preview
    )

    application_configuration_service_cmd_group = CliCommandType(
        operations_tmpl='azext_spring.application_configuration_service#{}',
        client_factory=cf_spring_20220101preview
    )

    gateway_cmd_group = CliCommandType(
        operations_tmpl='azext_spring.gateway#{}',
        client_factory=cf_spring_20220101preview
    )

    gateway_custom_domain_cmd_group = CliCommandType(
        operations_tmpl='azext_spring.gateway#{}',
        client_factory=cf_spring_20220101preview
    )

    gateway_route_config_cmd_group = CliCommandType(
        operations_tmpl='azext_spring.gateway#{}',
        client_factory=cf_spring_20220101preview
    )

    api_portal_cmd_group = CliCommandType(
        operations_tmpl='azext_spring.api_portal#{}',
        client_factory=cf_spring_20220101preview
    )

    api_portal_custom_domain_cmd_group = CliCommandType(
        operations_tmpl='azext_spring.api_portal#{}',
        client_factory=cf_spring_20220101preview
    )

    with self.command_group('spring', custom_command_type=spring_routing_util,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('create', 'spring_create', supports_no_wait=True)
        g.custom_command('list-marketplace-plan', 'spring_list_marketplace_plan',
                         is_preview=True,
                         table_transformer=transform_marketplace_plan_output)

    with self.command_group('spring', client_factory=cf_spring_20220501preview,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('update', 'spring_update', supports_no_wait=True)
        g.custom_command('delete', 'spring_delete', supports_no_wait=True)
        g.custom_command('start', 'spring_start', supports_no_wait=True)
        g.custom_command('stop', 'spring_stop', supports_no_wait=True)
        g.custom_command('list', 'spring_list', table_transformer=transform_spring_table_output)
        g.custom_show_command('show', 'spring_get', table_transformer=transform_spring_table_output)

    with self.command_group('spring test-endpoint', client_factory=cf_spring_20220101preview,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('enable ', 'enable_test_endpoint')
        g.custom_show_command('disable ', 'disable_test_endpoint')
        g.custom_command('renew-key', 'regenerate_keys')
        g.custom_command('list', 'list_keys')

    with self.command_group('spring config-server', client_factory=cf_config_servers,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('set', 'config_set', supports_no_wait=True)
        g.custom_command('clear', 'config_delete')
        g.custom_show_command('show', 'config_get')

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

    with self.command_group('spring app', client_factory=cf_spring_20220501preview,
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

    with self.command_group('spring app identity', custom_command_type=app_managed_identity_command,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('assign', 'app_identity_assign', validator=validate_app_identity_assign_or_warning)
        g.custom_command('remove', 'app_identity_remove', validator=validate_app_identity_remove_or_warning)
        g.custom_command('force-set', 'app_identity_force_set', is_preview=True)
        g.custom_show_command('show', 'app_identity_show')

    with self.command_group('spring app log', client_factory=cf_spring_20220101preview,
                            deprecate_info=g.deprecate(redirect='az spring app logs', hide=True),
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('tail', 'app_tail_log')

    with self.command_group('spring app', custom_command_type=app_command, client_factory=cf_spring_20220501preview,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('deploy', 'app_deploy', supports_no_wait=True)

    with self.command_group('spring app deployment', custom_command_type=app_command, client_factory=cf_spring_20220501preview,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('create', 'deployment_create', supports_no_wait=True)

    with self.command_group('spring app deployment', client_factory=cf_spring_20220501preview,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('list', 'deployment_list',
                         table_transformer=transform_spring_deployment_output)
        g.custom_show_command(
            'show', 'deployment_get', table_transformer=transform_spring_deployment_output)
        g.custom_command('delete', 'deployment_delete', supports_no_wait=True)
        g.custom_command('generate-heap-dump', 'deployment_generate_heap_dump')
        g.custom_command('generate-thread-dump', 'deployment_generate_thread_dump')
        g.custom_command('start-jfr', 'deployment_start_jfr')

    with self.command_group('spring app binding', client_factory=cf_spring_20220101preview,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('list', 'binding_list')
        g.custom_show_command('show', 'binding_get')
        g.custom_command('cosmos add', 'binding_cosmos_add')
        g.custom_command('cosmos update', 'binding_cosmos_update')
        g.custom_command('mysql add', 'binding_mysql_add')
        g.custom_command('mysql update', 'binding_mysql_update')
        g.custom_command('redis add', 'binding_redis_add')
        g.custom_command('redis update', 'binding_redis_update')
        g.custom_show_command('remove', 'binding_remove')

    with self.command_group('spring storage', client_factory=cf_spring_20220101preview,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('list', 'storage_list')
        g.custom_show_command('show', 'storage_get')
        g.custom_command('add', 'storage_add')
        g.custom_command('update', 'storage_update')
        g.custom_command('remove', 'storage_remove')
        g.custom_command('list-persistent-storage', "storage_list_persistent_storage", table_transformer=transform_app_table_output)

    with self.command_group('spring certificate', client_factory=cf_spring_20220101preview,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('add', 'certificate_add')
        g.custom_show_command('show', 'certificate_show', table_transformer=transform_spring_certificate_output)
        g.custom_command('list', 'certificate_list', table_transformer=transform_spring_certificate_output)
        g.custom_command('remove', 'certificate_remove')
        g.custom_command('list-reference-app', 'certificate_list_reference_app', table_transformer=transform_app_table_output)

    with self.command_group('spring app custom-domain', client_factory=cf_spring_20220101preview,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('bind', 'domain_bind')
        g.custom_show_command('show', 'domain_show', table_transformer=transform_spring_custom_domain_output)
        g.custom_command('list', 'domain_list', table_transformer=transform_spring_custom_domain_output)
        g.custom_command('update', 'domain_update')
        g.custom_command('unbind', 'domain_unbind')

    with self.command_group('spring app-insights',
                            client_factory=cf_spring_20201101preview,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('update', 'app_insights_update', supports_no_wait=True)
        g.custom_show_command('show', 'app_insights_show')

    with self.command_group('spring service-registry',
                            custom_command_type=service_registry_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_show_command('show', 'service_registry_show',
                              table_transformer=transform_service_registry_output)
        g.custom_command('bind', 'service_registry_bind')
        g.custom_command('unbind', 'service_registry_unbind')

    with self.command_group('spring application-configuration-service',
                            custom_command_type=application_configuration_service_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('clear', 'application_configuration_service_clear')
        g.custom_show_command('show', 'application_configuration_service_show',
                              table_transformer=transform_application_configuration_service_output)
        g.custom_command('bind', 'application_configuration_service_bind')
        g.custom_command('unbind', 'application_configuration_service_unbind')

    with self.command_group('spring application-configuration-service git repo',
                            custom_command_type=application_configuration_service_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('add', 'application_configuration_service_git_add')
        g.custom_command('update', 'application_configuration_service_git_update')
        g.custom_command('remove', 'application_configuration_service_git_remove')
        g.custom_command('list', 'application_configuration_service_git_list')

    with self.command_group('spring gateway',
                            custom_command_type=gateway_cmd_group,
                            exception_handler=handle_asc_exception,
                            is_preview=True) as g:
        g.custom_show_command('show', 'gateway_show', table_transformer=transform_spring_cloud_gateway_output)
        g.custom_command('update', 'gateway_update', validator=validate_gateway_update, supports_no_wait=True)
        g.custom_command('clear', 'gateway_clear', supports_no_wait=True)

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
                            exception_handler=handle_asc_exception,
                            is_preview=True) as g:
        g.custom_show_command('show', 'api_portal_show', table_transformer=transform_api_portal_output)
        g.custom_command('update', 'api_portal_update', validator=validate_api_portal_update)
        g.custom_command('clear', 'api_portal_clear')

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

    with self.command_group('spring build-service builder',
                            custom_command_type=builder_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('create', 'create_or_update_builder', supports_no_wait=True)
        g.custom_command('update', 'create_or_update_builder', supports_no_wait=True)
        g.custom_show_command('show', 'builder_show')
        g.custom_command('delete', 'builder_delete', supports_no_wait=True, confirmation=True)

    with self.command_group('spring build-service builder buildpack-binding',
                            custom_command_type=buildpack_binding_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('create', 'create_or_update_buildpack_binding')
        g.custom_command('set', 'create_or_update_buildpack_binding')
        g.custom_show_command('show', 'buildpack_binding_show')
        g.custom_command('list', 'buildpack_binding_list')
        g.custom_command('delete', 'buildpack_binding_delete', confirmation=True)

    with self.command_group('spring build-service', exception_handler=handle_asc_exception):
        pass

    with self.command_group('spring', exception_handler=handle_asc_exception):
        pass
