# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-many-lines

import json
from knack.util import CLIError


def logic_workflow_list(cmd, client,
                        resource_group_name=None,
                        top=None,
                        filter=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name=resource_group_name,
                                             top=top,
                                             filter=filter)
    return client.list_by_subscription(top=top,
                                       filter=filter)


def logic_workflow_show(cmd, client,
                        resource_group_name,
                        name):
    return client.get(resource_group_name=resource_group_name,
                      workflow_name=name)


def logic_workflow_create(cmd, client,
                          resource_group_name,
                          name,
                          definition,
                          location,
                          tags=None,
                          state=None,
                          endpoints_configuration=None,
                          access_control=None,
                          integration_account=None,
                          integration_service_environment=None):
    with open(definition) as json_file:
        try:
            workflow = json.load(json_file)
        except json.decoder.JSONDecodeError as ex:
            raise CLIError(
                'JSON decode error for {}: {}'.format(json_file, str(ex)))
        if 'definition' not in workflow:
            raise CLIError(str(json_file) +
                           " does not contain a 'definition' key")

        return client.create_or_update(resource_group_name=resource_group_name,
                                       workflow_name=name,
                                       location=location,
                                       tags=tags,
                                       state=state,
                                       endpoints_configuration=endpoints_configuration,
                                       access_control=workflow.get(
                                           'accessControl', access_control),
                                       integration_account=integration_account,
                                       integration_service_environment=integration_service_environment,
                                       definition=workflow['definition'],
                                       parameters=workflow.get('parameters', None))


def logic_workflow_update(cmd, client,
                          resource_group_name,
                          name,
                          definition,
                          tags=None,
                          state=None,
                          endpoints_configuration=None,
                          integration_account=None):

    # check workflow exist before another update is done via a put
    # per dicussion with the logic service team and to match powershells
    # behavior
    workflow = client.get(resource_group_name=resource_group_name,
                          workflow_name=name)
    integration_account = integration_account if integration_account else workflow.integration_account
    endpoints_configuration = endpoints_configuration if endpoints_configuration else workflow.endpoints_configuration
    return logic_workflow_create(cmd, client, resource_group_name, name,
                                 definition, workflow.location,
                                 tags if tags else workflow.tags,
                                 state,
                                 endpoints_configuration,
                                 integration_account,
                                 workflow.integration_service_environment)


def logic_workflow_delete(cmd, client,
                          resource_group_name,
                          name):
    return client.delete(resource_group_name=resource_group_name,
                         workflow_name=name)


def logic_integration_account_list(cmd, client,
                                   resource_group_name=None,
                                   top=None):
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name=resource_group_name,
                                             top=top)
    return client.list_by_subscription(top=top)


def logic_integration_account_show(cmd, client,
                                   resource_group_name,
                                   name):
    return client.get(resource_group_name=resource_group_name,
                      integration_account_name=name)


def logic_integration_account_create(cmd, client,
                                     resource_group_name,
                                     name,
                                     location=None,
                                     tags=None,
                                     sku=None,
                                     integration_service_environment=None,
                                     state=None):
    if isinstance(integration_service_environment, str):
        integration_service_environment = json.loads(
            integration_service_environment)
    return client.create_or_update(resource_group_name=resource_group_name,
                                   integration_account_name=name,
                                   location=location,
                                   tags=tags,
                                   sku=sku,
                                   integration_service_environment=integration_service_environment,
                                   state=state if state else 'Enabled')
    # TODO: Work around for empty property serialization issue.
    # Remove after LogicApp deploy the service fix. Contact: Rama Rayud"


def logic_integration_account_import(cmd, client,
                                     resource_group_name,
                                     name,
                                     input_path,
                                     location=None,
                                     tags=None,
                                     sku=None,):
    with open(input_path) as integrationJson:
        try:
            integration = json.load(integrationJson)
        except json.decoder.JSONDecodeError as ex:
            raise CLIError('JSON decode error for {}: {}'.format(
                integrationJson, str(ex)))
        if 'properties' not in integration:
            raise CLIError(str(integrationJson) +
                           " does not contain a 'properties' key")

        integration_service_environment = integration['properties'].get(
            'integrationServiceEnvironment', None)
        return client.create_or_update(resource_group_name=resource_group_name,
                                       integration_account_name=name,
                                       location=integration.get(
                                           'location', location),
                                       tags=integration.get('tags', tags),
                                       sku=integration.get('sku', sku),
                                       integration_service_environment=integration_service_environment,
                                       state=integration['properties'].get('state', 'Enabled'))
        # TODO: Work around for empty property serialization issue.
        # Remove after LogicApp deploy the service fix. Contact: Rama Rayud"


def logic_integration_account_update(cmd, client,
                                     name,
                                     resource_group_name,
                                     tags=None,
                                     sku=None,
                                     integration_service_environment=None,
                                     state=None):

    if isinstance(integration_service_environment, str):
        integration_service_environment = json.loads(
            integration_service_environment)
    return client.update(resource_group_name=resource_group_name,
                         integration_account_name=name,
                         location=None,
                         tags=tags,
                         sku=sku,
                         integration_service_environment=integration_service_environment,
                         state=state)


def logic_integration_account_delete(cmd, client,
                                     resource_group_name,
                                     name):
    return client.delete(resource_group_name=resource_group_name,
                         integration_account_name=name)
