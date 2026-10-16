# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Explicit, trusted native execution; never a sandbox or workflow coverage attestation."""
# pylint: disable=protected-access

import copy
from collections import deque
import os
import re
import shutil
import subprocess
import time
import uuid
import xml.etree.ElementTree as ET

from knack.util import CLIError

from . import _local, _testing
from ._context import _store_lock
from ._test_report import VERSION, _hash
from ._test_scaffold import ENGINE_VERSION, SDK_VERSION, STATE_DIRECTORY, default_project, selected_workflow

REPORT_TYPE = "logicapp-sdk-test"
TRX_NAMESPACE = "{http://microsoft.com/schemas/VisualStudio/TeamTest/2010}"
MAX_SOURCE_FILES = 256
MAX_SOURCE_BYTES = 16 * 1024 * 1024
SUPPORTED_PRODUCERS = ("0.1.25", "0.1.26", "1.0.0b1", VERSION)
# Priority is explicit: a partial/failed cleanup or publication cannot become a native pass.
RULES = {
    "cleanup.pending": ("cleanupPending", 9, "Tracked native processes could not be safely stopped. Inspect the retained process receipt; do not kill processes by name."),
    "report.publication": ("publicationError", 6, "Report publication failed. Inspect the destination before retrying."),
    "input.changed": ("stale", 5, "Selected local inputs changed during execution. No current-input pass is available."),
    "execution.interrupted": ("interrupted", 130, "Native execution was interrupted; no complete test verdict is available."),
    "execution.timeout": ("timeout", 8, "The native operation exceeded the invocation deadline. No complete test verdict is available."),
    "policy.terms": ("blocked", 4, "Review the Microsoft Logic Apps Tests SDK terms, data collection and update behavior; --accept-sdk-terms is required for this invocation."),
    "policy.trust": ("blocked", 4, "Restore, MSBuild and test code can execute arbitrary code and contact services. Review the project and supply --trust-project; this is not a sandbox."),
    "input.invalid": ("inputError", 3, "Select bounded, regular local workflow/project/configuration inputs without linked path components."),
    "toolchain.unavailable": ("runnerError", 2, "A native .NET 8 SDK executable is required; no tool was installed automatically."),
    "dependencies.unqualified": ("runnerError", 2, "The lockfile must resolve net8.0, Logic Apps Tests SDK 1.0.3, engine 1.165.50 and MSTest 4.0.2. Restore explicitly, then review the locked graph."),
    "restore.failed": ("restoreFailed", 2, "Native restore failed. Review the selected NuGet configuration and project; native output is withheld to avoid exporting credentials."),
    "build.failed": ("buildFailed", 2, "Native build failed. Review the project and dependencies, and use --restore for an explicitly approved restore. Native output is withheld."),
    "runner.failed": ("runnerError", 2, "The native runner did not produce consistent completed results. Inspect the retained local TRX; logs and embedded paths are not exported."),
    "results.invalid": ("runnerError", 2, "Native results are missing, oversized, malformed or outside the supported MSTest TRX subset. No partial pass was accepted."),
    "tests.failed": ("nativeTestsFailed", 1, "Native tests failed. This includes assertion failures and test exceptions, not a diagnosis of workflow business behavior."),
    "tests.empty": ("noTestsExecuted", 7, "No native tests executed. Zero discovery and entirely skipped/unconfigured scaffolds are not passing suites."),
}


class SdkError(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def new_report():
    return {
        "reportType": REPORT_TYPE, "schemaVersion": "1.0", "phase": "execution",
        "invocationId": str(uuid.uuid4()),
        "provenance": {"producer": "az.logicapp.test.run", "cliVersion": VERSION,
                       "evidence": "native-MSTest-TRX", "authenticity": "notAttested"},
        "workflow": {"name": None, "kind": None, "definitionHash": None},
        "testProjectHash": None,
        "dependencies": {"sdkVersion": SDK_VERSION, "engineVersion": ENGINE_VERSION,
                         "mstestVersion": "4.0.2", "targetFramework": "net8.0", "dotnetVersion": None,
                         "resolution": "notChecked"},
        "permissions": {"termsAccepted": False, "projectTrusted": False, "restoreAllowed": False},
        "coverage": {"workflowExecution": "notAttested", "businessCoverage": "notAttested",
                     "externalIsolation": "notProvided"},
        "inputStability": "notChecked", "executionState": "notExecuted",
        "summary": {"selected": 0, "executed": 0, "passed": 0, "failed": 0, "skipped": 0},
        "steps": [], "findings": [], "inspection": None, "outcome": "blocked", "exitCode": 4,
    }


def _add(report, code):
    finding = {"code": code, "message": RULES[code][2]}
    if finding not in report["findings"]:
        report["findings"].append(finding)


def finalize(report):
    codes = {row["code"] for row in report["findings"]}
    for code, (outcome, exit_code, _) in RULES.items():
        if code in codes:
            report.update(outcome=outcome, exitCode=exit_code)
            return report
    if report["executionState"] == "runnerCompleted" and report["summary"]["passed"] > 0:
        report.update(outcome="nativeTestsPassed", exitCode=0)
    else:
        report.update(outcome="blocked", exitCode=4)
    return report


def _snapshot(directory, excluded):
    result, total, nodes = {}, 0, 0

    def unreadable(_):
        raise _testing.InputError("input.unreadable")

    for parent, directories, files in os.walk(directory, followlinks=False, onerror=unreadable):
        nodes += len(directories) + len(files)
        if nodes > _testing.MAX_NODES:
            raise _testing.InputError("input.tooLarge")
        directories[:] = [name for name in directories if name not in ("bin", "obj", ".git", STATE_DIRECTORY)]
        for name in directories:
            _testing._path(os.path.join(parent, name))
        for name in sorted(files):
            path = os.path.join(parent, name)
            if (os.path.normcase(path) in excluded or name == "packages.lock.json" or
                    os.path.splitext(name)[1].lower() not in (".cs", ".csproj", ".props", ".targets", ".json", ".config")):
                continue
            data = _testing._read(path)
            total += len(data)
            if len(result) >= MAX_SOURCE_FILES or total > MAX_SOURCE_BYTES:
                raise _testing.InputError("input.tooLarge")
            result[path] = data
    return result


def _environment(state):
    allowed = ("SystemRoot", "WINDIR", "SystemDrive", "ComSpec", "ProgramFiles", "ProgramFiles(x86)",
               "ProgramW6432", "PROCESSOR_ARCHITECTURE", "NUMBER_OF_PROCESSORS", "OS", "PATHEXT", "PATH",
               "LANG", "LC_ALL")
    environment = {key: value for key, value in os.environ.items() if key.upper() in {
        item.upper() for item in allowed}}
    home = os.path.join(state, "home")
    environment.update(
        HOME=home, USERPROFILE=home, DOTNET_CLI_HOME=home,
        APPDATA=os.path.join(home, "AppData", "Roaming"), LOCALAPPDATA=os.path.join(home, "AppData", "Local"),
        TEMP=os.path.join(state, "tmp"), TMP=os.path.join(state, "tmp"),
        NUGET_PACKAGES=os.path.join(state, "packages"), NUGET_HTTP_CACHE_PATH=os.path.join(state, "http-cache"),
        AZURE_CONFIG_DIR=os.path.join(state, "azure"), DOTNET_CLI_TELEMETRY_OPTOUT="1",
        DOTNET_SKIP_FIRST_TIME_EXPERIENCE="1", DOTNET_GENERATE_ASPNET_CERTIFICATE="false",
        DOTNET_ADD_GLOBAL_TOOLS_TO_PATH="false", DOTNET_CLI_WORKLOAD_UPDATE_NOTIFY_DISABLE="true",
        DOTNET_CLI_USE_MSBUILD_SERVER="0", MSBUILDDISABLENODEREUSE="1", DOTNET_NOLOGO="1")
    for name in ("home", "tmp", "packages", "http-cache", "azure"):
        os.makedirs(_testing._path(os.path.join(state, name)), mode=0o700, exist_ok=True)
    return environment


def _receipt(path, record):
    _testing._publish(record, path, True, set())


def _refuse_retained_processes(state):
    runs = _testing._path(os.path.join(state, "runs"))
    if not os.path.lexists(runs):
        return
    pending, nodes = deque([runs]), 0
    try:
        while pending:
            directory = pending.popleft()
            with os.scandir(directory) as entries:
                for entry in entries:
                    nodes += 1
                    if nodes > _testing.MAX_NODES:
                        raise _testing.InputError("input.tooLarge")
                    path = _testing._path(entry.path)
                    name = entry.name.lower()
                    if name.startswith("process-") and name.endswith(".json"):
                        raise SdkError("cleanup.pending")
                    if directory == runs and entry.is_dir(follow_symlinks=False):
                        pending.append(path)
    except OSError as ex:
        raise SdkError("cleanup.pending") from ex


def _step(report, name, arguments, directory, environment, run_directory, deadline, output=None):
    step = {"name": name, "started": False, "nativeExitCode": None}
    report["steps"].append(step)
    process, record = None, None
    receipt = os.path.join(run_directory, "process-" + name + ".json")
    try:
        if time.monotonic() >= deadline:
            raise SdkError("execution.timeout")
        try:
            process = subprocess.Popen(arguments, cwd=directory, env=environment, stdin=subprocess.DEVNULL,
                                       stdout=output if output is not None else subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL, shell=False)
        except OSError as ex:
            raise SdkError({"toolchain": "toolchain.unavailable", "restore": "restore.failed",
                            "build": "build.failed", "test": "runner.failed"}[name]) from ex
        step["started"] = True
        if name == "test":
            report["executionState"] = "runnerStarted"
        record = {"pid": process.pid, "processCreateTimeUtc": _local.process_create_time_utc(process.pid)}
        _receipt(receipt, record)
        while process.poll() is None:
            _local._remember_runtime_children(record)
            _receipt(receipt, record)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise SdkError("execution.timeout")
            try:
                process.wait(timeout=min(0.1, remaining))
            except subprocess.TimeoutExpired:
                continue
        step["nativeExitCode"] = process.returncode
        return process.returncode
    except SdkError as ex:
        _add(report, ex.code)
        raise
    except KeyboardInterrupt:
        _add(report, "execution.interrupted")
        raise
    finally:
        if process is not None:
            record = record or {"pid": process.pid, "processCreateTimeUtc": None}
            try:
                _local._terminate_launched_process(process, record)
                pending = (process.poll() is None or _local._runtime_has_live_process(record) or
                           _local._unverified_cleanup_pending(record))
            except (OSError, subprocess.SubprocessError):
                pending = True
            if pending:
                record["cleanupPending"] = True
                _add(report, "cleanup.pending")
                _receipt(receipt, record)
                raise SdkError("cleanup.pending")
            if os.path.exists(receipt):
                os.unlink(receipt)


def _locked_dependencies(path):
    payload = _testing._json(_testing._read(path))
    try:
        rows = payload["dependencies"]["net8.0"]
        dependencies = {key.lower(): value for key, value in rows.items()}
        expected = {
            "Microsoft.Azure.Workflows.WebJobs.Tests.Extension": SDK_VERSION,
            "Microsoft.Azure.Workflows.WebJobs.Extension": ENGINE_VERSION,
            "MSTest.TestFramework": "4.0.2", "MSTest.TestAdapter": "4.0.2",
        }
        if len(dependencies) != len(rows) or set(payload["dependencies"]) != {"net8.0"} or any(
                dependencies[name.lower()]["resolved"] != version for name, version in expected.items()):
            raise SdkError("dependencies.unqualified")
    except (KeyError, TypeError, AttributeError) as ex:
        raise SdkError("dependencies.unqualified") from ex


def _xml(data):
    try:
        text = data.decode("utf-8-sig")
        if re.search(r"<!\s*(DOCTYPE|ENTITY)", text, re.IGNORECASE):
            raise ValueError("DTD")
        root = ET.fromstring(text)
        pending, nodes = [(root, 0)], 0
        while pending:
            element, depth = pending.pop()
            nodes += 1
            if depth > _testing.MAX_DEPTH or nodes > _testing.MAX_NODES:
                raise ValueError("bounds")
            pending.extend((child, depth + 1) for child in element)
        return root
    except (UnicodeError, ValueError, ET.ParseError) as ex:
        raise SdkError("results.invalid") from ex


def trx_summary(path):
    try:
        root = _xml(_testing._read(path))
    except _testing.InputError as ex:
        raise SdkError("results.invalid") from ex
    namespace = TRX_NAMESPACE
    if root.tag != namespace + "TestRun":
        raise SdkError("results.invalid")
    summaries, results = root.findall(namespace + "ResultSummary"), root.findall(namespace + "Results")
    if len(summaries) != 1 or len(results) > 1 or summaries[0].get("outcome") not in ("Completed", "Failed"):
        raise SdkError("results.invalid")
    counters = summaries[0].findall(namespace + "Counters")
    if len(counters) != 1:
        raise SdkError("results.invalid")
    values = counters[0].attrib
    required = ("total", "executed", "passed", "failed")
    if any(name not in values for name in required) or any(
            not re.fullmatch(r"[0-9]{1,6}", value) for value in values.values()):
        raise SdkError("results.invalid")
    counts = {key: int(value) for key, value in values.items()}
    if any(value for key, value in counts.items() if key not in required + ("notExecuted",)):
        raise SdkError("results.invalid")
    rows = list(results[0]) if results else []
    actual = {"Passed": 0, "Failed": 0, "NotExecuted": 0}
    seen = set()
    for row in rows:
        identity = row.get("executionId")
        if (row.tag != namespace + "UnitTestResult" or row.get("outcome") not in actual or
                not isinstance(identity, str) or not re.fullmatch(r"[0-9a-fA-F-]{36}", identity) or
                identity in seen or row.find(namespace + "InnerResults") is not None):
            raise SdkError("results.invalid")
        seen.add(identity)
        actual[row.get("outcome")] += 1
    if (counts["total"] != len(rows) or counts["passed"] != actual["Passed"] or
            counts["failed"] != actual["Failed"] or counts["executed"] != actual["Passed"] + actual["Failed"] or
            counts.get("notExecuted", 0) not in (0, actual["NotExecuted"]) or
            (actual["Failed"] > 0) != (summaries[0].get("outcome") == "Failed")):
        raise SdkError("results.invalid")
    return {"selected": len(rows), "executed": counts["executed"], "passed": counts["passed"],
            "failed": counts["failed"], "skipped": actual["NotExecuted"]}


def _execute(report, project, root, workflow, config, restore, timeout, report_path, protected):
    directory = os.path.dirname(project)
    excluded = {os.path.normcase(report_path)} if report_path else set()
    before = _snapshot(directory, excluded)
    workflow_path, workflow_bytes, document = selected_workflow(root, workflow)
    before[workflow_path] = workflow_bytes
    before[os.path.join(root, "host.json")] = _testing._read(os.path.join(root, "host.json"))
    if config:
        before[config] = _testing._read(config)
    protected.update(os.path.normcase(path) for path in before)
    protected.add(os.path.normcase(os.path.join(directory, "packages.lock.json")))
    if report_path:
        _testing._destination(report_path, False, protected)
    report["workflow"].update(name=workflow, kind=document["kind"], definitionHash=_testing._digest(workflow_bytes))
    report["testProjectHash"] = _testing._digest(_testing._read(project))
    state = _testing._path(os.path.join(directory, STATE_DIRECTORY))
    _refuse_retained_processes(state)
    environment = _environment(state)
    run_directory = _testing._path(os.path.join(state, "runs", report["invocationId"]))
    os.makedirs(run_directory, mode=0o700)
    executable = shutil.which("dotnet")
    if not executable or (os.name == "nt" and not executable.lower().endswith(".exe")):
        raise SdkError("toolchain.unavailable")
    deadline = time.monotonic() + timeout
    version_file = os.path.join(run_directory, "toolchain.txt")
    with open(version_file, "xb") as handle:
        code = _step(report, "toolchain", [executable, "--version"], directory, environment,
                     run_directory, deadline, output=handle)
    try:
        version = _testing._read(version_file).decode("utf-8-sig").strip()
    except (_testing.InputError, UnicodeError) as ex:
        raise SdkError("toolchain.unavailable") from ex
    if code or not re.fullmatch(r"8\.0\.[0-9]{3}", version):
        raise SdkError("toolchain.unavailable")
    report["dependencies"]["dotnetVersion"] = version
    common = [project, "-p:ImportDirectoryBuildProps=false", "-p:ImportDirectoryBuildTargets=false",
              "-p:UseSharedCompilation=false", "-p:BuildInParallel=false", "--verbosity", "quiet"]
    lockfile = os.path.join(directory, "packages.lock.json")
    if restore:
        arguments = [executable, "restore"] + common + ["--disable-parallel", "--use-lock-file",
                                                        "--configfile", config]
        if os.path.exists(lockfile):
            arguments.append("--locked-mode")
        if _step(report, "restore", arguments, directory, environment, run_directory, deadline):
            raise SdkError("restore.failed")
    try:
        _locked_dependencies(lockfile)
    except _testing.InputError as ex:
        raise SdkError("dependencies.unqualified") from ex
    report["dependencies"]["resolution"] = "locked"
    lock_bytes = _testing._read(lockfile)
    if _step(report, "build", [executable, "build"] + common + [
            "--no-restore", "--no-incremental", "--disable-build-servers"], directory, environment,
            run_directory, deadline):
        raise SdkError("build.failed")
    code = _step(report, "test", [executable, "test"] + common + [
        "--no-restore", "--no-build", "--logger", "trx;LogFileName=native.trx",
        "--results-directory", run_directory], directory, environment, run_directory, deadline)
    if any(row["code"] == "cleanup.pending" for row in report["findings"]):
        return
    report["summary"] = trx_summary(os.path.join(run_directory, "native.trx"))
    report["executionState"] = "runnerCompleted"
    if code not in (0, 1) or bool(code) != bool(report["summary"]["failed"]):
        raise SdkError("runner.failed")
    if report["summary"]["failed"]:
        _add(report, "tests.failed")
    elif not report["summary"]["executed"]:
        _add(report, "tests.empty")
    try:
        after = _snapshot(directory, excluded)
        for path in before:
            after[path] = _testing._read(path)
        changed_lock = _testing._read(lockfile) != lock_bytes
    except _testing.InputError as ex:
        report["inputStability"] = "changed"
        raise SdkError("input.changed") from ex
    if any(before[path] != after[path] for path in before) or any(
            path not in before for path in after) or changed_lock:
        report["inputStability"] = "changed"
        raise SdkError("input.changed")
    report["inputStability"] = "unchangedSelectedFiles"


def run_report(root, workflow, test_project=None, accept_sdk_terms=False, trust_project=False,
               restore=False, nuget_config=None, timeout=300, report_path=None):
    report, protected = new_report(), set()
    report["permissions"].update(termsAccepted=bool(accept_sdk_terms), projectTrusted=bool(trust_project),
                                 restoreAllowed=bool(restore))
    try:
        if not accept_sdk_terms:
            _add(report, "policy.terms")
        if not trust_project:
            _add(report, "policy.trust")
        if report["findings"]:
            return _publish(report, report_path, protected)
        if (isinstance(timeout, bool) or not isinstance(timeout, int) or not 1 <= timeout <= 3600 or
                nuget_config is not None and not restore):
            raise _testing.InputError("input.options")
        selected_workflow(root, workflow)
        project = _testing._path(test_project or default_project(root, workflow))
        if not project.lower().endswith(".csproj"):
            raise _testing.InputError("input.options")
        _testing._read(project)
        config = _testing._path(nuget_config or os.path.join(os.path.dirname(project), "NuGet.Config")) if restore else None
        if config:
            _testing._read(config)
        if report_path:
            _testing._destination(report_path, False, {os.path.normcase(project)})
        with _store_lock(project, label="SDK test project"):
            _execute(report, project, root, workflow, config, restore, timeout, report_path, protected)
    except KeyboardInterrupt:
        _add(report, "execution.interrupted")
    except SdkError as ex:
        _add(report, ex.code)
    except _testing.InputError as ex:
        if ex.rule == "input.changed":
            report["inputStability"] = "changed"
        _add(report, "input.changed" if ex.rule == "input.changed" else
             "report.publication" if ex.rule == "report.publication" else "input.invalid")
    except (OSError, UnicodeError, CLIError):
        _add(report, "input.invalid")
    return _publish(report, report_path, protected)


def _publish(report, path, protected):
    finalize(report)
    if path:
        try:
            _testing._publish(report, path, False, protected)
        except (_testing.InputError, OSError):
            _add(report, "report.publication")
            finalize(report)
    return report


def _valid_metadata(value, template):
    workflow = value["workflow"]
    if (set(workflow) != set(template["workflow"]) or workflow["kind"] not in (None, "Stateful", "Stateless") or
            not _hash(workflow["definitionHash"]) or not _hash(value["testProjectHash"]) or
            workflow["name"] is not None and not re.fullmatch(
                r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", workflow["name"])):
        return False
    dependencies = value["dependencies"]
    if (set(dependencies) != set(template["dependencies"]) or
            any(dependencies[key] != template["dependencies"][key] for key in
                ("sdkVersion", "engineVersion", "mstestVersion", "targetFramework")) or
            dependencies["resolution"] not in ("notChecked", "locked") or
            dependencies["dotnetVersion"] is not None and not re.fullmatch(
                r"8\.0\.[0-9]{3}", dependencies["dotnetVersion"])):
        return False
    if set(value["permissions"]) != set(template["permissions"]) or any(
            type(item) is not bool for item in value["permissions"].values()):  # pylint: disable=unidiomatic-typecheck
        return False
    if (value["executionState"] not in ("notExecuted", "runnerStarted", "runnerCompleted") or
            value["inputStability"] not in ("notChecked", "changed", "unchangedSelectedFiles")):
        return False
    counts = value["summary"]
    if set(counts) != set(template["summary"]) or any(
            type(item) is not int or not 0 <= item <= 100000 for item in counts.values()):  # pylint: disable=unidiomatic-typecheck
        return False
    return (counts["executed"] == counts["passed"] + counts["failed"] and
            counts["selected"] == counts["executed"] + counts["skipped"])


def _validated_steps(value):
    steps = value["steps"]
    if not isinstance(steps, list) or len(steps) > 4:
        return None
    names = []
    for step in steps:
        if (not isinstance(step, dict) or set(step) != {"name", "started", "nativeExitCode"} or
                step["name"] not in ("toolchain", "restore", "build", "test") or
                type(step["started"]) is not bool or step["nativeExitCode"] is not None and  # pylint: disable=unidiomatic-typecheck
                (type(step["nativeExitCode"]) is not int or  # pylint: disable=unidiomatic-typecheck
                 not -(2 ** 31) <= step["nativeExitCode"] < 2 ** 32)):
            return None
        if not step["started"] and step["nativeExitCode"] is not None:
            return None
        names.append(step["name"])
    order = ["toolchain"] + (["restore"] if value["permissions"]["restoreAllowed"] else []) + ["build", "test"]
    if names != order[:len(names)] or any(
            not step["started"] or step["nativeExitCode"] != 0 for step in steps[:-1]):
        return None
    return names, order


def _valid_execution(value, codes, names, order):
    permissions, counts, steps = value["permissions"], value["summary"], value["steps"]
    workflow, dependencies = value["workflow"], value["dependencies"]
    if (("tests.failed" in codes and not counts["failed"]) or
            ("tests.empty" in codes and counts["executed"]) or
            ("policy.terms" in codes and permissions["termsAccepted"]) or
            ("policy.trust" in codes and permissions["projectTrusted"])):
        return False
    if (("policy.terms" in codes) != (not permissions["termsAccepted"]) or
            ("policy.trust" in codes) != (not permissions["projectTrusted"])):
        return False
    if not all(permissions[key] for key in ("termsAccepted", "projectTrusted")) and (
            steps or any(workflow.values()) or value["testProjectHash"] is not None or
            value["executionState"] != "notExecuted"):
        return False
    if (value["executionState"] == "runnerStarted" and
            (not steps or names[-1] != "test" or not steps[-1]["started"])):
        return False
    if ((value["inputStability"] == "changed") != ("input.changed" in codes) or
            value["inputStability"] == "unchangedSelectedFiles" and
            value["executionState"] != "runnerCompleted"):
        return False
    if dependencies["resolution"] == "locked" and not dependencies["dotnetVersion"]:
        return False
    if value["executionState"] == "runnerCompleted":
        if (names != order or not all(step["started"] for step in steps) or
                any(step["nativeExitCode"] != 0 for step in steps[:-1]) or
                steps[-1]["nativeExitCode"] is None or
                not all(permissions[key] for key in ("termsAccepted", "projectTrusted")) or
                dependencies["resolution"] != "locked" or not dependencies["dotnetVersion"] or
                any(item is None for item in workflow.values()) or value["testProjectHash"] is None):
            return False
        if counts["failed"] and "tests.failed" not in codes and "runner.failed" not in codes:
            return False
        if not counts["executed"] and "tests.empty" not in codes and "runner.failed" not in codes:
            return False
        if ((steps[-1]["nativeExitCode"] not in (0, 1) or
             bool(steps[-1]["nativeExitCode"]) != bool(counts["failed"])) and "runner.failed" not in codes):
            return False
    elif any(counts.values()):
        return False
    return True


def validate_report(value):
    """Accept only closed execution records; validation does not authenticate their author."""
    template = new_report()
    try:
        if not isinstance(value, dict) or set(value) != set(template):
            return False
        fixed = ("reportType", "schemaVersion", "phase", "coverage", "inspection")
        if any(value[key] != template[key] for key in fixed):
            return False
        provenance = value["provenance"]
        if (set(provenance) != set(template["provenance"]) or
                provenance["cliVersion"] not in SUPPORTED_PRODUCERS or
                provenance != dict(template["provenance"], cliVersion=provenance["cliVersion"])):
            return False
        if str(uuid.UUID(value["invocationId"])) != value["invocationId"] or not _valid_metadata(value, template):
            return False
        validated = _validated_steps(value)
        if validated is None:
            return False
        names, order = validated
        findings = value["findings"]
        if not isinstance(findings, list) or len(findings) > len(RULES):
            return False
        codes = []
        for row in findings:
            if (not isinstance(row, dict) or set(row) != {"code", "message"} or
                    row["code"] not in RULES or row["message"] != RULES[row["code"]][2] or row["code"] in codes):
                return False
            codes.append(row["code"])
        if not _valid_execution(value, codes, names, order):
            return False
        expected = finalize(copy.deepcopy(value))
        if (type(value["exitCode"]) is not int or  # pylint: disable=unidiomatic-typecheck
                any(value[key] != expected[key] for key in ("outcome", "exitCode"))):
            return False
        if not codes and value["outcome"] != "nativeTestsPassed":
            return False
        if value["outcome"] == "nativeTestsPassed" and (
                value["inputStability"] != "unchangedSelectedFiles" or value["steps"][-1]["nativeExitCode"] != 0):
            return False
        return True
    except (KeyError, TypeError, ValueError, AttributeError):
        return False


def results_report(candidate, workflow_file=None):
    if not validate_report(candidate):
        raise SdkError("results.invalid")
    report = copy.deepcopy(candidate)
    report.update(phase="inspection", invocationId=str(uuid.uuid4()), outcome="inspected", exitCode=0)
    report["provenance"]["producer"] = "az.logicapp.test.results.show"
    report["inspection"] = {"sourceInvocationId": candidate["invocationId"],
                            "sourceOutcome": candidate["outcome"], "sourceExitCode": candidate["exitCode"],
                            "workflowIdentity": "notChecked", "authenticity": "notAttested"}
    if workflow_file:
        try:
            if report["workflow"]["definitionHash"] is None:
                raise _testing.InputError("input.options")
            current = _testing._read(workflow_file)
            if (report["workflow"]["definitionHash"] != _testing._digest(current) or
                    _testing._read(workflow_file) != current):
                report["inspection"]["workflowIdentity"] = "changed"
                report.update(outcome="stale", exitCode=5)
            else:
                report["inspection"]["workflowIdentity"] = "matches"
        except _testing.InputError as ex:
            report["inspection"]["workflowIdentity"] = "unavailable"
            _add(report, "input.changed" if ex.rule == "input.changed" else "input.invalid")
            report.update(outcome="inputError", exitCode=3)
            if ex.rule == "input.changed":
                report.update(outcome="stale", exitCode=5)
    return report
