# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines

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
