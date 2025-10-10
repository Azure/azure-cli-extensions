# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from knack.log import get_logger

import os
import abc
import time

__all__ = ["ArcDataCliCredential"]

logger = get_logger(__name__)


class BaseTokenMixin(abc.ABC):
    DEFAULT_REFRESH_OFFSET = 300
    """
    Time in seconds as a padding offset.
    """
    DEFAULT_TOKEN_REFRESH_RETRY_DELAY = 30
    """
    Time in seconds as a padding offset for token refresh.
    """

    def __init__(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        self._last_request_time = 0
        super(BaseTokenMixin, self).__init__(*args, **kwargs)  # type: ignore

    @abc.abstractmethod
    def acquire_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> Optional[AccessToken]
        """
        Attempt to acquire an access token from a cache or by redeeming a
        refresh token
        """

    @abc.abstractmethod
    def request_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        """Request an access token"""

    def should_refresh(self, token):
        # type: (AccessToken) -> bool
        now = int(time.time())
        if token.expires_on - now > BaseTokenMixin.DEFAULT_REFRESH_OFFSET:
            return False
        if (
            now - self._last_request_time
            < BaseTokenMixin.DEFAULT_TOKEN_REFRESH_RETRY_DELAY
        ):
            return False
        return True

    def get_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        """
        Request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method
        requires at least one scope.
        :keyword str tenant_id: optional tenant to include in the token request.

        :rtype: :class:`azure.core.credentials.AccessToken`

        :raises CredentialUnavailableError: the credential is unable to attempt
                authentication because it lacks required data, state, or
                platform support
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication
                failed. The error's ``message``
                attribute gives a reason.
        """


# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #


class ArcDataCliCredential(BaseTokenMixin):
    def __init__(self, scopes=None):
        super(ArcDataCliCredential, self).__init__()
        self._scopes = scopes

    # override
    def get_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        """
        Request an access token for `scopes`.
        """
        try:
            token = self.acquire_token(*scopes)
            if not token:
                self._last_request_time = int(time.time())
                token = self.request_token(*scopes)
            elif self.should_refresh(token):
                try:
                    self._last_request_time = int(time.time())
                    token = self.request_token(*scopes, **kwargs)
                except Exception:  # pylint:disable=broad-except
                    pass
            logger.debug("%s.get_token succeeded", self.__class__.__name__)
            return token

        except Exception as ex:
            logger.debug("%s.get_token: %s", self.__class__.__name__, ex)
            raise

    # override
    def acquire_token(self, *scopes):
        # type: (*str) -> Optional[AccessToken]
        """
        Attempt to acquire an access token from a cache or by redeeming
        a refresh token.
        """
        from azure.cli.core._profile import Profile
        from azure.cli.core._session import ACCOUNT
        from azure.cli.core._environment import get_config_dir

        azure_folder = get_config_dir()
        ACCOUNT.load(os.path.join(azure_folder, "azureProfile.json"))
        p = Profile(storage=ACCOUNT)
        cred, subscription_id, tenant_id = p.get_login_credentials()
        scopes = ["https://management.azure.com/.default"]
        access_token = cred.get_token(*scopes)

        return access_token

    # override
    def request_token(self, *scopes, **kwargs):
        # TODO: Impl refresh logic if possible. For now we give error
        # to az login again
        return super(ArcDataCliCredential, self).request_token(
            *scopes, **kwargs
        )
