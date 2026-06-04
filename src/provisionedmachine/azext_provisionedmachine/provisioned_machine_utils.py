# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Utilities for the `az ssh cert-create` command.

Step 1 – Prepare certificate metadata:
    user_public_key + username + role (from PIM assignment) + validity window

Step 2 – Sign via Key Vault Sign API:
    Build the OpenSSH certificate body in memory (ssh-rsa-cert-v01@openssh.com).
    Hash it with SHA-512 and send the digest to Key Vault's Sign API (RS512).
    The CA private key is non-exportable and never leaves Key Vault.
    Assemble the final certificate with the returned signature.

Step 3 – Return to user:
    Signed SSH user certificate + freshly generated user_private key.
    Output is identical to `ssh-keygen -s` and validated by standard sshd.

Expiry constraint: maximum 8 hours (enforced at device level).
"""

import base64
import datetime
import hashlib
import json
import os
import platform
import re
import shutil
import struct
import stat
import subprocess
import tempfile

import requests
from knack import log
from azure.cli.core import azclierror

logger = log.get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_KV_API_VERSION = "7.4"
_KV_CA_KEY_SUFFIX = "-ssh-ca"   # key name = {deviceId}-ssh-ca
_KV_SIGN_ALGORITHM = "RS512"    # RSASSA-PKCS1-v1_5 with SHA-512 = OpenSSH rsa-sha2-512
_KV_RESOURCE = "https://vault.azure.net"
_KV_TIMEOUT_SECONDS = 30

# OpenSSH certificate constants
_SSH_CERT_TYPE = "ssh-rsa-cert-v01@openssh.com"
_SSH_CERT_USER = 1       # user certificate (vs host=2)
_SSH_SIG_ALGO = "rsa-sha2-512"
_RSA_KEY_BITS = 4096
_PRIVATE_KEY_FILE_PERMISSION = 0o600   # owner read/write only
_RESOURCE_ID_PATTERN = re.compile(
    r"^/subscriptions/[0-9a-fA-F-]+/resourceGroups/[^/]+/providers/[^/]+/[^/]+/[^/]+$",
    re.IGNORECASE,
)
_VAULT_NAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9-]{1,22}[a-zA-Z0-9]$")

# Standard roles for ProvisionedMachine resources.
PROVISIONED_MACHINE_ROLES = {
    "reader": "Provisioned Machine Reader",
    "contributor": "Provisioned Machine Contributor",
    "admin": "Owner",  # TEMPORARY: using Owner until custom role creation is re-enabled
}

# Permissions matrix per role.
ROLE_PERMISSIONS = {
    "Provisioned Machine Reader": {
        "ssh_allowed": False,
        "certificate_types": [],
        "portal": ["view"],
    },
    "Provisioned Machine Contributor": {
        "ssh_allowed": True,
        "certificate_types": ["config-app", "ssh-non-sudo"],
        "portal": ["view", "create", "manage-updates", "manage-nics",
                   "collect-logs", "manage-networking"],
    },
    "Provisioned Machine Admin": {
        "ssh_allowed": True,
        "certificate_types": ["config-app", "ssh-non-sudo", "ssh-sudo"],
        "portal": ["view", "create", "manage-updates", "manage-nics",
                   "manage-disks", "reset-device", "keyvault-access",
                   "delete", "grant-access", "pim-setup",
                   "collect-logs", "manage-networking"],
    },
    # TEMPORARY: Owner mapping until custom role creation is re-enabled
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
    """Return the username alias of the currently signed-in identity.

    The UPN (e.g. ``user@contoso.com``) is retrieved from the Entra / Azure
    CLI login context and then stripped to the alias part (``user``).  The
    alias is used as the certificate principal and must match the SSH login
    user (``<alias>_jit``) on the device side.
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
    return extract_username_alias(user)


def extract_username_alias(upn):
    """Extract the alias (name) part from a UPN or return as-is.

    ``user@contoso.com`` → ``user``
    ``servicePrincipalId`` → ``servicePrincipalId``  (no '@' → unchanged)
    """
    if "@" in upn:
        return upn.split("@", 1)[0]
    return upn


def check_pim_eligibility(cmd, resource_id):
    """Verify the current user has an **active** PIM role assignment on *resource_id*.

    Queries the PIM Role Assignment Schedule Instances API to confirm that
    the user has activated JIT access.  Raises ``AuthenticationError`` if
    no active PIM assignment is found.

    Returns (instances, startTime, endTime).
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

    Returns one of ``Provisioned Machine Reader``, ``Provisioned Machine Contributor``,
    or ``Provisioned Machine Admin``.
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

    role_priority = {"Provisioned Machine Admin": 3, "Owner": 3, "Provisioned Machine Contributor": 2, "Provisioned Machine Reader": 1}
    best_role = None
    best_priority = 0

    for assignment in assignments:
        role_def_id = assignment.role_definition_id
        try:
            role_def = auth_client.role_definitions.get_by_id(role_def_id)
        except Exception:
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
            f"No Provisioned Machine Reader, Contributor, or Admin role assignment found for "
            f"the current user on resource '{resource_id}'. Ensure PIM-based "
            f"JIT access has been activated and the role is scoped to the "
            f"ProvisionedMachine resource."
        )

    logger.info("Resolved role '%s' for user '%s' on resource '%s'.",
                best_role, user_object_id, resource_id)
    return best_role


def generate_ephemeral_keypair(ssh_client_folder=None):
    """Generate a fresh RSA-4096 key pair in a secure temp directory.

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
        subprocess.check_call(cmd_args, timeout=30)
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

    import oschmod  # pylint: disable=import-outside-toplevel
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
            if os.path.isdir(parent) and parent.startswith(tempfile.gettempdir()):
                import shutil
                shutil.rmtree(parent, ignore_errors=True)
            elif os.path.isfile(path):
                os.remove(path)
        except OSError:
            logger.debug("Failed to clean up '%s'.", path)


def sign_certificate_metadata(cmd, keyvault_name, metadata):
    """Sign the user's public key via Key Vault Sign API (RS512).

    Metadata shape:  { username, role, deviceId, startTime, endTime, publicKeyPath }

    The Key Vault key name is derived as ``{deviceId}-ssh-ca``.

    Returns a dict with ``certificatePath``.
    """
    username = metadata["username"]
    role = metadata["role"]
    device_id = metadata["deviceId"]
    start_time = metadata["startTime"]
    end_time = metadata["endTime"]
    public_key_path = metadata["publicKeyPath"]

    # Key name is per-device: {deviceId}-ssh-ca
    kv_key_name = f"{device_id}{_KV_CA_KEY_SUFFIX}"
    logger.info("Using Key Vault key: %s", kv_key_name)

    # Read the user's public key.
    with open(public_key_path, "r", encoding="utf-8") as f:
        user_pub_key_line = f.read().strip()

    # Parse the public key (ssh-rsa AAAA... comment).
    user_key_parts = user_pub_key_line.split()
    if len(user_key_parts) < 2 or user_key_parts[0] != "ssh-rsa":
        raise azclierror.CLIInternalError(
            "Expected an ssh-rsa public key."
        )
    user_key_blob = base64.b64decode(user_key_parts[1])
    user_e, user_n = _parse_rsa_pubkey_blob(user_key_blob)

    # Fetch CA public key from Key Vault.
    ca_e, ca_n = _get_ca_public_key(cmd, keyvault_name, kv_key_name)
    ca_pub_blob = _encode_rsa_pubkey_blob(ca_e, ca_n)

    # Build principals list.
    principals = [f"username={username}", f"role={role}"]

    # Convert ISO timestamps to Unix epoch.
    valid_after = _iso_to_epoch(start_time)
    valid_before = _iso_to_epoch(end_time)

    key_id = username

    # Build the certificate body (everything that gets signed).
    cert_body = _build_cert_body(
        user_e=user_e,
        user_n=user_n,
        serial=0,
        key_id=key_id,
        principals=principals,
        valid_after=valid_after,
        valid_before=valid_before,
        ca_pub_blob=ca_pub_blob,
    )

    # Hash the body with SHA-512 and send to KV Sign API.
    digest = hashlib.sha512(cert_body).digest()
    signature_bytes = _kv_sign_digest(cmd, keyvault_name, kv_key_name, digest)

    # Assemble the final certificate.
    cert_blob = _assemble_openssh_cert(cert_body, signature_bytes)
    cert_line = f"{_SSH_CERT_TYPE} {base64.b64encode(cert_blob).decode('ascii')}"

    # Write certificate file.
    cert_path = public_key_path.replace(".pub", "-cert.pub")
    with open(cert_path, "w", encoding="utf-8") as f:
        f.write(cert_line + "\n")
    import oschmod  # pylint: disable=import-outside-toplevel
    oschmod.set_mode(cert_path, stat.S_IRUSR | stat.S_IWUSR)  # 0600

    logger.info("Signed SSH certificate written to %s", cert_path)
    return {
        "certificatePath": cert_path,
    }


def extract_device_id(resource_id):
    """Extract the device name (last segment) from an ARM resource ID.

    E.g. ``/subscriptions/.../providers/X/Y/myDevice`` → ``myDevice``
    """
    return resource_id.rstrip("/").rsplit("/", 1)[-1]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_current_user_object_id(cmd):
    """Return the OID of the currently signed-in user / service principal."""
    from azure.cli.core._profile import Profile

    profile = Profile(cli_ctx=cmd.cli_ctx)
    try:
        creds, _, _ = profile.get_login_credentials()
        token = creds.get_token("https://management.azure.com/.default")
    except Exception as ex:
        raise azclierror.AuthenticationError(
            "Failed to acquire an access token. Please run 'az login'."
        ) from ex

    try:
        payload_segment = token.token.split(".")[1]
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


def _get_kv_token(cmd, keyvault_name):
    """Acquire a Key Vault access token using the current az login context."""
    from azure.cli.core._profile import Profile

    profile = Profile(cli_ctx=cmd.cli_ctx)
    try:
        creds, _, _ = profile.get_login_credentials()
        token = creds.get_token(f"{_KV_RESOURCE}/.default")
    except Exception as ex:
        raise azclierror.AuthenticationError(
            f"Failed to acquire a Key Vault access token for vault "
            f"'{keyvault_name}'. Error: {ex}"
        ) from ex
    return token.token


def _get_ca_public_key(cmd, keyvault_name, key_name):
    """Fetch the CA public key (e, n) from Key Vault's Get Key API.

    Returns ``(e_int, n_int)``.
    """
    token = _get_kv_token(cmd, keyvault_name)

    vault_url = f"https://{keyvault_name}.vault.azure.net"
    key_url = (f"{vault_url}/keys/{key_name}"
               f"?api-version={_KV_API_VERSION}")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(key_url, headers=headers,
                                timeout=_KV_TIMEOUT_SECONDS)
    except requests.exceptions.Timeout as ex:
        raise azclierror.CLIInternalError(
            f"Key Vault request timed out after {_KV_TIMEOUT_SECONDS}s."
        ) from ex
    except requests.exceptions.ConnectionError as ex:
        raise azclierror.CLIInternalError(
            f"Unable to connect to Key Vault '{keyvault_name}'."
        ) from ex

    if response.status_code == 401:
        raise azclierror.AuthenticationError(
            f"Access denied to Key Vault '{keyvault_name}'. "
            f"Ensure the signed-in identity has 'Key Get' permission."
        )
    if response.status_code == 404:
        raise azclierror.ResourceNotFoundError(
            f"Key '{key_name}' not found in vault '{keyvault_name}'."
        )
    if response.status_code != 200:
        raise azclierror.CLIInternalError(
            f"Key Vault GET key failed (HTTP {response.status_code}): "
            f"{response.text}"
        )

    key_data = response.json().get("key", {})
    if key_data.get("kty") not in ("RSA", "RSA-HSM"):
        raise azclierror.CLIInternalError(
            f"CA key '{key_name}' is not an RSA key "
            f"(found: {key_data.get('kty')})."
        )

    e_b64 = key_data.get("e")
    n_b64 = key_data.get("n")
    if not e_b64 or not n_b64:
        raise azclierror.CLIInternalError(
            "CA public key response is missing 'e' or 'n' components."
        )

    e_int = int.from_bytes(_b64url_decode(e_b64), "big")
    n_int = int.from_bytes(_b64url_decode(n_b64), "big")
    return e_int, n_int


def _kv_sign_digest(cmd, keyvault_name, key_name, digest_bytes):
    """Send a SHA-512 digest to Key Vault Sign API and return raw signature bytes."""
    token = _get_kv_token(cmd, keyvault_name)

    vault_url = f"https://{keyvault_name}.vault.azure.net"
    sign_url = (f"{vault_url}/keys/{key_name}/sign"
                f"?api-version={_KV_API_VERSION}")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    digest_b64 = base64.urlsafe_b64encode(digest_bytes).decode("ascii").rstrip("=")
    payload = {
        "alg": _KV_SIGN_ALGORITHM,
        "value": digest_b64,
    }

    try:
        response = requests.post(
            sign_url, headers=headers, json=payload,
            timeout=_KV_TIMEOUT_SECONDS,
        )
    except requests.exceptions.Timeout as ex:
        raise azclierror.CLIInternalError(
            f"Key Vault Sign request timed out after {_KV_TIMEOUT_SECONDS}s."
        ) from ex
    except requests.exceptions.ConnectionError as ex:
        raise azclierror.CLIInternalError(
            f"Unable to connect to Key Vault '{keyvault_name}'."
        ) from ex

    if response.status_code == 401:
        raise azclierror.AuthenticationError(
            f"Access denied to Key Vault '{keyvault_name}'. "
            f"Ensure the signed-in identity has 'Key Sign' permission "
            f"on the '{key_name}' key."
        )
    if response.status_code == 404:
        raise azclierror.ResourceNotFoundError(
            f"Key '{key_name}' not found in vault '{keyvault_name}'."
        )
    if response.status_code != 200:
        raise azclierror.CLIInternalError(
            f"Key Vault Sign failed (HTTP {response.status_code}): "
            f"{response.text}"
        )

    sig_b64 = response.json().get("value")
    if not sig_b64:
        raise azclierror.CLIInternalError(
            "Key Vault returned an empty signature."
        )

    return _b64url_decode(sig_b64)


# ---------------------------------------------------------------------------
# OpenSSH certificate binary builder
# ---------------------------------------------------------------------------

def _build_cert_body(user_e, user_n, serial, key_id, principals,
                     valid_after, valid_before, ca_pub_blob):
    """Build the to-be-signed body of an ssh-rsa-cert-v01@openssh.com certificate."""
    buf = bytearray()

    # cert type
    buf += _ssh_string(_SSH_CERT_TYPE.encode())

    # nonce — 32 random bytes
    nonce = os.urandom(32)
    buf += _ssh_string(nonce)

    # user public key (e, n as mpint)
    buf += _ssh_mpint(user_e)
    buf += _ssh_mpint(user_n)

    # serial
    buf += struct.pack(">Q", serial)

    # type = user
    buf += struct.pack(">I", _SSH_CERT_USER)

    # key_id
    buf += _ssh_string(key_id.encode())

    # principals
    principals_buf = bytearray()
    for p in principals:
        principals_buf += _ssh_string(p.encode())
    buf += _ssh_string(bytes(principals_buf))

    # valid_after, valid_before
    buf += struct.pack(">Q", valid_after)
    buf += struct.pack(">Q", valid_before)

    # critical options: no-port-forwarding, no-agent-forwarding
    crit_buf = bytearray()
    for opt_name in sorted(["no-port-forwarding", "no-agent-forwarding"]):
        crit_buf += _ssh_string(opt_name.encode())
        crit_buf += _ssh_string(b"")   # empty value
    buf += _ssh_string(bytes(crit_buf))

    # extensions: permit-pty
    ext_buf = bytearray()
    for ext_name in sorted(["permit-pty"]):
        ext_buf += _ssh_string(ext_name.encode())
        ext_buf += _ssh_string(b"")
    buf += _ssh_string(bytes(ext_buf))

    # reserved (empty)
    buf += _ssh_string(b"")

    # signature_key (CA public key blob)
    buf += _ssh_string(ca_pub_blob)

    return bytes(buf)


def _assemble_openssh_cert(cert_body, signature_bytes):
    """Append the RSA signature to the certificate body."""
    sig_inner = bytearray()
    sig_inner += _ssh_string(_SSH_SIG_ALGO.encode())
    sig_inner += _ssh_string(signature_bytes)

    return cert_body + _ssh_string(bytes(sig_inner))


# ---------------------------------------------------------------------------
# SSH wire-format helpers
# ---------------------------------------------------------------------------

def _ssh_string(data):
    """Encode bytes as an SSH string: uint32 length + data."""
    return struct.pack(">I", len(data)) + data


def _ssh_mpint(value):
    """Encode a positive integer as an SSH mpint."""
    byte_length = (value.bit_length() + 7) // 8
    raw = value.to_bytes(byte_length, "big")
    if raw[0] & 0x80:
        raw = b"\x00" + raw
    return _ssh_string(raw)


def _parse_rsa_pubkey_blob(blob):
    """Parse an SSH RSA public key blob and return (e, n) as integers."""
    offset = 0

    def read_string():
        nonlocal offset
        length = struct.unpack(">I", blob[offset:offset + 4])[0]
        offset += 4
        data = blob[offset:offset + length]
        offset += length
        return data

    key_type = read_string()
    if key_type != b"ssh-rsa":
        raise azclierror.CLIInternalError(
            f"Expected ssh-rsa key type, got {key_type!r}."
        )
    e_bytes = read_string()
    n_bytes = read_string()
    return int.from_bytes(e_bytes, "big"), int.from_bytes(n_bytes, "big")


def _encode_rsa_pubkey_blob(e, n):
    """Encode RSA public key (e, n) as an SSH public key blob."""
    buf = bytearray()
    buf += _ssh_string(b"ssh-rsa")
    buf += _ssh_mpint(e)
    buf += _ssh_mpint(n)
    return bytes(buf)


def _iso_to_epoch(iso_time):
    """Convert an ISO 8601 UTC timestamp to a Unix epoch integer."""
    dt = datetime.datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
    return int(dt.timestamp())


def _b64url_decode(s):
    """Decode a base64url string (with or without padding)."""
    padded = s + "=" * (4 - len(s) % 4)
    return base64.urlsafe_b64decode(padded)


def _resolve_keygen(ssh_client_folder=None):
    """Locate the ``ssh-keygen`` binary on the current platform.

    Discovery strategy:
      1. If *ssh_client_folder* is given, look there first.
      2. Use ``shutil.which`` for a cross-platform PATH lookup.
      3. On Windows, probe well-known install locations including the
         Sysnative virtual folder (needed when Azure CLI runs as a 32-bit
         process under WoW64 file-system redirection).
      4. On Linux / macOS, probe common package-manager locations.

    If ssh-keygen cannot be found, raises ``CLIInternalError`` with
    platform-specific installation instructions.
    """
    system = platform.system()   # "Windows", "Linux", "Darwin"
    exe_name = "ssh-keygen.exe" if system == "Windows" else "ssh-keygen"

    # --- 1. Caller-supplied folder ------------------------------------
    if ssh_client_folder:
        candidate = os.path.join(ssh_client_folder, exe_name)
        if os.path.isfile(candidate):
            logger.info("ssh-keygen found in supplied folder: %s", candidate)
            return candidate
        # On 32-bit Python on Windows, System32 is redirected to SysWOW64.
        # Try the Sysnative alias which bypasses WoW64 redirection.
        if system == "Windows" and "system32" in ssh_client_folder.lower():
            sysnative = ssh_client_folder.lower().replace("system32", "Sysnative")
            alt = os.path.join(sysnative, exe_name)
            if os.path.isfile(alt):
                logger.info("ssh-keygen found via Sysnative redirect: %s", alt)
                return alt
        # Folder was given but binary not found — fall through to auto-detect
        # so the user still gets a helpful error rather than a silent failure.
        logger.warning("ssh-keygen not found in supplied folder '%s'; "
                       "attempting auto-detection.", ssh_client_folder)

    # --- 2. Cross-platform PATH lookup --------------------------------
    found = shutil.which("ssh-keygen")
    if found:
        logger.info("ssh-keygen found on PATH: %s", found)
        return found

    # --- 3. Platform-specific well-known locations --------------------
    if system == "Windows":
        candidate = _probe_windows_keygen(exe_name)
        if candidate:
            return candidate
    else:
        candidate = _probe_unix_keygen()
        if candidate:
            return candidate

    # --- 4. Not found — give actionable install instructions ----------
    raise azclierror.CLIInternalError(
        _openssh_install_message(system)
    )


def _probe_windows_keygen(exe_name):
    """Probe well-known Windows locations for ssh-keygen."""
    sys_root = os.environ.get("SystemRoot", r"C:\Windows")
    search_dirs = [
        # Sysnative bypasses WoW64 redirection (32-bit Python → real System32)
        os.path.join(sys_root, "Sysnative", "OpenSSH"),
        os.path.join(sys_root, "System32", "OpenSSH"),
        # Git-for-Windows bundles ssh-keygen
        os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"),
                     "Git", "usr", "bin"),
        os.path.join(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
                     "Git", "usr", "bin"),
    ]
    for folder in search_dirs:
        candidate = os.path.join(folder, exe_name)
        if os.path.isfile(candidate):
            logger.info("ssh-keygen found at well-known Windows path: %s", candidate)
            return candidate

    # Last resort: ask the OS via 'where' command.
    try:
        result = subprocess.run(             # pylint: disable=subprocess-run-check
            ["where", "ssh-keygen"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            first_line = result.stdout.strip().splitlines()[0]
            if os.path.isfile(first_line):
                logger.info("ssh-keygen found via 'where': %s", first_line)
                return first_line
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    return None


def _probe_unix_keygen():
    """Probe well-known Unix/macOS locations for ssh-keygen."""
    for candidate in ("/usr/bin/ssh-keygen",
                      "/usr/local/bin/ssh-keygen",
                      "/opt/homebrew/bin/ssh-keygen"):
        if os.path.isfile(candidate):
            logger.info("ssh-keygen found at well-known path: %s", candidate)
            return candidate

    # Last resort: ask the OS via 'which' command.
    try:
        result = subprocess.run(             # pylint: disable=subprocess-run-check
            ["which", "ssh-keygen"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            path = result.stdout.strip()
            if os.path.isfile(path):
                logger.info("ssh-keygen found via 'which': %s", path)
                return path
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    return None


def _openssh_install_message(system):
    """Return a platform-specific error message with install instructions."""
    if system == "Windows":
        return (
            "ssh-keygen was not found on this system.\n\n"
            "OpenSSH is required to generate SSH key pairs.  "
            "Install it using one of the following methods:\n\n"
            "  Option 1 — Windows Settings (recommended):\n"
            "    Settings → Apps → Optional features → Add a feature\n"
            "    → search 'OpenSSH Client' → Install\n\n"
            "  Option 2 — PowerShell (Admin):\n"
            "    Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0\n\n"
            "  Option 3 — winget:\n"
            "    winget install Microsoft.OpenSSH.Beta\n\n"
            "After installing, restart your terminal and retry the command.\n"
            "Alternatively, pass --ssh-client-folder to point to a folder "
            "containing ssh-keygen.exe."
        )
    if system == "Darwin":
        return (
            "ssh-keygen was not found on this system.\n\n"
            "OpenSSH is usually pre-installed on macOS.  If it is missing, "
            "install it with Homebrew:\n\n"
            "  brew install openssh\n\n"
            "After installing, retry the command.\n"
            "Alternatively, pass --ssh-client-folder to point to a folder "
            "containing ssh-keygen."
        )
    # Linux and other Unix
    return (
        "ssh-keygen was not found on this system.\n\n"
        "Install the OpenSSH client package for your distribution:\n\n"
        "  Ubuntu / Debian:  sudo apt install openssh-client\n"
        "  RHEL / Fedora:    sudo dnf install openssh-clients\n"
        "  SUSE:             sudo zypper install openssh-clients\n"
        "  Alpine:           sudo apk add openssh-keygen\n\n"
        "After installing, retry the command.\n"
        "Alternatively, pass --ssh-client-folder to point to a folder "
        "containing ssh-keygen."
    )
