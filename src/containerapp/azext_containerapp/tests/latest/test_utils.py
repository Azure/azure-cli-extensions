# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from azure.cli.core.azclierror import ValidationError
from azext_containerapp._utils import resolve_environment_mode_and_workload_profiles
from azext_containerapp._sdk_enums import EnvironmentMode


class TestEnvironmentModeEnum(unittest.TestCase):
    """Tests for the EnvironmentMode enum."""

    def test_environment_mode_values(self):
        self.assertEqual(EnvironmentMode.WORKLOAD_PROFILES.value, "WorkloadProfiles")
        self.assertEqual(EnvironmentMode.STANDARD.value, "Standard")
        self.assertEqual(EnvironmentMode.FREE.value, "Free")
        self.assertEqual(EnvironmentMode.CONSUMPTION_ONLY.value, "ConsumptionOnly")

    def test_environment_mode_case_insensitive(self):
        # CaseInsensitiveEnumMeta allows case-insensitive comparison
        self.assertEqual(EnvironmentMode("workloadprofiles"), EnvironmentMode.WORKLOAD_PROFILES)
        self.assertEqual(EnvironmentMode("CONSUMPTIONONLY"), EnvironmentMode.CONSUMPTION_ONLY)
        self.assertEqual(EnvironmentMode("Standard"), EnvironmentMode.STANDARD)

    def test_environment_mode_string_representation(self):
        # Enum values should work as strings
        self.assertEqual(str(EnvironmentMode.WORKLOAD_PROFILES), "WorkloadProfiles")
        self.assertEqual(str(EnvironmentMode.CONSUMPTION_ONLY), "ConsumptionOnly")


class TestResolveEnvironmentModeAndWorkloadProfiles(unittest.TestCase):
    """Tests for the new resolve_environment_mode_and_workload_profiles function."""

    # Tests for environment_mode only (new preferred path)
    def test_workload_profiles_mode_returns_true(self):
        effective, show_warning = resolve_environment_mode_and_workload_profiles('WorkloadProfiles', None)
        self.assertTrue(effective)
        self.assertFalse(show_warning)

    def test_standard_mode_returns_true(self):
        effective, show_warning = resolve_environment_mode_and_workload_profiles('Standard', None)
        self.assertTrue(effective)
        self.assertFalse(show_warning)

    def test_free_mode_returns_true(self):
        effective, show_warning = resolve_environment_mode_and_workload_profiles('Free', None)
        self.assertTrue(effective)
        self.assertFalse(show_warning)

    def test_consumption_only_mode_returns_false(self):
        effective, show_warning = resolve_environment_mode_and_workload_profiles('ConsumptionOnly', None)
        self.assertFalse(effective)
        self.assertFalse(show_warning)

    # Tests for enable_workload_profiles only (deprecated path)
    def test_deprecated_workload_profiles_true_shows_warning(self):
        effective, show_warning = resolve_environment_mode_and_workload_profiles(None, True)
        self.assertTrue(effective)
        self.assertTrue(show_warning)

    def test_deprecated_workload_profiles_false_shows_warning(self):
        effective, show_warning = resolve_environment_mode_and_workload_profiles(None, False)
        self.assertFalse(effective)
        self.assertTrue(show_warning)

    # Tests for neither specified (defaults)
    def test_neither_specified_defaults_to_workload_profiles_enabled(self):
        effective, show_warning = resolve_environment_mode_and_workload_profiles(None, None)
        self.assertTrue(effective)
        self.assertFalse(show_warning)

    # Tests for both specified (conflict detection)
    def test_consumption_only_with_workload_profiles_true_raises_error(self):
        with self.assertRaises(ValidationError) as context:
            resolve_environment_mode_and_workload_profiles('ConsumptionOnly', True)
        self.assertIn("Cannot use '--enable-workload-profiles' with '--environment-mode ConsumptionOnly'", str(context.exception))

    def test_workload_profiles_mode_with_deprecated_false_raises_error(self):
        with self.assertRaises(ValidationError) as context:
            resolve_environment_mode_and_workload_profiles('WorkloadProfiles', False)
        self.assertIn("Cannot use '--enable-workload-profiles false' with '--environment-mode WorkloadProfiles'", str(context.exception))

    def test_standard_mode_with_deprecated_false_raises_error(self):
        with self.assertRaises(ValidationError) as context:
            resolve_environment_mode_and_workload_profiles('Standard', False)
        self.assertIn("Cannot use '--enable-workload-profiles false' with '--environment-mode Standard'", str(context.exception))

    def test_free_mode_with_deprecated_false_raises_error(self):
        with self.assertRaises(ValidationError) as context:
            resolve_environment_mode_and_workload_profiles('Free', False)
        self.assertIn("Cannot use '--enable-workload-profiles false' with '--environment-mode Free'", str(context.exception))

    # Tests for compatible combinations (both specified, no conflict)
    def test_workload_profiles_mode_with_deprecated_true_shows_warning(self):
        effective, show_warning = resolve_environment_mode_and_workload_profiles('WorkloadProfiles', True)
        self.assertTrue(effective)
        self.assertTrue(show_warning)

    def test_consumption_only_with_deprecated_false_shows_warning(self):
        effective, show_warning = resolve_environment_mode_and_workload_profiles('ConsumptionOnly', False)
        self.assertFalse(effective)
        self.assertTrue(show_warning)

    def test_standard_mode_with_deprecated_true_shows_warning(self):
        effective, show_warning = resolve_environment_mode_and_workload_profiles('Standard', True)
        self.assertTrue(effective)
        self.assertTrue(show_warning)