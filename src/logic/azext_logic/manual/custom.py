# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError


def logic_workflow_update(cmd,
                          client,
                          resource_group_name,
                          name,
                          definition=None,
                          tags=None,
                          state=None):

    from azure.cli.core.azclierror import ValidationError

    if definition is not None and "definition" not in definition:
        raise ValidationError(str(definition) + " does not contain a 'definition' key")

    workflow = client.get(resource_group_name=resource_group_name, workflow_name=name)

    from ..generated.custom import logic_workflow_create
    return logic_workflow_create(
        cmd,
        client,
        resource_group_name,
        name,
        definition=definition if definition else {"definition": workflow.definition},
        location=workflow.location,
        tags=tags if tags else workflow.tags,
        state=state if state else workflow.state,
        endpoints_configuration=workflow.endpoints_configuration,
        integration_account=workflow.integration_account,
        integration_service_environment=workflow.integration_service_environment,
    )
