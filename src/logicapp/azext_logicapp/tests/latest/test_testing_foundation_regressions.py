# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
import json
import os
import socket
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from knack.events import EVENT_CLI_POST_EXECUTE, EVENT_CLI_SUCCESSFUL_EXECUTE

from azext_logicapp import _context, _test_report as protocol, _testing as testing, _workflow, custom

SECRET = "SECRET-LITERAL-NEVER-EXPORT"
XML = ('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net8.0</TargetFramework>'
       '</PropertyGroup><ItemGroup><PackageReference Include="' + protocol.SDK_PACKAGE +
       '" Version="1.0.3"/></ItemGroup></Project>')


class FoundationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / "App"
        self.project.mkdir()
        self.definition = self.write("Orders", _workflow.workflow_json("Stateful"), workflow=True)
        self.host = self.write("host.json", _workflow.HOST_JSON)
        self.test_project = self.root / "Tests.csproj"
        self.test_project.write_text(XML, encoding="utf-8")
        self.result_file = self.root / "report.json"
        for target, name in ((subprocess, "Popen"), (subprocess, "run"), (socket, "create_connection"),
                             (_context, "get_context")):
            patcher = mock.patch.object(target, name, side_effect=AssertionError("No execution, network or context"))
            patcher.start()
            self.addCleanup(patcher.stop)

    def write(self, name, payload, workflow=False):
        path = self.project / name
        if workflow:
            path = path / "workflow.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def plan(self, **kwargs):
        return testing.plan_report(str(self.project), "Orders", **kwargs)

    def save(self, report=None):
        self.result_file.write_text(json.dumps(report or self.plan()), encoding="utf-8")
        return str(self.result_file)

    def rules(self, report):
        return {row["rule"] for row in report["findings"]}

    def assert_gated(self, report):
        self.assertEqual("notExecuted", report["executionState"])
        self.assertEqual("notExecuted", report["businessTests"])
        self.assertEqual(0, report["summary"]["executed"])
        self.assertEqual(0, report["summary"]["passed"])
        self.assertEqual(0, report["summary"]["failed"])
        self.assertEqual("blocked", report["gates"]["sdkRestore"])
        self.assertEqual("blocked", report["gates"]["sdkExecution"])
        self.assertEqual("unresolved", report["gates"]["sdkAdoption"])
        self.assertIsNone(report["dependencies"]["installedSdkVersion"])

    def test_healthy_definition_is_limited_inspection_not_test_pass(self):
        before = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        report = self.plan(test_project=str(self.test_project))
        self.assertEqual(0, report["exitCode"])
        self.assertEqual("planned", report["outcome"])
        self.assertEqual("planning", report["exitPolicy"])
        self.assertEqual("2.0", report["schemaVersion"])
        self.assertEqual("passedLimited", report["coverage"]["static"])
        self.assertEqual("1.0.3", report["dependencies"]["declaredSdkVersion"])
        self.assertEqual("net8.0", report["dependencies"]["declaredTargetFramework"])
        self.assertEqual("notInspected", report["dependencies"]["resolution"])
        self.assertTrue(protocol.validate_report(report))
        self.assert_gated(report)
        self.assertEqual(before, {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()})

    def test_strict_plan_preserves_execution_gates_and_reports_without_running_tests(self):
        report = self.plan(strict=True, report_path=str(self.result_file))
        self.assertEqual(4, report["exitCode"])
        self.assertEqual("blocked", report["outcome"])
        self.assertEqual("strict", report["exitPolicy"])
        self.assertTrue(protocol.validate_report(report))
        self.assertEqual(report, json.loads(self.result_file.read_text()))
        self.assert_gated(report)
        inspected = testing.results_report(str(self.result_file))
        self.assertEqual(0, inspected["exitCode"])
        self.assertEqual("strict", inspected["exitPolicy"])
        self.assertEqual(4, inspected["inspection"]["sourceExitCode"])
        self.assertEqual("blocked", inspected["inspection"]["sourceOutcome"])
        self.assert_gated(inspected)

    def test_plan_policy_does_not_override_error_precedence(self):
        for strict in (False, True):
            for rule, outcome, code in (
                    ("workflow.actions.invalid", "authoringInvalid", 1),
                    ("input.invalidJson", "inputError", 3),
                    ("input.changed", "stale", 5),
                    ("report.publication", "publicationError", 6)):
                with self.subTest(strict=strict, rule=rule):
                    report = self.plan(strict=strict)
                    report["findings"].append(protocol.finding(rule, "workflow"))
                    protocol.finalize(report)
                    self.assertEqual((outcome, code), (report["outcome"], report["exitCode"]))
                    self.assert_gated(report)
            self.definition.write_text("{}", encoding="utf-8")
            self.assertEqual(1, self.plan(strict=strict)["exitCode"])
            self.definition.write_text("{", encoding="utf-8")
            self.assertEqual(3, self.plan(strict=strict)["exitCode"])
            self.write("Orders", _workflow.workflow_json("Stateful"), workflow=True)
            self.assertEqual(6, self.plan(strict=strict, report_path=str(self.root / "missing" / "p.json"))["exitCode"])
            with mock.patch.object(testing, "_recheck", side_effect=lambda report, _snapshots:
                                   report["findings"].append(protocol.finding("input.changed", "workflow"))):
                self.assertEqual(5, self.plan(strict=strict)["exitCode"])

    def test_previous_schema2_reports_preserve_both_exit_policies_and_blocked_sdk_gates(self):
        for strict in (False, True):
            with self.subTest(strict=strict):
                earlier = self.plan(strict=strict)
                earlier["provenance"]["cliVersion"] = "0.1.22"
                self.assertTrue(protocol.validate_report(earlier))
                inspected = testing.results_report(self.save(earlier))
                self.assertEqual(0, inspected["exitCode"])
                self.assertEqual("2.0", inspected["schemaVersion"])
                self.assertEqual("0.1.22", inspected["provenance"]["cliVersion"])
                self.assertEqual("strict" if strict else "planning", inspected["exitPolicy"])
                self.assertEqual(4 if strict else 0, inspected["inspection"]["sourceExitCode"])
                self.assertEqual("blocked" if strict else "planned", inspected["inspection"]["sourceOutcome"])
                self.assert_gated(inspected)

    def test_closed_policy_rejects_inconsistent_exits_and_schema_producer_combinations(self):
        for strict in (False, True):
            source = self.plan(strict=strict)
            for edit in (
                    lambda doc: doc.pop("exitPolicy"),
                    lambda doc: doc.update(exitPolicy=None),
                    lambda doc: doc.update(exitPolicy=[]),
                    lambda doc: doc.update(exitPolicy={}),
                    lambda doc: doc.update(exitPolicy=True),
                    lambda doc: doc.update(exitPolicy="execution"),
                    lambda doc: doc.update(exitPolicy="planning" if strict else "strict"),
                    lambda doc: doc.update(exitCode=0 if strict else 4),
                    lambda doc: doc.update(outcome="planned" if strict else "blocked"),
                    lambda doc: doc.update(schemaVersion="1.0"),
                    lambda doc: doc["provenance"].update(cliVersion="0.1.21")):
                with self.subTest(strict=strict, edit=edit):
                    invalid = copy.deepcopy(source)
                    edit(invalid)
                    self.assertFalse(protocol.validate_report(invalid))
                    self.assertEqual(3, testing.results_report(self.save(invalid))["exitCode"])

    def test_legacy_reports_preserve_source_exits_without_adopting_planning_policy(self):
        for version in ("0.1.17", "0.1.18", "0.1.19", "0.1.20", "0.1.21", "1.0.0b1"):
            legacy = self.plan()
            legacy["schemaVersion"] = "1.0"
            legacy["provenance"]["cliVersion"] = version
            del legacy["exitPolicy"]
            protocol.finalize(legacy)
            with self.subTest(version=version):
                self.assertEqual(("blocked", 4), (legacy["outcome"], legacy["exitCode"]))
                self.assertTrue(protocol.validate_report(legacy))
                inspected = testing.results_report(self.save(legacy))
                self.assertEqual(0, inspected["exitCode"])
                self.assertEqual("1.0", inspected["schemaVersion"])
                self.assertNotIn("exitPolicy", inspected)
                self.assertEqual(version, inspected["provenance"]["cliVersion"])
                self.assertEqual(4, inspected["inspection"]["sourceExitCode"])
                self.assertEqual("blocked", inspected["inspection"]["sourceOutcome"])
                self.assert_gated(inspected)
                for edit in (
                        lambda doc: doc.update(exitCode=0, outcome="planned"),
                        lambda doc: doc.update(exitPolicy="planning"),
                        lambda doc: doc.update(schemaVersion="2.0"),
                        lambda doc: doc["provenance"].update(cliVersion="unknown")):
                    invalid = copy.deepcopy(legacy)
                    edit(invalid)
                    self.assertFalse(protocol.validate_report(invalid))

    def test_prior_producer_error_catalogs_and_context_guidance_remain_inspectable(self):
        for version in ("0.1.17", "0.1.18", "0.1.19", "0.1.20", "0.1.21", "0.1.22", "0.1.23", "0.1.24"):
            earlier = self.plan()
            earlier["provenance"]["cliVersion"] = version
            if version in protocol._V1_PRODUCERS:
                earlier["schemaVersion"] = "1.0"
                del earlier["exitPolicy"]
            earlier["findings"].append(protocol.finding("report.invalid", "report", producer_version=version))
            protocol.finalize(earlier)
            with self.subTest(version=version):
                self.assertTrue(protocol.validate_report(earlier))
                inspected = testing.results_report(self.save(earlier))
                self.assertEqual(0, inspected["exitCode"])
                self.assertEqual(3, inspected["inspection"]["sourceExitCode"])
                self.assertEqual(earlier["findings"], inspected["findings"])
                self.assert_gated(inspected)
        context_error = testing.plan_report(str(self.project), "")
        context_error["provenance"]["cliVersion"] = "0.1.24"
        self.assertTrue(protocol.validate_report(context_error))
        self.assertIn("local context", next(row["recommendation"] for row in context_error["findings"]
                                           if row["rule"] == "input.options"))

    def test_stateless_is_preserved_not_qualified(self):
        self.write("Orders", _workflow.workflow_json("Stateless"), workflow=True)
        report = self.plan()
        self.assertEqual("Stateless", report["workflow"]["kind"])
        self.assert_gated(report)
        self.assertEqual("unknown", report["gates"]["platformQualification"])

    def test_context_guidance_and_version_bump_preserve_closed_historical_report_catalogs(self):
        source = testing.plan_report(str(self.project), "")
        self.assertEqual(3, source["exitCode"])
        self.assertTrue(protocol.validate_report(source))
        self.assert_gated(source)
        for version in ("0.1.17", "0.1.18", "0.1.19", "0.1.20", "0.1.21", "0.1.22", "0.1.23"):
            earlier = copy.deepcopy(source)
            earlier["provenance"]["cliVersion"] = version
            if version not in ("0.1.22", "0.1.23"):
                earlier["schemaVersion"] = "1.0"
                del earlier["exitPolicy"]
            for row in earlier["findings"]:
                if row["rule"] == "input.options":
                    row["message"] = "Explicit local paths and a bounded workflow name are required."
                    row["recommendation"] = (
                        "Supply --path and --workflow; do not use URLs, device paths or target contexts.")
            protocol.finalize(earlier)
            with self.subTest(version=version):
                self.assertTrue(protocol.validate_report(earlier))
                inspected = testing.results_report(self.save(earlier))
                self.assertEqual(0, inspected["exitCode"])
                self.assertEqual(version, inspected["provenance"]["cliVersion"])
                self.assertEqual(earlier["findings"], inspected["findings"])
                self.assertEqual(3, inspected["inspection"]["sourceExitCode"])
                self.assert_gated(inspected)
                invalid = copy.deepcopy(earlier)
                invalid["findings"][0]["recommendation"] = "Arbitrary unsupported guidance"
                self.assertFalse(protocol.validate_report(invalid))
                invalid = copy.deepcopy(earlier)
                invalid["summary"]["executed"] = 1
                self.assertFalse(protocol.validate_report(invalid))
        for version in ("0.1.22", "0.1.23", "0.1.24", "0.1.25", "0.1.26"):
            for strict in (False, True):
                earlier = self.plan(strict=strict)
                earlier["provenance"]["cliVersion"] = version
                with self.subTest(version=version, strict=strict):
                    self.assertTrue(protocol.validate_report(earlier))
                    inspected = testing.results_report(self.save(earlier))
                    self.assertEqual(0, inspected["exitCode"])
                    self.assertEqual(4 if strict else 0, inspected["inspection"]["sourceExitCode"])
                    self.assert_gated(inspected)
        invalid = self.plan()
        invalid["provenance"]["cliVersion"] = "99.99.99"
        self.assertFalse(protocol.validate_report(invalid))
        invalid = copy.deepcopy(source)
        invalid["provenance"]["cliVersion"] = "0.1.24"
        for row in invalid["findings"]:
            if row["rule"] == "input.options":
                row["message"] = "Explicit local paths and a bounded workflow name are required."
                row["recommendation"] = (
                    "Supply --path and --workflow; do not use URLs, device paths or target contexts.")
        self.assertFalse(protocol.validate_report(invalid))

    def test_public_preview_preserves_only_exact_legacy_and_current_options_catalogs(self):
        source = testing.plan_report(str(self.project), "")
        current = next(row for row in source["findings"] if row["rule"] == "input.options")
        old_message = "Explicit local paths and a bounded workflow name are required."
        old_recommendation = "Supply --path and --workflow; do not use URLs, device paths or target contexts."
        for schema, legacy in (("1.0", True), ("1.0", False), ("2.0", True), ("2.0", False)):
            report = copy.deepcopy(source)
            report["schemaVersion"] = schema
            report["provenance"]["cliVersion"] = "1.0.0b1"
            if schema == "1.0":
                del report["exitPolicy"]
            row = next(item for item in report["findings"] if item["rule"] == "input.options")
            if legacy:
                row.update(message=old_message, recommendation=old_recommendation)
            protocol.finalize(report)
            with self.subTest(schema=schema, legacy=legacy):
                if schema == "1.0" and not legacy:
                    self.assertFalse(protocol.validate_report(report))
                    continue
                original = copy.deepcopy(report)
                self.assertTrue(protocol.validate_report(report))
                inspected = testing.results_report(self.save(report))
                self.assertEqual(0, inspected["exitCode"])
                self.assertEqual(original, report)
                self.assertEqual(report["findings"], inspected["findings"])
                self.assertEqual(3, inspected["inspection"]["sourceExitCode"])
                self.assert_gated(inspected)
                for field, old in (("message", old_message), ("recommendation", old_recommendation)):
                    invalid = copy.deepcopy(report)
                    changed = next(item for item in invalid["findings"] if item["rule"] == "input.options")
                    changed[field] = current[field] if legacy else old
                    self.assertFalse(protocol.validate_report(invalid))

    def test_public_preview_preserves_exact_historical_and_sdk_report_error_catalogs(self):
        source = self.plan()
        for schema, legacy in (("1.0", True), ("1.0", False), ("2.0", True), ("2.0", False)):
            report = copy.deepcopy(source)
            report["schemaVersion"] = schema
            report["provenance"]["cliVersion"] = "1.0.0b1"
            if schema == "1.0":
                del report["exitPolicy"]
            row = protocol.finding("report.invalid", "report",
                                   producer_version="1.0.0b1" if legacy else None)
            report["findings"].append(row)
            protocol.finalize(report)
            with self.subTest(schema=schema, legacy=legacy):
                if schema == "1.0" and not legacy:
                    self.assertFalse(protocol.validate_report(report))
                    continue
                self.assertTrue(protocol.validate_report(report))
                inspected = testing.results_report(self.save(report))
                self.assertEqual(report["findings"], inspected["findings"])
                self.assertEqual(3, inspected["inspection"]["sourceExitCode"])
                self.assert_gated(inspected)
                for field in ("message", "recommendation"):
                    invalid = copy.deepcopy(report)
                    invalid["findings"][-1][field] = protocol.finding(
                        "report.invalid", "report", producer_version=None if legacy else "1.0.0b1")[field]
                    self.assertFalse(protocol.validate_report(invalid))

    def test_absent_empty_and_invalid_project_never_create_files(self):
        missing = self.root / "missing"
        before = sorted(str(path) for path in self.root.rglob("*"))
        for path in (missing, self.root):
            with self.subTest(path=path):
                report = testing.plan_report(str(path), "Orders")
                self.assertEqual(3, report["exitCode"])
                self.assertTrue(protocol.validate_report(report))
                self.assert_gated(report)
        self.assertEqual(before, sorted(str(path) for path in self.root.rglob("*")))
        self.host.write_text("null", encoding="utf-8")
        self.assertIn("host.invalid", self.rules(self.plan()))

    def test_workflow_shape_kind_schema_and_top_level_dependencies(self):
        for edit, rule in (
                (lambda doc: doc.pop("kind"), "workflow.kind.invalid"),
                (lambda doc: doc.update(kind=SECRET), "workflow.kind.invalid"),
                (lambda doc: doc.pop("definition"), "workflow.definition.missing"),
                (lambda doc: doc["definition"].pop("$schema"), "workflow.schema"),
                (lambda doc: doc["definition"].update(triggers={}), "workflow.triggers.missing"),
                (lambda doc: doc["definition"].update(actions=[]), "workflow.actions.invalid"),
                (lambda doc: doc["definition"].pop("actions"), "workflow.actions.invalid"),
                (lambda doc: doc["definition"]["actions"]["Response"].update(runAfter={SECRET: []}),
                 "graph.missing_action")):
            with self.subTest(rule=rule):
                doc = _workflow.workflow_json("Stateful")
                edit(doc)
                self.write("Orders", doc, workflow=True)
                report = self.plan()
                self.assertEqual(1, report["exitCode"])
                self.assertIn(rule, self.rules(report))
                self.assertNotIn(SECRET, json.dumps(report))
                self.assertTrue(protocol.validate_report(report))
        for content in ("null", "[]"):
            self.definition.write_text(content, encoding="utf-8")
            report = self.plan()
            self.assertIn("workflow.root", self.rules(report))
            self.assertEqual(1, report["exitCode"])

    def test_input_json_errors_never_echo_parser_values(self):
        for content in ('{"token":"' + SECRET, '{"kind":"Stateful","kind":"' + SECRET + '"}',
                        '{"secret":NaN}', '{"secret":Infinity}', '{"secret":1e9999}',
                        '[["' + SECRET + '"]', "\ud800"):
            with self.subTest(content=repr(content)):
                self.definition.write_bytes(content.encode("utf-8", errors="surrogatepass"))
                report = self.plan()
                self.assertEqual(3, report["exitCode"])
                self.assertIn("input.invalidJson", self.rules(report))
                self.assertNotIn(SECRET, json.dumps(report))
                self.assertTrue(protocol.validate_report(report))

    def test_json_byte_depth_and_node_bounds(self):
        for patch, content, rule in (
                (mock.patch.object(testing, "MAX_BYTES", 32), " " * 33, "input.tooLarge"),
                (mock.patch.object(testing, "MAX_DEPTH", 3), '{"a":{"b":{"c":{}}}}', "input.tooDeep"),
                (mock.patch.object(testing, "MAX_NODES", 3), "[1,2,3,4]", "input.tooDeep")):
            with self.subTest(rule=rule), patch:
                self.definition.write_text(content, encoding="utf-8")
                report = self.plan()
                self.assertIn(rule, self.rules(report))
                self.assertEqual(3, report["exitCode"])

    def test_path_arguments_are_sanitized_and_explicit(self):
        for name in (None, "", "..", "a\\b", "a/b", SECRET + "\n", "a" * 129):
            with self.subTest(name=name):
                report = testing.plan_report(str(self.project), name)
                self.assertEqual(3, report["exitCode"])
                self.assertIsNone(report["workflow"]["name"])
                self.assertNotIn(SECRET, json.dumps(report))
        for path in (None, "", "https://host/" + SECRET, "\\\\server\\" + SECRET,
                     "\\\\?\\C:\\" + SECRET, "file:" + SECRET, "NUL"):
            with self.subTest(path=path):
                report = testing.plan_report(path, "Orders")
                self.assertEqual(3, report["exitCode"])
                self.assertNotIn(SECRET, json.dumps(report))
        self.assertEqual(3, self.plan(force=True)["exitCode"])

    def test_no_nested_graph_or_expression_semantics_claim(self):
        doc = _workflow.workflow_json("Stateful")
        doc["definition"]["actions"]["Nested"] = {"type": "Scope", "actions": {SECRET: {"runAfter": {"missing": []}}}}
        doc["definition"]["actions"]["Compose_greeting"]["inputs"] = "@totallyInvalid(" + SECRET + ")"
        self.write("Orders", doc, workflow=True)
        report = self.plan()
        self.assertEqual("passedLimited", report["coverage"]["static"])
        self.assertEqual("notChecked", report["coverage"]["nestedGraphs"])
        self.assertEqual("notChecked", report["coverage"]["expressions"])
        self.assertNotIn(SECRET, json.dumps(report))

    def test_configuration_names_checked_without_values_or_configuration_hashes(self):
        doc = _workflow.workflow_json("Stateful")
        doc["definition"]["actions"]["Compose_greeting"]["inputs"] = {
            "one": "@appsetting('SECRET_SETTING')", "two": "@parameters('SECRET_PARAMETER')"}
        doc["definition"]["actions"]["Managed"] = {
            "type": "ApiConnection", "inputs": {"host": {"connection": {"referenceName": "SECRET_CONNECTION"}}}}
        self.write("Orders", doc, workflow=True)
        self.write("local.settings.json", {"IsEncrypted": False, "Values": {"SECRET_SETTING": SECRET}})
        self.write("parameters.json", {"SECRET_PARAMETER": {"value": SECRET}})
        self.write("connections.json", {"managedApiConnections": {"SECRET_CONNECTION": {"authentication": SECRET}}})
        report = self.plan()
        self.assertEqual(0, report["exitCode"])
        self.assertEqual("checkedLiteralDeclarations", report["coverage"]["configurationReferences"])
        text = json.dumps(report)
        for private in (SECRET, "SECRET_SETTING", "SECRET_PARAMETER", "SECRET_CONNECTION"):
            self.assertNotIn(private, text)
        for item in report["inputs"]:
            if item["role"] in ("settings", "parameters", "connections", "host"):
                self.assertIsNone(item["sha256"])
        self.write("parameters.json", {})
        invalid = self.plan()
        self.assertEqual(1, invalid["exitCode"])
        self.assertIn("reference.missing", self.rules(invalid))
        self.assertTrue(protocol.validate_report(invalid))
        self.assertEqual(0, testing.results_report(self.save(invalid))["exitCode"])

    def test_default_parameter_declarations_do_not_require_generated_configuration(self):
        doc = _workflow.workflow_json("Stateful")
        doc["definition"]["parameters"] = {"DEFAULT": {"type": "string", "defaultValue": SECRET}}
        doc["definition"]["actions"]["Compose_greeting"]["inputs"] = "@parameters('DEFAULT')"
        self.write("Orders", doc, workflow=True)
        report = self.plan()
        self.assertEqual(0, report["exitCode"])
        self.assertNotIn(SECRET, json.dumps(report))
        self.assertFalse((self.project / "parameters.json").exists())
        self.write("parameters.json", {})
        self.assertEqual(0, self.plan()["exitCode"])

    def test_business_payload_connection_names_are_not_connection_declarations(self):
        doc = _workflow.workflow_json("Stateful")
        doc["definition"]["actions"]["Compose_greeting"]["inputs"] = {
            "referenceName": SECRET, "connectionName": SECRET}
        self.write("Orders", doc, workflow=True)
        self.assertEqual(0, self.plan()["exitCode"])
        self.assertFalse((self.project / "connections.json").exists())

    def test_duplicate_historical_change_finding_does_not_hide_current_drift(self):
        source = self.plan()
        source["inputs"][1]["stable"] = False
        source["findings"].append(protocol.finding("input.changed", "workflow"))
        protocol.finalize(source)
        filename = self.save(source)
        data = self.definition.read_bytes()
        original = testing._read
        reads = []

        def drifting(path):
            if path == str(self.definition):
                reads.append(path)
                return data if len(reads) == 1 else b"{}"
            return original(path)
        with mock.patch.object(testing, "_read", side_effect=drifting):
            report = testing.results_report(filename, str(self.definition))
        self.assertEqual(5, report["exitCode"])
        self.assertEqual("changed", report["inspection"]["workflowIdentity"])

    def test_reference_errors_and_dynamic_refs_are_not_empty_defaults(self):
        doc = _workflow.workflow_json("Stateful")
        doc["definition"]["actions"]["Compose_greeting"]["inputs"] = "@appsetting('MISSING')"
        self.write("Orders", doc, workflow=True)
        self.assertEqual(3, self.plan()["exitCode"])
        self.write("local.settings.json", {"IsEncrypted": True, "Values": SECRET})
        report = self.plan()
        self.assertIn("reference.dynamic", self.rules(report))
        self.assertEqual(0, report["exitCode"])
        self.write("local.settings.json", {"IsEncrypted": False, "Values": []})
        self.assertIn("reference.shape", self.rules(self.plan()))
        doc["definition"]["actions"]["Compose_greeting"]["inputs"] = "@parameters(concat('" + SECRET + "'))"
        self.write("Orders", doc, workflow=True)
        self.assertIn("reference.dynamic", self.rules(self.plan()))

    def test_csproj_literal_metadata_cannot_clear_policy(self):
        for extra in ("", '<Approved>true</Approved><SdkLicenseAccepted>true</SdkLicenseAccepted>'):
            with self.subTest(extra=extra):
                self.test_project.write_text(XML.replace("</PropertyGroup>", extra + "</PropertyGroup>"), encoding="utf-8")
                report = self.plan(test_project=str(self.test_project))
                self.assertEqual(0, report["exitCode"])
                self.assert_gated(report)
                self.assertTrue(protocol.validate_report(report))

    def test_csproj_dynamic_metadata_and_imports_are_unknown_never_followed(self):
        variants = (
            XML.replace('net8.0', "$(Secret_" + SECRET + ")"),
            XML.replace('Version="1.0.3"', 'Version="1.0.*"'),
            XML.replace('<PropertyGroup>', '<PropertyGroup Condition="' + SECRET + '">'),
            XML.replace("</Project>", '<Import Project="https://host/' + SECRET + '"/></Project>'),
            XML.replace("</Project>", '<Target Name="Build"><Exec Command="' + SECRET + '"/></Target></Project>'),
            XML.replace("<TargetFramework>net8.0</TargetFramework>", "<TargetFrameworks>net8.0;net10.0</TargetFrameworks>"),
        )
        for content in variants:
            with self.subTest(content=content):
                self.test_project.write_text(content, encoding="utf-8")
                report = self.plan(test_project=str(self.test_project))
                self.assertIsNone(report["dependencies"]["declaredSdkVersion"])
                self.assertIn("testProject.metadata", self.rules(report))
                self.assertNotIn(SECRET, json.dumps(report))
                self.assert_gated(report)

    def test_csproj_malformed_entities_encoding_and_bounds(self):
        for content in (
                '<!DOCTYPE Project [<!ENTITY x SYSTEM "file:///' + SECRET + '">]><Project>&x;</Project>',
                "<Project>" + SECRET, "<notProject/>", "<Project>" * 60 + "</Project>" * 60):
            with self.subTest(content=content):
                self.test_project.write_text(content, encoding="utf-8")
                report = self.plan(test_project=str(self.test_project))
                self.assertEqual(3, report["exitCode"])
                self.assertIn("testProject.invalidXml", self.rules(report))
                self.assertEqual("testProject", next(
                    row["source"] for row in report["findings"] if row["rule"] == "testProject.invalidXml"))
                self.assertNotIn(SECRET, json.dumps(report))
        self.test_project.write_bytes(XML.encode("utf-16"))
        self.assertEqual(3, self.plan(test_project=str(self.test_project))["exitCode"])

    def test_changed_or_removed_input_is_stale_before_publication(self):
        original = testing._test_project
        for remove in (False, True):
            self.write("Orders", _workflow.workflow_json("Stateful"), workflow=True)

            def change(report, data):
                original(report, data)
                if remove:
                    self.definition.unlink()
                else:
                    self.definition.write_text("{}", encoding="utf-8")
            with self.subTest(remove=remove), mock.patch.object(testing, "_test_project", side_effect=change):
                report = self.plan(test_project=str(self.test_project), report_path=str(self.result_file), force=True)
                self.assertEqual(5, report["exitCode"])
                self.assertFalse(next(item for item in report["inputs"] if item["role"] == "workflow")["stable"])
                self.assertTrue(protocol.validate_report(report))
                self.assertEqual(report, json.loads(self.result_file.read_text()))

    def test_save_blocked_invalid_reports_and_overwrite_guards(self):
        report = self.plan(report_path=str(self.result_file))
        self.assertEqual(report, json.loads(self.result_file.read_text()))
        original = self.result_file.read_bytes()
        self.definition.write_text("{}", encoding="utf-8")
        denied = self.plan(report_path=str(self.result_file))
        self.assertEqual(6, denied["exitCode"])
        self.assertEqual(original, self.result_file.read_bytes())
        updated = self.plan(report_path=str(self.result_file), force=True)
        self.assertEqual(1, updated["exitCode"])
        self.assertEqual(updated, json.loads(self.result_file.read_text()))

    def test_report_destination_never_overwrites_inputs_or_creates_directories(self):
        before = self.definition.read_bytes()
        for target in (self.definition, self.host, self.project, self.root / "missing" / "report.json",
                       self.root / "local.settings.json", self.root / "report.txt"):
            with self.subTest(target=target):
                self.assertEqual(6, self.plan(report_path=str(target), force=True)["exitCode"])
        self.assertEqual(before, self.definition.read_bytes())
        self.assertFalse((self.root / "missing").exists())
        with mock.patch.object(os.path, "samefile", return_value=True):
            self.result_file.write_text("original", encoding="utf-8")
            self.assertEqual(6, self.plan(report_path=str(self.result_file), force=True)["exitCode"])
            self.assertEqual("original", self.result_file.read_text())

    def test_atomic_publication_failure_preserves_original_and_cleans_temporary(self):
        self.result_file.write_text("original", encoding="utf-8")
        with mock.patch.object(testing.os, "replace", side_effect=PermissionError(SECRET)):
            report = self.plan(report_path=str(self.result_file), force=True)
        self.assertEqual(6, report["exitCode"])
        self.assertEqual("original", self.result_file.read_text())
        self.assertEqual([], list(self.root.glob(".logicapp-test-*")))
        self.assertNotIn(SECRET, json.dumps(report))
        with mock.patch.object(testing.os, "link", side_effect=FileExistsError(SECRET)):
            self.result_file.unlink()
            report = self.plan(report_path=str(self.result_file))
        self.assertEqual(6, report["exitCode"])
        self.assertEqual([], list(self.root.glob(".logicapp-test-*")))

    def test_publication_fsync_failure_preserves_destination_and_cleans_temporary(self):
        self.result_file.write_bytes(b"original")
        with mock.patch.object(testing.os, "fsync", side_effect=OSError(SECRET)):
            report = self.plan(report_path=str(self.result_file), force=True)
        self.assertEqual(6, report["exitCode"])
        self.assertEqual(b"original", self.result_file.read_bytes())
        self.assertEqual([], list(self.root.glob(".logicapp-test-*")))
        self.assertNotIn(SECRET, json.dumps(report))

    def test_competing_publication_file_is_never_overwritten_without_force(self):
        original_link = testing.os.link

        def interleaved_link(source, destination):
            Path(destination).write_bytes(b"other writer")
            return original_link(source, destination)

        with mock.patch.object(testing.os, "link", side_effect=interleaved_link):
            report = self.plan(report_path=str(self.result_file))
        self.assertEqual(6, report["exitCode"])
        self.assertEqual(b"other writer", self.result_file.read_bytes())
        self.assertEqual([], list(self.root.glob(".logicapp-test-*")))

    def test_post_publication_cleanup_failure_reports_possibly_published_artifact(self):
        original_unlink = testing.os.unlink

        def fail_temporary_cleanup(path, *args, **kwargs):
            if Path(path).name.startswith(".logicapp-test-"):
                raise OSError(SECRET)
            return original_unlink(path, *args, **kwargs)

        with mock.patch.object(testing.os, "unlink", side_effect=fail_temporary_cleanup):
            report = self.plan(report_path=str(self.result_file))
        self.assertEqual(6, report["exitCode"])
        self.assertIn("destination may already exist", next(
            row["message"] for row in report["findings"] if row["rule"] == "report.publication"))
        published = json.loads(self.result_file.read_bytes())
        self.assertTrue(protocol.validate_report(published))
        self.assertEqual(0, published["exitCode"])
        self.assertEqual("notExecuted", published["executionState"])
        self.assertEqual(1, len(list(self.root.glob(".logicapp-test-*"))))
        self.assertNotIn(SECRET, json.dumps(report))

    def test_symbolic_links_and_reparse_components_are_not_inspected_or_written(self):
        with mock.patch.object(testing.os, "lstat", return_value=SimpleNamespace(st_mode=stat_mode(),
                                                                                 st_file_attributes=0x400)):
            self.assertEqual(3, self.plan()["exitCode"])
            report = testing.results_report(str(self.result_file))
            self.assertEqual(3, report["exitCode"])
        with mock.patch.object(testing.os.path, "lexists", return_value=True), \
                mock.patch.object(testing.os, "lstat", return_value=SimpleNamespace(st_mode=0o120777)):
            self.assertEqual(3, self.plan()["exitCode"])

    def test_result_inspection_is_successful_read_not_tests_passed(self):
        source = self.plan()
        report = testing.results_report(self.save(source))
        self.assertEqual(0, report["exitCode"])
        self.assertEqual("inspected", report["outcome"])
        self.assertEqual("inspection", report["phase"])
        self.assertEqual(0, report["inspection"]["sourceExitCode"])
        self.assertEqual("planned", report["inspection"]["sourceOutcome"])
        self.assertEqual("planning", report["exitPolicy"])
        self.assertEqual("notAttested", report["inspection"]["authenticity"])
        self.assertEqual("notChecked", report["inspection"]["workflowIdentity"])
        self.assertEqual(source["findings"], report["findings"])
        self.assert_gated(report)
        self.assertNotEqual(source["invocationId"], report["invocationId"])

    def test_inspecting_authoring_or_input_failure_does_not_reclassify_as_test_failure(self):
        for content in ("{}", SECRET):
            with self.subTest(content=content):
                self.definition.write_text(content, encoding="utf-8")
                source = self.plan()
                result = testing.results_report(self.save(source))
                self.assertEqual(0, result["exitCode"])
                self.assertEqual(source["exitCode"], result["inspection"]["sourceExitCode"])
                self.assert_gated(result)

    def test_explicit_identity_check_matches_changes_and_missing_workflow(self):
        filename = self.save()
        result = testing.results_report(filename, str(self.definition))
        self.assertEqual("matches", result["inspection"]["workflowIdentity"])
        self.assertEqual(0, result["exitCode"])
        self.definition.write_text("{}", encoding="utf-8")
        result = testing.results_report(filename, str(self.definition))
        self.assertEqual("changed", result["inspection"]["workflowIdentity"])
        self.assertEqual(5, result["exitCode"])
        self.definition.unlink()
        self.assertEqual(3, testing.results_report(filename, str(self.definition))["exitCode"])

    def test_results_never_follow_embedded_paths_or_accept_native_verdicts(self):
        for payload in (
                {"schemaVersion": "1.0", "sdkVersion": "1.0.3", "outcome": "passed", "path": "https://" + SECRET},
                {"TestResults": {"passed": 1}}, {"path": "..\\" + SECRET}, [],
                {"reportType": "logicapp-test-foundation", "schemaVersion": "2.0"}):
            self.result_file.write_text(json.dumps(payload), encoding="utf-8")
            report = testing.results_report(str(self.result_file))
            self.assertEqual(3, report["exitCode"])
            self.assertIn("report.invalid", self.rules(report))
            self.assertNotIn(SECRET, json.dumps(report))

    def test_protocol_tampering_types_enums_counts_provenance_and_relationships(self):
        source = self.plan(test_project=str(self.test_project))
        mutations = (
            lambda obj: obj.update(schemaVersion="3.0"),
            lambda obj: obj.update(invocationId=SECRET),
            lambda obj: obj.update(phase="execute"),
            lambda obj: obj.update(executionState="completed"),
            lambda obj: obj["summary"].update(executed=1, passed=1),
            lambda obj: obj["summary"].update(executed=False),
            lambda obj: obj["summary"].update(extra=SECRET),
            lambda obj: obj.update(exitCode=True),
            lambda obj: obj["gates"].update(sdkAdoption="accepted"),
            lambda obj: obj["provenance"].update(producer="nativeSDK"),
            lambda obj: obj["workflow"].update(definitionHash="sha256:" + "a" * 64),
            lambda obj: obj["inputs"].append(copy.deepcopy(obj["inputs"][0])),
            lambda obj: obj["inputs"][0].update(sha256="sha256:" + "a" * 64),
            lambda obj: obj["inputs"][0].update(stable=False),
            lambda obj: obj["inputs"][1].update(sha256=None),
            lambda obj: obj["workflow"].update(name=None),
            lambda obj: obj["findings"][0].update(message=SECRET),
            lambda obj: obj["findings"][0].update(jsonPointer="/" + SECRET),
            lambda obj: obj["findings"].clear(),
            lambda obj: obj["dependencies"].update(installedSdkVersion="1.0.3"),
            lambda obj: obj["dependencies"].update(declaredSdkVersion=SECRET),
            lambda obj: obj.update(artifactPath="..\\" + SECRET),
            lambda obj: obj["workflow"].update(kind=[]),
            lambda obj: obj["inputs"][0].update(role=[]),
        )
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                candidate = copy.deepcopy(source)
                mutate(candidate)
                self.assertFalse(protocol.validate_report(candidate))
                report = testing.results_report(self.save(candidate))
                self.assertEqual(3, report["exitCode"])
                self.assertNotIn(SECRET, json.dumps(report))

    def test_result_duplicate_nonfinite_depth_and_read_failures(self):
        for content in ('{"schemaVersion":"1.0","schemaVersion":"1.0"}', '{"secret":NaN}',
                        "<TestResults>" + SECRET, "[" * 60 + "]" * 60):
            self.result_file.write_text(content, encoding="utf-8")
            self.assertEqual(3, testing.results_report(str(self.result_file))["exitCode"])
        with mock.patch("builtins.open", side_effect=PermissionError(SECRET)):
            report = testing.results_report(str(self.result_file))
            self.assertEqual(3, report["exitCode"])
            self.assertNotIn(SECRET, json.dumps(report))

    def test_report_changed_during_inspection_is_not_accepted(self):
        source = json.dumps(self.plan()).encode("utf-8")
        with mock.patch.object(testing, "_read", side_effect=[source, b"{}"]):
            report = testing.results_report(str(self.result_file))
        self.assertEqual(5, report["exitCode"])

    def test_formatter_and_event_handlers_clean_up_on_success_and_failure(self):
        handlers = {}
        cli = SimpleNamespace(
            register_event=lambda key, func: handlers.setdefault(key, []).append(func),
            unregister_event=lambda key, func: handlers[key].remove(func))
        cmd = SimpleNamespace(cli_ctx=cli)
        result = custom.test_plan(cmd, str(self.project), "Orders", strict=True)
        self.assertEqual(4, result["exitCode"])
        rows = protocol.table_format(result)
        self.assertEqual("notExecuted", rows[0]["Execution"])
        with self.assertRaises(SystemExit) as raised:
            handlers[EVENT_CLI_SUCCESSFUL_EXECUTE][0](cli)
        self.assertEqual(4, raised.exception.code)
        self.assertTrue(all(not value for value in handlers.values()))
        custom.test_plan(cmd, str(self.project), "Orders", strict=True)
        handlers[EVENT_CLI_POST_EXECUTE][0](cli)
        self.assertTrue(all(not value for value in handlers.values()))
        result = custom.test_plan(cmd, str(self.project), "Orders")
        self.assertEqual(0, result["exitCode"])
        self.assertTrue(all(not value for value in handlers.values()))
        custom.test_results_show(cmd, self.save())
        self.assertTrue(all(not value for value in handlers.values()))


def stat_mode():
    return 0o100600
