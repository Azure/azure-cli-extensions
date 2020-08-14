# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.commands.parameters import get_location_type
from azure.cli.core.commands.validators import get_default_location_from_resource_group


def load_arguments(self, _):

    from azure.cli.core.commands.parameters import tags_type

    with self.argument_context('connectedk8s connect') as c:
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('cluster_name', options_list=['--name', '-n'], help='The name of the connected cluster.')
        c.argument('kube_config', options_list=['--kube-config'], help='Path to the kube config file.')
        c.argument('kube_context', options_list=['--kube-context'], help='Kubconfig context from current machine.')
        c.argument('https_proxy', options_list=['--proxy-https'], help='Https proxy URL to be used.')
        c.argument('http_proxy', options_list=['--proxy-http'], help='Http proxy URL to be used.')
        c.argument('no_proxy', options_list=['--proxy-skip-range'], help='List of URLs/CIDRs for which proxy should not to be used.')

    with self.argument_context('connectedk8s update') as c:
        c.argument('cluster_name', options_list=['--name', '-n'], id_part='name', help='The name of the connected cluster.')
        c.argument('kube_config', options_list=['--kube-config'], help='Path to the kube config file.')
        c.argument('kube_context', options_list=['--kube-context'], help='Kubconfig context from current machine.')
        c.argument('https_proxy', options_list=['--proxy-https'], help='Https proxy URL to be used.')
        c.argument('http_proxy', options_list=['--proxy-http'], help='Http proxy URL to be used.')
        c.argument('no_proxy', options_list=['--proxy-skip-range'], help='List of URLs/CIDRs for which proxy should not to be used.')

    with self.argument_context('connectedk8s list') as c:
        pass

    with self.argument_context('connectedk8s show') as c:
        c.argument('cluster_name', options_list=['--name', '-n'], id_part='name', help='The name of the connected cluster.')

    with self.argument_context('connectedk8s delete') as c:
        c.argument('cluster_name', options_list=['--name', '-n'], id_part='name', help='The name of the connected cluster.')
        c.argument('kube_config', options_list=['--kube-config'], help='Path to the kube config file.')
        c.argument('kube_context', options_list=['--kube-context'], help='Kubconfig context from current machine.')
