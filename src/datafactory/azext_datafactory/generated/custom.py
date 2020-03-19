# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines

import json


def datafactory_factory_list(cmd, client,
                             resource_group_name=None):
    if resource_group_name is not None:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list()


def datafactory_factory_show(cmd, client,
                             resource_group_name,
                             factory_name,
                             if_none_match=None):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, if_none_match=if_none_match)


def datafactory_factory_create(cmd, client,
                               resource_group_name,
                               factory_name,
                               location,
                               if_match=None,
                               tags=None,
                               identity=None,
                               properties_repo_configuration=None):
    properties_repo_configuration = json.loads(properties_repo_configuration) if isinstance(properties_repo_configuration, str) else properties_repo_configuration
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, if_match=if_match, location=location, tags=tags, identity=identity, repo_configuration=properties_repo_configuration)


def datafactory_factory_update(cmd, client,
                               resource_group_name,
                               factory_name,
                               tags=None,
                               identity=None):
    return client.update(resource_group_name=resource_group_name, factory_name=factory_name, tags=tags, identity=identity)


def datafactory_factory_delete(cmd, client,
                               resource_group_name,
                               factory_name):
    return client.delete(resource_group_name=resource_group_name, factory_name=factory_name)


def datafactory_factory_get_git_hub_access_token(cmd, client,
                                                 resource_group_name,
                                                 factory_name,
                                                 git_hub_access_code,
                                                 git_hub_access_token_base_url,
                                                 git_hub_client_id=None):
    return client.get_git_hub_access_token(resource_group_name=resource_group_name, factory_name=factory_name, git_hub_access_code=git_hub_access_code, git_hub_client_id=git_hub_client_id, git_hub_access_token_base_url=git_hub_access_token_base_url)


def datafactory_factory_get_data_plane_access(cmd, client,
                                              resource_group_name,
                                              factory_name,
                                              permissions=None,
                                              access_resource_path=None,
                                              profile_name=None,
                                              start_time=None,
                                              expire_time=None):
    return client.get_data_plane_access(resource_group_name=resource_group_name, factory_name=factory_name, permissions=permissions, access_resource_path=access_resource_path, profile_name=profile_name, start_time=start_time, expire_time=expire_time)


def datafactory_factory_configure_factory_repo(cmd, client,
                                               location_id,
                                               factory_resource_id=None,
                                               repo_configuration=None):
    repo_configuration = json.loads(repo_configuration) if isinstance(repo_configuration, str) else repo_configuration
    return client.configure_factory_repo(location_id=location_id, factory_resource_id=factory_resource_id, repo_configuration=repo_configuration)


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


def datafactory_integration_runtime_list(cmd, client,
                                         resource_group_name,
                                         factory_name):
    return client.list_by_factory(resource_group_name=resource_group_name, factory_name=factory_name)


def datafactory_integration_runtime_show(cmd, client,
                                         resource_group_name,
                                         factory_name,
                                         integration_runtime_name,
                                         if_none_match=None):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, if_none_match=if_none_match)


def datafactory_integration_runtime_create(cmd, client,
                                           resource_group_name,
                                           factory_name,
                                           integration_runtime_name,
                                           properties,
                                           if_match=None):
    properties = json.loads(properties) if isinstance(properties, str) else properties
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, if_match=if_match, properties=properties)


def datafactory_integration_runtime_update(cmd, client,
                                           resource_group_name,
                                           factory_name,
                                           integration_runtime_name,
                                           auto_update=None,
                                           update_delay_offset=None):
    return client.update(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, auto_update=auto_update, update_delay_offset=update_delay_offset)


def datafactory_integration_runtime_delete(cmd, client,
                                           resource_group_name,
                                           factory_name,
                                           integration_runtime_name):
    return client.delete(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


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


def datafactory_integration_runtime_regenerate_auth_key(cmd, client,
                                                        resource_group_name,
                                                        factory_name,
                                                        integration_runtime_name,
                                                        key_name=None):
    return client.regenerate_auth_key(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, key_name=key_name)


def datafactory_integration_runtime_create_linked_integration_runtime(cmd, client,
                                                                      resource_group_name,
                                                                      factory_name,
                                                                      integration_runtime_name,
                                                                      name=None,
                                                                      subscription_id=None,
                                                                      data_factory_name=None,
                                                                      data_factory_location=None):
    return client.create_linked_integration_runtime(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, name=name, subscription_id=subscription_id, data_factory_name=data_factory_name, data_factory_location=data_factory_location)


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


def datafactory_integration_runtime_remove_link(cmd, client,
                                                resource_group_name,
                                                factory_name,
                                                integration_runtime_name,
                                                linked_factory_name):
    return client.remove_link(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, linked_factory_name=linked_factory_name)


def datafactory_integration_runtime_list_auth_key(cmd, client,
                                                  resource_group_name,
                                                  factory_name,
                                                  integration_runtime_name):
    return client.list_auth_key(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


def datafactory_integration_runtime_object_metadata_refresh(cmd, client,
                                                            resource_group_name,
                                                            factory_name,
                                                            integration_runtime_name):
    return client.begin_refresh(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name)


def datafactory_integration_runtime_object_metadata_get(cmd, client,
                                                        resource_group_name,
                                                        factory_name,
                                                        integration_runtime_name,
                                                        metadata_path=None):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, metadata_path=metadata_path)


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
                                                concurrent_jobs_limit=None):
    return client.update(resource_group_name=resource_group_name, factory_name=factory_name, integration_runtime_name=integration_runtime_name, node_name=node_name, concurrent_jobs_limit=concurrent_jobs_limit)


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
                                    linked_service_name,
                                    if_none_match=None):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, linked_service_name=linked_service_name, if_none_match=if_none_match)


def datafactory_linked_service_create(cmd, client,
                                      resource_group_name,
                                      factory_name,
                                      linked_service_name,
                                      properties,
                                      if_match=None):
    properties = json.loads(properties) if isinstance(properties, str) else properties
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, linked_service_name=linked_service_name, if_match=if_match, properties=properties)


def datafactory_linked_service_update(cmd, client,
                                      resource_group_name,
                                      factory_name,
                                      linked_service_name,
                                      properties,
                                      if_match=None):
    properties = json.loads(properties) if isinstance(properties, str) else properties
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, linked_service_name=linked_service_name, if_match=if_match, properties=properties)


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
                             dataset_name,
                             if_none_match=None):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, dataset_name=dataset_name, if_none_match=if_none_match)


def datafactory_dataset_create(cmd, client,
                               resource_group_name,
                               factory_name,
                               dataset_name,
                               properties,
                               if_match=None):
    properties = json.loads(properties) if isinstance(properties, str) else properties
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, dataset_name=dataset_name, if_match=if_match, properties=properties)


def datafactory_dataset_update(cmd, client,
                               resource_group_name,
                               factory_name,
                               dataset_name,
                               properties,
                               if_match=None):
    properties = json.loads(properties) if isinstance(properties, str) else properties
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, dataset_name=dataset_name, if_match=if_match, properties=properties)


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
                              pipeline_name,
                              if_none_match=None):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, pipeline_name=pipeline_name, if_none_match=if_none_match)


def datafactory_pipeline_create(cmd, client,
                                resource_group_name,
                                factory_name,
                                pipeline_name,
                                if_match=None,
                                properties_description=None,
                                properties_activities=None,
                                properties_parameters=None,
                                properties_variables=None,
                                properties_concurrency=None,
                                properties_annotations=None,
                                properties_run_dimensions=None,
                                properties_folder=None):
    properties_activities = json.loads(properties_activities) if isinstance(properties_activities, str) else properties_activities
    properties_parameters = json.loads(properties_parameters) if isinstance(properties_parameters, str) else properties_parameters
    properties_variables = json.loads(properties_variables) if isinstance(properties_variables, str) else properties_variables
    properties_annotations = json.loads(properties_annotations) if isinstance(properties_annotations, str) else properties_annotations
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, pipeline_name=pipeline_name, if_match=if_match, description=properties_description, activities=properties_activities, parameters=properties_parameters, variables=properties_variables, concurrency=properties_concurrency, annotations=properties_annotations, run_dimensions=properties_run_dimensions, folder=properties_folder)


def datafactory_pipeline_update(cmd, client,
                                resource_group_name,
                                factory_name,
                                pipeline_name,
                                if_match=None,
                                properties_description=None,
                                properties_activities=None,
                                properties_parameters=None,
                                properties_variables=None,
                                properties_concurrency=None,
                                properties_annotations=None,
                                properties_run_dimensions=None,
                                properties_folder=None):
    properties_activities = json.loads(properties_activities) if isinstance(properties_activities, str) else properties_activities
    properties_parameters = json.loads(properties_parameters) if isinstance(properties_parameters, str) else properties_parameters
    properties_variables = json.loads(properties_variables) if isinstance(properties_variables, str) else properties_variables
    properties_annotations = json.loads(properties_annotations) if isinstance(properties_annotations, str) else properties_annotations
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, pipeline_name=pipeline_name, if_match=if_match, description=properties_description, activities=properties_activities, parameters=properties_parameters, variables=properties_variables, concurrency=properties_concurrency, annotations=properties_annotations, run_dimensions=properties_run_dimensions, folder=properties_folder)


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


def datafactory_pipeline_run_cancel(cmd, client,
                                    resource_group_name,
                                    factory_name,
                                    run_id,
                                    is_recursive=None):
    return client.cancel(resource_group_name=resource_group_name, factory_name=factory_name, run_id=run_id, is_recursive=is_recursive)


def datafactory_pipeline_run_query_by_factory(cmd, client,
                                              resource_group_name,
                                              factory_name,
                                              last_updated_after,
                                              last_updated_before,
                                              continuation_token=None,
                                              filters=None,
                                              order_by=None):
    return client.query_by_factory(resource_group_name=resource_group_name, factory_name=factory_name, continuation_token=continuation_token, last_updated_after=last_updated_after, last_updated_before=last_updated_before, filters=filters, order_by=order_by)


def datafactory_activity_run_query_by_pipeline_run(cmd, client,
                                                   resource_group_name,
                                                   factory_name,
                                                   run_id,
                                                   last_updated_after,
                                                   last_updated_before,
                                                   continuation_token=None,
                                                   filters=None,
                                                   order_by=None):
    return client.query_by_pipeline_run(resource_group_name=resource_group_name, factory_name=factory_name, run_id=run_id, continuation_token=continuation_token, last_updated_after=last_updated_after, last_updated_before=last_updated_before, filters=filters, order_by=order_by)


def datafactory_trigger_list(cmd, client,
                             resource_group_name,
                             factory_name):
    return client.list_by_factory(resource_group_name=resource_group_name, factory_name=factory_name)


def datafactory_trigger_show(cmd, client,
                             resource_group_name,
                             factory_name,
                             trigger_name,
                             if_none_match=None):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name, if_none_match=if_none_match)


def datafactory_trigger_create(cmd, client,
                               resource_group_name,
                               factory_name,
                               trigger_name,
                               properties,
                               if_match=None):
    properties = json.loads(properties) if isinstance(properties, str) else properties
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name, if_match=if_match, properties=properties)


def datafactory_trigger_update(cmd, client,
                               resource_group_name,
                               factory_name,
                               trigger_name,
                               properties,
                               if_match=None):
    properties = json.loads(properties) if isinstance(properties, str) else properties
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name, if_match=if_match, properties=properties)


def datafactory_trigger_delete(cmd, client,
                               resource_group_name,
                               factory_name,
                               trigger_name):
    return client.delete(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name)


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


def datafactory_trigger_query_by_factory(cmd, client,
                                         resource_group_name,
                                         factory_name,
                                         continuation_token=None,
                                         parent_trigger_name=None):
    return client.query_by_factory(resource_group_name=resource_group_name, factory_name=factory_name, continuation_token=continuation_token, parent_trigger_name=parent_trigger_name)


def datafactory_trigger_run_rerun(cmd, client,
                                  resource_group_name,
                                  factory_name,
                                  trigger_name,
                                  run_id):
    return client.rerun(resource_group_name=resource_group_name, factory_name=factory_name, trigger_name=trigger_name, run_id=run_id)


def datafactory_trigger_run_query_by_factory(cmd, client,
                                             resource_group_name,
                                             factory_name,
                                             last_updated_after,
                                             last_updated_before,
                                             continuation_token=None,
                                             filters=None,
                                             order_by=None):
    return client.query_by_factory(resource_group_name=resource_group_name, factory_name=factory_name, continuation_token=continuation_token, last_updated_after=last_updated_after, last_updated_before=last_updated_before, filters=filters, order_by=order_by)


def datafactory_data_flow_list(cmd, client,
                               resource_group_name,
                               factory_name):
    return client.list_by_factory(resource_group_name=resource_group_name, factory_name=factory_name)


def datafactory_data_flow_show(cmd, client,
                               resource_group_name,
                               factory_name,
                               data_flow_name,
                               if_none_match=None):
    return client.get(resource_group_name=resource_group_name, factory_name=factory_name, data_flow_name=data_flow_name, if_none_match=if_none_match)


def datafactory_data_flow_create(cmd, client,
                                 resource_group_name,
                                 factory_name,
                                 data_flow_name,
                                 properties,
                                 if_match=None):
    properties = json.loads(properties) if isinstance(properties, str) else properties
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, data_flow_name=data_flow_name, if_match=if_match, properties=properties)


def datafactory_data_flow_update(cmd, client,
                                 resource_group_name,
                                 factory_name,
                                 data_flow_name,
                                 properties,
                                 if_match=None):
    properties = json.loads(properties) if isinstance(properties, str) else properties
    return client.create_or_update(resource_group_name=resource_group_name, factory_name=factory_name, data_flow_name=data_flow_name, if_match=if_match, properties=properties)


def datafactory_data_flow_delete(cmd, client,
                                 resource_group_name,
                                 factory_name,
                                 data_flow_name):
    return client.delete(resource_group_name=resource_group_name, factory_name=factory_name, data_flow_name=data_flow_name)


def datafactory_data_flow_debug_session_create(cmd, client,
                                               resource_group_name,
                                               factory_name,
                                               compute_type=None,
                                               core_count=None,
                                               time_to_live=None,
                                               integration_runtime=None):
    integration_runtime = json.loads(integration_runtime) if isinstance(integration_runtime, str) else integration_runtime
    return client.begin_create(resource_group_name=resource_group_name, factory_name=factory_name, compute_type=compute_type, core_count=core_count, time_to_live=time_to_live, integration_runtime=integration_runtime)


def datafactory_data_flow_debug_session_delete(cmd, client,
                                               resource_group_name,
                                               factory_name,
                                               session_id=None):
    return client.delete(resource_group_name=resource_group_name, factory_name=factory_name, session_id=session_id)


def datafactory_data_flow_debug_session_query_by_factory(cmd, client,
                                                         resource_group_name,
                                                         factory_name):
    return client.query_by_factory(resource_group_name=resource_group_name, factory_name=factory_name)


def datafactory_data_flow_debug_session_add_data_flow(cmd, client,
                                                      resource_group_name,
                                                      factory_name,
                                                      session_id=None,
                                                      data_flow=None,
                                                      datasets=None,
                                                      linked_services=None,
                                                      staging=None,
                                                      debug_settings=None):
    data_flow = json.loads(data_flow) if isinstance(data_flow, str) else data_flow
    datasets = json.loads(datasets) if isinstance(datasets, str) else datasets
    linked_services = json.loads(linked_services) if isinstance(linked_services, str) else linked_services
    staging = json.loads(staging) if isinstance(staging, str) else staging
    debug_settings = json.loads(debug_settings) if isinstance(debug_settings, str) else debug_settings
    return client.add_data_flow(resource_group_name=resource_group_name, factory_name=factory_name, session_id=session_id, data_flow=data_flow, datasets=datasets, linked_services=linked_services, staging=staging, debug_settings=debug_settings)


def datafactory_data_flow_debug_session_execute_command(cmd, client,
                                                        resource_group_name,
                                                        factory_name,
                                                        session_id=None,
                                                        command=None,
                                                        command_payload=None):
    return client.begin_execute_command(resource_group_name=resource_group_name, factory_name=factory_name, session_id=session_id, command=command, command_payload=command_payload)
