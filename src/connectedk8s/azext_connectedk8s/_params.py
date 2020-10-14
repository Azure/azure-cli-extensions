# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

import os.path

from argcomplete.completers import FilesCompleter

from azure.cli.core.commands.parameters import get_location_type, file_type, tags_type
from azure.cli.core.commands.validators import get_default_location_from_resource_group


def load_arguments(self, _):

    with self.argument_context('connectedk8s connect') as c:
        c.argument('tags', tags_type)
        c.argument('location', arg_type=get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('cluster_name', options_list=['--name', '-n'], help='The name of the connected cluster.')
        c.argument('kube_config', options_list=['--kube-config'], help='Path to the kube config file.')
        c.argument('kube_context', options_list=['--kube-context'], help='Kubconfig context from current machine.')
        c.argument('https_proxy', options_list=['--proxy-https'], help='Https proxy URL to be used.')
        c.argument('http_proxy', options_list=['--proxy-http'], help='Http proxy URL to be used.')
        c.argument('no_proxy', options_list=['--proxy-skip-range'], help='List of URLs/CIDRs for which proxy should not to be used.')
        c.argument('aad_server_app_id', options_list=['--aad-server-app-id'], help='AAD Server app id of your kubernetes cluster.')
        c.argument('aad_client_app_id', options_list=['--aad-client-app-id'], help='AAD Client app id of your kubernetes cluster.')

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

    with self.argument_context('connectedk8s get-credentials') as c:
        c.argument('cluster_name', options_list=['--name', '-n'], id_part='name', help='The name of the connected cluster.')
        c.argument('context_name', options_list=['--context'], help='If specified, overwrite the default context name.')
        c.argument('overwrite_existing', options_list=['--overwrite-existing'], help='Overwrite any existing cluster entry with the same name.')
        c.argument('token', options_list=['--auth-token'], help='Client authentication token for non-AAD scenario.')
        c.argument('path', options_list=['--file', '-f'], type=file_type, completer=FilesCompleter(), default=os.path.join(os.path.expanduser('~'), '.kube', 'config'), help="Kubernetes configuration file to update. If not provided, updates the file '~/.kube/config'. Use '-' to print YAML to stdout instead.")
