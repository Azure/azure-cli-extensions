# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import hashlib
import json
import tempfile
import time
import oschmod
import subprocess

from knack import log
from azure.cli.core import azclierror
from azure.cli.core import telemetry
from azure.cli.core.style import Style, print_styled_text
from azure.cli.core._profile import Profile

from . import rsa_parser
from . import sftp_info
from . import sftp_utils

logger = log.get_logger(__name__)

def sftp_cert(cmd, cert_path=None, public_key_file=None):
    if not cert_path and not public_key_file:
        raise azclierror.RequiredArgumentMissingError("--file or --public-key-file must be provided.")
    if cert_path and not os.path.isdir(os.path.dirname(cert_path)):
        raise azclierror.InvalidArgumentValueError(f"{os.path.dirname(cert_path)} folder doesn't exist")

    if public_key_file:
        public_key_file = os.path.abspath(public_key_file)
    if cert_path:
        cert_path = os.path.abspath(cert_path)

    # If user doesn't provide a public key, save generated key pair to the same folder as --file
    keys_folder = None
    if not public_key_file:
        keys_folder = os.path.dirname(cert_path)

    public_key_file, _, _ = _check_or_create_public_private_files(public_key_file, None, keys_folder, None)
    # certificate generated here
    cert_file, _ = _get_and_write_certificate(cmd, public_key_file, cert_path, None)

    if keys_folder:
        logger.warning("%s contains sensitive information (id_rsa, id_rsa.pub). "
                       "Please delete once this certificate is no longer being used.", keys_folder)
    # pylint: disable=broad-except
    try:
        cert_expiration = sftp_utils.get_certificate_start_and_end_times(cert_file, None)[1]
        print_styled_text((Style.SUCCESS,
                           f"Generated SSH certificate {cert_file} is valid until {cert_expiration} in local time."))
    except Exception as e:
        logger.warning("Couldn't determine certificate validity. Error: %s", str(e))
        print_styled_text((Style.SUCCESS, f"Generated SSH certificate {cert_file}."))


def sftp_connect(cmd, storage_account, port = 10122, cert_file=None, private_key_file=None, public_key_file=None, host_override=None, sftp_args=None):
    # user cert if provided, otherwise generate one
    if not cert_file and not public_key_file:
        raise azclierror.RequiredArgumentMissingError("Either --cert-file or --public-key-file must be provided.")
    
    if cert_file and public_key_file:
        print_styled_text((Style.WARNING, "Both --cert-file and --public-key-file provided. Using --cert-file."))

    public_key_file, _, _ = _check_or_create_public_private_files(public_key_file, None, None, None)
    # this causes 'unprotected private key file' failure:
    cert_file, user = _get_and_write_certificate(cmd, public_key_file, None, None)
    #if not cert_file:
    #print_styled_text((Style.WARNING, "Generating SSH certificate..."))

    if '@' in user: user = user.split('@')[0] # only use username part of UPN
    username = storage_account + "." + user + "###OAuthSettingsOverride=True;OAuthTenantId=44f1980d-fc79-4cda-a367-883a275a4800;OAuthAppId=f33b34cb-1069-40dc-9873-50b2d4b6e881;OAuthSrpAppId=233acdea-7279-4f7b-92ce-180145123ba5;"

    sftp_session = sftp_info.SFTPSession(cert_file, private_key_file, username, host_override, port, None, None, None)
    print_styled_text((Style.SUCCESS, f"Connecting to {storage_account}..."))
    sftp_utils.start_sftp_connection(sftp_session)


### Helpers ###
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
        sftp_utils.create_ssh_keyfile(private_key_file, ssh_client_folder)

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

def _get_and_write_certificate(cmd, public_key_file, cert_file, ssh_client_folder):
    # should this include agc URIs?
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
    profile = Profile(cli_ctx=cmd.cli_ctx)

    t0 = time.time()
    # We currently are using the presence of get_msal_token to detect if we are running on an older azure cli client
    # TODO: Remove when adal has been deprecated for a while
    if hasattr(profile, "get_msal_token"):
        # we used to use the username from the token but now we throw it away
        _, certificate = profile.get_msal_token(scopes, data)
    else:
        # likely uses this path
        # credentia.get_token().token is the certificate
        credential, _, _ = profile.get_login_credentials(subscription_id=profile.get_subscription()["id"])
        certificatedata = credential.get_token(*scopes, data=data)
        certificate = certificatedata.token

    time_elapsed = time.time() - t0
    telemetry.add_extension_event('ssh', {'Context.Default.AzureCLI.SSHGetCertificateTime': time_elapsed})

    if not cert_file:
        cert_file = public_key_file + "-aadcert.pub"

    logger.debug("Generating certificate %s", cert_file)
    # cert written to here
    _write_cert_file(certificate, cert_file)
    # instead we use the validprincipals from the cert due to mismatched upn and email in guest scenarios
    username = sftp_utils.get_ssh_cert_principals(cert_file, ssh_client_folder)[0]
    # remove all permissions from the cert file except for read/write for the owner to avoid 'unprotected private key file' failure
    oschmod.set_mode(cert_file, 0o600)

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