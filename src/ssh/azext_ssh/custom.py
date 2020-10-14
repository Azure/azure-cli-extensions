# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import functools
import os
import hashlib
import json
import tempfile

from knack import util

from . import ip_utils
from . import rsa_parser
from . import ssh_utils


def ssh_vm(cmd, resource_group_name=None, vm_name=None, ssh_ip=None, public_key_file=None, private_key_file=None):
    _do_ssh_op(cmd, resource_group_name, vm_name, ssh_ip,
               public_key_file, private_key_file, ssh_utils.start_ssh_connection)


def ssh_config(cmd, config_path, resource_group_name=None, vm_name=None, ssh_ip=None,
               public_key_file=None, private_key_file=None):
    op_call = functools.partial(ssh_utils.write_ssh_config, config_path, resource_group_name, vm_name)
    _do_ssh_op(cmd, resource_group_name, vm_name, ssh_ip, public_key_file, private_key_file, op_call)


def ssh_cert(cmd, cert_path=None, public_key_file=None):
    public_key_file, _ = _check_or_create_public_private_files(public_key_file, None)
    cert_file, _ = _get_and_write_certificate(cmd, public_key_file, cert_path)
    print(cert_file + "\n")


def _do_ssh_op(cmd, resource_group, vm_name, ssh_ip, public_key_file, private_key_file, op_call):
    _assert_args(resource_group, vm_name, ssh_ip)
    public_key_file, private_key_file = _check_or_create_public_private_files(public_key_file, private_key_file)
    ssh_ip = ssh_ip or ip_utils.get_ssh_ip(cmd, resource_group, vm_name)

    if not ssh_ip:
        raise util.CLIError(f"VM '{vm_name}' does not have a public IP address to SSH to")

    cert_file, username = _get_and_write_certificate(cmd, public_key_file, None)
    op_call(ssh_ip, username, cert_file, private_key_file)


def _get_and_write_certificate(cmd, public_key_file, cert_file):
    scopes = ["https://pas.windows.net/CheckMyAccess/Linux/user_impersonation"]
    data = _prepare_jwk_data(public_key_file)
    from azure.cli.core._profile import Profile
    profile = Profile(cli_ctx=cmd.cli_ctx)
    username, certificate = profile.get_msal_token(scopes, data)
    if not cert_file:
        cert_file = public_key_file + "-aadcert.pub"
    return _write_cert_file(certificate, cert_file), username


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
        raise util.CLIError("The VM must be specified by --ip or --resource-group and --name")

    if resource_group and not vm_name or vm_name and not resource_group:
        raise util.CLIError("--resource-group and --name must be provided together")

    if ssh_ip and (vm_name or resource_group):
        raise util.CLIError("--ip cannot be used with --resource-group or --name")


def _check_or_create_public_private_files(public_key_file, private_key_file):
    # If nothing is passed in create a temporary directory with a ephemeral keypair
    if not public_key_file and not private_key_file:
        temp_dir = tempfile.mkdtemp(prefix="aadsshcert")
        public_key_file = os.path.join(temp_dir, "id_rsa.pub")
        private_key_file = os.path.join(temp_dir, "id_rsa")
        ssh_utils.create_ssh_keyfile(private_key_file)

    if not os.path.isfile(public_key_file):
        raise util.CLIError(f"Public key file {public_key_file} not found")

    # The private key is not required as the user may be using a keypair
    # stored in ssh-agent (and possibly in a hardware token)
    if private_key_file:
        if not os.path.isfile(private_key_file):
            raise util.CLIError(f"Private key file {private_key_file} not found")

    return public_key_file, private_key_file


def _write_cert_file(certificate_contents, cert_file):
    with open(cert_file, 'w') as f:
        f.write(f"ssh-rsa-cert-v01@openssh.com {certificate_contents}")

    return cert_file


def _get_modulus_exponent(public_key_file):
    if not os.path.isfile(public_key_file):
        raise util.CLIError(f"Public key file '{public_key_file}' was not found")

    with open(public_key_file, 'r') as f:
        public_key_text = f.read()

    parser = rsa_parser.RSAParser()
    try:
        parser.parse(public_key_text)
    except Exception as e:
        raise util.CLIError(f"Could not parse public key. Error: {str(e)}")
    modulus = parser.modulus
    exponent = parser.exponent

    return modulus, exponent
