# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Exercise the actual Azure CLI parser and formatter with isolated source loading."""

import contextlib
import copy
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import unittest
from unittest import mock

from azure.cli.core import get_default_cli, util
from azure.cli.core import extension
from azure.cli.core.extension import DevExtension

from azext_logicapp import _context, _run_execution, _runtime_doctor, _workflow, custom


PRIVATE = "private-provider-value-must-not-appear"


class CliContractRegressions(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.project = self.root / "App"
        self.definition = self.project / "Orders" / "workflow.json"
        self.definition.parent.mkdir(parents=True)
        self.definition.write_text(json.dumps(_workflow.workflow_json("Stateful")), encoding="utf-8")
        (self.project / "host.json").write_text(json.dumps(_workflow.HOST_JSON), encoding="utf-8")
        self.report_file = self.root / "report.json"
        source = Path(__file__).resolve().parents[3]
        config = self.root / "cli-config"
        config.mkdir()
        patches = [
            mock.patch.dict(os.environ, {"AZURE_CONFIG_DIR": str(config),
                                         "AZURE_EXTENSION_DIR": str(self.root / "extensions"),
                                         "AZURE_CORE_COLLECT_TELEMETRY": "0"}),
            mock.patch.object(extension, "get_extensions",
                              return_value=[DevExtension("logicapp", str(source))]),
            mock.patch.object(util, "handle_version_update"),
            mock.patch("azure.cli.core.parser.CommandRecommender.provide_recommendations", return_value=[]),
            mock.patch.object(util, "send_raw_request", side_effect=AssertionError("Unexpected Azure request")),
            mock.patch("requests.Session.send", side_effect=AssertionError("Unexpected network request")),
            mock.patch.object(socket, "create_connection", side_effect=AssertionError("Unexpected network probe")),
            mock.patch.object(subprocess, "Popen", side_effect=AssertionError("Unexpected process execution")),
            mock.patch.object(_context, "get_context", side_effect=AssertionError("Unexpected saved target")),
        ]
        for patcher in patches:
            patcher.start()
            self.addCleanup(patcher.stop)
        self.cli = get_default_cli()

    def invoke(self, args, expected=0, output="json", query=None):
        stdout, stderr = io.StringIO(), io.StringIO()
        arguments = args + ["--output", output]
        if query:
            arguments += ["--query", query]
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                code = self.cli.invoke(arguments, out_file=stdout)
            except SystemExit as error:
                code = error.code
        text = stdout.getvalue()
        detail = stderr.getvalue() + str(getattr(self.cli.result, "error", "") or "")
        self.assertEqual(expected, code, (args, text, detail))
        self.assertNotIn(PRIVATE, text + detail)
        value = json.loads(text) if output == "json" and text.strip() else None
        return value, text

    def plan(self, *extra):
        return ["logicapp", "test", "plan", "--path", str(self.project),
                "--workflow", "Orders", *extra]

    def test_foundation_json_query_table_and_all_diagnostic_exit_categories(self):
        report, _ = self.invoke(self.plan("--report-path", str(self.report_file)), expected=4)
        self.assertEqual("notExecuted", report["executionState"])
        self.assertEqual(0, report["summary"]["executed"])
        value, _ = self.invoke(self.plan(), expected=4, query="executionState")
        self.assertEqual("notExecuted", value)
        _, table = self.invoke(self.plan(), expected=4, output="table")
        self.assertIn("sdk.policy", table)
        self.assertIn("notExecuted", table)
        show = ["logicapp", "test", "results", "show", "--result-file", str(self.report_file)]
        inspected, _ = self.invoke(show)
        self.assertEqual(4, inspected["inspection"]["sourceExitCode"])
        self.assertEqual("notExecuted", inspected["businessTests"])
        self.definition.write_text("{}", encoding="utf-8")
        stale, _ = self.invoke(show + ["--workflow-file", str(self.definition)], expected=5)
        self.assertEqual("changed", stale["inspection"]["workflowIdentity"])
        authored, _ = self.invoke(self.plan(), expected=1)
        self.assertEqual("authoringInvalid", authored["outcome"])
        self.definition.write_text('{"private":"' + PRIVATE, encoding="utf-8")
        invalid, _ = self.invoke(self.plan(), expected=3)
        self.assertEqual("inputError", invalid["outcome"])
        publication, _ = self.invoke(self.plan("--report-path", str(self.root / "missing" / "plan.json")),
                                     expected=6)
        self.assertEqual("publicationError", publication["outcome"])
        self.assertFalse((self.root / "missing").exists())
        inspected, _ = self.invoke(show)
        self.assertEqual(0, inspected["exitCode"])

    def test_required_and_forbidden_arguments_do_not_execute_business_tests(self):
        for args in (
                ["logicapp", "test", "plan", "--path", str(self.project)],
                self.plan("--yes"),
                ["logicapp", "test", "results", "show"],
                ["logicapp", "test", "run"],
                ["logicapp", "test", "prepare"],
                ["logicapp", "run", "wait", "--workflow", "Orders", "--local"],
                ["logicapp", "run", "cancel", "--run-id", "source", "--local"],
                ["logicapp", "run", "resubmit", "--workflow", "Orders", "--run-id", "source", "--force"],
        ):
            with self.subTest(args=args):
                self.invoke(args, expected=2)

    def test_execution_report_formatting_and_exit_cleanup_across_invocations(self):
        client = object()
        with mock.patch.object(custom, "_client_from_target", return_value=(client, {})):
            for code, outcome in ((0, "completed"), (1, "readFailed"),
                                  (2, "waitTimedOut"), (4, "terminalNotExpected")):
                report = _run_execution._report("Orders", "source", "wait")
                report.update(exitCode=code, outcome=outcome, status="Running", action="observe")
                with self.subTest(code=code), \
                        mock.patch.object(_run_execution, "wait_run", return_value=report) as wait:
                    args = ["logicapp", "run", "wait", "--workflow", "Orders", "--run-id", "source",
                            "--local", "--timeout", "7", "--interval", "2"]
                    result, _ = self.invoke(args, expected=code)
                    self.assertEqual(outcome, result["outcome"])
                    wait.assert_called_once_with(client, "Orders", "source", 7, 2)
                    value, _ = self.invoke(args, expected=code, query="exitCode")
                    self.assertEqual(code, value)
                    _, table = self.invoke(args, expected=code, output="table")
                    self.assertIn(outcome, table)
        inspected, _ = self.invoke(self.plan("--report-path", str(self.report_file)), expected=4)
        self.assertEqual("notExecuted", inspected["executionState"])
        self.invoke(["logicapp", "test", "results", "show", "--result-file", str(self.report_file)])

    def test_cancel_resubmit_boolean_flags_history_and_defaults_reach_real_wrappers(self):
        client = object()
        report = _run_execution._report("Orders", "source", "cancel")
        report.update(outcome="cancellationRequested", action="cancel", requestAcknowledged=True)
        with mock.patch.object(custom, "_client_from_target", return_value=(client, {})), \
                mock.patch.object(_run_execution, "cancel_run", return_value=report) as cancel:
            self.invoke(["logicapp", "run", "cancel", "--workflow", "Orders", "--run-id", "source",
                         "--local", "--yes", "--wait", "--timeout", "7", "--interval", "2"])
            cancel.assert_called_once_with(client, "Orders", "source", True, True, 7, 2)
        report = copy.deepcopy(report)
        report.update(operation="resubmit", outcome="resubmitted", action="resubmit", newRunId="new-run")
        with mock.patch.object(custom, "_client_from_target", return_value=(client, {})), \
                mock.patch.object(_run_execution, "resubmit_run", return_value=report) as resubmit:
            result, _ = self.invoke(["logicapp", "run", "resubmit", "--workflow", "Orders",
                                     "--run-id", "source", "--local", "--yes",
                                     "--trigger-history-id", "history"])
            resubmit.assert_called_once_with(client, "Orders", "source", True, "history")
            self.assertEqual("new-run", result["newRunId"])
        report = _run_execution._report("Orders", "source", "wait")
        with mock.patch.object(custom, "_client_from_target", return_value=(client, {})), \
                mock.patch.object(_run_execution, "wait_run", return_value=report) as wait:
            self.invoke(["logicapp", "run", "wait", "--workflow", "Orders",
                         "--run-id", "source", "--local"])
            wait.assert_called_once_with(client, "Orders", "source", 300, 5)

    def test_failed_wait_then_metadata_inspection_has_independent_exits_and_query_output(self):
        reason = {"code": "InvalidTemplate", "message": "The template language function 'int' cannot convert the value."}
        action = {"name": "Convert_amount", "properties": {
            "status": "Failed", "code": "BadRequest", "error": reason,
            "inputsLink": {"uri": "https://example.invalid/input?sig=" + PRIVATE}}}
        skipped = {"name": "After_success", "properties": {"status": "Skipped", "code": "ActionSkipped"}}
        client = mock.Mock()
        client.list.return_value = {"value": [skipped, action], "nextContinuationToken": None}
        report = _run_execution._report("Orders", "source", "wait")
        report.update(exitCode=4, status="Failed", outcome="terminalNotExpected", terminal=True)
        target = ["--workflow", "Orders", "--run-id", "source", "--local", "--port", "17071"]
        with mock.patch.object(custom, "_client_from_target", return_value=(client, {"kind": "local"})), \
                mock.patch.object(_run_execution, "wait_run", return_value=report):
            waited, _ = self.invoke(["logicapp", "run", "wait", *target], expected=4)
            self.assertEqual("Failed", waited["status"])
            client.get.return_value = {"name": "source", "properties": {"status": "Failed"}}
            shown, _ = self.invoke(["logicapp", "run", "show", *target])
            self.assertEqual("Failed", shown["status"])
            failed, _ = self.invoke(["logicapp", "run", "action", "list", *target],
                                   query="value[?status=='Failed'].{action:action,reason:error.message}")
            self.assertEqual([{"action": "Convert_amount", "reason": reason["message"]}], failed)
            _, table = self.invoke(["logicapp", "run", "action", "list", *target], output="table",
                                   query="value[].{action:action,status:status,code:code}")
            self.assertIn("Convert_amount", table)
            self.assertIn("Skipped", table)
            client.get.return_value = action
            shown, _ = self.invoke(["logicapp", "run", "action", "show", *target, "--action", "Convert_amount"])
            self.assertEqual(reason, shown["error"])
            self.assertIsNone(shown["outputsLink"])
            self.invoke(["logicapp", "run", "action", "show-content", *target,
                         "--action", "Convert_amount", "--content", "outputs", "--max-bytes", "4096"], expected=1)
            client.get_raw_url.assert_not_called()

    def test_http_failure_with_null_metadata_error_can_read_recorded_response(self):
        body = {"statusCode": 400, "body": {"error": {
            "code": "DiagnosticDemoRejected", "message": "Diagnostic demo: amount must be positive."}}}
        encoded = json.dumps(body).encode("utf-8")
        action = {"name": "Call_backend", "properties": {
            "status": "Failed", "code": "BadRequest", "error": None,
            "outputsLink": {"uri": "https://example.invalid/output?sig=" + PRIVATE,
                            "contentSize": len(encoded)}}}
        client = mock.Mock()
        client.get.return_value = action
        client.get_raw_url.return_value = {"content": encoded, "headers": {}}
        target = ["--workflow", "Orders", "--run-id", "source", "--action", "Call_backend", "--local"]
        with mock.patch.object(custom, "_client_from_target", return_value=(client, {"kind": "local"})):
            shown, _ = self.invoke(["logicapp", "run", "action", "show", *target])
            self.assertEqual("Failed", shown["status"])
            self.assertIsNone(shown["error"])
            content, _ = self.invoke(["logicapp", "run", "action", "show-content", *target,
                                      "--content", "outputs", "--max-bytes", "4096"])
            self.assertEqual(body, content["body"])
            self.assertFalse(content["truncated"])
            client.get_raw_url.assert_called_once_with(action["properties"]["outputsLink"]["uri"], max_bytes=4096)

    def test_doctor_parser_formatting_diagnostic_exits_and_handler_cleanup(self):
        for code in (2, 1, 0):
            rows = []
            _runtime_doctor._finding(rows, "compatibility", "unknown" if code == 2 else
                                    "fail" if code == 1 else "pass", True, "bounded reason", "review")
            report = {"exitCode": code, "findings": rows, "businessBehavior": "not-tested"}
            with self.subTest(code=code), \
                    mock.patch.object(_runtime_doctor, "doctor_report", return_value=report) as doctor:
                args = ["logicapp", "runtime", "doctor", "--path", str(self.project),
                        "--port", "17071", "--probe-timeout", "3", "--strict"]
                result, _ = self.invoke(args, expected=code)
                self.assertEqual(code, result["exitCode"])
                doctor.assert_called_once_with(str(self.project), None, 17071, 3, True)
                value, _ = self.invoke(args, expected=code, query="businessBehavior")
                self.assertEqual("not-tested", value)
                _, table = self.invoke(args, expected=code, output="table")
                self.assertIn("compatibility", table)
        self.invoke(self.plan("--report-path", str(self.report_file)), expected=4)
        self.invoke(["logicapp", "test", "results", "show", "--result-file", str(self.report_file)])
