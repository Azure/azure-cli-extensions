# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock

from knack.util import CLIError

from azext_chaos._validators import validate_scope, validate_parameters_json


class TestValidateScope(unittest.TestCase):
    """Tests for the --scopes ARM resource ID validator."""

    def _make_namespace(self, scopes):
        ns = MagicMock()
        ns.scopes = scopes
        return ns

    def test_valid_subscription_scope(self):
        ns = self._make_namespace(
            ["/subscriptions/00000000-0000-0000-0000-000000000000"]
        )
        validate_scope(ns)  # should not raise

    def test_valid_resource_group_scope(self):
        ns = self._make_namespace(
            ["/subscriptions/00000000-0000-0000-0000-000000000000"
             "/resourceGroups/MyRG"]
        )
        validate_scope(ns)  # should not raise

    def test_valid_resource_scope(self):
        # Individual resources are not advertised in help (the portal does not
        # offer them), but the service accepts them, so the validator does not
        # go out of its way to block them.
        ns = self._make_namespace(
            ["/subscriptions/00000000-0000-0000-0000-000000000000"
             "/resourceGroups/MyRG/providers/Microsoft.Compute/virtualMachines/myVM"]
        )
        validate_scope(ns)  # should not raise

    def test_valid_service_group_scope(self):
        ns = self._make_namespace(
            ["/providers/Microsoft.Management/serviceGroups/my-critical-services"]
        )
        validate_scope(ns)  # should not raise

    def test_valid_service_group_scope_case_insensitive(self):
        ns = self._make_namespace(
            ["/providers/microsoft.management/servicegroups/sg1"]
        )
        validate_scope(ns)  # should not raise

    def test_mixed_subscription_and_service_group_scopes(self):
        ns = self._make_namespace([
            "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/RG1",
            "/providers/Microsoft.Management/serviceGroups/sg1",
        ])
        validate_scope(ns)  # should not raise

    def test_invalid_service_group_missing_name(self):
        ns = self._make_namespace(
            ["/providers/Microsoft.Management/serviceGroups"]
        )
        with self.assertRaises(CLIError):
            validate_scope(ns)

    def test_multiple_valid_scopes(self):
        ns = self._make_namespace([
            "/subscriptions/00000000-0000-0000-0000-000000000000",
            "/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/RG2"
        ])
        validate_scope(ns)  # should not raise

    def test_invalid_scope_no_leading_slash(self):
        ns = self._make_namespace(["subscriptions/00000000-0000-0000-0000-000000000000"])
        with self.assertRaises(CLIError):
            validate_scope(ns)

    def test_invalid_scope_missing_subscriptions(self):
        ns = self._make_namespace(["/foo/bar"])
        with self.assertRaises(CLIError):
            validate_scope(ns)

    def test_empty_scope_string(self):
        ns = self._make_namespace([""])
        with self.assertRaises(CLIError):
            validate_scope(ns)

    def test_none_scopes_passes(self):
        ns = self._make_namespace(None)
        validate_scope(ns)  # should not raise when scopes is None

    def test_empty_list_passes(self):
        ns = self._make_namespace([])
        validate_scope(ns)  # should not raise when scopes is empty


class TestValidateParametersJson(unittest.TestCase):
    """Tests for the --parameters JSON validator."""

    def _make_namespace(self, parameters):
        ns = MagicMock()
        ns.parameters = parameters
        return ns

    def test_raw_json_string(self):
        data = [{"key": "duration", "value": "PT5M"}]
        ns = self._make_namespace(json.dumps(data))
        validate_parameters_json(ns)
        self.assertEqual(ns.parameters, data)

    def test_file_reference(self):
        data = [{"key": "duration", "value": "PT10M"}]
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(data, f)
            f.flush()
            tmp_path = f.name
        try:
            ns = self._make_namespace(f"@{tmp_path}")
            validate_parameters_json(ns)
            self.assertEqual(ns.parameters, data)
        finally:
            os.unlink(tmp_path)

    def test_invalid_json_string(self):
        ns = self._make_namespace("{not valid json}")
        with self.assertRaises(CLIError):
            validate_parameters_json(ns)

    def test_none_parameters_passes(self):
        ns = self._make_namespace(None)
        validate_parameters_json(ns)  # should not raise

    def test_empty_string_passes(self):
        ns = self._make_namespace("")
        validate_parameters_json(ns)  # should not raise

    def test_file_reference_nonexistent(self):
        ns = self._make_namespace("@/nonexistent/path/file.json")
        with self.assertRaises(CLIError):
            validate_parameters_json(ns)

    def test_rejects_key_value_string(self):
        # F7: a natural key=value mistake gets a targeted error with the hint.
        ns = self._make_namespace("duration=PT10M")
        with self.assertRaises(CLIError) as ctx:
            validate_parameters_json(ns)
        self.assertIn('JSON array', str(ctx.exception))

    def test_rejects_json_object(self):
        # F7: a JSON object (not an array) is rejected with the format hint.
        ns = self._make_namespace('{"duration": "PT10M"}')
        with self.assertRaises(CLIError) as ctx:
            validate_parameters_json(ns)
        self.assertIn('JSON array', str(ctx.exception))

    def test_rejects_list_without_key_value(self):
        # F7: array elements must be {key, value} objects.
        ns = self._make_namespace('[{"name": "duration"}]')
        with self.assertRaises(CLIError):
            validate_parameters_json(ns)

    def test_accepts_valid_key_value_array(self):
        data = [{"key": "duration", "value": "PT10M"}]
        ns = self._make_namespace(json.dumps(data))
        validate_parameters_json(ns)
        self.assertEqual(ns.parameters, data)


if __name__ == '__main__':
    unittest.main()
