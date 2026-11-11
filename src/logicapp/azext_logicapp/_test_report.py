# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Closed, sanitized protocol for file inspection, not native SDK test results."""

import copy
import re
import uuid
from collections import OrderedDict

VERSION = "1.0.0b2"
SCHEMA = "2.0"
_V1_PRODUCERS = ("0.1.17", "0.1.18", "0.1.19", "0.1.20", "0.1.21", "1.0.0b1")
_V2_PRODUCERS = ("0.1.22", "0.1.23", "0.1.24", "0.1.25", "0.1.26", "1.0.0b1", VERSION)
_LEGACY_INPUT_OPTIONS_PRODUCERS = _V1_PRODUCERS + ("0.1.22", "0.1.23")
_LEGACY_REPORT_INVALID_PRODUCERS = _V1_PRODUCERS + ("0.1.22", "0.1.23", "0.1.24")
SDK_PACKAGE = "Microsoft.Azure.Workflows.WebJobs.Tests.Extension"
WORKFLOW_SCHEMA = ("https://schema.management.azure.com/providers/Microsoft.Logic/"
                   "schemas/2016-06-01/workflowdefinition.json#")
ROLES = ("workflow", "host", "testProject", "settings", "parameters", "connections", "report", "options")
POINTERS = ("", "/kind", "/definition", "/definition/$schema", "/definition/triggers",
            "/definition/actions", "/definition/actions/runAfter")

# Text is selected by rule, never copied from workflow values, XML or parser errors.
RULES = {
    "input.options": ("input", "error", "A local project and a bounded workflow name are required.",
                      "Select an existing local project with --path or a local context and supply --workflow; do not use URLs or device paths."),
    "input.unsafe": ("input", "error", "Input must be a local regular file without linked path components.",
                     "Select a regular local file; linked files and directories are not inspected."),
    "input.unreadable": ("input", "error", "The selected input is missing or unreadable.",
                         "Check the explicitly selected local file and permissions."),
    "input.tooLarge": ("input", "error", "Input exceeds the bounded inspection size.",
                       "Use a smaller reviewed input; no partial inspection was accepted."),
    "input.invalidJson": ("input", "error", "Input is not strict UTF-8 JSON with unique keys and finite numbers.",
                          "Correct JSON syntax, duplicate keys or nonfinite numbers."),
    "input.tooDeep": ("input", "error", "Input exceeds the inspection depth or node limit.",
                      "Reduce nesting or input size; no partial inspection was accepted."),
    "input.changed": ("input", "error", "An inspected input changed or became unavailable during inspection.",
                      "Retry after local edits finish; this report is stale."),
    "host.invalid": ("input", "error", "host.json must be an object with version 2.0 and the Workflows bundle.",
                     "Select an existing Standard project with its host.json."),
    "workflow.root": ("authoring", "error", "workflow.json must contain an object.",
                      "Supply a complete Standard workflow.json, not a bare definition."),
    "workflow.kind.invalid": ("authoring", "error", "An explicit Stateful or Stateless kind is required.",
                              "Set the authored kind explicitly; no Stateful default is applied."),
    "workflow.definition.missing": ("authoring", "error", "definition must be an object.",
                                    "Add the Standard workflow definition."),
    "workflow.schema": ("authoring", "error", "The known workflow definition schema URI is required.",
                        "Review definition.$schema; no remote schema is downloaded."),
    "workflow.triggers.missing": ("authoring", "error", "triggers must be a non-empty object.",
                                  "Add an authored trigger."),
    "workflow.actions.invalid": ("authoring", "error", "actions must be an object.",
                                 "Use an explicit actions object."),
    "trigger.invalid": ("authoring", "error", "A top-level trigger is not an object.",
                        "Review the top-level triggers object."),
    "trigger.kind.warning": ("authoring", "warning", "A Request trigger has an unusual kind.",
                             "Review the Request trigger kind."),
    "action.invalid": ("authoring", "error", "A top-level action is not an object.",
                       "Review the top-level actions object."),
    "graph.run_after.invalid": ("authoring", "error", "A top-level runAfter is not an object.",
                                "Review top-level action dependencies."),
    "graph.missing_action": ("authoring", "error", "A top-level runAfter references an absent action.",
                             "Review dependency names in the same top-level actions object."),
    "reference.missing": ("authoring", "error", "A literal configuration reference has no declaration.",
                          "Review the selected workflow and the explicitly bounded project configuration."),
    "reference.shape": ("input", "error", "Referenced configuration has an unsupported object shape.",
                        "Review the referenced local configuration without copying secrets into reports."),
    "reference.dynamic": ("coverage", "warning", "Dynamic or unsupported configuration references remain unchecked.",
                          "Review references manually; expressions and effective values are not evaluated."),
    "testProject.invalidXml": ("input", "error", "Test project XML is malformed, too complex or uses a DTD/entity.",
                               "Supply a bounded .csproj without DTD or entity declarations."),
    "testProject.dynamic": ("coverage", "warning", "MSBuild evaluation, imports and conditional metadata are not inspected.",
                            "Review the build graph separately; do not execute it to clear this finding."),
    "testProject.metadata": ("coverage", "warning", "Test framework or package metadata is absent or outside the supported literal subset.",
                             "Review literal net8.0/net9.0/net10.0 and exact SDK PackageReference metadata."),
    "testProject.absent": ("dependency", "warning", "No explicit test project was selected.",
                           "Optionally supply an existing --test-project; no project is generated."),
    "sdk.policy": ("policy", "warning", "SDK adoption, use/data/update terms and restore/execution approval are unresolved.",
                   "Obtain separate publisher/legal clarification and explicit adoption approval before any restore or execution."),
    "sdk.qualification": ("dependency", "warning", "SDK/runtime/runner/platform and network isolation are not qualified.",
                          "A separately approved qualification increment is required; declarations are not installed facts."),
    "scope.business": ("coverage", "warning", "No business tests, native runner or SDK were executed.",
                       "Use this report only for bounded authoring inspection, not a workflow test verdict."),
    "report.invalid": ("protocol", "error", "The result is not a supported preflight or sanitized native test report.",
                       "Supply original supported JSON saved by test plan or test run; raw SDK/TRX and unknown producers are not supported."),
    "report.publication": ("artifact", "error", "Report publication or temporary-file cleanup failed; the destination may already exist.",
                           "Inspect the destination before retrying; use an existing local directory and a regular .json destination, with --force only for intended replacement."),
    "report.stale": ("input", "error", "The explicitly selected workflow file differs from the recorded definition.",
                     "Create a new preflight report for the edited file; no native verdict is available."),
}


def finding(rule, source="options", pointer="", producer_version=None):
    category, severity, message, recommendation = RULES[rule]
    if rule == "input.options" and producer_version in _LEGACY_INPUT_OPTIONS_PRODUCERS:
        message = "Explicit local paths and a bounded workflow name are required."
        recommendation = "Supply --path and --workflow; do not use URLs, device paths or target contexts."
    if rule == "report.invalid" and producer_version in _LEGACY_REPORT_INVALID_PRODUCERS:
        message = "The result is not a supported foundation preflight report."
        recommendation = "Supply a report saved by test plan; native SDK/TRX/legacy reports are not supported."
    return {"rule": rule, "category": category, "severity": severity, "source": source,
            "jsonPointer": pointer, "message": message, "recommendation": recommendation}


def new_report(phase="preflight", strict=False):
    return {
        "reportType": "logicapp-test-foundation", "schemaVersion": SCHEMA,
        "invocationId": str(uuid.uuid4()), "phase": phase,
        "provenance": {"producer": "az.logicapp.test.plan" if phase == "preflight" else "az.logicapp.test.results.show",
                       "cliVersion": VERSION,
                       "evidence": "local-file-inspection", "authenticity": "notAttested"},
        "workflow": {"name": None, "kind": None, "definitionHash": None},
        "inputs": [],
        "coverage": {"static": "notChecked", "configurationReferences": "notChecked",
                     "nestedGraphs": "notChecked", "expressions": "notChecked",
                     "runtimeTemplate": "notChecked", "testDiscovery": "notChecked",
                     "businessBehavior": "notChecked", "externalIsolation": "notChecked"},
        "dependencies": {"sdkPackage": SDK_PACKAGE, "recommendedSdkVersion": "1.0.3",
                         "declaredSdkVersion": None, "declaredTargetFramework": None,
                         "installedSdkVersion": None, "resolvedEngineVersion": None,
                         "installedDotnetVersion": None, "runner": "notInspected",
                         "resolution": "notInspected"},
        "gates": {"sdkAdoption": "unresolved", "sdkRestore": "blocked", "sdkExecution": "blocked",
                  "platformQualification": "unknown", "networkIsolation": "unknown"},
        "qualification": "blocked", "executionState": "notExecuted", "businessTests": "notExecuted",
        "summary": {"executed": 0, "passed": 0, "failed": 0, "errors": 0, "warnings": 0},
        "findings": [], "inspection": None, "exitPolicy": "strict" if strict else "planning",
        "outcome": "blocked" if strict else "planned", "exitCode": 4 if strict else 0,
    }


def finalize(report):
    rows = report["findings"]
    report["summary"]["errors"] = sum(row["severity"] == "error" for row in rows)
    report["summary"]["warnings"] = sum(row["severity"] == "warning" for row in rows)
    rules = {row["rule"] for row in rows}
    if "report.publication" in rules:
        outcome, code = "publicationError", 6
    elif rules.intersection(("input.changed", "report.stale")):
        outcome, code = "stale", 5
    elif any(row["severity"] == "error" and row["category"] in ("input", "protocol") for row in rows):
        outcome, code = "inputError", 3
    elif report["phase"] == "inspection":
        outcome, code = "inspected", 0
    elif any(row["severity"] == "error" and row["category"] == "authoring" for row in rows):
        outcome, code = "authoringInvalid", 1
    elif report["schemaVersion"] == "1.0" or report["exitPolicy"] == "strict":
        outcome, code = "blocked", 4
    else:
        outcome, code = "planned", 0
    report.update(outcome=outcome, exitCode=code)
    return report


def _hash(value):
    return value is None or (isinstance(value, str) and re.fullmatch(r"sha256:[0-9a-f]{64}", value))


def _exact(actual, expected):
    return type(actual) is type(expected) and actual == expected


def _valid_header(value, template):
    if not isinstance(value, dict) or set(value) != set(template):
        return False
    legacy = value["schemaVersion"] == "1.0"
    if not legacy and value["exitPolicy"] not in ("planning", "strict"):
        return False
    variable = {"invocationId", "provenance", "workflow", "inputs", "coverage", "dependencies",
                "summary", "findings", "outcome", "exitCode", "exitPolicy"}
    if any(not _exact(value[key], template[key]) for key in set(template) - variable):
        return False
    provenance = value["provenance"]
    producers = _V1_PRODUCERS if legacy else _V2_PRODUCERS
    if not isinstance(provenance, dict) or provenance.get("cliVersion") not in producers:
        return False
    expected_provenance = dict(template["provenance"], cliVersion=provenance["cliVersion"])
    if not _exact(provenance, expected_provenance):
        return False
    if not isinstance(value["invocationId"], str):
        return False
    try:
        if str(uuid.UUID(value["invocationId"])) != value["invocationId"]:
            return False
    except ValueError:
        return False
    return True


def _valid_workflow(workflow, template):
    if not isinstance(workflow, dict) or set(workflow) != set(template):
        return False
    name = workflow["name"]
    if name is not None and (not isinstance(name, str) or
                             not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", name)):
        return False
    if workflow["kind"] not in (None, "Stateful", "Stateless") or not _hash(workflow["definitionHash"]):
        return False
    return True


def _valid_coverage_dependencies(value, template):
    coverage = value["coverage"]
    if not isinstance(coverage, dict) or set(coverage) != set(template["coverage"]):
        return False
    if coverage["static"] not in ("notChecked", "passedLimited", "failedLimited"):
        return False
    if coverage["configurationReferences"] not in ("notChecked", "checkedLiteralDeclarations"):
        return False
    if any(coverage[key] != "notChecked" for key in set(coverage) - {"static", "configurationReferences"}):
        return False
    deps = value["dependencies"]
    if not isinstance(deps, dict) or set(deps) != set(template["dependencies"]):
        return False
    if any(not _exact(deps[key], template["dependencies"][key])
           for key in set(deps) - {"declaredSdkVersion", "declaredTargetFramework"}):
        return False
    version = deps["declaredSdkVersion"]
    if version is not None and (not isinstance(version, str) or
                                not re.fullmatch(r"[0-9]{1,4}\.[0-9]{1,4}\.[0-9]{1,4}", version)):
        return False
    if deps["declaredTargetFramework"] not in (None, "net8.0", "net9.0", "net10.0"):
        return False
    return True


def _validated_inputs(inputs):
    if not isinstance(inputs, list) or len(inputs) > 6:
        return None
    seen = {}
    for item in inputs:
        if not isinstance(item, dict) or set(item) != {"role", "sha256", "sensitivity", "stable"}:
            return None
        role = item["role"]
        if not isinstance(role, str) or role not in ROLES[:6] or role in seen or not isinstance(item["stable"], bool):
            return None
        source = role in ("workflow", "testProject")
        if item["sensitivity"] != ("restricted-source" if source else "values-not-exported"):
            return None
        if not _hash(item["sha256"]) or (source and item["sha256"] is None) or (
                not source and item["sha256"] is not None):
            return None
        seen[role] = item
    return seen


def _valid_finding(row, schema, producer):
    if not isinstance(row, dict) or set(row) != set(finding("sdk.policy")):
        return False
    rule, source, pointer = row["rule"], row["source"], row["jsonPointer"]
    if not all(isinstance(item, str) for item in (rule, source, pointer)):
        return False
    if rule not in RULES or source not in ROLES or pointer not in POINTERS:
        return False
    if row == finding(rule, source, pointer, producer):
        return True
    # The unpublished public version spans both exact schema-2 guidance catalogs.
    return (schema == "2.0" and producer == "1.0.0b1" and rule in ("input.options", "report.invalid") and
            row == finding(rule, source, pointer))


def validate_report(value):
    """Validate each closed schema without reinterpreting historical exits."""
    if not isinstance(value, dict) or value.get("schemaVersion") not in ("1.0", SCHEMA):
        return False
    template = new_report()
    if value["schemaVersion"] == "1.0":
        template["schemaVersion"] = "1.0"
        del template["exitPolicy"]
    if not _valid_header(value, template):
        return False
    workflow = value["workflow"]
    if not _valid_workflow(workflow, template["workflow"]) or not _valid_coverage_dependencies(value, template):
        return False
    name = workflow["name"]
    coverage = value["coverage"]
    inputs, rows = value["inputs"], value["findings"]
    seen = _validated_inputs(inputs)
    if seen is None or not isinstance(rows, list) or len(rows) > 100:
        return False
    if workflow["definitionHash"] != (seen.get("workflow") or {}).get("sha256"):
        return False
    for row in rows:
        if not _valid_finding(row, value["schemaVersion"], value["provenance"]["cliVersion"]):
            return False
    if not all(any(row["rule"] == rule for row in rows)
               for rule in ("sdk.policy", "sdk.qualification", "scope.business")):
        return False
    if any(not item["stable"] and not any(
            row["rule"] == "input.changed" and row["source"] == item["role"] for row in rows) for item in inputs):
        return False
    if workflow["kind"] is not None and (name is None or workflow["definitionHash"] is None):
        return False
    if name is None and (inputs or coverage["static"] != "notChecked" or not any(
            row["rule"] == "input.options" for row in rows)):
        return False
    authoring_error = any(row["category"] == "authoring" and row["severity"] == "error" and
                          row["source"] == "workflow" for row in rows)
    if coverage["static"] == "passedLimited" and (
            authoring_error or workflow["kind"] is None or workflow["definitionHash"] is None):
        return False
    if coverage["static"] == "failedLimited" and not authoring_error:
        return False
    # JSON booleans and integer subclasses must not satisfy the closed scalar contract.
    if type(value["exitCode"]) is not int or not isinstance(value["summary"], dict):  # pylint: disable=unidiomatic-typecheck
        return False
    expected = finalize(copy.deepcopy(value))
    return (_exact(value["summary"], expected["summary"]) and
            all(type(value["summary"].get(key)) is int for key in template["summary"]) and  # pylint: disable=unidiomatic-typecheck
            set(value["summary"]) == set(template["summary"]) and
            all(value["summary"][key] == 0 for key in ("executed", "passed", "failed")) and
            value["outcome"] == expected["outcome"] and value["exitCode"] == expected["exitCode"])


def table_format(report):
    if report.get("reportType") == "logicapp-sdk-test":
        return [OrderedDict((("Phase", report["phase"]), ("Outcome", report["outcome"]),
                             ("Execution", report["executionState"]),
                             ("SourceOutcome", (report["inspection"] or {}).get("sourceOutcome", "")),
                             ("Executed", report["summary"]["executed"]),
                             ("Passed", report["summary"]["passed"]), ("Failed", report["summary"]["failed"]),
                             ("Skipped", report["summary"]["skipped"]), ("ExitCode", report["exitCode"]),
                             ("Reason", " ".join(row["message"] for row in report["findings"]))))]
    header = OrderedDict((("Phase", report["phase"]), ("Outcome", report["outcome"]),
                          ("Execution", report["executionState"]), ("ExitCode", report["exitCode"]),
                          ("Rule", ""), ("Severity", ""), ("Source", ""), ("Reason", "")))
    return [header] + [OrderedDict((("Phase", ""), ("Outcome", ""), ("Execution", ""),
                                   ("ExitCode", ""), ("Rule", row["rule"]),
                                   ("Severity", row["severity"]), ("Source", row["source"]),
                                   ("Reason", row["message"]))) for row in report["findings"]]
