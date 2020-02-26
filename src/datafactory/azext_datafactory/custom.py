# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument


def datafactory_operations_list(cmd, client):
    return client.list()


def datafactory_factories_list(cmd, client,
                               resource_group_name=None):
    if resource_group_name is not None:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list()


def datafactory_factories_show(cmd, client,
                               resource_group_name,
                               factory_name):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name)


def datafactory_factories_create(cmd, client,
                                 resource_group_name,
                                 factory_name,
                                 repo_configuration_type_repo_configuration,
                                 repo_configuration_account_name,
                                 repo_configuration_repository_name,
                                 repo_configuration_collaboration_branch,
                                 repo_configuration_root_folder,
                                 location=None,
                                 tags=None,
                                 repo_configuration_last_commit_id=None):
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, location=location, tags=tags, type_repo_configuration=repo_configuration_type_repo_configuration, account_name=repo_configuration_account_name, repository_name=repo_configuration_repository_name, collaboration_branch=repo_configuration_collaboration_branch, root_folder=repo_configuration_root_folder, last_commit_id=repo_configuration_last_commit_id)


def datafactory_factories_update(cmd, client,
                                 resource_group_name,
                                 factory_name,
                                 tags=None):
    return client.update(resource_group_name=resource_group_name, factory_name=factory_name, tags=tags)


def datafactory_factories_delete(cmd, client,
                                 resource_group_name,
                                 factory_name):
    return client.delete(resource_group_name=resource_group_name, factory_name=factory_name)


def datafactory_factories_configure_factory_repo(cmd, client,
                                                 location_id,
                                                 repo_configuration_type,
                                                 repo_configuration_account_name,
                                                 repo_configuration_repository_name,
                                                 repo_configuration_collaboration_branch,
                                                 repo_configuration_root_folder,
                                                 factory_resource_id=None,
                                                 repo_configuration_last_commit_id=None):
    return client.configure_factory_repo(location_id=location_id, factory_resource_id=factory_resource_id, type=repo_configuration_type, account_name=repo_configuration_account_name, repository_name=repo_configuration_repository_name, collaboration_branch=repo_configuration_collaboration_branch, root_folder=repo_configuration_root_folder, last_commit_id=repo_configuration_last_commit_id)


def datafactory_factories_get_data_plane_access(cmd, client,
                                                resource_group_name,
                                                factory_name,
                                                permissions=None,
                                                access_resource_path=None,
                                                profile_name=None,
                                                start_time=None,
                                                expire_time=None):
    return client.get_data_plane_access(resource_group_name=resource_group_name, factory_name=factory_name, permissions=permissions, access_resource_path=access_resource_path, profile_name=profile_name, start_time=start_time, expire_time=expire_time)


def datafactory_factories_get_git_hub_access_token(cmd, client,
                                                   resource_group_name,
                                                   factory_name,
                                                   git_hub_access_code,
                                                   git_hub_access_token_base_url,
                                                   git_hub_client_id=None):
    return client.get_git_hub_access_token(resource_group_name=resource_group_name, factory_name=factory_name, git_hub_access_code=git_hub_access_code, git_hub_client_id=git_hub_client_id, git_hub_access_token_base_url=git_hub_access_token_base_url)


def datafactory_exposure_control_get_feature_value_by_factory(cmd, client,
                                                              resource_group_name,
                                                              factory_name,
                                                              feature_name=None,
                                                              feature_type=None):
    return client.get_feature_value_by_factory(resource_group_name=resource_group_name, factory_name=factory_name, feature_name=feature_name, feature_type=feature_type)


def datafactory_exposure_control_get_feature_value(cmd, client,
                                                   location_id,
                                                   feature_name=None,
                                                   feature_type=None):
    return client.get_feature_value(location_id=location_id, feature_name=feature_name, feature_type=feature_type)


def datafactory_integration_runtimes_list(cmd, client,
                                          resource_group_name,
                                          factory_name):
    return client.list_by_factory(resource_group_name=resource_group_name, factory_name=factory_name)


def datafactory_integration_runtimes_show(cmd, client,
                                          resource_group_name,
                                          factory_name,
                                          integration_runtime_name):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


def datafactory_integration_runtimes_create(cmd, client,
                                            resource_group_name,
                                            factory_name,
                                            integration_runtime_name,
                                            properties_type,
                                            properties_description=None):
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, type=properties_type, description=properties_description)


def datafactory_integration_runtimes_update(cmd, client,
                                            resource_group_name,
                                            factory_name,
                                            integration_runtime_name,
                                            auto_update=None,
                                            update_delay_offset=None):
    return client.update(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, auto_update=auto_update, update_delay_offset=update_delay_offset)


def datafactory_integration_runtimes_delete(cmd, client,
                                            resource_group_name,
                                            factory_name,
                                            integration_runtime_name):
    return client.delete(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


def datafactory_integration_runtimes_create_linked_integration_runtime(cmd, client,
                                                                       resource_group_name,
                                                                       factory_name,
                                                                       integration_runtime_name,
                                                                       name=None,
                                                                       create_linked_integration_runtime_request_subscription_id=None,
                                                                       data_factory_name=None,
                                                                       data_factory_location=None):
    return client.create_linked_integration_runtime(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, name=name, create_linked_integration_runtime_request_subscription_id=create_linked_integration_runtime_request_subscription_id, data_factory_name=data_factory_name, data_factory_location=data_factory_location)


def datafactory_integration_runtimes_regenerate_auth_key(cmd, client,
                                                         resource_group_name,
                                                         factory_name,
                                                         integration_runtime_name,
                                                         key_name=None):
    return client.regenerate_auth_key(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, key_name=key_name)


def datafactory_integration_runtimes_remove_links(cmd, client,
                                                  resource_group_name,
                                                  factory_name,
                                                  integration_runtime_name,
                                                  linked_factory_name):
    return client.remove_links(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, linked_factory_name=linked_factory_name)


def datafactory_integration_runtimes_get_status(cmd, client,
                                                resource_group_name,
                                                factory_name,
                                                integration_runtime_name):
    return client.get_status(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


def datafactory_integration_runtimes_get_connection_info(cmd, client,
                                                         resource_group_name,
                                                         factory_name,
                                                         integration_runtime_name):
    return client.get_connection_info(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


def datafactory_integration_runtimes_list_auth_keys(cmd, client,
                                                    resource_group_name,
                                                    factory_name,
                                                    integration_runtime_name):
    return client.list_auth_keys(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


def datafactory_integration_runtimes_start(cmd, client,
                                           resource_group_name,
                                           factory_name,
                                           integration_runtime_name):
    return client.start(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


def datafactory_integration_runtimes_stop(cmd, client,
                                          resource_group_name,
                                          factory_name,
                                          integration_runtime_name):
    return client.stop(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


def datafactory_integration_runtimes_sync_credentials(cmd, client,
                                                      resource_group_name,
                                                      factory_name,
                                                      integration_runtime_name):
    return client.sync_credentials(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


def datafactory_integration_runtimes_get_monitoring_data(cmd, client,
                                                         resource_group_name,
                                                         factory_name,
                                                         integration_runtime_name):
    return client.get_monitoring_data(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


def datafactory_integration_runtimes_upgrade(cmd, client,
                                             resource_group_name,
                                             factory_name,
                                             integration_runtime_name):
    return client.upgrade(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


def datafactory_integration_runtime_object_metadata_get(cmd, client,
                                                        resource_group_name,
                                                        factory_name,
                                                        integration_runtime_name,
                                                        metadata_path=None):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, metadata_path=metadata_path)


def datafactory_integration_runtime_object_metadata_refresh(cmd, client,
                                                            resource_group_name,
                                                            factory_name,
                                                            integration_runtime_name):
    return client.refresh(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


def datafactory_integration_runtime_nodes_show(cmd, client,
                                               resource_group_name,
                                               factory_name,
                                               integration_runtime_name,
                                               node_name):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, node_name=node_name)


def datafactory_integration_runtime_nodes_update(cmd, client,
                                                 resource_group_name,
                                                 factory_name,
                                                 integration_runtime_name,
                                                 node_name,
                                                 concurrent_jobs_limit=None):
    return client.update(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, node_name=node_name, concurrent_jobs_limit=concurrent_jobs_limit)


def datafactory_integration_runtime_nodes_delete(cmd, client,
                                                 resource_group_name,
                                                 factory_name,
                                                 integration_runtime_name,
                                                 node_name):
    return client.delete(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, node_name=node_name)


def datafactory_integration_runtime_nodes_get_ip_address(cmd, client,
                                                         resource_group_name,
                                                         factory_name,
                                                         integration_runtime_name,
                                                         node_name):
    return client.get_ip_address(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, node_name=node_name)


def datafactory_linked_services_list(cmd, client,
                                     resource_group_name,
                                     factory_name):
    return client.list_by_factory(resource_group_name=resource_group_name, factory_name=factory_name)


def datafactory_linked_services_show(cmd, client,
                                     resource_group_name,
                                     factory_name,
                                     linked_service_name):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, linked_service_name=linked_service_name)


def datafactory_linked_services_create(cmd, client,
                                       resource_group_name,
                                       factory_name,
                                       linked_service_name,
                                       properties_type,
                                       reference_name,
                                       parameters=None,
                                       properties_description=None,
                                       properties_parameters_properties=None,
                                       properties_annotations=None):
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, linked_service_name=linked_service_name, type=properties_type, reference_name=reference_name, parameters=parameters, description=properties_description, parameters_properties=properties_parameters_properties, annotations=properties_annotations)


def datafactory_linked_services_update(cmd, client,
                                       resource_group_name,
                                       factory_name,
                                       linked_service_name,
                                       properties_type,
                                       reference_name,
                                       parameters=None,
                                       properties_description=None,
                                       properties_parameters_properties=None,
                                       properties_annotations=None):
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, linked_service_name=linked_service_name, type=properties_type, reference_name=reference_name, parameters=parameters, description=properties_description, parameters_properties=properties_parameters_properties, annotations=properties_annotations)


def datafactory_linked_services_delete(cmd, client,
                                       resource_group_name,
                                       factory_name,
                                       linked_service_name):
    return client.delete(resource_group_name=resource_group_name, factory_name=factory_name, linked_service_name=linked_service_name)


def datafactory_datasets_list(cmd, client,
                              resource_group_name,
                              factory_name):
    return client.list_by_factory(resource_group_name=resource_group_name, factory_name=factory_name)


def datafactory_datasets_show(cmd, client,
                              resource_group_name,
                              factory_name,
                              dataset_name):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, dataset_name=dataset_name)


def datafactory_datasets_create(cmd, client,
                                resource_group_name,
                                factory_name,
                                dataset_name,
                                properties_type,
                                reference_name,
                                properties_description=None,
                                parameters=None,
                                properties_parameters_properties=None,
                                properties_annotations=None,
                                name=None):
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, dataset_name=dataset_name, type=properties_type, description=properties_description, reference_name=reference_name, parameters=parameters, parameters_properties=properties_parameters_properties, annotations=properties_annotations, name=name)


def datafactory_datasets_update(cmd, client,
                                resource_group_name,
                                factory_name,
                                dataset_name,
                                properties_type,
                                reference_name,
                                properties_description=None,
                                parameters=None,
                                properties_parameters_properties=None,
                                properties_annotations=None,
                                name=None):
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, dataset_name=dataset_name, type=properties_type, description=properties_description, reference_name=reference_name, parameters=parameters, parameters_properties=properties_parameters_properties, annotations=properties_annotations, name=name)


def datafactory_datasets_delete(cmd, client,
                                resource_group_name,
                                factory_name,
                                dataset_name):
    return client.delete(resource_group_name=resource_group_name, factory_name=factory_name, dataset_name=dataset_name)


def datafactory_pipelines_list(cmd, client,
                               resource_group_name,
                               factory_name):
    return client.list_by_factory(resource_group_name=resource_group_name, factory_name=factory_name)


def datafactory_pipelines_show(cmd, client,
                               resource_group_name,
                               factory_name,
                               pipeline_name):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, pipeline_name=pipeline_name)


def datafactory_pipelines_create(cmd, client,
                                 resource_group_name,
                                 factory_name,
                                 pipeline_name,
                                 description=None,
                                 activities=None,
                                 parameters=None,
                                 variables=None,
                                 concurrency=None,
                                 annotations=None,
                                 run_dimensions=None,
                                 folder_name=None):
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, pipeline_name=pipeline_name, description=description, activities=activities, parameters=parameters, variables=variables, concurrency=concurrency, annotations=annotations, run_dimensions=run_dimensions, name=folder_name)


def datafactory_pipelines_update(cmd, client,
                                 resource_group_name,
                                 factory_name,
                                 pipeline_name,
                                 description=None,
                                 activities=None,
                                 parameters=None,
                                 variables=None,
                                 concurrency=None,
                                 annotations=None,
                                 run_dimensions=None,
                                 folder_name=None):
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, pipeline_name=pipeline_name, description=description, activities=activities, parameters=parameters, variables=variables, concurrency=concurrency, annotations=annotations, run_dimensions=run_dimensions, name=folder_name)


def datafactory_pipelines_delete(cmd, client,
                                 resource_group_name,
                                 factory_name,
                                 pipeline_name):
    return client.delete(resource_group_name=resource_group_name, factory_name=factory_name, pipeline_name=pipeline_name)


def datafactory_pipelines_create_run(cmd, client,
                                     resource_group_name,
                                     factory_name,
                                     pipeline_name,
                                     reference_pipeline_run_id=None,
                                     is_recovery=None,
                                     start_activity_name=None,
                                     start_from_failure=None,
                                     parameters=None):
    return client.create_run(resource_group_name=resource_group_name, factory_name=factory_name, pipeline_name=pipeline_name, reference_pipeline_run_id=reference_pipeline_run_id, is_recovery=is_recovery, start_activity_name=start_activity_name, start_from_failure=start_from_failure, parameters=parameters)


def datafactory_pipeline_runs_show(cmd, client,
                                   resource_group_name,
                                   factory_name,
                                   run_id):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, run_id=run_id)


def datafactory_pipeline_runs_query_by_factory(cmd, client,
                                               resource_group_name,
                                               factory_name,
                                               last_updated_after,
                                               last_updated_before,
                                               continuation_token=None,
                                               filters=None,
                                               order_by=None):
    return client.query_by_factory(resource_group_name=resource_group_name, factory_name=factory_name, continuation_token=continuation_token, last_updated_after=last_updated_after, last_updated_before=last_updated_before, filters=filters, order_by=order_by)


def datafactory_pipeline_runs_cancel(cmd, client,
                                     resource_group_name,
                                     factory_name,
                                     run_id,
                                     is_recursive=None):
    return client.cancel(resource_group_name=resource_group_name, factory_name=factory_name, run_id=run_id, is_recursive=is_recursive)


def datafactory_activity_runs_query_by_pipeline_run(cmd, client,
                                                    resource_group_name,
                                                    factory_name,
                                                    run_id,
                                                    last_updated_after,
                                                    last_updated_before,
                                                    continuation_token=None,
                                                    filters=None,
                                                    order_by=None):
    return client.query_by_pipeline_run(resource_group_name=resource_group_name, factory_name=factory_name, run_id=run_id, continuation_token=continuation_token, last_updated_after=last_updated_after, last_updated_before=last_updated_before, filters=filters, order_by=order_by)


def datafactory_triggers_list(cmd, client,
                              resource_group_name,
                              factory_name):
    return client.list_by_factory(resource_group_name=resource_group_name, factory_name=factory_name)


def datafactory_triggers_show(cmd, client,
                              resource_group_name,
                              factory_name,
                              trigger_name):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name)


def datafactory_triggers_create(cmd, client,
                                resource_group_name,
                                factory_name,
                                trigger_name,
                                properties_type,
                                properties_description=None,
                                properties_annotations=None):
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name, type=properties_type, description=properties_description, annotations=properties_annotations)


def datafactory_triggers_update(cmd, client,
                                resource_group_name,
                                factory_name,
                                trigger_name,
                                properties_type,
                                properties_description=None,
                                properties_annotations=None):
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name, type=properties_type, description=properties_description, annotations=properties_annotations)


def datafactory_triggers_delete(cmd, client,
                                resource_group_name,
                                factory_name,
                                trigger_name):
    return client.delete(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name)


def datafactory_triggers_query_by_factory(cmd, client,
                                          resource_group_name,
                                          factory_name,
                                          continuation_token=None,
                                          parent_trigger_name=None):
    return client.query_by_factory(resource_group_name=resource_group_name, factory_name=factory_name, continuation_token=continuation_token, parent_trigger_name=parent_trigger_name)


def datafactory_triggers_subscribe_to_events(cmd, client,
                                             resource_group_name,
                                             factory_name,
                                             trigger_name):
    return client.subscribe_to_events(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name)


def datafactory_triggers_get_event_subscription_status(cmd, client,
                                                       resource_group_name,
                                                       factory_name,
                                                       trigger_name):
    return client.get_event_subscription_status(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name)


def datafactory_triggers_unsubscribe_from_events(cmd, client,
                                                 resource_group_name,
                                                 factory_name,
                                                 trigger_name):
    return client.unsubscribe_from_events(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name)


def datafactory_triggers_start(cmd, client,
                               resource_group_name,
                               factory_name,
                               trigger_name):
    return client.start(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name)


def datafactory_triggers_stop(cmd, client,
                              resource_group_name,
                              factory_name,
                              trigger_name):
    return client.stop(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name)


def datafactory_trigger_runs_query_by_factory(cmd, client,
                                              resource_group_name,
                                              factory_name,
                                              last_updated_after,
                                              last_updated_before,
                                              continuation_token=None,
                                              filters=None,
                                              order_by=None):
    return client.query_by_factory(resource_group_name=resource_group_name, factory_name=factory_name, continuation_token=continuation_token, last_updated_after=last_updated_after, last_updated_before=last_updated_before, filters=filters, order_by=order_by)


def datafactory_trigger_runs_rerun(cmd, client,
                                   resource_group_name,
                                   factory_name,
                                   trigger_name,
                                   run_id):
    return client.rerun(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name, run_id=run_id)


def datafactory_data_flows_list(cmd, client,
                                resource_group_name,
                                factory_name):
    return client.list_by_factory(resource_group_name=resource_group_name, factory_name=factory_name)


def datafactory_data_flows_show(cmd, client,
                                resource_group_name,
                                factory_name,
                                data_flow_name):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, data_flow_name=data_flow_name)


def datafactory_data_flows_create(cmd, client,
                                  resource_group_name,
                                  factory_name,
                                  data_flow_name,
                                  properties_type=None,
                                  properties_description=None,
                                  properties_annotations=None,
                                  name=None):
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, data_flow_name=data_flow_name, type=properties_type, description=properties_description, annotations=properties_annotations, name=name)


def datafactory_data_flows_update(cmd, client,
                                  resource_group_name,
                                  factory_name,
                                  data_flow_name,
                                  properties_type=None,
                                  properties_description=None,
                                  properties_annotations=None,
                                  name=None):
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, data_flow_name=data_flow_name, type=properties_type, description=properties_description, annotations=properties_annotations, name=name)


def datafactory_data_flows_delete(cmd, client,
                                  resource_group_name,
                                  factory_name,
                                  data_flow_name):
    return client.delete(resource_group_name=resource_group_name, factory_name=factory_name, data_flow_name=data_flow_name)


def datafactory_data_flow_debug_session_create(cmd, client,
                                               resource_group_name,
                                               factory_name,
                                               type,
                                               compute_type=None,
                                               core_count=None,
                                               time_to_live=None,
                                               integration_runtime_name=None,
                                               description=None):
    return client.create(resource_group_name=resource_group_name, factory_name=factory_name, compute_type=compute_type, core_count=core_count, time_to_live=time_to_live, name=integration_runtime_name, type=type, description=description)


def datafactory_data_flow_debug_session_delete(cmd, client,
                                               resource_group_name,
                                               factory_name,
                                               session_id=None):
    return client.delete(resource_group_name=resource_group_name, factory_name=factory_name, session_id=session_id)


def datafactory_data_flow_debug_session_add_data_flow(cmd, client,
                                                      resource_group_name,
                                                      factory_name,
                                                      reference_name,
                                                      session_id=None,
                                                      data_flow_name=None,
                                                      type=None,
                                                      description=None,
                                                      annotations=None,
                                                      name_data_flow_properties_folder=None,
                                                      datasets=None,
                                                      linked_services=None,
                                                      parameters=None,
                                                      staging_folder_path=None,
                                                      debug_settings_source_settings=None,
                                                      debug_settings_parameters_debug_settings=None):
    return client.add_data_flow(resource_group_name=resource_group_name, factory_name=factory_name, session_id=session_id, name=data_flow_name, type=type, description=description, annotations=annotations, name_data_flow_properties_folder=name_data_flow_properties_folder, datasets=datasets, linked_services=linked_services, reference_name=reference_name, parameters=parameters, folder_path=staging_folder_path, source_settings=debug_settings_source_settings, parameters_debug_settings=debug_settings_parameters_debug_settings)


def datafactory_data_flow_debug_session_execute_command(cmd, client,
                                                        resource_group_name,
                                                        factory_name,
                                                        command_payload_stream_name,
                                                        session_id=None,
                                                        command=None,
                                                        command_payload_row_limits=None,
                                                        command_payload_columns=None,
                                                        command_payload_expression=None):
    return client.execute_command(resource_group_name=resource_group_name, factory_name=factory_name, session_id=session_id, command=command, stream_name=command_payload_stream_name, row_limits=command_payload_row_limits, columns=command_payload_columns, expression=command_payload_expression)


def datafactory_data_flow_debug_session_query_by_factory(cmd, client,
                                                         resource_group_name,
                                                         factory_name):
    return client.query_by_factory(resource_group_name=resource_group_name, factory_name=factory_name)
