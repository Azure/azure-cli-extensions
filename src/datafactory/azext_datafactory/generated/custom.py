# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument


def datafactory_factory_list(cmd, client,
                             resource_group_name=None):
    if resource_group_name is not None:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list()


def datafactory_factory_show(cmd, client,
                             resource_group_name,
                             factory_name):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name)


def datafactory_factory_create(cmd, client,
                               resource_group_name,
                               factory_name,
                               location,
                               tags=None,
                               factory_identity=None,
                               factory_repo_configuration=None):
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, location=location, tags=tags, identity=factory_identity, repo_configuration=factory_repo_configuration)


def datafactory_factory_update(cmd, client,
                               resource_group_name,
                               factory_name,
                               tags=None,
                               factory_update_parameters_identity=None):
    return client.update(resource_group_name=resource_group_name, factory_name=factory_name, tags=tags, identity=factory_update_parameters_identity)


def datafactory_factory_delete(cmd, client,
                               resource_group_name,
                               factory_name):
    return client.delete(resource_group_name=resource_group_name, factory_name=factory_name)


def datafactory_factory_get_data_plane_access(cmd, client,
                                              resource_group_name,
                                              factory_name,
                                              policy_permissions=None,
                                              policy_access_resource_path=None,
                                              policy_profile_name=None,
                                              policy_start_time=None,
                                              policy_expire_time=None):
    return client.get_data_plane_access(resource_group_name=resource_group_name, factory_name=factory_name, permissions=policy_permissions, access_resource_path=policy_access_resource_path, profile_name=policy_profile_name, start_time=policy_start_time, expire_time=policy_expire_time)


def datafactory_factory_get_git_hub_access_token(cmd, client,
                                                 resource_group_name,
                                                 factory_name,
                                                 git_hub_access_token_request_git_hub_access_code,
                                                 git_hub_access_token_request_git_hub_access_token_base_url,
                                                 git_hub_access_token_request_git_hub_client_id=None):
    return client.get_git_hub_access_token(resource_group_name=resource_group_name, factory_name=factory_name, git_hub_access_code=git_hub_access_token_request_git_hub_access_code, git_hub_client_id=git_hub_access_token_request_git_hub_client_id, git_hub_access_token_base_url=git_hub_access_token_request_git_hub_access_token_base_url)


def datafactory_factory_configure_factory_repo(cmd, client,
                                               location_id,
                                               factory_repo_update_factory_resource_id=None,
                                               factory_repo_update_repo_configuration=None):
    return client.configure_factory_repo(location_id=location_id, factory_resource_id=factory_repo_update_factory_resource_id, repo_configuration=factory_repo_update_repo_configuration)


def datafactory_exposure_control_get_feature_value_by_factory(cmd, client,
                                                              resource_group_name,
                                                              factory_name,
                                                              exposure_control_request_feature_name=None,
                                                              exposure_control_request_feature_type=None):
    return client.get_feature_value_by_factory(resource_group_name=resource_group_name, factory_name=factory_name, feature_name=exposure_control_request_feature_name, feature_type=exposure_control_request_feature_type)


def datafactory_exposure_control_get_feature_value(cmd, client,
                                                   location_id,
                                                   exposure_control_request_feature_name=None,
                                                   exposure_control_request_feature_type=None):
    return client.get_feature_value(location_id=location_id, feature_name=exposure_control_request_feature_name, feature_type=exposure_control_request_feature_type)


def datafactory_integration_runtime_list(cmd, client,
                                         resource_group_name,
                                         factory_name):
    return client.list_by_factory(resource_group_name=resource_group_name, factory_name=factory_name)


def datafactory_integration_runtime_show(cmd, client,
                                         resource_group_name,
                                         factory_name,
                                         integration_runtime_name):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


def datafactory_integration_runtime_create(cmd, client,
                                           resource_group_name,
                                           factory_name,
                                           integration_runtime_name,
                                           integration_runtime_properties):
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, properties=integration_runtime_properties)


def datafactory_integration_runtime_update(cmd, client,
                                           resource_group_name,
                                           factory_name,
                                           integration_runtime_name,
                                           update_integration_runtime_request_auto_update=None,
                                           update_integration_runtime_request_update_delay_offset=None):
    return client.update(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, auto_update=update_integration_runtime_request_auto_update, update_delay_offset=update_integration_runtime_request_update_delay_offset)


def datafactory_integration_runtime_delete(cmd, client,
                                           resource_group_name,
                                           factory_name,
                                           integration_runtime_name):
    return client.delete(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


def datafactory_integration_runtime_create_linked_integration_runtime(cmd, client,
                                                                      resource_group_name,
                                                                      factory_name,
                                                                      integration_runtime_name,
                                                                      create_linked_integration_runtime_request_name=None,
                                                                      create_linked_integration_runtime_request_data_factory_name=None,
                                                                      create_linked_integration_runtime_request_data_factory_location=None):
    return client.create_linked_integration_runtime(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, name=create_linked_integration_runtime_request_name, data_factory_name=create_linked_integration_runtime_request_data_factory_name, data_factory_location=create_linked_integration_runtime_request_data_factory_location)


def datafactory_integration_runtime_regenerate_auth_key(cmd, client,
                                                        resource_group_name,
                                                        factory_name,
                                                        integration_runtime_name,
                                                        regenerate_key_parameters_key_name=None):
    return client.regenerate_auth_key(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, key_name=regenerate_key_parameters_key_name)


def datafactory_integration_runtime_remove_link(cmd, client,
                                                resource_group_name,
                                                factory_name,
                                                integration_runtime_name,
                                                linked_integration_runtime_request_linked_factory_name):
    return client.remove_link(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, linked_factory_name=linked_integration_runtime_request_linked_factory_name)


def datafactory_integration_runtime_get_status(cmd, client,
                                               resource_group_name,
                                               factory_name,
                                               integration_runtime_name):
    return client.get_status(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


def datafactory_integration_runtime_get_connection_info(cmd, client,
                                                        resource_group_name,
                                                        factory_name,
                                                        integration_runtime_name):
    return client.get_connection_info(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


def datafactory_integration_runtime_list_auth_key(cmd, client,
                                                  resource_group_name,
                                                  factory_name,
                                                  integration_runtime_name):
    return client.list_auth_key(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


def datafactory_integration_runtime_start(cmd, client,
                                          resource_group_name,
                                          factory_name,
                                          integration_runtime_name):
    return client.begin_start(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


def datafactory_integration_runtime_stop(cmd, client,
                                         resource_group_name,
                                         factory_name,
                                         integration_runtime_name):
    return client.begin_stop(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


def datafactory_integration_runtime_sync_credentials(cmd, client,
                                                     resource_group_name,
                                                     factory_name,
                                                     integration_runtime_name):
    return client.sync_credentials(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


def datafactory_integration_runtime_get_monitoring_data(cmd, client,
                                                        resource_group_name,
                                                        factory_name,
                                                        integration_runtime_name):
    return client.get_monitoring_data(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


def datafactory_integration_runtime_upgrade(cmd, client,
                                            resource_group_name,
                                            factory_name,
                                            integration_runtime_name):
    return client.upgrade(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


def datafactory_integration_runtime_object_metadata_get(cmd, client,
                                                        resource_group_name,
                                                        factory_name,
                                                        integration_runtime_name,
                                                        get_metadata_request_metadata_path=None):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, metadata_path=get_metadata_request_metadata_path)


def datafactory_integration_runtime_object_metadata_refresh(cmd, client,
                                                            resource_group_name,
                                                            factory_name,
                                                            integration_runtime_name):
    return client.begin_refresh(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


def datafactory_integration_runtime_node_show(cmd, client,
                                              resource_group_name,
                                              factory_name,
                                              integration_runtime_name,
                                              node_name):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, node_name=node_name)


def datafactory_integration_runtime_node_update(cmd, client,
                                                resource_group_name,
                                                factory_name,
                                                integration_runtime_name,
                                                node_name,
                                                update_integration_runtime_node_request_concurrent_jobs_limit=None):
    return client.update(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, node_name=node_name, concurrent_jobs_limit=update_integration_runtime_node_request_concurrent_jobs_limit)


def datafactory_integration_runtime_node_delete(cmd, client,
                                                resource_group_name,
                                                factory_name,
                                                integration_runtime_name,
                                                node_name):
    return client.delete(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, node_name=node_name)


def datafactory_integration_runtime_node_get_ip_address(cmd, client,
                                                        resource_group_name,
                                                        factory_name,
                                                        integration_runtime_name,
                                                        node_name):
    return client.get_ip_address(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, node_name=node_name)


def datafactory_linked_service_list(cmd, client,
                                    resource_group_name,
                                    factory_name):
    return client.list_by_factory(resource_group_name=resource_group_name, factory_name=factory_name)


def datafactory_linked_service_show(cmd, client,
                                    resource_group_name,
                                    factory_name,
                                    linked_service_name):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, linked_service_name=linked_service_name)


def datafactory_linked_service_create(cmd, client,
                                      resource_group_name,
                                      factory_name,
                                      linked_service_name,
                                      linked_service_properties):
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, linked_service_name=linked_service_name, properties=linked_service_properties)


def datafactory_linked_service_update(cmd, client,
                                      resource_group_name,
                                      factory_name,
                                      linked_service_name,
                                      linked_service_properties):
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, linked_service_name=linked_service_name, properties=linked_service_properties)


def datafactory_linked_service_delete(cmd, client,
                                      resource_group_name,
                                      factory_name,
                                      linked_service_name):
    return client.delete(resource_group_name=resource_group_name, factory_name=factory_name, linked_service_name=linked_service_name)


def datafactory_dataset_list(cmd, client,
                             resource_group_name,
                             factory_name):
    return client.list_by_factory(resource_group_name=resource_group_name, factory_name=factory_name)


def datafactory_dataset_show(cmd, client,
                             resource_group_name,
                             factory_name,
                             dataset_name):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, dataset_name=dataset_name)


def datafactory_dataset_create(cmd, client,
                               resource_group_name,
                               factory_name,
                               dataset_name,
                               dataset_properties):
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, dataset_name=dataset_name, properties=dataset_properties)


def datafactory_dataset_update(cmd, client,
                               resource_group_name,
                               factory_name,
                               dataset_name,
                               dataset_properties):
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, dataset_name=dataset_name, properties=dataset_properties)


def datafactory_dataset_delete(cmd, client,
                               resource_group_name,
                               factory_name,
                               dataset_name):
    return client.delete(resource_group_name=resource_group_name, factory_name=factory_name, dataset_name=dataset_name)


def datafactory_pipeline_list(cmd, client,
                              resource_group_name,
                              factory_name):
    return client.list_by_factory(resource_group_name=resource_group_name, factory_name=factory_name)


def datafactory_pipeline_show(cmd, client,
                              resource_group_name,
                              factory_name,
                              pipeline_name):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, pipeline_name=pipeline_name)


def datafactory_pipeline_create(cmd, client,
                                resource_group_name,
                                factory_name,
                                pipeline_name,
                                pipeline_description=None,
                                pipeline_activities=None,
                                pipeline_parameters=None,
                                pipeline_variables=None,
                                pipeline_concurrency=None,
                                pipeline_annotations=None,
                                pipeline_run_dimensions=None,
                                pipeline_folder=None):
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, pipeline_name=pipeline_name, description=pipeline_description, activities=pipeline_activities, parameters=pipeline_parameters, variables=pipeline_variables, concurrency=pipeline_concurrency, annotations=pipeline_annotations, run_dimensions=pipeline_run_dimensions, folder=pipeline_folder)


def datafactory_pipeline_update(cmd, client,
                                resource_group_name,
                                factory_name,
                                pipeline_name,
                                pipeline_description=None,
                                pipeline_activities=None,
                                pipeline_parameters=None,
                                pipeline_variables=None,
                                pipeline_concurrency=None,
                                pipeline_annotations=None,
                                pipeline_run_dimensions=None,
                                pipeline_folder=None):
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, pipeline_name=pipeline_name, description=pipeline_description, activities=pipeline_activities, parameters=pipeline_parameters, variables=pipeline_variables, concurrency=pipeline_concurrency, annotations=pipeline_annotations, run_dimensions=pipeline_run_dimensions, folder=pipeline_folder)


def datafactory_pipeline_delete(cmd, client,
                                resource_group_name,
                                factory_name,
                                pipeline_name):
    return client.delete(resource_group_name=resource_group_name, factory_name=factory_name, pipeline_name=pipeline_name)


def datafactory_pipeline_create_run(cmd, client,
                                    resource_group_name,
                                    factory_name,
                                    pipeline_name,
                                    reference_pipeline_run_id=None,
                                    is_recovery=None,
                                    start_activity_name=None,
                                    start_from_failure=None,
                                    parameters=None):
    return client.create_run(resource_group_name=resource_group_name, factory_name=factory_name, pipeline_name=pipeline_name, reference_pipeline_run_id=reference_pipeline_run_id, is_recovery=is_recovery, start_activity_name=start_activity_name, start_from_failure=start_from_failure, parameters=parameters)


def datafactory_pipeline_run_show(cmd, client,
                                  resource_group_name,
                                  factory_name,
                                  run_id):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, run_id=run_id)


def datafactory_pipeline_run_query_by_factory(cmd, client,
                                              resource_group_name,
                                              factory_name,
                                              filter_parameters_last_updated_after,
                                              filter_parameters_last_updated_before,
                                              filter_parameters_continuation_token=None,
                                              filter_parameters_filters=None,
                                              filter_parameters_order_by=None):
    return client.query_by_factory(resource_group_name=resource_group_name, factory_name=factory_name, continuation_token=filter_parameters_continuation_token, last_updated_after=filter_parameters_last_updated_after, last_updated_before=filter_parameters_last_updated_before, filters=filter_parameters_filters, order_by=filter_parameters_order_by)


def datafactory_pipeline_run_cancel(cmd, client,
                                    resource_group_name,
                                    factory_name,
                                    run_id,
                                    is_recursive=None):
    return client.cancel(resource_group_name=resource_group_name, factory_name=factory_name, run_id=run_id, is_recursive=is_recursive)


def datafactory_activity_run_query_by_pipeline_run(cmd, client,
                                                   resource_group_name,
                                                   factory_name,
                                                   run_id,
                                                   filter_parameters_last_updated_after,
                                                   filter_parameters_last_updated_before,
                                                   filter_parameters_continuation_token=None,
                                                   filter_parameters_filters=None,
                                                   filter_parameters_order_by=None):
    return client.query_by_pipeline_run(resource_group_name=resource_group_name, factory_name=factory_name, run_id=run_id, continuation_token=filter_parameters_continuation_token, last_updated_after=filter_parameters_last_updated_after, last_updated_before=filter_parameters_last_updated_before, filters=filter_parameters_filters, order_by=filter_parameters_order_by)


def datafactory_trigger_list(cmd, client,
                             resource_group_name,
                             factory_name):
    return client.list_by_factory(resource_group_name=resource_group_name, factory_name=factory_name)


def datafactory_trigger_show(cmd, client,
                             resource_group_name,
                             factory_name,
                             trigger_name):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name)


def datafactory_trigger_create(cmd, client,
                               resource_group_name,
                               factory_name,
                               trigger_name,
                               trigger_properties):
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name, properties=trigger_properties)


def datafactory_trigger_update(cmd, client,
                               resource_group_name,
                               factory_name,
                               trigger_name,
                               trigger_properties):
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name, properties=trigger_properties)


def datafactory_trigger_delete(cmd, client,
                               resource_group_name,
                               factory_name,
                               trigger_name):
    return client.delete(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name)


def datafactory_trigger_query_by_factory(cmd, client,
                                         resource_group_name,
                                         factory_name,
                                         filter_parameters_continuation_token=None,
                                         filter_parameters_parent_trigger_name=None):
    return client.query_by_factory(resource_group_name=resource_group_name, factory_name=factory_name, continuation_token=filter_parameters_continuation_token, parent_trigger_name=filter_parameters_parent_trigger_name)


def datafactory_trigger_subscribe_to_event(cmd, client,
                                           resource_group_name,
                                           factory_name,
                                           trigger_name):
    return client.begin_subscribe_to_event(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name)


def datafactory_trigger_get_event_subscription_status(cmd, client,
                                                      resource_group_name,
                                                      factory_name,
                                                      trigger_name):
    return client.get_event_subscription_status(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name)


def datafactory_trigger_unsubscribe_from_event(cmd, client,
                                               resource_group_name,
                                               factory_name,
                                               trigger_name):
    return client.begin_unsubscribe_from_event(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name)


def datafactory_trigger_start(cmd, client,
                              resource_group_name,
                              factory_name,
                              trigger_name):
    return client.begin_start(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name)


def datafactory_trigger_stop(cmd, client,
                             resource_group_name,
                             factory_name,
                             trigger_name):
    return client.begin_stop(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name)


def datafactory_trigger_run_query_by_factory(cmd, client,
                                             resource_group_name,
                                             factory_name,
                                             filter_parameters_last_updated_after,
                                             filter_parameters_last_updated_before,
                                             filter_parameters_continuation_token=None,
                                             filter_parameters_filters=None,
                                             filter_parameters_order_by=None):
    return client.query_by_factory(resource_group_name=resource_group_name, factory_name=factory_name, continuation_token=filter_parameters_continuation_token, last_updated_after=filter_parameters_last_updated_after, last_updated_before=filter_parameters_last_updated_before, filters=filter_parameters_filters, order_by=filter_parameters_order_by)


def datafactory_trigger_run_rerun(cmd, client,
                                  resource_group_name,
                                  factory_name,
                                  trigger_name,
                                  run_id):
    return client.rerun(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name, run_id=run_id)


def datafactory_data_flow_list(cmd, client,
                               resource_group_name,
                               factory_name):
    return client.list_by_factory(resource_group_name=resource_group_name, factory_name=factory_name)


def datafactory_data_flow_show(cmd, client,
                               resource_group_name,
                               factory_name,
                               data_flow_name):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, data_flow_name=data_flow_name)


def datafactory_data_flow_create(cmd, client,
                                 resource_group_name,
                                 factory_name,
                                 data_flow_name,
                                 data_flow_properties):
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, data_flow_name=data_flow_name, properties=data_flow_properties)


def datafactory_data_flow_update(cmd, client,
                                 resource_group_name,
                                 factory_name,
                                 data_flow_name,
                                 data_flow_properties):
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, data_flow_name=data_flow_name, properties=data_flow_properties)


def datafactory_data_flow_delete(cmd, client,
                                 resource_group_name,
                                 factory_name,
                                 data_flow_name):
    return client.delete(resource_group_name=resource_group_name, factory_name=factory_name, data_flow_name=data_flow_name)


def datafactory_data_flow_debug_session_create(cmd, client,
                                               resource_group_name,
                                               factory_name,
                                               request_compute_type=None,
                                               request_core_count=None,
                                               request_time_to_live=None,
                                               request_integration_runtime=None):
    return client.begin_create(resource_group_name=resource_group_name, factory_name=factory_name, compute_type=request_compute_type, core_count=request_core_count, time_to_live=request_time_to_live, integration_runtime=request_integration_runtime)


def datafactory_data_flow_debug_session_delete(cmd, client,
                                               resource_group_name,
                                               factory_name,
                                               request_session_id=None):
    return client.delete(resource_group_name=resource_group_name, factory_name=factory_name, session_id=request_session_id)


def datafactory_data_flow_debug_session_add_data_flow(cmd, client,
                                                      resource_group_name,
                                                      factory_name,
                                                      request_session_id=None,
                                                      request_data_flow=None,
                                                      request_datasets=None,
                                                      request_linked_services=None,
                                                      request_staging=None,
                                                      request_debug_settings=None):
    return client.add_data_flow(resource_group_name=resource_group_name, factory_name=factory_name, session_id=request_session_id, data_flow=request_data_flow, datasets=request_datasets, linked_services=request_linked_services, staging=request_staging, debug_settings=request_debug_settings)


def datafactory_data_flow_debug_session_execute_command(cmd, client,
                                                        resource_group_name,
                                                        factory_name,
                                                        request_session_id=None,
                                                        request_command=None,
                                                        request_command_payload=None):
    return client.begin_execute_command(resource_group_name=resource_group_name, factory_name=factory_name, session_id=request_session_id, command=request_command, command_payload=request_command_payload)


def datafactory_data_flow_debug_session_query_by_factory(cmd, client,
                                                         resource_group_name,
                                                         factory_name):
    return client.query_by_factory(resource_group_name=resource_group_name, factory_name=factory_name)
