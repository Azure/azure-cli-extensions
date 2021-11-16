# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import functools
import os
import hashlib
import json
import tempfile
import urllib.request
import base64
import stat
import time
from glob import glob

from knack import log
from azure.cli.core import azclierror
from azure.cli.core import telemetry

from . import ip_utils
from . import rsa_parser
from . import ssh_utils
from . import constants as consts
from . import file_utils

logger = log.get_logger(__name__)


def ssh_vm(cmd, resource_group_name=None, vm_name=None, ssh_ip=None, public_key_file=None,
           private_key_file=None, use_private_ip=False, local_user=None, cert_file=None, port=None,
           ssh_client_path=None, delete_credentials=False, resource_type=None, ssh_args=None):

    if delete_credentials and os.environ.get("AZUREPS_HOST_ENVIRONMENT") != "cloud-shell/1.0":
        raise azclierror.ArgumentUsageError("Can't use --delete-private-key outside an Azure Cloud Shell session.")

    _assert_args(resource_group_name, vm_name, ssh_ip, resource_type, cert_file, local_user)
    credentials_folder = None
    do_ssh_op = _decide_op_call(cmd, resource_group_name, vm_name, ssh_ip, resource_type, None, None,
                                ssh_client_path, ssh_args, delete_credentials, credentials_folder)
    do_ssh_op(cmd, vm_name, resource_group_name, ssh_ip, public_key_file, private_key_file, local_user,
              cert_file, port, use_private_ip, credentials_folder)


def ssh_config(cmd, config_path, resource_group_name=None, vm_name=None, ssh_ip=None,
               public_key_file=None, private_key_file=None, overwrite=False, use_private_ip=False,
               local_user=None, cert_file=None, port=None, resource_type=None, credentials_folder=None):

    if (public_key_file or private_key_file) and credentials_folder:
        raise azclierror.ArgumentUsageError("--keys-destination-folder can't be used in conjunction with "
                                            "--public-key-file/-p or --private-key-file/-i.")
    _assert_args(resource_group_name, vm_name, ssh_ip, resource_type, cert_file, local_user)

    # Default credential location
    if not credentials_folder:
        config_folder = os.path.dirname(config_path)
        if not os.path.isdir(config_folder):
            raise azclierror.InvalidArgumentValueError(f"Config file destination folder {config_folder} "
                                                       "does not exist.")
        folder_name = ssh_ip
        if resource_group_name and vm_name:
            folder_name = resource_group_name + "-" + vm_name

        credentials_folder = os.path.join(config_folder, os.path.join("az_ssh_config", folder_name))

    do_ssh_op = _decide_op_call(cmd, resource_group_name, vm_name, ssh_ip, resource_type, config_path, overwrite,
                                None, None, False, credentials_folder)
    do_ssh_op(cmd, vm_name, resource_group_name, ssh_ip, public_key_file, private_key_file, local_user,
              cert_file, port, use_private_ip, credentials_folder)


def ssh_cert(cmd, cert_path=None, public_key_file=None):
    if not cert_path and not public_key_file:
        raise azclierror.RequiredArgumentMissingError("--file or --public-key-file must be provided.")
    if cert_path and not os.path.isdir(os.path.dirname(cert_path)):
        raise azclierror.InvalidArgumentValueError(f"{os.path.dirname(cert_path)} folder doesn't exist")
    # If user doesn't provide a public key, save generated key pair to the same folder as --file
    keys_folder = None
    if not public_key_file:
        keys_folder = os.path.dirname(cert_path)
        logger.warning("The generated SSH keys are stored at %s. Please delete SSH keys when the certificate "
                       "is no longer being used.", keys_folder)
    public_key_file, _, _ = _check_or_create_public_private_files(public_key_file, None, keys_folder)
    cert_file, _ = _get_and_write_certificate(cmd, public_key_file, cert_path)
    print(cert_file + "\n")


def ssh_arc(cmd, resource_group_name=None, vm_name=None, public_key_file=None, private_key_file=None,
            local_user=None, cert_file=None, port=None, ssh_client_path=None, delete_credentials=False, ssh_args=None):

    if delete_credentials and os.environ.get("AZUREPS_HOST_ENVIRONMENT") != "cloud-shell/1.0":
        raise azclierror.ArgumentUsageError("Can't use --delete-private-key outside an Azure Cloud Shell session.")

    _assert_args(resource_group_name, vm_name, None, "Microsoft.HybridCompute", cert_file, local_user)

    credentials_folder = None

    op_call = functools.partial(ssh_utils.start_ssh_connection, ssh_client_path=ssh_client_path, ssh_args=ssh_args,
                                delete_credentials=delete_credentials)
    _do_ssh_op(cmd, vm_name, resource_group_name, None, public_key_file, private_key_file, local_user, cert_file, port,
               False, credentials_folder, op_call, True)


def _do_ssh_op(cmd, vm_name, resource_group_name, ssh_ip, public_key_file, private_key_file, username,
               cert_file, port, use_private_ip, credentials_folder, op_call, is_arc):

    proxy_path = None
    relay_info = None
    if is_arc:
        proxy_path = _arc_get_client_side_proxy()
        relay_info = _arc_list_access_details(cmd, resource_group_name, vm_name)
    else:
        ssh_ip = ssh_ip or ip_utils.get_ssh_ip(cmd, resource_group_name, vm_name, use_private_ip)
        if not ssh_ip:
            if not use_private_ip:
                raise azclierror.ResourceNotFoundError(f"VM '{vm_name}' does not have a public IP address to SSH to")
            raise azclierror.ResourceNotFoundError(f"VM '{vm_name}' does not have a public or private IP address to"
                                                   "SSH to")

    # If user provides local user, no credentials should be deleted.
    delete_keys = False
    delete_cert = False
    if not username:
        delete_cert = True
        public_key_file, private_key_file, delete_keys = _check_or_create_public_private_files(public_key_file,
                                                                                               private_key_file,
                                                                                               credentials_folder)
        cert_file, username = _get_and_write_certificate(cmd, public_key_file, None)

    print(cert_file)
    op_call(relay_info, proxy_path, vm_name, ssh_ip, username, cert_file, private_key_file, port, is_arc, delete_keys,
            delete_cert, public_key_file)


def _get_and_write_certificate(cmd, public_key_file, cert_file):
    cloudtoscope = {
        "azurecloud": "https://pas.windows.net/CheckMyAccess/Linux/.default",
        "azurechinacloud": "https://pas.chinacloudapi.cn/CheckMyAccess/Linux/.default",
        "azureusgovernment": "https://pasff.usgovcloudapi.net/CheckMyAccess/Linux/.default"
    }
    scope = cloudtoscope.get(cmd.cli_ctx.cloud.name.lower(), None)
    if not scope:
        raise azclierror.InvalidArgumentValueError(
            f"Unsupported cloud {cmd.cli_ctx.cloud.name.lower()}",
            "Supported clouds include azurecloud,azurechinacloud,azureusgovernment")

    scopes = [scope]
    data = _prepare_jwk_data(public_key_file)
    from azure.cli.core._profile import Profile
    profile = Profile(cli_ctx=cmd.cli_ctx)

    t0 = time.time()
    # We currently are using the presence of get_msal_token to detect if we are running on an older azure cli client
    # TODO: Remove when adal has been deprecated for a while
    if hasattr(profile, "get_msal_token"):
        # we used to use the username from the token but now we throw it away
        _, certificate = profile.get_msal_token(scopes, data)
    else:
        credential, _, _ = profile.get_login_credentials(subscription_id=profile.get_subscription()["id"])
        certificatedata = credential.get_token(*scopes, data=data)
        certificate = certificatedata.token

    time_elapsed = time.time() - t0
    telemetry.add_extension_event('ssh', {'Context.Default.AzureCLI.SSHGetCertificateTime': time_elapsed})

    if not cert_file:
        cert_file = public_key_file + "-aadcert.pub"
    _write_cert_file(certificate, cert_file)
    # instead we use the validprincipals from the cert due to mismatched upn and email in guest scenarios
    username = ssh_utils.get_ssh_cert_principals(cert_file)[0]
    return cert_file, username.lower()


def _prepare_jwk_data(public_key_file):
    modulus, exponent = _get_modulus_exponent(public_key_file)
    key_hash = hashlib.sha256()
    key_hash.update(modulus.encode('utf-8'))
    key_hash.update(exponent.encode('utf-8'))
    key_id = key_hash.hexdigest()
    jwk = {
        "kty": "RSA",
        "n": modulus,
        "e": exponent,
        "kid": key_id
    }
    json_jwk = json.dumps(jwk)
    data = {
        "token_type": "ssh-cert",
        "req_cnf": json_jwk,
        "key_id": key_id
    }
    return data


def _assert_args(resource_group, vm_name, ssh_ip, resource_type, cert_file, username):
    if resource_type and resource_type != "Microsoft.Compute" and resource_type != "Microsoft.HybridCompute":
        raise azclierror.InvalidArgumentValueError("--resource-type must be either \"Microsoft.Compute\" "
                                                   "for Azure VMs or \"Microsoft.HybridCompute\" for Arc Servers.")

    if not (resource_group or vm_name or ssh_ip):
        raise azclierror.RequiredArgumentMissingError(
            "The VM must be specified by --ip or --resource-group and "
            "--vm-name/--name")

    if resource_group and not vm_name or vm_name and not resource_group:
        raise azclierror.MutuallyExclusiveArgumentError(
            "--resource-group and --vm-name/--name must be provided together")

    if ssh_ip and (vm_name or resource_group):
        raise azclierror.MutuallyExclusiveArgumentError(
            "--ip cannot be used with --resource-group or --vm-name/--name")

    if cert_file and not username:
        raise azclierror.MutuallyExclusiveArgumentError(
            "To authenticate with a certificate you need to provide a --local-user")

    if cert_file and not os.path.isfile(cert_file):
        raise azclierror.FileOperationError(f"Certificate file {cert_file} not found")


def _check_or_create_public_private_files(public_key_file, private_key_file, credentials_folder):
    delete_keys = False
    # If nothing is passed in create a temporary directory with a ephemeral keypair
    if not public_key_file and not private_key_file:
        # We only want to delete the keys if the user hasn't provided their own keys
        # Only ssh vm deletes generated keys.
        delete_keys = True
        if not credentials_folder:
            # az ssh vm: Create keys on temp folder and delete folder once connection succeeds/fails.
            credentials_folder = tempfile.mkdtemp(prefix="aadsshcert")
        else:
            # az ssh config: Keys saved to the same folder as --file or to --keys-destination-folder.
            # az ssh cert: Keys saved to the same folder as --file.
            if not os.path.isdir(credentials_folder):
                os.makedirs(credentials_folder)
        public_key_file = os.path.join(credentials_folder, "id_rsa.pub")
        private_key_file = os.path.join(credentials_folder, "id_rsa")
        ssh_utils.create_ssh_keyfile(private_key_file)

    if not public_key_file:
        if private_key_file:
            public_key_file = private_key_file + ".pub"
        else:
            raise azclierror.RequiredArgumentMissingError("Public key file not specified")

    if not os.path.isfile(public_key_file):
        raise azclierror.FileOperationError(f"Public key file {public_key_file} not found")

    # The private key is not required as the user may be using a keypair
    # stored in ssh-agent (and possibly in a hardware token)
    if private_key_file:
        if not os.path.isfile(private_key_file):
            raise azclierror.FileOperationError(f"Private key file {private_key_file} not found")

    return public_key_file, private_key_file, delete_keys


def _write_cert_file(certificate_contents, cert_file):
    with open(cert_file, 'w') as f:
        f.write(f"ssh-rsa-cert-v01@openssh.com {certificate_contents}")

    return cert_file


def _get_modulus_exponent(public_key_file):
    if not os.path.isfile(public_key_file):
        raise azclierror.FileOperationError(f"Public key file '{public_key_file}' was not found")

    with open(public_key_file, 'r') as f:
        public_key_text = f.read()

    parser = rsa_parser.RSAParser()
    try:
        parser.parse(public_key_text)
    except Exception as e:
        raise azclierror.FileOperationError(f"Could not parse public key. Error: {str(e)}")
    modulus = parser.modulus
    exponent = parser.exponent

    return modulus, exponent


# Downloads client side proxy to connect to Arc Connectivity Platform
def _arc_get_client_side_proxy():
    import platform
    operating_system = platform.system()
    machine = platform.machine()

    logger.debug("Platform OS: %s", operating_system)
    logger.debug("Platform architecture: %s", machine)

    if machine.endswith('64'):
        architecture = 'amd64'
    elif machine.endswith('86'):
        architecture = '386'
    elif machine == '':
        raise azclierror.BadRequestError("Couldn't identify the platform architecture.")
    else:
        telemetry.set_exception(exception='Unsuported architecture for installing proxy',
                                fault_type=consts.Proxy_Unsuported_Arch_Fault_Type,
                                summary=f'{machine} is not supported for installing client proxy')
        raise azclierror.BadRequestError(f"Unsuported architecture: {machine} is not currently supported")

    # define the request url and install location based on the os and architecture
    proxy_name = f"sshProxy_{operating_system.lower()}_{architecture}"
    request_uri = (f"{consts.CLIENT_PROXY_STORAGE_URL}/{consts.CLIENT_PROXY_RELEASE}"
                   f"/{proxy_name}_{consts.CLIENT_PROXY_VERSION}")
    install_location = os.path.join(".clientsshproxy", proxy_name + "_" + consts.CLIENT_PROXY_VERSION.replace('.', '_'))
    older_version_location = os.path.join(".clientsshproxy", proxy_name + "*")

    if operating_system == 'Windows':
        request_uri = request_uri + ".exe"
        install_location = install_location + ".exe"
        older_version_location = older_version_location + ".exe"
    elif operating_system not in ('Linux', 'Darwin'):
        telemetry.set_exception(exception='Unsuported OS for installing ssh client proxy',
                                fault_type=consts.Proxy_Unsuported_OS_Fault_Type,
                                summary=f'{operating_system} is not supported for installing client proxy')
        raise azclierror.BadRequestError(f"Unsuported OS: {operating_system} platform is not currently supported")

    install_location = os.path.expanduser(os.path.join('~', install_location))
    older_version_location = os.path.expanduser(os.path.join('~', older_version_location))
    install_dir = os.path.dirname(install_location)

    # Only download new proxy if it doesn't exist already
    if not os.path.isfile(install_location):
        t0 = time.time()
        # download the executable
        try:
            with urllib.request.urlopen(request_uri) as response:
                response_content = response.read()
                response.close()
        except Exception as e:
            telemetry.set_exception(exception=e, fault_type=consts.Proxy_Download_Failed_Fault_Type,
                                    summary=f'Failed to download proxy from {request_uri}')
            raise azclierror.ClientRequestError(f"Failed to download client proxy executable from {request_uri}. "
                                                "Error: " + str(e)) from e
        time_elapsed = time.time() - t0

        proxy_data = {
            'Context.Default.AzureCLI.SSHProxyDownloadTime': time_elapsed,
            'Context.Default.AzureCLI.SSHProxyVersion': consts.CLIENT_PROXY_VERSION
        }
        telemetry.add_extension_event('ssh', proxy_data)

        # if directory doesn't exist, create it
        if not os.path.exists(install_dir):
            file_utils.create_directory(install_dir, f"Failed to create client proxy directory '{install_dir}'. ")
        # if directory exists, delete any older versions of the proxy
        else:
            older_version_files = glob(older_version_location)
            for f in older_version_files:
                file_utils.delete_file(f, f"failed to delete older version file {f}", warning=True)

        # write executable in the install location
        file_utils.write_to_file(install_location, 'wb', response_content, "Failed to create client proxy file. ")
        os.chmod(install_location, os.stat(install_location).st_mode | stat.S_IXUSR)

    return install_location


# Get the Access Details to connect to Arc Connectivity platform from the HybridCompute Resource Provider
# TO DO: This is a temporary API call to get the relay info. We will move to a different one in the future.
def _arc_list_access_details(cmd, resource_group, vm_name):
    from azext_ssh._client_factory import cf_endpoint
    client = cf_endpoint(cmd.cli_ctx)
    try:
        t0 = time.time()
        result = client.list_credentials(resource_group_name=resource_group, machine_name=vm_name,
                                         endpoint_name="default")
        time_elapsed = time.time() - t0
        telemetry.add_extension_event('ssh', {'Context.Default.AzureCLI.SSHListCredentialsTime': time_elapsed})
    except Exception as e:
        telemetry.set_exception(exception='Call to listCredentials failed',
                                fault_type=consts.List_Credentials_Failed,
                                summary=f'listCredentials failed with error: {str(e)}.')
        raise azclierror.ClientRequestError(f"Request for Azure Relay Information Failed: {str(e)}")

    result_string = json.dumps(
        {
            "relay": {
                "namespaceName": result.namespace_name,
                "namespaceNameSuffix": result.namespace_name_suffix,
                "hybridConnectionName": result.hybrid_connection_name,
                "accessKey": result.access_key,
                "expiresOn": result.expires_on
            }
        })
    result_bytes = result_string.encode("ascii")
    enc = base64.b64encode(result_bytes)
    base64_result_string = enc.decode("ascii")
    return base64_result_string


def _decide_op_call(cmd, resource_group_name, vm_name, ssh_ip, resource_type, config_path, overwrite,
                    ssh_client_path, ssh_args, delete_credentials, credentials_folder):

    # If the user provides an IP address the target will be treated as an Azure VM even if it is an
    # Arc Server. Which just means that the Connectivity Proxy won't be used to establish connection.
    is_arc_server = False

    if ssh_ip:
        is_arc_server = False

    elif resource_type:
        if resource_type == "Microsoft.HybridCompute":
            is_arc_server = True

    else:
        vm_error, is_azure_vm = _check_if_azure_vm(cmd, resource_group_name, vm_name)
        arc_error, is_arc_server = _check_if_arc_server(cmd, resource_group_name, vm_name)

        if is_azure_vm and is_arc_server:
            raise azclierror.BadRequestError(f"{resource_group_name} has Azure VM and Arc Server with the "
                                             f"same name: {vm_name}. Please provide a --resource-type.")
        if not is_azure_vm and not is_arc_server:
            from azure.core.exceptions import ResourceNotFoundError
            if isinstance(arc_error, ResourceNotFoundError) and isinstance(vm_error, ResourceNotFoundError):
                raise azclierror.ResourceNotFoundError(f"The resource {vm_name} in the resource group "
                                                       f"{resource_group_name} was not found. Erros:\n"
                                                       f"{str(arc_error)}\n{str(vm_error)}")
            raise azclierror.BadRequestError("Unable to determine the target machine type as Azure VM or "
                                             f"Arc Server. Errors:\n{str(arc_error)}\n{str(vm_error)}")

    if config_path:
        op_call = functools.partial(ssh_utils.write_ssh_config, config_path=config_path, overwrite=overwrite,
                                    resource_group=resource_group_name, credentials_folder=credentials_folder)
    else:
        op_call = functools.partial(ssh_utils.start_ssh_connection, ssh_client_path=ssh_client_path, ssh_args=ssh_args,
                                    delete_credentials=delete_credentials)
    do_ssh_op = functools.partial(_do_ssh_op, is_arc=is_arc_server, op_call=op_call)
    return do_ssh_op


def _check_if_azure_vm(cmd, resource_group_name, vm_name):
    from azure.cli.core.commands import client_factory
    from azure.cli.core import profiles
    from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
    try:
        compute_client = client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_COMPUTE)
        compute_client.virtual_machines.get(resource_group_name, vm_name)
    except ResourceNotFoundError as e:
        return e, False
    # If user is not authorized to get the VM, it will throw a HttpResponseError
    except HttpResponseError as e:
        return e, False
    return None, True


def _check_if_arc_server(cmd, resource_group_name, vm_name):
    from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
    from azext_ssh._client_factory import cf_machine
    client = cf_machine(cmd.cli_ctx)
    try:
        client.get(resource_group_name=resource_group_name, machine_name=vm_name)
    except ResourceNotFoundError as e:
        return e, False
    # If user is not authorized to get the arc server, it will throw a HttpResponseError
    except HttpResponseError as e:
        return e, False
    return None, True
