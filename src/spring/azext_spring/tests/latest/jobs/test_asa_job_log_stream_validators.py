# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

import unittest
from argparse import Namespace

from azext_spring.jobs.job_validators import validate_job_log_stream
from azext_spring.tests.latest.common.test_utils import get_test_cmd
from azure.cli.core.azclierror import InvalidArgumentValueError

try:
    import unittest.mock as mock
except ImportError:
    from unittest import mock


class TestValidateJobLogStream(unittest.TestCase):
    def test_mutual_exclusive_param(self):
        ns = Namespace(
            resource_group="group",
            service="service",
            all_instances=True,
            instance="fake-instance-name"
        )

        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_job_log_stream(get_test_cmd(), ns)

        self.assertEqual("--all-instances cannot be set together with --instance/-i.", str(context.exception))

    @mock.patch('azext_spring.jobs.job_validators.only_support_enterprise', autospec=True)
    def test_execution_name_not_set_and_instance_is_none(self, only_support_enterprise_mock):
        only_support_enterprise_mock.return_value = True

        ns = Namespace(
            resource_group="group",
            service="service",
            name="fake-job-name",
            execution=None,
            all_instances=None,
            instance=None,
            lines=50,
            limit=2048,
            since=None,
            max_log_requests=5
        )

        validate_job_log_stream(get_test_cmd(), ns)

    @mock.patch('azext_spring.jobs.job_validators.only_support_enterprise', autospec=True)
    def test_valid_log_lines(self, only_support_enterprise_mock):
        only_support_enterprise_mock.return_value = True

        valid_log_lines = [1, 2, 5, 10, 99, 100, 200, 10000]

        for lines in valid_log_lines:
            ns = Namespace(
                lines=lines,
                resource_group="group",
                service="service",
                name="fake-job-name",
                execution="fake-execution-name",
                all_instances=None,
                instance="fake-instance-name",
                limit=2048,
                since=None,
                max_log_requests=5
            )
            validate_job_log_stream(get_test_cmd(), ns)
            self.assertEqual(lines, ns.lines)

    def test_log_lines_too_small(self):
        ns = Namespace(
            lines=-1,
            resource_group="group",
            service="service",
            name="fake-job-name",
            execution="fake-execution-name",
            all_instances=None,
            instance="fake-instance-name",
            limit=2048,
            since=None,
            max_log_requests=5
        )
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_job_log_stream(get_test_cmd(), ns)
        self.assertEqual('--lines must be in the range [1,10000]', str(context.exception))

    @mock.patch('azext_spring.jobs.job_validators.only_support_enterprise', autospec=True)
    def test_log_lines_too_big(self, only_support_enterprise_mock):
        only_support_enterprise_mock.return_value = True

        ns = Namespace(
            lines=10001,
            resource_group="group",
            service="service",
            name="fake-job-name",
            execution="fake-execution-name",
            all_instances=None,
            instance="fake-instance-name",
            limit=2048,
            since=None,
            max_log_requests=5
        )
        with self.assertLogs('cli.azext_spring.log_stream.log_stream_validators', 'ERROR') as cm:
            validate_job_log_stream(get_test_cmd(), ns)
        expect_error_msgs = ['ERROR:cli.azext_spring.log_stream.log_stream_validators:'
                             '--lines can not be more than 10000, using 10000 instead']
        self.assertEqual(expect_error_msgs, cm.output)
        self.assertEqual(10000, ns.lines)

    @mock.patch('azext_spring.jobs.job_validators.only_support_enterprise', autospec=True)
    def test_valid_log_since(self, only_support_enterprise_mock):
        only_support_enterprise_mock.return_value = True

        valid_log_since = ['1h',
                           '1m', '2m', '5m', '10m', '11m', '20m', '30m', '40m', '50m', '59m', '60m',
                           '1s', '2s', '5s', '9s', '10s', '20s', '29s', '30s', '60s', '100s', '500s', '3000s', '3600s',
                           '1', '2', '5', '10', '20', '29', '30', '3000', '3600']

        for since in valid_log_since:
            ns = Namespace(
                since=since,
                resource_group="group",
                service="service",
                name="fake-job-name",
                execution="fake-execution-name",
                all_instances=None,
                instance="fake-instance-name",
                limit=2048,
                lines=50,
                max_log_requests=5
            )
            validate_job_log_stream(get_test_cmd(), ns)
            last = since[-1:]
            since_in_seconds = int(since[:-1]) if last in ("hms") else int(since)
            if last == 'h':
                since_in_seconds = since_in_seconds * 3600
            elif last == 'm':
                since_in_seconds = since_in_seconds * 60
            self.assertEqual(since_in_seconds, ns.since)

    def test_invalid_log_since(self):
        invalid_log_since = ['asdf1h', '1masdf', 'asdfe2m', 'asd5m', '1efef0m', '11mm']

        for since in invalid_log_since:
            ns = Namespace(
                since=since,
                resource_group="group",
                service="service",
                name="fake-job-name",
                execution="fake-execution-name",
                all_instances=None,
                instance="fake-instance-name",
                limit=2048,
                lines=50,
                max_log_requests=5
            )
            with self.assertRaises(InvalidArgumentValueError) as context:
                validate_job_log_stream(get_test_cmd(), ns)
            self.assertEqual("--since contains invalid characters", str(context.exception))

    def test_log_since_too_big(self):
        invalid_log_since = ['2h', '61m', '3601s', '9000s', '9000']

        for since in invalid_log_since:
            ns = Namespace(
                since=since,
                resource_group="group",
                service="service",
                name="fake-job-name",
                execution="fake-execution-name",
                all_instances=None,
                instance="fake-instance-name",
                limit=2048,
                lines=50,
                max_log_requests=5
            )
            with self.assertRaises(InvalidArgumentValueError) as context:
                validate_job_log_stream(get_test_cmd(), ns)
            self.assertEqual("--since can not be more than 1h", str(context.exception))

    @mock.patch('azext_spring.jobs.job_validators.only_support_enterprise', autospec=True)
    def test_valid_log_limit(self, only_support_enterprise_mock):
        only_support_enterprise_mock.return_value = True

        valid_log_limit = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]

        for limit in valid_log_limit:
            ns = Namespace(
                limit=limit,
                resource_group="group",
                service="service",
                name="fake-job-name",
                execution="fake-execution-name",
                all_instances=None,
                instance="fake-instance-name",
                since=None,
                lines=50,
                max_log_requests=5
            )
            validate_job_log_stream(get_test_cmd(), ns)
            self.assertEqual(limit * 1024, ns.limit)

    def test_negative_log_limit(self):
        invalid_log_limit = [-1, -2, -3, -4, -10, -100, -1000]

        for limit in invalid_log_limit:
            ns = Namespace(
                limit=limit,
                resource_group="group",
                service="service",
                name="fake-job-name",
                execution="fake-execution-name",
                all_instances=None,
                instance="fake-instance-name",
                since=None,
                lines=50,
                max_log_requests=5
            )
            with self.assertRaises(InvalidArgumentValueError) as context:
                validate_job_log_stream(get_test_cmd(), ns)
            self.assertEqual('--limit must be in the range [1,2048]', str(context.exception))

    @mock.patch('azext_spring.jobs.job_validators.only_support_enterprise', autospec=True)
    def test_log_limit_too_big(self, only_support_enterprise_mock):
        only_support_enterprise_mock.return_value = True

        invalid_log_limit = [2049, 2050, 3000, 3001, 10000, 20000, 100000]

        for limit in invalid_log_limit:
            ns = Namespace(
                limit=limit,
                resource_group="group",
                service="service",
                name="fake-job-name",
                execution="fake-execution-name",
                all_instances=None,
                instance="fake-instance-name",
                since=None,
                lines=50,
                max_log_requests=5
            )
            with self.assertLogs('cli.azext_spring.log_stream.log_stream_validators', 'ERROR') as cm:
                validate_job_log_stream(get_test_cmd(), ns)
            error_msgs = ['ERROR:cli.azext_spring.log_stream.log_stream_validators:'
                          '--limit can not be more than 2048, using 2048 instead']
            self.assertEqual(error_msgs, cm.output)
            self.assertEqual(2048 * 1024, ns.limit)
