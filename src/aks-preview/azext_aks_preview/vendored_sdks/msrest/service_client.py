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

import contextlib
import logging
import os
try:
    from urlparse import urljoin, urlparse
except ImportError:
    from urllib.parse import urljoin, urlparse
import warnings

from typing import Any, Dict, Union, IO, Tuple, Optional, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from .configuration import Configuration

from oauthlib import oauth2
import requests.adapters

from .authentication import Authentication
from .pipeline import ClientRequest
from .http_logger import log_request, log_response
from .exceptions import (
    TokenExpiredError,
    ClientRequestError,
    raise_with_traceback)


_LOGGER = logging.getLogger(__name__)

class SDKClient(object):
    """The base class of all generated SDK client.
    """
    def __init__(self, creds, config):
        # type: (Any, Configuration) -> None
        self._client = ServiceClient(creds, config)

    def close(self):
        # type: () -> None
        """Close the client if keep_alive is True.
        """
        self._client.close()

    def __enter__(self):
        # type: () -> SDKClient
        self._client.__enter__()
        return self

    def __exit__(self, *exc_details):
        self._client.__exit__(*exc_details)

class _RequestsHTTPDriver(object):

    _protocols = ['http://', 'https://']

    def __init__(self, config):
        # type: (Configuration) -> None
        self.config = config
        self.session = requests.Session()

    def __enter__(self):
        # type: () -> _RequestsHTTPDriver
        return self

    def __exit__(self, *exc_details):
        self.close()

    def close(self):
        self.session.close()

    def configure_session(self, **config):
        # type: (str) -> Dict[str, Any]
        """Apply configuration to session.

        :param config: Specific configuration overrides.
        :rtype: dict
        :return: A dict that will be kwarg-send to session.request
        """
        kwargs = self.config.connection()  # type: Dict[str, Any]
        for opt in ['timeout', 'verify', 'cert']:
            kwargs[opt] = config.get(opt, kwargs[opt])
        kwargs.update({k:config[k] for k in ['cookies'] if k in config})
        kwargs['allow_redirects'] = config.get(
            'allow_redirects', bool(self.config.redirect_policy))

        kwargs['headers'] = self.config.headers.copy()
        kwargs['headers']['User-Agent'] = self.config.user_agent
        proxies = config.get('proxies', self.config.proxies())
        if proxies:
            kwargs['proxies'] = proxies

        kwargs['stream'] = config.get('stream', True)

        self.session.max_redirects = int(config.get('max_redirects', self.config.redirect_policy()))
        self.session.trust_env = bool(config.get('use_env_proxies', self.config.proxies.use_env_settings))

        # Patch the redirect method directly *if not done already*
        if not getattr(self.session.resolve_redirects, 'is_mrest_patched', False):
            redirect_logic = self.session.resolve_redirects

            def wrapped_redirect(resp, req, **kwargs):
                attempt = self.config.redirect_policy.check_redirect(resp, req)
                return redirect_logic(resp, req, **kwargs) if attempt else []
            wrapped_redirect.is_mrest_patched = True  # type: ignore

            self.session.resolve_redirects = wrapped_redirect  # type: ignore

        # if "enable_http_logger" is defined at the operation level, take the value.
        # if not, take the one in the client config
        # if not, disable http_logger
        hooks = []
        if config.get("enable_http_logger", self.config.enable_http_logger):
            def log_hook(r, *args, **kwargs):
                log_request(None, r.request)
                log_response(None, r.request, r, result=r)
            hooks.append(log_hook)

        def make_user_hook_cb(user_hook, session):
            def user_hook_cb(r, *args, **kwargs):
                kwargs.setdefault("msrest", {})['session'] = session
                return user_hook(r, *args, **kwargs)
            return user_hook_cb

        for user_hook in self.config.hooks:
            hooks.append(make_user_hook_cb(user_hook, self.session))

        if hooks:
            kwargs['hooks'] = {'response': hooks}

        # Change max_retries in current all installed adapters
        max_retries = config.get('retries', self.config.retry_policy())
        for protocol in self._protocols:
            self.session.adapters[protocol].max_retries=max_retries

        output_kwargs = self.config.session_configuration_callback(
            self.session,
            self.config,
            config,
            **kwargs
        )
        if output_kwargs is not None:
            kwargs = output_kwargs

        return kwargs

    def send(self, request, **config):
        # type: (ClientRequest, Any) -> requests.Response
        """Send request object according to configuration.

        :param ClientRequest request: The request object to be sent.
        :param config: Any specific config overrides
        """
        kwargs = config.copy()
        if request.files:
            kwargs['files'] = request.files
        elif request.data:
            kwargs['data'] = request.data
        kwargs.setdefault("headers", {}).update(request.headers)

        response = self.session.request(
            request.method,
            request.url,
            **kwargs)
        return response

class ServiceClient(object):
    """REST Service Client.
    Maintains client pipeline and handles all requests and responses.

    :param Configuration config: Service configuration.
    :param Authentication creds: Authenticated credentials.
    """

    def __init__(self, creds, config):
        # type: (Any, Configuration) -> None
        self.config = config
        self.creds = creds if creds else Authentication()
        self._http_driver = _RequestsHTTPDriver(config)

    def __enter__(self):
        # type: () -> ServiceClient
        self.config.keep_alive = True
        self._http_driver.__enter__()
        return self

    def __exit__(self, *exc_details):
        self._http_driver.__exit__(*exc_details)
        self.config.keep_alive = False

    def close(self):
        # type: () -> None
        """Close the session if keep_alive is True.
        """
        self._http_driver.close()

    def _format_data(self, data):
        # type: (Union[str, IO]) -> Union[Tuple[None, str], Tuple[Optional[str], IO, str]]
        """Format field data according to whether it is a stream or
        a string for a form-data request.

        :param data: The request field data.
        :type data: str or file-like object.
        """
        if hasattr(data, 'read'):
            data = cast(IO, data)
            data_name = None
            try:
                if data.name[0] != '<' and data.name[-1] != '>':
                    data_name = os.path.basename(data.name)
            except (AttributeError, TypeError):
                pass
            return (data_name, data, "application/octet-stream")
        return (None, cast(str, data))

    def _request(self, url, params, headers, content, form_content):
        # type: (Optional[str], Optional[Dict[str, str]], Optional[Dict[str, str]], Any, Optional[Dict[str, Any]]) -> ClientRequest
        """Create ClientRequest object.

        :param str url: URL for the request.
        :param dict params: URL query parameters.
        :param dict headers: Headers
        :param dict form_content: Form content
        """
        request = ClientRequest()

        if url:
            request.url = self.format_url(url)

        if params:
            request.format_parameters(params)

        if headers:
            request.headers.update(headers)
        # All requests should contain a Accept.
        # This should be done by Autorest, but wasn't in old Autorest
        # Force it for now, but might deprecate it later.
        if "Accept" not in request.headers:
            _LOGGER.debug("Accept header absent and forced to application/json")
            request.headers['Accept'] = 'application/json'

        if content is not None:
            request.add_content(content)

        if form_content:
            self._add_formdata(request, form_content)

        return request

    def _add_formdata(self, request, content=None):
        # type: (ClientRequest, Optional[Dict[str, str]]) -> None
        """Add data as a multipart form-data request to the request.

        We only deal with file-like objects or strings at this point.
        The requests is not yet streamed.

        :param ClientRequest request: The request object to be sent.
        :param dict headers: Any headers to add to the request.
        :param dict content: Dictionary of the fields of the formdata.
        """
        if content is None:
            content = {}
        content_type = request.headers.pop('Content-Type', None) if request.headers else None

        if content_type and content_type.lower() == 'application/x-www-form-urlencoded':
            # Do NOT use "add_content" that assumes input is JSON
            request.data = {f: d for f, d in content.items() if d is not None}
        else: # Assume "multipart/form-data"
            request.files = {f: self._format_data(d) for f, d in content.items() if d is not None}

    def send_formdata(self, request, headers=None, content=None, **config):
        """Send data as a multipart form-data request.
        We only deal with file-like objects or strings at this point.
        The requests is not yet streamed.

        This method is deprecated, and shouldn't be used anymore.

        :param ClientRequest request: The request object to be sent.
        :param dict headers: Any headers to add to the request.
        :param dict content: Dictionary of the fields of the formdata.
        :param config: Any specific config overrides.
        """
        request.headers = headers
        self._add_formdata(request, content)
        return self.send(request, **config)

    def send(self, request, headers=None, content=None, **config):
        """Prepare and send request object according to configuration.

        :param ClientRequest request: The request object to be sent.
        :param dict headers: Any headers to add to the request.
        :param content: Any body data to add to the request.
        :param config: Any specific config overrides
        """
        if self.config.keep_alive:
            http_driver = self._http_driver
        else:
            http_driver = _RequestsHTTPDriver(self.config)

        try:
            self.creds.signed_session(http_driver.session)
        except TypeError: # Credentials does not support session injection
            http_driver.session = self.creds.signed_session()
            if http_driver is self._http_driver:
                _LOGGER.warning("Your credentials class does not support session injection. Performance will not be at the maximum.")

        kwargs = http_driver.configure_session(**config)

        # "content" and "headers" are deprecated, only old SDK
        if headers:
            request.headers.update(headers)
        if not request.files and request.data == [] and content is not None:
            request.add_content(content)
        # End of deprecation

        response = None
        try:
            try:
                response = http_driver.send(request, **kwargs)
                return response
            except (oauth2.rfc6749.errors.InvalidGrantError,
                    oauth2.rfc6749.errors.TokenExpiredError) as err:
                error = "Token expired or is invalid. Attempting to refresh."
                _LOGGER.warning(error)

            try:
                try:
                    self.creds.refresh_session(http_driver.session)
                except TypeError: # Credentials does not support session injection
                    http_driver.session = self.creds.refresh_session()
                    if http_driver is self._http_driver:
                        _LOGGER.warning("Your credentials class does not support session injection. Performance will not be at the maximum.")
                    # Only reconfigure on refresh if it's a new session
                    kwargs = http_driver.configure_session(**config)

                response = http_driver.send(request, **kwargs)
                return response
            except (oauth2.rfc6749.errors.InvalidGrantError,
                    oauth2.rfc6749.errors.TokenExpiredError) as err:
                msg = "Token expired or is invalid."
                raise_with_traceback(TokenExpiredError, msg, err)

        except (requests.RequestException,
                oauth2.rfc6749.errors.OAuth2Error) as err:
            msg = "Error occurred in request."
            raise_with_traceback(ClientRequestError, msg, err)
        finally:
            self._close_local_session_if_necessary(response, http_driver, kwargs['stream'])

    def _close_local_session_if_necessary(self, response, http_driver, stream):
        # Do NOT close session if using my own HTTP driver. No exception.
        if self._http_driver is http_driver:
            return
        # Here, it's a local session, I might close it.
        if not response or not stream:
            http_driver.session.close()

    def stream_download(self, data, callback):
        """Generator for streaming request body data.

        :param data: A response object to be streamed.
        :param callback: Custom callback for monitoring progress.
        """
        block = self.config.connection.data_block_size
        if not data._content_consumed:
            with contextlib.closing(data) as response:
                for chunk in response.iter_content(block):
                    if not chunk:
                        break
                    if callback and callable(callback):
                        callback(chunk, response=response)
                    yield chunk
        else:
            for chunk in data.iter_content(block):
                if not chunk:
                    break
                if callback and callable(callback):
                    callback(chunk, response=data)
                yield chunk
        data.close()

    def stream_upload(self, data, callback):
        """Generator for streaming request body data.

        :param data: A file-like object to be streamed.
        :param callback: Custom callback for monitoring progress.
        """
        while True:
            chunk = data.read(self.config.connection.data_block_size)
            if not chunk:
                break
            if callback and callable(callback):
                callback(chunk, response=None)
            yield chunk

    def format_url(self, url, **kwargs):
        # type: (str, Any) -> str
        """Format request URL with the client base URL, unless the
        supplied URL is already absolute.

        :param str url: The request URL to be formatted if necessary.
        """
        url = url.format(**kwargs)
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            url = url.lstrip('/')
            base = self.config.base_url.format(**kwargs).rstrip('/')
            url = urljoin(base + '/', url)
        return url

    def add_header(self, header, value):
        # type: (str, str) -> None
        """Add a persistent header - this header will be applied to all
        requests sent during the current client session.

        .. deprecated:: 0.5.0
           Use config.headers instead

        :param str header: The header name.
        :param str value: The header value.
        """
        warnings.warn("Private attribute _client.add_header is deprecated. Use config.headers instead.",
                      DeprecationWarning)
        self.config.headers[header] = value

    def get(self, url=None, params=None, headers=None, content=None, form_content=None):
        # type: (Optional[str], Optional[Dict[str, str]], Optional[Dict[str, str]], Any, Optional[Dict[str, Any]]) -> ClientRequest
        """Create a GET request object.

        :param str url: The request URL.
        :param dict params: Request URL parameters.
        :param dict headers: Headers
        :param dict form_content: Form content
        """
        request = self._request(url, params, headers, content, form_content)
        request.method = 'GET'
        return request

    def put(self, url=None, params=None, headers=None, content=None, form_content=None):
        # type: (Optional[str], Optional[Dict[str, str]], Optional[Dict[str, str]], Any, Optional[Dict[str, Any]]) -> ClientRequest
        """Create a PUT request object.

        :param str url: The request URL.
        :param dict params: Request URL parameters.
        :param dict headers: Headers
        :param dict form_content: Form content
        """
        request = self._request(url, params, headers, content, form_content)
        request.method = 'PUT'
        return request

    def post(self, url=None, params=None, headers=None, content=None, form_content=None):
        # type: (Optional[str], Optional[Dict[str, str]], Optional[Dict[str, str]], Any, Optional[Dict[str, Any]]) -> ClientRequest
        """Create a POST request object.

        :param str url: The request URL.
        :param dict params: Request URL parameters.
        :param dict headers: Headers
        :param dict form_content: Form content
        """
        request = self._request(url, params, headers, content, form_content)
        request.method = 'POST'
        return request

    def head(self, url=None, params=None, headers=None, content=None, form_content=None):
        # type: (Optional[str], Optional[Dict[str, str]], Optional[Dict[str, str]], Any, Optional[Dict[str, Any]]) -> ClientRequest
        """Create a HEAD request object.

        :param str url: The request URL.
        :param dict params: Request URL parameters.
        :param dict headers: Headers
        :param dict form_content: Form content
        """
        request = self._request(url, params, headers, content, form_content)
        request.method = 'HEAD'
        return request

    def patch(self, url=None, params=None, headers=None, content=None, form_content=None):
        # type: (Optional[str], Optional[Dict[str, str]], Optional[Dict[str, str]], Any, Optional[Dict[str, Any]]) -> ClientRequest
        """Create a PATCH request object.

        :param str url: The request URL.
        :param dict params: Request URL parameters.
        :param dict headers: Headers
        :param dict form_content: Form content
        """
        request = self._request(url, params, headers, content, form_content)
        request.method = 'PATCH'
        return request

    def delete(self, url=None, params=None, headers=None, content=None, form_content=None):
        # type: (Optional[str], Optional[Dict[str, str]], Optional[Dict[str, str]], Any, Optional[Dict[str, Any]]) -> ClientRequest
        """Create a DELETE request object.

        :param str url: The request URL.
        :param dict params: Request URL parameters.
        :param dict headers: Headers
        :param dict form_content: Form content
        """
        request = self._request(url, params, headers, content, form_content)
        request.method = 'DELETE'
        return request

    def merge(self, url=None, params=None, headers=None, content=None, form_content=None):
        # type: (Optional[str], Optional[Dict[str, str]], Optional[Dict[str, str]], Any, Optional[Dict[str, Any]]) -> ClientRequest
        """Create a MERGE request object.

        :param str url: The request URL.
        :param dict params: Request URL parameters.
        :param dict headers: Headers
        :param dict form_content: Form content
        """
        request = self._request(url, params, headers, content, form_content)
        request.method = 'MERGE'
        return request
