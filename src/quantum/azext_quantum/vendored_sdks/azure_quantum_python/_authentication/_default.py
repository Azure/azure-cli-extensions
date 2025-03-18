# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import re
from typing import Optional
import urllib3
from azure.core.credentials import AccessToken
# from azure.identity import (
from ...azure_identity import (
    AzurePowerShellCredential,
    EnvironmentCredential,
    ManagedIdentityCredential,
    AzureCliCredential,
    VisualStudioCodeCredential,
    InteractiveBrowserCredential,
    DeviceCodeCredential,
    _internal as AzureIdentityInternals,
)
from ._chained import _ChainedTokenCredential
from ._token import _TokenFileCredential
# from azure.quantum._constants import ConnectionConstants
from .._constants import ConnectionConstants

_LOGGER = logging.getLogger(__name__)
WWW_AUTHENTICATE_REGEX = re.compile(
    r"""
        ^
        Bearer\sauthorization_uri="
            https://(?P<authority>[^/]*)/
            (?P<tenant_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})
        "
    """,
    re.VERBOSE | re.IGNORECASE)
WWW_AUTHENTICATE_HEADER_NAME = "WWW-Authenticate"


class _DefaultAzureCredential(_ChainedTokenCredential):
    """
    Based on Azure.Identity.DefaultAzureCredential from:
    https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/azure/identity/_credentials/default.py

    The three key differences are:
    1) Inherit from _ChainedTokenCredential, which has 
       more aggressive error handling than ChainedTokenCredential
    2) Instantiate the internal credentials the first time the get_token gets called
       such that we can get the tenant_id if it was not passed by the user (but we don't
       want to do that in the constructor).
       We automatically identify the user's tenant_id for a given subscription 
       so that users with MSA accounts don't need to pass it.
       This is a mitigation for bug https://github.com/Azure/azure-sdk-for-python/issues/18975
       We need the following parameters to enable auto-detection of tenant_id
       - subscription_id
       - arm_endpoint (defaults to the production url "https://management.azure.com/")
    3) Add custom TokenFileCredential as first method to attempt,
       which will look for a local access token.
    """
    def __init__(
        self,
        arm_endpoint: str,
        subscription_id: str,
        client_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        authority: Optional[str] = None,
    ):
        if arm_endpoint is None:
            raise ValueError("arm_endpoint is mandatory parameter")
        if subscription_id is None:
            raise ValueError("subscription_id is mandatory parameter")

        self.authority = self._authority_or_default(
            authority=authority,
            arm_endpoint=arm_endpoint)
        self.tenant_id = tenant_id
        self.subscription_id = subscription_id
        self.arm_endpoint = arm_endpoint
        self.client_id = client_id
        # credentials will be created lazy on the first call to get_token
        super(_DefaultAzureCredential, self).__init__()

    def _authority_or_default(self, authority: str, arm_endpoint: str):
        if authority:
            return AzureIdentityInternals.normalize_authority(authority)
        if arm_endpoint == ConnectionConstants.ARM_DOGFOOD_ENDPOINT:
            return ConnectionConstants.DOGFOOD_AUTHORITY
        return ConnectionConstants.AUTHORITY

    def _initialize_credentials(self):
        self._discover_tenant_id_(
            arm_endpoint=self.arm_endpoint,
            subscription_id=self.subscription_id)
        credentials = []
        credentials.append(_TokenFileCredential())
        credentials.append(EnvironmentCredential())
        if self.client_id:
            credentials.append(ManagedIdentityCredential(client_id=self.client_id))
        if self.authority and self.tenant_id:
            credentials.append(VisualStudioCodeCredential(authority=self.authority, tenant_id=self.tenant_id))
            credentials.append(AzureCliCredential(tenant_id=self.tenant_id))
            credentials.append(AzurePowerShellCredential(tenant_id=self.tenant_id))
            credentials.append(InteractiveBrowserCredential(authority=self.authority, tenant_id=self.tenant_id))
            if self.client_id:
                credentials.append(DeviceCodeCredential(authority=self.authority, client_id=self.client_id, tenant_id=self.tenant_id))
        self.credentials = credentials

    def get_token(self, *scopes: str, **kwargs) -> AccessToken:
        """
        Request an access token for `scopes`.
        This method is called automatically by Azure SDK clients.
        
        :param str scopes: desired scopes for the access token.
        This method requires at least one scope.
        
        :raises ~azure.core.exceptions.ClientAuthenticationError:authentication failed.
            The exception has a `message` attribute listing each authentication
            attempt and its error message.
        """
        # lazy-initialize the credentials
        if self.credentials is None or len(self.credentials) == 0:
            self._initialize_credentials()

        return super(_DefaultAzureCredential, self).get_token(*scopes, **kwargs)

    def _discover_tenant_id_(self, arm_endpoint:str, subscription_id:str):
        """
        If the tenant_id was not given, try to obtain it
        by calling the management endpoint for the subscription_id,
        or by applying default values.
        """
        if self.tenant_id:
            return

        try:
            url = (
                f"{arm_endpoint.rstrip('/')}/subscriptions/"
                + f"{subscription_id}?api-version=2018-01-01"
                + "&discover-tenant-id"  # used by the test recording infrastructure
            )
            http = urllib3.PoolManager()
            response = http.request(
                method="GET",
                url=url,
            )
            if WWW_AUTHENTICATE_HEADER_NAME in response.headers:
                www_authenticate = response.headers[WWW_AUTHENTICATE_HEADER_NAME]
                match = re.search(WWW_AUTHENTICATE_REGEX, www_authenticate)
                if match:
                    self.tenant_id = match.group("tenant_id")
        # pylint: disable=broad-exception-caught
        except Exception as ex:
            _LOGGER.error(ex)

        # apply default values
        self.tenant_id = self.tenant_id or ConnectionConstants.MSA_TENANT_ID
