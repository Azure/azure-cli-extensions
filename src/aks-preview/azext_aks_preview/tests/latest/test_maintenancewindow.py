# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest

import azext_aks_preview.maintenancewindow as mw
from azext_aks_preview.__init__ import register_aks_preview_resource_type
from azure.cli.command_modules.acs.tests.latest.mocks import MockCLI, MockCmd
from azure.cli.core.azclierror import (
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
    RequiredArgumentMissingError,
)


def _base_raw_parameters():
    """A baseline raw_parameters dict matching the kwargs aks_maintenancewindow_create
    forwards via `locals()`. Per-test cases override what they need.
    """
    return {
        "resource_group_name": "test_rg",
        "maintenance_window_name": "test_mw",
        "location": "westus2",
        "tags": None,
        "schedule_type": None,
        "interval_days": None,
        "interval_weeks": None,
        "interval_months": None,
        "day_of_week": None,
        "day_of_month": None,
        "week_index": None,
        "duration_hours": None,
        "utc_offset": None,
        "start_date": None,
        "start_time": None,
        "no_wait": False,
    }


class TestConstructMaintenanceWindowResource(unittest.TestCase):
    def setUp(self):
        # Make MaintenanceWindowResource + Schedule models resolvable via
        # cmd.get_models() — same setup the MTC tests use.
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)

    def test_missing_start_time(self):
        raw = _base_raw_parameters()
        raw.update({"schedule_type": "Daily", "interval_days": 2, "duration_hours": 4})
        with self.assertRaises(RequiredArgumentMissingError) as cm:
            mw.constructMaintenanceWindowResource(self.cmd, raw)
        self.assertIn("--start-time", str(cm.exception))

    def test_missing_duration(self):
        raw = _base_raw_parameters()
        raw.update({"schedule_type": "Daily", "interval_days": 2, "start_time": "01:00"})
        with self.assertRaises(RequiredArgumentMissingError) as cm:
            mw.constructMaintenanceWindowResource(self.cmd, raw)
        self.assertIn("--duration", str(cm.exception))

    def test_invalid_schedule_type(self):
        raw = _base_raw_parameters()
        raw.update({
            "schedule_type": "Hourly",  # not a real schedule type
            "start_time": "01:00",
            "duration_hours": 4,
        })
        with self.assertRaises(InvalidArgumentValueError):
            mw.constructMaintenanceWindowResource(self.cmd, raw)

    def test_daily_schedule_with_extra_args_is_rejected(self):
        # The reused constructDailySchedule rejects week-only / month-only args.
        raw = _base_raw_parameters()
        raw.update({
            "schedule_type": "Daily",
            "interval_days": 2,
            "day_of_week": "Monday",  # not allowed for Daily
            "start_time": "01:00",
            "duration_hours": 4,
        })
        with self.assertRaises(MutuallyExclusiveArgumentError):
            mw.constructMaintenanceWindowResource(self.cmd, raw)

    def test_weekly_happy_path(self):
        raw = _base_raw_parameters()
        raw.update({
            "schedule_type": "Weekly",
            "interval_weeks": 1,
            "day_of_week": "Saturday",
            "duration_hours": 8,
            "utc_offset": "-07:00",
            "start_time": "02:00",
            "tags": {"environment": "production"},
        })
        resource = mw.constructMaintenanceWindowResource(self.cmd, raw)
        self.assertEqual(resource.location, "westus2")
        self.assertEqual(resource.tags, {"environment": "production"})
        self.assertEqual(resource.properties.duration_hours, 8)
        self.assertEqual(resource.properties.start_time, "02:00")
        self.assertEqual(resource.properties.utc_offset, "-07:00")
        self.assertIsNotNone(resource.properties.schedule.weekly)
        self.assertEqual(resource.properties.schedule.weekly.interval_weeks, 1)
        self.assertEqual(resource.properties.schedule.weekly.day_of_week, "Saturday")

    def test_daily_happy_path(self):
        raw = _base_raw_parameters()
        raw.update({
            "schedule_type": "Daily",
            "interval_days": 2,
            "duration_hours": 6,
            "utc_offset": "-08:00",
            "start_time": "00:00",
        })
        resource = mw.constructMaintenanceWindowResource(self.cmd, raw)
        self.assertIsNotNone(resource.properties.schedule.daily)
        self.assertEqual(resource.properties.schedule.daily.interval_days, 2)

    def test_absolute_monthly_happy_path(self):
        raw = _base_raw_parameters()
        raw.update({
            "schedule_type": "AbsoluteMonthly",
            "interval_months": 1,
            "day_of_month": 15,
            "duration_hours": 6,
            "utc_offset": "+05:30",
            "start_time": "09:30",
        })
        resource = mw.constructMaintenanceWindowResource(self.cmd, raw)
        self.assertIsNotNone(resource.properties.schedule.absolute_monthly)
        self.assertEqual(resource.properties.schedule.absolute_monthly.interval_months, 1)
        self.assertEqual(resource.properties.schedule.absolute_monthly.day_of_month, 15)

    def test_relative_monthly_happy_path(self):
        raw = _base_raw_parameters()
        raw.update({
            "schedule_type": "RelativeMonthly",
            "interval_months": 1,
            "day_of_week": "Friday",
            "week_index": "Last",
            "duration_hours": 4,
            "utc_offset": "+00:00",
            "start_time": "01:00",
        })
        resource = mw.constructMaintenanceWindowResource(self.cmd, raw)
        self.assertIsNotNone(resource.properties.schedule.relative_monthly)
        self.assertEqual(resource.properties.schedule.relative_monthly.day_of_week, "Friday")
        self.assertEqual(resource.properties.schedule.relative_monthly.week_index, "Last")


class TestHasAnyScheduleArg(unittest.TestCase):
    def test_empty_returns_false(self):
        self.assertFalse(mw.hasAnyScheduleArg({}))

    def test_tags_only_returns_false(self):
        self.assertFalse(mw.hasAnyScheduleArg({"tags": {"env": "prod"}}))

    def test_any_schedule_field_returns_true(self):
        for key in (
            "schedule_type",
            "interval_days",
            "interval_weeks",
            "interval_months",
            "day_of_week",
            "day_of_month",
            "week_index",
            "duration_hours",
            "utc_offset",
            "start_date",
            "start_time",
        ):
            with self.subTest(key=key):
                self.assertTrue(mw.hasAnyScheduleArg({key: "anything"}))


if __name__ == "__main__":
    unittest.main()
