# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines, too-many-locals, too-many-branches, too-many-statements

import uuid
from azure.cli.core.util import sdk_no_wait


def _uuid():
    return str(uuid.uuid4())


def automation_account_list(client, resource_group_name=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list()


def automation_account_show(client, resource_group_name, automation_account_name):
    return client.get(resource_group_name=resource_group_name, automation_account_name=automation_account_name)


def automation_account_delete(client, resource_group_name, automation_account_name):
    return client.delete(resource_group_name=resource_group_name, automation_account_name=automation_account_name)


def automation_account_create(client, resource_group_name, automation_account_name, location=None, tags=None,
                              sku="Basic"):
    parameters = {}
    parameters['name'] = automation_account_name
    parameters['location'] = location
    parameters['tags'] = tags
    parameters['sku'] = {'name': sku}
    return client.create_or_update(resource_group_name=resource_group_name,
                                   automation_account_name=automation_account_name,
                                   parameters=parameters)


def automation_account_update(client, resource_group_name, automation_account_name, tags=None, sku=None):
    parameters = {}
    parameters['name'] = automation_account_name
    parameters['tags'] = tags
    if sku is None:
        account = client.get(resource_group_name=resource_group_name, automation_account_name=automation_account_name)
        sku = account.sku.name
    parameters['sku'] = {'name': sku}
    return client.update(resource_group_name=resource_group_name, automation_account_name=automation_account_name,
                         parameters=parameters)


def automation_runbook_draft_replace_content(client, resource_group_name, automation_account_name, name, content,
                                             no_wait=False):
    return sdk_no_wait(no_wait, client.begin_replace_content, resource_group_name=resource_group_name,
                       automation_account_name=automation_account_name, runbook_name=name, runbook_content=content)


def automation_runbook_draft_undo_edit(client, resource_group_name, automation_account_name, name):
    return client.undo_edit(resource_group_name=resource_group_name, automation_account_name=automation_account_name,
                            runbook_name=name)


def automation_runbook_start(client, resource_group_name, automation_account_name, name=None,
                             properties_parameters=None, run_on=None):
    parameters = {}
    parameters['parameters'] = properties_parameters
    parameters['run_on'] = run_on
    parameters['runbook'] = {}
    parameters['runbook']['name'] = name
    job_name = _uuid()
    return client.create(resource_group_name=resource_group_name,
                         automation_account_name=automation_account_name,
                         job_name=job_name,
                         parameters=parameters)


def automation_runbook_create(client, resource_group_name, automation_account_name, name, runbook_type, location=None,
                              tags=None, log_verbose=None, log_progress=None, description=None,
                              log_activity_trace=None):
    parameters = {}
    parameters['name'] = name
    parameters['location'] = location
    parameters['tags'] = tags
    parameters['log_verbose'] = log_verbose
    parameters['log_progress'] = log_progress
    parameters['runbook_type'] = runbook_type
    parameters['description'] = description
    parameters['log_activity_trace'] = log_activity_trace
    parameters['draft'] = {}
    return client.create_or_update(resource_group_name=resource_group_name,
                                   automation_account_name=automation_account_name,
                                   runbook_name=name,
                                   parameters=parameters)


def automation_runbook_update(client, resource_group_name, automation_account_name, name, tags=None, description=None,
                              log_verbose=None, log_progress=None, log_activity_trace=None):
    parameters = {}
    parameters['tags'] = tags
    parameters['description'] = description
    parameters['log_verbose'] = log_verbose
    parameters['log_progress'] = log_progress
    parameters['log_activity_trace'] = log_activity_trace
    return client.update(resource_group_name=resource_group_name, automation_account_name=automation_account_name,
                         runbook_name=name, parameters=parameters)


def automation_job_list(client, resource_group_name, automation_account_name):
    return client.list_by_automation_account(resource_group_name=resource_group_name,
                                             automation_account_name=automation_account_name)


def automation_job_show(client, resource_group_name, automation_account_name, job_name):
    return client.get(resource_group_name=resource_group_name, automation_account_name=automation_account_name,
                      job_name=job_name)


def automation_job_get_output(client, resource_group_name, automation_account_name, job_name):
    return client.get_output(resource_group_name=resource_group_name, automation_account_name=automation_account_name,
                             job_name=job_name)


def automation_job_resume(client, resource_group_name, automation_account_name, job_name):
    return client.resume(resource_group_name=resource_group_name, automation_account_name=automation_account_name,
                         job_name=job_name)


def automation_job_stop(client, resource_group_name, automation_account_name, job_name):
    return client.stop(resource_group_name=resource_group_name, automation_account_name=automation_account_name,
                       job_name=job_name)


def automation_job_suspend(client, resource_group_name, automation_account_name, job_name):
    return client.suspend(resource_group_name=resource_group_name, automation_account_name=automation_account_name,
                          job_name=job_name)


def automation_schedule_list(client, resource_group_name, automation_account_name):
    return client.list_by_automation_account(resource_group_name, automation_account_name)


def automation_schedule_show(client, resource_group_name, automation_account_name, schedule_name):
    return client.get(resource_group_name, automation_account_name, schedule_name)


def automation_schedule_create(client, resource_group_name, automation_account_name, schedule_name, frequency, interval,
                               start_time=None, description=None, expiry_time=None, time_zone=None):
    parameters = {}
    parameters['name'] = schedule_name
    parameters['frequency'] = frequency
    parameters['interval'] = interval
    if start_time is not None:
        parameters['startTime'] = start_time
    if description is not None:
        parameters['description'] = description
    if expiry_time is not None:
        parameters['expiryTime'] = expiry_time
    if time_zone is not None:
        parameters['timeZone'] = time_zone

    return client.create_or_update(resource_group_name, automation_account_name, schedule_name, parameters)


def automation_schedule_update(client, resource_group_name, automation_account_name, schedule_name, description=None,
                               is_enabled=None):
    parameters = {'properties': {}}
    parameters['name'] = schedule_name
    if is_enabled is not None:
        parameters['properties']['isEnabled'] = is_enabled
    if description is not None:
        parameters['properties']['description'] = description

    return client.update(resource_group_name, automation_account_name, schedule_name, parameters)


def automation_schedule_delete(client, resource_group_name, automation_account_name, schedule_name):
    return client.delete(resource_group_name, automation_account_name, schedule_name)


def automation_software_update_configuration_list(client, resource_group_name, automation_account_name):
    return client.list(resource_group_name, automation_account_name)


def automation_software_update_configuration_show(client, resource_group_name, automation_account_name,
                                                  software_update_configuration_name):
    return client.get_by_name(resource_group_name, automation_account_name,
                              software_update_configuration_name)


def automation_software_update_configuration_create(client, resource_group_name, automation_account_name,
                                                    software_update_configuration_name, frequency, interval,
                                                    operating_system, included_update_classifications=None,
                                                    excluded_kb_numbers=None, included_kb_numbers=None,
                                                    reboot_setting=None, duration=None, azure_virtual_machines=None,
                                                    non_azure_computer_names=None, azure_queries_scope=None,
                                                    azure_queries_locations=None, non_azure_queries_function_alias=None,
                                                    non_azure_queries_workspace_id=None, azure_queries_tags=None,
                                                    start_time=None, expiry_time=None, time_zone=None,
                                                    expiry_time_offset_minutes=None, is_enabled=None, next_run=None,
                                                    next_run_offset_minutes=None, creation_time=None,
                                                    last_modified_time=None, description=None, pre_task_status=None,
                                                    pre_task_source=None, pre_task_job_id=None, post_task_status=None,
                                                    post_task_source=None, post_task_job_id=None):
    parameters = {}
    update_configuration = {}
    update_configuration['operatingSystem'] = operating_system
    if operating_system == 'Windows':
        windows = {}
        if included_update_classifications is not None:
            windows['includedUpdateClassifications'] = included_update_classifications
        if excluded_kb_numbers is not None:
            windows['excludedKbNumbers'] = excluded_kb_numbers
        if included_kb_numbers is not None:
            windows['includedKbNumbers'] = included_kb_numbers
        if reboot_setting is not None:
            windows['rebootSetting'] = reboot_setting
        update_configuration['windows'] = windows
    if operating_system == 'Linux':
        linux = {}
        if included_update_classifications is not None:
            linux['includedUpdateClassifications'] = included_update_classifications
        if excluded_kb_numbers is not None:
            linux['excludedKbNumbers'] = excluded_kb_numbers
        if included_kb_numbers is not None:
            linux['includedKbNumbers'] = included_kb_numbers
        if reboot_setting is not None:
            linux['rebootSetting'] = reboot_setting
        update_configuration['linux'] = linux
    if duration is not None:
        update_configuration['duration'] = duration
    if azure_virtual_machines is not None:
        update_configuration['azureVirtualMachines'] = azure_virtual_machines
    if non_azure_computer_names:
        update_configuration['nonAzureComputerNames'] = non_azure_computer_names

    targets = {}
    azure_queries = {}
    if azure_queries_scope is not None:
        azure_queries['scope'] = azure_queries_scope
    if azure_queries_locations is not None:
        azure_queries['locations'] = azure_queries_locations
    if azure_queries_tags is not None:
        azure_queries['tagSettings'] = {'tags': {'tag': azure_queries_tags}}
    if azure_queries:
        targets['azureQueries'] = [azure_queries]

    non_azure_queries = {}
    if non_azure_queries_function_alias is not None:
        non_azure_queries['functionAlias'] = non_azure_queries_function_alias
    if non_azure_queries_workspace_id is not None:
        non_azure_queries['workspaceId'] = non_azure_queries_workspace_id
    if non_azure_queries:
        targets['nonAzureQueries'] = [non_azure_queries]

    if targets:
        update_configuration['targets'] = targets
    if update_configuration:
        parameters['updateConfiguration'] = update_configuration

    schedule_info = {}
    if start_time is not None:
        schedule_info['startTime'] = start_time
    if expiry_time is not None:
        schedule_info['expiryTime'] = expiry_time
    if expiry_time_offset_minutes is not None:
        schedule_info['expiryTimeOffsetMinutes'] = expiry_time_offset_minutes
    if is_enabled is not None:
        schedule_info['isEnabled'] = is_enabled
    if next_run is not None:
        schedule_info['nextRun'] = next_run
    if next_run_offset_minutes is not None:
        schedule_info['nextRunOffsetMinutes'] = next_run_offset_minutes
    if interval is not None:
        schedule_info['interval'] = interval
    if frequency is not None:
        schedule_info['frequency'] = frequency
    if time_zone is not None:
        schedule_info['timeZone'] = time_zone
    if creation_time is not None:
        schedule_info['creationTime'] = creation_time
    if last_modified_time is not None:
        schedule_info['lastModifiedTime'] = last_modified_time
    if description is not None:
        schedule_info['description'] = description
    if schedule_info:
        parameters['scheduleInfo'] = schedule_info

    tasks = {}
    pre_task = {}
    if pre_task_status is not None:
        pre_task['status'] = pre_task_status
    if pre_task_source is not None:
        pre_task['source'] = pre_task_source
    if pre_task_status is not None:
        pre_task['jobId'] = pre_task_job_id
    post_task = {}
    if post_task_status is not None:
        post_task['status'] = post_task_status
    if post_task_source is not None:
        post_task['source'] = post_task_source
    if post_task_status is not None:
        post_task['jobId'] = post_task_job_id

    if pre_task:
        tasks['preTask'] = pre_task
    if post_task:
        tasks['postTask'] = post_task
    if tasks:
        parameters['tasks'] = tasks

    return client.create(resource_group_name, automation_account_name, software_update_configuration_name, parameters)


def automation_software_update_configuration_delete(client, resource_group_name, automation_account_name,
                                                    software_update_configuration_name):
    return client.delete(resource_group_name, automation_account_name,
                         software_update_configuration_name)


def automation_software_update_configuration_runs_list(client, resource_group_name, automation_account_name):
    return client.list(resource_group_name, automation_account_name)


def automation_software_update_configuration_runs_show(client, resource_group_name, automation_account_name,
                                                       software_update_configuration_run_id):
    return client.get_by_id(resource_group_name, automation_account_name, software_update_configuration_run_id)


def automation_software_update_configuration_machine_runs_list(client, resource_group_name, automation_account_name):
    return client.list(resource_group_name, automation_account_name)


def automation_software_update_configuration_machine_runs_show(client, resource_group_name, automation_account_name,
                                                               software_update_configuration_machine_run_id):
    return client.get_by_id(resource_group_name, automation_account_name, software_update_configuration_machine_run_id)
