# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Authentication and client management for Analytics Frontend API"""

from azure.cli.core._profile import Profile
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import CLIError
from knack.log import get_logger

logger = get_logger(__name__)


def get_frontend_token(cmd):
    """Get access token from MSAL cache or Azure context

    Authentication priority:
    1. MSAL token (device code flow) - if user ran 'frontend login'
    2. Azure CLI token (az login) - fallback

    :param cmd: CLI command context
    :return: Tuple of (access_token, subscription, tenant)
    :raises: CLIError if token cannot be obtained
    """
    import os
    from ._msal_auth import get_msal_token, get_auth_scope

    profile = Profile(cli_ctx=cmd.cli_ctx)
    subscription = get_subscription_id(cmd.cli_ctx)

    # Priority 0: explicit token via environment variable (for local/test envs only)
    env_token = os.environ.get('MANAGEDCLEANROOM_ACCESS_TOKEN')
    if env_token:
        logger.warning("Using token from MANAGEDCLEANROOM_ACCESS_TOKEN env var FOR TESTING PURPOSES ONLY")
        from collections import namedtuple
        AccessToken = namedtuple('AccessToken', ['token', 'expires_on'])
        token_obj = AccessToken(token=env_token, expires_on=0)
        return (token_obj, subscription, None)

    auth_scope = get_auth_scope(cmd)

    logger.debug("Using auth scope: %s", auth_scope)

    try:
        msal_token = get_msal_token(cmd)
        if msal_token:
            logger.debug("Using MSAL device code flow token")
            return (msal_token[0], subscription, msal_token[2])

        logger.debug("Using Azure CLI (az login) token")
        return profile.get_raw_token(
            subscription=subscription,
            resource=auth_scope
        )

    except Exception as ex:
        raise CLIError(
            f'Failed to get access token: {str(ex)}\n\n'
            'Please authenticate using one of:\n'
            '  1. az managedcleanroom frontend login  (MSAL device code flow)\n'
            '  2. az login (Azure CLI authentication)\n')


def get_frontend_config(cmd):
    """Read frontend endpoint configuration from Azure CLI config

    :param cmd: CLI command context
    :return: Configured endpoint URL or None
    :rtype: str or None
    """
    config = cmd.cli_ctx.config
    return config.get('managedcleanroom-frontend', 'endpoint', fallback=None)


def set_frontend_config(cmd, endpoint):
    """Store frontend endpoint in Azure CLI config

    :param cmd: CLI command context
    :param endpoint: API endpoint URL to store
    :type endpoint: str
    """
    cmd.cli_ctx.config.set_value(
        'managedcleanroom-frontend',
        'endpoint',
        endpoint)


def get_frontend_client(cmd, endpoint=None):
    """Create Analytics Frontend API client with Azure authentication

    Uses Profile.get_raw_token() to fetch access token from Azure context.
    Token is fetched fresh on every invocation.

    :param cmd: CLI command context
    :param endpoint: Optional explicit endpoint URL (overrides config)
    :type endpoint: str
    :return: Configured AnalyticsFrontendAPI client
    :raises: CLIError if token fetch fails or endpoint not configured
    """
    from .analytics_frontend_api import AnalyticsFrontendAPI
    from azure.core.pipeline.policies import BearerTokenCredentialPolicy, SansIOHTTPPolicy

    api_endpoint = endpoint or get_frontend_config(cmd)
    if not api_endpoint:
        raise CLIError(
            'Analytics Frontend API endpoint not configured.\n'
            'Configure using: az config set managedcleanroom-frontend.endpoint=<url>\n'
            'Or use the --endpoint flag with your command.')

    access_token_obj, _, _ = get_frontend_token(cmd)

    logger.debug(
        "Creating Analytics Frontend API client for endpoint: %s",
        api_endpoint)

    # Check if this is a local development endpoint
    is_local = api_endpoint.startswith(
        'http://localhost') or api_endpoint.startswith('http://127.0.0.1')

    # Create simple credential wrapper for the access token
    credential = type('TokenCredential', (), {
        'get_token': lambda self, *args, **kwargs: access_token_obj
    })()

    if is_local:
        # For local development, create a custom auth policy that bypasses
        # HTTPS check
        class LocalBearerTokenPolicy(SansIOHTTPPolicy):
            """Bearer token policy that allows HTTP for local development"""

            def __init__(self, token_obj):
                self._token = token_obj  # AccessToken object

            def on_request(self, request):
                """Add authorization header with bearer token"""
                # Extract token string from AccessToken object
                # The token might be a tuple ('Bearer', 'token_string') or just
                # the token string
                if hasattr(self._token, 'token'):
                    token_value = self._token.token
                else:
                    token_value = self._token

                # If it's a tuple, extract the actual token (second element)
                if isinstance(token_value, tuple) and len(token_value) >= 2:
                    token_string = token_value[1]
                else:
                    token_string = str(token_value)

                auth_header = f'Bearer {token_string}'
                logger.debug(
                    "Setting Authorization header: Bearer %s...", token_string[:50])
                request.http_request.headers['Authorization'] = auth_header

        auth_policy = LocalBearerTokenPolicy(access_token_obj)
    else:
        # For production, use standard bearer token policy with HTTPS
        # enforcement
        # Use configured auth_scope with .default suffix for Azure SDK
        from ._msal_auth import get_auth_scope
        scope = get_auth_scope(cmd)
        if not scope.endswith('/.default'):
            scope = f'{scope}/.default'

        auth_policy = BearerTokenCredentialPolicy(
            credential,
            scope
        )

    # Return configured client
    return AnalyticsFrontendAPI(
        endpoint=api_endpoint,
        authentication_policy=auth_policy
    )
