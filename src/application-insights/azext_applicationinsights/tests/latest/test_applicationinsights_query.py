# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import datetime
import unittest
from unittest.mock import MagicMock, patch

from azure.cli.core.azclierror import InvalidArgumentValueError

from azext_applicationinsights.custom import execute_query


class ApplicationInsightsQueryTests(unittest.TestCase):

    def setUp(self):
        self.cmd = MagicMock()
        self.cmd.cli_ctx = MagicMock()

    @patch('azext_applicationinsights.aaz.latest.monitor.app_insights.QueryExecute')
    @patch('azext_applicationinsights.custom.get_query_targets', return_value=['app-id'])
    def test_query_without_time_arguments_omits_timespan(self, get_query_targets, query_execute):
        execute_query(self.cmd, ['app-id'], 'requests | count')

        get_query_targets.assert_called_once_with(self.cmd.cli_ctx, ['app-id'], None)
        query_execute.return_value.assert_called_once_with(command_args={
            'app_id': 'app-id',
            'query': 'requests | count',
            'applications': [],
        })

    @patch('azext_applicationinsights.custom.get_timespan', return_value='start/end')
    @patch('azext_applicationinsights.aaz.latest.monitor.app_insights.QueryExecute')
    @patch('azext_applicationinsights.custom.get_query_targets', return_value=['app-id'])
    def test_query_with_explicit_offset_includes_timespan(
            self, _, query_execute, get_timespan):
        offset = datetime.timedelta(days=7)

        execute_query(self.cmd, ['app-id'], 'requests | count', offset=offset)

        get_timespan.assert_called_once_with(self.cmd.cli_ctx, None, None, offset)
        query_execute.return_value.assert_called_once_with(command_args={
            'app_id': 'app-id',
            'query': 'requests | count',
            'applications': [],
            'timespan': 'start/end',
        })

    @patch('azext_applicationinsights.custom.get_timespan', return_value='start/end')
    @patch('azext_applicationinsights.aaz.latest.monitor.app_insights.QueryExecute')
    @patch('azext_applicationinsights.custom.get_query_targets', return_value=['app-id'])
    def test_query_with_start_and_end_time_includes_timespan(
            self, _, query_execute, get_timespan):
        start_time = datetime.datetime(2026, 9, 1)
        end_time = datetime.datetime(2026, 9, 8)

        execute_query(
            self.cmd,
            ['app-id'],
            'requests | count',
            start_time=start_time,
            end_time=end_time,
        )

        get_timespan.assert_called_once_with(
            self.cmd.cli_ctx, start_time, end_time, None)
        query_execute.return_value.assert_called_once_with(command_args={
            'app_id': 'app-id',
            'query': 'requests | count',
            'applications': [],
            'timespan': 'start/end',
        })

    def test_query_with_one_time_boundary_requires_offset(self):
        for time_argument in ('start_time', 'end_time'):
            with self.subTest(time_argument=time_argument):
                with self.assertRaisesRegex(
                        InvalidArgumentValueError,
                        '--offset is required'):
                    execute_query(
                        self.cmd,
                        ['app-id'],
                        'requests | count',
                        **{time_argument: datetime.datetime(2026, 9, 1)},
                    )


if __name__ == '__main__':
    unittest.main()
