# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azext_arcdata.arm_sdk.azure.models.spn import Spn
from azext_arcdata.dc.util import get_config_file_path
from azext_arcdata.core.util import display
from azext_arcdata.core.prompt import prompt_for_input
from . import constants as azure_constants
from knack.log import get_logger

import atexit
import os
import msal

log = get_logger(__name__)

# #############################################################################
# -- AAD related functions --
# #############################################################################


def acquire_token(scopes):
    """
    Obtains AAD bearer token for given scope
    """
    spn = _check_for_spn()

    token = None
    while not token:
        try:
            token = _get_token_using_msal(spn, scopes)
        except BaseException:
            display(
                'Service principal "{}" failed to authenticate with Azure. '
                "Please try again\n".format(spn.client_id)
            )

        # If we did not get a token, prompt for spn
        if not token:
            spn = _prompt_for_spn()

    _store_spn_in_env(spn)
    return token


def _check_for_spn():
    """
    Checks if service principal is stored in the environment
    or contained in config_file. Returns spn if found, prompts
    user for spn otherwise
    """
    spn = Spn()

    # Check if spn in environment
    get_spn_from_env = True
    for spn_env in azure_constants.SPN_ENV_KEYS.values():
        if spn_env not in os.environ or not os.environ[spn_env]:
            get_spn_from_env = False
            break
    if get_spn_from_env:
        spn.authority = os.environ[azure_constants.SPN_ENV_KEYS["authority"]]
        spn.tenant_id = os.environ[azure_constants.SPN_ENV_KEYS["tenant_id"]]
        spn.client_id = os.environ[azure_constants.SPN_ENV_KEYS["client_id"]]
        spn.client_secret = os.environ[
            azure_constants.SPN_ENV_KEYS["client_secret"]
        ]
        return spn
    else:
        # Prompt the user
        return _prompt_for_spn()


def _store_spn_in_env(spn: Spn):
    """
    Stores service principal object in environment
    :param spn: Service Principal object
    """
    if spn.authority and spn.client_id and spn.tenant_id and spn.client_secret:
        os.environ[azure_constants.SPN_ENV_KEYS["authority"]] = spn.authority
        os.environ[azure_constants.SPN_ENV_KEYS["tenant_id"]] = spn.tenant_id
        os.environ[azure_constants.SPN_ENV_KEYS["client_id"]] = spn.client_id
        os.environ[
            azure_constants.SPN_ENV_KEYS["client_secret"]
        ] = spn.client_secret
    else:
        missing_keys = []
        for spn_env in azure_constants.SPN_ENV_KEYS.values():
            if spn_env not in os.environ or not os.environ[spn_env]:
                missing_keys.append(spn_env)
        raise ValueError(
            "The following service principal values are missing: {}".format(
                ", ".join(missing_keys)
            )
        )


def _prompt_for_spn():
    """
    Prompts the user to enter the service principal info
    """
    spn = Spn()

    display("Please provide the service principal information for upload:")
    # public cloud we can use the default login url
    spn.authority = azure_constants.PUBLIC_CLOUD_LOGIN_URL
    spn.tenant_id = prompt_for_input("Service principal tenant id: ")
    spn.client_id = prompt_for_input("Service principal client id: ")
    spn.client_secret = prompt_for_input("Service principal secret: ")

    return spn


def _get_token_using_msal(spn, scopes):
    """
    Uses the MSAL library to obtain AAD auth token for
    the given service principal and scope(s)

    :param spn: service principal object
    :param scopes: list containing scopes requested to
    access a protected API

    :return: auth token string, None if auth fails
    """
    cache = msal.SerializableTokenCache()
    cache_file = _get_cache_file()
    if os.path.exists(cache_file):
        cache.deserialize(open(cache_file, "r").read())
    atexit.register(
        lambda: open(cache_file, "w").write(cache.serialize())
        if cache.has_state_changed
        else None
    )

    app = msal.ConfidentialClientApplication(
        spn.client_id,
        spn.client_secret,
        azure_constants.AAD_LOGIN_URL + spn.tenant_id,
        token_cache=cache,
    )

    # First look up a token from cache, since we are looking for token for the
    # current app, NOT for an end user. Notice we give account parameter as
    # None.
    result = app.acquire_token_silent(scopes, account=None)
    if result:
        log.info("Get AAD token from cache.")
    else:
        log.info("No suitable token exists in cache. Get a new one from AAD.")
        result = app.acquire_token_for_client(scopes)
    if "access_token" in result:
        return result["access_token"]
    else:
        log.error(
            "Failed to get access token from AAD with the following error"
        )
        log.error('Error: "{}"'.format(result.get("error")))
        log.error(
            'Error description: "{}"'.format(result.get("error_description"))
        )
        log.error('Correlation Id: "{}"'.format(result.get("correlation_id")))


def _get_cache_file():
    """
    Get token cache file
    """
    cache_file = get_config_file_path(azure_constants.AAD_PROFILE_FILENAME)

    if not os.path.exists(cache_file):
        log.info("Create AAD token cache file.")
        f = open(cache_file, "w+")
        f.close()

    return cache_file
