# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from argparse import Namespace
from azure.cli.core.util import CLIError
from azure.cli.core.azclierror import InvalidArgumentValueError
from ..._gateway_constant import (GATEWAY_RESPONSE_CACHE_SCOPE_ROUTE, GATEWAY_RESPONSE_CACHE_SCOPE_INSTANCE,
                                  GATEWAY_RESPONSE_CACHE_SIZE_RESET_VALUE, GATEWAY_RESPONSE_CACHE_TTL_RESET_VALUE)
from ..._validators_enterprise import (_validate_gateway_response_cache, _validate_gateway_response_cache_exclusive,
                                       _validate_gateway_response_cache_scope, _validate_gateway_response_cache_size,
                                       _validate_gateway_response_cache_ttl)


class TestGatewayValidator(unittest.TestCase):
    def test_response_cache_scope(self):
        invalid_scope_list = [" ", "Route ", "  Route", " Route ", " Instance ", " xxx ", "-1"]
        valid_route_scope_list = ["Route", "route", "ROUTE"]
        valid_instance_scope_list = ["Instance", "instance", "INSTANCE"]
        for invalid_scope in invalid_scope_list:
            ns = Namespace(response_cache_scope=invalid_scope)
            self._test_invalid_response_cache_scope(ns)
        for valid_scope in valid_route_scope_list:
            ns = Namespace(response_cache_scope=valid_scope)
            self._test_valid_response_cache_scope(ns, GATEWAY_RESPONSE_CACHE_SCOPE_ROUTE)
        for valid_scope in valid_instance_scope_list:
            ns = Namespace(response_cache_scope=valid_scope)
            self._test_valid_response_cache_scope(ns, GATEWAY_RESPONSE_CACHE_SCOPE_INSTANCE)

    def _test_invalid_response_cache_scope(self, ns):
        with self.assertRaises(InvalidArgumentValueError) as context:
            _validate_gateway_response_cache_scope(ns)
        self.assertEqual("The allowed values for '--response-cache-scope' are [Route, Instance]",
                         str(context.exception))

    def _test_valid_response_cache_scope(self, ns, expectedScope):
        _validate_gateway_response_cache_scope(ns)
        self.assertEqual(expectedScope, ns.response_cache_scope)

    def test_response_cache_size(self):
        invalid_cache_size_list = ["-2", "0", ",", "00GB", "0MB", "-1MB", "09KB", "12345678901GB"]
        valid_cache_size_list = ["1234567890GB", "1000GB", "100GB", "10GB", "1GB",
                                 "1234567890MB", "1000MB", "100MB", "10MB", "1MB",
                                 "1234567890KB", "1000KB", "100KB", "10KB", "1KB"]
        for size in invalid_cache_size_list:
            ns = Namespace(response_cache_size=size)
            self._test_invalid_response_cache_size(ns)

        for size in valid_cache_size_list:
            ns = Namespace(response_cache_size=size)
            self._test_valid_response_cache_size(ns)

        ns = Namespace(response_cache_size="DEFAULT")
        _validate_gateway_response_cache_size(ns)
        self.assertTrue(ns.response_cache_size == GATEWAY_RESPONSE_CACHE_SIZE_RESET_VALUE)

        ns = Namespace(response_cache_size="default")
        _validate_gateway_response_cache_size(ns)
        self.assertTrue(ns.response_cache_size == GATEWAY_RESPONSE_CACHE_SIZE_RESET_VALUE)

        ns = Namespace(response_cache_size="Default")
        _validate_gateway_response_cache_size(ns)
        self.assertTrue(ns.response_cache_size == GATEWAY_RESPONSE_CACHE_SIZE_RESET_VALUE)

    def _test_invalid_response_cache_size(self, ns):
        with self.assertRaises(InvalidArgumentValueError) as context:
            _validate_gateway_response_cache_size(ns)
        self.assertEqual("Invalid response cache size '{}', the regex used to validate is '{}'".format(
            ns.response_cache_size, r"^[1-9][0-9]{0,9}(GB|MB|KB)$"
        ), str(context.exception))

    def _test_valid_response_cache_size(self, ns):
        _validate_gateway_response_cache_size(ns)

    def test_response_cache_ttl(self):
        invalid_cache_ttl_list = ["-2", "0", ",", "00h", "0m", "-1s", "09m", "12345678901s"]
        valid_cache_ttl_list = ["1234567890h", "1000h", "100h", "10h", "1h",
                                "1234567890m", "1000m", "100m", "10m", "1m",
                                "1234567890s", "1000s", "100s", "10s", "1s"]
        for size in invalid_cache_ttl_list:
            ns = Namespace(response_cache_ttl=size)
            self._test_invalid_response_cache_ttl(ns)

        for size in valid_cache_ttl_list:
            ns = Namespace(response_cache_ttl=size)
            self._test_valid_response_cache_ttl(ns)

        ns = Namespace(response_cache_ttl="DEFAULT")
        _validate_gateway_response_cache_ttl(ns)
        self.assertTrue(ns.response_cache_ttl == GATEWAY_RESPONSE_CACHE_TTL_RESET_VALUE)

        ns = Namespace(response_cache_ttl="default")
        _validate_gateway_response_cache_ttl(ns)
        self.assertTrue(ns.response_cache_ttl == GATEWAY_RESPONSE_CACHE_TTL_RESET_VALUE)

        ns = Namespace(response_cache_ttl="Default")
        _validate_gateway_response_cache_ttl(ns)
        self.assertTrue(ns.response_cache_ttl == GATEWAY_RESPONSE_CACHE_TTL_RESET_VALUE)

    def _test_invalid_response_cache_ttl(self, ns):
        with self.assertRaises(InvalidArgumentValueError) as context:
            _validate_gateway_response_cache_ttl(ns)
        self.assertEqual("Invalid response cache ttl '{}', the regex used to validate is '{}'".format(
            ns.response_cache_ttl, r"^[1-9][0-9]{0,9}(h|m|s)$"
        ), str(context.exception))

    def _test_valid_response_cache_ttl(self, ns):
        _validate_gateway_response_cache_ttl(ns)

    def test_validate_gateway_response_cache_exclusive(self):
        invalid_ns_list = [
            Namespace(enable_response_cache=False, response_cache_scope="Route", response_cache_size="10GB",
                      response_cache_ttl="10s"),
            Namespace(enable_response_cache=False, response_cache_scope="Route", response_cache_size="10GB",
                      response_cache_ttl=None),
            Namespace(enable_response_cache=False, response_cache_scope="Route", response_cache_size=None,
                      response_cache_ttl="10s"),
            Namespace(enable_response_cache=False, response_cache_scope=None, response_cache_size="10GB",
                      response_cache_ttl="10s"),
            Namespace(enable_response_cache=False, response_cache_scope=None, response_cache_size="10GB",
                      response_cache_ttl=None),
            Namespace(enable_response_cache=False, response_cache_scope=None, response_cache_size=None,
                      response_cache_ttl="10s"),
            Namespace(enable_response_cache=False, response_cache_scope="Route", response_cache_size=None,
                      response_cache_ttl=None)
        ]
        valid_ns_list = [
            Namespace(enable_response_cache=True, response_cache_scope="Route", response_cache_size="10GB",
                      response_cache_ttl="10s"),
            Namespace(enable_response_cache=None, response_cache_scope="Route", response_cache_size="10GB",
                      response_cache_ttl="10s"),
        ]

        for ns in invalid_ns_list:
            with self.assertRaises(InvalidArgumentValueError) as context:
                _validate_gateway_response_cache_exclusive(ns)
            self.assertEqual("Conflict detected: Parameters in ['--response-cache-scope', "
                             "'--response-cache-scope', '--response-cache-ttl'] "
                             "cannot be set together with '--enable-response-cache false'.", str(context.exception))
        for ns in valid_ns_list:
            _validate_gateway_response_cache_exclusive(ns)

    def test_validate_gateway_response_cache(self):
        valid_ns_list = [
            Namespace(response_cache_scope="Route", response_cache_size="10GB", response_cache_ttl="10s",
                      enable_response_cache=None),
            Namespace(response_cache_scope=None, response_cache_size=None, response_cache_ttl=None,
                      enable_response_cache=None),
            Namespace(response_cache_scope=None, response_cache_size="10GB", response_cache_ttl="10s",
                      enable_response_cache=None),
            Namespace(response_cache_scope="Route", response_cache_size=None, response_cache_ttl="10s",
                      enable_response_cache=None),
            Namespace(response_cache_scope="Route", response_cache_size="10GB", response_cache_ttl=None,
                      enable_response_cache=None),
            Namespace(response_cache_scope=None, response_cache_size=None, response_cache_ttl="10s",
                      enable_response_cache=None),
            Namespace(response_cache_scope=None, response_cache_size="10GB", response_cache_ttl=None,
                      enable_response_cache=None),
            Namespace(response_cache_scope="Route", response_cache_size=None, response_cache_ttl=None,
                      enable_response_cache=None),
            Namespace(response_cache_scope="Route", response_cache_size="10GB", response_cache_ttl="10s",
                      enable_response_cache=True),
            Namespace(response_cache_scope=None, response_cache_size=None, response_cache_ttl=None,
                      enable_response_cache=True),
            Namespace(response_cache_scope=None, response_cache_size="10GB", response_cache_ttl="10s",
                      enable_response_cache=True),
            Namespace(response_cache_scope="Route", response_cache_size=None, response_cache_ttl="10s",
                      enable_response_cache=True),
            Namespace(response_cache_scope="Route", response_cache_size="10GB", response_cache_ttl=None,
                      enable_response_cache=True),
            Namespace(response_cache_scope=None, response_cache_size=None, response_cache_ttl="10s",
                      enable_response_cache=True),
            Namespace(response_cache_scope=None, response_cache_size="10GB", response_cache_ttl=None,
                      enable_response_cache=True),
            Namespace(response_cache_scope="Route", response_cache_size=None, response_cache_ttl=None,
                      enable_response_cache=True),
        ]

        for ns in valid_ns_list:
            _validate_gateway_response_cache(ns)
