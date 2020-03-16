# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument
import json
from knack.util import CLIError

def logic_workflow_list(cmd, client,
                        resource_group_name=None,
                        top=None,
                        filter=None):
    if resource_group_name is not None:
        return client.list_by_resource_group(resource_group_name=resource_group_name, top=top, filter=filter)
    return client.list_by_subscription(top=top, filter=filter)


def logic_workflow_show(cmd, client,
                        resource_group_name,
                        workflow_name):
    return client.get(resource_group_name=resource_group_name, workflow_name=workflow_name)


def logic_workflow_create(cmd, client,
                          resource_group_name,
                          location,
                          workflow_name,
                          workflow_file_path):
    
    with open(workflow_file_path) as json_file:
        workflow = json.load(json_file)
        if 'properties' in workflow and 'definition' not in workflow['properties']:
            raise CLIError(str(json_file) + " does not contain a 'properties.definition' key")
        elif 'properties' not in workflow and 'definition' not in workflow:
            raise CLIError(str(json_file) + " does not contain a 'definition' key")
        elif 'properties' not in workflow:
             workflow = {'properties' : workflow}        
        workflow['location'] = location
        return client.create_or_update(resource_group_name=resource_group_name, workflow_name=workflow_name, workflow=workflow)
    


def logic_workflow_update(cmd, client,
                          resource_group_name,
                          workflow_name,
                          tags=None):
    tags = {'tags': tags}
    return client.update(resource_group_name=resource_group_name, workflow_name=workflow_name, tags=tags)


def logic_workflow_delete(cmd, client,
                          resource_group_name,
                          workflow_name):
    return client.delete(resource_group_name=resource_group_name, workflow_name=workflow_name)


def logic_workflow_generate_upgraded_definition(cmd, client,
                                                resource_group_name,
                                                workflow_name,
                                                parameters):
    return client.generate_upgraded_definition(resource_group_name=resource_group_name, workflow_name=workflow_name, parameters=parameters)


def logic_workflow_list_callback_url(cmd, client,
                                     resource_group_name,
                                     workflow_name,
                                     list_callback_url):
    return client.list_callback_url(resource_group_name=resource_group_name, workflow_name=workflow_name, list_callback_url=list_callback_url)


def logic_workflow_move(cmd, client,
                        resource_group_name,
                        workflow_name,
                        move):
    return client.begin_move(resource_group_name=resource_group_name, workflow_name=workflow_name, move=move)


def logic_workflow_regenerate_access_key(cmd, client,
                                         resource_group_name,
                                         workflow_name,
                                         key_type):
    return client.regenerate_access_key(resource_group_name=resource_group_name, workflow_name=workflow_name, key_type=key_type)


def logic_workflow_validate_by_resource_group(cmd, client,
                                              resource_group_name,
                                              workflow_name,
                                              validate):
    return client.validate_by_resource_group(resource_group_name=resource_group_name, workflow_name=workflow_name, validate=validate)


def logic_workflow_validate_by_location(cmd, client,
                                        resource_group_name,
                                        location,
                                        workflow_name):
    return client.validate_by_location(resource_group_name=resource_group_name, location=location, workflow_name=workflow_name)


def logic_workflow_disable(cmd, client,
                           resource_group_name,
                           workflow_name):
    return client.disable(resource_group_name=resource_group_name, workflow_name=workflow_name)


def logic_workflow_enable(cmd, client,
                          resource_group_name,
                          workflow_name):
    return client.enable(resource_group_name=resource_group_name, workflow_name=workflow_name)


def logic_workflow_list_swagger(cmd, client,
                                resource_group_name,
                                workflow_name):
    return client.list_swagger(resource_group_name=resource_group_name, workflow_name=workflow_name)


def logic_workflow_version_list(cmd, client,
                                resource_group_name,
                                workflow_name,
                                top=None):
    return client.list(resource_group_name=resource_group_name, workflow_name=workflow_name, top=top)


def logic_workflow_version_show(cmd, client,
                                resource_group_name,
                                workflow_name,
                                version_id):
    return client.get(resource_group_name=resource_group_name, workflow_name=workflow_name, version_id=version_id)


def logic_workflow_trigger_list(cmd, client,
                                resource_group_name,
                                workflow_name,
                                top=None,
                                filter=None):
    return client.list(resource_group_name=resource_group_name, workflow_name=workflow_name, top=top, filter=filter)


def logic_workflow_trigger_show(cmd, client,
                                resource_group_name,
                                workflow_name,
                                trigger_name):
    return client.get(resource_group_name=resource_group_name, workflow_name=workflow_name, trigger_name=trigger_name)


def logic_workflow_trigger_reset(cmd, client,
                                 resource_group_name,
                                 workflow_name,
                                 trigger_name,
                                 set_state=None):
    if resource_group_name is not None and workflow_name is not None and trigger_name is not None:
        return client.get_schema_json(resource_group_name=resource_group_name, workflow_name=workflow_name, trigger_name=trigger_name)
    elif resource_group_name is not None and workflow_name is not None and trigger_name is not None and set_state is not None:
        return client.set_state(resource_group_name=resource_group_name, workflow_name=workflow_name, trigger_name=trigger_name, set_state=set_state)
    return client.reset(resource_group_name=resource_group_name, workflow_name=workflow_name, trigger_name=trigger_name)


def logic_workflow_trigger_run(cmd, client,
                               resource_group_name,
                               workflow_name,
                               trigger_name):
    return client.run(resource_group_name=resource_group_name, workflow_name=workflow_name, trigger_name=trigger_name)


def logic_workflow_trigger_list_callback_url(cmd, client,
                                             resource_group_name,
                                             workflow_name,
                                             trigger_name):
    return client.list_callback_url(resource_group_name=resource_group_name, workflow_name=workflow_name, trigger_name=trigger_name)


def logic_workflow_version_trigger_list_callback_url(cmd, client,
                                                     resource_group_name,
                                                     workflow_name,
                                                     version_id,
                                                     trigger_name,
                                                     parameters=None):
    return client.list_callback_url(resource_group_name=resource_group_name, workflow_name=workflow_name, version_id=version_id, trigger_name=trigger_name, parameters=parameters)


def logic_workflow_trigger_history_list(cmd, client,
                                        resource_group_name,
                                        workflow_name,
                                        trigger_name,
                                        top=None,
                                        filter=None):
    return client.list(resource_group_name=resource_group_name, workflow_name=workflow_name, trigger_name=trigger_name, top=top, filter=filter)


def logic_workflow_trigger_history_show(cmd, client,
                                        resource_group_name,
                                        workflow_name,
                                        trigger_name,
                                        history_name):
    return client.get(resource_group_name=resource_group_name, workflow_name=workflow_name, trigger_name=trigger_name, history_name=history_name)


def logic_workflow_trigger_history_resubmit(cmd, client,
                                            resource_group_name,
                                            workflow_name,
                                            trigger_name,
                                            history_name):
    return client.resubmit(resource_group_name=resource_group_name, workflow_name=workflow_name, trigger_name=trigger_name, history_name=history_name)


def logic_workflow_run_list(cmd, client,
                            resource_group_name,
                            workflow_name,
                            top=None,
                            filter=None):
    return client.list(resource_group_name=resource_group_name, workflow_name=workflow_name, top=top, filter=filter)


def logic_workflow_run_show(cmd, client,
                            resource_group_name,
                            workflow_name,
                            run_name):
    return client.get(resource_group_name=resource_group_name, workflow_name=workflow_name, run_name=run_name)


def logic_workflow_run_cancel(cmd, client,
                              resource_group_name,
                              workflow_name,
                              run_name):
    return client.cancel(resource_group_name=resource_group_name, workflow_name=workflow_name, run_name=run_name)


def logic_workflow_run_action_list(cmd, client,
                                   resource_group_name,
                                   workflow_name,
                                   run_name,
                                   top=None,
                                   filter=None):
    return client.list(resource_group_name=resource_group_name, workflow_name=workflow_name, run_name=run_name, top=top, filter=filter)


def logic_workflow_run_action_show(cmd, client,
                                   resource_group_name,
                                   workflow_name,
                                   run_name,
                                   action_name):
    return client.get(resource_group_name=resource_group_name, workflow_name=workflow_name, run_name=run_name, action_name=action_name)


def logic_workflow_run_action_list_expression_trace(cmd, client,
                                                    resource_group_name,
                                                    workflow_name,
                                                    run_name,
                                                    action_name):
    return client.list_expression_trace(resource_group_name=resource_group_name, workflow_name=workflow_name, run_name=run_name, action_name=action_name)


def logic_workflow_run_action_repetition_list(cmd, client,
                                              resource_group_name,
                                              workflow_name,
                                              run_name,
                                              action_name):
    return client.list(resource_group_name=resource_group_name, workflow_name=workflow_name, run_name=run_name, action_name=action_name)


def logic_workflow_run_action_repetition_show(cmd, client,
                                              resource_group_name,
                                              workflow_name,
                                              run_name,
                                              action_name,
                                              repetition_name):
    return client.get(resource_group_name=resource_group_name, workflow_name=workflow_name, run_name=run_name, action_name=action_name, repetition_name=repetition_name)


def logic_workflow_run_action_repetition_list_expression_trace(cmd, client,
                                                               resource_group_name,
                                                               workflow_name,
                                                               run_name,
                                                               action_name,
                                                               repetition_name):
    return client.list_expression_trace(resource_group_name=resource_group_name, workflow_name=workflow_name, run_name=run_name, action_name=action_name, repetition_name=repetition_name)


def logic_workflow_run_action_repetition_request_history_list(cmd, client,
                                                              resource_group_name,
                                                              workflow_name,
                                                              run_name,
                                                              action_name,
                                                              repetition_name):
    return client.list(resource_group_name=resource_group_name, workflow_name=workflow_name, run_name=run_name, action_name=action_name, repetition_name=repetition_name)


def logic_workflow_run_action_repetition_request_history_show(cmd, client,
                                                              resource_group_name,
                                                              workflow_name,
                                                              run_name,
                                                              action_name,
                                                              repetition_name,
                                                              request_history_name):
    return client.get(resource_group_name=resource_group_name, workflow_name=workflow_name, run_name=run_name, action_name=action_name, repetition_name=repetition_name, request_history_name=request_history_name)


def logic_workflow_run_action_request_history_list(cmd, client,
                                                   resource_group_name,
                                                   workflow_name,
                                                   run_name,
                                                   action_name):
    return client.list(resource_group_name=resource_group_name, workflow_name=workflow_name, run_name=run_name, action_name=action_name)


def logic_workflow_run_action_request_history_show(cmd, client,
                                                   resource_group_name,
                                                   workflow_name,
                                                   run_name,
                                                   action_name,
                                                   request_history_name):
    return client.get(resource_group_name=resource_group_name, workflow_name=workflow_name, run_name=run_name, action_name=action_name, request_history_name=request_history_name)


def logic_workflow_run_action_scope_repetition_list(cmd, client,
                                                    resource_group_name,
                                                    workflow_name,
                                                    run_name,
                                                    action_name):
    return client.list(resource_group_name=resource_group_name, workflow_name=workflow_name, run_name=run_name, action_name=action_name)


def logic_workflow_run_action_scope_repetition_show(cmd, client,
                                                    resource_group_name,
                                                    workflow_name,
                                                    run_name,
                                                    action_name,
                                                    repetition_name):
    return client.get(resource_group_name=resource_group_name, workflow_name=workflow_name, run_name=run_name, action_name=action_name, repetition_name=repetition_name)


def logic_workflow_run_operation_show(cmd, client,
                                      resource_group_name,
                                      workflow_name,
                                      run_name,
                                      operation_id):
    return client.get(resource_group_name=resource_group_name, workflow_name=workflow_name, run_name=run_name, operation_id=operation_id)


def logic_integration_account_list(cmd, client,
                                   resource_group_name=None,
                                   top=None):
    if resource_group_name is not None:
        return client.list_by_resource_group(resource_group_name=resource_group_name, top=top)
    return client.list_by_subscription(top=top)


def logic_integration_account_show(cmd, client,
                                   resource_group_name,
                                   integration_account_name):
    return client.get(resource_group_name=resource_group_name, integration_account_name=integration_account_name)


def logic_integration_account_create(cmd, client,
                                     resource_group_name,
                                     integration_account_name,
                                     integration_file_path):
    with open(integration_file_path) as integrationJson:
        integration = json.load(integrationJson)
        if 'properties' not in integration:
            raise CLIError(str(integrationJson) + " does not contain a 'properties' key")
        if 'location' not in integration:
            raise CLIError(str(integrationJson) + " does not contain a 'location' key")
    return client.create_or_update(resource_group_name=resource_group_name, integration_account_name=integration_account_name, integration_account=integration)


def logic_integration_account_update(cmd, client,
                                     resource_group_name,
                                     integration_account_name,
                                     sku=None,
                                     tags=None):
    update_dict = {}
    if sku:
        update_dict['sku'] = {"name": sku}
    if tags:
        update_dict['tags'] = tags
    if not update_dict:
        raise CLIError("Nothing to update. Either --sku or --tags must be specfied")
    return client.update(resource_group_name=resource_group_name, integration_account_name=integration_account_name, update=update_dict)


def logic_integration_account_delete(cmd, client,
                                     resource_group_name,
                                     integration_account_name):
    return client.delete(resource_group_name=resource_group_name, integration_account_name=integration_account_name)


def logic_integration_account_list_callback_url(cmd, client,
                                                resource_group_name,
                                                integration_account_name,
                                                parameters):
    return client.list_callback_url(resource_group_name=resource_group_name, integration_account_name=integration_account_name, parameters=parameters)


def logic_integration_account_list_key_vault_key(cmd, client,
                                                 resource_group_name,
                                                 integration_account_name,
                                                 list_key_vault_keys):
    return client.list_key_vault_key(resource_group_name=resource_group_name, integration_account_name=integration_account_name, list_key_vault_keys=list_key_vault_keys)


def logic_integration_account_log_tracking_event(cmd, client,
                                                 resource_group_name,
                                                 integration_account_name,
                                                 log_tracking_events):
    return client.log_tracking_event(resource_group_name=resource_group_name, integration_account_name=integration_account_name, log_tracking_events=log_tracking_events)


def logic_integration_account_regenerate_access_key(cmd, client,
                                                    resource_group_name,
                                                    integration_account_name,
                                                    regenerate_access_key):
    return client.regenerate_access_key(resource_group_name=resource_group_name, integration_account_name=integration_account_name, regenerate_access_key=regenerate_access_key)


def logic_integration_account_assembly_list(cmd, client,
                                            resource_group_name,
                                            integration_account_name):
    return client.list(resource_group_name=resource_group_name, integration_account_name=integration_account_name)


def logic_integration_account_assembly_show(cmd, client,
                                            resource_group_name,
                                            integration_account_name,
                                            assembly_artifact_name):
    return client.get(resource_group_name=resource_group_name, integration_account_name=integration_account_name, assembly_artifact_name=assembly_artifact_name)


def logic_integration_account_assembly_create(cmd, client,
                                              resource_group_name,
                                              integration_account_name,
                                              assembly_artifact_name,
                                              assembly_artifact):
    return client.create_or_update(resource_group_name=resource_group_name, integration_account_name=integration_account_name, assembly_artifact_name=assembly_artifact_name, assembly_artifact=assembly_artifact)


def logic_integration_account_assembly_update(cmd, client,
                                              resource_group_name,
                                              integration_account_name,
                                              assembly_artifact_name,
                                              assembly_artifact):
    return client.create_or_update(resource_group_name=resource_group_name, integration_account_name=integration_account_name, assembly_artifact_name=assembly_artifact_name, assembly_artifact=assembly_artifact)


def logic_integration_account_assembly_delete(cmd, client,
                                              resource_group_name,
                                              integration_account_name,
                                              assembly_artifact_name):
    return client.delete(resource_group_name=resource_group_name, integration_account_name=integration_account_name, assembly_artifact_name=assembly_artifact_name)


def logic_integration_account_assembly_list_content_callback_url(cmd, client,
                                                                 resource_group_name,
                                                                 integration_account_name,
                                                                 assembly_artifact_name):
    return client.list_content_callback_url(resource_group_name=resource_group_name, integration_account_name=integration_account_name, assembly_artifact_name=assembly_artifact_name)


def logic_integration_account_batch_configuration_list(cmd, client,
                                                       resource_group_name,
                                                       integration_account_name):
    return client.list(resource_group_name=resource_group_name, integration_account_name=integration_account_name)


def logic_integration_account_batch_configuration_show(cmd, client,
                                                       resource_group_name,
                                                       integration_account_name,
                                                       batch_configuration_name):
    return client.get(resource_group_name=resource_group_name, integration_account_name=integration_account_name, batch_configuration_name=batch_configuration_name)


def logic_integration_account_batch_configuration_create(cmd, client,
                                                         resource_group_name,
                                                         integration_account_name,
                                                         batch_configuration_name,
                                                         batch_configuration):
    return client.create_or_update(resource_group_name=resource_group_name, integration_account_name=integration_account_name, batch_configuration_name=batch_configuration_name, batch_configuration=batch_configuration)


def logic_integration_account_batch_configuration_update(cmd, client,
                                                         resource_group_name,
                                                         integration_account_name,
                                                         batch_configuration_name,
                                                         batch_configuration):
    return client.create_or_update(resource_group_name=resource_group_name, integration_account_name=integration_account_name, batch_configuration_name=batch_configuration_name, batch_configuration=batch_configuration)


def logic_integration_account_batch_configuration_delete(cmd, client,
                                                         resource_group_name,
                                                         integration_account_name,
                                                         batch_configuration_name):
    return client.delete(resource_group_name=resource_group_name, integration_account_name=integration_account_name, batch_configuration_name=batch_configuration_name)


def logic_integration_account_schema_list(cmd, client,
                                          resource_group_name,
                                          integration_account_name,
                                          top=None,
                                          filter=None):
    return client.list(resource_group_name=resource_group_name, integration_account_name=integration_account_name, top=top, filter=filter)


def logic_integration_account_schema_show(cmd, client,
                                          resource_group_name,
                                          integration_account_name,
                                          schema_name):
    return client.get(resource_group_name=resource_group_name, integration_account_name=integration_account_name, schema_name=schema_name)


def logic_integration_account_schema_create(cmd, client,
                                            resource_group_name,
                                            integration_account_name,
                                            schema_name,
                                            schema):
    return client.create_or_update(resource_group_name=resource_group_name, integration_account_name=integration_account_name, schema_name=schema_name, schema=schema)


def logic_integration_account_schema_update(cmd, client,
                                            resource_group_name,
                                            integration_account_name,
                                            schema_name,
                                            schema):
    return client.create_or_update(resource_group_name=resource_group_name, integration_account_name=integration_account_name, schema_name=schema_name, schema=schema)


def logic_integration_account_schema_delete(cmd, client,
                                            resource_group_name,
                                            integration_account_name,
                                            schema_name):
    return client.delete(resource_group_name=resource_group_name, integration_account_name=integration_account_name, schema_name=schema_name)


def logic_integration_account_schema_list_content_callback_url(cmd, client,
                                                               resource_group_name,
                                                               integration_account_name,
                                                               schema_name,
                                                               list_content_callback_url):
    return client.list_content_callback_url(resource_group_name=resource_group_name, integration_account_name=integration_account_name, schema_name=schema_name, list_content_callback_url=list_content_callback_url)


def logic_integration_account_map_list(cmd, client,
                                       resource_group_name,
                                       integration_account_name,
                                       top=None,
                                       filter=None):
    return client.list(resource_group_name=resource_group_name, integration_account_name=integration_account_name, top=top, filter=filter)


def logic_integration_account_map_show(cmd, client,
                                       resource_group_name,
                                       integration_account_name,
                                       map_name):
    return client.get(resource_group_name=resource_group_name, integration_account_name=integration_account_name, map_name=map_name)


def logic_integration_account_map_create(cmd, client,
                                         resource_group_name,
                                         integration_account_name,
                                         map_name,
                                         map):
    return client.create_or_update(resource_group_name=resource_group_name, integration_account_name=integration_account_name, map_name=map_name, map=map)


def logic_integration_account_map_update(cmd, client,
                                         resource_group_name,
                                         integration_account_name,
                                         map_name,
                                         map):
    return client.create_or_update(resource_group_name=resource_group_name, integration_account_name=integration_account_name, map_name=map_name, map=map)


def logic_integration_account_map_delete(cmd, client,
                                         resource_group_name,
                                         integration_account_name,
                                         map_name):
    return client.delete(resource_group_name=resource_group_name, integration_account_name=integration_account_name, map_name=map_name)


def logic_integration_account_map_list_content_callback_url(cmd, client,
                                                            resource_group_name,
                                                            integration_account_name,
                                                            map_name,
                                                            list_content_callback_url):
    return client.list_content_callback_url(resource_group_name=resource_group_name, integration_account_name=integration_account_name, map_name=map_name, list_content_callback_url=list_content_callback_url)


def logic_integration_account_partner_list(cmd, client,
                                           resource_group_name,
                                           integration_account_name,
                                           top=None,
                                           filter=None):
    return client.list(resource_group_name=resource_group_name, integration_account_name=integration_account_name, top=top, filter=filter)


def logic_integration_account_partner_show(cmd, client,
                                           resource_group_name,
                                           integration_account_name,
                                           partner_name):
    return client.get(resource_group_name=resource_group_name, integration_account_name=integration_account_name, partner_name=partner_name)


def logic_integration_account_partner_create(cmd, client,
                                             resource_group_name,
                                             integration_account_name,
                                             partner_name,
                                             partner):
    return client.create_or_update(resource_group_name=resource_group_name, integration_account_name=integration_account_name, partner_name=partner_name, partner=partner)


def logic_integration_account_partner_update(cmd, client,
                                             resource_group_name,
                                             integration_account_name,
                                             partner_name,
                                             partner):
    return client.create_or_update(resource_group_name=resource_group_name, integration_account_name=integration_account_name, partner_name=partner_name, partner=partner)


def logic_integration_account_partner_delete(cmd, client,
                                             resource_group_name,
                                             integration_account_name,
                                             partner_name):
    return client.delete(resource_group_name=resource_group_name, integration_account_name=integration_account_name, partner_name=partner_name)


def logic_integration_account_partner_list_content_callback_url(cmd, client,
                                                                resource_group_name,
                                                                integration_account_name,
                                                                partner_name,
                                                                list_content_callback_url):
    return client.list_content_callback_url(resource_group_name=resource_group_name, integration_account_name=integration_account_name, partner_name=partner_name, list_content_callback_url=list_content_callback_url)


def logic_integration_account_agreement_list(cmd, client,
                                             resource_group_name,
                                             integration_account_name,
                                             top=None,
                                             filter=None):
    return client.list(resource_group_name=resource_group_name, integration_account_name=integration_account_name, top=top, filter=filter)


def logic_integration_account_agreement_show(cmd, client,
                                             resource_group_name,
                                             integration_account_name,
                                             agreement_name):
    return client.get(resource_group_name=resource_group_name, integration_account_name=integration_account_name, agreement_name=agreement_name)


def logic_integration_account_agreement_create(cmd, client,
                                               resource_group_name,
                                               integration_account_name,
                                               agreement_name,
                                               agreement):
    return client.create_or_update(resource_group_name=resource_group_name, integration_account_name=integration_account_name, agreement_name=agreement_name, agreement=agreement)


def logic_integration_account_agreement_update(cmd, client,
                                               resource_group_name,
                                               integration_account_name,
                                               agreement_name,
                                               agreement):
    return client.create_or_update(resource_group_name=resource_group_name, integration_account_name=integration_account_name, agreement_name=agreement_name, agreement=agreement)


def logic_integration_account_agreement_delete(cmd, client,
                                               resource_group_name,
                                               integration_account_name,
                                               agreement_name):
    return client.delete(resource_group_name=resource_group_name, integration_account_name=integration_account_name, agreement_name=agreement_name)


def logic_integration_account_agreement_list_content_callback_url(cmd, client,
                                                                  resource_group_name,
                                                                  integration_account_name,
                                                                  agreement_name,
                                                                  list_content_callback_url):
    return client.list_content_callback_url(resource_group_name=resource_group_name, integration_account_name=integration_account_name, agreement_name=agreement_name, list_content_callback_url=list_content_callback_url)


def logic_integration_account_certificate_list(cmd, client,
                                               resource_group_name,
                                               integration_account_name,
                                               top=None):
    return client.list(resource_group_name=resource_group_name, integration_account_name=integration_account_name, top=top)


def logic_integration_account_certificate_show(cmd, client,
                                               resource_group_name,
                                               integration_account_name,
                                               certificate_name):
    return client.get(resource_group_name=resource_group_name, integration_account_name=integration_account_name, certificate_name=certificate_name)


def logic_integration_account_certificate_create(cmd, client,
                                                 resource_group_name,
                                                 integration_account_name,
                                                 certificate_name,
                                                 certificate):
    return client.create_or_update(resource_group_name=resource_group_name, integration_account_name=integration_account_name, certificate_name=certificate_name, certificate=certificate)


def logic_integration_account_certificate_update(cmd, client,
                                                 resource_group_name,
                                                 integration_account_name,
                                                 certificate_name,
                                                 certificate):
    return client.create_or_update(resource_group_name=resource_group_name, integration_account_name=integration_account_name, certificate_name=certificate_name, certificate=certificate)


def logic_integration_account_certificate_delete(cmd, client,
                                                 resource_group_name,
                                                 integration_account_name,
                                                 certificate_name):
    return client.delete(resource_group_name=resource_group_name, integration_account_name=integration_account_name, certificate_name=certificate_name)


def logic_integration_account_session_list(cmd, client,
                                           resource_group_name,
                                           integration_account_name,
                                           top=None,
                                           filter=None):
    return client.list(resource_group_name=resource_group_name, integration_account_name=integration_account_name, top=top, filter=filter)


def logic_integration_account_session_show(cmd, client,
                                           resource_group_name,
                                           integration_account_name,
                                           session_name):
    return client.get(resource_group_name=resource_group_name, integration_account_name=integration_account_name, session_name=session_name)


def logic_integration_account_session_create(cmd, client,
                                             resource_group_name,
                                             integration_account_name,
                                             session_name,
                                             session):
    return client.create_or_update(resource_group_name=resource_group_name, integration_account_name=integration_account_name, session_name=session_name, session=session)


def logic_integration_account_session_update(cmd, client,
                                             resource_group_name,
                                             integration_account_name,
                                             session_name,
                                             session):
    return client.create_or_update(resource_group_name=resource_group_name, integration_account_name=integration_account_name, session_name=session_name, session=session)


def logic_integration_account_session_delete(cmd, client,
                                             resource_group_name,
                                             integration_account_name,
                                             session_name):
    return client.delete(resource_group_name=resource_group_name, integration_account_name=integration_account_name, session_name=session_name)


def logic_integration_service_environment_list(cmd, client,
                                               resource_group=None,
                                               top=None):
    if resource_group is not None:
        return client.list_by_resource_group(resource_group=resource_group, top=top)
    return client.list_by_subscription(top=top)


def logic_integration_service_environment_show(cmd, client,
                                               resource_group,
                                               integration_service_environment_name):
    return client.get(resource_group=resource_group, integration_service_environment_name=integration_service_environment_name)


def logic_integration_service_environment_create(cmd, client,
                                                 resource_group,
                                                 integration_service_environment_name,
                                                 integration_service_environment):
    return client.begin_create_or_update(resource_group=resource_group, integration_service_environment_name=integration_service_environment_name, integration_service_environment=integration_service_environment)


def logic_integration_service_environment_update(cmd, client,
                                                 resource_group,
                                                 integration_service_environment_name,
                                                 integration_service_environment):
    return client.begin_update(resource_group=resource_group, integration_service_environment_name=integration_service_environment_name, integration_service_environment=integration_service_environment)


def logic_integration_service_environment_delete(cmd, client,
                                                 resource_group,
                                                 integration_service_environment_name):
    return client.delete(resource_group=resource_group, integration_service_environment_name=integration_service_environment_name)


def logic_integration_service_environment_restart(cmd, client,
                                                  resource_group,
                                                  integration_service_environment_name):
    return client.restart(resource_group=resource_group, integration_service_environment_name=integration_service_environment_name)


def logic_integration_service_environment_sku_list(cmd, client,
                                                   resource_group,
                                                   integration_service_environment_name):
    return client.list(resource_group=resource_group, integration_service_environment_name=integration_service_environment_name)


def logic_integration_service_environment_network_health_show(cmd, client,
                                                              resource_group,
                                                              integration_service_environment_name):
    return client.get(resource_group=resource_group, integration_service_environment_name=integration_service_environment_name)


def logic_integration_service_environment_managed_api_list(cmd, client,
                                                           resource_group,
                                                           integration_service_environment_name):
    return client.list(resource_group=resource_group, integration_service_environment_name=integration_service_environment_name)


def logic_integration_service_environment_managed_api_show(cmd, client,
                                                           resource_group,
                                                           integration_service_environment_name,
                                                           api_name):
    return client.get(resource_group=resource_group, integration_service_environment_name=integration_service_environment_name, api_name=api_name)


def logic_integration_service_environment_managed_api_delete(cmd, client,
                                                             resource_group,
                                                             integration_service_environment_name,
                                                             api_name):
    return client.begin_delete(resource_group=resource_group, integration_service_environment_name=integration_service_environment_name, api_name=api_name)


def logic_integration_service_environment_managed_api_put(cmd, client,
                                                          resource_group,
                                                          integration_service_environment_name,
                                                          api_name):
    return client.begin_put(resource_group=resource_group, integration_service_environment_name=integration_service_environment_name, api_name=api_name)


def logic_integration_service_environment_managed_api_operation_list(cmd, client,
                                                                     resource_group,
                                                                     integration_service_environment_name,
                                                                     api_name):
    return client.list(resource_group=resource_group, integration_service_environment_name=integration_service_environment_name, api_name=api_name)
