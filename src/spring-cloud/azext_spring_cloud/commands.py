# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from ._client_factory import (cf_app_services, cf_spring_cloud, cf_bindings)
from ._transformers import (transform_spring_cloud_table_output,
                            transform_app_table_output, transform_spring_cloud_deployment_output)


# pylint: disable=too-many-statements
def load_command_table(self, _):

    with self.command_group('spring-cloud', client_factory=cf_app_services) as g:
        g.custom_command('create', 'spring_cloud_create',
                         supports_no_wait=True)
        g.custom_command('delete', 'spring_cloud_delete',
                         supports_no_wait=True)
        g.custom_command('list', 'spring_cloud_list',
                         table_transformer=transform_spring_cloud_table_output)
        g.custom_show_command('show', 'spring_cloud_get',
                              table_transformer=transform_spring_cloud_table_output)

    with self.command_group('spring-cloud test-endpoint', client_factory=cf_spring_cloud) as g:
        g.custom_command('enable ', 'enable_test_endpoint')
        g.custom_show_command('disable ', 'disable_test_endpoint')
        g.custom_command('renew-key', 'regenerate_keys')
        g.custom_command('list', 'list_keys')

    with self.command_group('spring-cloud config-server', client_factory=cf_app_services) as g:
        g.custom_command('set', 'config_set', supports_no_wait=True)
        g.custom_command('clear', 'config_delete')
        g.custom_show_command('show', 'config_get')

    with self.command_group('spring-cloud config-server git', client_factory=cf_app_services, supports_local_cache=True) as g:
        g.custom_command('set', 'config_git_set')
        g.custom_command('repo add', 'config_repo_add')
        g.custom_command('repo remove', 'config_repo_delete')
        g.custom_command('repo update', 'config_repo_update')
        g.custom_command('repo list', 'config_repo_list')

    with self.command_group('spring-cloud app', client_factory=cf_spring_cloud) as g:
        g.custom_command('create', 'app_create')
        g.custom_command('update', 'app_update')
        g.custom_command('deploy', 'app_deploy', supports_no_wait=True)
        g.custom_command('scale', 'app_scale', supports_no_wait=True)
        g.custom_command('show-deploy-log', 'app_get_build_log')
        g.custom_command('set-deployment', 'app_set_deployment',
                         supports_no_wait=True)
        g.custom_command('delete', 'app_delete')
        g.custom_command('list', 'app_list',
                         table_transformer=transform_app_table_output)
        g.custom_show_command(
            'show', 'app_get', table_transformer=transform_app_table_output)
        g.custom_command('start', 'app_start', supports_no_wait=True)
        g.custom_command('stop', 'app_stop', supports_no_wait=True)
        g.custom_command('restart', 'app_restart', supports_no_wait=True)

    with self.command_group('spring-cloud app deployment', client_factory=cf_spring_cloud) as g:
        g.custom_command('create', 'deployment_create', supports_no_wait=True)
        g.custom_command('list', 'deployment_list',
                         table_transformer=transform_spring_cloud_deployment_output)
        g.custom_show_command(
            'show', 'deployment_get', table_transformer=transform_spring_cloud_deployment_output)
        g.custom_command('delete', 'deployment_delete')

    with self.command_group('spring-cloud app binding', client_factory=cf_bindings) as g:
        g.custom_command('list', 'binding_list')
        g.custom_command('show', 'binding_get')
        g.custom_command('cosmos add', 'binding_cosmos_add')
        g.custom_command('cosmos update', 'binding_cosmos_update')
        g.custom_command('mysql add', 'binding_mysql_add')
        g.custom_command('mysql update', 'binding_mysql_update')
        g.custom_command('redis add', 'binding_redis_add')
        g.custom_command('redis update', 'binding_redis_update')
        g.custom_show_command('remove', 'binding_remove')

    with self.command_group('spring-cloud', is_preview=True):
        pass
