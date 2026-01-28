# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from azure.cli.core.azclierror import ValidationError
from azext_containerapp._utils import resolve_environment_mode_and_workload_profiles


class TestResolveEnvironmentModeAndWorkloadProfiles(unittest.TestCase):
    """Tests for the new resolve_environment_mode_and_workload_profiles function."""

    # Tests for environment_mode only (new preferred path)
    def test_workload_profiles_mode_returns_true(self):
        effective = resolve_environment_mode_and_workload_profiles('WorkloadProfiles', None)
        self.assertTrue(effective)

    def test_consumption_only_mode_returns_false(self):
        effective = resolve_environment_mode_and_workload_profiles('ConsumptionOnly', None)
        self.assertFalse(effective)

    # Tests for enable_workload_profiles only
    def test_workload_profiles_true_shows_warning(self):
        effective = resolve_environment_mode_and_workload_profiles(None, True)
        self.assertTrue(effective)

    def test_workload_profiles_false_shows_warning(self):
        effective = resolve_environment_mode_and_workload_profiles(None, False)
        self.assertFalse(effective)

    # Tests for neither specified (defaults)
    def test_neither_specified_defaults_to_workload_profiles_enabled(self):
        effective = resolve_environment_mode_and_workload_profiles(None, None)
        self.assertTrue(effective)

    # Tests for both specified (conflict detection)
    def test_consumption_only_with_workload_profiles_true_raises_error(self):
        with self.assertRaises(ValidationError) as context:
            resolve_environment_mode_and_workload_profiles('ConsumptionOnly', True)
        self.assertIn("Cannot use '--enable-workload-profiles' with '--environment-mode ConsumptionOnly'", str(context.exception))

    def test_workload_profiles_mode_with_deprecated_false_raises_error(self):
        with self.assertRaises(ValidationError) as context:
            resolve_environment_mode_and_workload_profiles('WorkloadProfiles', False)
        self.assertIn("Cannot use '--enable-workload-profiles false' with '--environment-mode WorkloadProfiles'", str(context.exception))

    # Tests for compatible combinations (both specified, no conflict)
    def test_workload_profiles_mode_with_deprecated_true_shows_warning(self):
        effective = resolve_environment_mode_and_workload_profiles('WorkloadProfiles', True)
        self.assertTrue(effective)

    def test_consumption_only_with_deprecated_false_shows_warning(self):
        effective = resolve_environment_mode_and_workload_profiles('ConsumptionOnly', False)
        self.assertFalse(effective)