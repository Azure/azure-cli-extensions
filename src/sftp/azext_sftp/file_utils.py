# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import errno
import os
import hashlib
import json
import tempfile
import time
import datetime
import oschmod
import shutil

from azure.cli.core import azclierror
from azure.cli.core import telemetry
from azure.cli.core._profile import Profile
from knack import log

from . import constants as const
from . import rsa_parser
from . import sftp_utils

logger = log.get_logger(__name__)


def make_dirs_for_file(file_path):
    if not os.path.exists(file_path):
        mkdir_p(os.path.dirname(file_path))


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python <= 2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def delete_file(file_path, message, warning=False):
    # pylint: disable=broad-except
    if os.path.isfile(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            if warning:
                logger.warning(message)
            else:
                raise azclierror.FileOperationError(message + "Error: " + str(e)) from e


def delete_folder(dir_path, message, warning=False):
    # pylint: disable=broad-except
    if os.path.isdir(dir_path):
        try:
            os.rmdir(dir_path)
        except Exception as e:
            if warning:
                logger.warning(message)
            else:
                raise azclierror.FileOperationError(message + "Error: " + str(e)) from e


def create_directory(file_path, error_message):
    try:
        os.makedirs(file_path)
    except Exception as e:
        raise azclierror.FileOperationError(error_message + "Error: " + str(e)) from e


def write_to_file(file_path, mode, content, error_message, encoding=None):
    # pylint: disable=unspecified-encoding
    try:
        if encoding:
            with open(file_path, mode, encoding=encoding) as f:
                f.write(content)
        else:
            with open(file_path, mode) as f:
                f.write(content)
    except Exception as e:
        raise azclierror.FileOperationError(error_message + "Error: " + str(e)) from e


def get_line_that_contains(substring, lines):
    for line in lines:
        if substring in line:
            return line
    return None


def remove_invalid_characters_foldername(folder_name):
    new_foldername = ""
    for c in folder_name:
        if c not in const.WINDOWS_INVALID_FOLDERNAME_CHARS:
            new_foldername += c
    return new_foldername


def check_or_create_public_private_files(public_key_file, private_key_file, credentials_folder, ssh_client_folder=None):
    """Check for existing key files or create new ones if needed."""
    delete_keys = False

    # If nothing is passed in create a temporary directory with a ephemeral keypair
    if not public_key_file and not private_key_file:
        # We only want to delete the keys if the user hasn't provided their own keys
        delete_keys = True
        if not credentials_folder:
            # Create keys on temp folder and delete folder once connection succeeds/fails.
            credentials_folder = tempfile.mkdtemp(prefix="aadsftpcert")
        else:
            # Keys saved to the same folder as --file or to --keys-destination-folder.
            if not os.path.isdir(credentials_folder):
                os.makedirs(credentials_folder)
        public_key_file = os.path.join(credentials_folder, "id_rsa.pub")
        private_key_file = os.path.join(credentials_folder, "id_rsa")
        sftp_utils.create_ssh_keyfile(private_key_file, ssh_client_folder)

    if not public_key_file:
        if private_key_file:
            public_key_file = str(private_key_file) + ".pub"
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


def get_and_write_certificate(cmd, public_key_file, cert_file, ssh_client_folder):
    """Generate and write an SSH certificate using Azure AD authentication."""
    # Map cloud names to scopes
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

    # Get certificate using MSAL token
    if hasattr(profile, "get_msal_token"):
        # we used to use the username from the token but now we throw it away
        _, certificate = profile.get_msal_token(scopes, data)
    else:
        # Fallback for older CLI versions
        credential, _, _ = profile.get_login_credentials(subscription_id=profile.get_subscription()["id"])
        certificatedata = credential.get_token(*scopes, data=data)
        certificate = certificatedata.token

    time_elapsed = time.time() - t0
    telemetry.add_extension_event('sftp', {'Context.Default.AzureCLI.SFTPGetCertificateTime': time_elapsed})

    if not cert_file:
        cert_file = str(public_key_file) + "-aadcert.pub"

    logger.debug("Generating certificate %s", cert_file)

    # Write certificate to file
    _write_cert_file(certificate, cert_file)

    # Get username from certificate principals
    username = sftp_utils.get_ssh_cert_principals(cert_file, ssh_client_folder)[0]

    # Set appropriate permissions
    oschmod.set_mode(cert_file, 0o600)

    return cert_file, username.lower()


def _prepare_jwk_data(public_key_file):
    """Prepare JWK data for certificate request."""
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
    """Write SSH certificate to file."""
    with open(cert_file, 'w', encoding='utf-8') as f:
        f.write(f"ssh-rsa-cert-v01@openssh.com {certificate_contents}")
    oschmod.set_mode(cert_file, 0o644)
    return cert_file


def _get_modulus_exponent(public_key_file):
    """Extract modulus and exponent from RSA public key file."""
    if not os.path.isfile(public_key_file):
        raise azclierror.FileOperationError(f"Public key file '{public_key_file}' was not found")

    with open(public_key_file, 'r', encoding='utf-8') as f:
        public_key_text = f.read()

    parser = rsa_parser.RSAParser()
    try:
        parser.parse(public_key_text)
    except Exception as e:
        raise azclierror.FileOperationError(f"Could not parse public key. Error: {str(e)}")

    return parser.modulus, parser.exponent


def validate_certificate(cert_file, ssh_client_folder=None):
    """Validate an SSH certificate and check its expiration."""
    if not os.path.isfile(cert_file):
        raise azclierror.FileOperationError(f"Certificate file {cert_file} not found.")

    try:
        times = sftp_utils.get_certificate_start_and_end_times(cert_file, ssh_client_folder)
        if times and times[1] < datetime.datetime.now():
            return False, "Certificate has expired"
        return True, "Certificate is valid"
    except Exception as e:
        logger.warning("Could not validate certificate: %s", str(e))
        return None, str(e)
