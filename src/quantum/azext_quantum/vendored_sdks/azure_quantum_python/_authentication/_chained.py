# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging

import sys
from azure.core.exceptions import ClientAuthenticationError
# from azure.identity import CredentialUnavailableError
from ...azure_identity import CredentialUnavailableError
from azure.core.credentials import AccessToken, TokenCredential


_LOGGER = logging.getLogger(__name__)



def filter_credential_warnings(record):
    """Suppress warnings from credentials other than DefaultAzureCredential"""
    if record.levelno == logging.WARNING:
        message = record.getMessage()
        return "DefaultAzureCredential" in message
    return True


def _get_error_message(history):
    attempts = []
    for credential, error in history:
        if error:
            attempts.append(f"{credential.__class__.__name__}: {error}")
        else:
            attempts.append(credential.__class__.__name__)
    return """
Attempted credentials:\n\t{}""".format(
        "\n\t".join(attempts)
    )


class _ChainedTokenCredential(object):
    """
    Based on Azure.Identity.ChainedTokenCredential from:
    https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/azure/identity/_credentials/chained.py

    The key difference is that we don't stop attempting all credentials
    if some of then failed or raised an exception.
    We also don't log a warning unless all credential attempts have failed.
    """

    def __init__(self, *credentials: TokenCredential):
        self._successful_credential = None
        self.credentials = credentials

    def get_token(self, *scopes: str, **kwargs) -> AccessToken:  # pylint:disable=unused-argument
        """
        Request a token from each chained credential, in order,
        returning the first token received.
        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token.
        This method requires at least one scope.

        :raises ~azure.core.exceptions.ClientAuthenticationError:
        no credential in the chain provided a token
        """
        history = []

        # Suppress warnings from credentials in Azure.Identity
        azure_identity_logger = logging.getLogger("azure.identity")
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.addFilter(filter_credential_warnings)
        azure_identity_logger.addHandler(handler)
        try:
            for credential in self.credentials:
                try:
                    token = credential.get_token(*scopes, **kwargs)
                    _LOGGER.info(
                        "%s acquired a token from %s",
                        self.__class__.__name__,
                        credential.__class__.__name__,
                    )
                    self._successful_credential = credential
                    return token
                except CredentialUnavailableError as ex:
                    # credential didn't attempt authentication because
                    # it lacks required data or state -> continue
                    history.append((credential, ex.message))
                    _LOGGER.info(
                        "%s - %s is unavailable",
                        self.__class__.__name__,
                        credential.__class__.__name__,
                    )
                except Exception as ex:  # pylint: disable=broad-except
                    # credential failed to authenticate,
                    # or something unexpectedly raised -> break
                    history.append((credential, str(ex)))
                    # instead of logging a warning, we just want to log an info
                    # since other credentials might succeed
                    _LOGGER.info(
                        '%s.get_token failed: %s raised unexpected error "%s"',
                        self.__class__.__name__,
                        credential.__class__.__name__,
                        ex,
                        exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
                    )
                    # here we do NOT want break and
                    # will continue to try other credentials

        finally:
            # Re-enable warnings from credentials in Azure.Identity
            azure_identity_logger.removeHandler(handler)

        # if all attempts failed, only then we log a warning and raise an error
        attempts = _get_error_message(history)
        message = (
            self.__class__.__name__
            + " failed to retrieve a token from the included credentials."
            + attempts
        )
        _LOGGER.warning(message)
        raise ClientAuthenticationError(message=message)
