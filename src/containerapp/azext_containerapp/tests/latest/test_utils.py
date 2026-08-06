# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from azure.cli.core.azclierror import ValidationError
from azext_containerapp._utils import validate_environment_mode_and_workload_profiles_compatible


class TestResolveEnvironmentModeAndWorkloadProfiles(unittest.TestCase):
    """Tests for the new resolve_environment_mode_and_workload_profiles function."""

    # Tests for environment_mode only (new preferred path)
    def test_workload_profiles_mode_does_not_raise(self):
        # Should not raise any exception
        validate_environment_mode_and_workload_profiles_compatible('WorkloadProfiles', None)

    def test_consumption_only_mode_does_not_raise(self):
        # Should not raise any exception
        validate_environment_mode_and_workload_profiles_compatible('ConsumptionOnly', None)

    # Tests for enable_workload_profiles only
    def test_workload_profiles_true_does_not_raise(self):
        # Should not raise any exception
        validate_environment_mode_and_workload_profiles_compatible(None, True)

    def test_workload_profiles_false_does_not_raise(self):
        # Should not raise any exception
        validate_environment_mode_and_workload_profiles_compatible(None, False)

    # Tests for neither specified (defaults)
    def test_neither_specified_does_not_raise(self):
        # Should not raise any exception
        validate_environment_mode_and_workload_profiles_compatible(None, None)

    # Tests for both specified (conflict detection)
    def test_consumption_only_with_workload_profiles_true_raises_error(self):
        with self.assertRaises(ValidationError):
            validate_environment_mode_and_workload_profiles_compatible('ConsumptionOnly', True)

    def test_workload_profiles_mode_with_deprecated_false_raises_error(self):
        with self.assertRaises(ValidationError):
            validate_environment_mode_and_workload_profiles_compatible('WorkloadProfiles', False)

    # Tests for compatible combinations (both specified, no conflict)
    def test_workload_profiles_mode_with_deprecated_true_does_not_raise(self):
        # Should not raise any exception
        validate_environment_mode_and_workload_profiles_compatible('WorkloadProfiles', True)

    def test_consumption_only_with_deprecated_false_does_not_raise(self):
        # Should not raise any exception
        validate_environment_mode_and_workload_profiles_compatible('ConsumptionOnly', False)

    # Additional edge case tests
    def test_workload_profiles_mode_case_insensitive(self):
        # Should not raise - test case insensitivity
        validate_environment_mode_and_workload_profiles_compatible('workloadprofiles', None)
        validate_environment_mode_and_workload_profiles_compatible('WORKLOADPROFILES', None)

    def test_consumption_only_mode_case_insensitive(self):
        # Should not raise - test case insensitivity
        validate_environment_mode_and_workload_profiles_compatible('consumptiononly', None)
        validate_environment_mode_and_workload_profiles_compatible('CONSUMPTIONONLY', None)

    def test_consumption_only_case_insensitive_with_workload_profiles_true_raises(self):
        with self.assertRaises(ValidationError):
            validate_environment_mode_and_workload_profiles_compatible('consumptiononly', True)

    def test_workload_profiles_case_insensitive_with_deprecated_false_raises(self):
        with self.assertRaises(ValidationError):
            validate_environment_mode_and_workload_profiles_compatible('workloadprofiles', False)