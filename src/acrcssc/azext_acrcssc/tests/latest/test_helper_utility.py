import unittest
from unittest.mock import MagicMock, patch
from azext_acrcssc.helper._utility import convert_cron_to_schedule, convert_timespan_to_cron
from azure.cli.core.azclierror import InvalidArgumentValueError


class TestCSSCUtilities(unittest.TestCase):
    def test_convert_timespan_to_cron_valid(self):
        test_cases = [
            ('1d', '0 0 */1 * *'),
            ('5d', '0 0 */5 * *'),
            ('10d', '0 0 */10 * *')
        ]

        for timespan, result in test_cases:
            result = convert_timespan_to_cron(timespan)
            self.assertEqual(result, result)

    def test_convert_timespan_to_cron_invalid(self):
        test_cases = [('12'), ('0d'), ('99d'), ('dd'), ('d')]

        for timespan in test_cases:
            self.assertRaises(InvalidArgumentValueError, convert_timespan_to_cron, timespan)

    def test_convert_cron_to_schedule_valid(self):
        test_cases = [
            ('0 0 */1 * *', '1d'),
            ('0 0 */5 * *', '5d'),
            ('0 0 */10 * *', '10d')
        ]

        for cron, result in test_cases:
            self.assertEqual(convert_cron_to_schedule(cron), result)

    def test_convert_cron_to_schedule_invalid(self):
        test_cases = [('*'), (''), ('* * * * *'), ('dd'), ('d')]

        for cron in test_cases:
            self.assertEqual(convert_cron_to_schedule(cron), None)

