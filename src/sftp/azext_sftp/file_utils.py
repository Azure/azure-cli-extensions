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
import oschmod

from azure.cli.core import azclierror
from azure.cli.core import telemetry
from azure.cli.core._profile import Profile
from knack import log

from . import constants as const
from . import rsa_parser
from . import sftp_utils

logger = log.get_logger(__name__)


def make_dirs_for_file(file_path):
    """Create directories for the given file path if they don't exist."""
    if not os.path.exists(file_path):
        mkdir_p(os.path.dirname(file_path))


def mkdir_p(path):
    """Create directory and all parent directories if they don't exist."""
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST or not os.path.isdir(path):
            raise


def delete_file(file_path, message, warning=False):
    """Delete a file with error handling."""
    if os.path.isfile(file_path):
        # pylint: disable=broad-except
        try:
            os.remove(file_path)
        except Exception as e:
            if warning:
                logger.warning(message)
            else:
                raise azclierror.FileOperationError(f"{message}Error: {str(e)}") from e


def delete_folder(dir_path, message, warning=False):
    """Delete a folder with error handling."""
    if os.path.isdir(dir_path):
        # pylint: disable=broad-except
        try:
            os.rmdir(dir_path)
        except Exception as e:
            if warning:
                logger.warning(message)
            else:
                raise azclierror.FileOperationError(f"{message}Error: {str(e)}") from e


def create_directory(file_path, error_message):
    """Create a directory with error handling."""
    try:
        os.makedirs(file_path)
    except Exception as e:
        raise azclierror.FileOperationError(f"{error_message}Error: {str(e)}") from e


def write_to_file(file_path, mode, content, error_message, encoding=None):
    """Write content to a file with error handling."""
    try:
        with open(file_path, mode, encoding=encoding) as f:
            f.write(content)
    except Exception as e:
        raise azclierror.FileOperationError(f"{error_message}Error: {str(e)}") from e


def get_line_that_contains(substring, lines):
    """Find the first line containing the substring."""
    return next((line for line in lines if substring in line), None)


def remove_invalid_characters_foldername(folder_name):
    """Remove invalid characters from folder name for Windows compatibility."""
    return ''.join(c for c in folder_name if c not in const.WINDOWS_INVALID_FOLDERNAME_CHARS)


def check_or_create_public_private_files(public_key_file, private_key_file, credentials_folder, ssh_client_folder=None):
    """Check for existing key files or create new ones if needed."""
    delete_keys = False

    if not public_key_file and not private_key_file:
        if not credentials_folder:
            credentials_folder = tempfile.mkdtemp(prefix="aadsftpcert")
        else:
            if not os.path.isdir(credentials_folder):
                os.makedirs(credentials_folder)
        
        public_key_file = os.path.join(credentials_folder, "id_rsa.pub")
        private_key_file = os.path.join(credentials_folder, "id_rsa")
        
        # Check if existing keys are present before generating new ones
        if not (os.path.isfile(public_key_file) and os.path.isfile(private_key_file)):
            # Only generate new keys if both don't exist
            sftp_utils.create_ssh_keyfile(private_key_file, ssh_client_folder)
            # Only set delete_keys to True when we actually create new keys
            delete_keys = True
        # If existing keys are found, delete_keys remains False

    if not public_key_file:
        if private_key_file:
            public_key_file = str(private_key_file) + ".pub"
        else:
            raise azclierror.RequiredArgumentMissingError("Public key file not specified")

    if not os.path.isfile(public_key_file):
        raise azclierror.FileOperationError(f"Public key file {public_key_file} not found")

    if private_key_file:
        if not os.path.isfile(private_key_file):
            raise azclierror.FileOperationError(f"Private key file {private_key_file} not found")

    if not private_key_file:
        if public_key_file.endswith(".pub"):
            private_key_file = public_key_file[:-4] if os.path.isfile(public_key_file[:-4]) else None

    return public_key_file, private_key_file, delete_keys


def get_and_write_certificate(cmd, public_key_file, cert_file, ssh_client_folder):
    """Generate and write an SSH certificate using Azure AD authentication."""
    cloud_scopes = {
        "azurecloud": "https://pas.windows.net/CheckMyAccess/Linux/.default",
        "azurechinacloud": "https://pas.chinacloudapi.cn/CheckMyAccess/Linux/.default",
        "azureusgovernment": "https://pasff.usgovcloudapi.net/CheckMyAccess/Linux/.default"
    }

    scope = cloud_scopes.get(cmd.cli_ctx.cloud.name.lower())
    if not scope:
        raise azclierror.InvalidArgumentValueError(
            f"Unsupported cloud {cmd.cli_ctx.cloud.name.lower()}",
            "Supported clouds include azurecloud,azurechinacloud,azureusgovernment")

    data = _prepare_jwk_data(public_key_file)
    profile = Profile(cli_ctx=cmd.cli_ctx)
    t0 = time.time()

    if hasattr(profile, "get_msal_token"):
        _, certificate = profile.get_msal_token([scope], data)
    else:
        credential, _, _ = profile.get_login_credentials(subscription_id=profile.get_subscription()["id"])
        certificatedata = credential.get_token(scope, data=data)
        certificate = certificatedata.token

    time_elapsed = time.time() - t0
    telemetry.add_extension_event('sftp', {'Context.Default.AzureCLI.SFTPGetCertificateTime': time_elapsed})

    if not cert_file:
        cert_file = str(public_key_file.removesuffix(".pub")) + "-aadcert.pub"

    logger.debug("Generating certificate %s", cert_file)
    _write_cert_file(certificate, cert_file)
    username = sftp_utils.get_ssh_cert_principals(cert_file, ssh_client_folder)[0]
    oschmod.set_mode(cert_file, 0o600)

    return cert_file, username.lower()


def _prepare_jwk_data(public_key_file):
    """Prepare JWK data for certificate request."""
    modulus, exponent = _get_modulus_exponent(public_key_file)
    key_hash = hashlib.sha256()
    key_hash.update(modulus.encode('utf-8'))
    key_hash.update(exponent.encode('utf-8'))
    key_id = key_hash.hexdigest()

    jwk = {"kty": "RSA", "n": modulus, "e": exponent, "kid": key_id}

    return {
        "token_type": "ssh-cert",
        "req_cnf": json.dumps(jwk),
        "key_id": key_id
    }


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
