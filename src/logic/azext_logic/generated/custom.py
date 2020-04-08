# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-many-lines

import json


def logic_workflow_list(cmd, client,
                        resource_group_name=None,
                        top=None,
                        filter=None):
    if resource_group_name is not None:
        return client.list_by_resource_group(resource_group_name=resource_group_name,
                                             top=top,
                                             filter=filter)
    return client.list_by_subscription(top=top,
                                       filter=filter)


def logic_workflow_show(cmd, client,
                        resource_group_name,
                        workflow_name):
    return client.get(resource_group_name=resource_group_name,
                      workflow_name=workflow_name)


def logic_workflow_create(cmd, client,
                          resource_group_name,
                          workflow_name,
                          location=None,
                          tags=None,
                          state=None,
                          endpoints_configuration=None,
                          sku=None,
                          integration_account=None,
                          integration_service_environment=None,
                          definition=None,
                          parameters=None):
    if isinstance(endpoints_configuration, str):
        endpoints_configuration = json.loads(endpoints_configuration)
    if isinstance(sku, str):
        sku = json.loads(sku)
    if isinstance(definition, str):
        definition = json.loads(definition)
    if isinstance(parameters, str):
        parameters = json.loads(parameters)
    return client.create_or_update(resource_group_name=resource_group_name,
                                   workflow_name=workflow_name,
                                   location=location,
                                   tags=tags,
                                   state=state,
                                   endpoints_configuration=endpoints_configuration,
                                   sku=sku,
                                   integration_account=integration_account,
                                   integration_service_environment=integration_service_environment,
                                   definition=definition,
                                   parameters=parameters)


def logic_workflow_update(cmd, client,
                          resource_group_name,
                          workflow_name,
                          location=None,
                          tags=None,
                          state=None,
                          endpoints_configuration=None,
                          sku=None,
                          integration_account=None,
                          integration_service_environment=None,
                          definition=None,
                          parameters=None):
    if isinstance(endpoints_configuration, str):
        endpoints_configuration = json.loads(endpoints_configuration)
    if isinstance(sku, str):
        sku = json.loads(sku)
    if isinstance(definition, str):
        definition = json.loads(definition)
    if isinstance(parameters, str):
        parameters = json.loads(parameters)
    return client.update(resource_group_name=resource_group_name,
                         workflow_name=workflow_name,
                         location=location,
                         tags=tags,
                         state=state,
                         endpoints_configuration=endpoints_configuration,
                         sku=sku,
                         integration_account=integration_account,
                         integration_service_environment=integration_service_environment,
                         definition=definition,
                         parameters=parameters)


def logic_workflow_delete(cmd, client,
                          resource_group_name,
                          workflow_name):
    return client.delete(resource_group_name=resource_group_name,
                         workflow_name=workflow_name)


def logic_workflow_disable(cmd, client,
                           resource_group_name,
                           workflow_name):
    return client.disable(resource_group_name=resource_group_name,
                          workflow_name=workflow_name)


def logic_workflow_enable(cmd, client,
                          resource_group_name,
                          workflow_name):
    return client.enable(resource_group_name=resource_group_name,
                         workflow_name=workflow_name)


def logic_workflow_generate_upgraded_definition(cmd, client,
                                                resource_group_name,
                                                workflow_name,
                                                target_schema_version=None):
    return client.generate_upgraded_definition(resource_group_name=resource_group_name,
                                               workflow_name=workflow_name,
                                               target_schema_version=target_schema_version)


def logic_workflow_list_callback_url(cmd, client,
                                     resource_group_name,
                                     workflow_name,
                                     not_after=None,
                                     key_type=None):
    return client.list_callback_url(resource_group_name=resource_group_name,
                                    workflow_name=workflow_name,
                                    not_after=not_after,
                                    key_type=key_type)


def logic_workflow_list_swagger(cmd, client,
                                resource_group_name,
                                workflow_name):
    return client.list_swagger(resource_group_name=resource_group_name,
                               workflow_name=workflow_name)


def logic_workflow_move(cmd, client,
                        resource_group_name,
                        workflow_name,
                        location=None,
                        tags=None,
                        state=None,
                        endpoints_configuration=None,
                        sku=None,
                        integration_account=None,
                        integration_service_environment=None,
                        definition=None,
                        parameters=None):
    if isinstance(endpoints_configuration, str):
        endpoints_configuration = json.loads(endpoints_configuration)
    if isinstance(sku, str):
        sku = json.loads(sku)
    if isinstance(definition, str):
        definition = json.loads(definition)
    if isinstance(parameters, str):
        parameters = json.loads(parameters)
    return client.begin_move(resource_group_name=resource_group_name,
                             workflow_name=workflow_name,
                             location=location,
                             tags=tags,
                             state=state,
                             endpoints_configuration=endpoints_configuration,
                             sku=sku,
                             integration_account=integration_account,
                             integration_service_environment=integration_service_environment,
                             definition=definition,
                             parameters=parameters)


def logic_workflow_regenerate_access_key(cmd, client,
                                         resource_group_name,
                                         workflow_name,
                                         key_type=None):
    return client.regenerate_access_key(resource_group_name=resource_group_name,
                                        workflow_name=workflow_name,
                                        key_type=key_type)


def logic_workflow_validate_by_location(cmd, client,
                                        resource_group_name,
                                        location,
                                        workflow_name):
    return client.validate_by_location(resource_group_name=resource_group_name,
                                       location=location,
                                       workflow_name=workflow_name)


def logic_workflow_validate_by_resource_group(cmd, client,
                                              resource_group_name,
                                              workflow_name,
                                              location=None,
                                              tags=None,
                                              state=None,
                                              endpoints_configuration=None,
                                              sku=None,
                                              integration_account=None,
                                              integration_service_environment=None,
                                              definition=None,
                                              parameters=None):
    if isinstance(endpoints_configuration, str):
        endpoints_configuration = json.loads(endpoints_configuration)
    if isinstance(sku, str):
        sku = json.loads(sku)
    if isinstance(definition, str):
        definition = json.loads(definition)
    if isinstance(parameters, str):
        parameters = json.loads(parameters)
    return client.validate_by_resource_group(resource_group_name=resource_group_name,
                                             workflow_name=workflow_name,
                                             location=location,
                                             tags=tags,
                                             state=state,
                                             endpoints_configuration=endpoints_configuration,
                                             sku=sku,
                                             integration_account=integration_account,
                                             integration_service_environment=integration_service_environment,
                                             definition=definition,
                                             parameters=parameters)


def logic_workflow_version_list(cmd, client,
                                resource_group_name,
                                workflow_name,
                                top=None):
    return client.list(resource_group_name=resource_group_name,
                       workflow_name=workflow_name,
                       top=top)


def logic_workflow_version_show(cmd, client,
                                resource_group_name,
                                workflow_name,
                                version_id):
    return client.get(resource_group_name=resource_group_name,
                      workflow_name=workflow_name,
                      version_id=version_id)


def logic_workflow_trigger_list(cmd, client,
                                resource_group_name,
                                workflow_name,
                                top=None,
                                filter=None):
    return client.list(resource_group_name=resource_group_name,
                       workflow_name=workflow_name,
                       top=top,
                       filter=filter)


def logic_workflow_trigger_show(cmd, client,
                                resource_group_name,
                                workflow_name,
                                trigger_name):
    if resource_group_name is not None and workflow_name is not None and trigger_name is not None:
        return client.get(resource_group_name=resource_group_name,
                          workflow_name=workflow_name,
                          trigger_name=trigger_name)
    return client.get_schema_json(resource_group_name=resource_group_name,
                                  workflow_name=workflow_name,
                                  trigger_name=trigger_name)


def logic_workflow_trigger_list_callback_url(cmd, client,
                                             resource_group_name,
                                             workflow_name,
                                             trigger_name):
    return client.list_callback_url(resource_group_name=resource_group_name,
                                    workflow_name=workflow_name,
                                    trigger_name=trigger_name)


def logic_workflow_trigger_reset(cmd, client,
                                 resource_group_name,
                                 workflow_name,
                                 trigger_name):
    return client.reset(resource_group_name=resource_group_name,
                        workflow_name=workflow_name,
                        trigger_name=trigger_name)


def logic_workflow_trigger_run(cmd, client,
                               resource_group_name,
                               workflow_name,
                               trigger_name):
    return client.run(resource_group_name=resource_group_name,
                      workflow_name=workflow_name,
                      trigger_name=trigger_name)


def logic_workflow_trigger_set_state(cmd, client,
                                     resource_group_name,
                                     workflow_name,
                                     trigger_name,
                                     source):
    if isinstance(source, str):
        source = json.loads(source)
    return client.set_state(resource_group_name=resource_group_name,
                            workflow_name=workflow_name,
                            trigger_name=trigger_name,
                            source=source)


def logic_workflow_version_trigger_list_callback_url(cmd, client,
                                                     resource_group_name,
                                                     workflow_name,
                                                     version_id,
                                                     trigger_name,
                                                     not_after=None,
                                                     key_type=None):
    return client.list_callback_url(resource_group_name=resource_group_name,
                                    workflow_name=workflow_name,
                                    version_id=version_id,
                                    trigger_name=trigger_name,
                                    not_after=not_after,
                                    key_type=key_type)


def logic_workflow_trigger_history_list(cmd, client,
                                        resource_group_name,
                                        workflow_name,
                                        trigger_name,
                                        top=None,
                                        filter=None):
    return client.list(resource_group_name=resource_group_name,
                       workflow_name=workflow_name,
                       trigger_name=trigger_name,
                       top=top,
                       filter=filter)


def logic_workflow_trigger_history_show(cmd, client,
                                        resource_group_name,
                                        workflow_name,
                                        trigger_name,
                                        history_name):
    return client.get(resource_group_name=resource_group_name,
                      workflow_name=workflow_name,
                      trigger_name=trigger_name,
                      history_name=history_name)


def logic_workflow_trigger_history_resubmit(cmd, client,
                                            resource_group_name,
                                            workflow_name,
                                            trigger_name,
                                            history_name):
    return client.resubmit(resource_group_name=resource_group_name,
                           workflow_name=workflow_name,
                           trigger_name=trigger_name,
                           history_name=history_name)


def logic_workflow_run_list(cmd, client,
                            resource_group_name,
                            workflow_name,
                            top=None,
                            filter=None):
    return client.list(resource_group_name=resource_group_name,
                       workflow_name=workflow_name,
                       top=top,
                       filter=filter)


def logic_workflow_run_show(cmd, client,
                            resource_group_name,
                            workflow_name,
                            run_name):
    return client.get(resource_group_name=resource_group_name,
                      workflow_name=workflow_name,
                      run_name=run_name)


def logic_workflow_run_cancel(cmd, client,
                              resource_group_name,
                              workflow_name,
                              run_name):
    return client.cancel(resource_group_name=resource_group_name,
                         workflow_name=workflow_name,
                         run_name=run_name)


def logic_workflow_run_action_list(cmd, client,
                                   resource_group_name,
                                   workflow_name,
                                   run_name,
                                   top=None,
                                   filter=None):
    return client.list(resource_group_name=resource_group_name,
                       workflow_name=workflow_name,
                       run_name=run_name,
                       top=top,
                       filter=filter)


def logic_workflow_run_action_show(cmd, client,
                                   resource_group_name,
                                   workflow_name,
                                   run_name,
                                   action_name):
    return client.get(resource_group_name=resource_group_name,
                      workflow_name=workflow_name,
                      run_name=run_name,
                      action_name=action_name)


def logic_workflow_run_action_list_expression_trace(cmd, client,
                                                    resource_group_name,
                                                    workflow_name,
                                                    run_name,
                                                    action_name):
    return client.list_expression_trace(resource_group_name=resource_group_name,
                                        workflow_name=workflow_name,
                                        run_name=run_name,
                                        action_name=action_name)


def logic_workflow_run_action_repetition_list(cmd, client,
                                              resource_group_name,
                                              workflow_name,
                                              run_name,
                                              action_name):
    return client.list(resource_group_name=resource_group_name,
                       workflow_name=workflow_name,
                       run_name=run_name,
                       action_name=action_name)


def logic_workflow_run_action_repetition_show(cmd, client,
                                              resource_group_name,
                                              workflow_name,
                                              run_name,
                                              action_name,
                                              repetition_name):
    return client.get(resource_group_name=resource_group_name,
                      workflow_name=workflow_name,
                      run_name=run_name,
                      action_name=action_name,
                      repetition_name=repetition_name)


def logic_workflow_run_action_repetition_list_expression_trace(cmd, client,
                                                               resource_group_name,
                                                               workflow_name,
                                                               run_name,
                                                               action_name,
                                                               repetition_name):
    return client.list_expression_trace(resource_group_name=resource_group_name,
                                        workflow_name=workflow_name,
                                        run_name=run_name,
                                        action_name=action_name,
                                        repetition_name=repetition_name)


def logic_workflow_run_action_repetition_request_history_list(cmd, client,
                                                              resource_group_name,
                                                              workflow_name,
                                                              run_name,
                                                              action_name,
                                                              repetition_name):
    return client.list(resource_group_name=resource_group_name,
                       workflow_name=workflow_name,
                       run_name=run_name,
                       action_name=action_name,
                       repetition_name=repetition_name)


def logic_workflow_run_action_repetition_request_history_show(cmd, client,
                                                              resource_group_name,
                                                              workflow_name,
                                                              run_name,
                                                              action_name,
                                                              repetition_name,
                                                              request_history_name):
    return client.get(resource_group_name=resource_group_name,
                      workflow_name=workflow_name,
                      run_name=run_name,
                      action_name=action_name,
                      repetition_name=repetition_name,
                      request_history_name=request_history_name)


def logic_workflow_run_action_request_history_list(cmd, client,
                                                   resource_group_name,
                                                   workflow_name,
                                                   run_name,
                                                   action_name):
    return client.list(resource_group_name=resource_group_name,
                       workflow_name=workflow_name,
                       run_name=run_name,
                       action_name=action_name)


def logic_workflow_run_action_request_history_show(cmd, client,
                                                   resource_group_name,
                                                   workflow_name,
                                                   run_name,
                                                   action_name,
                                                   request_history_name):
    return client.get(resource_group_name=resource_group_name,
                      workflow_name=workflow_name,
                      run_name=run_name,
                      action_name=action_name,
                      request_history_name=request_history_name)


def logic_workflow_run_action_scope_repetition_list(cmd, client,
                                                    resource_group_name,
                                                    workflow_name,
                                                    run_name,
                                                    action_name):
    return client.list(resource_group_name=resource_group_name,
                       workflow_name=workflow_name,
                       run_name=run_name,
                       action_name=action_name)


def logic_workflow_run_action_scope_repetition_show(cmd, client,
                                                    resource_group_name,
                                                    workflow_name,
                                                    run_name,
                                                    action_name,
                                                    repetition_name):
    return client.get(resource_group_name=resource_group_name,
                      workflow_name=workflow_name,
                      run_name=run_name,
                      action_name=action_name,
                      repetition_name=repetition_name)


def logic_workflow_run_operation_show(cmd, client,
                                      resource_group_name,
                                      workflow_name,
                                      run_name,
                                      operation_id):
    return client.get(resource_group_name=resource_group_name,
                      workflow_name=workflow_name,
                      run_name=run_name,
                      operation_id=operation_id)


def logic_integration_account_list(cmd, client,
                                   resource_group_name=None,
                                   top=None):
    if resource_group_name is not None:
        return client.list_by_resource_group(resource_group_name=resource_group_name,
                                             top=top)
    return client.list_by_subscription(top=top)


def logic_integration_account_show(cmd, client,
                                   resource_group_name,
                                   integration_account_name):
    return client.get(resource_group_name=resource_group_name,
                      integration_account_name=integration_account_name)


def logic_integration_account_create(cmd, client,
                                     resource_group_name,
                                     integration_account_name,
                                     location=None,
                                     tags=None,
                                     sku=None,
                                     integration_service_environment=None,
                                     state=None):
    if isinstance(integration_service_environment, str):
        integration_service_environment = json.loads(integration_service_environment)
    return client.create_or_update(resource_group_name=resource_group_name,
                                   integration_account_name=integration_account_name,
                                   location=location,
                                   tags=tags,
                                   sku=sku,
                                   integration_service_environment=integration_service_environment,
                                   state=state)


def logic_integration_account_update(cmd, client,
                                     resource_group_name,
                                     integration_account_name,
                                     location=None,
                                     tags=None,
                                     sku=None,
                                     integration_service_environment=None,
                                     state=None):
    if isinstance(integration_service_environment, str):
        integration_service_environment = json.loads(integration_service_environment)
    return client.update(resource_group_name=resource_group_name,
                         integration_account_name=integration_account_name,
                         location=location,
                         tags=tags,
                         sku=sku,
                         integration_service_environment=integration_service_environment,
                         state=state)


def logic_integration_account_delete(cmd, client,
                                     resource_group_name,
                                     integration_account_name):
    return client.delete(resource_group_name=resource_group_name,
                         integration_account_name=integration_account_name)


def logic_integration_account_list_callback_url(cmd, client,
                                                resource_group_name,
                                                integration_account_name,
                                                not_after=None,
                                                key_type=None):
    return client.list_callback_url(resource_group_name=resource_group_name,
                                    integration_account_name=integration_account_name,
                                    not_after=not_after,
                                    key_type=key_type)


def logic_integration_account_list_key_vault_key(cmd, client,
                                                 resource_group_name,
                                                 integration_account_name,
                                                 key_vault,
                                                 skip_token=None):
    return client.list_key_vault_key(resource_group_name=resource_group_name,
                                     integration_account_name=integration_account_name,
                                     key_vault=key_vault,
                                     skip_token=skip_token)


def logic_integration_account_log_tracking_event(cmd, client,
                                                 resource_group_name,
                                                 integration_account_name,
                                                 source_type,
                                                 events,
                                                 track_events_options=None):
    if isinstance(events, str):
        events = json.loads(events)
    return client.log_tracking_event(resource_group_name=resource_group_name,
                                     integration_account_name=integration_account_name,
                                     source_type=source_type,
                                     track_events_options=track_events_options,
                                     events=events)


def logic_integration_account_regenerate_access_key(cmd, client,
                                                    resource_group_name,
                                                    integration_account_name,
                                                    key_type=None):
    return client.regenerate_access_key(resource_group_name=resource_group_name,
                                        integration_account_name=integration_account_name,
                                        key_type=key_type)


def logic_integration_account_assembly_list(cmd, client,
                                            resource_group_name,
                                            integration_account_name):
    return client.list(resource_group_name=resource_group_name,
                       integration_account_name=integration_account_name)


def logic_integration_account_assembly_show(cmd, client,
                                            resource_group_name,
                                            integration_account_name,
                                            assembly_artifact_name):
    return client.get(resource_group_name=resource_group_name,
                      integration_account_name=integration_account_name,
                      assembly_artifact_name=assembly_artifact_name)


def logic_integration_account_assembly_create(cmd, client,
                                              resource_group_name,
                                              integration_account_name,
                                              assembly_artifact_name,
                                              properties,
                                              location=None,
                                              tags=None):
    return client.create_or_update(resource_group_name=resource_group_name,
                                   integration_account_name=integration_account_name,
                                   assembly_artifact_name=assembly_artifact_name,
                                   location=location,
                                   tags=tags,
                                   properties=properties)


def logic_integration_account_assembly_update(cmd, client,
                                              resource_group_name,
                                              integration_account_name,
                                              assembly_artifact_name,
                                              properties,
                                              location=None,
                                              tags=None):
    return client.create_or_update(resource_group_name=resource_group_name,
                                   integration_account_name=integration_account_name,
                                   assembly_artifact_name=assembly_artifact_name,
                                   location=location,
                                   tags=tags,
                                   properties=properties)


def logic_integration_account_assembly_delete(cmd, client,
                                              resource_group_name,
                                              integration_account_name,
                                              assembly_artifact_name):
    return client.delete(resource_group_name=resource_group_name,
                         integration_account_name=integration_account_name,
                         assembly_artifact_name=assembly_artifact_name)


def logic_integration_account_assembly_list_content_callback_url(cmd, client,
                                                                 resource_group_name,
                                                                 integration_account_name,
                                                                 assembly_artifact_name):
    return client.list_content_callback_url(resource_group_name=resource_group_name,
                                            integration_account_name=integration_account_name,
                                            assembly_artifact_name=assembly_artifact_name)


def logic_integration_account_batch_configuration_list(cmd, client,
                                                       resource_group_name,
                                                       integration_account_name):
    return client.list(resource_group_name=resource_group_name,
                       integration_account_name=integration_account_name)


def logic_integration_account_batch_configuration_show(cmd, client,
                                                       resource_group_name,
                                                       integration_account_name,
                                                       batch_configuration_name):
    return client.get(resource_group_name=resource_group_name,
                      integration_account_name=integration_account_name,
                      batch_configuration_name=batch_configuration_name)


def logic_integration_account_batch_configuration_create(cmd, client,
                                                         resource_group_name,
                                                         integration_account_name,
                                                         batch_configuration_name,
                                                         properties,
                                                         location=None,
                                                         tags=None):
    if isinstance(properties, str):
        properties = json.loads(properties)
    return client.create_or_update(resource_group_name=resource_group_name,
                                   integration_account_name=integration_account_name,
                                   batch_configuration_name=batch_configuration_name,
                                   location=location,
                                   tags=tags,
                                   properties=properties)


def logic_integration_account_batch_configuration_update(cmd, client,
                                                         resource_group_name,
                                                         integration_account_name,
                                                         batch_configuration_name,
                                                         properties,
                                                         location=None,
                                                         tags=None):
    if isinstance(properties, str):
        properties = json.loads(properties)
    return client.create_or_update(resource_group_name=resource_group_name,
                                   integration_account_name=integration_account_name,
                                   batch_configuration_name=batch_configuration_name,
                                   location=location,
                                   tags=tags,
                                   properties=properties)


def logic_integration_account_batch_configuration_delete(cmd, client,
                                                         resource_group_name,
                                                         integration_account_name,
                                                         batch_configuration_name):
    return client.delete(resource_group_name=resource_group_name,
                         integration_account_name=integration_account_name,
                         batch_configuration_name=batch_configuration_name)


def logic_integration_account_schema_list(cmd, client,
                                          resource_group_name,
                                          integration_account_name,
                                          top=None,
                                          filter=None):
    return client.list(resource_group_name=resource_group_name,
                       integration_account_name=integration_account_name,
                       top=top,
                       filter=filter)


def logic_integration_account_schema_show(cmd, client,
                                          resource_group_name,
                                          integration_account_name,
                                          schema_name):
    return client.get(resource_group_name=resource_group_name,
                      integration_account_name=integration_account_name,
                      schema_name=schema_name)


def logic_integration_account_schema_create(cmd, client,
                                            resource_group_name,
                                            integration_account_name,
                                            schema_name,
                                            schema_type,
                                            properties_content_type,
                                            location=None,
                                            tags=None,
                                            target_namespace=None,
                                            document_name=None,
                                            file_name=None,
                                            metadata=None,
                                            content=None):
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    return client.create_or_update(resource_group_name=resource_group_name,
                                   integration_account_name=integration_account_name,
                                   schema_name=schema_name,
                                   location=location,
                                   tags=tags,
                                   schema_type=schema_type,
                                   target_namespace=target_namespace,
                                   document_name=document_name,
                                   file_name=file_name,
                                   metadata=metadata,
                                   content=content,
                                   content_type_parameter=properties_content_type)


def logic_integration_account_schema_update(cmd, client,
                                            resource_group_name,
                                            integration_account_name,
                                            schema_name,
                                            schema_type,
                                            properties_content_type,
                                            location=None,
                                            tags=None,
                                            target_namespace=None,
                                            document_name=None,
                                            file_name=None,
                                            metadata=None,
                                            content=None):
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    return client.create_or_update(resource_group_name=resource_group_name,
                                   integration_account_name=integration_account_name,
                                   schema_name=schema_name,
                                   location=location,
                                   tags=tags,
                                   schema_type=schema_type,
                                   target_namespace=target_namespace,
                                   document_name=document_name,
                                   file_name=file_name,
                                   metadata=metadata,
                                   content=content,
                                   content_type_parameter=properties_content_type)


def logic_integration_account_schema_delete(cmd, client,
                                            resource_group_name,
                                            integration_account_name,
                                            schema_name):
    return client.delete(resource_group_name=resource_group_name,
                         integration_account_name=integration_account_name,
                         schema_name=schema_name)


def logic_integration_account_schema_list_content_callback_url(cmd, client,
                                                               resource_group_name,
                                                               integration_account_name,
                                                               schema_name,
                                                               not_after=None,
                                                               key_type=None):
    return client.list_content_callback_url(resource_group_name=resource_group_name,
                                            integration_account_name=integration_account_name,
                                            schema_name=schema_name,
                                            not_after=not_after,
                                            key_type=key_type)


def logic_integration_account_map_list(cmd, client,
                                       resource_group_name,
                                       integration_account_name,
                                       top=None,
                                       filter=None):
    return client.list(resource_group_name=resource_group_name,
                       integration_account_name=integration_account_name,
                       top=top,
                       filter=filter)


def logic_integration_account_map_show(cmd, client,
                                       resource_group_name,
                                       integration_account_name,
                                       map_name):
    return client.get(resource_group_name=resource_group_name,
                      integration_account_name=integration_account_name,
                      map_name=map_name)


def logic_integration_account_map_create(cmd, client,
                                         resource_group_name,
                                         integration_account_name,
                                         map_name,
                                         map_type,
                                         properties_content_type,
                                         location=None,
                                         tags=None,
                                         parameters_schema=None,
                                         content=None,
                                         metadata=None):
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    return client.create_or_update(resource_group_name=resource_group_name,
                                   integration_account_name=integration_account_name,
                                   map_name=map_name,
                                   location=location,
                                   tags=tags,
                                   map_type=map_type,
                                   parameters_schema=parameters_schema,
                                   content=content,
                                   content_type_parameter=properties_content_type,
                                   metadata=metadata)


def logic_integration_account_map_update(cmd, client,
                                         resource_group_name,
                                         integration_account_name,
                                         map_name,
                                         map_type,
                                         properties_content_type,
                                         location=None,
                                         tags=None,
                                         parameters_schema=None,
                                         content=None,
                                         metadata=None):
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    return client.create_or_update(resource_group_name=resource_group_name,
                                   integration_account_name=integration_account_name,
                                   map_name=map_name,
                                   location=location,
                                   tags=tags,
                                   map_type=map_type,
                                   parameters_schema=parameters_schema,
                                   content=content,
                                   content_type_parameter=properties_content_type,
                                   metadata=metadata)


def logic_integration_account_map_delete(cmd, client,
                                         resource_group_name,
                                         integration_account_name,
                                         map_name):
    return client.delete(resource_group_name=resource_group_name,
                         integration_account_name=integration_account_name,
                         map_name=map_name)


def logic_integration_account_map_list_content_callback_url(cmd, client,
                                                            resource_group_name,
                                                            integration_account_name,
                                                            map_name,
                                                            not_after=None,
                                                            key_type=None):
    return client.list_content_callback_url(resource_group_name=resource_group_name,
                                            integration_account_name=integration_account_name,
                                            map_name=map_name,
                                            not_after=not_after,
                                            key_type=key_type)


def logic_integration_account_partner_list(cmd, client,
                                           resource_group_name,
                                           integration_account_name,
                                           top=None,
                                           filter=None):
    return client.list(resource_group_name=resource_group_name,
                       integration_account_name=integration_account_name,
                       top=top,
                       filter=filter)


def logic_integration_account_partner_show(cmd, client,
                                           resource_group_name,
                                           integration_account_name,
                                           partner_name):
    return client.get(resource_group_name=resource_group_name,
                      integration_account_name=integration_account_name,
                      partner_name=partner_name)


def logic_integration_account_partner_create(cmd, client,
                                             resource_group_name,
                                             integration_account_name,
                                             partner_name,
                                             partner_type,
                                             content,
                                             location=None,
                                             tags=None,
                                             metadata=None):
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    if isinstance(content, str):
        content = json.loads(content)
    return client.create_or_update(resource_group_name=resource_group_name,
                                   integration_account_name=integration_account_name,
                                   partner_name=partner_name,
                                   location=location,
                                   tags=tags,
                                   partner_type=partner_type,
                                   metadata=metadata,
                                   content=content)


def logic_integration_account_partner_update(cmd, client,
                                             resource_group_name,
                                             integration_account_name,
                                             partner_name,
                                             partner_type,
                                             content,
                                             location=None,
                                             tags=None,
                                             metadata=None):
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    if isinstance(content, str):
        content = json.loads(content)
    return client.create_or_update(resource_group_name=resource_group_name,
                                   integration_account_name=integration_account_name,
                                   partner_name=partner_name,
                                   location=location,
                                   tags=tags,
                                   partner_type=partner_type,
                                   metadata=metadata,
                                   content=content)


def logic_integration_account_partner_delete(cmd, client,
                                             resource_group_name,
                                             integration_account_name,
                                             partner_name):
    return client.delete(resource_group_name=resource_group_name,
                         integration_account_name=integration_account_name,
                         partner_name=partner_name)


def logic_integration_account_partner_list_content_callback_url(cmd, client,
                                                                resource_group_name,
                                                                integration_account_name,
                                                                partner_name,
                                                                not_after=None,
                                                                key_type=None):
    return client.list_content_callback_url(resource_group_name=resource_group_name,
                                            integration_account_name=integration_account_name,
                                            partner_name=partner_name,
                                            not_after=not_after,
                                            key_type=key_type)


def logic_integration_account_agreement_list(cmd, client,
                                             resource_group_name,
                                             integration_account_name,
                                             top=None,
                                             filter=None):
    return client.list(resource_group_name=resource_group_name,
                       integration_account_name=integration_account_name,
                       top=top,
                       filter=filter)


def logic_integration_account_agreement_show(cmd, client,
                                             resource_group_name,
                                             integration_account_name,
                                             agreement_name):
    return client.get(resource_group_name=resource_group_name,
                      integration_account_name=integration_account_name,
                      agreement_name=agreement_name)


def logic_integration_account_agreement_create(cmd, client,
                                               resource_group_name,
                                               integration_account_name,
                                               agreement_name,
                                               agreement_type,
                                               host_partner,
                                               guest_partner,
                                               host_identity,
                                               guest_identity,
                                               content,
                                               location=None,
                                               tags=None,
                                               metadata=None):
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    if isinstance(content, str):
        content = json.loads(content)
    return client.create_or_update(resource_group_name=resource_group_name,
                                   integration_account_name=integration_account_name,
                                   agreement_name=agreement_name,
                                   location=location,
                                   tags=tags,
                                   metadata=metadata,
                                   agreement_type=agreement_type,
                                   host_partner=host_partner,
                                   guest_partner=guest_partner,
                                   host_identity=host_identity,
                                   guest_identity=guest_identity,
                                   content=content)


def logic_integration_account_agreement_update(cmd, client,
                                               resource_group_name,
                                               integration_account_name,
                                               agreement_name,
                                               agreement_type,
                                               host_partner,
                                               guest_partner,
                                               host_identity,
                                               guest_identity,
                                               content,
                                               location=None,
                                               tags=None,
                                               metadata=None):
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    if isinstance(content, str):
        content = json.loads(content)
    return client.create_or_update(resource_group_name=resource_group_name,
                                   integration_account_name=integration_account_name,
                                   agreement_name=agreement_name,
                                   location=location,
                                   tags=tags,
                                   metadata=metadata,
                                   agreement_type=agreement_type,
                                   host_partner=host_partner,
                                   guest_partner=guest_partner,
                                   host_identity=host_identity,
                                   guest_identity=guest_identity,
                                   content=content)


def logic_integration_account_agreement_delete(cmd, client,
                                               resource_group_name,
                                               integration_account_name,
                                               agreement_name):
    return client.delete(resource_group_name=resource_group_name,
                         integration_account_name=integration_account_name,
                         agreement_name=agreement_name)


def logic_integration_account_agreement_list_content_callback_url(cmd, client,
                                                                  resource_group_name,
                                                                  integration_account_name,
                                                                  agreement_name,
                                                                  not_after=None,
                                                                  key_type=None):
    return client.list_content_callback_url(resource_group_name=resource_group_name,
                                            integration_account_name=integration_account_name,
                                            agreement_name=agreement_name,
                                            not_after=not_after,
                                            key_type=key_type)


def logic_integration_account_certificate_list(cmd, client,
                                               resource_group_name,
                                               integration_account_name,
                                               top=None):
    return client.list(resource_group_name=resource_group_name,
                       integration_account_name=integration_account_name,
                       top=top)


def logic_integration_account_certificate_show(cmd, client,
                                               resource_group_name,
                                               integration_account_name,
                                               certificate_name):
    return client.get(resource_group_name=resource_group_name,
                      integration_account_name=integration_account_name,
                      certificate_name=certificate_name)


def logic_integration_account_certificate_create(cmd, client,
                                                 resource_group_name,
                                                 integration_account_name,
                                                 certificate_name,
                                                 location=None,
                                                 tags=None,
                                                 metadata=None,
                                                 key=None,
                                                 public_certificate=None):
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    if isinstance(key, str):
        key = json.loads(key)
    return client.create_or_update(resource_group_name=resource_group_name,
                                   integration_account_name=integration_account_name,
                                   certificate_name=certificate_name,
                                   location=location,
                                   tags=tags,
                                   metadata=metadata,
                                   key=key,
                                   public_certificate=public_certificate)


def logic_integration_account_certificate_update(cmd, client,
                                                 resource_group_name,
                                                 integration_account_name,
                                                 certificate_name,
                                                 location=None,
                                                 tags=None,
                                                 metadata=None,
                                                 key=None,
                                                 public_certificate=None):
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    if isinstance(key, str):
        key = json.loads(key)
    return client.create_or_update(resource_group_name=resource_group_name,
                                   integration_account_name=integration_account_name,
                                   certificate_name=certificate_name,
                                   location=location,
                                   tags=tags,
                                   metadata=metadata,
                                   key=key,
                                   public_certificate=public_certificate)


def logic_integration_account_certificate_delete(cmd, client,
                                                 resource_group_name,
                                                 integration_account_name,
                                                 certificate_name):
    return client.delete(resource_group_name=resource_group_name,
                         integration_account_name=integration_account_name,
                         certificate_name=certificate_name)


def logic_integration_account_session_list(cmd, client,
                                           resource_group_name,
                                           integration_account_name,
                                           top=None,
                                           filter=None):
    return client.list(resource_group_name=resource_group_name,
                       integration_account_name=integration_account_name,
                       top=top,
                       filter=filter)


def logic_integration_account_session_show(cmd, client,
                                           resource_group_name,
                                           integration_account_name,
                                           session_name):
    return client.get(resource_group_name=resource_group_name,
                      integration_account_name=integration_account_name,
                      session_name=session_name)


def logic_integration_account_session_create(cmd, client,
                                             resource_group_name,
                                             integration_account_name,
                                             session_name,
                                             location=None,
                                             tags=None,
                                             content=None):
    if isinstance(content, str):
        content = json.loads(content)
    return client.create_or_update(resource_group_name=resource_group_name,
                                   integration_account_name=integration_account_name,
                                   session_name=session_name,
                                   location=location,
                                   tags=tags,
                                   content=content)


def logic_integration_account_session_update(cmd, client,
                                             resource_group_name,
                                             integration_account_name,
                                             session_name,
                                             location=None,
                                             tags=None,
                                             content=None):
    if isinstance(content, str):
        content = json.loads(content)
    return client.create_or_update(resource_group_name=resource_group_name,
                                   integration_account_name=integration_account_name,
                                   session_name=session_name,
                                   location=location,
                                   tags=tags,
                                   content=content)


def logic_integration_account_session_delete(cmd, client,
                                             resource_group_name,
                                             integration_account_name,
                                             session_name):
    return client.delete(resource_group_name=resource_group_name,
                         integration_account_name=integration_account_name,
                         session_name=session_name)


def logic_integration_service_environment_list(cmd, client,
                                               resource_group=None,
                                               top=None):
    if resource_group is not None:
        return client.list_by_resource_group(resource_group=resource_group,
                                             top=top)
    return client.list_by_subscription(top=top)


def logic_integration_service_environment_show(cmd, client,
                                               resource_group,
                                               integration_service_environment_name):
    return client.get(resource_group=resource_group,
                      integration_service_environment_name=integration_service_environment_name)


def logic_integration_service_environment_create(cmd, client,
                                                 resource_group,
                                                 integration_service_environment_name,
                                                 location=None,
                                                 tags=None,
                                                 properties=None,
                                                 sku=None):
    if isinstance(properties, str):
        properties = json.loads(properties)
    return client.begin_create_or_update(resource_group=resource_group,
                                         integration_service_environment_name=integration_service_environment_name,
                                         location=location,
                                         tags=tags,
                                         properties=properties,
                                         sku=sku)


def logic_integration_service_environment_update(cmd, client,
                                                 resource_group,
                                                 integration_service_environment_name,
                                                 location=None,
                                                 tags=None,
                                                 properties=None,
                                                 sku=None):
    if isinstance(properties, str):
        properties = json.loads(properties)
    return client.begin_update(resource_group=resource_group,
                               integration_service_environment_name=integration_service_environment_name,
                               location=location,
                               tags=tags,
                               properties=properties,
                               sku=sku)


def logic_integration_service_environment_delete(cmd, client,
                                                 resource_group,
                                                 integration_service_environment_name):
    return client.delete(resource_group=resource_group,
                         integration_service_environment_name=integration_service_environment_name)


def logic_integration_service_environment_restart(cmd, client,
                                                  resource_group,
                                                  integration_service_environment_name):
    return client.restart(resource_group=resource_group,
                          integration_service_environment_name=integration_service_environment_name)


def logic_integration_service_environment_sku_list(cmd, client,
                                                   resource_group,
                                                   integration_service_environment_name):
    return client.list(resource_group=resource_group,
                       integration_service_environment_name=integration_service_environment_name)


def logic_integration_service_environment_network_health_show(cmd, client,
                                                              resource_group,
                                                              integration_service_environment_name):
    return client.get(resource_group=resource_group,
                      integration_service_environment_name=integration_service_environment_name)


def logic_integration_service_environment_managed_api_list(cmd, client,
                                                           resource_group,
                                                           integration_service_environment_name):
    return client.list(resource_group=resource_group,
                       integration_service_environment_name=integration_service_environment_name)


def logic_integration_service_environment_managed_api_show(cmd, client,
                                                           resource_group,
                                                           integration_service_environment_name,
                                                           api_name):
    return client.get(resource_group=resource_group,
                      integration_service_environment_name=integration_service_environment_name,
                      api_name=api_name)


def logic_integration_service_environment_managed_api_delete(cmd, client,
                                                             resource_group,
                                                             integration_service_environment_name,
                                                             api_name):
    return client.begin_delete(resource_group=resource_group,
                               integration_service_environment_name=integration_service_environment_name,
                               api_name=api_name)


def logic_integration_service_environment_managed_api_put(cmd, client,
                                                          resource_group,
                                                          integration_service_environment_name,
                                                          api_name):
    return client.begin_put(resource_group=resource_group,
                            integration_service_environment_name=integration_service_environment_name,
                            api_name=api_name)


def logic_integration_service_environment_managed_api_operation_list(cmd, client,
                                                                     resource_group,
                                                                     integration_service_environment_name,
                                                                     api_name):
    return client.list(resource_group=resource_group,
                       integration_service_environment_name=integration_service_environment_name,
                       api_name=api_name)
