# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


class TokenCredential(object):
    """
    Represents a token that is used to authorize HTTPS requests.
    The token can be updated by the user.

    :ivar str token:
        The authorization token. It can be set by the user at any point in a thread-safe way.
    """

    def __init__(self, initial_value):
        """
        :param initial_value: initial value for the token.
        """
        self.token = initial_value

    def update_token(self, new_value):
        """
        :param new_value: new value to be set as the token.
        """
        self.token = new_value

    def get_token(self):
        """
        :return: current token value.
        """
        return self.token
