# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import functools
import os
import hashlib
import json
import tempfile

from azure.cli.core import azclierror

from . import ip_utils
from . import rsa_parser
from . import ssh_utils


def ssh_vm(cmd, resource_group_name=None, vm_name=None, ssh_ip=None, public_key_file=None,
           private_key_file=None, use_private_ip=False, port=None, ssh_args=None):
    credentials_folder = None
    is_config = False
    op_call = functools.partial(ssh_utils.start_ssh_connection, port, ssh_args)
    _do_ssh_op(cmd, resource_group_name, vm_name, ssh_ip,
               public_key_file, private_key_file, use_private_ip, credentials_folder, is_config, op_call)


def ssh_config(cmd, config_path, resource_group_name=None, vm_name=None, ssh_ip=None,
               public_key_file=None, private_key_file=None, overwrite=False, use_private_ip=False, credentials_folder=None):
    op_call = functools.partial(ssh_utils.write_ssh_config, config_path, resource_group_name, vm_name, overwrite)
    is_config = True
    # Default credential location
    if not credentials_folder:
        config_folder = os.path.dirname(config_path)
        folder_name = resource_group_name + "-" + vm_name
        credentials_folder = os.path.join(config_folder, os.path.join("az_ssh_config", folder_name))

    _do_ssh_op(cmd, resource_group_name, vm_name, ssh_ip, public_key_file, private_key_file, use_private_ip, credentials_folder, is_config, op_call)


def ssh_cert(cmd, cert_path=None, public_key_file=None):
    public_key_file, _ = _check_or_create_public_private_files(public_key_file, None)
    cert_file, _ = _get_and_write_certificate(cmd, public_key_file, cert_path)
    print(cert_file + "\n")


def _do_ssh_op(cmd, resource_group, vm_name, ssh_ip, public_key_file, private_key_file, use_private_ip, credentials_folder, is_config, op_call):
    _assert_args(resource_group, vm_name, ssh_ip)
    ssh_ip = ssh_ip or ip_utils.get_ssh_ip(cmd, resource_group, vm_name, use_private_ip)

    if not ssh_ip:
        if not use_private_ip:
            raise azclierror.ResourceNotFoundError(f"VM '{vm_name}' does not have a public IP address to SSH to")

        raise azclierror.ResourceNotFoundError(f"VM '{vm_name}' does not have a public or private IP address to SSH to")

    # Get ssh_ip before getting public key to avoid getting "ResourceNotFound" exception after creating the keys
    public_key_file, private_key_file, delete_keys = _check_or_create_public_private_files(public_key_file, private_key_file, credentials_folder, is_config)
    cert_file, username = _get_and_write_certificate(cmd, public_key_file, None)
    op_call(ssh_ip, username, cert_file, private_key_file, delete_keys)


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


def _assert_args(resource_group, vm_name, ssh_ip):
    if not (resource_group or vm_name or ssh_ip):
        raise azclierror.RequiredArgumentMissingError(
            "The VM must be specified by --ip or --resource-group and --vm-name/--name")

    if resource_group and not vm_name or vm_name and not resource_group:
        raise azclierror.MutuallyExclusiveArgumentError(
            "--resource-group and --vm-name/--name must be provided together")

    if ssh_ip and (vm_name or resource_group):
        raise azclierror.MutuallyExclusiveArgumentError(
            "--ip cannot be used with --resource-group or --vm-name/--name")


def _check_or_create_public_private_files(public_key_file, private_key_file, credentials_folder, is_config):
    delete_keys = False
    # If nothing is passed in create a temporary directory with a ephemeral keypair
    if not public_key_file and not private_key_file:
        # We only want to delete the keys if the user hasn't providede their own keys
        delete_keys = True
        if not is_config:
            # az ssh vm: Create keys on temp folder and delete folder once connection is established.
            credentials_folder = tempfile.mkdtemp(prefix="aadsshcert")
        else:
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
