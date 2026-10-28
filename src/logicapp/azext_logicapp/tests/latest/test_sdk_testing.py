# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest import mock
import xml.etree.ElementTree as ET
import zipfile

from azure.cli.core.azclierror import ValidationError

from azext_logicapp import _sdk_testing as sdk, _test_scaffold as scaffold, _testing, _workflow

PRIVATE = "PRIVATE-TEST-PAYLOAD-NEVER-EXPORT"


def native_trx(outcomes, summary=None):
    namespace = sdk.TRX_NAMESPACE
    root = ET.Element(namespace + "TestRun")
    results = ET.SubElement(root, namespace + "Results")
    for index, outcome in enumerate(outcomes):
        row = ET.SubElement(results, namespace + "UnitTestResult",
                            executionId="00000000-0000-0000-0000-{:012d}".format(index + 1), outcome=outcome)
        ET.SubElement(row, namespace + "Output").text = PRIVATE
    overall = ET.SubElement(root, namespace + "ResultSummary",
                            outcome=summary or ("Failed" if "Failed" in outcomes else "Completed"))
    ET.SubElement(overall, namespace + "Counters", total=str(len(outcomes)),
                  executed=str(outcomes.count("Passed") + outcomes.count("Failed")),
                  passed=str(outcomes.count("Passed")), failed=str(outcomes.count("Failed")),
                  notExecuted="0", error="0", timeout="0", aborted="0")
    return ET.tostring(root, encoding="utf-8")


def successful_record():
    report = sdk.new_report()
    report["workflow"].update(name="Orders", kind="Stateful", definitionHash="sha256:" + "a" * 64)
    report["testProjectHash"] = "sha256:" + "b" * 64
    report["dependencies"].update(dotnetVersion="8.0.426", resolution="locked")
    report["permissions"].update(termsAccepted=True, projectTrusted=True)
    report.update(inputStability="unchangedSelectedFiles", executionState="runnerCompleted")
    report["summary"].update(selected=2, executed=2, passed=2)
    report["steps"] = [{"name": name, "started": True, "nativeExitCode": 0}
                       for name in ("toolchain", "build", "test")]
    return sdk.finalize(report)


class SdkTestingTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.app = self.root / "App"
        self.workflow = self.app / "Orders" / "workflow.json"
        self.workflow.parent.mkdir(parents=True)
        self.workflow.write_text(json.dumps(_workflow.workflow_json("Stateful")), encoding="utf-8")
        (self.app / "host.json").write_text(json.dumps(_workflow.HOST_JSON), encoding="utf-8")
        self.project = Path(scaffold.default_project(str(self.app), "Orders"))
        patcher = mock.patch.object(subprocess, "Popen", side_effect=AssertionError("No native code in unit tests"))
        patcher.start()
        self.addCleanup(patcher.stop)

    def create(self):
        return scaffold.create_project(str(self.app), "Orders")

    def run_sdk(self, **kwargs):
        return sdk.run_report(str(self.app), "Orders", accept_sdk_terms=True, trust_project=True, **kwargs)

    def test_scaffold_is_source_only_ignored_unconfigured_and_plan_discoverable(self):
        result = self.create()
        self.assertEqual("requiresAuthoring", result["scaffoldState"])
        self.assertEqual("notExecuted", result["executionState"])
        self.assertFalse(result["restorePerformed"])
        self.assertEqual(6, len(list(self.project.parent.iterdir())))
        code = (self.project.parent / "WorkflowTests.cs").read_text()
        self.assertIn("[Ignore(", code)
        self.assertLess(code.index("Assert.Inconclusive("), code.index("new UnitTestExecutor("))
        xml = self.project.read_text()
        for version in ("[1.0.3]", "[1.165.50]", "[4.0.2]"):
            self.assertIn(version, xml)
        self.assertIn("CopyToOutputDirectory=\"Always\"", xml)
        report = _testing.plan_report(str(self.app), "Orders")
        self.assertEqual("1.0.3", report["dependencies"]["declaredSdkVersion"])
        self.assertEqual("notExecuted", report["executionState"])
        self.assertEqual(0, report["summary"]["executed"])
        self.assertTrue(_testing.protocol.validate_report(report))

    def test_create_never_clobbers_existing_directory_or_changes_definition(self):
        before = self.workflow.read_bytes()
        self.create()
        source = self.project.read_bytes()
        with self.assertRaises(ValidationError):
            self.create()
        self.assertEqual(source, self.project.read_bytes())
        self.assertEqual(before, self.workflow.read_bytes())

    def test_create_refuses_invalid_inputs_and_requires_explicit_multiple_trigger_selection(self):
        self.workflow.write_text('{"definition":{},"kind":"Stateful"}', encoding="utf-8")
        with self.assertRaises(ValidationError):
            self.create()
        self.assertFalse(self.project.parent.exists())
        workflow = _workflow.workflow_json("Stateful")
        triggers = workflow["definition"]["triggers"]
        triggers["second"] = copy.deepcopy(next(iter(triggers.values())))
        self.workflow.write_text(json.dumps(workflow), encoding="utf-8")
        with self.assertRaises(ValidationError):
            self.create()
        scaffold.create_project(str(self.app), "Orders", trigger="second")
        self.assertIn('"second"', (self.project.parent / "WorkflowTests.cs").read_text())

    def test_msbuild_path_literals_do_not_expand_properties_or_globs(self):
        value = scaffold._msbuild_path('..\\$(Injected);@(*)\\name&"%.json')
        self.assertNotIn("$(", value)
        self.assertNotIn("@(", value)
        self.assertIn("%24%28Injected%29%3B", value)
        self.assertIn("&amp;&quot;%25", value)

    def test_missing_permissions_are_read_only_and_cannot_be_replaced_by_a_plan(self):
        before = sorted(str(path) for path in self.root.rglob("*"))
        report = sdk.run_report(str(self.app), "Orders", restore=True)
        self.assertEqual(4, report["exitCode"])
        self.assertEqual({"policy.terms", "policy.trust"}, {row["code"] for row in report["findings"]})
        self.assertEqual(before, sorted(str(path) for path in self.root.rglob("*")))
        self.assertTrue(sdk.validate_report(report))
        self.assertEqual("notExecuted", report["executionState"])

    def test_child_environment_drops_credentials_hooks_and_shared_profiles(self):
        state = str(self.root / "private")
        with mock.patch.dict(os.environ, {
                "AZURE_CLIENT_SECRET": PRIVATE, "ARM_CLIENT_SECRET": PRIVATE,
                "NUGET_PLUGIN_PATHS": PRIVATE, "DOTNET_STARTUP_HOOKS": PRIVATE,
                "MSBUILD_EXE_PATH": PRIVATE, "HOME": PRIVATE, "AZURE_CONFIG_DIR": PRIVATE,
                "HTTPS_PROXY": PRIVATE, "USERPROFILE": PRIVATE}):
            environment = sdk._environment(state)
        self.assertNotIn(PRIVATE, json.dumps(environment))
        self.assertEqual("false", environment["DOTNET_GENERATE_ASPNET_CERTIFICATE"])
        self.assertTrue(environment["NUGET_PACKAGES"].startswith(state))
        self.assertTrue(environment["AZURE_CONFIG_DIR"].startswith(state))

    def fake_native(self, outcomes, exit_code=0, edit=False):
        def step(report, name, arguments, directory, environment, run_directory, deadline, output=None):
            report["steps"].append({"name": name, "started": True, "nativeExitCode": exit_code if name == "test" else 0})
            if name == "toolchain":
                output.write(b"8.0.426\n")
            elif name == "test":
                report["executionState"] = "runnerStarted"
                self.assertIn("--no-restore", arguments)
                self.assertIn("--no-build", arguments)
                (Path(run_directory) / "native.trx").write_bytes(native_trx(outcomes))
                if edit:
                    (self.project.parent / "WorkflowTests.cs").write_text("// changed", encoding="utf-8")
            return exit_code if name == "test" else 0
        return step

    def prepare_locked(self, output_path=None):
        result = scaffold.create_project(str(self.app), "Orders", output_path=output_path)
        project = Path(result["testProject"])
        versions = {"Microsoft.Azure.Workflows.WebJobs.Tests.Extension": "1.0.3",
                    "Microsoft.Azure.Workflows.WebJobs.Extension": "1.165.50",
                    "MSTest.TestAdapter": "4.0.2", "MSTest.TestFramework": "4.0.2"}
        (project.parent / "packages.lock.json").write_text(
            json.dumps({"dependencies": {"net8.0": {key: {"resolved": value} for key, value in versions.items()}}}),
            encoding="utf-8")
        return project

    def test_create_and_run_artifacts_never_enter_default_or_custom_deployment_packages(self):
        production = self.app / "lib" / "production.dll"
        production.parent.mkdir()
        production.write_bytes(b"PRODUCTION-ASSEMBLY-MUST-REMAIN")
        for destination in (None, str(self.app / "Quality" / "Smoke")):
            with self.subTest(destination=destination):
                project = self.prepare_locked(destination)
                (project.parent / "trigger.json").write_text(json.dumps({"private": PRIVATE}), encoding="utf-8")
                with mock.patch.object(sdk.shutil, "which", return_value="dotnet.exe"), \
                        mock.patch.object(sdk, "_step", side_effect=self.fake_native(["Passed"])):
                    report = self.run_sdk(test_project=str(project))
                self.assertEqual(0, report["exitCode"])
                for relative in (("bin", "test.dll"), ("obj", "test.dll"),
                                 (scaffold.STATE_DIRECTORY, "packages", "sdk", "1.0.3", "sdk.dll")):
                    artifact = project.parent.joinpath(*relative)
                    artifact.parent.mkdir(parents=True, exist_ok=True)
                    artifact.write_bytes(b"SDK-BINARY-MUST-NOT-BE-DEPLOYED")
                project.rename(project.with_name("Existing.Native.csproj"))
                archive = self.root / ("default.zip" if destination is None else "custom.zip")
                result = _workflow.deterministic_package(str(self.app), str(archive))
                prefix = project.parent.relative_to(self.app).as_posix() + "/"
                with zipfile.ZipFile(archive) as bundle:
                    names = bundle.namelist()
                    self.assertFalse(any(name.startswith(prefix) for name in names), names)
                    self.assertEqual(self.workflow.read_bytes(), bundle.read("Orders/workflow.json"))
                    self.assertEqual(production.read_bytes(), bundle.read("lib/production.dll"))
                    self.assertNotIn(PRIVATE.encode("utf-8"), b"".join(bundle.read(name) for name in names))
                self.assertIn({"path": prefix[:-1], "reason": "native-test-project"}, result["excluded"])

    def test_source_only_scaffold_and_external_raw_trx_are_deployment_excluded(self):
        self.create()
        (self.app / "evidence.TrX").write_text(PRIVATE, encoding="utf-8")
        archive = self.root / "scaffold.zip"
        result = _workflow.deterministic_package(str(self.app), str(archive))
        with zipfile.ZipFile(archive) as bundle:
            self.assertEqual(["host.json", "Orders/workflow.json"], bundle.namelist())
        self.assertIn({"path": "Tests/Orders", "reason": "native-test-project"}, result["excluded"])
        self.assertIn({"path": "evidence.TrX", "reason": "native-test-results"}, result["excluded"])

    def test_deployment_test_boundaries_are_case_equivalent(self):
        for marker_name in (scaffold.PROJECT_FILE.upper(), scaffold.STATE_DIRECTORY.upper()):
            directory = self.app / marker_name.replace(".", "_")
            directory.mkdir()
            marker = directory / marker_name
            if marker_name.lower() == scaffold.STATE_DIRECTORY:
                marker.mkdir()
                (directory / "Existing.Native.csproj").write_text(
                    "<Project><PropertyGroup><IsTestProject>true</IsTestProject></PropertyGroup></Project>",
                    encoding="utf-8")
            else:
                marker.write_text(
                    "<Project><PropertyGroup><IsTestProject>true</IsTestProject></PropertyGroup></Project>",
                    encoding="utf-8")
            (directory / "fixture.json").write_text(PRIVATE, encoding="utf-8")
        archive = self.root / "case-equivalent.zip"
        result = _workflow.deterministic_package(str(self.app), str(archive))
        with zipfile.ZipFile(archive) as bundle:
            self.assertEqual(["host.json", "Orders/workflow.json"], bundle.namelist())
        self.assertEqual(2, sum(row["reason"] == "native-test-project" for row in result["excluded"]))

    def test_package_refuses_test_projects_colocated_with_deployable_content(self):
        nested = self.app / "AnotherApp"
        nested.mkdir()
        (nested / "host.json").write_text("{}", encoding="utf-8")
        for directory in (self.app, self.workflow.parent, nested):
            for marker_name in (scaffold.PROJECT_FILE, scaffold.STATE_DIRECTORY.upper()):
                marker = directory / marker_name
                marker.write_text("<Project />", encoding="utf-8")
                archive = self.root / "unsafe.zip"
                with self.subTest(directory=directory, marker=marker_name), \
                        self.assertRaisesRegex(ValidationError, "dedicated"):
                    _workflow.deterministic_package(str(self.app), str(archive))
                self.assertFalse(archive.exists())
                self.assertFalse(Path(str(archive) + ".manifest.json").exists())
                marker.unlink()

    def test_runner_requires_consistent_nonzero_test_counts_and_never_invents_coverage(self):
        self.prepare_locked()
        for outcomes, code, expected in [
                (["Passed"], 0, "nativeTestsPassed"), (["Failed"], 1, "nativeTestsFailed"),
                ([], 0, "noTestsExecuted"), (["NotExecuted"], 0, "noTestsExecuted"),
                (["Passed"], 1, "runnerError"), (["Failed"], 0, "runnerError"),
                (["Failed"], 134, "runnerError")]:
            with self.subTest(outcomes=outcomes, code=code), \
                    mock.patch.object(sdk.shutil, "which", return_value="dotnet.exe"), \
                    mock.patch.object(sdk, "_step", side_effect=self.fake_native(outcomes, code)):
                report = self.run_sdk()
                self.assertEqual(expected, report["outcome"])
                self.assertNotIn(PRIVATE, json.dumps(report))
                self.assertEqual("notAttested", report["coverage"]["workflowExecution"])
                self.assertEqual("notAttested", report["coverage"]["businessCoverage"])
                self.assertTrue(sdk.validate_report(report), report)

    def test_first_native_producer_remains_inspectable_without_approving_future_execution(self):
        report = successful_record()
        for version in ("0.1.25", "0.1.26", "1.0.0b1"):
            with self.subTest(version=version):
                report["provenance"]["cliVersion"] = version
                self.assertTrue(sdk.validate_report(report))
                saved = self.root / ("native-" + version + ".json")
                saved.write_text(json.dumps(report), encoding="utf-8")
                inspected = _testing.results_report(str(saved))
                self.assertEqual("nativeTestsPassed", inspected["inspection"]["sourceOutcome"])
                self.assertEqual(2, inspected["summary"]["passed"])
                self.assertEqual("notAttested", inspected["coverage"]["workflowExecution"])
                with mock.patch.object(sdk, "VERSION", "1.0.0b3"):
                    self.assertTrue(sdk.validate_report(report))
        changed = copy.deepcopy(report)
        changed["provenance"]["cliVersion"] = "99.0.0"
        self.assertFalse(sdk.validate_report(changed))
        with mock.patch.object(sdk, "_step", side_effect=AssertionError("Historical approval reused")):
            refused = sdk.run_report(str(self.app), "Orders")
        self.assertEqual(4, refused["exitCode"])

    def test_source_drift_cannot_reuse_a_current_native_pass(self):
        self.prepare_locked()
        with mock.patch.object(sdk.shutil, "which", return_value="dotnet.exe"), \
                mock.patch.object(sdk, "_step", side_effect=self.fake_native(["Passed"], edit=True)):
            report = self.run_sdk()
        self.assertEqual("stale", report["outcome"])
        self.assertEqual(5, report["exitCode"])
        self.assertEqual("changed", report["inputStability"])
        self.assertTrue(sdk.validate_report(report))

    def test_existing_report_destination_refuses_before_native_execution(self):
        self.prepare_locked()
        destination = self.root / "result.json"
        destination.write_text(PRIVATE, encoding="utf-8")
        with mock.patch.object(sdk, "_step", side_effect=AssertionError("Execution before destination refusal")):
            report = self.run_sdk(report_path=str(destination))
        self.assertEqual(6, report["exitCode"])
        self.assertEqual(PRIVATE, destination.read_text())

    def test_retained_process_receipt_blocks_another_invocation_without_reading_or_signalling_it(self):
        self.prepare_locked()
        receipt = self.project.parent / scaffold.STATE_DIRECTORY / "runs" / "prior-invocation" / "process-test.json"
        receipt.parent.mkdir(parents=True)
        receipt.write_text(PRIVATE, encoding="utf-8")
        with mock.patch.object(sdk.shutil, "which", return_value="dotnet.exe"), \
                mock.patch.object(sdk, "_step", side_effect=self.fake_native(["Passed"])), \
                mock.patch.object(sdk._local, "_terminate_record_process",
                                  side_effect=AssertionError("Untrusted receipt cannot authorize signalling")):
            report = self.run_sdk()
        self.assertEqual(9, report["exitCode"])
        self.assertEqual("notExecuted", report["executionState"])
        self.assertEqual([], report["steps"])
        self.assertTrue(sdk.validate_report(report))
        self.assertEqual(PRIVATE, receipt.read_text())
        receipt.unlink()
        (receipt.parent / "native.trx").write_text(PRIVATE, encoding="utf-8")
        with mock.patch.object(sdk.shutil, "which", return_value="dotnet.exe"), \
                mock.patch.object(sdk, "_step", side_effect=self.fake_native(["Passed"])):
            report = self.run_sdk()
        self.assertEqual(0, report["exitCode"])
        self.assertTrue(sdk.validate_report(report))

    def test_trx_counts_are_derived_from_rows_not_success_shaped_summaries(self):
        path = self.root / "native.trx"
        path.write_bytes(native_trx(["Passed", "NotExecuted"]))
        self.assertEqual({"selected": 2, "executed": 1, "passed": 1, "failed": 0, "skipped": 1},
                         sdk.trx_summary(str(path)))
        root = ET.fromstring(path.read_bytes())
        root.find(sdk.TRX_NAMESPACE + "ResultSummary").find(sdk.TRX_NAMESPACE + "Counters").set("passed", "2")
        path.write_bytes(ET.tostring(root))
        with self.assertRaises(sdk.SdkError):
            sdk.trx_summary(str(path))
        path.write_bytes(b'<!DOCTYPE TestRun [<!ENTITY x "value">]><TestRun>&x;</TestRun>')
        with self.assertRaises(sdk.SdkError):
            sdk.trx_summary(str(path))

    def test_missing_or_incomplete_native_results_are_runner_errors_not_local_input_errors(self):
        self.prepare_locked()
        native = self.fake_native(["Passed"])
        for invalid in (None, b"not XML", native_trx(["Passed"], summary="Aborted")):
            def step(*args, **kwargs):
                code = native(*args, **kwargs)
                if args[1] == "test":
                    path = Path(args[5]) / "native.trx"
                    if invalid is None:
                        path.unlink()
                    else:
                        path.write_bytes(invalid)
                return code
            with self.subTest(invalid=invalid), \
                    mock.patch.object(sdk.shutil, "which", return_value="dotnet.exe"), \
                    mock.patch.object(sdk, "_step", side_effect=step):
                report = self.run_sdk()
                self.assertEqual(2, report["exitCode"])
                self.assertEqual("runnerError", report["outcome"])
                self.assertEqual(0, report["summary"]["passed"])
                self.assertTrue(sdk.validate_report(report), report)

    def test_native_launch_errors_are_classified_without_exporting_os_error_details(self):
        run = self.root / "run"
        run.mkdir()
        for name, expected in (("toolchain", "toolchain.unavailable"), ("restore", "restore.failed"),
                               ("build", "build.failed"), ("test", "runner.failed")):
            report = sdk.new_report()
            with self.subTest(step=name), mock.patch.object(subprocess, "Popen", side_effect=OSError(PRIVATE)):
                with self.assertRaisesRegex(sdk.SdkError, expected):
                    sdk._step(report, name, ["dotnet.exe"], str(self.root), {}, str(run), time.monotonic() + 5)
            self.assertEqual(2, sdk.finalize(report)["exitCode"])
            self.assertNotIn(PRIVATE, json.dumps(report))
            self.assertFalse(report["steps"][0]["started"])

    def test_closed_sdk_records_reject_tampering_boolean_counts_and_unreviewed_versions(self):
        valid = successful_record()
        self.assertTrue(sdk.validate_report(valid))
        candidates = []
        for location, key, value in [
                ("summary", "passed", True), ("summary", "failed", 1),
                ("provenance", "cliVersion", "9.9.9"), ("coverage", "businessCoverage", "certified"),
                ("permissions", "projectTrusted", False), ("dependencies", "engineVersion", "9.9.9")]:
            candidate = copy.deepcopy(valid)
            candidate[location][key] = value
            candidates.append(candidate)
        candidate = copy.deepcopy(valid)
        candidate["findings"] = [{"code": "tests.empty", "message": PRIVATE}]
        candidates.append(candidate)
        candidate = copy.deepcopy(valid)
        candidate["artifactPath"] = PRIVATE
        candidates.append(candidate)
        for edit in (
                lambda value: value["steps"][0].update(started=False, nativeExitCode=None),
                lambda value: value["steps"][0].update(nativeExitCode=1),
                lambda value: value["steps"][-1].update(nativeExitCode=134),
                lambda value: value.update(inputStability="changed"),
                lambda value: value["dependencies"].update(dotnetVersion=None)):
            candidate = copy.deepcopy(valid)
            edit(candidate)
            candidates.append(candidate)
        for candidate in candidates:
            with self.subTest(candidate=candidate):
                self.assertFalse(sdk.validate_report(candidate))
        self.assertFalse(sdk.validate_report(sdk.finalize(sdk.new_report())))

    def test_results_inspection_preserves_historical_verdict_without_following_paths_or_rerunning(self):
        report = successful_record()
        report["workflow"]["definitionHash"] = _testing._digest(self.workflow.read_bytes())
        path = self.root / "native.json"
        path.write_text(json.dumps(report), encoding="utf-8")
        result = _testing.results_report(str(path), str(self.workflow))
        self.assertEqual("inspection", result["phase"])
        self.assertEqual("inspected", result["outcome"])
        self.assertEqual("nativeTestsPassed", result["inspection"]["sourceOutcome"])
        self.assertEqual("matches", result["inspection"]["workflowIdentity"])
        self.workflow.write_text("{}", encoding="utf-8")
        stale = _testing.results_report(str(path), str(self.workflow))
        self.assertEqual("stale", stale["outcome"])
        self.assertEqual(5, stale["exitCode"])
        unavailable = _testing.results_report(str(path), str(self.root / "missing.json"))
        self.assertEqual("logicapp-sdk-test", unavailable["reportType"])
        self.assertEqual("unavailable", unavailable["inspection"]["workflowIdentity"])
        self.assertEqual("nativeTestsPassed", unavailable["inspection"]["sourceOutcome"])
        self.assertEqual(3, unavailable["exitCode"])
        self.assertEqual(2, unavailable["summary"]["passed"])
        current = self.workflow.read_bytes()
        report["workflow"]["definitionHash"] = _testing._digest(current)
        raw = json.dumps(report).encode("utf-8")
        with mock.patch.object(_testing, "_read", side_effect=[raw, raw, current, current + b" "]) as read:
            changed = _testing.results_report(str(path), str(self.workflow))
        self.assertEqual(5, changed["exitCode"])
        self.assertEqual("changed", changed["inspection"]["workflowIdentity"])
        self.assertEqual(4, read.call_count)

    def test_cleanup_pending_is_persisted_and_stops_the_pipeline(self):
        self.create()
        run = self.root / "run"
        run.mkdir()
        report = sdk.new_report()
        process = mock.Mock(pid=1234567, returncode=0)
        process.poll.return_value = 0
        with mock.patch.object(subprocess, "Popen", return_value=process), \
                mock.patch.object(sdk._local, "process_create_time_utc", return_value="2026-01-01T00:00:00.0000000Z"), \
                mock.patch.object(sdk._local, "_terminate_launched_process") as cleanup, \
                mock.patch.object(sdk._local, "_runtime_has_live_process", return_value=True):
            with self.assertRaisesRegex(sdk.SdkError, "cleanup.pending"):
                sdk._step(report, "build", ["dotnet.exe"], str(self.root), {}, str(run), time.monotonic() + 5)
        cleanup.assert_called_once()
        receipt = json.loads((run / "process-build.json").read_text())
        self.assertEqual(1234567, receipt["pid"])
        self.assertTrue(receipt["cleanupPending"])
        self.assertEqual("cleanupPending", sdk.finalize(report)["outcome"])
