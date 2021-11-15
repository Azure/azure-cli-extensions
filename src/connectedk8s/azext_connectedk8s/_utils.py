# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import platform
from base64 import b64encode

from requests.adapters import HTTPAdapter
from Crypto.IO import PEM
from Crypto.PublicKey import RSA
from Crypto.Util import asn1
from psutil import process_iter, NoSuchProcess, AccessDenied, ZombieProcess, net_connections
from knack.log import get_logger
from knack.prompting import NoTTYException, prompt_y_n
from azure.cli.core import telemetry
from azure.cli.core.azclierror import CLIInternalError
from azure.cli.core.azclierror import ManualInterrupt
import azext_connectedk8s._constants as consts
from .vendored_sdks.models import ConnectedCluster, ConnectedClusterIdentity

logger = get_logger(__name__)


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = consts.DEFAULT_REQUEST_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


def get_values_file():
    values_file_provided = False
    values_file = os.getenv('HELMVALUESPATH')
    if (values_file is not None) and (os.path.isfile(values_file)):
        values_file_provided = True
        logger.warning("Values files detected. Reading additional helm parameters from same.")
        # trimming required for windows os
        if (values_file.startswith("'") or values_file.startswith('"')):
            values_file = values_file[1:]
        if (values_file.endswith("'") or values_file.endswith('"')):
            values_file = values_file[:-1]

    return values_file_provided, values_file


def flatten(dd, separator='.', prefix=''):
    try:
        if isinstance(dd, dict):
            return {prefix + separator + k if prefix else k: v for kk, vv in dd.items()
                    for k, v in flatten(vv, separator, kk).items()}
        else:
            return {prefix: dd}
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.Error_Flattening_User_Supplied_Value_Dict,
                                summary='Error while flattening the user supplied helm values dict')
        raise CLIInternalError("Error while flattening the user supplied helm values dict")


def check_features_to_update(features_to_update):
    update_cluster_connect, update_azure_rbac, update_cl = False, False, False
    for feature in features_to_update:
        if feature == "cluster-connect":
            update_cluster_connect = True
        elif feature == "azure-rbac":
            update_azure_rbac = True
        elif feature == "custom-locations":
            update_cl = True
    return update_cluster_connect, update_azure_rbac, update_cl


def user_confirmation(message, yes=False):
    if yes:
        return
    try:
        if not prompt_y_n(message):
            raise ManualInterrupt('Operation cancelled.')
    except NoTTYException:
        raise CLIInternalError('Unable to prompt for confirmation as no tty available. Use --yes.')


def is_guid(guid):
    import uuid
    try:
        uuid.UUID(guid)
        return True
    except ValueError:
        return False


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


def send_cloud_telemetry(cmd):
    telemetry.add_extension_event('connectedk8s', {'Context.Default.AzureCLI.AzureCloud': cmd.cli_ctx.cloud.name})
    cloud_name = cmd.cli_ctx.cloud.name.upper()
    # Setting cloud name to format that is understood by golang SDK.
    if cloud_name == consts.PublicCloud_OriginalName:
        cloud_name = consts.Azure_PublicCloudName
    elif cloud_name == consts.USGovCloud_OriginalName:
        cloud_name = consts.Azure_USGovCloudName
    return cloud_name


def get_public_key(key_pair):
    pubKey = key_pair.publickey()
    seq = asn1.DerSequence([pubKey.n, pubKey.e])
    enc = seq.encode()
    return b64encode(enc).decode('utf-8')


def get_private_key(key_pair):
    privKey_DER = key_pair.exportKey(format='DER')
    return PEM.encode(privKey_DER, "RSA PRIVATE KEY")


def generate_request_payload(location, public_key, tags, kubernetes_distro, kubernetes_infra):
    # Create connected cluster resource object
    identity = ConnectedClusterIdentity(
        type="SystemAssigned"
    )
    if tags is None:
        tags = {}
    cc = ConnectedCluster(
        location=location,
        identity=identity,
        agent_public_key_certificate=public_key,
        tags=tags,
        distribution=kubernetes_distro,
        infrastructure=kubernetes_infra
    )
    return cc


def initial_log_warning():
    logger.warning("This operation might take a while...\n")


def generate_public_private_key():
    # Generate public-private key pair
    try:
        key_pair = RSA.generate(4096)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.KeyPair_Generate_Fault_Type,
                                summary='Failed to generate public-private key pair')
        raise CLIInternalError("Failed to generate public-private key pair. " + str(e))
    try:
        public_key = get_public_key(key_pair)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.PublicKey_Export_Fault_Type,
                                summary='Failed to export public key')
        raise CLIInternalError("Failed to export public key." + str(e))
    try:
        private_key_pem = get_private_key(key_pair)
    except Exception as e:
        telemetry.set_exception(exception=e, fault_type=consts.PrivateKey_Export_Fault_Type,
                                summary='Failed to export private key')
        raise CLIInternalError("Failed to export private key." + str(e))

    return public_key, private_key_pem
