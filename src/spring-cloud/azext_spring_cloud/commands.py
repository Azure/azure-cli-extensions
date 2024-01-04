# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_spring_cloud._utils import handle_asc_exception

from ._client_factory import (cf_spring_cloud_20220301preview,
                              cf_spring_cloud_20220101preview,
                              cf_spring_cloud_20201101preview,
                              cf_config_servers)
from ._transformers import (transform_spring_cloud_table_output,
                            transform_app_table_output,
                            transform_spring_cloud_deployment_output,
                            transform_spring_cloud_certificate_output,
                            transform_spring_cloud_custom_domain_output,
                            transform_application_configuration_service_output,
                            transform_service_registry_output,
                            transform_spring_cloud_gateway_output,
                            transform_api_portal_output)
from ._validators_enterprise import (validate_gateway_update, validate_api_portal_update)
from ._app_managed_identity_validator import (validate_app_identity_remove_or_warning,
                                              validate_app_identity_assign_or_warning)


# pylint: disable=too-many-statements
def load_command_table(self, _):
    def _metadata_deprecate_message(self):
        msg = "The {} has been deprecated and will be removed in Nov. 2022.".format(self.object_type)
        msg += " We recommend that you upgrade to the new '{}' command group".format(self.redirect)
        msg += " by installing the 'spring' extension: run `az extension add -n spring`."
        msg += " For more information, please visit: https://aka.ms/azure-spring-cloud-rename."
        return msg

    spring_cloud_routing_util = CliCommandType(
        operations_tmpl='azext_spring_cloud.spring_cloud_instance#{}',
        client_factory=cf_spring_cloud_20220101preview
    )

    app_command = CliCommandType(
        operations_tmpl='azext_spring_cloud.app#{}',
        client_factory=cf_spring_cloud_20220301preview
    )

    app_managed_identity_command = CliCommandType(
        operations_tmpl='azext_spring_cloud.app_managed_identity#{}',
        client_factory=cf_spring_cloud_20220301preview
    )

    service_registry_cmd_group = CliCommandType(
        operations_tmpl='azext_spring_cloud.service_registry#{}',
        client_factory=cf_spring_cloud_20220101preview
    )

    builder_cmd_group = CliCommandType(
        operations_tmpl="azext_spring_cloud._build_service#{}",
        client_factory=cf_spring_cloud_20220101preview
    )

    buildpack_binding_cmd_group = CliCommandType(
        operations_tmpl="azext_spring_cloud.buildpack_binding#{}",
        client_factory=cf_spring_cloud_20220101preview
    )

    application_configuration_service_cmd_group = CliCommandType(
        operations_tmpl='azext_spring_cloud.application_configuration_service#{}',
        client_factory=cf_spring_cloud_20220101preview
    )

    gateway_cmd_group = CliCommandType(
        operations_tmpl='azext_spring_cloud.gateway#{}',
        client_factory=cf_spring_cloud_20220101preview
    )

    gateway_custom_domain_cmd_group = CliCommandType(
        operations_tmpl='azext_spring_cloud.gateway#{}',
        client_factory=cf_spring_cloud_20220101preview
    )

    gateway_route_config_cmd_group = CliCommandType(
        operations_tmpl='azext_spring_cloud.gateway#{}',
        client_factory=cf_spring_cloud_20220101preview
    )

    api_portal_cmd_group = CliCommandType(
        operations_tmpl='azext_spring_cloud.api_portal#{}',
        client_factory=cf_spring_cloud_20220101preview
    )

    api_portal_custom_domain_cmd_group = CliCommandType(
        operations_tmpl='azext_spring_cloud.api_portal#{}',
        client_factory=cf_spring_cloud_20220101preview
    )

    with self.command_group('spring-cloud', custom_command_type=spring_cloud_routing_util,
                            deprecate_info=self.deprecate(target='spring-cloud', redirect='spring',
                                                          message_func=_metadata_deprecate_message),
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('create', 'spring_cloud_create', supports_no_wait=True)

    with self.command_group('spring-cloud', client_factory=cf_spring_cloud_20220101preview,
                            deprecate_info=self.deprecate(target='spring-cloud', redirect='spring',
                                                          message_func=_metadata_deprecate_message),
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('update', 'spring_cloud_update', supports_no_wait=True)
        g.custom_command('delete', 'spring_cloud_delete', supports_no_wait=True)
        g.custom_command('start', 'spring_cloud_start', supports_no_wait=True)
        g.custom_command('stop', 'spring_cloud_stop', supports_no_wait=True)
        g.custom_command('list', 'spring_cloud_list', table_transformer=transform_spring_cloud_table_output)
        g.custom_show_command('show', 'spring_cloud_get', table_transformer=transform_spring_cloud_table_output)

    with self.command_group('spring-cloud test-endpoint', client_factory=cf_spring_cloud_20220101preview,
                            deprecate_info=self.deprecate(target='spring-cloud test-endpoint',
                                                          redirect='spring test-endpoint',
                                                          message_func=_metadata_deprecate_message),
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('enable ', 'enable_test_endpoint')
        g.custom_show_command('disable ', 'disable_test_endpoint')
        g.custom_command('renew-key', 'regenerate_keys')
        g.custom_command('list', 'list_keys')

    with self.command_group('spring-cloud config-server', client_factory=cf_config_servers,
                            deprecate_info=self.deprecate(target='spring-cloud config-server',
                                                          redirect='spring config-server',
                                                          message_func=_metadata_deprecate_message),
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('set', 'config_set', supports_no_wait=True)
        g.custom_command('clear', 'config_delete')
        g.custom_show_command('show', 'config_get')

    with self.command_group('spring-cloud config-server git', client_factory=cf_config_servers,
                            deprecate_info=self.deprecate(target='spring-cloud config-server git',
                                                          redirect='spring config-server git',
                                                          message_func=_metadata_deprecate_message),
                            supports_local_cache=True, exception_handler=handle_asc_exception) as g:
        g.custom_command('set', 'config_git_set')
        g.custom_command('repo add', 'config_repo_add')
        g.custom_command('repo remove', 'config_repo_delete')
        g.custom_command('repo update', 'config_repo_update')
        g.custom_command('repo list', 'config_repo_list')

    with self.command_group('spring-cloud app', custom_command_type=app_command,
                            deprecate_info=self.deprecate(target='spring-cloud app', redirect='spring app',
                                                          message_func=_metadata_deprecate_message),
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('create', 'app_create')
        g.custom_command('update', 'app_update', supports_no_wait=True)
        g.custom_command('deploy', 'app_deploy', supports_no_wait=True)

    with self.command_group('spring-cloud app', client_factory=cf_spring_cloud_20220101preview,
                            deprecate_info=self.deprecate(target='spring-cloud app', redirect='spring app',
                                                          message_func=_metadata_deprecate_message),
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
            'show', 'app_get', table_transformer=transform_app_table_output,
            client_factory=cf_spring_cloud_20220301preview)
        g.custom_command('start', 'app_start', supports_no_wait=True)
        g.custom_command('stop', 'app_stop', supports_no_wait=True)
        g.custom_command('restart', 'app_restart', supports_no_wait=True)
        g.custom_command('logs', 'app_tail_log')
        g.custom_command('append-persistent-storage', 'app_append_persistent_storage')
        g.custom_command('append-loaded-public-certificate', 'app_append_loaded_public_certificate')

    with self.command_group('spring-cloud app identity', custom_command_type=app_managed_identity_command,
                            deprecate_info=self.deprecate(target='spring-cloud app identity', redirect='spring app identity',
                                                          message_func=_metadata_deprecate_message),
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('assign', 'app_identity_assign', validator=validate_app_identity_assign_or_warning)
        g.custom_command('remove', 'app_identity_remove', validator=validate_app_identity_remove_or_warning)
        g.custom_command('force-set', 'app_identity_force_set', is_preview=True)
        g.custom_show_command('show', 'app_identity_show')

    with self.command_group('spring-cloud app log', client_factory=cf_spring_cloud_20220101preview,
                            deprecate_info=g.deprecate(redirect='az spring app logs', hide=True,
                                                       message_func=_metadata_deprecate_message),
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('tail', 'app_tail_log')

    with self.command_group('spring-cloud app deployment', custom_command_type=app_command,
                            deprecate_info=self.deprecate(target='spring-cloud app deployment', redirect='spring app deployment',
                                                          message_func=_metadata_deprecate_message),
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('create', 'deployment_create', supports_no_wait=True)

    with self.command_group('spring-cloud app deployment', client_factory=cf_spring_cloud_20220101preview,
                            deprecate_info=self.deprecate(target='spring-cloud app deployment', redirect='spring app deployment',
                                                          message_func=_metadata_deprecate_message),
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('list', 'deployment_list',
                         table_transformer=transform_spring_cloud_deployment_output)
        g.custom_show_command(
            'show', 'deployment_get', table_transformer=transform_spring_cloud_deployment_output)
        g.custom_command('delete', 'deployment_delete', supports_no_wait=True)
        g.custom_command('generate-heap-dump', 'deployment_generate_heap_dump')
        g.custom_command('generate-thread-dump', 'deployment_generate_thread_dump')
        g.custom_command('start-jfr', 'deployment_start_jfr')

    with self.command_group('spring-cloud app binding', client_factory=cf_spring_cloud_20220101preview,
                            deprecate_info=self.deprecate(target='spring-cloud app binding', redirect='spring app binding',
                                                          message_func=_metadata_deprecate_message),
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

    with self.command_group('spring-cloud storage', client_factory=cf_spring_cloud_20220101preview,
                            deprecate_info=self.deprecate(target='spring-cloud storage', redirect='spring storage',
                                                          message_func=_metadata_deprecate_message),
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('list', 'storage_list')
        g.custom_show_command('show', 'storage_get')
        g.custom_command('add', 'storage_add')
        g.custom_command('update', 'storage_update')
        g.custom_command('remove', 'storage_remove')
        g.custom_command('list-persistent-storage', "storage_list_persistent_storage", table_transformer=transform_app_table_output)

    with self.command_group('spring-cloud certificate', client_factory=cf_spring_cloud_20220101preview,
                            deprecate_info=self.deprecate(target='spring-cloud certificate', redirect='spring certificate',
                                                          message_func=_metadata_deprecate_message),
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('add', 'certificate_add')
        g.custom_show_command('show', 'certificate_show', table_transformer=transform_spring_cloud_certificate_output)
        g.custom_command('list', 'certificate_list', table_transformer=transform_spring_cloud_certificate_output)
        g.custom_command('remove', 'certificate_remove')
        g.custom_command('list-reference-app', 'certificate_list_reference_app', table_transformer=transform_app_table_output)

    with self.command_group('spring-cloud app custom-domain', client_factory=cf_spring_cloud_20220101preview,
                            deprecate_info=self.deprecate(target='spring-cloud app custom-domain',
                                                          redirect='spring app custom-domain',
                                                          message_func=_metadata_deprecate_message),
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('bind', 'domain_bind')
        g.custom_show_command('show', 'domain_show', table_transformer=transform_spring_cloud_custom_domain_output)
        g.custom_command('list', 'domain_list', table_transformer=transform_spring_cloud_custom_domain_output)
        g.custom_command('update', 'domain_update')
        g.custom_command('unbind', 'domain_unbind')

    with self.command_group('spring-cloud app-insights',
                            client_factory=cf_spring_cloud_20201101preview,
                            deprecate_info=self.deprecate(target='spring-cloud app-insights', redirect='spring app-insights',
                                                          message_func=_metadata_deprecate_message),
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('update', 'app_insights_update', supports_no_wait=True)
        g.custom_show_command('show', 'app_insights_show')

    with self.command_group('spring-cloud service-registry',
                            custom_command_type=service_registry_cmd_group,
                            deprecate_info=self.deprecate(target='spring-cloud service-registry',
                                                          redirect='spring service-registry',
                                                          message_func=_metadata_deprecate_message),
                            exception_handler=handle_asc_exception,
                            is_preview=True) as g:
        g.custom_show_command('show', 'service_registry_show',
                              table_transformer=transform_service_registry_output)
        g.custom_command('bind', 'service_registry_bind')
        g.custom_command('unbind', 'service_registry_unbind')

    with self.command_group('spring-cloud application-configuration-service',
                            custom_command_type=application_configuration_service_cmd_group,
                            deprecate_info=self.deprecate(target='spring-cloud application-configuration-service',
                                                          redirect='spring application-configuration-service',
                                                          message_func=_metadata_deprecate_message),
                            exception_handler=handle_asc_exception,
                            is_preview=True) as g:
        g.custom_command('clear', 'application_configuration_service_clear')
        g.custom_show_command('show', 'application_configuration_service_show',
                              table_transformer=transform_application_configuration_service_output)
        g.custom_command('bind', 'application_configuration_service_bind')
        g.custom_command('unbind', 'application_configuration_service_unbind')

    with self.command_group('spring-cloud application-configuration-service git repo',
                            deprecate_info=self.deprecate(target='spring-cloud application-configuration-service git repo',
                                                          redirect='spring application-configuration-service git repo',
                                                          message_func=_metadata_deprecate_message),
                            custom_command_type=application_configuration_service_cmd_group,
                            exception_handler=handle_asc_exception) as g:
        g.custom_command('add', 'application_configuration_service_git_add')
        g.custom_command('update', 'application_configuration_service_git_update')
        g.custom_command('remove', 'application_configuration_service_git_remove')
        g.custom_command('list', 'application_configuration_service_git_list')

    with self.command_group('spring-cloud gateway',
                            custom_command_type=gateway_cmd_group,
                            deprecate_info=self.deprecate(target='spring-cloud gateway', redirect='spring gateway',
                                                          message_func=_metadata_deprecate_message),
                            exception_handler=handle_asc_exception,
                            is_preview=True) as g:
        g.custom_show_command('show', 'gateway_show', table_transformer=transform_spring_cloud_gateway_output)
        g.custom_command('update', 'gateway_update', validator=validate_gateway_update, supports_no_wait=True)
        g.custom_command('clear', 'gateway_clear', supports_no_wait=True)

    with self.command_group('spring-cloud gateway custom-domain',
                            custom_command_type=gateway_custom_domain_cmd_group,
                            deprecate_info=self.deprecate(target='spring-cloud gateway custom-domain',
                                                          redirect='spring gateway custom-domain',
                                                          message_func=_metadata_deprecate_message),
                            exception_handler=handle_asc_exception) as g:
        g.custom_show_command('show', 'gateway_custom_domain_show',
                              table_transformer=transform_spring_cloud_custom_domain_output)
        g.custom_command('list', 'gateway_custom_domain_list',
                         table_transformer=transform_spring_cloud_custom_domain_output)
        g.custom_command('bind', 'gateway_custom_domain_update')
        g.custom_command('unbind', 'gateway_custom_domain_unbind')
        g.custom_command('update', 'gateway_custom_domain_update')

    with self.command_group('spring-cloud gateway route-config',
                            custom_command_type=gateway_route_config_cmd_group,
                            deprecate_info=self.deprecate(target='spring-cloud gateway route-config',
                                                          redirect='spring gateway route-config',
                                                          message_func=_metadata_deprecate_message),
                            exception_handler=handle_asc_exception) as g:
        g.custom_show_command('show', 'gateway_route_config_show')
        g.custom_command('list', 'gateway_route_config_list')
        g.custom_command('create', 'gateway_route_config_create')
        g.custom_command('update', 'gateway_route_config_update')
        g.custom_command('remove', 'gateway_route_config_remove')

    with self.command_group('spring-cloud api-portal',
                            custom_command_type=api_portal_cmd_group,
                            deprecate_info=self.deprecate(target='spring-cloud api-portal',
                                                          redirect='spring api-portal',
                                                          message_func=_metadata_deprecate_message),
                            exception_handler=handle_asc_exception,
                            is_preview=True) as g:
        g.custom_show_command('show', 'api_portal_show', table_transformer=transform_api_portal_output)
        g.custom_command('update', 'api_portal_update', validator=validate_api_portal_update)
        g.custom_command('clear', 'api_portal_clear')

    with self.command_group('spring-cloud api-portal custom-domain',
                            custom_command_type=api_portal_custom_domain_cmd_group,
                            deprecate_info=self.deprecate(target='spring-cloud api-portal custom-domain',
                                                          redirect='spring api-portal custom-domain',
                                                          message_func=_metadata_deprecate_message),
                            exception_handler=handle_asc_exception) as g:
        g.custom_show_command('show', 'api_portal_custom_domain_show',
                              table_transformer=transform_spring_cloud_custom_domain_output)
        g.custom_command('list', 'api_portal_custom_domain_list',
                         table_transformer=transform_spring_cloud_custom_domain_output)
        g.custom_command('bind', 'api_portal_custom_domain_update')
        g.custom_command('unbind', 'api_portal_custom_domain_unbind')
        g.custom_command('update', 'api_portal_custom_domain_update')

    with self.command_group('spring-cloud build-service builder',
                            custom_command_type=builder_cmd_group,
                            deprecate_info=self.deprecate(target='spring-cloud build-service builder',
                                                          redirect='spring build-service builder',
                                                          message_func=_metadata_deprecate_message),
                            exception_handler=handle_asc_exception, is_preview=True) as g:
        g.custom_command('create', 'create_or_update_builder', supports_no_wait=True)
        g.custom_command('update', 'create_or_update_builder', supports_no_wait=True)
        g.custom_show_command('show', 'builder_show')
        g.custom_command('delete', 'builder_delete', supports_no_wait=True, confirmation=True)

    with self.command_group('spring-cloud build-service builder buildpack-binding',
                            custom_command_type=buildpack_binding_cmd_group,
                            deprecate_info=self.deprecate(target='spring-cloud build-service builder buildpack-binding',
                                                          redirect='spring build-service builder buildpack-binding',
                                                          message_func=_metadata_deprecate_message),
                            exception_handler=handle_asc_exception, is_preview=True) as g:
        g.custom_command('create', 'create_or_update_buildpack_binding')
        g.custom_command('set', 'create_or_update_buildpack_binding')
        g.custom_show_command('show', 'buildpack_binding_show')
        g.custom_command('list', 'buildpack_binding_list')
        g.custom_command('delete', 'buildpack_binding_delete', confirmation=True)

    with self.command_group('spring-cloud build-service', exception_handler=handle_asc_exception,
                            deprecate_info=self.deprecate(target='spring-cloud build-service', redirect='spring build-service',
                                                          message_func=_metadata_deprecate_message),
                            is_preview=True):
        pass

    with self.command_group('spring-cloud', exception_handler=handle_asc_exception,
                            deprecate_info=self.deprecate(target='spring-cloud', redirect='spring', hide=True,
                                                          message_func=_metadata_deprecate_message)):
        pass
