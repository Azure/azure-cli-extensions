# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import tempfile
import unittest

from azure.cli.core.azclierror import ValidationError

from azext_logicapp import _workflow, custom


class WorkflowValidationRegressions(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.workflow_path = os.path.join(self.folder.name, "hello")
        os.makedirs(self.workflow_path)

    def _write(self, payload):
        with open(os.path.join(self.workflow_path, "workflow.json"), "w", encoding="utf-8") as handle:
            json.dump(payload, handle)

    def test_invalid_trigger_shapes_return_structured_findings(self):
        for triggers in (["invalid"], [], "invalid", "", None, 1, True, {}):
            with self.subTest(triggers=triggers):
                self._write({"kind": "Stateful", "definition": {"triggers": triggers, "actions": {}}})
                report = _workflow.static_validate(self.folder.name, workflow="hello")
                self.assertFalse(report["valid"])
                self.assertEqual({"errors": 1, "warnings": 0, "workflows": 1}, report["summary"])
                finding = report["findings"][0]
                self.assertEqual("workflow.triggers.missing", finding["rule"])
                self.assertEqual("$.definition.triggers", finding["jsonPath"])
                self.assertEqual("error", finding["severity"])

    def test_missing_triggers_does_not_skip_other_checks(self):
        self._write({
            "kind": "invalid",
            "definition": {
                "actions": {
                    "Compose": {
                        "type": "Compose",
                        "inputs": "@appsetting('setting')",
                        "runAfter": {"missing": ["Succeeded"]},
                    },
                },
            },
        })
        report = _workflow.static_validate(self.folder.name, workflow="hello")
        self.assertEqual({"errors": 3, "warnings": 1, "workflows": 1}, report["summary"])
        self.assertEqual(
            {"workflow.kind.invalid", "workflow.triggers.missing",
             "graph.missing_action", "appsetting.offline_unverified"},
            {finding["rule"] for finding in report["findings"]},
        )

    def test_missing_or_nonobject_actions_return_structured_findings(self):
        for kind in ("Stateful", "Stateless"):
            for value in ("missing", None, [], "invalid", 1, True):
                with self.subTest(kind=kind, actions=value):
                    document = _workflow.workflow_json(kind)
                    if value == "missing":
                        document["definition"].pop("actions")
                    else:
                        document["definition"]["actions"] = value
                    self._write(document)
                    report = _workflow.static_validate(self.folder.name, workflow="hello")
                    self.assertFalse(report["valid"])
                    self.assertEqual({"errors": 1, "warnings": 0, "workflows": 1}, report["summary"])
                    self.assertEqual("workflow.actions.invalid", report["findings"][0]["rule"])
                    self.assertEqual("$.definition.actions", report["findings"][0]["jsonPath"])
                    with self.assertRaises(ValidationError):
                        custom.workflow_validate(None, path=self.folder.name, workflow="hello")

    def test_empty_actions_objects_remain_valid(self):
        for kind in ("Stateful", "Stateless"):
            with self.subTest(kind=kind):
                document = _workflow.workflow_json(kind)
                document["definition"]["actions"] = {}
                self._write(document)
                report = custom.workflow_validate(None, path=self.folder.name, workflow="hello")
                self.assertTrue(report["valid"])
                self.assertEqual([], report["findings"])

    def test_non_object_triggers_preserve_action_and_reference_findings(self):
        self._write({
            "kind": "Stateful",
            "definition": {"triggers": ["invalid"], "actions": {"Compose": None}},
            "$connections": {},
        })
        report = _workflow.static_validate(self.folder.name, workflow="hello")
        self.assertEqual(
            {"workflow.triggers.missing", "action.invalid", "connection.offline_unverified"},
            {finding["rule"] for finding in report["findings"]},
        )

    def test_command_raises_validation_error_containing_report_not_attribute_error(self):
        for triggers in (["invalid"], "invalid", None):
            with self.subTest(triggers=triggers):
                self._write({"kind": "Stateful", "definition": {"triggers": triggers, "actions": {}}})
                with self.assertRaises(ValidationError) as raised:
                    custom.workflow_validate(None, path=self.folder.name, workflow="hello")
                report = json.loads(str(raised.exception))
                self.assertFalse(report["valid"])
                self.assertEqual("workflow.triggers.missing", report["findings"][0]["rule"])

    def test_valid_trigger_checks_are_unchanged(self):
        self._write(_workflow.workflow_json("Stateful"))
        report = custom.workflow_validate(None, path=self.folder.name, workflow="hello")
        self.assertTrue(report["valid"])
        self.assertEqual([], report["findings"])
        self.assertEqual({"errors": 0, "warnings": 0, "workflows": 1}, report["summary"])

        self._write({
            "kind": "Stateful",
            "definition": {"triggers": {"bad": None, "manual": {"type": "Request", "kind": "Other"}},
                           "actions": {}},
        })
        report = _workflow.static_validate(self.folder.name, workflow="hello")
        self.assertEqual({"trigger.invalid", "trigger.kind.warning"},
                         {finding["rule"] for finding in report["findings"]})


if __name__ == "__main__":
    unittest.main()
