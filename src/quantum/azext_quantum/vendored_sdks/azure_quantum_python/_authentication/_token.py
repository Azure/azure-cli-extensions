##
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
##
import json
from json.decoder import JSONDecodeError
import logging
import os
import time

# from azure.identity import CredentialUnavailableError
from ...azure_identity import CredentialUnavailableError
from azure.core.credentials import AccessToken
# from azure.quantum._constants import EnvironmentVariables
from .._constants import EnvironmentVariables

_LOGGER = logging.getLogger(__name__)


class _TokenFileCredential(object):
    """
    Implements a custom TokenCredential to use a local file as
    the source for an AzureQuantum token.

    It will only use the local file if the AZURE_QUANTUM_TOKEN_FILE
    environment variable is set, and references an existing json file
    that contains the access_token and expires_on timestamp in milliseconds.

    If the environment variable is not set, the file does not exist,
    or the token is invalid in any way (expired, for example),
    then the credential will throw CredentialUnavailableError,
    so that _ChainedTokenCredential can fallback to other methods.
    """
    def __init__(self):
        self.token_file = os.environ.get(EnvironmentVariables.QUANTUM_TOKEN_FILE)
        if self.token_file:
            _LOGGER.debug("Using provided token file location: %s", self.token_file)
        else:
            _LOGGER.debug("No token file location provided for %s environment variable.",
                          EnvironmentVariables.QUANTUM_TOKEN_FILE)

    def get_token(self, *scopes: str, **kwargs) -> AccessToken: # pylint:disable=unused-argument
        """Request an access token for `scopes`.
        This method is called automatically by Azure SDK clients.
        This method only returns tokens for the https://quantum.microsoft.com/.default scope.
        
        :param str scopes: desired scopes for the access token.
        
        :raises ~azure.identity.CredentialUnavailableError 
            when failing to get the token.
            The exception has a `message` attribute with the error message.
        """
        if not self.token_file:
            raise CredentialUnavailableError(message="Token file location not set.")

        if not os.path.isfile(self.token_file):
            raise CredentialUnavailableError(
                message=f"Token file at {self.token_file} does not exist.")

        try:
            token = self._parse_token_file(self.token_file)
        except JSONDecodeError as exception:
            raise CredentialUnavailableError(
                message="Failed to parse token file: Invalid JSON.") from exception
        except KeyError as exception:
            raise CredentialUnavailableError(
                message="Failed to parse token file: Missing expected value: "
                        + str(exception)) from exception
        except Exception as exception:
            raise CredentialUnavailableError(
                message="Failed to parse token file: " + str(exception)) from exception

        if token.expires_on <= time.time():
            raise CredentialUnavailableError(
                message=f"Token already expired at {time.asctime(time.gmtime(token.expires_on))}")

        return token

    def _parse_token_file(self, path) -> AccessToken:
        with open(path, mode="r", encoding="utf-8") as file:
            data = json.load(file)
            # Convert ms to seconds, since python time.time only handles epoch time in seconds
            expires_on = int(data["expires_on"]) / 1000
            token = AccessToken(data["access_token"],  expires_on)
            return token
