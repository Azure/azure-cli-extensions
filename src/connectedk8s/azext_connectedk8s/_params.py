# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

import os.path
from argcomplete.completers import FilesCompleter
from azure.cli.core.commands.parameters import get_location_type, get_enum_type, file_type, tags_type
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from azext_connectedk8s._constants import Distribution_Enum_Values, Infrastructure_Enum_Values, Feature_Values
from knack.arguments import (CLIArgumentType, CaseInsensitiveList)


features_types = CLIArgumentType(
    nargs='+',
    choices=CaseInsensitiveList(Feature_Values)
)


def load_arguments(self, _):

    with self.argument_context('connectedk8s connect') as c:
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('cluster_name', options_list=['--name', '-n'], help='The name of the connected cluster.')
        c.argument('kube_config', options_list=['--kube-config'], help='Path to the kube config file.')
        c.argument('kube_context', options_list=['--kube-context'], help='Kubconfig context from current machine.')
        c.argument('https_proxy', options_list=['--proxy-https'], arg_group='Proxy', help='Https proxy URL to be used.')
        c.argument('http_proxy', options_list=['--proxy-http'], arg_group='Proxy', help='Http proxy URL to be used.')
        c.argument('no_proxy', options_list=['--proxy-skip-range'], arg_group='Proxy', help='List of URLs/CIDRs for which proxy should not to be used.')
        c.argument('proxy_cert', options_list=['--proxy-cert'], arg_group='Proxy', type=file_type, completer=FilesCompleter(), help='Path to the certificate file for proxy')
        c.argument('distribution', options_list=['--distribution'], help='The Kubernetes distribution which will be running on this connected cluster.', arg_type=get_enum_type(Distribution_Enum_Values))
        c.argument('infrastructure', options_list=['--infrastructure'], help='The infrastructure on which the Kubernetes cluster represented by this connected cluster will be running on.', arg_type=get_enum_type(Infrastructure_Enum_Values))
        c.argument('disable_auto_upgrade', options_list=['--disable-auto-upgrade'], action='store_true', help='Flag to disable auto upgrade of arc agents.')

    with self.argument_context('connectedk8s update') as c:
        c.argument('cluster_name', options_list=['--name', '-n'], id_part='name', help='The name of the connected cluster.')
        c.argument('kube_config', options_list=['--kube-config'], help='Path to the kube config file.')
        c.argument('kube_context', options_list=['--kube-context'], help='Kubconfig context from current machine.')
        c.argument('https_proxy', options_list=['--proxy-https'], arg_group='Proxy', help='Https proxy URL to be used.')
        c.argument('http_proxy', options_list=['--proxy-http'], arg_group='Proxy', help='Http proxy URL to be used.')
        c.argument('no_proxy', options_list=['--proxy-skip-range'], arg_group='Proxy', help='List of URLs/CIDRs for which proxy should not to be used.')
        c.argument('proxy_cert', options_list=['--proxy-cert'], arg_group='Proxy', type=file_type, completer=FilesCompleter(), help='Path to the certificate file for proxy')
        c.argument('disable_proxy', options_list=['--disable-proxy'], arg_group='Proxy', action='store_true', help='Disables proxy settings for agents')
        c.argument('auto_upgrade', options_list=['--auto-upgrade'], help='Flag to enable/disable auto upgrade of arc agents. By default, auto upgrade of agents is enabled.', arg_type=get_enum_type(["true", "false"]))

    with self.argument_context('connectedk8s upgrade') as c:
        c.argument('cluster_name', options_list=['--name', '-n'], id_part='name', help='The name of the connected cluster.')
        c.argument('kube_config', options_list=['--kube-config'], help='Path to the kube config file.')
        c.argument('kube_context', options_list=['--kube-context'], help='Kubconfig context from current machine.')
        c.argument('arc_agent_version', options_list=['--agent-version'], help='Version of agent to update the helm charts to.')

    with self.argument_context('connectedk8s enable-features') as c:
        c.argument('cluster_name', options_list=['--name', '-n'], id_part='name', help='The name of the connected cluster.')
        c.argument('kube_config', options_list=['--kube-config'], help='Path to the kube config file.')
        c.argument('kube_context', options_list=['--kube-context'], help='Kubconfig context from current machine.')
        c.argument('features', features_types, options_list=['--features'], help='Space-separated list of features you want to enable.')
        c.argument('azrbac_client_id', options_list=['--app-id'], arg_group='Azure RBAC', help='Application ID for enabling Azure RBAC. Specify when enabling azure-rbac.')
        c.argument('azrbac_client_secret', options_list=['--app-secret'], arg_group='Azure RBAC', help='Application secret for enabling Azure RBAC. Specify when enabling azure-rbac.')
        c.argument('azrbac_skip_authz_check', options_list=['--skip-azure-rbac-list'], arg_group='Azure RBAC', help='Comma separated list of names of usernames/email/oid. Azure RBAC will be skipped for these users. Specify when enabling azure-rbac.')

    with self.argument_context('connectedk8s disable-features') as c:
        c.argument('cluster_name', options_list=['--name', '-n'], id_part='name', help='The name of the connected cluster.')
        c.argument('kube_config', options_list=['--kube-config'], help='Path to the kube config file.')
        c.argument('kube_context', options_list=['--kube-context'], help='Kubconfig context from current machine.')
        c.argument('features', features_types, options_list=['--features'], help='Space-separated list of features you want to disable.')
        c.argument('yes', options_list=['--yes', '-y'], help='Do not prompt for confirmation.', action='store_true')

    with self.argument_context('connectedk8s list') as c:
        pass

    with self.argument_context('connectedk8s show') as c:
        c.argument('cluster_name', options_list=['--name', '-n'], id_part='name', help='The name of the connected cluster.')

    with self.argument_context('connectedk8s delete') as c:
        c.argument('cluster_name', options_list=['--name', '-n'], id_part='name', help='The name of the connected cluster.')
        c.argument('kube_config', options_list=['--kube-config'], help='Path to the kube config file.')
        c.argument('kube_context', options_list=['--kube-context'], help='Kubconfig context from current machine.')

    with self.argument_context('connectedk8s proxy') as c:
        c.argument('cluster_name', options_list=['--name', '-n'], id_part='name', help='The name of the connected cluster.')
        c.argument('token', options_list=['--token'], help='Service account token to use to authenticate to the kubernetes cluster.')
        c.argument('context_name', options_list=['--kube-context'], help='If specified, overwrite the default context name.')
        c.argument('path', options_list=['--file', '-f'], type=file_type, completer=FilesCompleter(), default=os.path.join(os.path.expanduser('~'), '.kube', 'config'), help="Kubernetes configuration file to update. If not provided, updates the file '~/.kube/config'. Use '-' to print YAML to stdout instead.")
        c.argument('api_server_port', options_list=['--port'], help='Port used for accessing connected cluster.')
