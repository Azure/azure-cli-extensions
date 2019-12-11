# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument


def list_datafactory(cmd, client):
    return client.list()


def create_datafactory(cmd, client,
                       resource_group,
                       name,
                       git_hub_access_code,
                       git_hub_access_token_base_url,
                       factory_resource_id=None,
                       repo_configuration=None,
                       location=None,
                       tags=None,
                       additional_properties=None,
                       identity=None,
                       git_hub_client_id=None,
                       permissions=None,
                       access_resource_path=None,
                       profile_name=None,
                       start_time=None,
                       expire_time=None):
    body = {}
    body['factory_resource_id'] = factory_resource_id  # str
    body['repo_configuration'] = json.loads(repo_configuration) if isinstance(repo_configuration, str) else repo_configuration
    body['location'] = location  # str
    body['tags'] = tags  # dictionary
    body['additional_properties'] = additional_properties  # dictionary
    body['identity'] = json.loads(identity) if isinstance(identity, str) else identity
    body['git_hub_access_code'] = git_hub_access_code  # str
    body['git_hub_client_id'] = git_hub_client_id  # str
    body['git_hub_access_token_base_url'] = git_hub_access_token_base_url  # str
    body['permissions'] = permissions  # str
    body['access_resource_path'] = access_resource_path  # str
    body['profile_name'] = profile_name  # str
    body['start_time'] = start_time  # str
    body['expire_time'] = expire_time  # str
    return client.create_or_update(resource_group_name=resource_group, factory_name=name, factory=body)


def update_datafactory(cmd, client,
                       resource_group,
                       name,
                       factory_resource_id=None,
                       repo_configuration=None,
                       location=None,
                       tags=None,
                       additional_properties=None,
                       identity=None,
                       git_hub_access_code=None,
                       git_hub_client_id=None,
                       git_hub_access_token_base_url=None,
                       permissions=None,
                       access_resource_path=None,
                       profile_name=None,
                       start_time=None,
                       expire_time=None):
    body = client.get(resource_group_name=resource_group, factory_name=name, if-none-match=body).as_dict()
    if factory_resource_id is not None:
        body['factory_resource_id'] = factory_resource_id  # str
    if repo_configuration is not None:
        body['repo_configuration'] = json.loads(repo_configuration) if isinstance(repo_configuration, str) else repo_configuration
    if location is not None:
        body['location'] = location  # str
    if tags is not None:
        body['tags'] = tags  # dictionary
    if additional_properties is not None:
        body['additional_properties'] = additional_properties  # dictionary
    if identity is not None:
        body['identity'] = json.loads(identity) if isinstance(identity, str) else identity
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
    return client.get(resource_group_name=resource_group, factory_name=name, if-none-match=body)


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
    body = client.get(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=name, if-none-match=body).as_dict()
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
    return client.get(resource_group_name=resource_group, factory_name=factory_name, integration_runtime_name=name, if-none-match=body)


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
                                     additional_properties=None,
                                     connect_via=None,
                                     description=None,
                                     parameters=None,
                                     annotations=None):
    body = {}
    body['additional_properties'] = additional_properties  # dictionary
    body['connect_via'] = json.loads(connect_via) if isinstance(connect_via, str) else connect_via
    body['description'] = description  # str
    body['parameters'] = parameters  # dictionary
    body['annotations'] = None if annotations is None else annotations.split(',')
    return client.create_or_update(resource_group_name=resource_group, factory_name=factory_name, linked_service_name=name, linked_service=body)


def update_datafactory_linkedservice(cmd, client,
                                     resource_group,
                                     factory_name,
                                     name,
                                     additional_properties=None,
                                     connect_via=None,
                                     description=None,
                                     parameters=None,
                                     annotations=None):
    body = client.get(resource_group_name=resource_group, factory_name=factory_name, linked_service_name=name, if-none-match=body).as_dict()
    if additional_properties is not None:
        body['additional_properties'] = additional_properties  # dictionary
    if connect_via is not None:
        body['connect_via'] = json.loads(connect_via) if isinstance(connect_via, str) else connect_via
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
    return client.get(resource_group_name=resource_group, factory_name=factory_name, linked_service_name=name, if-none-match=body)


def list_datafactory_linkedservice(cmd, client,
                                   resource_group,
                                   factory_name):
    return client.list_by_factory(resource_group_name=resource_group, factory_name=factory_name)


def create_datafactory_dataset(cmd, client,
                               resource_group,
                               factory_name,
                               name,
                               linked_service_name,
                               additional_properties=None,
                               description=None,
                               structure=None,
                               schema=None,
                               parameters=None,
                               annotations=None,
                               folder=None):
    body = {}
    body['additional_properties'] = additional_properties  # dictionary
    body['description'] = description  # str
    body['structure'] = structure  # unknown-primary[object]
    body['schema'] = schema  # unknown-primary[object]
    body['linked_service_name'] = json.loads(linked_service_name) if isinstance(linked_service_name, str) else linked_service_name
    body['parameters'] = parameters  # dictionary
    body['annotations'] = None if annotations is None else annotations.split(',')
    body['folder'] = json.loads(folder) if isinstance(folder, str) else folder
    return client.create_or_update(resource_group_name=resource_group, factory_name=factory_name, dataset_name=name, dataset=body)


def update_datafactory_dataset(cmd, client,
                               resource_group,
                               factory_name,
                               name,
                               additional_properties=None,
                               description=None,
                               structure=None,
                               schema=None,
                               linked_service_name=None,
                               parameters=None,
                               annotations=None,
                               folder=None):
    body = client.get(resource_group_name=resource_group, factory_name=factory_name, dataset_name=name, if-none-match=body).as_dict()
    if additional_properties is not None:
        body['additional_properties'] = additional_properties  # dictionary
    if description is not None:
        body['description'] = description  # str
    if structure is not None:
        body['structure'] = structure  # unknown-primary[object]
    if schema is not None:
        body['schema'] = schema  # unknown-primary[object]
    if linked_service_name is not None:
        body['linked_service_name'] = json.loads(linked_service_name) if isinstance(linked_service_name, str) else linked_service_name
    if parameters is not None:
        body['parameters'] = parameters  # dictionary
    if annotations is not None:
        body['annotations'] = None if annotations is None else annotations.split(',')
    if folder is not None:
        body['folder'] = json.loads(folder) if isinstance(folder, str) else folder
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
    return client.get(resource_group_name=resource_group, factory_name=factory_name, dataset_name=name, if-none-match=body)


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
                                folder=None):
    body = {}
    body['additional_properties'] = additional_properties  # dictionary
    body['description'] = description  # str
    body['activities'] = activities
    body['parameters'] = parameters  # dictionary
    body['variables'] = variables  # dictionary
    body['concurrency'] = concurrency  # number
    body['annotations'] = None if annotations is None else annotations.split(',')
    body['run_dimensions'] = run_dimensions  # dictionary
    body['folder'] = json.loads(folder) if isinstance(folder, str) else folder
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
                                folder=None):
    body = client.get(resource_group_name=resource_group, factory_name=factory_name, pipeline_name=pipeline_name, if-none-match=body).as_dict()
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
    if folder is not None:
        body['folder'] = json.loads(folder) if isinstance(folder, str) else folder
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
    return client.get(resource_group_name=resource_group, factory_name=factory_name, pipeline_name=pipeline_name, if-none-match=body)


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
    body = client.get(resource_group_name=resource_group, factory_name=factory_name, trigger_name=name, if-none-match=body).as_dict()
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
    return client.get(resource_group_name=resource_group, factory_name=factory_name, trigger_name=name, if-none-match=body)


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
                                folder=None):
    body = {}
    body['description'] = description  # str
    body['annotations'] = None if annotations is None else annotations.split(',')
    body['folder'] = json.loads(folder) if isinstance(folder, str) else folder
    return client.create_or_update(resource_group_name=resource_group, factory_name=factory_name, data_flow_name=name, data_flow=body)


def update_datafactory_dataflow(cmd, client,
                                resource_group,
                                factory_name,
                                name,
                                description=None,
                                annotations=None,
                                folder=None):
    body = client.get(resource_group_name=resource_group, factory_name=factory_name, data_flow_name=name, if-none-match=body).as_dict()
    if description is not None:
        body['description'] = description  # str
    if annotations is not None:
        body['annotations'] = None if annotations is None else annotations.split(',')
    if folder is not None:
        body['folder'] = json.loads(folder) if isinstance(folder, str) else folder
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
    return client.get(resource_group_name=resource_group, factory_name=factory_name, data_flow_name=name, if-none-match=body)


def list_datafactory_dataflow(cmd, client,
                              resource_group,
                              factory_name):
    return client.list_by_factory(resource_group_name=resource_group, factory_name=factory_name)


def create_datafactory_create_data_flow_debug_session(cmd, client,
                                                      resource_group,
                                                      name,
                                                      compute_type=None,
                                                      core_count=None,
                                                      time_to_live=None,
                                                      integration_runtime=None,
                                                      additional_properties=None,
                                                      session_id=None,
                                                      data_flow=None,
                                                      datasets=None,
                                                      linked_services=None,
                                                      staging=None,
                                                      debug_settings=None,
                                                      command=None,
                                                      command_payload=None):
    body = {}
    body['compute_type'] = compute_type  # str
    body['core_count'] = core_count  # number
    body['time_to_live'] = time_to_live  # number
    body['integration_runtime'] = json.loads(integration_runtime) if isinstance(integration_runtime, str) else integration_runtime
    body['additional_properties'] = additional_properties  # dictionary
    body['session_id'] = session_id  # str
    body['data_flow'] = json.loads(data_flow) if isinstance(data_flow, str) else data_flow
    body['datasets'] = datasets
    body['linked_services'] = linked_services
    body['staging'] = json.loads(staging) if isinstance(staging, str) else staging
    body['debug_settings'] = json.loads(debug_settings) if isinstance(debug_settings, str) else debug_settings
    body['command'] = command  # str
    body['command_payload'] = json.loads(command_payload) if isinstance(command_payload, str) else command_payload
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
    return client.delete(resource_group_name=resource_group, factory_name=name, request=body)


def execute_command_datafactory_create_data_flow_debug_session(cmd, client,
                                                               resource_group,
                                                               name):
    body = {}
    return client.execute_command(resource_group_name=resource_group, factory_name=name, request=body)
