# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

import unittest
from argparse import Namespace

from azext_spring.log_stream.log_stream_validators import (validate_log_limit, validate_log_lines, validate_log_since,
                                                           validate_max_log_requests, validate_thread_number)
from azure.cli.core.azclierror import InvalidArgumentValueError
from knack.util import CLIError

try:
    import unittest.mock as mock
except ImportError:
    from unittest import mock


class TestLogStreamValidator(unittest.TestCase):
    def test_valid_log_lines(self):
        valid_log_lines = [1, 2, 5, 10, 99, 100, 200, 10000]

        for lines in valid_log_lines:
            ns = Namespace(
                lines=lines,
            )
            validate_log_lines(ns)
            self.assertEquals(lines, ns.lines)

    def test_log_lines_too_small(self):
        ns = Namespace(
            lines=-1,
        )
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_log_lines(ns)
        self.assertEquals('--lines must be in the range [1,10000]', str(context.exception))

    def test_log_lines_too_big(self):
        ns = Namespace(
            lines=10001,
        )
        with self.assertLogs('cli.azext_spring.log_stream.log_stream_validators', 'ERROR') as cm:
            validate_log_lines(ns)
        expect_error_msgs = ['ERROR:cli.azext_spring.log_stream.log_stream_validators:'
                             '--lines can not be more than 10000, using 10000 instead']
        self.assertEquals(expect_error_msgs, cm.output)
        self.assertEquals(10000, ns.lines)

    def test_valid_log_since(self):
        valid_log_since = ['1h',
                           '1m', '2m', '5m', '10m', '11m', '20m', '30m', '40m', '50m', '59m', '60m',
                           '1s', '2s', '5s', '9s', '10s', '20s', '29s', '30s', '60s', '100s', '500s', '3000s', '3600s',
                           '1', '2', '5', '10', '20', '29', '30', '3000', '3600']

        for since in valid_log_since:
            ns = Namespace(
                since=since
            )
            validate_log_since(ns)
            last = since[-1:]
            since_in_seconds = int(since[:-1]) if last in ("hms") else int(since)
            if last == 'h':
                since_in_seconds = since_in_seconds * 3600
            elif last == 'm':
                since_in_seconds = since_in_seconds * 60
            self.assertEquals(since_in_seconds, ns.since)

    def test_invalid_log_since(self):
        invalid_log_since = ['asdf1h', '1masdf', 'asdfe2m', 'asd5m', '1efef0m', '11mm']

        for since in invalid_log_since:
            ns = Namespace(
                since=since
            )
            with self.assertRaises(InvalidArgumentValueError) as context:
                validate_log_since(ns)
            self.assertEquals("--since contains invalid characters", str(context.exception))

    def test_log_since_too_big(self):
        invalid_log_since = ['2h', '61m', '3601s', '9000s', '9000']

        for since in invalid_log_since:
            ns = Namespace(
                since=since
            )
            with self.assertRaises(InvalidArgumentValueError) as context:
                validate_log_since(ns)
            self.assertEquals("--since can not be more than 1h", str(context.exception))

    def test_valid_log_limit(self):
        valid_log_limit = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]

        for limit in valid_log_limit:
            ns = Namespace(
                limit=limit
            )
            validate_log_limit(ns)
            self.assertEquals(limit * 1024, ns.limit)

    def test_negative_log_limit(self):
        invalid_log_limit = [-1, -2, -3, -4, -10, -100, -1000]

        for limit in invalid_log_limit:
            ns = Namespace(
                limit=limit
            )
            with self.assertRaises(InvalidArgumentValueError) as context:
                validate_log_limit(ns)
            self.assertEquals('--limit must be in the range [1,2048]', str(context.exception))

    def test_log_limit_too_big(self):
        invalid_log_limit = [2049, 2050, 3000, 3001, 10000, 20000, 100000]

        for limit in invalid_log_limit:
            ns = Namespace(
                limit=limit
            )
            with self.assertLogs('cli.azext_spring.log_stream.log_stream_validators', 'ERROR') as cm:
                validate_log_limit(ns)
            error_msgs = ['ERROR:cli.azext_spring.log_stream.log_stream_validators:'
                          '--limit can not be more than 2048, using 2048 instead']
            self.assertEquals(error_msgs, cm.output)
            self.assertEquals(2048 * 1024, ns.limit)

    def test_invalid_max_log_requests(self):
        invalid_max_log_requests_number = [-100, -10, -1, 0]

        for num in invalid_max_log_requests_number:
            ns = Namespace(
                max_log_requests=num
            )

            with self.assertRaises(InvalidArgumentValueError) as context:
                validate_max_log_requests(ns)

            self.assertEquals("--max-log-requests should be larger than 0.", str(context.exception))

    def test_validate_thread_number(self):
        thread_num = 10
        for max_allowed_thread_number in range(0, thread_num):
            with self.assertRaises(CLIError) as context:
                validate_thread_number(True, thread_num, max_allowed_thread_number)

    def test_valid_thread_number(self):
        thread_num = 2
        for max_allowed_thread_number in range(thread_num, thread_num + 100):
            validate_thread_number(True, thread_num, max_allowed_thread_number)

        thread_num = 10
        for max_allowed_thread_number in range(0, thread_num):
            validate_thread_number(False, thread_num, max_allowed_thread_number)
