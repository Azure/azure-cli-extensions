# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sys
import os
import platform
import base64
import json
import requests
import yaml
import time
import azext_connectedk8s._constants as consts
from base64 import b64encode, b64decode
from azure.cli.core._profile import Profile
from azure.cli.core import telemetry
from azure.cli.core.azclierror import CLIInternalError
from psutil import process_iter, NoSuchProcess, AccessDenied, ZombieProcess, net_connections
from knack.log import get_logger
logger = get_logger(__name__)


def check_if_port_is_open(port):
    try:
        connections = net_connections(kind='inet')
        for tup in connections:
            if int(tup[3][1]) == int(port):
                return True
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.Port_Check_Fault_Type,
                                summary='Failed to check if port is in use.')
        if platform.system() != 'Darwin':
            logger.info("Failed to check if port is in use. " + str(e))
        return False
    return False


def close_subprocess_and_raise_cli_error(proc_subprocess, msg):
    proc_subprocess.terminate()
    raise CLIInternalError(msg)


def check_if_csp_is_running(clientproxy_process):
    if clientproxy_process.poll() is None:
        return True
    else:
        return False


def make_api_call_with_retries(uri, data, method, tls_verify, fault_type, summary, cli_error, clientproxy_process):
    for i in range(consts.API_CALL_RETRIES):
        try:
            response = requests.request(method, uri, json=data, verify=tls_verify)
            return response
        except Exception as e:
            time.sleep(5)
            if i != consts.API_CALL_RETRIES - 1:
                pass
            else:
                telemetry.set_exception(exception=e, fault_type=fault_type, summary=summary)
                close_subprocess_and_raise_cli_error(clientproxy_process, cli_error + str(e))


def fetch_pop_publickey_kid(api_server_port, clientproxy_process):
    requestbody = {}
    poppublickey_uri = f'https://localhost:{api_server_port}/identity/poppublickey'
    # Needed to prevent skip tls warning from printing to the console
    original_stderr = sys.stderr
    f = open(os.devnull, 'w')
    sys.stderr = f

    get_publickey_response = make_api_call_with_retries(poppublickey_uri, requestbody, "get", False,
                                                        consts.Get_PublicKey_Info_Fault_Type,
                                                        'Failed to fetch public key info from clientproxy',
                                                        "Failed to fetch public key info from client proxy",
                                                        clientproxy_process)

    sys.stderr = original_stderr
    publickey_info = json.loads(get_publickey_response.text)
    kid = publickey_info['publicKey']['kid']

    return kid


def fetch_and_post_at_to_csp(cmd, api_server_port, tenant_id, kid, clientproxy_process):
    req_cnfJSON = {"kid": kid, "xms_ksl": "sw"}
    req_cnf = base64.urlsafe_b64encode(json.dumps(req_cnfJSON).encode('utf-8')).decode('utf-8')

    # remove padding '=' character
    if req_cnf[len(req_cnf) - 1] == '=':
        req_cnf = req_cnf[:-1]

    token_data = {"token_type": "pop", "key_id": kid, "req_cnf": req_cnf}
    profile = Profile(cli_ctx=cmd.cli_ctx)
    try:
        credential, _, _ = profile.get_login_credentials(subscription_id=profile.get_subscription()["id"],
                                                         resource=consts.KAP_1P_Server_App_Scope)
        accessToken = credential.get_token(consts.KAP_1P_Server_App_Scope, data=token_data)
        jwtToken = accessToken.token
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.Post_AT_To_ClientProxy_Failed_Fault_Type,
                                summary='Failed to fetch access token using the PoP public key sent by client proxy')
        close_subprocess_and_raise_cli_error(clientproxy_process,
                                             'Failed to post access token to client proxy' + str(e))

    jwtTokenData = {"accessToken": jwtToken, "serverId": consts.KAP_1P_Server_AppId, "tenantID": tenant_id, "kid": kid}
    post_at_uri = f'https://localhost:{api_server_port}/identity/at'
    # Needed to prevent skip tls warning from printing to the console
    original_stderr = sys.stderr
    f = open(os.devnull, 'w')
    sys.stderr = f
    post_at_response = make_api_call_with_retries(post_at_uri, jwtTokenData, "post", False,
                                                  consts.PublicKey_Export_Fault_Type,
                                                  'Failed to post access token to client proxy',
                                                  "Failed to post access token to client proxy",
                                                  clientproxy_process)

    sys.stderr = original_stderr
    return post_at_response


def insert_token_in_kubeconfig(data, token):
    b64kubeconfig = data['kubeconfigs'][0]['value']
    decoded_kubeconfig_str = b64decode(b64kubeconfig).decode("utf-8")
    dict_yaml = yaml.safe_load(decoded_kubeconfig_str)
    dict_yaml['users'][0]['user']['token'] = token
    kubeconfig = yaml.dump(dict_yaml).encode("utf-8")
    b64kubeconfig = b64encode(kubeconfig).decode("utf-8")
    return b64kubeconfig


def check_process(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    for proc in process_iter():
        try:
            if proc.name().startswith(processName):
                return True
        except (NoSuchProcess, AccessDenied, ZombieProcess):
            pass
    return False
