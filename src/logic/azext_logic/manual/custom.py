# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines, unused-argument, protected-access

from knack.util import CLIError
from azure.cli.core.aaz import has_value
from azext_logic.aaz.latest.logic.integration_account.map import Create as _MapCreate
from azext_logic.aaz.latest.logic.integration_account.map import Update as _MapUpdate


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
    if 'definition' not in definition:
        raise CLIError(str(definition) +
                       " does not contain a 'definition' key")
    workflow = {
        'location': location,
        'tags': tags,
        'state': state,
        'endpoints_configuration': endpoints_configuration,
        'access_control': definition.get(
            'accessControl', access_control),
        'integration_account': integration_account,
        'integration_service_environment': integration_service_environment,
        'definition': definition['definition'],
        'parameters': definition.get('parameters', None)
    }
    return client.create_or_update(resource_group_name=resource_group_name,
                                   workflow_name=name,
                                   workflow=workflow)


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


def logic_integration_account_create(cmd, client,
                                     resource_group_name,
                                     name,
                                     location=None,
                                     tags=None,
                                     sku=None,
                                     integration_service_environment=None,
                                     state=None):
    import json
    if isinstance(integration_service_environment, str):
        integration_service_environment = json.loads(
            integration_service_environment)
    integration_account = {
        'location': location,
        'tags': tags,
        'sku': {'name': sku},
        'integration_service_environment': integration_service_environment,
        'state': state if state else 'Enabled',
    }
    return client.create_or_update(resource_group_name=resource_group_name,
                                   integration_account_name=name,
                                   integration_account=integration_account)


def logic_integration_account_import(cmd, client,
                                     resource_group_name,
                                     name,
                                     input_path,
                                     location=None,
                                     tags=None,
                                     sku=None, ):
    if 'properties' not in input_path:
        raise CLIError(str(input_path) +
                       " does not contain a 'properties' key")

    integration_service_environment = input_path['properties'].get(
        'integrationServiceEnvironment', None)
    integration_account = {
        'location': input_path.get('location', location),
        'tags': input_path.get('tags', tags),
        'sku': input_path.get('sku', {'name': sku}),
        'integration_service_environment': integration_service_environment,
        'state': input_path['properties'].get('state', 'Enabled'),
    }
    return client.create_or_update(resource_group_name=resource_group_name,
                                   integration_account_name=name,
                                   integration_account=integration_account)


def logic_integration_account_update(cmd, client,
                                     name,
                                     resource_group_name,
                                     tags=None,
                                     sku=None,
                                     integration_service_environment=None,
                                     state=None):
    import json
    if isinstance(integration_service_environment, str):
        integration_service_environment = json.loads(
            integration_service_environment)
    integration_account = {
        'location': None,
        'tags': tags,
        'sku': {'name': sku},
        'integration_service_environment': integration_service_environment,
        'state': state,
    }
    return client.update(resource_group_name=resource_group_name,
                         integration_account_name=name,
                         integration_account=integration_account)


class MapCreate(_MapCreate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZFileArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.map_content = AAZFileArg(
            options=["--map-content"],
            help="The content.",
        )
        args_schema.content._registered = False
        return args_schema

    def pre_operations(self):
        args = self.ctx.args
        if has_value(args.map_content):
            args.content = args.map_content


class MapUpdate(_MapUpdate):
    @classmethod
    def _build_arguments_schema(cls, *args, **kwargs):
        from azure.cli.core.aaz import AAZFileArg
        args_schema = super()._build_arguments_schema(*args, **kwargs)
        args_schema.map_content = AAZFileArg(
            options=["--map-content"],
            help="The content.",
        )
        args_schema.content._registered = False
        return args_schema

    def pre_instance_update(self, instance):
        if has_value(self.ctx.args.content_type):
            return
        if instance.properties.map_type in ['Xslt', 'Xslt20', 'Xslt30']:
            instance.properties.content_type = 'application/xml'
        if instance.properties.map_type == 'Liquid':
            instance.properties.content_type = 'text/plain'
