# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time
import sys
import json
from base64 import b64encode, b64decode
from subprocess import Popen, DEVNULL

import requests
from azure.cli.core import telemetry
from azure.cli.core.azclierror import ManualInterrupt, CLIInternalError, InvalidArgumentValueError
from azure.cli.core.commands.client_factory import get_subscription_id
import azext_connectedk8s._constants as consts
import azext_connectedk8s._kube_utils as kube_utils
import azext_connectedk8s._connected_cluster_utils as cc_utils
from .vendored_sdks.preview_2021_04_01.models import ListClusterUserCredentialsProperties


def create_proxy_details(https_proxy=None, http_proxy=None, no_proxy=None, proxy_cert=None, disable_proxy=None):
    proxy_details = {}
    proxy_details['https_proxy'] = escape_proxy_settings(https_proxy)
    proxy_details['http_proxy'] = escape_proxy_settings(http_proxy)
    proxy_details['no_proxy'] = escape_proxy_settings(no_proxy)

    # check whether proxy cert path exists
    if proxy_cert != "" and (not os.path.exists(proxy_cert)):
        telemetry.set_exception(exception='Proxy cert path does not exist',
                                fault_type=consts.Proxy_Cert_Path_Does_Not_Exist_Fault_Type,
                                summary='Proxy cert path does not exist')
        raise InvalidArgumentValueError(str.format(consts.Proxy_Cert_Path_Does_Not_Exist_Error, proxy_cert))

    proxy_details['proxy_cert'] = proxy_cert.replace('\\', r'\\\\')
    proxy_details['disable_proxy'] = disable_proxy
    return proxy_details


def escape_proxy_settings(proxy_setting):
    if proxy_setting is None:
        return ""
    proxy_setting = proxy_setting.replace(',', r'\,')
    proxy_setting = proxy_setting.replace('/', r'\/')
    return proxy_setting


# Prepare data as needed by client proxy executable
def prepare_clientproxy_data(response):
    data = {}
    data['kubeconfigs'] = []
    kubeconfig = {}
    kubeconfig['name'] = 'Kubeconfig'
    kubeconfig['value'] = b64encode(response.kubeconfigs[0].value).decode("utf-8")
    data['kubeconfigs'].append(kubeconfig)
    data['hybridConnectionConfig'] = {}
    data['hybridConnectionConfig']['relay'] = response.hybrid_connection_config.relay
    data['hybridConnectionConfig']['hybridConnectionName'] = response.hybrid_connection_config.hybrid_connection_name
    data['hybridConnectionConfig']['token'] = response.hybrid_connection_config.token
    data['hybridConnectionConfig']['expirationTime'] = response.hybrid_connection_config.expiration_time
    return data


def client_side_proxy_main(cmd,
                           client,
                           resource_group_name,
                           cluster_name,
                           args,
                           client_proxy_port,
                           api_server_port,
                           creds,
                           user_type,
                           debug_mode,
                           token=None,
                           path=os.path.join(os.path.expanduser('~'), '.kube', 'config'),
                           context_name=None,
                           clientproxy_process=None):
    expiry, clientproxy_process = client_side_proxy(cmd, client, resource_group_name, cluster_name,
                                                    0, args, client_proxy_port, api_server_port,
                                                    creds, user_type, debug_mode, token=token, path=path,
                                                    context_name=context_name, clientproxy_process=None)
    next_refresh_time = expiry - consts.CSP_REFRESH_TIME

    while True:
        time.sleep(60)
        if check_if_csp_is_running(clientproxy_process):
            if time.time() >= next_refresh_time:
                expiry, clientproxy_process = client_side_proxy(cmd, client, resource_group_name,
                                                                cluster_name, 1, args, client_proxy_port,
                                                                api_server_port, creds, user_type, debug_mode,
                                                                token=token, path=path, context_name=context_name,
                                                                clientproxy_process=clientproxy_process)
                next_refresh_time = expiry - consts.CSP_REFRESH_TIME
        else:
            telemetry.set_exception(exception='Process closed externally.',
                                    fault_type=consts.Proxy_Closed_Externally_Fault_Type,
                                    summary='Process closed externally.')
            raise ManualInterrupt('Proxy closed externally.')


def client_side_proxy(cmd,
                      client,
                      resource_group_name,
                      cluster_name,
                      flag,
                      args,
                      client_proxy_port,
                      api_server_port,
                      creds,
                      user_type,
                      debug_mode,
                      token=None,
                      path=os.path.join(os.path.expanduser('~'), '.kube', 'config'),
                      context_name=None,
                      clientproxy_process=None):

    subscription_id = get_subscription_id(cmd.cli_ctx)

    if token is not None:
        auth_method = 'Token'
    else:
        auth_method = 'AAD'

    # Fetching hybrid connection details from Userrp
    try:
        list_prop = ListClusterUserCredentialsProperties(
            authentication_method=auth_method,
            client_proxy=True
        )
        response = client.list_cluster_user_credentials(resource_group_name, cluster_name, list_prop)
    except Exception as e:
        if flag == 1:
            clientproxy_process.terminate()
        cc_utils.arm_exception_handler(e, consts.Get_Credentials_Failed_Fault_Type,
                                       'Unable to list cluster user credentials')
        raise CLIInternalError("Failed to get credentials." + str(e))

    # Starting the client proxy process, if this is the first time that this function is invoked
    if flag == 0:
        try:
            if debug_mode:
                clientproxy_process = Popen(args)
            else:
                clientproxy_process = Popen(args, stdout=DEVNULL, stderr=DEVNULL)
            print(f'Proxy is listening on port {api_server_port}')

        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=consts.Run_Clientproxy_Fault_Type,
                                    summary='Unable to run client proxy executable')
            raise CLIInternalError("Failed to start proxy process." + str(e))

        if user_type == 'user':
            identity_data = {}
            identity_data['refreshToken'] = creds
            identity_uri = f'https://localhost:{api_server_port}/identity/rt'

            # Needed to prevent skip tls warning from printing to the console
            original_stderr = sys.stderr
            f = open(os.devnull, 'w')
            sys.stderr = f

            make_api_call_with_retries(identity_uri, identity_data, False, consts.Post_RefreshToken_Fault_Type,
                                       'Unable to post refresh token details to clientproxy',
                                       "Failed to pass refresh token details to proxy.", clientproxy_process)
            sys.stderr = original_stderr

    data = prepare_clientproxy_data(response)
    expiry = data['hybridConnectionConfig']['expirationTime']

    if token is not None:
        data['kubeconfigs'][0]['value'] = kube_utils.insert_token_in_kubeconfig(data, token)

    uri = (
        f'http://localhost:{client_proxy_port}/subscriptions/{subscription_id}'
        f'/resourceGroups/{resource_group_name}/providers/Microsoft.Kubernetes/'
        f'connectedClusters/{cluster_name}/register?api-version=2020-10-01'
    )

    # Posting hybrid connection details to proxy in order to get kubeconfig
    response = make_api_call_with_retries(uri, data, False, consts.Post_Hybridconn_Fault_Type,
                                          'Unable to post hybrid connection details to clientproxy',
                                          "Failed to pass hybrid connection details to proxy.", clientproxy_process)

    if flag == 0:
        # Decoding kubeconfig into a string
        try:
            kubeconfig = json.loads(response.text)
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=consts.Load_Kubeconfig_Fault_Type,
                                    summary='Unable to load Kubeconfig')
            close_subprocess_and_raise_cli_error(clientproxy_process, "Failed to load kubeconfig." + str(e))

        kubeconfig = kubeconfig['kubeconfigs'][0]['value']
        kubeconfig = b64decode(kubeconfig).decode("utf-8")

        try:
            kube_utils.print_or_merge_credentials(path, kubeconfig, True, context_name)
            if path != "-":
                if context_name is None:
                    kubeconfig_obj = kube_utils.load_kubernetes_configuration(path)
                    temp_context_name = kubeconfig_obj['current-context']
                else:
                    temp_context_name = context_name
                print("Start sending kubectl requests on '{}' context using kubeconfig at {}"
                      .format(temp_context_name, path))

            print("Press Ctrl+C to close proxy.")

        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=consts.Merge_Kubeconfig_Fault_Type,
                                    summary='Unable to merge kubeconfig.')
            close_subprocess_and_raise_cli_error(clientproxy_process, "Failed to merge kubeconfig." + str(e))

    return expiry, clientproxy_process


def check_if_csp_is_running(clientproxy_process):
    return bool(clientproxy_process.poll())


def make_api_call_with_retries(uri, data, tls_verify, fault_type, summary, cli_error, clientproxy_process):
    for i in range(consts.API_CALL_RETRIES):
        try:
            response = requests.post(uri, json=data, verify=tls_verify)
            return response
        except Exception as e:
            if i != consts.API_CALL_RETRIES - 1:
                pass
            else:
                telemetry.set_exception(exception=e, fault_type=fault_type, summary=summary)
                close_subprocess_and_raise_cli_error(clientproxy_process, cli_error + str(e))
    return None


def close_subprocess_and_raise_cli_error(proc_subprocess, msg):
    proc_subprocess.terminate()
    raise CLIInternalError(msg)
