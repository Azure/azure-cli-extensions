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


try:
    import configparser
    from configparser import NoOptionError
except ImportError:
    import ConfigParser as configparser  # type: ignore
    from ConfigParser import NoOptionError  # type: ignore
import platform

from typing import Dict, List, Any, Callable

import requests

from .exceptions import raise_with_traceback
from .pipeline import (
    ClientRetryPolicy,
    ClientRedirectPolicy,
    ClientProxies,
    ClientConnection)
from .version import msrest_version


def default_session_configuration_callback(session, global_config, local_config, **kwargs):
    # type: (requests.Session, Configuration, Dict[str,str], str) -> Dict[str, str]
    """Configuration callback if you need to change default session configuration.

    :param requests.Session session: The session.
    :param Configuration global_config: The global configuration.
    :param dict[str,str] local_config: The on-the-fly configuration passed on the call.
    :param dict[str,str] kwargs: The current computed values for session.request method.
    :return: Must return kwargs, to be passed to session.request. If None is return, initial kwargs will be used.
    :rtype: dict[str,str]
    """
    return kwargs


class Configuration(object):
    """Client configuration.

    :param str baseurl: REST API base URL.
    :param str filepath: Path to existing config file (optional).
    """

    def __init__(self, base_url, filepath=None):
        # type: (str, str) -> None
        # Service
        self.base_url = base_url

        # Communication configuration
        self.connection = ClientConnection()

        # Headers (sent with every requests)
        self.headers = {}  # type: Dict[str, str]

        # ProxyConfiguration
        self.proxies = ClientProxies()

        # Retry configuration
        self.retry_policy = ClientRetryPolicy()

        # Redirect configuration
        self.redirect_policy = ClientRedirectPolicy()

        # User-Agent Header
        self._user_agent = "python/{} ({}) requests/{} msrest/{}".format(
            platform.python_version(),
            platform.platform(),
            requests.__version__,
            msrest_version)

        # Should we log HTTP requests/response?
        self.enable_http_logger = False

        # Requests hooks. Must respect requests hook callback signature
        # Note that we will inject the following parameters:
        # - kwargs['msrest']['session'] with the current session
        self.hooks = []  # type: List[Callable[[requests.Response, str, str], None]]

        self.session_configuration_callback = default_session_configuration_callback

        # If set to True, ServiceClient will own the sessionn
        self.keep_alive = False

        self._config = configparser.ConfigParser()
        self._config.optionxform = str

        if filepath:
            self.load(filepath)

    @property
    def user_agent(self):
        # type: () -> str
        """The current user agent value."""
        return self._user_agent

    def add_user_agent(self, value):
        # type: (str) -> None
        """Add value to current user agent with a space.

        :param str value: value to add to user agent.
        """
        self._user_agent = "{} {}".format(self._user_agent, value)

    def _clear_config(self):
        # type: () -> None
        """Clearout config object in memory."""
        for section in self._config.sections():
            self._config.remove_section(section)

    def save(self, filepath):
        # type: (str) -> None
        """Save current configuration to file.

        :param str filepath: Path to file where settings will be saved.
        :raises: ValueError if supplied filepath cannot be written to.
        """
        sections = [
            "Connection",
            "Proxies",
            "RetryPolicy",
            "RedirectPolicy"]
        for section in sections:
            self._config.add_section(section)

        self._config.set("Connection", "base_url", self.base_url)
        self._config.set("Connection", "timeout", self.connection.timeout)
        self._config.set("Connection", "verify", self.connection.verify)
        self._config.set("Connection", "cert", self.connection.cert)

        self._config.set("Proxies", "proxies", self.proxies.proxies)
        self._config.set("Proxies", "env_settings",
                         self.proxies.use_env_settings)

        self._config.set("RetryPolicy", "retries", self.retry_policy.retries)
        self._config.set("RetryPolicy", "backoff_factor",
                         self.retry_policy.backoff_factor)
        self._config.set("RetryPolicy", "max_backoff",
                         self.retry_policy.max_backoff)

        self._config.set("RedirectPolicy", "allow", self.redirect_policy.allow)
        self._config.set("RedirectPolicy", "max_redirects",
                         self.redirect_policy.max_redirects)
        try:
            with open(filepath, 'w') as configfile:
                self._config.write(configfile)
        except (KeyError, EnvironmentError):
            error = "Supplied config filepath invalid."
            raise_with_traceback(ValueError, error)
        finally:
            self._clear_config()

    def load(self, filepath):
        # type: (str) -> None
        """Load configuration from existing file.

        :param str filepath: Path to existing config file.
        :raises: ValueError if supplied config file is invalid.
        """
        try:
            self._config.read(filepath)

            self.base_url = \
                self._config.get("Connection", "base_url")
            self.connection.timeout = \
                self._config.getint("Connection", "timeout")
            self.connection.verify = \
                self._config.getboolean("Connection", "verify")
            self.connection.cert = \
                self._config.get("Connection", "cert")

            self.proxies.proxies = \
                eval(self._config.get("Proxies", "proxies"))
            self.proxies.use_env_settings = \
                self._config.getboolean("Proxies", "env_settings")

            self.retry_policy.retries = \
                self._config.getint("RetryPolicy", "retries")
            self.retry_policy.backoff_factor = \
                self._config.getfloat("RetryPolicy", "backoff_factor")
            self.retry_policy.max_backoff = \
                self._config.getint("RetryPolicy", "max_backoff")

            self.redirect_policy.allow = \
                self._config.getboolean("RedirectPolicy", "allow")
            self.redirect_policy.max_redirects = \
                self._config.set("RedirectPolicy", "max_redirects")

        except (ValueError, EnvironmentError, NoOptionError):
            error = "Supplied config file incompatible."
            raise_with_traceback(ValueError, error)
        finally:
            self._clear_config()
