# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=broad-exception-raised, broad-exception-caught

"""MSAL Device Code Flow authentication for Analytics Frontend API"""

import os
from pathlib import Path
from knack.log import get_logger

logger = get_logger(__name__)

# MSAL Configuration Constants
# TODO (sakshamgarg): Need to register a new app in AAD and use that for authentication
# for the device code flow. The current client ID is used only for testing
# purposes.
DEFAULT_MS_CLIENT_ID = "8a3849c1-81c5-4d62-b83e-3bb2bb11251a"
DEFAULT_MS_TENANT_ID = "common"
DEFAULT_MS_SCOPES = "User.Read"


def get_config_value(cmd, config_key, env_var_name, default_value):
    """Get configuration value with priority: env var → az config → default

    :param cmd: CLI command context
    :param config_key: Azure config key name (e.g., 'client_id')
    :param env_var_name: Environment variable name (e.g., 'MANAGEDCLEANROOM_CLIENT_ID')
    :param default_value: Default value if not configured
    :return: Configuration value
    """
    # Priority 1: Environment variable
    env_value = os.environ.get(env_var_name)
    if env_value:
        logger.debug(
            "Using %s from environment variable: %s", config_key, env_var_name)
        return env_value

    # Priority 2: Azure CLI config
    config = cmd.cli_ctx.config
    config_value = config.get(
        'managedcleanroom-frontend',
        config_key,
        fallback=None)
    if config_value:
        logger.debug("Using %s from Azure CLI config", config_key)
        return config_value

    # Priority 3: Default value
    logger.debug("Using default %s", config_key)
    return default_value


def get_msal_config(cmd):
    """Get MSAL configuration from environment/config/defaults

    :param cmd: CLI command context
    :return: Dict with client_id, tenant_id, authority, scopes
    """
    client_id = get_config_value(
        cmd,
        'client_id',
        'MANAGEDCLEANROOM_CLIENT_ID',
        DEFAULT_MS_CLIENT_ID)
    tenant_id = get_config_value(
        cmd,
        'tenant_id',
        'MANAGEDCLEANROOM_TENANT_ID',
        DEFAULT_MS_TENANT_ID)
    scopes_str = get_config_value(
        cmd,
        'scopes',
        'MANAGEDCLEANROOM_SCOPES',
        DEFAULT_MS_SCOPES)

    # Parse scopes (comma-separated string to list)
    scopes = [s.strip() for s in scopes_str.split(',')]

    authority = f"https://login.microsoftonline.com/{tenant_id}"

    return {
        'client_id': client_id,
        'tenant_id': tenant_id,
        'authority': authority,
        'scopes': scopes
    }


def get_auth_scope(cmd):
    """Get OAuth2 scope/resource for token requests

    Priority: env var → az config → default

    :param cmd: CLI command context
    :return: OAuth2 scope/resource URL
    """
    return get_config_value(
        cmd,
        'auth_scope',
        'MANAGEDCLEANROOM_AUTH_SCOPE',
        'https://management.azure.com/'
    )


def get_msal_cache_dir():
    """Get directory for MSAL token cache

    :return: Path to cache directory
    """
    cache_dir = Path.home() / ".managedcleanroom" / "msal_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_msal_cache_file():
    """Get path to MSAL token cache file

    :return: Path to token cache file
    """
    return get_msal_cache_dir() / "token_cache.json"


def load_cache(msal_token_cache_file):
    """Load MSAL token cache from file

    Matches cleanroom extension pattern.

    :param msal_token_cache_file: Path to cache file
    :return: MSAL SerializableTokenCache
    """
    from msal import SerializableTokenCache

    cache = SerializableTokenCache()
    if os.path.exists(msal_token_cache_file):
        cache.deserialize(open(msal_token_cache_file, "r").read())
    return cache


def save_cache(cache, msal_token_cache_file):
    """Save MSAL token cache to file

    Matches cleanroom extension pattern.

    :param cache: MSAL SerializableTokenCache
    :param msal_token_cache_file: Path to cache file
    """
    if cache.has_state_changed:
        with open(msal_token_cache_file, "w") as f:
            f.write(cache.serialize())


def perform_device_code_flow(cmd):
    """Perform MSAL device code flow authentication

    Based on cleanroom extension's ms_perform_device_code_flow.

    :param cmd: CLI command context
    :return: Authentication result with access token and claims
    :raises: Exception if authentication fails
    """
    import msal

    # Get MSAL configuration
    config = get_msal_config(cmd)

    cache_file = str(get_msal_cache_file())
    token_cache = load_cache(cache_file)

    app = msal.PublicClientApplication(
        config['client_id'],
        authority=config['authority'],
        token_cache=token_cache
    )

    # Check for existing account in cache
    account = None
    for acc in app.get_accounts():
        if acc["environment"] == "login.microsoftonline.com" and acc["realm"] == config['tenant_id']:
            account = acc
            break

    if account:
        # Try silent token acquisition first
        logger.debug("Attempting silent token acquisition")
        result = app.acquire_token_silent(config['scopes'], account=account)
        if result and "access_token" in result:
            logger.debug("Successfully acquired token silently")
            save_cache(token_cache, cache_file)
            return result

    # No cached token found, perform device code flow
    logger.info("Initiating device code flow authentication")
    flow = app.initiate_device_flow(scopes=config['scopes'])

    if "user_code" not in flow:
        raise Exception(
            "Failed to create device flow: {}".format(
                flow.get(
                    'error_description',
                    'Unknown error')))

    # Display instructions to user (matches cleanroom pattern)
    print("Please go to", flow["verification_uri"])
    print("And enter the code:", flow["user_code"])

    # Wait for user to authenticate
    result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        # Extract user information from token claims
        name = result["id_token_claims"].get("name", "")
        email = result["id_token_claims"].get("preferred_username", "")
        oid = result["id_token_claims"].get("oid", "")

        if email == "" or oid == "":
            raise Exception(
                "Login failed: missing email or oid in token claims")

        logger.info("Authentication successful for user: %s", email)
        print("User:", name)
        print("Email:", email)
        print("oid:", oid)

        save_cache(token_cache, cache_file)
        return result

    err = result.get("error_description")
    raise Exception("Login failed: {}".format(err))


def get_msal_token(cmd):
    """Get cached MSAL access token if available

    Attempts silent token acquisition from cache.

    :param cmd: CLI command context
    :return: Tuple of (access_token, subscription, tenant_id) or None
    """
    import msal

    cache_file = str(get_msal_cache_file())
    if not os.path.exists(cache_file):
        logger.debug("No MSAL token cache found")
        return None

    try:
        # Get MSAL configuration
        config = get_msal_config(cmd)

        token_cache = load_cache(cache_file)
        app = msal.PublicClientApplication(
            config['client_id'],
            authority=config['authority'],
            token_cache=token_cache
        )

        # Find account in cache
        accounts = app.get_accounts()
        if not accounts:
            logger.debug("No accounts found in MSAL cache")
            return None

        # Use first account (typically only one)
        account = accounts[0]
        logger.debug(
            "Attempting to acquire token for account: %s",
            account.get('username', 'unknown'))

        # Try silent token acquisition
        result = app.acquire_token_silent(config['scopes'], account=account)

        if result and "access_token" in result:
            logger.debug("Successfully acquired MSAL token from cache")
            save_cache(token_cache, cache_file)

            # Extract tenant ID from token claims
            tenant_id = result.get(
                "id_token_claims", {}).get(
                "tid", config['tenant_id'])

            # Return in format expected by get_frontend_token()
            # (access_token, subscription, tenant_id)
            return (result["access_token"], None, tenant_id)

        logger.debug(
            "Failed to acquire token silently: %s",
            result.get('error', 'Unknown error'))
        return None

    except Exception as ex:
        logger.debug("Error retrieving MSAL token: %s", ex)
        return None


def clear_msal_cache():
    """Clear MSAL token cache (logout)

    Deletes the token cache file.
    """
    cache_file = get_msal_cache_file()
    if cache_file.exists():
        try:
            cache_file.unlink()
            logger.info("Cleared MSAL token cache: %s", cache_file)
        except Exception as ex:
            raise Exception("Failed to clear token cache: {}".format(ex))
    else:
        logger.debug("No MSAL token cache to clear")
