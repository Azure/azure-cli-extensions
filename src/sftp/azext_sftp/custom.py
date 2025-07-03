# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import hashlib
import json
import tempfile
import time
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

logger = log.get_logger(__name__)


def sftp_cert(cmd, cert_path=None, public_key_file=None, ssh_client_folder=None):
    """Generate SSH certificate for SFTP authentication using Azure AD."""
    logger.debug("Starting SFTP certificate generation")

    if not cert_path and not public_key_file:
        raise azclierror.RequiredArgumentMissingError("--file or --public-key-file must be provided.")

    if cert_path:
        cert_path = os.path.expanduser(cert_path)
    if public_key_file:
        public_key_file = os.path.expanduser(public_key_file)
    if ssh_client_folder:
        ssh_client_folder = os.path.expanduser(ssh_client_folder)

    if cert_path and not os.path.isdir(os.path.dirname(cert_path)):
        raise azclierror.InvalidArgumentValueError(f"{os.path.dirname(cert_path)} folder doesn't exist")

    if public_key_file:
        public_key_file = os.path.abspath(public_key_file)
        logger.debug("Using public key file: %s", public_key_file)
    if cert_path:
        cert_path = os.path.abspath(cert_path)
        logger.debug("Certificate will be written to: %s", cert_path)
    if ssh_client_folder:
        ssh_client_folder = os.path.abspath(ssh_client_folder)
        logger.debug("Using SSH client folder: %s", ssh_client_folder)

    keys_folder = None
    if not public_key_file:
        keys_folder = os.path.dirname(cert_path)
        logger.debug("Will generate key pair in: %s", keys_folder)

    try:
        public_key_file, _, _ = _check_or_create_public_private_files(
            public_key_file, None, keys_folder, ssh_client_folder)
        cert_file, _ = _get_and_write_certificate(cmd, public_key_file, cert_path, ssh_client_folder)
    except Exception as e:
        logger.debug("Certificate generation failed: %s", str(e))
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


def sftp_connect(cmd, storage_account, port=None, cert_file=None, private_key_file=None,
                 public_key_file=None, sftp_args=None, ssh_client_folder=None):
    """Connect to Azure Storage Account via SFTP with automatic certificate generation if needed."""
    logger.debug("Starting SFTP connection to storage account: %s", storage_account)

    if cert_file:
        cert_file = os.path.expanduser(cert_file)
    if private_key_file:
        private_key_file = os.path.expanduser(private_key_file)
    if public_key_file:
        public_key_file = os.path.expanduser(public_key_file)

    _assert_args(storage_account, cert_file, public_key_file, private_key_file)

    auto_generate_cert = False
    delete_keys = False
    delete_cert = False
    credentials_folder = None

    if not cert_file and not public_key_file and not private_key_file:
        logger.info("Fully managed mode: No credentials provided")
        auto_generate_cert = True
        delete_cert = True
        delete_keys = True
        credentials_folder = tempfile.mkdtemp(prefix="aadsftp")

        try:
            profile = Profile(cli_ctx=cmd.cli_ctx)
            profile.get_subscription()
        except Exception:
            if credentials_folder and os.path.isdir(credentials_folder):
                shutil.rmtree(credentials_folder)
            raise

        print_styled_text((Style.ACTION, "Generating temporary credentials..."))

    if cert_file and public_key_file:
        print_styled_text((Style.WARNING, "Using certificate file (ignoring public key)."))

    try:
        if auto_generate_cert:
            public_key_file, private_key_file, _ = _check_or_create_public_private_files(
                None, None, credentials_folder, ssh_client_folder)
            cert_file, user = _get_and_write_certificate(cmd, public_key_file, None, ssh_client_folder)
        elif not cert_file:
            profile = Profile(cli_ctx=cmd.cli_ctx)
            profile.get_subscription()

            public_key_file, private_key_file, _ = _check_or_create_public_private_files(
                public_key_file, private_key_file, None, ssh_client_folder)
            print_styled_text((Style.ACTION, "Generating certificate..."))
            cert_file, user = _get_and_write_certificate(cmd, public_key_file, None, ssh_client_folder)
            delete_cert = True
        else:
            logger.debug("Using provided certificate file...")
            if not os.path.isfile(cert_file):
                raise azclierror.FileOperationError(f"Certificate file {cert_file} not found.")

            user = sftp_utils.get_ssh_cert_principals(cert_file, ssh_client_folder)[0].lower()

        if '@' in user:
            user = user.split('@')[0]

        username = f"{storage_account}.{user}"

        storage_suffix = _get_storage_endpoint_suffix(cmd)
        hostname = f"{storage_account}.{storage_suffix}"

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
            yes_without_prompt=False
        )

        sftp_session.local_user = user
        sftp_session.resolve_connection_info()

        if port is not None:
            print_styled_text((Style.PRIMARY, f"Connecting to {username}@{hostname}:{port}"))
        else:
            print_styled_text((Style.PRIMARY, f"Connecting to {username}@{hostname}"))

        _do_sftp_op(sftp_session, sftp_utils.start_sftp_connection)

    except Exception as e:
        if delete_keys or delete_cert:
            logger.debug("An error occurred. Cleaning up generated credentials.")
            _cleanup_credentials(delete_keys, delete_cert, credentials_folder, cert_file,
                                 private_key_file, public_key_file)
        raise e
    finally:
        if delete_keys or delete_cert:
            _cleanup_credentials(delete_keys, delete_cert, credentials_folder, cert_file,
                                 private_key_file, public_key_file)


def _check_or_create_public_private_files(public_key_file, private_key_file, credentials_folder,
                                          ssh_client_folder=None):
    delete_keys = False
    if not public_key_file and not private_key_file:
        delete_keys = True
        if not credentials_folder:
            credentials_folder = tempfile.mkdtemp(prefix="aadsshcert")
        else:
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

    if private_key_file:
        if not os.path.isfile(private_key_file):
            raise azclierror.FileOperationError(f"Private key file {private_key_file} not found")

    if not private_key_file:
        if public_key_file.endswith(".pub"):
            private_key_file = public_key_file[:-4] if os.path.isfile(public_key_file[:-4]) else None

    return public_key_file, private_key_file, delete_keys


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
    profile = Profile(cli_ctx=cmd.cli_ctx)

    t0 = time.time()
    if hasattr(profile, "get_msal_token"):
        _, certificate = profile.get_msal_token(scopes, data)
    else:
        credential, _, _ = profile.get_login_credentials(subscription_id=profile.get_subscription()["id"])
        certificatedata = credential.get_token(*scopes, data=data)
        certificate = certificatedata.token

    time_elapsed = time.time() - t0
    telemetry.add_extension_event('sftp',
                                  {'Context.Default.AzureCLI.SftpGetCertificateTime': time_elapsed})

    if not cert_file:
        base_name = os.path.splitext(str(public_key_file))[0]
        cert_file = base_name + "-aadcert.pub"

    logger.debug("Generating certificate %s", cert_file)
    _write_cert_file(certificate, cert_file)
    username = sftp_utils.get_ssh_cert_principals(cert_file, ssh_client_folder)[0]
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
    """Validate SFTP connection arguments."""
    if not storage_account:
        raise azclierror.RequiredArgumentMissingError("Storage account name is required.")

    if cert_file:
        expanded_cert_file = os.path.expanduser(cert_file)
        if not os.path.isfile(expanded_cert_file):
            raise azclierror.FileOperationError(f"Certificate file {cert_file} not found.")

    if public_key_file:
        expanded_public_key_file = os.path.expanduser(public_key_file)
        if not os.path.isfile(expanded_public_key_file):
            raise azclierror.FileOperationError(f"Public key file {public_key_file} not found.")

    if private_key_file:
        expanded_private_key_file = os.path.expanduser(private_key_file)
        if not os.path.isfile(expanded_private_key_file):
            raise azclierror.FileOperationError(f"Private key file {private_key_file} not found.")


def _do_sftp_op(sftp_session, op_call):
    """Execute SFTP operation with session."""
    sftp_session.validate_session()
    return op_call(sftp_session)


def _cleanup_credentials(delete_keys, delete_cert, credentials_folder, cert_file, private_key_file, public_key_file):
    """Clean up generated credentials."""
    try:
        if delete_cert and cert_file and os.path.isfile(cert_file):
            file_utils.delete_file(cert_file, f"Deleting generated certificate {cert_file}", warning=False)

        if delete_keys:
            if private_key_file and os.path.isfile(private_key_file):
                file_utils.delete_file(private_key_file,
                                       f"Deleting generated private key {private_key_file}", warning=False)
            if public_key_file and os.path.isfile(public_key_file):
                file_utils.delete_file(public_key_file,
                                       f"Deleting generated public key {public_key_file}", warning=False)

        if credentials_folder and os.path.isdir(credentials_folder):
            logger.debug("Deleting credentials folder %s", credentials_folder)
            shutil.rmtree(credentials_folder)

    except OSError as e:
        logger.warning("Failed to clean up credentials: %s", str(e))


def _get_storage_endpoint_suffix(cmd):
    """Get the appropriate storage endpoint suffix based on Azure cloud environment."""
    cloud_to_storage_suffix = {
        "azurecloud": "blob.core.windows.net",
        "azurechinacloud": "blob.core.chinacloudapi.cn",
        "azureusgovernment": "blob.core.usgovcloudapi.net"
    }
    return cloud_to_storage_suffix.get(cmd.cli_ctx.cloud.name.lower(), "blob.core.windows.net")
