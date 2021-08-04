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
from ._validators import _validate_configuration_type, _validate_operator_namespace, _validate_operator_instance_name


def load_arguments(self, _):
    sourcecontrolconfiguration_type = CLIArgumentType(help='Name of the Kubernetes Configuration')

    with self.argument_context('k8s-configuration') as c:
        c.argument('tags', tags_type)
        c.argument('location',
                   validator=get_default_location_from_resource_group)
        c.argument('name', sourcecontrolconfiguration_type,
                   options_list=['--name', '-n'])
        c.argument('cluster_name',
                   options_list=['--cluster-name', '-c'],
                   help='Name of the Kubernetes cluster')
        c.argument('cluster_type',
                   arg_type=get_enum_type(['connectedClusters', 'managedClusters']),
                   help='Specify Arc clusters or AKS managed clusters.')
        c.argument('repository_url',
                   options_list=['--repository-url', '-u'],
                   help='Url of the source control repository')
        c.argument('scope',
                   arg_type=get_enum_type(['namespace', 'cluster']),
                   help='''Specify scope of the operator to be 'namespace' or 'cluster' ''')
        c.argument('configuration_type',
                   validator=_validate_configuration_type,
                   arg_type=get_enum_type(['sourceControlConfiguration']),
                   help='Type of the configuration')
        c.argument('enable_helm_operator',
                   arg_group="Helm Operator",
                   arg_type=get_three_state_flag(),
                   options_list=['--enable-helm-operator', '--enable-hop'],
                   help='Enable support for Helm chart deployments')
        c.argument('helm_operator_params',
                   arg_group="Helm Operator",
                   options_list=['--helm-operator-params', '--hop-params'],
                   help='Chart values for the Helm Operator (if enabled)')
        c.argument('helm_operator_chart_version',
                   arg_group="Helm Operator",
                   options_list=['--helm-operator-chart-version', '--hop-chart-version'],
                   help='Chart version of the Helm Operator (if enabled)')
        c.argument('operator_params',
                   arg_group="Operator",
                   help='Parameters for the Operator')
        c.argument('operator_instance_name',
                   arg_group="Operator",
                   help='Instance name of the Operator',
                   validator=_validate_operator_instance_name)
        c.argument('operator_namespace',
                   arg_group="Operator",
                   help='Namespace in which to install the Operator',
                   validator=_validate_operator_namespace)
        c.argument('operator_type',
                   arg_group="Operator",
                   help='''Type of the operator. Valid value is 'flux' ''')
        c.argument('ssh_private_key',
                   arg_group="Auth",
                   help='Specify Base64-encoded private ssh key for private repository sync')
        c.argument('ssh_private_key_file',
                   arg_group="Auth",
                   help='Specify filepath to private ssh key for private repository sync')
        c.argument('https_user',
                   arg_group="Auth",
                   help='Specify HTTPS username for private repository sync')
        c.argument('https_key',
                   arg_group="Auth",
                   help='Specify HTTPS token/password for private repository sync')
        c.argument('ssh_known_hosts',
                   arg_group="Auth",
                   help='Specify Base64-encoded known_hosts contents containing public SSH keys required to access private Git instances')
        c.argument('ssh_known_hosts_file',
                   arg_group="Auth",
                   help='Specify filepath to known_hosts contents containing public SSH keys required to access private Git instances')
