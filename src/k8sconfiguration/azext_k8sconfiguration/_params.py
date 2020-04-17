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


def load_arguments(self, _):
    # sourcecontrolconfiguration_type = CLIArgumentType(options_list='--sourcecontrolconfiguration-name',
    # help='Name of the K8sconfiguration.', id_part='name')
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
                   help='''Optional switch to set the scope of the operator to be cluster. Default scope is 'namespace' ''')

    with self.argument_context('k8sconfiguration list') as c:
        c.argument('sourcecontrolconfiguration', sourcecontrolconfiguration_type, id_part=None)
