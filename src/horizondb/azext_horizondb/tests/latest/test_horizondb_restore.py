# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import datetime
import unittest

from azure.cli.core.azclierror import InvalidArgumentValueError

from azext_horizondb.commands.custom_commands import _parse_restore_time


class HorizonDBParseRestoreTimeTests(unittest.TestCase):

    def test_default_is_utc_aware_and_before_now(self):
        # When no restore time is supplied the value defaults to ~6 minutes before now
        # (the preview minimum buffer) and must be timezone-aware in UTC.
        result = _parse_restore_time(None)
        self.assertIsNotNone(result.tzinfo)
        self.assertEqual(result.utcoffset(), datetime.timedelta(0))
        delta = datetime.datetime.now(datetime.timezone.utc) - result
        self.assertGreaterEqual(delta, datetime.timedelta(minutes=5))
        self.assertLessEqual(delta, datetime.timedelta(minutes=7))

    def test_naive_value_is_interpreted_as_utc(self):
        # A value without an explicit offset is treated as UTC rather than passed through naive.
        result = _parse_restore_time("2026-07-15T02:10:00")
        self.assertEqual(result.utcoffset(), datetime.timedelta(0))
        self.assertEqual(
            result,
            datetime.datetime(2026, 7, 15, 2, 10, 0, tzinfo=datetime.timezone.utc))

    def test_offset_aware_value_is_converted_to_utc(self):
        # An offset-aware value is normalized to UTC so the service receives an unambiguous time.
        result = _parse_restore_time("2026-07-15T02:10:00+08:00")
        self.assertEqual(result.utcoffset(), datetime.timedelta(0))
        self.assertEqual(
            result,
            datetime.datetime(2026, 7, 14, 18, 10, 0, tzinfo=datetime.timezone.utc))

    def test_z_suffix_value_is_utc(self):
        result = _parse_restore_time("2026-07-15T02:10:00Z")
        self.assertEqual(result.utcoffset(), datetime.timedelta(0))
        self.assertEqual(
            result,
            datetime.datetime(2026, 7, 15, 2, 10, 0, tzinfo=datetime.timezone.utc))

    def test_invalid_value_raises(self):
        with self.assertRaises(InvalidArgumentValueError):
            _parse_restore_time("not-a-date")


if __name__ == '__main__':
    unittest.main()
