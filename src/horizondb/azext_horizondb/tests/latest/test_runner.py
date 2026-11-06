# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import marshal
from unittest import TestCase

import pytest_forked
from _pytest.reports import TestReport as Report


class TestRunnerTests(TestCase):

    def test_forked_reports_round_trip_without_losing_results(self):
        for outcome, longrepr in [('passed', None), ('failed', 'Expected assertion failure')]:
            with self.subTest(outcome=outcome):
                report = Report(
                    nodeid='test_pool.py::PoolTests::test_pool_update_sends_only_node_count_in_patch',
                    location=('test_pool.py', 0, 'PoolTests.test_pool_update_sends_only_node_count_in_patch'),
                    keywords={},
                    outcome=outcome,
                    longrepr=longrepr,
                    when='call',
                )
                data = pytest_forked.serialize_report(report)
                restored = Report(**marshal.loads(marshal.dumps(data)))

                self.assertEqual(restored.nodeid, report.nodeid)
                self.assertEqual(restored.outcome, outcome)
                self.assertEqual(restored.longrepr, longrepr)
