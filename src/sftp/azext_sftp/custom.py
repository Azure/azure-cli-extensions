# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import hashlib
import json
import tempfile
import time
import datetime
import shutil
import oschmod

from knack import log
from azure.cli.core import azclierror
from azure.cli.core import telemetry
from azure.cli.core.style import Style, print_styled_text
from azure.cli.core._profile import Profile

from . import rsa_parser
from . import sftp_info
from . import sftp_utils
from . import file_utils
from . import constants as const

logger = log.get_logger(__name__)


def sftp_cert(cmd, cert_path=None, public_key_file=None, ssh_client_folder=None):
    """
    Generate SSH certificate for SFTP authentication using Azure AD.

    Args:
        cmd: CLI command context
        cert_path: Path where the certificate should be written
        public_key_file: Path to existing RSA public key file
        ssh_client_folder: Path to SSH client executables directory

    Returns:
        None

    Raises:
        RequiredArgumentMissingError: When required arguments are missing
        InvalidArgumentValueError: When provided paths are invalid
    """
    logger.debug("Starting SFTP certificate generation")

    if not cert_path and not public_key_file:
        raise azclierror.RequiredArgumentMissingError("--file or --public-key-file must be provided.")

    if cert_path and not os.path.isdir(os.path.dirname(cert_path)):
        raise azclierror.InvalidArgumentValueError(f"{os.path.dirname(cert_path)} folder doesn't exist")

    # Normalize paths to absolute paths
    if public_key_file:
        public_key_file = os.path.abspath(public_key_file)
        logger.debug("Using public key file: %s", public_key_file)
    if cert_path:
        cert_path = os.path.abspath(cert_path)
        logger.debug("Certificate will be written to: %s", cert_path)
    if ssh_client_folder:
        ssh_client_folder = os.path.abspath(ssh_client_folder)
        logger.debug("Using SSH client folder: %s", ssh_client_folder)

    # If user doesn't provide a public key, save generated key pair to the same folder as --file
    keys_folder = None
    if not public_key_file:
        keys_folder = os.path.dirname(cert_path)
        logger.debug("Will generate key pair in: %s", keys_folder)

    try:
        public_key_file, _, _ = _check_or_create_public_private_files(public_key_file, None, keys_folder, ssh_client_folder)
        # certificate generated here
        cert_file, _ = _get_and_write_certificate(cmd, public_key_file, cert_path, ssh_client_folder)
    except Exception as e:
        logger.error("Failed to generate certificate: %s", str(e))
        raise

    if keys_folder:
        logger.warning("%s contains sensitive information (id_rsa, id_rsa.pub). "
                       "Please delete once this certificate is no longer being used.", keys_folder)
    # pylint: disable=broad-except
    try:
        cert_expiration = sftp_utils.get_certificate_start_and_end_times(cert_file, ssh_client_folder)[1]
        print_styled_text((Style.SUCCESS,
                           f"Generated SSH certificate {cert_file} is valid until {cert_expiration} in local time."))
    except Exception as e:
        logger.warning("Couldn't determine certificate validity. Error: %s", str(e))
        print_styled_text((Style.SUCCESS, f"Generated SSH certificate {cert_file}."))


def sftp_connect(cmd, storage_account, port=None, cert_file=None, private_key_file=None, public_key_file=None, sftp_args=None, ssh_client_folder=None, sftp_batch_commands=None):
    """
    Connect to Azure Storage Account via SFTP with automatic certificate generation if needed.

    Args:
        cmd: CLI command context
        storage_account: Azure Storage Account name or resource ID
        port: SFTP port number (default: 22)
        cert_file: Path to SSH certificate file
        private_key_file: Path to SSH private key file
        public_key_file: Path to SSH public key file
        sftp_args: Additional SFTP client arguments
        ssh_client_folder: Path to SSH client executables
        sftp_batch_commands: Non-interactive SFTP commands to execute

    Returns:
        None

    Raises:
        Various Azure CLI errors for validation and connection issues
    """
    logger.debug("Starting SFTP connection to storage account: %s", storage_account)

    # Validate input parameters
    _assert_args(storage_account, cert_file, public_key_file, private_key_file)

    # Allow connection with no credentials for fully managed experience
    auto_generate_cert = False
    delete_keys = False
    delete_cert = False
    credentials_folder = None

    if not cert_file and not public_key_file and not private_key_file:
        logger.info("Fully managed mode: No credentials provided")
        print_styled_text((Style.ACTION, "Fully managed mode: No credentials provided."))
        print_styled_text((Style.ACTION, "Generating SSH key pair and certificate automatically..."))
        print_styled_text((Style.WARNING, "Note: Generated credentials will be cleaned up after connection."))
        auto_generate_cert = True
        delete_cert = True
        delete_keys = True
        credentials_folder = tempfile.mkdtemp(prefix="aadsftp")

    if cert_file and public_key_file:
        print_styled_text((Style.WARNING, "Both --certificate-file and --public-key-file provided. Using --certificate-file."))
        print_styled_text((Style.ACTION, "To use public key instead, omit --certificate-file parameter."))

    try:        # Get or create keys/certificate
        if auto_generate_cert:
            public_key_file, private_key_file, _ = _check_or_create_public_private_files(None, None, credentials_folder, ssh_client_folder)
            cert_file, user = _get_and_write_certificate(cmd, public_key_file, None, ssh_client_folder)
        elif not cert_file:
            public_key_file, private_key_file, _ = _check_or_create_public_private_files(public_key_file, private_key_file, None, ssh_client_folder)
            print_styled_text((Style.ACTION, "Generating SSH certificate..."))
            cert_file, user = _get_and_write_certificate(cmd, public_key_file, None, ssh_client_folder)
            delete_cert = True
        else:
            # Validate existing certificate
            logger.debug("Validating provided certificate file...")
            if not os.path.isfile(cert_file):
                raise azclierror.FileOperationError(f"Certificate file {cert_file} not found.")

            # Check certificate validity
            try:
                logger.debug("Checking certificate validity...")
                times = sftp_utils.get_certificate_start_and_end_times(cert_file, ssh_client_folder)
                if times and times[1] < datetime.datetime.now():
                    print_styled_text((Style.WARNING, f"Certificate {cert_file} has expired. Generating new certificate..."))
                    # Extract public key from existing cert and generate new one
                    temp_dir = tempfile.mkdtemp(prefix="aadsftp")
                    public_key_file = os.path.join(temp_dir, "id_rsa.pub")
                    private_key_file = os.path.join(temp_dir, "id_rsa")
                    sftp_utils.create_ssh_keyfile(private_key_file, ssh_client_folder)
                    cert_file, user = _get_and_write_certificate(cmd, public_key_file, None, ssh_client_folder)
                    delete_cert = True
                    delete_keys = True
                else:
                    user = sftp_utils.get_ssh_cert_principals(cert_file, ssh_client_folder)[0].lower()
            except Exception as e:
                logger.warning("Could not validate certificate: %s. Proceeding with provided certificate.", str(e))
                user = sftp_utils.get_ssh_cert_principals(cert_file, ssh_client_folder)[0].lower()

        # Process username - extract username part if it's a UPN
        if '@' in user:
            user = user.split('@')[0]

        # Build Azure Storage SFTP username format
        username = f"{storage_account}.{user}"

        # Use cloud-aware hostname resolution
        storage_suffix = _get_storage_endpoint_suffix(cmd)
        hostname = f"{storage_account}.{storage_suffix}"

        # Inform user about connection details
        print_styled_text((Style.ACTION, "Azure Storage SFTP Connection Details:"))
        print_styled_text((Style.PRIMARY, f"  Storage Account: {storage_account}"))
        print_styled_text((Style.PRIMARY, f"  Username: {username}"))
        if port is not None:
            print_styled_text((Style.PRIMARY, f"  Endpoint: {hostname}:{port}"))
        else:
            print_styled_text((Style.PRIMARY, f"  Endpoint: {hostname} (default SSH port)"))
        print_styled_text((Style.PRIMARY, f"  Cloud Environment: {cmd.cli_ctx.cloud.name}"))

        sftp_session = sftp_info.SFTPSession(
            storage_account=storage_account,
            username=username,
            host=hostname,
            port=port,
            cert_file=cert_file,
            private_key_file=private_key_file,
            sftp_args=sftp_args,
            ssh_client_folder=ssh_client_folder,
            ssh_proxy_folder=None,
            credentials_folder=credentials_folder,
            yes_without_prompt=False,
            sftp_batch_commands=sftp_batch_commands
        )

        # Set local user for username resolution
        sftp_session.local_user = user
        sftp_session.resolve_connection_info()

        print_styled_text((Style.SUCCESS, "Establishing SFTP connection..."))
        _do_sftp_op(cmd, sftp_session, sftp_utils.start_sftp_connection)

    except Exception as e:
        # Clean up generated credentials on error
        if delete_keys or delete_cert:
            logger.debug("An error occurred. Cleaning up generated credentials.")
            _cleanup_credentials(delete_keys, delete_cert, credentials_folder, cert_file, private_key_file, public_key_file)
        raise e
    finally:
        # Clean up generated credentials after successful connection
        if delete_keys or delete_cert:
            _cleanup_credentials(delete_keys, delete_cert, credentials_folder, cert_file, private_key_file, public_key_file)

# Helpers


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
    from azure.cli.core._profile import Profile
    profile = Profile(cli_ctx=cmd.cli_ctx)

    t0 = time.time()
    # Use MSAL token for modern Azure CLI authentication
    if hasattr(profile, "get_msal_token"):
        _, certificate = profile.get_msal_token(scopes, data)
    else:
        # Fallback for older Azure CLI versions
        credential, _, _ = profile.get_login_credentials(subscription_id=profile.get_subscription()["id"])
        certificatedata = credential.get_token(*scopes, data=data)
        certificate = certificatedata.token

    time_elapsed = time.time() - t0
    telemetry.add_extension_event('sftp', {'Context.Default.AzureCLI.SftpGetCertificateTime': time_elapsed})

    if not cert_file:
        # Remove any existing file extension before adding the certificate suffix
        base_name = os.path.splitext(str(public_key_file))[0]
        cert_file = base_name + "-aadcert.pub"

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


def _assert_args(storage_account, cert_file, public_key_file, private_key_file):
    """Validate SFTP connection arguments, following SSH extension patterns."""
    if not storage_account:
        raise azclierror.RequiredArgumentMissingError("Storage account name is required.")

    if cert_file and not os.path.isfile(cert_file):
        raise azclierror.FileOperationError(f"Certificate file {cert_file} not found.")

    if public_key_file and not os.path.isfile(public_key_file):
        raise azclierror.FileOperationError(f"Public key file {public_key_file} not found.")

    if private_key_file and not os.path.isfile(private_key_file):
        raise azclierror.FileOperationError(f"Private key file {private_key_file} not found.")


def _do_sftp_op(cmd, sftp_session, op_call):
    """Execute SFTP operation with session, similar to SSH extension's _do_ssh_op."""
    # Validate session before operation
    sftp_session.validate_session()

    # Call the actual operation (connection, etc.)
    return op_call(sftp_session)


def _cleanup_credentials(delete_keys, delete_cert, credentials_folder, cert_file, private_key_file, public_key_file):
    """Clean up generated credentials similar to SSH extension pattern."""
    try:
        if delete_cert and cert_file and os.path.isfile(cert_file):
            file_utils.delete_file(cert_file, f"Deleting generated certificate {cert_file}", warning=False)

        if delete_keys:
            if private_key_file and os.path.isfile(private_key_file):
                file_utils.delete_file(private_key_file, f"Deleting generated private key {private_key_file}", warning=False)
            if public_key_file and os.path.isfile(public_key_file):
                file_utils.delete_file(public_key_file, f"Deleting generated public key {public_key_file}", warning=False)

        if credentials_folder and os.path.isdir(credentials_folder):
            logger.debug("Deleting credentials folder %s", credentials_folder)
            shutil.rmtree(credentials_folder)

    except OSError as e:
        logger.warning("Failed to clean up credentials: %s", str(e))


def _get_storage_endpoint_suffix(cmd):
    """Get the appropriate storage endpoint suffix based on Azure cloud environment.

    This follows the same pattern as the SSH extension for cloud environment handling.
    """
    cloud_to_storage_suffix = {
        "azurecloud": "blob.core.windows.net",
        "azurechinacloud": "blob.core.chinacloudapi.cn",
        "azureusgovernment": "blob.core.usgovcloudapi.net"
    }
    return cloud_to_storage_suffix.get(cmd.cli_ctx.cloud.name.lower(), "blob.core.windows.net")
