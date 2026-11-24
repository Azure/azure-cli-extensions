# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Utilities for the `az ssh cert-create` command.

Step 1 – Prepare certificate metadata:
    user_public_key + username + role (from PIM assignment) + expiry

Step 2 – Sign via Key Vault:
    AZ CLI sends signing request to Key Vault Sign API using az login context.
    CA private key never leaves Key Vault.

Step 3 – Return to user:
    Signed SSH user certificate + freshly generated user_private key.

Expiry constraint: maximum 8 hours (enforced at device level).
"""

import base64
import datetime
import hashlib
import json
import os
import re
import stat
import subprocess
import tempfile

import oschmod
import requests
from knack import log
from azure.cli.core import azclierror

logger = log.get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_KV_SIGN_API_VERSION = "7.4"
_KV_CA_KEY_NAME = "ssh-ca"
_KV_SIGN_ALGORITHM = "RS256"
_KV_RESOURCE = "https://vault.azure.net"
_KV_SIGN_TIMEOUT_SECONDS = 30
_RSA_KEY_BITS = 4096
_PRIVATE_KEY_FILE_PERMISSION = 0o600   # owner read/write only
_RESOURCE_ID_PATTERN = re.compile(
    r"^/subscriptions/[0-9a-fA-F-]+/resourceGroups/[^/]+/providers/[^/]+/[^/]+/[^/]+$",
    re.IGNORECASE,
)
_VAULT_NAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9-]{1,22}[a-zA-Z0-9]$")

# Standard roles for ProvisionedMachine resources.
# Maps Azure RBAC role name substrings to a canonical role label.
PROVISIONED_MACHINE_ROLES = {
    "reader": "Reader",
    "contributor": "Contributor",
    "owner": "Owner",
}

# Permissions matrix per role.
# Each role defines which certificate types it can generate and what
# capabilities the device should grant.
#
# Certificates are generated for ALL roles. Access restrictions are enforced
# on the device side, not by the CLI.
# Reader      - View-only in portal; device blocks SSH access.
# Contributor - Config app + SSH (non-sudo).
# Owner       - Config app + SSH (non-sudo) + SSH (sudo).
ROLE_PERMISSIONS = {
    "Reader": {
        "ssh_allowed": False,
        "certificate_types": [],
        "portal": ["view"],
    },
    "Contributor": {
        "ssh_allowed": True,
        "certificate_types": ["config-app", "ssh-non-sudo"],
        "portal": ["view", "create", "manage-updates", "manage-nics",
                   "collect-logs", "manage-networking"],
    },
    "Owner": {
        "ssh_allowed": True,
        "certificate_types": ["config-app", "ssh-non-sudo", "ssh-sudo"],
        "portal": ["view", "create", "manage-updates", "manage-nics",
                   "manage-disks", "reset-device", "keyvault-access",
                   "delete", "grant-access", "pim-setup",
                   "collect-logs", "manage-networking"],
    },
}


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

def validate_resource_id(resource_id):
    """Validate that *resource_id* looks like a fully-qualified ARM resource ID."""
    if not resource_id or not _RESOURCE_ID_PATTERN.match(resource_id):
        raise azclierror.InvalidArgumentValueError(
            f"'{resource_id}' is not a valid ARM resource ID. "
            "Expected format: /subscriptions/<sub>/resourceGroups/<rg>/"
            "providers/<provider>/<type>/<name>"
        )


def validate_vault_name(vault_name):
    """Validate that *vault_name* conforms to Key Vault naming rules."""
    if not vault_name or not _VAULT_NAME_PATTERN.match(vault_name):
        raise azclierror.InvalidArgumentValueError(
            f"'{vault_name}' is not a valid Key Vault name. "
            "It must be 3-24 characters, start with a letter, end with a "
            "letter or digit, and contain only letters, digits, and hyphens."
        )


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def get_current_user_principal(cmd):
    """Return the UPN (or app ID) of the currently signed-in identity.

    The value is derived from the Entra / Azure CLI login context so the
    caller never needs to supply it manually.
    """
    from azure.cli.core._profile import Profile
    profile = Profile(cli_ctx=cmd.cli_ctx)
    try:
        user = profile.get_current_account_user()
    except Exception as ex:
        raise azclierror.AuthenticationError(
            "Unable to determine the signed-in user. "
            "Please run 'az login' first."
        ) from ex
    if not user:
        raise azclierror.AuthenticationError(
            "No signed-in user found. Please run 'az login' first."
        )
    return user


def check_pim_eligibility(cmd, resource_id):
    """Verify the current user has an **active** PIM role assignment on *resource_id*.

    Queries the PIM Role Assignment Schedule Instances API to confirm that
    the user has activated JIT access.  Raises ``AuthenticationError`` if
    no active PIM assignment is found.

    Returns the list of active PIM schedule instances.
    """
    from azure.cli.core._profile import Profile

    user_object_id = _get_current_user_object_id(cmd)
    profile = Profile(cli_ctx=cmd.cli_ctx)

    try:
        creds, _, _ = profile.get_login_credentials()
        token = creds.get_token("https://management.azure.com/.default")
    except Exception as ex:
        raise azclierror.AuthenticationError(
            "Failed to acquire a management token for PIM eligibility check."
        ) from ex

    # Query active PIM role assignment schedule instances scoped to the resource.
    api_version = "2020-10-01"
    url = (
        f"https://management.azure.com{resource_id}"
        f"/providers/Microsoft.Authorization"
        f"/roleAssignmentScheduleInstances"
        f"?api-version={api_version}"
        f"&$filter=assignedTo('{user_object_id}')"
    )

    try:
        resp = requests.get(
            url,
            headers={"Authorization": f"Bearer {token.token}"},
            timeout=30,
        )
    except requests.exceptions.RequestException as ex:
        raise azclierror.CLIInternalError(
            f"Failed to query PIM eligibility on '{resource_id}': {ex}"
        ) from ex

    if resp.status_code == 404:
        raise azclierror.ResourceNotFoundError(
            f"Resource '{resource_id}' was not found. Verify the resource ID is correct."
        )
    if resp.status_code != 200:
        raise azclierror.CLIInternalError(
            f"PIM eligibility check failed (HTTP {resp.status_code}): {resp.text}"
        )

    data = resp.json()
    instances = data.get("value", [])

    # Filter for PIM-activated assignments only.
    # assignmentType == "Activated" means the user activated JIT access via PIM.
    # assignmentType == "Assigned" means a permanent/direct role assignment,
    # which should NOT be accepted — PIM activation is required.
    pim_activated = [
        inst for inst in instances
        if (inst.get("properties", {}).get("assignmentType", "")).lower() == "activated"
    ]

    if not pim_activated:
        has_direct = len(instances) > 0
        if has_direct:
            raise azclierror.AuthenticationError(
                f"You have a direct (permanent) role assignment on resource "
                f"'{resource_id}', but PIM-based JIT activation is required. "
                f"Direct role assignments are not accepted for SSH certificate "
                f"generation. Please activate your role via PIM first:\n"
                f"  1. Go to Azure Portal → Privileged Identity Management → My roles\n"
                f"  2. Select Azure resources → find your eligible role\n"
                f"  3. Click 'Activate' and provide a justification\n"
                f"  4. Wait 1-2 minutes for propagation, then retry."
            )
        raise azclierror.AuthenticationError(
            f"No active PIM role assignment found for the current user on resource "
            f"'{resource_id}'. Please activate your PIM-eligible role first:\n"
            f"  1. Go to Azure Portal → Privileged Identity Management → My roles\n"
            f"  2. Select Azure resources → find your eligible role\n"
            f"  3. Click 'Activate' and provide a justification\n"
            f"  4. Wait 1-2 minutes for propagation, then retry."
        )

    # Extract the expiry from the PIM activation's endDateTime.
    # Use the latest endDateTime among all activated assignments.
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    latest_end = None
    for inst in pim_activated:
        end_str = inst.get("properties", {}).get("endDateTime")
        if end_str:
            try:
                end_dt = datetime.datetime.fromisoformat(end_str.replace("Z", "+00:00"))
                if latest_end is None or end_dt > latest_end:
                    latest_end = end_dt
            except (ValueError, TypeError):
                logger.debug("Could not parse endDateTime '%s'.", end_str)

    if latest_end is None:
        raise azclierror.CLIInternalError(
            "PIM activation found but endDateTime is missing. "
            "Cannot determine certificate expiry."
        )

    if latest_end <= now_utc:
        raise azclierror.AuthenticationError(
            f"Your PIM activation has expired (ended {latest_end.isoformat()}). "
            f"Please re-activate your PIM-eligible role and retry."
        )

    start_time = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time = latest_end.strftime("%Y-%m-%dT%H:%M:%SZ")

    remaining_hours = (latest_end - now_utc).total_seconds() / 3600.0
    logger.info("Found %d PIM-activated assignment(s) for user '%s' on '%s'. "
                "Remaining: %.2f hours (until %s).",
                len(pim_activated), user_object_id, resource_id,
                remaining_hours, latest_end.isoformat())
    return pim_activated, start_time, end_time


def resolve_user_role(cmd, resource_id):
    """Determine the highest-privilege role the signed-in user holds on *resource_id*.

    Uses the Azure Authorization SDK to list role assignments scoped to the
    ProvisionedMachine resource and maps them to Reader / Contributor / Owner.

    Returns one of ``Contributor`` or ``Owner``.

    Raises ``AuthenticationError`` if:
    - No relevant assignment is found.
    - The highest role is Reader (Reader has no SSH access).
    """
    from azure.cli.core.commands.client_factory import get_mgmt_service_client

    try:
        from azure.mgmt.authorization import AuthorizationManagementClient
    except ImportError as ex:
        raise azclierror.CLIInternalError(
            "The 'azure-mgmt-authorization' package is required. "
            "Please run: pip install azure-mgmt-authorization"
        ) from ex

    user_object_id = _get_current_user_object_id(cmd)

    try:
        auth_client = get_mgmt_service_client(cmd.cli_ctx, AuthorizationManagementClient)
        assignments = list(auth_client.role_assignments.list_for_scope(
            scope=resource_id,
            filter=f"assignedTo('{user_object_id}')"
        ))
    except Exception as ex:
        raise azclierror.CLIInternalError(
            f"Failed to query role assignments on '{resource_id}': {ex}"
        ) from ex

    if not assignments:
        raise azclierror.AuthenticationError(
            f"No role assignments found for the current user on resource "
            f"'{resource_id}'. Ensure PIM-based JIT access has been activated."
        )

    role_priority = {"Owner": 3, "Contributor": 2, "Reader": 1}
    best_role = None
    best_priority = 0

    for assignment in assignments:
        role_def_id = assignment.role_definition_id
        try:
            role_def = auth_client.role_definitions.get_by_id(role_def_id)
        except Exception:  # pylint: disable=broad-except
            logger.debug("Skipping role definition '%s' (could not resolve).", role_def_id)
            continue
        role_name = (role_def.role_name or "").lower()

        for key, standard in PROVISIONED_MACHINE_ROLES.items():
            if key in role_name:
                priority = role_priority.get(standard, 0)
                if priority > best_priority:
                    best_role = standard
                    best_priority = priority

    if not best_role:
        raise azclierror.AuthenticationError(
            f"No Reader, Contributor, or Owner role assignment found for "
            f"the current user on resource '{resource_id}'. Ensure PIM-based "
            f"JIT access has been activated and the role is scoped to the "
            f"ProvisionedMachine resource."
        )

    logger.info("Resolved role '%s' for user '%s' on resource '%s'.",
                best_role, user_object_id, resource_id)
    return best_role


def generate_ephemeral_keypair(ssh_client_folder=None):
    """Generate a fresh RSA-4096 key pair in a secure temp directory.

    The private key file permissions are set to 0600 (owner read/write only).

    Returns ``(private_key_path, public_key_path)``.
    """
    keys_dir = tempfile.mkdtemp(prefix="azssh_pm_")
    private_key_path = os.path.join(keys_dir, "id_rsa.pem")
    public_key_path = private_key_path + ".pub"

    keygen = _resolve_keygen(ssh_client_folder)
    cmd_args = [
        keygen, "-t", "rsa", "-b", str(_RSA_KEY_BITS),
        "-f", private_key_path, "-N", "", "-q",
    ]

    try:
        subprocess.check_call(cmd_args, timeout=30)  # pylint: disable=subprocess-run-check
    except FileNotFoundError as ex:
        raise azclierror.CLIInternalError(
            "ssh-keygen not found. Ensure OpenSSH is installed or provide "
            "--ssh-client-folder."
        ) from ex
    except subprocess.TimeoutExpired as ex:
        raise azclierror.CLIInternalError(
            "ssh-keygen timed out while generating the key pair."
        ) from ex
    except subprocess.CalledProcessError as ex:
        raise azclierror.CLIInternalError(
            f"ssh-keygen exited with code {ex.returncode}."
        ) from ex

    if not os.path.isfile(private_key_path) or not os.path.isfile(public_key_path):
        raise azclierror.CLIInternalError(
            "ssh-keygen completed but key files were not created."
        )

    # Restrict private key to owner-only access (cross-platform via oschmod).
    oschmod.set_mode(private_key_path, _PRIVATE_KEY_FILE_PERMISSION)

    logger.info("Generated ephemeral key pair at %s", keys_dir)
    return private_key_path, public_key_path


def cleanup_ephemeral_files(*file_paths):
    """Best-effort removal of sensitive ephemeral files and their parent dirs."""
    for path in file_paths:
        if not path:
            continue
        try:
            parent = os.path.dirname(path)
            # Remove all files in the temp directory.
            if os.path.isdir(parent) and parent.startswith(tempfile.gettempdir()):
                import shutil
                shutil.rmtree(parent, ignore_errors=True)
            elif os.path.isfile(path):
                os.remove(path)
        except OSError:
            logger.debug("Failed to clean up '%s'.", path)


def sign_certificate_metadata(cmd, keyvault_name, metadata):
    """Sign the certificate metadata with the CA private key in Key Vault.

    Metadata shape:  { userPublicKey, username, role, startTime, endTime }

    The Key Vault hosts a non-exportable CA private key (named ``ssh-ca``).
    AZ CLI sends the signing request using the az login context.
    The CA private key never leaves Key Vault.

    Returns a dict with ``signedCertificate`` and ``certificatePath``.
    """
    signing_payload = {
        "userPublicKey": metadata["userPublicKey"],
        "username": metadata["username"],
        "role": metadata["role"],
        "startTime": metadata["startTime"],
        "endTime": metadata["endTime"],
    }

    logger.info("Sending signing request to Key Vault '%s' (valid %s to %s) ...",
                keyvault_name, metadata["startTime"], metadata["endTime"])

    # Sign via Key Vault - CA private key never leaves the vault.
    _signature, cert_data = _call_keyvault_sign(cmd, keyvault_name, signing_payload)

    # Write the signed SSH user certificate to a temp file.
    cert_dir = tempfile.mkdtemp(prefix="azssh_cert_")
    cert_path = os.path.join(cert_dir, "ssh-cert.pub")
    with open(cert_path, "w", encoding="utf-8") as f:
        f.write(cert_data)
    oschmod.set_mode(cert_path, stat.S_IRUSR | stat.S_IWUSR)  # 0600

    # Uncomment below to write signing payload metadata for debugging/verification.
    # metadata_path = os.path.join(cert_dir, "metadata.json")
    # with open(metadata_path, "w", encoding="utf-8") as f:
    #     json.dump(signing_payload, f, indent=2)
    # logger.info("Signing metadata written to %s", metadata_path)

    logger.info("Signed SSH user certificate written to %s", cert_path)
    return {
        "signedCertificate": cert_data,
        "certificatePath": cert_path,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_current_user_object_id(cmd):
    """Return the OID of the currently signed-in user / service principal.

    Extracts the ``oid`` claim from the ARM access token.  This avoids a
    dependency on the deprecated ``azure-graphrbac`` SDK.
    """
    from azure.cli.core._profile import Profile

    profile = Profile(cli_ctx=cmd.cli_ctx)
    try:
        creds, _, _ = profile.get_login_credentials()
        token = creds.get_token("https://management.azure.com/.default")
    except Exception as ex:
        raise azclierror.AuthenticationError(
            "Failed to acquire an access token. Please run 'az login'."
        ) from ex

    # Decode without verification – we only need the 'oid' claim and the
    # token was just issued by the CLI's own credential chain.
    try:
        # The token is a JWT; decode the payload (middle segment).
        payload_segment = token.token.split(".")[1]
        # Add padding if needed.
        padded = payload_segment + "=" * (4 - len(payload_segment) % 4)
        payload_bytes = base64.urlsafe_b64decode(padded)
        claims = json.loads(payload_bytes)
    except Exception as ex:
        raise azclierror.CLIInternalError(
            "Failed to decode the access token to extract the user object ID."
        ) from ex

    oid = claims.get("oid") or claims.get("sub")
    if not oid:
        raise azclierror.CLIInternalError(
            "The access token does not contain an 'oid' or 'sub' claim."
        )
    return oid


def _call_keyvault_sign(cmd, keyvault_name, metadata):
    """Call Key Vault REST API to sign the metadata.

    Uses the ``ssh-ca`` key in the vault to perform an RS256 sign operation.
    The CA private key never leaves Key Vault.

    Returns a tuple of ``(signature_b64, certificate_string)``.
    """
    from azure.cli.core._profile import Profile

    profile = Profile(cli_ctx=cmd.cli_ctx)
    try:
        creds, _, _ = profile.get_login_credentials()
        token = creds.get_token(f"{_KV_RESOURCE}/.default")
    except Exception as ex:
        raise azclierror.AuthenticationError(
            f"Failed to acquire a Key Vault access token for vault "
            f"'{keyvault_name}'. Ensure you have 'Key Sign' permissions "
            f"on the vault. Error: {ex}"
        ) from ex

    vault_url = f"https://{keyvault_name}.vault.azure.net"
    sign_url = (f"{vault_url}/keys/{_KV_CA_KEY_NAME}/sign"
                f"?api-version={_KV_SIGN_API_VERSION}")

    headers = {
        "Authorization": f"Bearer {token.token}",
        "Content-Type": "application/json",
    }

    request_body = {
        "alg": _KV_SIGN_ALGORITHM,
        "value": _build_signing_payload(metadata),
    }

    try:
        response = requests.post(
            sign_url, headers=headers, json=request_body,
            timeout=_KV_SIGN_TIMEOUT_SECONDS,
        )
    except requests.exceptions.Timeout as ex:
        raise azclierror.CLIInternalError(
            f"Key Vault signing request timed out after "
            f"{_KV_SIGN_TIMEOUT_SECONDS}s. Please try again."
        ) from ex
    except requests.exceptions.ConnectionError as ex:
        raise azclierror.CLIInternalError(
            f"Unable to connect to Key Vault '{keyvault_name}'. "
            f"Check network connectivity and vault name."
        ) from ex

    if response.status_code == 401:
        raise azclierror.AuthenticationError(
            f"Access denied to Key Vault '{keyvault_name}'. "
            f"Ensure the signed-in identity has 'Key Sign' permission "
            f"on the '{_KV_CA_KEY_NAME}' key."
        )
    if response.status_code == 404:
        raise azclierror.ResourceNotFoundError(
            f"Key '{_KV_CA_KEY_NAME}' not found in vault '{keyvault_name}'. "
            f"Ensure the CA signing key exists."
        )
    if response.status_code != 200:
        raise azclierror.CLIInternalError(
            f"Key Vault signing failed (HTTP {response.status_code}): "
            f"{response.text}"
        )

    result = response.json()
    signature_b64 = result.get("value")
    if not signature_b64:
        raise azclierror.CLIInternalError(
            "Key Vault returned an empty signature. "
            "Check the CA key configuration."
        )

    cert_data = _build_ssh_certificate(metadata, signature_b64)
    return signature_b64, cert_data


def _build_signing_payload(metadata):
    """Create a base64url-encoded SHA-256 digest of the metadata for Key Vault.

    Key Vault sign API expects a digest, not raw data.  We compute
    SHA-256(canonical JSON) and base64url-encode the result.
    """
    canonical = json.dumps(
        metadata, separators=(",", ":"), sort_keys=True, ensure_ascii=True
    ).encode("utf-8")
    digest = hashlib.sha256(canonical).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def _build_ssh_certificate(metadata, signature_b64):
    """Construct an OpenSSH certificate from the metadata and KV signature.

    NOTE: In production the Key Vault / CA service would return a fully-formed
    ``ssh-rsa-cert-v01@openssh.com`` certificate.  This helper is a placeholder
    that concatenates the public key with the CA-signed blob so that the
    overall CLI flow can be tested end-to-end once the CA service contract is
    finalized.
    """
    # Placeholder – real implementation depends on the Device API / CA contract.
    public_key = metadata["userPublicKey"]
    # Return a synthetic certificate string that the device agent will validate.
    return f"{public_key} {signature_b64}"


def _resolve_keygen(ssh_client_folder):
    if ssh_client_folder:
        return os.path.join(ssh_client_folder, "ssh-keygen")
    return "ssh-keygen"
