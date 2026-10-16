# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Bounded local file preflight. No subprocesses, SDK loads or network probes."""

import copy
import hashlib
import json
import os
import re
import stat
import tempfile
import xml.etree.ElementTree as ET

from . import _test_report as protocol
from ._workflow import validate_workflow_document

MAX_BYTES = 1024 * 1024
MAX_DEPTH = 48
MAX_NODES = 20000
MAX_FINDINGS = 90
UNAVAILABLE = object()


class InputError(Exception):
    def __init__(self, rule):
        super().__init__(rule)
        self.rule = rule


def _path(value):
    if not isinstance(value, str) or not value.strip() or "\x00" in value or "://" in value:
        raise InputError("input.options")
    if value.startswith(("\\\\", "//")):
        raise InputError("input.unsafe")
    path = os.path.abspath(value)
    # Reject alternate streams/device names as well as linked ancestor directories.
    tail = os.path.splitdrive(path)[1]
    if ":" in tail:
        raise InputError("input.unsafe")
    for part in re.split(r"[\\/]", tail):
        if re.fullmatch(r"(?i)(con|prn|aux|nul|com[0-9]|lpt[0-9])(?:\..*)?", part):
            raise InputError("input.unsafe")
    current = path
    while True:
        if os.path.lexists(current):
            info = os.lstat(current)
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise InputError("input.unsafe")
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return path


def _read(path):
    try:
        path = _path(path)
        info = os.stat(path)
        if not stat.S_ISREG(info.st_mode):
            raise InputError("input.unsafe")
        if info.st_size > MAX_BYTES:
            raise InputError("input.tooLarge")
        with open(path, "rb") as handle:
            opened = os.fstat(handle.fileno())
            if not stat.S_ISREG(opened.st_mode) or (info.st_dev, info.st_ino) != (opened.st_dev, opened.st_ino):
                raise InputError("input.changed")
            data = handle.read(MAX_BYTES + 1)
            after = os.fstat(handle.fileno())
        if len(data) > MAX_BYTES:
            raise InputError("input.tooLarge")
        if (opened.st_size, opened.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise InputError("input.changed")
        _path(path)
        return data
    except OSError as ex:
        raise InputError("input.unreadable") from ex


def _json(data):
    # Check depth before invoking the recursive stdlib parser.
    depth, quoted, escaped = 0, False, False
    for byte in data:
        if quoted:
            if escaped:
                escaped = False
            elif byte == 92:
                escaped = True
            elif byte == 34:
                quoted = False
        elif byte == 34:
            quoted = True
        elif byte in (91, 123):
            depth += 1
            if depth > MAX_DEPTH:
                raise InputError("input.tooDeep")
        elif byte in (93, 125):
            depth -= 1
    try:
        from ._json import strict_json_loads
        payload = strict_json_loads(data.decode("utf-8-sig"))
    except (ValueError, UnicodeError, RecursionError) as ex:
        raise InputError("input.invalidJson") from ex
    nodes, pending = 0, [payload]
    while pending:
        item = pending.pop()
        nodes += 1
        if nodes > MAX_NODES:
            raise InputError("input.tooDeep")
        if isinstance(item, dict):
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)
        elif isinstance(item, float) and not (-float("inf") < item < float("inf")):
            raise InputError("input.invalidJson")
    return payload


def _digest(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _add(report, rule, source="options", pointer=""):
    row = protocol.finding(rule, source, pointer)
    if row not in report["findings"]:
        report["findings"].append(row)
    if len(report["findings"]) > MAX_FINDINGS:
        raise InputError("input.tooLarge")


def _input(report, snapshots, role, path, json_input=True):
    try:
        data = _read(path)
        snapshots[role] = (path, data)
        source = role in ("workflow", "testProject")
        item = {"role": role, "sha256": _digest(data) if source else None,
                "sensitivity": "restricted-source" if source else "values-not-exported", "stable": True}
        report["inputs"].append(item)
        if role == "workflow":
            report["workflow"]["definitionHash"] = item["sha256"]
        return _json(data) if json_input else data
    except InputError as ex:
        _add(report, ex.rule, role)
        return UNAVAILABLE


def _static(report, document):
    rows = []
    validate_workflow_document(document, report["workflow"]["name"], "workflow.json", rows)
    pointers = {
        "workflow.root": "", "workflow.kind.invalid": "/kind",
        "workflow.definition.missing": "/definition", "workflow.triggers.missing": "/definition/triggers",
        "workflow.actions.invalid": "/definition/actions", "trigger.invalid": "/definition/triggers",
        "trigger.kind.warning": "/definition/triggers", "action.invalid": "/definition/actions",
        "graph.run_after.invalid": "/definition/actions", "graph.missing_action": "/definition/actions",
    }
    for row in rows:
        rule = row["rule"]
        if rule in pointers:
            _add(report, rule, "workflow", pointers[rule])
    if isinstance(document, dict):
        if document.get("kind") in ("Stateful", "Stateless"):
            report["workflow"]["kind"] = document["kind"]
        definition = document.get("definition")
        if isinstance(definition, dict):
            if definition.get("$schema") != protocol.WORKFLOW_SCHEMA:
                _add(report, "workflow.schema", "workflow", "/definition/$schema")
            if not isinstance(definition.get("actions"), dict):
                _add(report, "workflow.actions.invalid", "workflow", "/definition/actions")
    report["coverage"]["static"] = (
        "failedLimited" if any(row["category"] == "authoring" and row["severity"] == "error"
                               for row in report["findings"]) else "passedLimited")


def _connection_references(definition, refs):
    dynamic = False
    for group in ("triggers", "actions"):
        operations = definition.get(group)
        for operation in operations.values() if isinstance(operations, dict) else ():
            if not isinstance(operation, dict):
                continue
            inputs = operation.get("inputs")
            if not isinstance(inputs, dict):
                continue
            connection = None
            if operation.get("type") in ("ApiConnection", "ApiConnectionWebhook"):
                host = inputs.get("host")
                host = host if isinstance(host, dict) else {}
                host_connection = host.get("connection")
                if isinstance(host_connection, dict):
                    connection = host_connection.get("referenceName")
            elif operation.get("type") == "ServiceProvider":
                configuration = inputs.get("serviceProviderConfiguration")
                if isinstance(configuration, dict):
                    connection = configuration.get("connectionName")
            if isinstance(connection, str):
                if re.fullmatch(r"[A-Za-z0-9_.-]{1,128}", connection):
                    refs["connections"].add(connection)
                else:
                    dynamic = True
    return dynamic


def _literal_references(document, refs):
    pending, dynamic = [document], False
    while pending:
        value = pending.pop()
        if isinstance(value, dict):
            pending.extend(value.values())
        elif isinstance(value, list):
            pending.extend(value)
        elif isinstance(value, str):
            for function, role in (("appsetting", "settings"), ("parameters", "parameters")):
                matches = re.findall(r"\b" + function + r"\(\s*'([A-Za-z0-9_.-]{1,128})'\s*\)", value)
                refs[role].update(matches)
                if len(re.findall(r"\b" + function + r"\(", value)) > len(matches):
                    dynamic = True
            if "$connections" in value:
                dynamic = True
    return dynamic


def _references(report, snapshots, root, document):
    refs = {"settings": set(), "parameters": set(), "connections": set()}
    definition = document.get("definition", {}) if isinstance(document, dict) else {}
    definition = definition if isinstance(definition, dict) else {}
    defaults = definition.get("parameters", {})
    defaults = {key for key, value in defaults.items() if isinstance(value, dict) and "defaultValue" in value} \
        if isinstance(defaults, dict) else set()
    connection_dynamic = _connection_references(definition, refs)
    literal_dynamic = _literal_references(document, refs)
    dynamic = connection_dynamic or literal_dynamic
    files = {"settings": "local.settings.json", "parameters": "parameters.json", "connections": "connections.json"}
    checked = False
    for role, names in refs.items():
        if not names:
            continue
        checked = True
        path = os.path.join(root, files[role])
        if role == "parameters" and not os.path.lexists(path) and names <= defaults:
            continue
        payload = _input(report, snapshots, role, path)
        if payload is UNAVAILABLE:
            continue
        declarations = None
        if isinstance(payload, dict):
            if role == "settings":
                if payload.get("IsEncrypted") is False:
                    declarations = payload.get("Values")
                else:
                    _add(report, "reference.dynamic", role)
                    continue
            elif role == "parameters":
                declarations = dict.fromkeys(payload.keys() | defaults)
            else:
                groups = [payload.get(key, {}) for key in (
                    "managedApiConnections", "serviceProviderConnections", "functionConnections")]
                if all(isinstance(group, dict) for group in groups):
                    declarations = {key: None for group in groups for key in group}
        if not isinstance(declarations, dict):
            _add(report, "reference.shape", role)
        elif names - declarations.keys():
            _add(report, "reference.missing", role)
    if checked:
        report["coverage"]["configurationReferences"] = "checkedLiteralDeclarations"
    if dynamic:
        _add(report, "reference.dynamic", "workflow")


def _test_project_xml(data):
    try:
        text = data.decode("utf-8-sig")
        if re.search(r"<!\s*(DOCTYPE|ENTITY)", text, re.IGNORECASE):
            raise ValueError("DTD")
        root = ET.fromstring(text)
        if root.tag.rsplit("}", 1)[-1] != "Project":
            raise ValueError("project")
        pending, count = [(root, 0)], 0
        while pending:
            element, depth = pending.pop()
            count += 1
            if depth > MAX_DEPTH or count > MAX_NODES:
                raise ValueError("bounds")
            pending.extend((child, depth + 1) for child in element)
    except (ValueError, UnicodeError, ET.ParseError) as ex:
        raise InputError("testProject.invalidXml") from ex
    return root


def _test_project(report, data):
    root = _test_project_xml(data)
    dynamic = any(element.tag.rsplit("}", 1)[-1] in (
        "Import", "ImportGroup", "Target", "Choose", "UsingTask", "ProjectReference") or
        "Condition" in element.attrib or any(token in (element.text or "") for token in ("$(", "@(", "%(")) or
        any("$(" in value or "@(" in value or "%(" in value for value in element.attrib.values())
        for element in root.iter())
    if "Sdk" in root.attrib:
        _add(report, "testProject.dynamic", "testProject")
    if any(token in (root.get("Sdk") or "") for token in ("$(", "@(", "%(")):
        dynamic = True
    # Only direct unconditional literal properties/references are declared evidence.
    frameworks, versions = [], []
    for group in root:
        if group.attrib:
            dynamic = True
            continue
        tag = group.tag.rsplit("}", 1)[-1]
        if tag == "PropertyGroup":
            for element in group:
                name = element.tag.rsplit("}", 1)[-1]
                if name == "TargetFramework" and not element.attrib and not list(element):
                    frameworks.append(element.text)
                elif name == "TargetFrameworks":
                    dynamic = True
        if tag == "ItemGroup":
            for element in group:
                if element.tag.rsplit("}", 1)[-1] == "PackageReference" and (
                        element.get("Include") == protocol.SDK_PACKAGE):
                    if set(element.attrib) == {"Include", "Version"} and not list(element):
                        version = element.get("Version")
                        if re.fullmatch(r"\[[0-9]{1,4}\.[0-9]{1,4}\.[0-9]{1,4}\]", version or ""):
                            version = version[1:-1]
                        versions.append(version)
                    else:
                        dynamic = True
    deps = report["dependencies"]
    if not dynamic:
        if len(frameworks) == 1 and frameworks[0] in ("net8.0", "net9.0", "net10.0"):
            deps["declaredTargetFramework"] = frameworks[0]
        if len(versions) == 1 and re.fullmatch(r"[0-9]{1,4}\.[0-9]{1,4}\.[0-9]{1,4}", versions[0]):
            deps["declaredSdkVersion"] = versions[0]
    if dynamic:
        _add(report, "testProject.dynamic", "testProject")
    if deps["declaredTargetFramework"] is None or deps["declaredSdkVersion"] is None:
        _add(report, "testProject.metadata", "testProject")


def _recheck(report, snapshots):
    for item in report["inputs"]:
        path, original = snapshots[item["role"]]
        try:
            changed = _read(path) != original
        except InputError:
            changed = True
        if changed:
            item["stable"] = False
            _add(report, "input.changed", item["role"])


def _scope(report):
    for rule in ("sdk.policy", "sdk.qualification", "scope.business"):
        _add(report, rule)


def _destination(path, force, protected):
    target = _path(path)
    parent = os.path.dirname(target)
    if (not target.lower().endswith(".json") or parent == os.path.dirname(parent) or
            not os.path.isdir(parent) or
            os.path.basename(target).lower() in (
                "workflow.json", "host.json", "local.settings.json", "parameters.json", "connections.json")):
        raise InputError("report.publication")
    if os.path.normcase(target) in protected:
        raise InputError("report.publication")
    if os.path.lexists(target):
        if not os.path.isfile(target) or not force:
            raise InputError("report.publication")
        for source in protected:
            if os.path.exists(source) and os.path.samefile(target, source):
                raise InputError("report.publication")
    return target


def _publish(report, path, force, protected):
    temporary = None
    try:
        target = _destination(path, force, protected)
        content = (json.dumps(report, ensure_ascii=True, allow_nan=False, indent=2) + "\n").encode("utf-8")
        if len(content) > MAX_BYTES:
            raise InputError("report.publication")
        with tempfile.NamedTemporaryFile(dir=os.path.dirname(target), prefix=".logicapp-test-",
                                         suffix=".tmp", delete=False) as handle:
            temporary = handle.name
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        _destination(target, force, protected)
        if force:
            os.replace(temporary, target)
        else:
            os.link(temporary, target)
    except OSError as ex:
        raise InputError("report.publication") from ex
    finally:
        if temporary and os.path.exists(temporary):
            try:
                os.unlink(temporary)
            except OSError as ex:
                raise InputError("report.publication") from ex


def plan_report(path, workflow, test_project=None, report_path=None, force=False, strict=False):
    report, snapshots, protected = protocol.new_report(strict=strict), {}, set()
    try:
        if not isinstance(workflow, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", workflow):
            raise InputError("input.options")
        report["workflow"]["name"] = workflow
        root = _path(path)
        if not os.path.isdir(root):
            raise InputError("input.unreadable")
        if force and report_path is None:
            raise InputError("input.options")
        workflow_path = os.path.join(root, workflow, "workflow.json")
        protected.update(os.path.normcase(os.path.join(root, name)) for name in (
            "host.json", "local.settings.json", "parameters.json", "connections.json"))
        protected.add(os.path.normcase(workflow_path))
        host = _input(report, snapshots, "host", os.path.join(root, "host.json"))
        if host is not UNAVAILABLE and (not isinstance(host, dict) or host.get("version") != "2.0" or
                                        not isinstance(host.get("extensionBundle"), dict) or
                                        host["extensionBundle"].get("id") != "Microsoft.Azure.Functions.ExtensionBundle.Workflows"):
            _add(report, "host.invalid", "host")
        document = _input(report, snapshots, "workflow", workflow_path)
        if document is not UNAVAILABLE:
            _static(report, document)
            _references(report, snapshots, root, document)
        if test_project is not None:
            selected = _path(test_project)
            protected.add(os.path.normcase(selected))
            if not selected.lower().endswith(".csproj"):
                raise InputError("input.options")
            data = _input(report, snapshots, "testProject", selected, json_input=False)
            if data is not UNAVAILABLE:
                try:
                    _test_project(report, data)
                except InputError as ex:
                    _add(report, ex.rule, "testProject")
        else:
            from ._test_scaffold import default_project
            generated = default_project(root, workflow)
            if os.path.lexists(generated):
                protected.add(os.path.normcase(generated))
                data = _input(report, snapshots, "testProject", generated, json_input=False)
                if data is not UNAVAILABLE:
                    try:
                        _test_project(report, data)
                    except InputError as ex:
                        _add(report, ex.rule, "testProject")
            else:
                _add(report, "testProject.absent", "testProject")
    except InputError as ex:
        _add(report, ex.rule)
    except OSError:
        _add(report, "input.unreadable")
    _scope(report)
    _recheck(report, snapshots)
    protocol.finalize(report)
    if report_path is not None:
        try:
            _publish(report, report_path, force, protected)
        except (InputError, OSError):
            _add(report, "report.publication", "report")
            protocol.finalize(report)
    return report


def results_report(result_file, workflow_file=None):
    report = protocol.new_report(phase="inspection")
    _scope(report)
    try:
        data = _read(result_file)
        candidate = _json(data)
        if isinstance(candidate, dict) and candidate.get("reportType") == "logicapp-sdk-test":
            from . import _sdk_testing
            if not _sdk_testing.validate_report(candidate):
                raise InputError("report.invalid")
            if _read(result_file) != data:
                raise InputError("input.changed")
            return _sdk_testing.results_report(candidate, workflow_file)
        if not protocol.validate_report(candidate):
            raise InputError("report.invalid")
        if _read(result_file) != data:
            raise InputError("input.changed")
    except InputError as ex:
        _add(report, ex.rule, "report")
        return protocol.finalize(report)
    report = copy.deepcopy(candidate)
    report.update(phase="inspection", invocationId=protocol.new_report()["invocationId"])
    report["provenance"]["producer"] = "az.logicapp.test.results.show"
    report["inspection"] = {"sourceInvocationId": candidate["invocationId"],
                            "sourceOutcome": candidate["outcome"], "sourceExitCode": candidate["exitCode"],
                            "workflowIdentity": "notChecked", "authenticity": "notAttested"}
    historical = report["findings"]
    report["findings"] = []
    if workflow_file is not None:
        try:
            current = _read(workflow_file)
            if report["workflow"]["definitionHash"] is None:
                report["inspection"]["workflowIdentity"] = "unavailable"
                _add(report, "report.invalid", "report")
            elif _digest(current) != report["workflow"]["definitionHash"]:
                report["inspection"]["workflowIdentity"] = "changed"
                _add(report, "report.stale", "workflow")
            elif _read(workflow_file) != current:
                report["inspection"]["workflowIdentity"] = "changed"
                _add(report, "input.changed", "workflow")
            else:
                report["inspection"]["workflowIdentity"] = "matches"
        except InputError as ex:
            report["inspection"]["workflowIdentity"] = "unavailable"
            _add(report, ex.rule, "workflow")
    protocol.finalize(report)
    report["findings"] = historical + [row for row in report["findings"] if row not in historical]
    report["summary"]["errors"] = sum(row["severity"] == "error" for row in report["findings"])
    report["summary"]["warnings"] = sum(row["severity"] == "warning" for row in report["findings"])
    return report
