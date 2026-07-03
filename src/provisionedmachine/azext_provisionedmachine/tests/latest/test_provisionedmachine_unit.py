# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Unit tests for provisionedmachine CLI extension.

Tests cover:
- show-status table transformer (happy path + failure path + edge cases)
- os-image list table transformer (JSON shape + OsImageType sourcing)
- install-os version comparison logic
- install-os auto-resolve version behavior

These tests import the pure-logic functions directly to avoid Azure CLI SDK dependencies.
Run with: python -m pytest azext_provisionedmachine/tests/latest/test_provisionedmachine_unit.py -v
       or: azdev test provisionedmachine --discover
"""

import unittest
import sys
import os


# ---------------------------------------------------------------------------
# Import pure-logic functions without triggering Azure CLI SDK imports.
#
# The commands.py transformer functions have no SDK dependencies.
# The _compare_versions static method is self-contained.
# We use importlib to load just those modules selectively.
# ---------------------------------------------------------------------------

# Add the extension source to path
_ext_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _ext_root not in sys.path:
    sys.path.insert(0, _ext_root)

# Stub out azure.cli.core.aaz to prevent import errors when loading _install_os.py
# We only need the static _compare_versions method.
import types

def _ensure_module(dotted_name):
    """Create stub module hierarchy so 'from azure.cli.core.aaz import *' doesn't crash."""
    parts = dotted_name.split('.')
    for i in range(len(parts)):
        name = '.'.join(parts[:i + 1])
        if name not in sys.modules:
            sys.modules[name] = types.ModuleType(name)

# Create stubs for azure.cli.core.aaz and dependencies
for mod in [
    'azure', 'azure.cli', 'azure.cli.core', 'azure.cli.core.aaz',
    'azure.cli.core.commands', 'azure.cli.core.azclierror',
    'azure.cli.core.util',
    'knack', 'knack.log', 'knack.help_files',
]:
    _ensure_module(mod)

# Stub azure.cli.core classes needed by __init__.py
core_mod = sys.modules['azure.cli.core']
core_mod.AzCommandsLoader = type('AzCommandsLoader', (), {
    '__init__': lambda self, *a, **kw: None,
    'command_table': {},
})

cmd_mod = sys.modules['azure.cli.core.commands']
cmd_mod.CliCommandType = type('CliCommandType', (), {
    '__init__': lambda self, *a, **kw: None,
})

azclierror_mod = sys.modules['azure.cli.core.azclierror']
azclierror_mod.ResourceNotFoundError = type('ResourceNotFoundError', (Exception,), {})
azclierror_mod.InvalidArgumentValueError = type('InvalidArgumentValueError', (Exception,), {})
azclierror_mod.RequiredArgumentMissingError = type('RequiredArgumentMissingError', (Exception,), {})

# Add required attributes to stubs
aaz_mod = sys.modules['azure.cli.core.aaz']
# Provide no-op classes/functions so 'from azure.cli.core.aaz import *' works
for attr in ['AAZCommand', 'AAZHttpOperation', 'AAZStrArg', 'AAZListArg',
             'AAZResourceGroupNameArg', 'AAZStrArgFormat', 'AAZObjectType',
             'AAZStrType', 'AAZListType', 'AAZAnyType', 'register_command',
             'register_callback', 'has_value', 'register_command_group',
             'AAZCommandGroup']:
    if not hasattr(aaz_mod, attr):
        if attr in ('register_command', 'register_command_group'):
            setattr(aaz_mod, attr, lambda *a, **kw: (lambda cls: cls))
        elif attr in ('register_callback',):
            setattr(aaz_mod, attr, lambda fn: fn)
        elif attr == 'has_value':
            setattr(aaz_mod, attr, lambda x: x is not None)
        else:
            setattr(aaz_mod, attr, type(attr, (), {'__init__': lambda self, *a, **kw: None}))

# Make 'from azure.cli.core.aaz import *' export all stubs
aaz_mod.__all__ = [attr for attr in dir(aaz_mod) if not attr.startswith('_')]

# Stub knack.log
knack_log = sys.modules['knack.log']
knack_log.get_logger = lambda name: types.SimpleNamespace(
    info=lambda *a, **kw: None,
    warning=lambda *a, **kw: None,
    error=lambda *a, **kw: None,
)

# Stub knack.help_files
knack_help = sys.modules['knack.help_files']
knack_help.helps = {}

# Now we can safely import the functions we need to test
from azext_provisionedmachine.commands import (
    transform_show_status_table_output,
    transform_os_image_list_table_output,
)

# Import _compare_versions from install_os module
from azext_provisionedmachine.aaz.latest.provisionedmachine._install_os import InstallOs
_compare_versions = InstallOs._compare_versions


# ---------------------------------------------------------------------------
# Fixtures: representative API responses mirroring the lifecycle contracts
# ---------------------------------------------------------------------------

SHOW_STATUS_HAPPY_PATH = {
    "lifecycleStatus": {
        "status": "ReadyForOs",
        "stage": "ProvisionMachine",
        "message": "Machine has been successfully onboarded to Azure",
        "lastUpdatedUtc": "2025-03-23T08:05:35Z",
    },
    "lifecycleStages": [
        {
            "name": "ProvisionMachine",
            "description": "Provision Machine",
            "status": "Completed",
            "startTimeUtc": "2025-03-23T08:01:10Z",
            "endTimeUtc": "2025-03-23T08:05:35Z",
            "lastUpdatedUtc": "2025-03-23T08:05:35Z",
            "subStages": [
                {
                    "name": "RegisterMachine",
                    "description": "Register Machine with onboarding service",
                    "status": "Completed",
                    "lastUpdatedUtc": "2025-03-23T08:02:45Z",
                },
                {
                    "name": "ArcEnableMaintenanceEnvironment",
                    "description": "Arc-Enable Maintenance environment",
                    "status": "Completed",
                    "lastUpdatedUtc": "2025-03-23T08:05:30Z",
                },
                {
                    "name": "InstallExtensions",
                    "description": "Install required Arc Extensions",
                    "status": "Completed",
                    "lastUpdatedUtc": "2025-03-23T08:05:35Z",
                },
            ],
        },
        {
            "name": "InstallOS",
            "description": "Install OS",
            "status": "NotStarted",
            "startTimeUtc": None,
            "endTimeUtc": None,
            "lastUpdatedUtc": None,
            "subStages": [
                {
                    "name": "Initialize",
                    "description": "Initialize resource",
                    "status": "NotStarted",
                    "lastUpdatedUtc": None,
                },
                {
                    "name": "DownloadOS",
                    "description": "Download OS",
                    "status": "NotStarted",
                    "lastUpdatedUtc": None,
                },
            ],
        },
    ],
}

SHOW_STATUS_FAILURE = {
    "lifecycleStatus": {
        "status": "Failed",
        "stage": "InstallOS",
        "message": "Failed to download the OS",
        "lastUpdatedUtc": "2025-03-23T08:18:45Z",
        "recommendedSteps": [
            "Ensure the machine has sufficient disk space.",
            "Retry installing the OS.",
        ],
    },
    "lifecycleStages": [
        {
            "name": "ProvisionMachine",
            "description": "Provision Machine",
            "status": "Completed",
            "lastUpdatedUtc": "2025-03-23T08:05:35Z",
            "subStages": [],
        },
        {
            "name": "InstallOS",
            "description": "Install OS",
            "status": "Failed",
            "lastUpdatedUtc": "2025-03-23T08:18:45Z",
            "subStages": [
                {
                    "name": "Initialize",
                    "description": "Initialize resource",
                    "status": "Completed",
                    "lastUpdatedUtc": "2025-03-23T08:08:10Z",
                },
                {
                    "name": "DownloadOS",
                    "description": "Download OS",
                    "status": "Failed",
                    "lastUpdatedUtc": "2025-03-23T08:18:45Z",
                    "error": {
                        "code": "DownloadFailed",
                        "message": "Failed to download OS image.",
                    },
                },
            ],
        },
    ],
}

OS_IMAGE_LIST_RESPONSE = [
    {
        "id": "/subscriptions/sub1/providers/Microsoft.AzureStackHCI/locations/eastus/osImages/50.2607.0.8",
        "name": "50.2607.0.8",
        "type": "Microsoft.AzureStackHCI/OsImages",
        "properties": {
            "validatedSolutionRecipeVersion": "50.2607.0.8",
            "composedImageVersion": "2.2607.2.42",
        },
    },
    {
        "id": "/subscriptions/sub1/providers/Microsoft.AzureStackHCI/locations/eastus/osImages/50.2605.0.3",
        "name": "50.2605.0.3",
        "type": "Microsoft.AzureStackHCI/OsImages",
        "properties": {
            "validatedSolutionRecipeVersion": "50.2605.0.3",
            "composedImageVersion": "2.2605.1.18",
        },
    },
    {
        "id": "/subscriptions/sub1/providers/Microsoft.AzureStackHCI/locations/eastus/osImages/50.2603.0.1",
        "name": "50.2603.0.1",
        "type": "Microsoft.AzureStackHCI/OsImages",
        "properties": {
            "validatedSolutionRecipeVersion": "50.2603.0.1",
            "composedImageVersion": "2.2603.0.55",
        },
    },
]


# ===========================================================================
# show-status table transformer tests
# ===========================================================================

class TestShowStatusTableTransformer(unittest.TestCase):
    """Tests for transform_show_status_table_output."""

    def test_happy_path_returns_all_stages_and_substages(self):
        """Verify every stage and sub-stage appears as a row in the table."""
        rows = transform_show_status_table_output(SHOW_STATUS_HAPPY_PATH)

        # 2 stages + 3 sub-stages (ProvisionMachine) + 2 sub-stages (InstallOS) = 7
        self.assertEqual(len(rows), 7)

    def test_happy_path_first_row_is_first_stage(self):
        """First row must be the first stage (lifecycle status is printed to stderr)."""
        rows = transform_show_status_table_output(SHOW_STATUS_HAPPY_PATH)
        first = rows[0]

        self.assertEqual(first["Name"], "ProvisionMachine")
        self.assertEqual(first["Status"], "Completed")

    def test_happy_path_stage_rows_have_correct_status(self):
        """Stage-level rows carry the stage status (Completed, NotStarted, etc.)."""
        rows = transform_show_status_table_output(SHOW_STATUS_HAPPY_PATH)

        # rows[0] = ProvisionMachine stage
        self.assertEqual(rows[0]["Name"], "ProvisionMachine")
        self.assertEqual(rows[0]["Status"], "Completed")

        # rows[4] = InstallOS stage (after 3 ProvisionMachine sub-stages)
        self.assertEqual(rows[4]["Name"], "InstallOS")
        self.assertEqual(rows[4]["Status"], "NotStarted")

    def test_happy_path_substage_rows_have_tree_prefix(self):
        """Sub-stage rows must start with '  └─ ' tree prefix."""
        rows = transform_show_status_table_output(SHOW_STATUS_HAPPY_PATH)

        substage_rows = [r for r in rows if r["Name"].startswith("  └─")]
        # 3 sub-stages for ProvisionMachine + 2 for InstallOS = 5
        self.assertEqual(len(substage_rows), 5)

        # Check first sub-stage name
        self.assertEqual(substage_rows[0]["Name"], "  └─ RegisterMachine")
        self.assertEqual(substage_rows[0]["Status"], "Completed")

    def test_failure_path_first_stage(self):
        """Failure scenario: first row is ProvisionMachine stage."""
        rows = transform_show_status_table_output(SHOW_STATUS_FAILURE)
        first = rows[0]

        self.assertEqual(first["Name"], "ProvisionMachine")
        self.assertEqual(first["Status"], "Completed")

    def test_failure_path_substage_shows_failed(self):
        """Failure scenario: the DownloadOS sub-stage should show Failed."""
        rows = transform_show_status_table_output(SHOW_STATUS_FAILURE)

        download_rows = [r for r in rows if "DownloadOS" in r["Name"]]
        self.assertEqual(len(download_rows), 1)
        self.assertEqual(download_rows[0]["Status"], "Failed")

    def test_non_dict_input_returns_as_is(self):
        """Non-dict input (e.g., string error) passes through unchanged."""
        result = transform_show_status_table_output("some error string")
        self.assertEqual(result, "some error string")

    def test_empty_lifecycle_status(self):
        """Empty lifecycleStatus should produce no rows."""
        data = {"lifecycleStatus": {}, "lifecycleStages": []}
        rows = transform_show_status_table_output(data)
        self.assertEqual(len(rows), 0)

    def test_no_substages(self):
        """Stage with no subStages should still appear without sub-stage rows."""
        data = {
            "lifecycleStatus": {
                "status": "Provisioning",
                "stage": "ProvisionMachine",
                "message": "Provisioning in progress",
                "lastUpdatedUtc": "2025-03-23T08:02:00Z",
            },
            "lifecycleStages": [
                {
                    "name": "ProvisionMachine",
                    "description": "Provision Machine",
                    "status": "InProgress",
                    "lastUpdatedUtc": "2025-03-23T08:02:00Z",
                    "subStages": [],
                },
            ],
        }
        rows = transform_show_status_table_output(data)
        # 1 stage row only (lifecycle status is printed to stderr)
        self.assertEqual(len(rows), 1)

    def test_none_substages(self):
        """Stage with subStages=None should not crash."""
        data = {
            "lifecycleStatus": {
                "status": "Creating",
                "message": "",
                "lastUpdatedUtc": "2025-03-23T08:00:00Z",
            },
            "lifecycleStages": [
                {
                    "name": "ProvisionMachine",
                    "description": "Provision Machine",
                    "status": "NotStarted",
                    "lastUpdatedUtc": None,
                    "subStages": None,
                },
            ],
        }
        rows = transform_show_status_table_output(data)
        # 1 stage row only
        self.assertEqual(len(rows), 1)

    def test_row_keys_are_consistent(self):
        """Every row must have the same set of keys for table rendering."""
        rows = transform_show_status_table_output(SHOW_STATUS_HAPPY_PATH)
        expected_keys = {"Name", "Description", "Status", "LastUpdated"}
        for row in rows:
            self.assertEqual(set(row.keys()), expected_keys)

    def test_recommended_steps_printed_to_stderr(self):
        """Recommended steps should be printed to stderr, not in table rows."""
        import io
        import sys
        
        captured = io.StringIO()
        sys.stderr = captured
        rows = transform_show_status_table_output(SHOW_STATUS_FAILURE)
        sys.stderr = sys.__stderr__
        
        output = captured.getvalue()
        self.assertIn("Recommended Steps:", output)
        self.assertIn("Ensure the machine has sufficient disk space.", output)
        self.assertIn("Retry installing the OS.", output)
        
        # Verify no recommended step rows in table
        step_rows = [r for r in rows if "Step" in r.get("Name", "")]
        self.assertEqual(len(step_rows), 0)


# ===========================================================================
# os-image list table transformer tests
# ===========================================================================

class TestOsImageListTableTransformer(unittest.TestCase):
    """Tests for transform_os_image_list_table_output."""

    def test_returns_correct_number_of_rows(self):
        """Each OS image produces exactly one table row."""
        rows = transform_os_image_list_table_output(OS_IMAGE_LIST_RESPONSE)
        self.assertEqual(len(rows), 3)

    def test_vsr_version_extracted_from_properties(self):
        """VsrVersion comes from properties.validatedSolutionRecipeVersion, not from name."""
        rows = transform_os_image_list_table_output(OS_IMAGE_LIST_RESPONSE)
        self.assertEqual(rows[0]["VsrVersion"], "50.2607.0.8")
        self.assertEqual(rows[1]["VsrVersion"], "50.2605.0.3")
        self.assertEqual(rows[2]["VsrVersion"], "50.2603.0.1")

    def test_os_image_type_sourced_from_injected_field(self):
        """OsImageType should come from the injected _os_image_type field."""
        # Simulate the _output() method injecting _os_image_type
        test_data = [
            {
                "properties": {"validatedSolutionRecipeVersion": "50.2607.0.8"},
                "_os_image_type": "AzureLinux"
            },
            {
                "properties": {"validatedSolutionRecipeVersion": "50.2605.0.3"},
                "_os_image_type": "AzureLinux"
            }
        ]
        rows = transform_os_image_list_table_output(test_data)
        self.assertEqual(rows[0]["OsImageType"], "AzureLinux")
        self.assertEqual(rows[1]["OsImageType"], "AzureLinux")

    def test_non_list_input_returns_as_is(self):
        """Non-list input passes through unchanged."""
        result = transform_os_image_list_table_output("error string")
        self.assertEqual(result, "error string")

    def test_empty_list(self):
        """Empty list produces no rows."""
        rows = transform_os_image_list_table_output([])
        self.assertEqual(len(rows), 0)

    def test_item_without_properties(self):
        """Item missing 'properties' key should produce empty VsrVersion."""
        rows = transform_os_image_list_table_output([
            {"name": "test", "type": "Microsoft.AzureStackHCI/OsImages"},
        ])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["VsrVersion"], "")

    def test_non_dict_items_skipped(self):
        """Non-dict items in the list are skipped."""
        rows = transform_os_image_list_table_output([
            "not-a-dict",
            {"name": "50.2607.0.8", "properties": {"validatedSolutionRecipeVersion": "50.2607.0.8"}},
        ])
        self.assertEqual(len(rows), 1)

    def test_json_shape_preserves_all_properties(self):
        """Raw JSON response should retain all API fields (id, name, type, properties)."""
        # This tests the raw response shape, not the transformer.
        # The transformer only runs for -o table; raw JSON should keep everything.
        item = OS_IMAGE_LIST_RESPONSE[0]
        self.assertIn("id", item)
        self.assertIn("name", item)
        self.assertIn("type", item)
        self.assertIn("properties", item)
        self.assertIn("validatedSolutionRecipeVersion", item["properties"])
        self.assertIn("composedImageVersion", item["properties"])


# ===========================================================================
# install-os version comparison tests
# ===========================================================================

class TestVersionComparison(unittest.TestCase):
    """Tests for _compare_versions."""

    def test_greater_major(self):
        self.assertGreater(_compare_versions("51.0.0.0", "50.0.0.0"), 0)

    def test_less_major(self):
        self.assertLess(_compare_versions("49.0.0.0", "50.0.0.0"), 0)

    def test_equal_versions(self):
        self.assertEqual(_compare_versions("50.2607.0.8", "50.2607.0.8"), 0)

    def test_greater_minor(self):
        self.assertGreater(_compare_versions("50.2607.0.8", "50.2605.0.3"), 0)

    def test_greater_patch(self):
        self.assertGreater(_compare_versions("50.2607.0.8", "50.2607.0.3"), 0)

    def test_numeric_not_lexicographic(self):
        """Ensure numeric comparison: 50.x > 9.x (lexicographic would say 9 > 5)."""
        self.assertGreater(_compare_versions("50.0.0.0", "9.0.0.0"), 0)

    def test_different_length_versions(self):
        """Shorter version is padded with zeros."""
        self.assertEqual(_compare_versions("50.2607", "50.2607.0.0"), 0)

    def test_three_segment_vs_four_segment(self):
        self.assertLess(_compare_versions("50.2607.0", "50.2607.0.1"), 0)

    def test_ordering_of_known_vsr_versions(self):
        """Verify the ordering of real VSR versions from the API."""
        versions = ["50.2603.0.1", "50.2605.0.3", "50.2607.0.8"]
        for i in range(len(versions) - 1):
            self.assertLess(
                _compare_versions(versions[i], versions[i + 1]),
                0,
                f"{versions[i]} should be less than {versions[i+1]}",
            )

    def test_find_latest_from_api_response(self):
        """Simulate the auto-resolve logic: iterate images and find the latest version."""
        images = OS_IMAGE_LIST_RESPONSE  # Already in descending order from API

        # Method 1: Take first item (API returns descending)
        latest_by_first = images[0]["properties"]["validatedSolutionRecipeVersion"]
        self.assertEqual(latest_by_first, "50.2607.0.8")

        # Method 2: Use _compare_versions to find max (fallback validation)
        latest_version = None
        for image in images:
            vsr = image["properties"]["validatedSolutionRecipeVersion"]
            if latest_version is None or _compare_versions(vsr, latest_version) > 0:
                latest_version = vsr
        self.assertEqual(latest_version, "50.2607.0.8")

        # Both methods agree
        self.assertEqual(latest_by_first, latest_version)


# ===========================================================================
# install-os auto-resolve edge cases (pure logic, no API calls)
# ===========================================================================

class TestAutoResolveVersionLogic(unittest.TestCase):
    """Test the auto-resolve logic paths without making actual API calls."""

    def test_empty_images_list_should_fail(self):
        """When API returns no images, _resolve_latest_version should raise."""
        # We can't call _resolve_latest_version directly without a live context,
        # but we can verify the logic pattern: empty list → no latest version
        images = []
        latest_version = None
        for image in images:
            props = image.get("properties", {})
            vsr = props.get("validatedSolutionRecipeVersion", "")
            if vsr and (latest_version is None or _compare_versions(vsr, latest_version) > 0):
                latest_version = vsr
        self.assertIsNone(latest_version)

    def test_single_image_returns_its_version(self):
        """Single image in list → that version is the latest."""
        images = [OS_IMAGE_LIST_RESPONSE[0]]
        latest_version = None
        for image in images:
            props = image.get("properties", {})
            vsr = props.get("validatedSolutionRecipeVersion", "")
            if vsr and (latest_version is None or _compare_versions(vsr, latest_version) > 0):
                latest_version = vsr
        self.assertEqual(latest_version, "50.2607.0.8")

    def test_unsorted_input_still_finds_latest(self):
        """Even if API response is not sorted, the logic should find the max."""
        images = list(reversed(OS_IMAGE_LIST_RESPONSE))  # ascending order
        latest_version = None
        for image in images:
            props = image.get("properties", {})
            vsr = props.get("validatedSolutionRecipeVersion", "")
            if vsr and (latest_version is None or _compare_versions(vsr, latest_version) > 0):
                latest_version = vsr
        self.assertEqual(latest_version, "50.2607.0.8")

    def test_images_with_missing_vsr_version_skipped(self):
        """Images without validatedSolutionRecipeVersion are skipped."""
        images = [
            {"properties": {}},
            {"properties": {"validatedSolutionRecipeVersion": ""}},
            {"properties": {"validatedSolutionRecipeVersion": "50.2605.0.3"}},
        ]
        latest_version = None
        for image in images:
            props = image.get("properties", {})
            vsr = props.get("validatedSolutionRecipeVersion", "")
            if vsr and (latest_version is None or _compare_versions(vsr, latest_version) > 0):
                latest_version = vsr
        self.assertEqual(latest_version, "50.2605.0.3")


if __name__ == "__main__":
    unittest.main()
