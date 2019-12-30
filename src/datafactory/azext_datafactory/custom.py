# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument

from ._client_factory import cf_resource_groups


def _get_rg_location(ctx, resource_group_name, subscription_id=None):
    groups = cf_resource_groups(ctx, subscription_id=subscription_id)
    # Just do the get, we don't need the result, it will error out if the group doesn't exist.
    rg = groups.get(resource_group_name)
    return rg.location


def list_datafactory(cmd, client):
    return client.list()


def create_datafactory(cmd, client,
                       resource_group,
                       name,
                       account_name=None,
                       repository_name=None,
                       collaboration_branch=None,
                       root_folder=None,
                       _type=None,
                       repo_configuration_account_name=None,
                       repo_configuration_repository_name=None,
                       repo_configuration_collaboration_branch=None,
                       repo_configuration_root_folder=None,
                       git_hub_access_code=None,
                       git_hub_access_token_base_url=None,
                       factory_resource_id=None,
                       last_commit_id=None,
                       location=None,
                       tags=None,
                       additional_properties=None,
                       repo_configuration_last_commit_id=None,
                       git_hub_client_id=None,
                       permissions=None,
                       access_resource_path=None,
                       profile_name=None,
                       start_time=None,
                       expire_time=None):
    body = {}
    if factory_resource_id is not None:
        body['factory_resource_id'] = factory_resource_id  # str
    if account_name is not None:
        body.setdefault('repo_configuration', {})['account_name'] = account_name  # str
    if repository_name is not None:
        body.setdefault('repo_configuration', {})['repository_name'] = repository_name  # str
    if collaboration_branch is not None:
        body.setdefault('repo_configuration', {})['collaboration_branch'] = collaboration_branch  # str
    if root_folder is not None:
        body.setdefault('repo_configuration', {})['root_folder'] = root_folder  # str
    if last_commit_id is not None:
        body.setdefault('repo_configuration', {})['last_commit_id'] = last_commit_id  # str

    if location is None:
        rg_location = _get_rg_location(cmd.cli_ctx, resource_group)
        location = rg_location
    body['location'] = location
    
    if tags is not None:
        body['tags'] = tags  # dictionary
    if additional_properties is not None:
        body['additional_properties'] = additional_properties  # dictionary
    if _type is not None:
        body.setdefault('identity', {})['type'] = _type  # str
    if repo_configuration_account_name is not None:
        body.setdefault('repo_configuration', {})['account_name'] = repo_configuration_account_name  # str
    if repo_configuration_repository_name is not None:
        body.setdefault('repo_configuration', {})['repository_name'] = repo_configuration_repository_name  # str
    if repo_configuration_collaboration_branch is not None:
        body.setdefault('repo_configuration', {})['collaboration_branch'] = repo_configuration_collaboration_branch  # str
    if repo_configuration_root_folder is not None:
        body.setdefault('repo_configuration', {})['root_folder'] = repo_configuration_root_folder  # str
    if repo_configuration_last_commit_id is not None:
        body.setdefault('repo_configuration', {})['last_commit_id'] = repo_configuration_last_commit_id  # str
    if git_hub_access_code is not None:
        body['git_hub_access_code'] = git_hub_access_code  # str
    if git_hub_client_id is not None:
        body['git_hub_client_id'] = git_hub_client_id  # str
    if git_hub_access_token_base_url is not None:
        body['git_hub_access_token_base_url'] = git_hub_access_token_base_url  # str
    if permissions is not None:
        body['permissions'] = permissions  # str
    if access_resource_path is not None:
        body['access_resource_path'] = access_resource_path  # str
    if profile_name is not None:
        body['profile_name'] = profile_name  # str
    if start_time is not None:
        body['start_time'] = start_time  # str
    if expire_time is not None:
        body['expire_time'] = expire_time  # str
    return client.create_or_update(resource_group_name=resource_group, factory_name=name, factory=body)


def update_datafactory(cmd, client,
                       resource_group,
                       name,
                       factory_resource_id=None,
                       account_name=None,
                       repository_name=None,
                       collaboration_branch=None,
                       root_folder=None,
                       last_commit_id=None,
                       location=None,
                       tags=None,
                       additional_properties=None,
                       _type=None,
                       repo_configuration_account_name=None,
                       repo_configuration_repository_name=None,
                       repo_configuration_collaboration_branch=None,
                       repo_configuration_root_folder=None,
                       repo_configuration_last_commit_id=None,
                       git_hub_access_code=None,
                       git_hub_client_id=None,
                       git_hub_access_token_base_url=None,
                       permissions=None,
                       access_resource_path=None,
                       profile_name=None,
                       start_time=None,
                       expire_time=None):
    body = {}
    body = client.get(resource_group_name=resource_group, factory_name=name, if_none_match=body).as_dict()
    if factory_resource_id is not None:
        body['factory_resource_id'] = factory_resource_id  # str
    if account_name is not None:
        body.setdefault('repo_configuration', {})['account_name'] = account_name  # str
    if repository_name is not None:
        body.setdefault('repo_configuration', {})['repository_name'] = repository_name  # str
    if collaboration_branch is not None:
        body.setdefault('repo_configuration', {})['collaboration_branch'] = collaboration_branch  # str
    if root_folder is not None:
        body.setdefault('repo_configuration', {})['root_folder'] = root_folder  # str
    if last_commit_id is not None:
        body.setdefault('repo_configuration', {})['last_commit_id'] = last_commit_id  # str
    if location is not None:
        body['location'] = location  # str
    if tags is not None:
        body['tags'] = tags  # dictionary
    if additional_properties is not None:
        body['additional_properties'] = additional_properties  # dictionary
    if _type is not None:
        body.setdefault('identity', {})['type'] = _type  # str
    if repo_configuration_account_name is not None:
        body.setdefault('repo_configuration', {})['account_name'] = repo_configuration_account_name  # str
    if repo_configuration_repository_name is not None:
        body.setdefault('repo_configuration', {})['repository_name'] = repo_configuration_repository_name  # str
    if repo_configuration_collaboration_branch is not None:
        body.setdefault('repo_configuration', {})['collaboration_branch'] = repo_configuration_collaboration_branch  # str
    if repo_configuration_root_folder is not None:
        body.setdefault('repo_configuration', {})['root_folder'] = repo_configuration_root_folder  # str
    if repo_configuration_last_commit_id is not None:
        body.setdefault('repo_configuration', {})['last_commit_id'] = repo_configuration_last_commit_id  # str
    if git_hub_access_code is not None:
        body['git_hub_access_code'] = git_hub_access_code  # str
    if git_hub_client_id is not None:
        body['git_hub_client_id'] = git_hub_client_id  # str
    if git_hub_access_token_base_url is not None:
        body['git_hub_access_token_base_url'] = git_hub_access_token_base_url  # str
    if permissions is not None:
        body['permissions'] = permissions  # str
    if access_resource_path is not None:
        body['access_resource_path'] = access_resource_path  # str
    if profile_name is not None:
        body['profile_name'] = profile_name  # str
    if start_time is not None:
        body['start_time'] = start_time  # str
    if expire_time is not None:
        body['expire_time'] = expire_time  # str
    return client.create_or_update(resource_group_name=resource_group, factory_name=name, factory=body)


def delete_datafactory(cmd, client,
                       resource_group,
                       name):
    return client.delete(resource_group_name=resource_group, factory_name=name)


def get_datafactory(cmd, client,
                    resource_group,
                    name):
    body = {}
    return client.get(resource_group_name=resource_group, factory_name=name, if_none_match=body)


def list_datafactory(cmd, client,
                     resource_group):
    if resource_group is not None:
        return client.list_by_resource_group(resource_group_name=resource_group)
    return client.list()


def configure_factory_repo_datafactory(cmd, client,
                                       location_id):
    body = {}
    return client.configure_factory_repo(location_id=location_id, factory_repo_update=body)


def get_git_hub_access_token_datafactory(cmd, client,
                                         resource_group,
                                         name):
    body = {}
    return client.get_git_hub_access_token(resource_group_name=resource_group, factory_name=name, git_hub_access_token_request=body)


def get_data_plane_access_datafactory(cmd, client,
                                      resource_group,
                                      name):
    body = {}
    return client.get_data_plane_access(resource_group_name=resource_group, factory_name=name, policy=body)


def get_feature_value_datafactory_get_feature_value(cmd, client,
                                                    location_id):
    body = {}
    return client.get_feature_value(location_id=location_id, exposure_control_request=body)


def get_feature_value_by_factory_datafactory_get_feature_value(cmd, client,
                                                               resource_group,
                                                               name):
    body = {}
    return client.get_feature_value_by_factory(resource_group_name=resource_group, factory_name=name, exposure_control_request=body)


def create_datafactory_integration_runtime(cmd, client,
                                           resource_group,
                                           factory_name,
                                           name,
                                           additional_properties=None,
                                           description=None,
                                           auto_update=None,
                                           update_delay_offset=None,
                                           key_name=None,
                                           subscription_id=None,
                                           data_factory_name=None,
                                           data_factory_location=None):
    body = {}
    body['additional_properties'] = additional_properties  # dictionary
    body['description'] = description  # str
    body['auto_update'] = auto_update  # str
    body['update_delay_offset'] = update_delay_offset  # str
    body['key_name'] = key_name  # str
    body['subscription_id'] = subscription_id  # str
    body['data_factory_name'] = data_factory_name  # str
    body['data_factory_location'] = data_factory_location  # str
    return client.create_or_update(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=name, integration_runtime=body)


def update_datafactory_integration_runtime(cmd, client,
                                           resource_group,
                                           factory_name,
                                           name,
                                           additional_properties=None,
                                           description=None,
                                           auto_update=None,
                                           update_delay_offset=None,
                                           key_name=None,
                                           subscription_id=None,
                                           data_factory_name=None,
                                           data_factory_location=None):
    body = {}
    body = client.get(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=name, if_none_match=body).as_dict()
    if additional_properties is not None:
        body['additional_properties'] = additional_properties  # dictionary
    if description is not None:
        body['description'] = description  # str
    if auto_update is not None:
        body['auto_update'] = auto_update  # str
    if update_delay_offset is not None:
        body['update_delay_offset'] = update_delay_offset  # str
    if key_name is not None:
        body['key_name'] = key_name  # str
    if subscription_id is not None:
        body['subscription_id'] = subscription_id  # str
    if data_factory_name is not None:
        body['data_factory_name'] = data_factory_name  # str
    if data_factory_location is not None:
        body['data_factory_location'] = data_factory_location  # str
    return client.create_or_update(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=name, integration_runtime=body)


def delete_datafactory_integration_runtime(cmd, client,
                                           resource_group,
                                           factory_name,
                                           name):
    return client.delete(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=name)


def get_datafactory_integration_runtime(cmd, client,
                                        resource_group,
                                        factory_name,
                                        name):
    body = {}
    return client.get(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=name, if_none_match=body)


def list_datafactory_integration_runtime(cmd, client,
                                         resource_group,
                                         factory_name):
    return client.list_by_factory(resource_group_name=resource_group, factory_name=factory_name)


def get_status_datafactory_integration_runtime(cmd, client,
                                               resource_group,
                                               factory_name,
                                               name):
    return client.get_status(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=name)


def get_connection_info_datafactory_integration_runtime(cmd, client,
                                                        resource_group,
                                                        factory_name,
                                                        name):
    return client.get_connection_info(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=name)


def regenerate_auth_key_datafactory_integration_runtime(cmd, client,
                                                        resource_group,
                                                        factory_name,
                                                        name):
    body = {}
    return client.regenerate_auth_key(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=name, regenerate_key_parameters=body)


def create_linked_integration_runtime_datafactory_integration_runtime(cmd, client,
                                                                      resource_group,
                                                                      factory_name,
                                                                      name):
    body = {}
    return client.create_linked_integration_runtime(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=name, create_linked_integration_runtime_request=body)


def start_datafactory_integration_runtime(cmd, client,
                                          resource_group,
                                          factory_name,
                                          name):
    return client.start(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=name)


def stop_datafactory_integration_runtime(cmd, client,
                                         resource_group,
                                         factory_name,
                                         name):
    return client.stop(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=name)


def sync_credentials_datafactory_integration_runtime(cmd, client,
                                                     resource_group,
                                                     factory_name,
                                                     name):
    return client.sync_credentials(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=name)


def get_monitoring_data_datafactory_integration_runtime(cmd, client,
                                                        resource_group,
                                                        factory_name,
                                                        name):
    return client.get_monitoring_data(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=name)


def upgrade_datafactory_integration_runtime(cmd, client,
                                            resource_group,
                                            factory_name,
                                            name):
    return client.upgrade(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=name)


def remove_links_datafactory_integration_runtime(cmd, client,
                                                 resource_group,
                                                 factory_name,
                                                 name):
    body = {}
    return client.remove_links(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=name, linked_integration_runtime_request=body)


def list_auth_keys_datafactory_integration_runtime(cmd, client,
                                                   resource_group,
                                                   factory_name,
                                                   name):
    return client.list_auth_keys(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=name)


def refresh_datafactory_integration_runtime_refresh_object_metadata(cmd, client,
                                                                    resource_group,
                                                                    factory_name,
                                                                    name):
    return client.refresh(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=name)


def get_datafactory_integration_runtime_refresh_object_metadata(cmd, client,
                                                                resource_group,
                                                                factory_name,
                                                                name):
    body = {}
    return client.get(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=name, get_metadata_request=body)


def update_datafactory_integration_runtime_node(cmd, client,
                                                resource_group,
                                                factory_name,
                                                integration_runtime_name,
                                                name,
                                                concurrent_jobs_limit=None):
    body = client.get(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=integration_runtime_name, node_name=name).as_dict()
    if concurrent_jobs_limit is not None:
        body['concurrent_jobs_limit'] = concurrent_jobs_limit  # number
    return client.update(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=integration_runtime_name, node_name=name, update_integration_runtime_node_request=body)


def delete_datafactory_integration_runtime_node(cmd, client,
                                                resource_group,
                                                factory_name,
                                                integration_runtime_name,
                                                name):
    return client.delete(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=integration_runtime_name, node_name=name)


def get_datafactory_integration_runtime_node(cmd, client,
                                             resource_group,
                                             factory_name,
                                             integration_runtime_name,
                                             name):
    return client.get(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=integration_runtime_name, node_name=name)


def get_ip_address_datafactory_integration_runtime_node(cmd, client,
                                                        resource_group,
                                                        factory_name,
                                                        integration_runtime_name,
                                                        name):
    return client.get_ip_address(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=integration_runtime_name, node_name=name)


def create_datafactory_linkedservice(cmd, client,
                                     resource_group,
                                     factory_name,
                                     name,
                                     connect_via_type,
                                     connect_via_reference_name,
                                     additional_properties=None,
                                     connect_via_parameters=None,
                                     description=None,
                                     parameters=None,
                                     annotations=None):
    body = {}
    body['additional_properties'] = additional_properties  # dictionary
    body.setdefault('connect_via', {})['type'] = connect_via_type  # str
    body.setdefault('connect_via', {})['reference_name'] = connect_via_reference_name  # str
    body.setdefault('connect_via', {})['parameters'] = connect_via_parameters  # dictionary
    body['description'] = description  # str
    body['parameters'] = parameters  # dictionary
    body['annotations'] = None if annotations is None else annotations.split(',')
    return client.create_or_update(resource_group_name=resource_group, factory_name=factory_name, linked_service_name=name, linked_service=body)


def update_datafactory_linkedservice(cmd, client,
                                     resource_group,
                                     factory_name,
                                     name,
                                     additional_properties=None,
                                     connect_via_type=None,
                                     connect_via_reference_name=None,
                                     connect_via_parameters=None,
                                     description=None,
                                     parameters=None,
                                     annotations=None):
    body = {}
    body = client.get(resource_group_name=resource_group, factory_name=factory_name, linked_service_name=name, if_none_match=body).as_dict()
    if additional_properties is not None:
        body['additional_properties'] = additional_properties  # dictionary
    if connect_via_type is not None:
        body.setdefault('connect_via', {})['type'] = connect_via_type  # str
    if connect_via_reference_name is not None:
        body.setdefault('connect_via', {})['reference_name'] = connect_via_reference_name  # str
    if connect_via_parameters is not None:
        body.setdefault('connect_via', {})['parameters'] = connect_via_parameters  # dictionary
    if description is not None:
        body['description'] = description  # str
    if parameters is not None:
        body['parameters'] = parameters  # dictionary
    if annotations is not None:
        body['annotations'] = None if annotations is None else annotations.split(',')
    return client.create_or_update(resource_group_name=resource_group, factory_name=factory_name, linked_service_name=name, linked_service=body)


def delete_datafactory_linkedservice(cmd, client,
                                     resource_group,
                                     factory_name,
                                     name):
    return client.delete(resource_group_name=resource_group, factory_name=factory_name, linked_service_name=name)


def get_datafactory_linkedservice(cmd, client,
                                  resource_group,
                                  factory_name,
                                  name):
    body = {}
    return client.get(resource_group_name=resource_group, factory_name=factory_name, linked_service_name=name, if_none_match=body)


def list_datafactory_linkedservice(cmd, client,
                                   resource_group,
                                   factory_name):
    return client.list_by_factory(resource_group_name=resource_group, factory_name=factory_name)


def create_datafactory_dataset(cmd, client,
                               resource_group,
                               factory_name,
                               name,
                               linked_service_name_type,
                               linked_service_name_reference_name,
                               additional_properties=None,
                               description=None,
                               structure=None,
                               schema=None,
                               linked_service_name_parameters=None,
                               parameters=None,
                               annotations=None,
                               folder_name=None):
    body = {}
    body['additional_properties'] = additional_properties  # dictionary
    body['description'] = description  # str
    body['structure'] = structure  # unknown-primary[object]
    body['schema'] = schema  # unknown-primary[object]
    body.setdefault('linked_service_name', {})['type'] = linked_service_name_type  # str
    body.setdefault('linked_service_name', {})['reference_name'] = linked_service_name_reference_name  # str
    body.setdefault('linked_service_name', {})['parameters'] = linked_service_name_parameters  # dictionary
    body['parameters'] = parameters  # dictionary
    body['annotations'] = None if annotations is None else annotations.split(',')
    body.setdefault('folder', {})['name'] = folder_name  # str
    return client.create_or_update(resource_group_name=resource_group, factory_name=factory_name, dataset_name=name, dataset=body)


def update_datafactory_dataset(cmd, client,
                               resource_group,
                               factory_name,
                               name,
                               additional_properties=None,
                               description=None,
                               structure=None,
                               schema=None,
                               linked_service_name_type=None,
                               linked_service_name_reference_name=None,
                               linked_service_name_parameters=None,
                               parameters=None,
                               annotations=None,
                               folder_name=None):
    body = {}
    body = client.get(resource_group_name=resource_group, factory_name=factory_name, dataset_name=name, if_none_match=body).as_dict()
    if additional_properties is not None:
        body['additional_properties'] = additional_properties  # dictionary
    if description is not None:
        body['description'] = description  # str
    if structure is not None:
        body['structure'] = structure  # unknown-primary[object]
    if schema is not None:
        body['schema'] = schema  # unknown-primary[object]
    if linked_service_name_type is not None:
        body.setdefault('linked_service_name', {})['type'] = linked_service_name_type  # str
    if linked_service_name_reference_name is not None:
        body.setdefault('linked_service_name', {})['reference_name'] = linked_service_name_reference_name  # str
    if linked_service_name_parameters is not None:
        body.setdefault('linked_service_name', {})['parameters'] = linked_service_name_parameters  # dictionary
    if parameters is not None:
        body['parameters'] = parameters  # dictionary
    if annotations is not None:
        body['annotations'] = None if annotations is None else annotations.split(',')
    if folder_name is not None:
        body.setdefault('folder', {})['name'] = folder_name  # str
    return client.create_or_update(resource_group_name=resource_group, factory_name=factory_name, dataset_name=name, dataset=body)


def delete_datafactory_dataset(cmd, client,
                               resource_group,
                               factory_name,
                               name):
    return client.delete(resource_group_name=resource_group, factory_name=factory_name, dataset_name=name)


def get_datafactory_dataset(cmd, client,
                            resource_group,
                            factory_name,
                            name):
    body = {}
    return client.get(resource_group_name=resource_group, factory_name=factory_name, dataset_name=name, if_none_match=body)


def list_datafactory_dataset(cmd, client,
                             resource_group,
                             factory_name):
    return client.list_by_factory(resource_group_name=resource_group, factory_name=factory_name)


def create_datafactory_pipeline(cmd, client,
                                resource_group,
                                factory_name,
                                pipeline_name,
                                additional_properties=None,
                                description=None,
                                activities=None,
                                parameters=None,
                                variables=None,
                                concurrency=None,
                                annotations=None,
                                run_dimensions=None,
                                folder_name=None):
    body = {}
    body['additional_properties'] = additional_properties  # dictionary
    body['description'] = description  # str
    body['activities'] = activities
    body['parameters'] = parameters  # dictionary
    body['variables'] = variables  # dictionary
    body['concurrency'] = concurrency  # number
    body['annotations'] = None if annotations is None else annotations.split(',')
    body['run_dimensions'] = run_dimensions  # dictionary
    body.setdefault('folder', {})['name'] = folder_name  # str
    return client.create_or_update(resource_group_name=resource_group, factory_name=factory_name, pipeline_name=pipeline_name, pipeline=body)


def update_datafactory_pipeline(cmd, client,
                                resource_group,
                                factory_name,
                                pipeline_name,
                                additional_properties=None,
                                description=None,
                                activities=None,
                                parameters=None,
                                variables=None,
                                concurrency=None,
                                annotations=None,
                                run_dimensions=None,
                                folder_name=None):
    body = {}
    body = client.get(resource_group_name=resource_group, factory_name=factory_name, pipeline_name=pipeline_name, if_none_match=body).as_dict()
    if additional_properties is not None:
        body['additional_properties'] = additional_properties  # dictionary
    if description is not None:
        body['description'] = description  # str
    if activities is not None:
        body['activities'] = activities
    if parameters is not None:
        body['parameters'] = parameters  # dictionary
    if variables is not None:
        body['variables'] = variables  # dictionary
    if concurrency is not None:
        body['concurrency'] = concurrency  # number
    if annotations is not None:
        body['annotations'] = None if annotations is None else annotations.split(',')
    if run_dimensions is not None:
        body['run_dimensions'] = run_dimensions  # dictionary
    if folder_name is not None:
        body.setdefault('folder', {})['name'] = folder_name  # str
    return client.create_or_update(resource_group_name=resource_group, factory_name=factory_name, pipeline_name=pipeline_name, pipeline=body)


def delete_datafactory_pipeline(cmd, client,
                                resource_group,
                                factory_name,
                                pipeline_name):
    return client.delete(resource_group_name=resource_group, factory_name=factory_name, pipeline_name=pipeline_name)


def get_datafactory_pipeline(cmd, client,
                             resource_group,
                             factory_name,
                             pipeline_name):
    body = {}
    return client.get(resource_group_name=resource_group, factory_name=factory_name, pipeline_name=pipeline_name, if_none_match=body)


def list_datafactory_pipeline(cmd, client,
                              resource_group,
                              factory_name):
    return client.list_by_factory(resource_group_name=resource_group, factory_name=factory_name)


def create_run_datafactory_pipeline(cmd, client,
                                    resource_group,
                                    factory_name,
                                    pipeline_name,
                                    reference_pipeline_run_id=None,
                                    is_recovery=None,
                                    name=None,
                                    parameters=None):
    return client.create_run(resource_group_name=resource_group, factory_name=factory_name, pipeline_name=pipeline_name, reference_pipeline_run_id=reference_pipeline_run_id, is_recovery=is_recovery, start_activity_name=name, parameters=parameters)


def query_by_factory_datafactory_query_pipeline_run(cmd, client,
                                                    resource_group,
                                                    name):
    body = {}
    return client.query_by_factory(resource_group_name=resource_group, factory_name=name, filter_parameters=body)


def cancel_datafactory_query_pipeline_run(cmd, client,
                                          resource_group,
                                          name,
                                          run_id,
                                          is_recursive=None):
    return client.cancel(resource_group_name=resource_group, factory_name=name, run_id=run_id, is_recursive=is_recursive)


def get_datafactory_query_pipeline_run(cmd, client,
                                       resource_group,
                                       name,
                                       run_id):
    return client.get(resource_group_name=resource_group, factory_name=name, run_id=run_id)


def query_by_pipeline_run_datafactory_pipelinerun_query_activityrun(cmd, client,
                                                                    resource_group,
                                                                    name,
                                                                    run_id):
    body = {}
    return client.query_by_pipeline_run(resource_group_name=resource_group, factory_name=name, run_id=run_id, filter_parameters=body)


def create_datafactory_trigger(cmd, client,
                               resource_group,
                               factory_name,
                               name,
                               additional_properties=None,
                               description=None,
                               annotations=None):
    body = {}
    body['additional_properties'] = additional_properties  # dictionary
    body['description'] = description  # str
    body['annotations'] = None if annotations is None else annotations.split(',')
    return client.create_or_update(resource_group_name=resource_group, factory_name=factory_name, trigger_name=name, trigger=body)


def update_datafactory_trigger(cmd, client,
                               resource_group,
                               factory_name,
                               name,
                               additional_properties=None,
                               description=None,
                               annotations=None):
    body = {}
    body = client.get(resource_group_name=resource_group, factory_name=factory_name, trigger_name=name, if_none_match=body).as_dict()
    if additional_properties is not None:
        body['additional_properties'] = additional_properties  # dictionary
    if description is not None:
        body['description'] = description  # str
    if annotations is not None:
        body['annotations'] = None if annotations is None else annotations.split(',')
    return client.create_or_update(resource_group_name=resource_group, factory_name=factory_name, trigger_name=name, trigger=body)


def delete_datafactory_trigger(cmd, client,
                               resource_group,
                               factory_name,
                               name):
    return client.delete(resource_group_name=resource_group, factory_name=factory_name, trigger_name=name)


def get_datafactory_trigger(cmd, client,
                            resource_group,
                            factory_name,
                            name):
    body = {}
    return client.get(resource_group_name=resource_group, factory_name=factory_name, trigger_name=name, if_none_match=body)


def list_datafactory_trigger(cmd, client,
                             resource_group,
                             factory_name):
    return client.list_by_factory(resource_group_name=resource_group, factory_name=factory_name)


def subscribe_to_events_datafactory_trigger(cmd, client,
                                            resource_group,
                                            factory_name,
                                            name):
    return client.subscribe_to_events(resource_group_name=resource_group, factory_name=factory_name, trigger_name=name)


def get_event_subscription_status_datafactory_trigger(cmd, client,
                                                      resource_group,
                                                      factory_name,
                                                      name):
    return client.get_event_subscription_status(resource_group_name=resource_group, factory_name=factory_name, trigger_name=name)


def unsubscribe_from_events_datafactory_trigger(cmd, client,
                                                resource_group,
                                                factory_name,
                                                name):
    return client.unsubscribe_from_events(resource_group_name=resource_group, factory_name=factory_name, trigger_name=name)


def start_datafactory_trigger(cmd, client,
                              resource_group,
                              factory_name,
                              name):
    return client.start(resource_group_name=resource_group, factory_name=factory_name, trigger_name=name)


def stop_datafactory_trigger(cmd, client,
                             resource_group,
                             factory_name,
                             name):
    return client.stop(resource_group_name=resource_group, factory_name=factory_name, trigger_name=name)


def rerun_datafactory_trigger_trigger_run_rerun(cmd, client,
                                                resource_group,
                                                factory_name,
                                                name,
                                                run_id):
    return client.rerun(resource_group_name=resource_group, factory_name=factory_name, trigger_name=name, run_id=run_id)


def query_by_factory_datafactory_trigger_trigger_run_rerun(cmd, client,
                                                           resource_group,
                                                           factory_name):
    body = {}
    return client.query_by_factory(resource_group_name=resource_group, factory_name=factory_name, filter_parameters=body)


def create_datafactory_trigger_rerun_trigger(cmd, client,
                                             resource_group,
                                             factory_name,
                                             trigger_name,
                                             name,
                                             start_time,
                                             end_time,
                                             max_concurrency):
    body = {}
    body['start_time'] = start_time  # datetime
    body['end_time'] = end_time  # datetime
    body['max_concurrency'] = max_concurrency  # number
    return client.create(resource_group_name=resource_group, factory_name=factory_name, trigger_name=trigger_name, rerun_trigger_name=name, rerun_tumbling_window_trigger_action_parameters=body)


def update_datafactory_trigger_rerun_trigger(cmd, client,
                                             resource_group,
                                             factory_name,
                                             trigger_name,
                                             name,
                                             start_time=None,
                                             end_time=None,
                                             max_concurrency=None):
    body = {}
    if start_time is not None:
        body['start_time'] = start_time  # datetime
    if end_time is not None:
        body['end_time'] = end_time  # datetime
    if max_concurrency is not None:
        body['max_concurrency'] = max_concurrency  # number
    return client.create(resource_group_name=resource_group, factory_name=factory_name, trigger_name=trigger_name, rerun_trigger_name=name, rerun_tumbling_window_trigger_action_parameters=body)


def list_datafactory_trigger_rerun_trigger(cmd, client,
                                           resource_group,
                                           factory_name,
                                           trigger_name):
    return client.list_by_trigger(resource_group_name=resource_group, factory_name=factory_name, trigger_name=trigger_name)


def start_datafactory_trigger_rerun_trigger(cmd, client,
                                            resource_group,
                                            factory_name,
                                            trigger_name,
                                            name):
    return client.start(resource_group_name=resource_group, factory_name=factory_name, trigger_name=trigger_name, rerun_trigger_name=name)


def stop_datafactory_trigger_rerun_trigger(cmd, client,
                                           resource_group,
                                           factory_name,
                                           trigger_name,
                                           name):
    return client.stop(resource_group_name=resource_group, factory_name=factory_name, trigger_name=trigger_name, rerun_trigger_name=name)


def cancel_datafactory_trigger_rerun_trigger(cmd, client,
                                             resource_group,
                                             factory_name,
                                             trigger_name,
                                             name):
    return client.cancel(resource_group_name=resource_group, factory_name=factory_name, trigger_name=trigger_name, rerun_trigger_name=name)


def create_datafactory_dataflow(cmd, client,
                                resource_group,
                                factory_name,
                                name,
                                description=None,
                                annotations=None,
                                folder_name=None):
    body = {}
    body['description'] = description  # str
    body['annotations'] = None if annotations is None else annotations.split(',')
    body.setdefault('folder', {})['name'] = folder_name  # str
    return client.create_or_update(resource_group_name=resource_group, factory_name=factory_name, data_flow_name=name, data_flow=body)


def update_datafactory_dataflow(cmd, client,
                                resource_group,
                                factory_name,
                                name,
                                description=None,
                                annotations=None,
                                folder_name=None):
    body = {}
    body = client.get(resource_group_name=resource_group, factory_name=factory_name, data_flow_name=name, if_none_match=body).as_dict()
    if description is not None:
        body['description'] = description  # str
    if annotations is not None:
        body['annotations'] = None if annotations is None else annotations.split(',')
    if folder_name is not None:
        body.setdefault('folder', {})['name'] = folder_name  # str
    return client.create_or_update(resource_group_name=resource_group, factory_name=factory_name, data_flow_name=name, data_flow=body)


def delete_datafactory_dataflow(cmd, client,
                                resource_group,
                                factory_name,
                                name):
    return client.delete(resource_group_name=resource_group, factory_name=factory_name, data_flow_name=name)


def get_datafactory_dataflow(cmd, client,
                             resource_group,
                             factory_name,
                             name):
    body = {}
    return client.get(resource_group_name=resource_group, factory_name=factory_name, data_flow_name=name, if_none_match=body)


def list_datafactory_dataflow(cmd, client,
                              resource_group,
                              factory_name):
    return client.list_by_factory(resource_group_name=resource_group, factory_name=factory_name)


def create_datafactory_create_data_flow_debug_session(cmd, client,
                                                      resource_group,
                                                      name,
                                                      linked_service_type,
                                                      linked_service_reference_name,
                                                      stream_name,
                                                      compute_type=None,
                                                      core_count=None,
                                                      time_to_live=None,
                                                      properties_additional_properties=None,
                                                      properties_description=None,
                                                      additional_properties=None,
                                                      session_id=None,
                                                      properties_annotations=None,
                                                      properties_folder_name=None,
                                                      datasets=None,
                                                      linked_services=None,
                                                      linked_service_parameters=None,
                                                      folder_path=None,
                                                      source_settings=None,
                                                      parameters=None,
                                                      dataset_parameters=None,
                                                      command=None,
                                                      row_limits=None,
                                                      columns=None,
                                                      expression=None):
    body = {}
    body['compute_type'] = compute_type  # str
    body['core_count'] = core_count  # number
    body['time_to_live'] = time_to_live  # number
    body.setdefault('integration_runtime', {}).setdefault('properties', {})['additional_properties'] = properties_additional_properties  # dictionary
    body.setdefault('integration_runtime', {}).setdefault('properties', {})['description'] = properties_description  # str
    body['additional_properties'] = additional_properties  # dictionary
    body['session_id'] = session_id  # str
    body.setdefault('data_flow', {}).setdefault('properties', {})['annotations'] = None if properties_annotations is None else properties_annotations.split(',')
    body.setdefault('data_flow', {}).setdefault('properties', {}).setdefault('folder', {})['name'] = properties_folder_name  # str
    body['datasets'] = datasets
    body['linked_services'] = linked_services
    body.setdefault('staging', {}).setdefault('linked_service', {})['type'] = linked_service_type  # str
    body.setdefault('staging', {}).setdefault('linked_service', {})['reference_name'] = linked_service_reference_name  # str
    body.setdefault('staging', {}).setdefault('linked_service', {})['parameters'] = linked_service_parameters  # dictionary
    body.setdefault('staging', {})['folder_path'] = folder_path  # str
    body.setdefault('debug_settings', {})['source_settings'] = source_settings
    body.setdefault('debug_settings', {})['parameters'] = parameters  # dictionary
    body.setdefault('debug_settings', {})['dataset_parameters'] = dataset_parameters  # unknown-primary[object]
    body['command'] = command  # str
    body.setdefault('command_payload', {})['stream_name'] = stream_name  # str
    body.setdefault('command_payload', {})['row_limits'] = row_limits  # number
    body.setdefault('command_payload', {})['columns'] = None if columns is None else columns.split(',')
    body.setdefault('command_payload', {})['expression'] = expression  # str
    return client.create(resource_group_name=resource_group, factory_name=name, request=body)


def query_by_factory_datafactory_create_data_flow_debug_session(cmd, client,
                                                                resource_group,
                                                                name):
    return client.query_by_factory(resource_group_name=resource_group, factory_name=name)


def add_data_flow_datafactory_create_data_flow_debug_session(cmd, client,
                                                             resource_group,
                                                             name):
    body = {}
    return client.add_data_flow(resource_group_name=resource_group, factory_name=name, request=body)


def delete_datafactory_create_data_flow_debug_session(cmd, client,
                                                      resource_group,
                                                      name):
    body = {}
    return client.delete(resource_group_name=resource_group, factory_name=name, request=body)


def execute_command_datafactory_create_data_flow_debug_session(cmd, client,
                                                               resource_group,
                                                               name):
    body = {}
    return client.execute_command(resource_group_name=resource_group, factory_name=name, request=body)
