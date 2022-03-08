# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import hashlib
import json
import tempfile

import colorama
from colorama import Fore
from colorama import Style

from knack import log
from azure.cli.core import azclierror

from . import ip_utils
from . import rsa_parser
from . import ssh_utils
from . import ssh_info

logger = log.get_logger(__name__)


def ssh_vm(cmd, resource_group_name=None, vm_name=None, ssh_ip=None, public_key_file=None,
           private_key_file=None, use_private_ip=False, local_user=None, cert_file=None, port=None,
           ssh_client_folder=None, ssh_args=None):

    if '--debug' in cmd.cli_ctx.data['safe_params'] and set(['-v', '-vv', '-vvv']).isdisjoint(ssh_args):
        ssh_args = ['-v'] if not ssh_args else ['-v'] + ssh_args

    _assert_args(resource_group_name, vm_name, ssh_ip, cert_file, local_user)
    credentials_folder = None
    op_call = ssh_utils.start_ssh_connection
    ssh_session = ssh_info.SSHSession(resource_group_name, vm_name, ssh_ip, public_key_file,
                                      private_key_file, use_private_ip, local_user, cert_file, port,
                                      ssh_client_folder, ssh_args)
    _do_ssh_op(cmd, ssh_session, credentials_folder, op_call)


def ssh_config(cmd, config_path, resource_group_name=None, vm_name=None, ssh_ip=None,
               public_key_file=None, private_key_file=None, overwrite=False, use_private_ip=False,
               local_user=None, cert_file=None, port=None, credentials_folder=None, ssh_client_folder=None):

    _assert_args(resource_group_name, vm_name, ssh_ip, cert_file, local_user)
    # If user provides their own key pair, certificate will be written in the same folder as public key.
    if (public_key_file or private_key_file) and credentials_folder:
        raise azclierror.ArgumentUsageError("--keys-destination-folder can't be used in conjunction with "
                                            "--public-key-file/-p or --private-key-file/-i.")

    config_session = ssh_info.ConfigSession(config_path, resource_group_name, vm_name, ssh_ip, public_key_file,
                                            private_key_file, overwrite, use_private_ip, local_user, cert_file,
                                            port, ssh_client_folder)

    op_call = ssh_utils.write_ssh_config

    # if the folder doesn't exist, this extension won't create a new one.
    config_folder = os.path.dirname(config_session.config_path)
    if not os.path.isdir(config_folder):
        raise azclierror.InvalidArgumentValueError(f"Config file destination folder {config_folder} "
                                                   "does not exist.")

    # Default credential location
    # Add logic to test if credentials folder is valid
    if not credentials_folder:
        # * is not a valid name for a folder in Windows. Treat this as a special case.
        folder_name = config_session.ip if config_session.ip != "*" else "all_ips"
        if config_session.resource_group_name and config_session.vm_name:
            folder_name = config_session.resource_group_name + "-" + config_session.vm_name
        credentials_folder = os.path.join(config_folder, os.path.join("az_ssh_config", folder_name))
    else:
        credentials_folder = os.path.abspath(credentials_folder)

    _do_ssh_op(cmd, config_session, credentials_folder, op_call)


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

    colorama.init()
    # pylint: disable=broad-except
    try:
        cert_expiration = ssh_utils.get_certificate_start_and_end_times(cert_file, ssh_client_folder)[1]
        print(Fore.GREEN + f"Generated SSH certificate {cert_file} is valid until {cert_expiration} in local time."
              + Style.RESET_ALL)
    except Exception as e:
        logger.warning("Couldn't determine certificate validity. Error: %s", str(e))
        print(Fore.GREEN + f"Generated SSH certificate {cert_file}." + Style.RESET_ALL)


def _do_ssh_op(cmd, op_info, credentials_folder, op_call):
    # Get ssh_ip before getting public key to avoid getting "ResourceNotFound" exception after creating the keys
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
    # If user provides a local user, use the provided credentials for authentication
    if not op_info.local_user:
        delete_cert = True
        op_info.public_key_file, op_info.private_key_file, delete_keys = \
            _check_or_create_public_private_files(op_info.public_key_file,
                                                  op_info.private_key_file,
                                                  credentials_folder,
                                                  op_info.ssh_client_folder)

        op_info.cert_file, op_info.local_user = _get_and_write_certificate(cmd, op_info.public_key_file,
                                                                           None, op_info.ssh_client_folder)

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

    # We currently are using the presence of get_msal_token to detect if we are running on an older azure cli client
    # TODO: Remove when adal has been deprecated for a while
    if hasattr(profile, "get_msal_token"):
        # we used to use the username from the token but now we throw it away
        _, certificate = profile.get_msal_token(scopes, data)
    else:
        credential, _, _ = profile.get_login_credentials(subscription_id=profile.get_subscription()["id"])
        certificatedata = credential.get_token(*scopes, data=data)
        certificate = certificatedata.token

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


def _assert_args(resource_group, vm_name, ssh_ip, cert_file, username):
    if not (resource_group or vm_name or ssh_ip):
        raise azclierror.RequiredArgumentMissingError(
            "The VM must be specified by --ip or --resource-group and --vm-name/--name")

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
    # If nothing is passed, then create a directory with a ephemeral keypair
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

    return public_key_file, private_key_file, delete_keys


def _write_cert_file(certificate_contents, cert_file):
    with open(cert_file, 'w', encoding='utf-8') as f:
        f.write(f"ssh-rsa-cert-v01@openssh.com {certificate_contents}")

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
