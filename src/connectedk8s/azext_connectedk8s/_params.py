# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType


def load_arguments(self, _):

    from azure.cli.core.commands.parameters import tags_type, get_resource_name_completion_list, name_type

    #cluster_name_type = CLIArgumentType(options_list='--cluster-name-name', help='Name of the Connected Kubernetes Cluster.', id_part='name')

    with self.argument_context('connectedk8s') as c:
        c.argument('resource_group_name', name_type, help='Name of the resource group.',
                   completer=get_resource_name_completion_list('Microsoft.Kubernetes/ConnectedClusters'), options_list=['--resource-group', '-g'])
        c.argument('tags', tags_type)
        c.argument('cluster_name', name_type, help='Name of the connected cluster.', 
                   completer=get_resource_name_completion_list('Microsoft.Kubernetes/ConnectedClusters'), options_list=['--name', '-n'])

    #with self.argument_context('connectedk8s list') as c:
    #    c.argument('cluster_name', cluster_name_type, id_part=None, options_list=['--name', '-n'])
