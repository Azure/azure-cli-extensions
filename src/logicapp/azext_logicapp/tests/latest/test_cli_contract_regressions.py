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
from azure.cli.core.azclierror import MutuallyExclusiveArgumentError, ResourceNotFoundError
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

    def test_context_create_omitted_port_is_a_plain_default_and_explicit_ports_stay_validated(self):
        storage = mock.patch.object(_context, "store_path", return_value=str(self.root / "contexts.json"))
        storage.start()
        self.addCleanup(storage.stop)
        created, _ = self.invoke(["logicapp", "context", "create", "--name", "default-port",
                                  "--path", str(self.project), "--use"])
        self.assertEqual(7071, created["target"]["port"])
        self.assertIs(type(created["target"]["port"]), int)
        explicit, _ = self.invoke(["logicapp", "context", "create", "--name", "explicit-port",
                                   "--path", str(self.project), "--port", "7079"])
        self.assertEqual(7079, explicit["target"]["port"])
        cloud, _ = self.invoke(["logicapp", "context", "create", "--name", "cloud",
                                "--resource-group", "rg", "--logic-app-name", "app"])
        self.assertIsNone(cloud["target"]["port"])
        before = _context.load_store()
        for value in ("0", "65536"):
            with self.subTest(port=value):
                self.invoke(["logicapp", "context", "create", "--name", "invalid-port",
                             "--path", str(self.project), "--port", value], expected=1)
        self.assertEqual(before, _context.load_store())
        self.assertFalse((self.project / "Tests").exists())

    def test_sdk_create_uses_context_paths_and_plan_remains_read_only(self):
        context = {"name": "development", "target": {"kind": "local", "path": str(self.project), "port": 7071}}
        with mock.patch.object(custom, "get_context", return_value=(context, {})):
            created, _ = self.invoke(["logicapp", "test", "create", "--workflow", "Orders"])
            self.assertEqual("requiresAuthoring", created["scaffoldState"])
            self.assertTrue((self.project / "Tests" / "Orders" / "Workflow.Tests.csproj").is_file())
            plan, _ = self.invoke(["logicapp", "test", "plan", "--workflow", "Orders"])
            self.assertEqual("1.0.3", plan["dependencies"]["declaredSdkVersion"])
            self.assertEqual("notExecuted", plan["executionState"])
            self.invoke(["logicapp", "test", "create", "--workflow", "Orders"], expected=1)

    def test_sdk_run_missing_permissions_formats_json_query_and_table_without_execution(self):
        arguments = ["logicapp", "test", "run", "--path", str(self.project), "--workflow", "Orders"]
        report, _ = self.invoke(arguments, expected=4)
        self.assertEqual("logicapp-sdk-test", report["reportType"])
        self.assertEqual("blocked", report["outcome"])
        self.assertFalse((self.project / "Tests").exists())
        value, _ = self.invoke(arguments, expected=4, query="executionState")
        self.assertEqual("notExecuted", value)
        _, table = self.invoke(arguments, expected=4, output="table")
        self.assertIn("blocked", table)
        self.invoke(arguments + ["--accept-sdk-terms"], expected=4)
        self.invoke(arguments + ["--trust-project"], expected=4)

    def test_foundation_json_query_table_and_all_diagnostic_exit_categories(self):
        report, _ = self.invoke(self.plan("--report-path", str(self.report_file)))
        self.assertEqual("notExecuted", report["executionState"])
        self.assertEqual(0, report["summary"]["executed"])
        self.assertEqual("planned", report["outcome"])
        value, _ = self.invoke(self.plan(), query="executionState")
        self.assertEqual("notExecuted", value)
        _, table = self.invoke(self.plan(), output="table")
        self.assertIn("sdk.policy", table)
        self.assertIn("notExecuted", table)
        strict, _ = self.invoke(self.plan("--strict", "--report-path", str(self.report_file), "--force"), expected=4)
        self.assertEqual("strict", strict["exitPolicy"])
        self.assertEqual("blocked", strict["outcome"])
        value, _ = self.invoke(self.plan("--strict"), expected=4, query="exitCode")
        self.assertEqual(4, value)
        _, table = self.invoke(self.plan("--strict"), expected=4, output="table")
        self.assertIn("blocked", table)
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

    def test_strict_preserves_diagnostic_errors_and_is_only_a_plan_option(self):
        self.definition.write_text("{}", encoding="utf-8")
        self.invoke(self.plan("--strict"), expected=1)
        self.definition.write_text("{", encoding="utf-8")
        self.invoke(self.plan("--strict"), expected=3)
        self.invoke(self.plan("--strict", "--report-path", str(self.root / "absent" / "p.json")), expected=6)
        self.invoke(["logicapp", "test", "results", "show", "--result-file", str(self.report_file), "--strict"],
                    expected=2)

    def test_plan_uses_active_or_named_local_context_without_writing_or_executing(self):
        context = {"name": "development", "target": {"kind": "local", "path": str(self.project), "port": 7071}}
        before = {str(path): path.read_bytes() for path in self.project.rglob("*") if path.is_file()}
        for name in (None, "development"):
            with self.subTest(context=name), \
                    mock.patch.object(custom, "get_context", return_value=(context, {})) as get_context:
                args = ["logicapp", "test", "plan", "--workflow", "Orders"]
                if name:
                    args += ["--context", name]
                report, text = self.invoke(args)
                get_context.assert_called_once_with(name)
                self.assertEqual("planned", report["outcome"])
                self.assertEqual("Stateful", report["workflow"]["kind"])
                self.assertEqual("notExecuted", report["businessTests"])
                self.assertEqual([0, 0, 0], [report["summary"][key] for key in ("executed", "passed", "failed")])
                self.assertEqual("blocked", report["gates"]["sdkRestore"])
                self.assertEqual("blocked", report["gates"]["sdkExecution"])
                self.assertNotIn(str(self.project), text)
        self.assertEqual(before, {str(path): path.read_bytes()
                                  for path in self.project.rglob("*") if path.is_file()})

    def test_plan_explicit_path_bypasses_implicit_context_and_empty_paths_do_not_fall_back(self):
        with mock.patch.object(custom, "get_context", side_effect=AssertionError("Active context consulted")):
            self.invoke(self.plan(), query="executionState")
            for value in ("", " "):
                self.invoke(["logicapp", "test", "plan", "--path", value, "--workflow", "Orders"], expected=1)

    def test_plan_named_context_is_validated_but_explicit_path_selects_project_and_output_base(self):
        other = self.root / "Other"
        (other / "Reports").mkdir(parents=True)
        context = {"name": "development", "target": {"kind": "local", "path": str(other), "port": 7071}}
        (self.project / "Reports").mkdir()
        with mock.patch.object(custom, "get_context", return_value=(context, {})) as get_context:
            report, _ = self.invoke(self.plan("--context", "development",
                                             "--report-path", os.path.join("Reports", "plan.json")))
            get_context.assert_called_once_with("development")
        self.assertEqual("Stateful", report["workflow"]["kind"])
        self.assertEqual(report, json.loads((self.project / "Reports" / "plan.json").read_text()))
        self.assertFalse((other / "Reports" / "plan.json").exists())

    def test_plan_relative_report_uses_context_project_and_preserves_publication_guards(self):
        context = {"name": "development", "target": {"kind": "local", "path": str(self.project), "port": 7071}}
        (self.project / "Reports").mkdir()
        args = ["logicapp", "test", "plan", "--workflow", "Orders", "--strict",
                "--report-path", os.path.join("Reports", "plan.json")]
        with mock.patch.object(custom, "get_context", return_value=(context, {})):
            report, _ = self.invoke(args, expected=4)
            saved = self.project / "Reports" / "plan.json"
            original = saved.read_bytes()
            self.assertEqual(report, json.loads(original))
            self.assertEqual("notExecuted", report["executionState"])
            refused, _ = self.invoke(args, expected=6)
            self.assertEqual("publicationError", refused["outcome"])
            self.assertEqual(original, saved.read_bytes())
            self.invoke(args + ["--force"], expected=4)
            before = self.definition.read_bytes()
            protected, _ = self.invoke(
                ["logicapp", "test", "plan", "--workflow", "Orders", "--force",
                 "--report-path", os.path.join("Orders", "workflow.json")], expected=6)
            self.assertEqual("publicationError", protected["outcome"])
            self.assertEqual(before, self.definition.read_bytes())
            missing = self.project / "Absent" / "plan.json"
            self.invoke(["logicapp", "test", "plan", "--workflow", "Orders",
                         "--report-path", os.path.join("Absent", "plan.json")], expected=6)
            self.assertFalse(missing.parent.exists())

    def test_plan_context_keeps_absolute_report_destination_unchanged(self):
        context = {"name": "development", "target": {"kind": "local", "path": str(self.project), "port": 7071}}
        with mock.patch.object(custom, "get_context", return_value=(context, {})):
            report, _ = self.invoke(["logicapp", "test", "plan", "--workflow", "Orders",
                                     "--report-path", str(self.report_file)])
        self.assertEqual(report, json.loads(self.report_file.read_text()))

    def test_plan_no_context_defaults_to_current_directory_and_keeps_test_project_input_relative_to_cwd(self):
        previous = os.getcwd()
        os.chdir(self.project)
        try:
            with mock.patch.object(custom, "get_context", return_value=(None, {})) as get_context:
                report, _ = self.invoke(["logicapp", "test", "plan", "--workflow", "Orders"])
                get_context.assert_called_once_with(None)
                self.assertEqual("Stateful", report["workflow"]["kind"])
        finally:
            os.chdir(previous)
        test_project = self.root / "Tests.csproj"
        test_project.write_text(
            '<Project><PropertyGroup><TargetFramework>net8.0</TargetFramework></PropertyGroup></Project>',
            encoding="utf-8")
        os.chdir(self.root)
        try:
            with mock.patch.object(custom, "get_context", return_value=(
                    {"target": {"kind": "local", "path": str(self.project)}}, {})):
                report, _ = self.invoke(["logicapp", "test", "plan", "--workflow", "Orders",
                                         "--test-project", "Tests.csproj"])
                self.assertEqual("net8.0", report["dependencies"]["declaredTargetFramework"])
        finally:
            os.chdir(previous)

    def test_plan_cloud_and_missing_named_contexts_never_fall_back_to_a_local_project(self):
        cloud = {"name": "cloud", "target": {"kind": "cloud", "resourceGroup": "rg", "name": "app"}}
        with mock.patch.object(custom, "get_context", return_value=(cloud, {})):
            self.invoke(["logicapp", "test", "plan", "--workflow", "Orders"], expected=1)
            self.invoke(self.plan("--context", "cloud"), expected=1)
            with self.assertRaises(MutuallyExclusiveArgumentError) as caught:
                custom.test_plan(None, workflow="Orders", context="cloud")
            self.assertNotIn("--with-runtime", str(caught.exception))
        with mock.patch.object(custom, "get_context",
                               side_effect=ResourceNotFoundError("Selected context was not found.")):
            self.invoke(["logicapp", "test", "plan", "--context", "missing", "--workflow", "Orders"], expected=3)
            self.invoke(self.plan("--context", "missing"), expected=3)

    @unittest.skipUnless(os.name == "nt", "Windows drive-relative path syntax")
    def test_plan_rejects_drive_relative_reports_instead_of_using_per_drive_current_directory(self):
        self.invoke(self.plan("--report-path", "C:plan.json"), expected=1)

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
                ["logicapp", "run", "resubmit", "--workflow", "Orders", "--run-id", "source"],
                ["logicapp", "run", "resubmit", "--workflow", "Orders", "--action", "Selected"],
                ["logicapp", "run", "resubmit", "--run-id", "source", "--action", "Selected"],
                ["logicapp", "run", "resubmit", "--workflow", "Orders", "--run-id", "source",
                 "--action", "Selected", "--history-name", "history"],
                ["logicapp", "trigger", "history", "resubmit", "--workflow", "Orders", "--trigger", "manual"],
                ["logicapp", "trigger", "history", "resubmit", "--workflow", "Orders", "--history-name", "history"],
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
        inspected, _ = self.invoke(self.plan("--strict", "--report-path", str(self.report_file)), expected=4)
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
        report.update(operation="triggerHistoryResubmit", outcome="accepted", action="resubmitRequested",
                      runId=None, triggerName="manual", triggerHistoryId="history", newRunId="new-run")
        with mock.patch.object(custom, "_client_from_target", return_value=(client, {})), \
                mock.patch.object(_run_execution, "resubmit_trigger_history", return_value=report) as resubmit:
            result, _ = self.invoke(["logicapp", "trigger", "history", "resubmit", "--workflow", "Orders",
                                     "--trigger", "manual", "--local", "--yes", "--history-name", "history"])
            resubmit.assert_called_once_with(client, "Orders", "manual", "history", True)
            self.assertEqual("new-run", result["newRunId"])
        report = _run_execution._report("Orders", "source", "wait")
        with mock.patch.object(custom, "_client_from_target", return_value=(client, {})), \
                mock.patch.object(_run_execution, "wait_run", return_value=report) as wait:
            self.invoke(["logicapp", "run", "wait", "--workflow", "Orders",
                         "--run-id", "source", "--local"])
            wait.assert_called_once_with(client, "Orders", "source", 300, 5)

    def test_action_resubmit_parser_preserves_selected_action_reports_and_exit_formatting(self):
        client = object()
        with mock.patch.object(custom, "_client_from_target", return_value=(client, {})):
            for code, outcome in ((0, "accepted"), (1, "readFailed"), (2, "requestDeadlineExpired")):
                report = _run_execution._report("Orders", "source", "actionResubmit")
                report.update(exitCode=code, outcome=outcome, actionName="Selected", sourceRunId="source",
                              newRunId="new-run" if not code else None, newRunStatus=None)
                with self.subTest(code=code), mock.patch.object(
                        _run_execution, "resubmit_run_action", return_value=report) as resubmit:
                    args = ["logicapp", "run", "resubmit", "--workflow", "Orders", "--run-id", "source",
                            "--action", "Selected", "--local", "--yes"]
                    result, _ = self.invoke(args, expected=code)
                    self.assertEqual("Selected", result["actionName"])
                    resubmit.assert_called_once_with(client, "Orders", "source", "Selected", True)
                    queried, _ = self.invoke(args, expected=code, query="actionName")
                    self.assertEqual("Selected", queried)
                    _, table = self.invoke(args, expected=code, output="table")
                    self.assertIn("Selected", table)

    def test_lifecycle_parser_preserves_omission_saved_port_and_explicit_7071(self):
        selected = {"target": {"kind": "local", "path": str(self.project), "port": 7079}}
        with mock.patch.object(custom, "get_context", return_value=(selected, {})), \
                mock.patch.object(custom, "start_runtime", return_value={"started": True}) as start, \
                mock.patch.object(custom, "show_runtime", return_value={"running": False}) as show, \
                mock.patch.object(custom, "stop_runtime", return_value={"stopped": False}) as stop:
            self.invoke(["logicapp", "runtime", "start"])
            start.assert_called_once_with(mock.ANY, str(self.project), port=7079, background=False,
                                          ready_timeout=30, no_azurite=False)
            self.invoke(["logicapp", "runtime", "show"])
            show.assert_called_once_with(port=7079)
            self.invoke(["logicapp", "runtime", "stop"])
            stop.assert_called_once_with(port=7079, all_records=False)
            self.invoke(["logicapp", "runtime", "start", "--port", "7071"])
            self.assertEqual(str(self.project), start.call_args.args[1])
            self.assertEqual(7071, start.call_args.kwargs["port"])
            self.invoke(["logicapp", "runtime", "show", "--port", "7071"])
            self.assertEqual(7071, show.call_args.kwargs["port"])
            self.invoke(["logicapp", "runtime", "stop", "--all"])
            stop.assert_called_with(port=None, all_records=True)

    def test_cloud_authoring_refusal_and_dual_plane_validation_through_parser(self):
        cloud = {"target": {"kind": "cloud", "resourceGroup": "rg", "logicAppName": "app"}}
        client = mock.Mock()
        client.post_with_receipt.return_value = {"statusCode": 200, "payload": None}
        with mock.patch.object(custom, "get_context", return_value=(cloud, {})), \
                mock.patch.object(custom, "create_workflow_file") as create, \
                mock.patch.object(custom, "create_local_connection") as connection, \
                mock.patch.object(custom, "_read_secret_from_stdin") as secret, \
                mock.patch.object(custom, "build_runtime_client", return_value=client):
            self.invoke(["logicapp", "workflow", "create", "--context", "cloud", "--workflow", "new"], expected=1)
            self.invoke(["logicapp", "connection", "create", "--context", "cloud", "--name", "conn",
                         "--connector", "serviceBus", "--secret", "setting"], expected=1)
            create.assert_not_called()
            connection.assert_not_called()
            secret.assert_not_called()
            result, _ = self.invoke(["logicapp", "workflow", "validate", "--context", "cloud",
                                     "--path", str(self.project), "--workflow", "Orders", "--with-runtime"])
            self.assertTrue(result["valid"])
            self.assertTrue(result["coverage"]["checks"]["runtimeTemplate"])
            client.post_with_receipt.assert_called_once()

    def test_replacement_set_parser_and_retired_update_surface(self):
        with mock.patch.object(custom, "_client_from_target", return_value=(object(), {})), \
                mock.patch.object(custom._workflow_mutation, "set_workflow",
                                  return_value={"action": "updated"}) as replace:
            result, _ = self.invoke(["logicapp", "workflow", "set", "--workflow", "Orders",
                                     "--file", str(self.definition), "--local", "--allow-non-atomic", "--yes"])
            self.assertEqual("updated", result["action"])
            self.assertEqual((str(self.definition), None, True, True), replace.call_args.args[2:])
            self.invoke(["logicapp", "workflow", "update", "--workflow", "Orders",
                         "--file", str(self.definition), "--local"], expected=2)

    def test_managed_create_names_and_legacy_compatibility_reach_same_guarded_handler(self):
        with mock.patch.object(custom._managed_connection, "create_managed_connection",
                               return_value={"created": True}) as create:
            canonical = ["logicapp", "connection", "managed", "create", "-g", "rg",
                         "--logic-app-name", "app", "--name", "conn", "--connector", "azureblob",
                         "--location", "eastus", "--auth-mode", "managed-identity"]
            self.invoke(canonical)
            self.assertEqual(("rg", "app", "conn", "azureblob", "eastus", "managed-identity"),
                             create.call_args.args[1:])
            self.invoke(["logicapp", "connection", "create", "--managed-api", "-g", "rg",
                         "--name", "app", "--connection-name", "conn", "--connector", "azureblob",
                         "--location", "eastus", "--auth-mode", "managed-identity"])
            self.assertEqual(("rg", "app", "conn", "azureblob", "eastus", "managed-identity"),
                             create.call_args.args[1:])
            count = create.call_count
            missing_app = canonical[:]
            index = missing_app.index("--logic-app-name")
            del missing_app[index:index + 2]
            with mock.patch.object(custom, "get_context", return_value=(None, {})):
                self.invoke(missing_app, expected=1)
            self.invoke(canonical + ["--connection-name", "other"], expected=2)
            self.assertEqual(count, create.call_count)

    def test_local_managed_create_parser_accepts_project_scope_and_global_subscription_override(self):
        subscription = "22222222-2222-2222-2222-222222222222"

        def capture(cmd, *args, **kwargs):
            return {"scope": cmd.cli_ctx.data.get("subscription_id"),
                    "path": kwargs["local_project"], "group": args[0], "location": args[4]}

        command = ["logicapp", "connection", "managed", "create", "--name", "conn",
                   "--connector", "office365", "--auth-mode", "oauth", "--path", str(self.project)]
        with mock.patch.object(custom._managed_connection, "create_managed_connection", side_effect=capture), \
                mock.patch("azure.cli.core._profile.Profile.get_subscription",
                           return_value={"id": subscription, "name": "Override", "tenantId": "tenant"}), \
                mock.patch("azure.cli.core._profile.Profile.load_cached_subscriptions",
                           return_value=[{"id": subscription, "name": "Override", "tenantId": "tenant"}]):
            result, _ = self.invoke(command + ["--subscription", subscription, "-g", "override", "-l", "westus"])
            self.assertEqual(subscription, result["scope"])
            self.assertEqual(str(self.project), result["path"])
            self.assertEqual("override", result["group"])
            self.assertEqual("westus", result["location"])
            result, _ = self.invoke(command + ["--subscription", "Override"])
            self.assertEqual(subscription, result["scope"])
            result, _ = self.invoke(command)
            self.assertIsNone(result["scope"])
            self.assertIsNone(result["group"])
            self.assertIsNone(result["location"])

    def test_managed_create_accepts_named_and_active_contexts_without_changing_context_schema(self):
        command = ["logicapp", "connection", "managed", "create", "--name", "conn",
                   "--connector", "office365", "--auth-mode", "oauth"]
        with mock.patch.object(custom._managed_connection, "create_managed_connection", return_value={}) as create:
            local = {"target": {"kind": "local", "path": str(self.project), "port": 7071}}
            with mock.patch.object(custom, "get_context", return_value=(local, {})):
                self.invoke(command + ["--context", "dev"])
                self.assertEqual(str(self.project), create.call_args.kwargs["local_project"])
                self.invoke(command)
                self.assertEqual(str(self.project), create.call_args.kwargs["local_project"])
                self.invoke(command + ["--context", "dev", "--logic-app-name", "app"], expected=1)
                self.invoke(command + ["--context", "dev", "--path", ""], expected=1)
            cloud = {"target": {"kind": "cloud", "resourceGroup": "rg", "logicAppName": "app"}}
            with mock.patch.object(custom, "get_context", return_value=(cloud, {})):
                self.invoke(command + ["--context", "prod", "-l", "eastus"])
                self.assertEqual(("rg", "app", "conn", "office365", "eastus", "oauth"),
                                 create.call_args.args[1:])
                self.assertNotIn("local_project", create.call_args.kwargs)
                self.invoke(command + ["--context", "prod", "--path", str(self.project)], expected=1)

    def test_local_managed_create_parser_runs_complete_local_path_without_a_deployed_app(self):
        from azext_logicapp import _local_managed_connection

        self.cli.config.set_value("defaults", "group", "unrelated-default-group")
        subscription = "11111111-1111-1111-1111-111111111111"
        settings_path = self.project / "local.settings.json"
        settings_path.write_text(json.dumps({"IsEncrypted": False, "Values": {
            "WORKFLOWS_SUBSCRIPTION_ID": subscription, "WORKFLOWS_RESOURCE_GROUP_NAME": "rg",
            "WORKFLOWS_LOCATION_NAME": "eastus"}}), encoding="utf-8")
        resource = None
        calls = []

        def arm(_cmd, method, resource_id, body=None, _sender=None):
            nonlocal resource
            calls.append((method, resource_id))
            self.assertNotIn("/sites/", resource_id)
            self.assertNotIn("/accessPolicies", resource_id)
            if resource_id.endswith("/listConnectionKeys"):
                return {"connectionKey": PRIVATE}
            if method == "PUT":
                resource = copy.deepcopy(body)
                resource["properties"]["connectionRuntimeUrl"] = "https://connector.invalid/runtime"
                return resource
            if resource is None:
                raise ResourceNotFoundError("Not found")
            return resource

        with mock.patch.object(custom._managed_connection, "_arm", side_effect=arm), \
                mock.patch.object(_local_managed_connection, "Profile") as profile, \
                mock.patch.object(_local_managed_connection, "is_tracked_by_git", return_value=False), \
                mock.patch.object(custom._managed_connection, "_resolve_app_principal",
                                  side_effect=AssertionError("Unexpected deployed identity")), \
                mock.patch.object(custom._managed_connection, "_ConnectionsFile",
                                  side_effect=AssertionError("Unexpected remote VFS")):
            profile.return_value.get_subscription.return_value = {"id": subscription}
            result, _ = self.invoke(["logicapp", "connection", "managed", "create", "--name", "conn",
                                     "--connector", "office365", "--auth-mode", "raw", "--path", str(self.project)])
        self.assertIsNone(result["accessPolicy"])
        self.assertEqual(str(self.project), result["localProject"])
        self.assertEqual(["GET", "PUT", "GET", "POST"], [row[0] for row in calls])
        saved = json.loads(settings_path.read_text(encoding="utf-8"))
        self.assertEqual(PRIVATE, saved["Values"]["conn-connectionKey"])
        self.assertNotIn(PRIVATE, (self.project / "connections.json").read_text(encoding="utf-8"))
        self.assertTrue(all("/resourceGroups/rg/" in resource_id for _, resource_id in calls))

    def test_managed_create_configured_group_applies_only_to_explicit_deployed_targets(self):
        self.cli.config.set_value("defaults", "group", "configured-group")
        command = ["logicapp", "connection", "managed", "create", "--name", "conn",
                   "--connector", "office365", "--auth-mode", "raw"]
        with mock.patch.object(custom._managed_connection, "create_managed_connection", return_value={}) as create:
            self.invoke(command + ["--path", str(self.project)])
            self.assertIsNone(create.call_args.args[1])
            self.invoke(command + ["--path", str(self.project), "-g", "configured-group"])
            self.assertEqual("configured-group", create.call_args.args[1])
            local = {"target": {"kind": "local", "path": str(self.project), "port": 7071}}
            with mock.patch.object(custom, "get_context", return_value=(local, {})):
                for target in ([], ["--context", "dev"]):
                    self.invoke(command + target)
                    self.assertIsNone(create.call_args.args[1])
            cloud = {"target": {"kind": "cloud", "resourceGroup": "context-group", "logicAppName": "app"}}
            with mock.patch.object(custom, "get_context", return_value=(cloud, {})):
                for target in ([], ["--context", "prod"]):
                    self.invoke(command + target + ["-l", "eastus"])
                    self.assertEqual("context-group", create.call_args.args[1])
                count = create.call_count
                self.invoke(command + ["--context", "prod", "-g", "configured-group", "-l", "eastus"], expected=1)
                self.assertEqual(count, create.call_count)
            self.invoke(command + ["--logic-app-name", "app", "-l", "eastus"])
            self.assertEqual("configured-group", create.call_args.args[1])

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
        self.invoke(self.plan("--strict", "--report-path", str(self.report_file)), expected=4)
        self.invoke(["logicapp", "test", "results", "show", "--result-file", str(self.report_file)])
