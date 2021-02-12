# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from argcomplete.completers import FilesCompleter
from azure.cli.core.commands.parameters import get_location_type, get_enum_type
from azure.cli.core.commands.parameters import (file_type)
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from azext_connectedk8s._constants import Distribution_Enum_Values, Infrastructure_Enum_Values


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
        c.argument('proxy_cert', options_list=['--proxy-cert'], type=file_type, completer=FilesCompleter(), help='Path to the certificate file for proxy')
        c.argument('distribution', options_list=['--distribution'], help='The Kubernetes distribution which will be running on this connected cluster.', arg_type=get_enum_type(Distribution_Enum_Values))
        c.argument('infrastructure', options_list=['--infrastructure'], help='The infrastructure on which the Kubernetes cluster represented by this connected cluster will be running on.', arg_type=get_enum_type(Infrastructure_Enum_Values))
        c.argument('disable_auto_upgrade', options_list=['--disable-auto-upgrade'], action='store_true', help='Flag to disable auto upgrade of arc agents.')
        c.argument('enable_azure_rbac', options_list=['--enable-azure-rbac'], action='store_true', help='Enable azure rbac for authorization', is_preview=True)
        c.argument('guard_client_id', options_list=['--client-id'], help='Client id for the Guard Authorization webhook. Specify when using enable-azure-rbac.', is_preview=True)
        c.argument('guard_client_secret', options_list=['--client-secret'], help='Client secret for the Guard Authorization webhook. Specify when using enable-azure-rbac.', is_preview=True)

    with self.argument_context('connectedk8s update') as c:
        c.argument('cluster_name', options_list=['--name', '-n'], id_part='name', help='The name of the connected cluster.')
        c.argument('kube_config', options_list=['--kube-config'], help='Path to the kube config file.')
        c.argument('kube_context', options_list=['--kube-context'], help='Kubconfig context from current machine.')
        c.argument('https_proxy', options_list=['--proxy-https'], help='Https proxy URL to be used.')
        c.argument('http_proxy', options_list=['--proxy-http'], help='Http proxy URL to be used.')
        c.argument('no_proxy', options_list=['--proxy-skip-range'], help='List of URLs/CIDRs for which proxy should not to be used.')
        c.argument('proxy_cert', options_list=['--proxy-cert'], type=file_type, completer=FilesCompleter(), help='Path to the certificate file for proxy')
        c.argument('disable_proxy', options_list=['--disable-proxy'], action='store_true', help='Disables proxy settings for agents')
        c.argument('auto_upgrade', options_list=['--auto-upgrade'], help='Flag to enable/disable auto upgrade of arc agents. By default, auto upgrade of agents is enabled.', arg_type=get_enum_type(["true", "false"]))
        c.argument('azure_rbac', options_list=['--azure-rbac'], help='Flag to enable/disable azure rbac for authorization', is_preview=True)
        c.argument('guard_client_id', options_list=['--client-id'], help='Client id for the Guard Authorization webhook. Specify when enabling azure-rbac.', is_preview=True)
        c.argument('guard_client_secret', options_list=['--client-secret'], help='Client secret for the Guard Authorization webhook. Specify when enabling azure-rbac.', is_preview=True)

    with self.argument_context('connectedk8s upgrade') as c:
        c.argument('cluster_name', options_list=['--name', '-n'], id_part='name', help='The name of the connected cluster.')
        c.argument('kube_config', options_list=['--kube-config'], help='Path to the kube config file.')
        c.argument('kube_context', options_list=['--kube-context'], help='Kubconfig context from current machine.')
        c.argument('arc_agent_version', options_list=['--agent-version'], help='Version of agent to update the helm charts to.')

    with self.argument_context('connectedk8s list') as c:
        pass

    with self.argument_context('connectedk8s show') as c:
        c.argument('cluster_name', options_list=['--name', '-n'], id_part='name', help='The name of the connected cluster.')

    with self.argument_context('connectedk8s delete') as c:
        c.argument('cluster_name', options_list=['--name', '-n'], id_part='name', help='The name of the connected cluster.')
        c.argument('kube_config', options_list=['--kube-config'], help='Path to the kube config file.')
        c.argument('kube_context', options_list=['--kube-context'], help='Kubconfig context from current machine.')
