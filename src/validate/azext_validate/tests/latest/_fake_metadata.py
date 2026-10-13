# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Synthetic published command metadata for tests, in the same shape as the public metadata stores."""

import json


class FakeResponse:  # pylint: disable=too-few-public-methods
    def __init__(self, body):
        self.status_code = 200 if body is not None else 404
        self._body = body
        self.text = body if isinstance(body, str) else json.dumps(body)

    def json(self):
        return json.loads(self._body) if isinstance(self._body, str) else self._body


class FakeSession:  # pylint: disable=too-few-public-methods
    """A requests-like session that serves fixed responses and records every URL asked for."""

    def __init__(self, responses):
        self.responses = responses
        self.urls = []

    def get(self, url, **_kwargs):
        self.urls.append(url)
        return FakeResponse(self.responses.get(url))
