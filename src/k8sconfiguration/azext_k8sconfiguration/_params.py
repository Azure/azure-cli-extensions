# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType

from azure.cli.core.commands.parameters import (
    get_three_state_flag,
    get_enum_type,
    tags_type
)

from azure.cli.core.commands.validators import get_default_location_from_resource_group
from ._validators import validate_configuration_type


def load_arguments(self, _):
    sourcecontrolconfiguration_type = CLIArgumentType(help='Name of the K8sconfiguration.')

    with self.argument_context('k8sconfiguration') as c:
        c.argument('tags', tags_type)
        c.argument('location', validator=get_default_location_from_resource_group)
        c.argument('name', sourcecontrolconfiguration_type, options_list=['--name', '-n'])
        c.argument('cluster_name', options_list=['--cluster-name', '-c'], help='Name of the Kubernetes cluster')
        c.argument('cluster_type', arg_type=get_enum_type(['connectedClusters', 'managedClusters']),
                   help='Optional parameter to specify Onprem clusters (default) or AKS clusters.')
        c.argument('repository_url', options_list=['--repository-url', '-u'],
                   help='Url of the sourceControl repository')
        c.argument('enable_helm_operator', arg_type=get_three_state_flag(),
                   help='Enable support for Helm chart deployments')
        c.argument('cluster_scoped', action='store_true',
                   help='''Optional switch to set scope of the operator to be cluster. Default scope is 'namespace'.''')
        c.argument('configuration_type', validator=validate_configuration_type,
                   arg_type=get_enum_type(['sourceControlConfiguration']),
                   help='Type of the configuration')
        c.argument('helm_operator_params',
                   help='Optional. Chart values for the Helm Operator (if enabled)')
        c.argument('helm_operator_version',
                   help='''Optional. Chart version of the Helm Operator, if enabled.  Default:'0.2.0'.''')
        c.argument('operator_params',
                   help='Optional. Parameters for the Operator.')
        c.argument('operator_instance_name',
                   help='Instance name of the Operator.')
        c.argument('operator_namespace',
                   help='Namespace in which to install the Operator.')
        c.argument('operator_type',
                   help='''Optional. Type of the operator. Valid value is 'flux'.''')
        c.argument('',
                   help='')

    with self.argument_context('k8sconfiguration list') as c:
        c.argument('sourcecontrolconfiguration', sourcecontrolconfiguration_type, id_part=None)
