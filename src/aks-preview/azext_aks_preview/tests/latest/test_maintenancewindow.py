# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import argparse
import unittest
from unittest.mock import MagicMock, patch

import azext_aks_preview.custom as custom
import azext_aks_preview.maintenancewindow as mw
from azext_aks_preview._validators import validate_duration_hours
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


class TestValidateDurationHours(unittest.TestCase):
    """Pins the --duration argparse-time validator (Ye's iter-2 ask).

    The RP enforces 4-24 hours; the local validator surfaces the same
    constraint as a clear argparse error instead of an opaque server 400.
    """

    def _ns(self, value):
        # Mimic the argparse Namespace shape the validator inspects.
        return argparse.Namespace(duration_hours=value)

    def test_none_is_ok(self):
        # --duration omitted should not fire the validator.
        validate_duration_hours(self._ns(None))  # no-op, no raise

    def test_lower_bound_inclusive(self):
        validate_duration_hours(self._ns(4))

    def test_upper_bound_inclusive(self):
        validate_duration_hours(self._ns(24))

    def test_typical_value(self):
        validate_duration_hours(self._ns(8))

    def test_below_lower_bound_raises(self):
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validate_duration_hours(self._ns(3))
        self.assertIn("4 and 24", str(cm.exception))

    def test_above_upper_bound_raises(self):
        with self.assertRaises(InvalidArgumentValueError) as cm:
            validate_duration_hours(self._ns(25))
        self.assertIn("4 and 24", str(cm.exception))

    def test_negative_raises(self):
        with self.assertRaises(InvalidArgumentValueError):
            validate_duration_hours(self._ns(-1))

    def test_zero_raises(self):
        with self.assertRaises(InvalidArgumentValueError):
            validate_duration_hours(self._ns(0))


class TestAksMaintenancewindowUpdateRMW(unittest.TestCase):
    """Pins the read-modify-write semantics of `aks maintenancewindow update`.

    The update handler must:
      - fetch the existing MW via client.get()
      - leave fields the caller did not supply untouched
      - replace tags only when --tags is supplied (acs convention; no merge)
      - rebuild the schedule end-to-end when any schedule arg is supplied
      - warn (not error) when --location differs from existing.location, and
        keep the existing location (TrackedResource immutability)
    """

    def setUp(self):
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        # Build a realistic "existing" MW returned by client.get(): tagged,
        # weekly schedule, non-empty not_allowed_dates, in westus2.
        self.client = MagicMock()
        self.existing = self._build_existing_mw()
        self.client.get.return_value = self.existing
        # begin_create_or_update returns a poller-like that yields the body
        # back when .result() is called; tests usually only need to inspect
        # what was passed in, so a MagicMock is fine.
        self.client.begin_create_or_update.return_value = MagicMock()

    def _build_existing_mw(self):
        MaintenanceWindowResource = self.cmd.get_models(
            "MaintenanceWindowResource",
            resource_type=custom.CUSTOM_MGMT_AKS_PREVIEW,
            operation_group="maintenance_windows",
        )
        Properties = self.cmd.get_models(
            "MaintenanceWindowResourceProperties",
            resource_type=custom.CUSTOM_MGMT_AKS_PREVIEW,
            operation_group="maintenance_windows",
        )
        Schedule = self.cmd.get_models(
            "Schedule",
            resource_type=custom.CUSTOM_MGMT_AKS_PREVIEW,
            operation_group="maintenance_windows",
        )
        WeeklySchedule = self.cmd.get_models(
            "WeeklySchedule",
            resource_type=custom.CUSTOM_MGMT_AKS_PREVIEW,
            operation_group="maintenance_windows",
        )
        DateSpan = self.cmd.get_models(
            "DateSpan",
            resource_type=custom.CUSTOM_MGMT_AKS_PREVIEW,
            operation_group="maintenance_windows",
        )
        import datetime
        return MaintenanceWindowResource(
            location="westus2",
            tags={"env": "prod", "team": "aks"},
            properties=Properties(
                schedule=Schedule(weekly=WeeklySchedule(interval_weeks=1, day_of_week="Saturday")),
                start_time="02:00",
                duration_hours=8,
                utc_offset="-07:00",
                not_allowed_dates=[
                    DateSpan(start=datetime.date(2026, 12, 23), end=datetime.date(2027, 1, 5)),
                ],
            ),
        )

    def _call_update(self, **kwargs):
        # Helper that invokes the update handler with our fake client and
        # only the kwargs the caller wants to override; everything else
        # stays None (= "not supplied").
        defaults = {
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
            "tags": None,
            "location": None,
            "no_wait": False,
        }
        defaults.update(kwargs)
        return custom.aks_maintenancewindow_update(
            self.cmd,
            self.client,
            resource_group_name="rg-maintenance",
            maintenance_window_name="prod-weekends",
            **defaults,
        )

    def _put_body(self):
        # The body passed to client.begin_create_or_update.
        # Signature is (rg, name, body, ...) — body is positional arg 2.
        return self.client.begin_create_or_update.call_args.args[2]

    def test_tags_only_update_preserves_schedule_and_dates(self):
        self._call_update(tags={"env": "staging"})
        body = self._put_body()
        # Tags replaced (no merge — caller wins, acs `aks update` convention).
        self.assertEqual(body.tags, {"env": "staging"})
        # Schedule untouched.
        self.assertIsNotNone(body.properties.schedule.weekly)
        self.assertEqual(body.properties.schedule.weekly.day_of_week, "Saturday")
        # not_allowed_dates preserved — this is the A4 silent-erasure fix.
        self.assertEqual(len(body.properties.not_allowed_dates), 1)
        # Scalars preserved.
        self.assertEqual(body.properties.duration_hours, 8)
        self.assertEqual(body.properties.start_time, "02:00")

    def test_duration_only_update_preserves_tags_and_schedule(self):
        self._call_update(duration_hours=6)
        body = self._put_body()
        self.assertEqual(body.properties.duration_hours, 6)
        # Tags + schedule + not_allowed_dates untouched.
        self.assertEqual(body.tags, {"env": "prod", "team": "aks"})
        self.assertIsNotNone(body.properties.schedule.weekly)
        self.assertEqual(len(body.properties.not_allowed_dates), 1)

    def test_schedule_change_rebuilds_schedule_preserves_other_fields(self):
        # Change from Weekly Saturday to Weekly Sunday. interval_weeks must
        # also be supplied — constructWeeklySchedule requires it.
        self._call_update(schedule_type="Weekly", day_of_week="Sunday", interval_weeks=1)
        body = self._put_body()
        # Schedule shape changed.
        self.assertEqual(body.properties.schedule.weekly.day_of_week, "Sunday")
        # Tags + scalars + not_allowed_dates preserved.
        self.assertEqual(body.tags, {"env": "prod", "team": "aks"})
        self.assertEqual(body.properties.duration_hours, 8)
        self.assertEqual(body.properties.start_time, "02:00")
        self.assertEqual(len(body.properties.not_allowed_dates), 1)

    def test_omitted_tags_keeps_existing_tags(self):
        # The A4-adjacent guard: omitting --tags should preserve the existing
        # tag dict, NOT silently clear it.
        self._call_update(duration_hours=10)
        body = self._put_body()
        self.assertEqual(body.tags, {"env": "prod", "team": "aks"})

    def test_location_mismatch_is_warned_not_erroring(self):
        # The A3 fix: TrackedResource location is immutable post-create.
        # Supplying a different --location should warn and keep the existing
        # location rather than letting ARM reject the PUT with an opaque 400.
        with patch.object(custom.logger, "warning") as warn_mock:
            self._call_update(location="eastus", duration_hours=6)
        warn_mock.assert_called_once()
        body = self._put_body()
        self.assertEqual(body.location, "westus2")

    def test_no_args_is_a_noop_put_of_existing(self):
        # Calling update with nothing supplied should PUT the existing
        # resource back unchanged. This is the trivial RMW degenerate case.
        self._call_update()
        body = self._put_body()
        self.assertEqual(body.tags, {"env": "prod", "team": "aks"})
        self.assertEqual(body.location, "westus2")
        self.assertEqual(body.properties.duration_hours, 8)

    def test_get_is_called_before_put(self):
        self._call_update(tags={"env": "x"})
        self.client.get.assert_called_once_with("rg-maintenance", "prod-weekends")
        self.client.begin_create_or_update.assert_called_once()

    def test_config_file_replaces_properties_keeps_tags_location(self):
        # --config-file's `properties` block replaces existing.properties
        # wholesale (MTC's --config-file convention). Tags + location stay
        # from the existing resource unless overridden by --tags or by
        # `tags` in the JSON.
        new_props = {
            "schedule": {"daily": {"intervalDays": 3}},
            "startTime": "05:00",
            "durationHours": 6,
            "utcOffset": "+00:00",
            "notAllowedDates": [{"start": "2026-12-23", "end": "2027-01-05"}],
        }
        with patch("azext_aks_preview.custom.get_file_json", return_value={"properties": new_props}):
            self._call_update(config_file="/tmp/fake.json")
        body = self._put_body()
        # body is a dict here (we ship the dict directly through the SDK).
        self.assertEqual(body["properties"], new_props)
        self.assertEqual(body["tags"], {"env": "prod", "team": "aks"})
        self.assertEqual(body["location"], "westus2")

    def test_config_file_with_tags_arg_overrides(self):
        new_props = {"schedule": {"daily": {"intervalDays": 2}}, "startTime": "01:00", "durationHours": 4}
        with patch("azext_aks_preview.custom.get_file_json", return_value={"properties": new_props}):
            self._call_update(config_file="/tmp/fake.json", tags={"env": "staging"})
        body = self._put_body()
        self.assertEqual(body["tags"], {"env": "staging"})

    def test_config_file_must_be_dict(self):
        with patch("azext_aks_preview.custom.get_file_json", return_value=["not", "a", "dict"]):
            with self.assertRaises(Exception) as cm:
                self._call_update(config_file="/tmp/fake.json")
            self.assertIn("must contain a JSON object", str(cm.exception))


class TestAksMaintenancewindowCreateConfigFile(unittest.TestCase):
    """Pins the --config-file path on create: JSON body wholly defines the
    resource (mirrors `aks maintenanceconfiguration add --config-file`).
    --location and --tags from the CLI args fill in if not already in JSON.
    """

    def setUp(self):
        register_aks_preview_resource_type()
        self.cli_ctx = MockCLI()
        self.cmd = MockCmd(self.cli_ctx)
        self.client = MagicMock()
        self.client.begin_create_or_update.return_value = MagicMock()

    def _put_body(self):
        return self.client.begin_create_or_update.call_args.args[2]

    def test_config_file_uses_json_directly(self):
        body = {
            "location": "eastus",
            "properties": {
                "schedule": {"weekly": {"intervalWeeks": 1, "dayOfWeek": "Saturday"}},
                "startTime": "02:00",
                "durationHours": 8,
                "utcOffset": "-07:00",
            },
        }
        with patch("azext_aks_preview.custom.get_file_json", return_value=body):
            with patch("azext_aks_preview.custom.get_rg_location", return_value="westus2"):
                custom.aks_maintenancewindow_create(
                    self.cmd, self.client,
                    resource_group_name="rg-mw",
                    maintenance_window_name="prod-weekends",
                    location=None, schedule_type=None, interval_days=None,
                    interval_weeks=None, interval_months=None, day_of_week=None,
                    day_of_month=None, week_index=None, duration_hours=None,
                    utc_offset=None, start_date=None, start_time=None,
                    tags=None, config_file="/tmp/fake.json", no_wait=False,
                )
        put_body = self._put_body()
        # location from JSON wins over the RG-location fallback when present.
        self.assertEqual(put_body["location"], "eastus")
        self.assertEqual(put_body["properties"]["schedule"]["weekly"]["dayOfWeek"], "Saturday")

    def test_config_file_without_location_uses_rg_fallback(self):
        body_no_location = {
            "properties": {
                "schedule": {"daily": {"intervalDays": 1}},
                "startTime": "00:00",
                "durationHours": 4,
                "utcOffset": "+00:00",
            },
        }
        with patch("azext_aks_preview.custom.get_file_json", return_value=body_no_location):
            with patch("azext_aks_preview.custom.get_rg_location", return_value="northeurope"):
                custom.aks_maintenancewindow_create(
                    self.cmd, self.client,
                    resource_group_name="rg-mw",
                    maintenance_window_name="nightly",
                    location=None, schedule_type=None, interval_days=None,
                    interval_weeks=None, interval_months=None, day_of_week=None,
                    day_of_month=None, week_index=None, duration_hours=None,
                    utc_offset=None, start_date=None, start_time=None,
                    tags=None, config_file="/tmp/fake.json", no_wait=False,
                )
        self.assertEqual(self._put_body()["location"], "northeurope")


if __name__ == "__main__":
    unittest.main()
