# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------

import functools
import json
import logging
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse
import xml.etree.ElementTree as ET

from typing import Dict, Any, Optional, Union, List, TYPE_CHECKING

if TYPE_CHECKING:
    import xml.etree.ElementTree as ET

import requests
from urllib3 import Retry  # Needs requests 2.16 at least to be safe

from .serialization import Deserializer, Model


_LOGGER = logging.getLogger(__name__)



class ClientRequest(requests.Request):
    """Wrapper for requests.Request object."""

    def format_parameters(self, params):
        # type: (Dict[str, str]) -> None
        """Format parameters into a valid query string.
        It's assumed all parameters have already been quoted as
        valid URL strings.

        :param dict params: A dictionary of parameters.
        """
        query = urlparse(self.url).query
        if query:
            self.url = self.url.partition('?')[0]
            existing_params = {
                p[0]: p[-1]
                for p in [p.partition('=') for p in query.split('&')]
            }
            params.update(existing_params)
        query_params = ["{}={}".format(k, v) for k, v in params.items()]
        query = '?' + '&'.join(query_params)
        self.url = self.url + query

    def add_content(self, data):
        # type: (Optional[Union[Dict[str, Any], ET.Element]]) -> None
        """Add a body to the request.

        :param data: Request body data, can be a json serializable
         object (e.g. dictionary) or a generator (e.g. file data).
        """
        if data is None:
            return

        if isinstance(data, ET.Element):
            self.data = ET.tostring(data, encoding="utf8")
            self.headers['Content-Length'] = str(len(self.data))
            return

        # By default, assume JSON
        try:
            self.data = json.dumps(data)
            self.headers['Content-Length'] = str(len(self.data))
        except TypeError:
            self.data = data


class ClientRawResponse(object):
    """Wrapper for response object.
    This allows for additional data to be gathereded from the response,
    for example deserialized headers.
    It also allows the raw response object to be passed back to the user.

    :param output: Deserialized response object.
    :param response: Raw response object.
    """

    def __init__(self, output, response):
        # type: (Union[Model, List[Model]], Optional[requests.Response]) -> None
        self.response = response
        self.output = output
        self.headers = {}  # type: Dict[str, Optional[Any]]
        self._deserialize = Deserializer()

    def add_headers(self, header_dict):
        # type: (Dict[str, str]) -> None
        """Deserialize a specific header.

        :param dict header_dict: A dictionary containing the name of the
         header and the type to deserialize to.
        """
        if not self.response:
            return
        for name, data_type in header_dict.items():
            value = self.response.headers.get(name)
            value = self._deserialize(data_type, value)
            self.headers[name] = value


class ClientRetryPolicy(object):
    """Retry configuration settings.
    Container for retry policy object.
    """

    safe_codes = [i for i in range(500) if i != 408] + [501, 505]

    def __init__(self):
        self.policy = Retry()
        self.policy.total = 3
        self.policy.connect = 3
        self.policy.read = 3
        self.policy.backoff_factor = 0.8
        self.policy.BACKOFF_MAX = 90

        retry_codes = [i for i in range(999) if i not in self.safe_codes]
        self.policy.status_forcelist = retry_codes
        self.policy.method_whitelist = ['HEAD', 'TRACE', 'GET', 'PUT',
                                        'OPTIONS', 'DELETE', 'POST', 'PATCH']

    def __call__(self):
        # type: () -> Retry
        """Return configuration to be applied to connection."""
        debug = ("Configuring retry: max_retries=%r, "
                 "backoff_factor=%r, max_backoff=%r")
        _LOGGER.debug(
            debug, self.retries, self.backoff_factor, self.max_backoff)
        return self.policy

    @property
    def retries(self):
        # type: () -> int
        """Total number of allowed retries."""
        return self.policy.total

    @retries.setter
    def retries(self, value):
        # type: (int) -> None
        self.policy.total = value
        self.policy.connect = value
        self.policy.read = value

    @property
    def backoff_factor(self):
        # type: () -> Union[int, float]
        """Factor by which back-off delay is incementally increased."""
        return self.policy.backoff_factor

    @backoff_factor.setter
    def backoff_factor(self, value):
        # type: (Union[int, float]) -> None
        self.policy.backoff_factor = value

    @property
    def max_backoff(self):
        # type: () -> int
        """Max retry back-off delay."""
        return self.policy.BACKOFF_MAX

    @max_backoff.setter
    def max_backoff(self, value):
        # type: (int) -> None
        self.policy.BACKOFF_MAX = value


class ClientRedirectPolicy(object):
    """Redirect configuration settings.
    """

    def __init__(self):
        self.allow = True
        self.max_redirects = 30

    def __bool__(self):
        # type: () -> bool
        """Whether redirects are allowed."""
        return self.allow

    def __call__(self):
        # type: () -> int
        """Return configuration to be applied to connection."""
        debug = "Configuring redirects: allow=%r, max=%r"
        _LOGGER.debug(debug, self.allow, self.max_redirects)
        return self.max_redirects

    def check_redirect(self, resp, request):
        # type: (requests.Response, requests.PreparedRequest) -> bool
        """Whether redirect policy should be applied based on status code."""
        if resp.status_code in (301, 302) and \
                request.method not in ['GET', 'HEAD']:
            return False
        return True


class ClientProxies(object):
    """Proxy configuration settings.
    Proxies can also be configured using HTTP_PROXY and HTTPS_PROXY
    environment variables, in which case set use_env_settings to True.
    """

    def __init__(self):
        self.proxies = {}
        self.use_env_settings = True

    def __call__(self):
        # type: () -> Dict[str, str]
        """Return configuration to be applied to connection."""
        proxy_string = "\n".join(
            ["    {}: {}".format(k, v) for k, v in self.proxies.items()])

        _LOGGER.debug("Configuring proxies: %r", proxy_string)
        debug = "Evaluate proxies against ENV settings: %r"
        _LOGGER.debug(debug, self.use_env_settings)
        return self.proxies

    def add(self, protocol, proxy_url):
        # type: (str, str) -> None
        """Add proxy.

        :param str protocol: Protocol for which proxy is to be applied. Can
         be 'http', 'https', etc. Can also include host.
        :param str proxy_url: The proxy URL. Where basic auth is required,
         use the format: http://user:password@host
        """
        self.proxies[protocol] = proxy_url


class ClientConnection(object):
    """Request connection configuration settings.
    """

    def __init__(self):
        self.timeout = 100
        self.verify = True
        self.cert = None
        self.data_block_size = 4096

    def __call__(self):
        # type: () -> Dict[str, Union[str, int]]
        """Return configuration to be applied to connection."""
        debug = "Configuring request: timeout=%r, verify=%r, cert=%r"
        _LOGGER.debug(debug, self.timeout, self.verify, self.cert)
        return {'timeout': self.timeout,
                'verify': self.verify,
                'cert': self.cert}
