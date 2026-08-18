# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
from azure.cli.core.commands.parameters import (
    tags_type,
    get_location_type,
    get_enum_type,
    get_resource_name_completion_list,
)
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from azext_aimanager.constants import (
    DELETE_POLICIES,
    MODEL_DEPLOYMENT_PERFORMANCE_MODES,
    MODEL_SOURCE_TYPES,
)
from azext_aimanager._validators import (
    validate_ai_manager_name,
    validate_namespace_name,
    validate_model_deployment_name,
    validate_ai_model_name,
    validate_model_source_name,
    validate_labels,
    validate_annotations,
    validate_overrides,
)


def load_arguments(self, _):
    with self.argument_context('aimanager') as c:
        c.argument('ai_manager_name', options_list=['--name', '-n'],
                   validator=validate_ai_manager_name,
                   help='The name of the AI Manager resource.',
                   completer=get_resource_name_completion_list('Microsoft.ContainerService/aiManagers'))

    for scope in ['aimanager create', 'aimanager update']:
        with self.argument_context(scope) as c:
            c.argument('tags', arg_type=tags_type, help='The tags to set to the AI Manager.')
            c.argument('delete_policy', arg_type=get_enum_type(DELETE_POLICIES),
                       help='Delete options of the AI Manager. Defaults to Delete.')
            c.argument('aks_custom_headers', options_list=['--aks-custom-headers'],
                       help='Comma-separated key=value pairs to specify custom headers.')

    with self.argument_context('aimanager create') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx),
                   validator=get_default_location_from_resource_group)

    with self.argument_context('aimanager list') as c:
        c.ignore('ai_manager_name')

    with self.argument_context('aimanager get-credentials') as c:
        c.argument('path', options_list=['--file', '-f'],
                   help='Kubernetes configuration file to update. Use "-" to print YAML to stdout instead.')
        c.argument('overwrite_existing', action='store_true',
                   help='Overwrite any existing cluster entry with the same name.')
        c.argument('context_name',
                   help='If specified, overwrite the default context name.')
        c.argument('aks_custom_headers', options_list=['--aks-custom-headers'],
                   help='Comma-separated key=value pairs to specify custom headers.')

    with self.argument_context('aimanager modelsource') as c:
        c.argument('ai_manager_name', options_list=['--aimanager-name'],
                   validator=validate_ai_manager_name,
                   help='The name of the AI Manager resource.')
        c.argument('model_source_name', options_list=['--name', '-n'],
                   validator=validate_model_source_name,
                   help='The name of the model source.')

    with self.argument_context('aimanager modelsource list') as c:
        c.ignore('model_source_name')

    with self.argument_context('aimanager modelsource add') as c:
        c.argument('source_type', options_list=['--source-type', '-s'], required=True,
                   arg_type=get_enum_type(MODEL_SOURCE_TYPES),
                   help='The type of the model source. Immutable after creation.')

    for scope in ['aimanager modelsource add', 'aimanager modelsource update']:
        with self.argument_context(scope) as c:
            c.argument('description',
                       help='An optional, free-form description of the model source.')
            c.argument('token',
                       help='Access token used by the platform to authenticate to the source. '
                            'Optional for public sources such as ungated Hugging Face models.')
            c.argument('aks_custom_headers', options_list=['--aks-custom-headers'],
                       help='Comma-separated key=value pairs to specify custom headers.')

    with self.argument_context('aimanager namespace') as c:
        c.argument('ai_manager_name', options_list=['--aimanager-name', '--manager', '-m'],
                   validator=validate_ai_manager_name,
                   help='The name of the AI Manager resource.')
        c.argument('namespace_name', options_list=['--name', '-n'],
                   validator=validate_namespace_name,
                   help='The name of the AI Manager namespace.')

    for scope in ['aimanager namespace add', 'aimanager namespace update']:
        with self.argument_context(scope) as c:
            c.argument('labels', nargs='*', validator=validate_labels,
                       help='Space-separated labels (key=value) applied to the Kubernetes namespace.')
            c.argument('annotations', nargs='*', validator=validate_annotations,
                       help='Space-separated annotations (key=value) applied to the Kubernetes namespace.')
            c.argument('aks_custom_headers', options_list=['--aks-custom-headers'],
                       help='Comma-separated key=value pairs to specify custom headers.')

    with self.argument_context('aimanager namespace get-credentials') as c:
        c.argument('path', options_list=['--file', '-f'],
                   help='Kubernetes configuration file to update. Use "-" to print YAML to stdout instead.')
        c.argument('overwrite_existing', action='store_true',
                   help='Overwrite any existing cluster entry with the same name.')
        c.argument('context_name',
                   help='If specified, overwrite the default context name.')
        c.argument('aks_custom_headers', options_list=['--aks-custom-headers'],
                   help='Comma-separated key=value pairs to specify custom headers.')

    for scope in ['aimanager namespace list-accesskeys', 'aimanager namespace rotate-accesskeys']:
        with self.argument_context(scope) as c:
            c.argument('aks_custom_headers', options_list=['--aks-custom-headers'],
                       help='Comma-separated key=value pairs to specify custom headers.')

    with self.argument_context('aimanager namespace modeldeployment') as c:
        c.argument('ai_manager_name', options_list=['--aimanager-name'],
                   validator=validate_ai_manager_name,
                   help='The name of the AI Manager resource.')
        c.argument('namespace_name', options_list=['--namespace-name'],
                   validator=validate_namespace_name,
                   help='The name of the AI Manager namespace.')
        c.argument('model_deployment_name', options_list=['--name', '-n'],
                   validator=validate_model_deployment_name,
                   help='The name of the model deployment.')

    with self.argument_context('aimanager namespace modeldeployment list') as c:
        c.ignore('model_deployment_name')

    with self.argument_context('aimanager namespace modeldeployment add') as c:
        c.argument('model_resource_id', options_list=['--model-resource-id'], required=True,
                   help='The full ARM resource ID of the AI model to deploy.')
        c.argument('model_source_resource_id', options_list=['--model-source-resource-id', '--source-id'],
                   help='The full ARM resource ID of the model source used to pull artifacts.')
        c.argument('vm_size', options_list=['--vm-size', '-s'], required=True,
                   help='The Azure VM SKU used to host the deployment.')

    for scope in ['aimanager namespace modeldeployment add',
                  'aimanager namespace modeldeployment update']:
        with self.argument_context(scope) as c:
            c.argument('performance_mode', arg_type=get_enum_type(MODEL_DEPLOYMENT_PERFORMANCE_MODES),
                       help='Runtime performance mode.')
            c.argument('replicas', type=int,
                       help='Fixed replica count. Cannot be combined with autoscale arguments.')
            c.argument('min_replicas', type=int,
                       help='Minimum autoscale replica count. Must be at least 1.')
            c.argument('max_replicas', type=int,
                       help='Maximum autoscale replica count.')
            c.argument('overrides', nargs='*', validator=validate_overrides,
                       help='Space-separated experimental deployment overrides (key=value).')
            c.argument('aks_custom_headers', options_list=['--aks-custom-headers'],
                       help='Comma-separated key=value pairs to specify custom headers.')

    with self.argument_context('aimanager model') as c:
        c.argument('location', arg_type=get_location_type(self.cli_ctx), required=True,
                   help='The Azure region hosting the AI model catalog.')
        c.argument('ai_model_name', options_list=['--name', '-n'],
                   validator=validate_ai_model_name,
                   help='The name of the AI model. This is an opaque, stable identifier derived '
                        'from the model ID; use "az aimanager model list" to discover it.')

    with self.argument_context('aimanager model list') as c:
        c.ignore('ai_model_name')
