# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import hashlib
import json
import tempfile
import time
import platform
import oschmod

from knack import log
from azure.cli.core import azclierror
from azure.cli.core import telemetry
from azure.cli.core.style import Style, print_styled_text

from . import ip_utils
from . import rdp_utils
from . import rsa_parser
from . import ssh_utils
from . import connectivity_utils
from . import ssh_info
from . import file_utils
from . import constants as const
from . import resource_type_utils
from . import target_os_utils

logger = log.get_logger(__name__)


def ssh_vm(cmd, resource_group_name=None, vm_name=None, ssh_ip=None, public_key_file=None,
           private_key_file=None, use_private_ip=False, local_user=None, cert_file=None, port=None,
           ssh_client_folder=None, delete_credentials=False, resource_type=None, ssh_proxy_folder=None,
           winrdp=False, yes_without_prompt=False, ssh_args=None):

    # delete_credentials can only be used by Azure Portal to provide one-click experience on CloudShell.
    if delete_credentials and os.environ.get("AZUREPS_HOST_ENVIRONMENT") != "cloud-shell/1.0":
        raise azclierror.ArgumentUsageError("Can't use --delete-private-key outside an Azure Cloud Shell session.")

    # include openssh client logs to --debug output to make it easier to users to debug connection issued.
    if '--debug' in cmd.cli_ctx.data['safe_params'] and set(['-v', '-vv', '-vvv']).isdisjoint(ssh_args):
        ssh_args = ['-vvv'] if not ssh_args else ['-vvv'] + ssh_args

    _assert_args(resource_group_name, vm_name, ssh_ip, resource_type, cert_file, local_user)

    # all credentials for this command are saved in temp folder and deleted at the end of execution.
    credentials_folder = None

    op_call = ssh_utils.start_ssh_connection
    if winrdp:
        if platform.system() != 'Windows':
            raise azclierror.BadRequestError("RDP connection is not supported for this platform. "
                                             "Supported platforms: Windows")
        op_call = rdp_utils.start_rdp_connection

    ssh_session = ssh_info.SSHSession(resource_group_name, vm_name, ssh_ip, public_key_file,
                                      private_key_file, use_private_ip, local_user, cert_file, port,
                                      ssh_client_folder, ssh_args, delete_credentials, resource_type,
                                      ssh_proxy_folder, credentials_folder, winrdp, yes_without_prompt)
    ssh_session.resource_type = resource_type_utils.decide_resource_type(cmd, ssh_session)
    target_os_utils.handle_target_os_type(cmd, ssh_session)

    _do_ssh_op(cmd, ssh_session, op_call)


def ssh_config(cmd, config_path, resource_group_name=None, vm_name=None, ssh_ip=None,
               public_key_file=None, private_key_file=None, overwrite=False, use_private_ip=False,
               local_user=None, cert_file=None, port=None, resource_type=None, credentials_folder=None,
               ssh_proxy_folder=None, ssh_client_folder=None, yes_without_prompt=False):

    # If user provides their own key pair, certificate will be written in the same folder as public key.
    if (public_key_file or private_key_file) and credentials_folder:
        raise azclierror.ArgumentUsageError("--keys-destination-folder can't be used in conjunction with "
                                            "--public-key-file/-p or --private-key-file/-i.")
    _assert_args(resource_group_name, vm_name, ssh_ip, resource_type, cert_file, local_user)

    config_session = ssh_info.ConfigSession(config_path, resource_group_name, vm_name, ssh_ip,
                                            public_key_file, private_key_file, overwrite, use_private_ip,
                                            local_user, cert_file, port, resource_type, credentials_folder,
                                            ssh_proxy_folder, ssh_client_folder, yes_without_prompt)
    op_call = ssh_utils.write_ssh_config

    config_session.resource_type = resource_type_utils.decide_resource_type(cmd, config_session)
    target_os_utils.handle_target_os_type(cmd, config_session)

    # if the folder doesn't exist, this extension won't create a new one.
    config_folder = os.path.dirname(config_session.config_path)
    if not os.path.isdir(config_folder):
        raise azclierror.InvalidArgumentValueError(f"Config file destination folder {config_folder} "
                                                   "does not exist.")
    if not credentials_folder:
        # * is not a valid name for a folder in Windows. Treat this as a special case.
        folder_name = config_session.ip if config_session.ip != "*" else "all_ips"
        if config_session.resource_group_name and config_session.vm_name:
            folder_name = config_session.resource_group_name + "-" + config_session.vm_name
        if not set(folder_name).isdisjoint(set(const.WINDOWS_INVALID_FOLDERNAME_CHARS)) and \
           platform.system() == "Windows" and (not config_session.local_user or config_session.is_arc()):
            folder_name = file_utils.remove_invalid_characters_foldername(folder_name)
            if folder_name == "":
                raise azclierror.RequiredArgumentMissingError("Can't create default folder for generated keys. "
                                                              "Please provide --keys-destination-folder.")
        config_session.credentials_folder = os.path.join(config_folder, os.path.join("az_ssh_config", folder_name))

    _do_ssh_op(cmd, config_session, op_call)


def ssh_cert(cmd, cert_path=None, public_key_file=None, ssh_client_folder=None):
    if not cert_path and not public_key_file:
        raise azclierror.RequiredArgumentMissingError("--file or --public-key-file must be provided.")
    if cert_path and not os.path.isdir(os.path.dirname(cert_path)):
        raise azclierror.InvalidArgumentValueError(f"{os.path.dirname(cert_path)} folder doesn't exist")

    if public_key_file:
        public_key_file = os.path.abspath(public_key_file)
    if cert_path:
        cert_path = os.path.abspath(cert_path)
    if ssh_client_folder:
        ssh_client_folder = os.path.abspath(ssh_client_folder)

    # If user doesn't provide a public key, save generated key pair to the same folder as --file
    keys_folder = None
    if not public_key_file:
        keys_folder = os.path.dirname(cert_path)

    public_key_file, _, _ = _check_or_create_public_private_files(public_key_file, None, keys_folder, ssh_client_folder)
    cert_file, _ = _get_and_write_certificate(cmd, public_key_file, cert_path, ssh_client_folder)

    if keys_folder:
        logger.warning("%s contains sensitive information (id_rsa, id_rsa.pub). "
                       "Please delete once this certificate is no longer being used.", keys_folder)
    # pylint: disable=broad-except
    try:
        cert_expiration = ssh_utils.get_certificate_start_and_end_times(cert_file, ssh_client_folder)[1]
        print_styled_text((Style.SUCCESS,
                           f"Generated SSH certificate {cert_file} is valid until {cert_expiration} in local time."))
    except Exception as e:
        logger.warning("Couldn't determine certificate validity. Error: %s", str(e))
        print_styled_text((Style.SUCCESS, f"Generated SSH certificate {cert_file}."))


def ssh_arc(cmd, resource_group_name=None, vm_name=None, public_key_file=None, private_key_file=None,
            local_user=None, cert_file=None, port=None, resource_type=None, ssh_client_folder=None,
            delete_credentials=False, ssh_proxy_folder=None, winrdp=False, yes_without_prompt=False, ssh_args=None):

    if not resource_type:
        resource_type = const.ARC_RESOURCE_TYPE_PLACEHOLDER

    ssh_vm(cmd, resource_group_name, vm_name, None, public_key_file, private_key_file,
           False, local_user, cert_file, port, ssh_client_folder, delete_credentials,
           resource_type, ssh_proxy_folder, winrdp, yes_without_prompt, ssh_args)


def _do_ssh_op(cmd, op_info, op_call):
    # Get ssh_ip before getting public key to avoid getting "ResourceNotFound" exception after creating the keys
    if not op_info.is_arc():
        if op_info.ssh_proxy_folder:
            logger.warning("Target machine is not an Arc Server, --ssh-proxy-folder value will be ignored.")
        op_info.ip = op_info.ip or ip_utils.get_ssh_ip(cmd, op_info.resource_group_name,
                                                       op_info.vm_name, op_info.use_private_ip)
        if not op_info.ip:
            if not op_info.use_private_ip:
                raise azclierror.ResourceNotFoundError(f"VM '{op_info.vm_name}' does not have a public "
                                                       "IP address to SSH to")
            raise azclierror.ResourceNotFoundError("Internal Error. Couldn't determine the IP address.")

    # If user provides local user, no credentials should be deleted.
    delete_keys = False
    delete_cert = False
    cert_lifetime = None
    # If user provides a local user, use the provided credentials for authentication
    if not op_info.local_user:
        delete_cert = True
        op_info.public_key_file, op_info.private_key_file, delete_keys = \
            _check_or_create_public_private_files(op_info.public_key_file, op_info.private_key_file,
                                                  op_info.credentials_folder, op_info.ssh_client_folder)
        op_info.cert_file, op_info.local_user = _get_and_write_certificate(cmd, op_info.public_key_file,
                                                                           None, op_info.ssh_client_folder)
        if op_info.is_arc():
            # pylint: disable=broad-except
            try:
                cert_lifetime = ssh_utils.get_certificate_lifetime(op_info.cert_file,
                                                                   op_info.ssh_client_folder).total_seconds()
            except Exception as e:
                logger.warning("Couldn't determine certificate expiration. Error: %s", str(e))

    try:
        if op_info.is_arc():
            op_info.proxy_path = connectivity_utils.get_client_side_proxy(op_info.ssh_proxy_folder)
            (op_info.relay_info, op_info.new_service_config) = connectivity_utils.get_relay_information(
                cmd, op_info.resource_group_name, op_info.vm_name, op_info.resource_type,
                cert_lifetime, op_info.port, op_info.yes_without_prompt)
    except Exception as e:
        if delete_keys or delete_cert:
            logger.debug("An error occured before operation concluded. Deleting generated keys: %s %s %s",
                         op_info.private_key_file + ', ' if delete_keys else "",
                         op_info.public_key_file + ', ' if delete_keys else "",
                         op_info.cert_file if delete_cert else "")
            ssh_utils.do_cleanup(delete_keys, delete_cert, op_info.delete_credentials, op_info.cert_file,
                                 op_info.private_key_file, op_info.public_key_file)
        raise e

    op_call(op_info, delete_keys, delete_cert)


def _get_and_write_certificate(cmd, public_key_file, cert_file, ssh_client_folder):
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

    logger.debug("Generating certificate %s", cert_file)
    _write_cert_file(certificate, cert_file)
    # instead we use the validprincipals from the cert due to mismatched upn and email in guest scenarios
    username = ssh_utils.get_ssh_cert_principals(cert_file, ssh_client_folder)[0]
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

    if resource_type and \
       resource_type.lower() not in const.SUPPORTED_RESOURCE_TYPES and \
       resource_type.lower() not in const.LEGACY_SUPPORTED_RESOURCE_TYPES and \
       resource_type != const.ARC_RESOURCE_TYPE_PLACEHOLDER:
        raise azclierror.InvalidArgumentValueError("--resource-type must be either "
                                                   "\"Microsoft.Compute/virtualMachines\", "
                                                   "\"Microsoft.HybridCompute/machines\", "
                                                   "or \"Microsoft.ConnectedVMwarevSphere/virtualMachines\".")

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


def _check_or_create_public_private_files(public_key_file, private_key_file, credentials_folder,
                                          ssh_client_folder=None):
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
        ssh_utils.create_ssh_keyfile(private_key_file, ssh_client_folder)

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

    # Try to get private key if it's saved next to the public key. Not fail if it can't be found.
    if not private_key_file:
        if public_key_file.endswith(".pub"):
            private_key_file = public_key_file[:-4] if os.path.isfile(public_key_file[:-4]) else None

    return public_key_file, private_key_file, delete_keys


def _write_cert_file(certificate_contents, cert_file):
    with open(cert_file, 'w', encoding='utf-8') as f:
        f.write(f"ssh-rsa-cert-v01@openssh.com {certificate_contents}")
    oschmod.set_mode(cert_file, 0o644)
    return cert_file


def _get_modulus_exponent(public_key_file):
    if not os.path.isfile(public_key_file):
        raise azclierror.FileOperationError(f"Public key file '{public_key_file}' was not found")

    with open(public_key_file, 'r', encoding='utf-8') as f:
        public_key_text = f.read()

    parser = rsa_parser.RSAParser()
    try:
        parser.parse(public_key_text)
    except Exception as e:
        raise azclierror.FileOperationError(f"Could not parse public key. Error: {str(e)}")
    modulus = parser.modulus
    exponent = parser.exponent

    return modulus, exponent
