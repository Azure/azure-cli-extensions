# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import fnmatch
import hashlib
import json
import os
import re
import zipfile

# pylint: disable=import-error,no-name-in-module
from azure.cli.core.azclierror import FileOperationError, InvalidArgumentValueError, MutuallyExclusiveArgumentError, ResourceNotFoundError, ValidationError

from ._constants import NATIVE_TEST_PROJECT_FILE, NATIVE_TEST_STATE_DIRECTORY, WORKFLOW_KINDS


HOST_JSON = {
    "version": "2.0",
    "extensionBundle": {
        "id": "Microsoft.Azure.Functions.ExtensionBundle.Workflows",
        "version": "[1.*, 2.0.0)"
    }
}

LOCAL_SETTINGS_JSON = {
    "IsEncrypted": False,
    "Values": {
        "AzureWebJobsStorage": "UseDevelopmentStorage=true",
        "FUNCTIONS_WORKER_RUNTIME": "node"
    }
}


def workflow_json(workflow_kind):
    return {
        "definition": {
            "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
            "contentVersion": "1.0.0.0",
            "triggers": {
                "manual": {
                    "type": "Request",
                    "kind": "Http",
                    "inputs": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"}
                            }
                        }
                    }
                }
            },
            "actions": {
                "Compose_greeting": {
                    "type": "Compose",
                    "inputs": {
                        "greeting": "@concat('hello ', coalesce(triggerBody()?['name'], 'world'))",
                        "correlationId": "@workflow()['run']['name']"
                    },
                    "runAfter": {}
                },
                "Response": {
                    "type": "Response",
                    "kind": "Http",
                    "inputs": {
                        "statusCode": 200,
                        "body": "@outputs('Compose_greeting')"
                    },
                    "runAfter": {
                        "Compose_greeting": ["Succeeded"]
                    }
                }
            },
            "outputs": {}
        },
        "kind": workflow_kind
    }


def abs_path(path):
    return os.path.abspath(os.path.expanduser(path or os.curdir))


def create_workflow_file(root, workflow, workflow_kind=None, definition_file=None, force=False):
    """Add one workflow to an existing project.

    Additive by design: it writes only ``<root>/<workflow>/workflow.json`` and never
    touches ``host.json`` or ``local.settings.json``, so adding a second workflow
    does not require the destructive ``--force`` that ``project create`` needs.
    """
    root = abs_path(root)
    if not os.path.isfile(os.path.join(root, "host.json")):
        raise ResourceNotFoundError(
            "Logic Apps project not found at '{root}'. Run 'az logicapp project create --path {root}' first.".format(root=root))
    validate_workflow_name(workflow)
    if definition_file:
        payload = _load_definition_file(definition_file)
    else:
        payload = workflow_json(workflow_kind or "Stateful")
    if workflow_kind:
        payload["kind"] = workflow_kind
    payload.setdefault("kind", "Stateful")
    if payload["kind"] not in WORKFLOW_KINDS:
        raise InvalidArgumentValueError("kind must be one of {}.".format(", ".join(WORKFLOW_KINDS)))
    target = os.path.join(root, workflow, "workflow.json")
    if os.path.exists(target) and not force:
        raise ValidationError("Workflow '{}' already exists at {}. Use --force to replace it.".format(workflow, target))
    item = write_json_file(target, payload, force=True)
    item["class"] = "workflowDefinition"
    return {
        "path": root,
        "workflow": workflow,
        "workflowKind": payload["kind"],
        "source": os.path.abspath(definition_file) if definition_file else "template",
        "files": [item],
    }


def _load_definition_file(definition_file):
    from ._json import strict_json_loads

    path = os.path.abspath(os.path.expanduser(definition_file))
    if not os.path.isfile(path):
        raise ResourceNotFoundError("Definition file not found: {}".format(path))
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = strict_json_loads(handle.read())
    except (ValueError, RecursionError) as ex:
        raise InvalidArgumentValueError("{} is not valid JSON: {}".format(path, ex)) from ex
    except OSError as ex:
        raise FileOperationError("Could not read {}".format(path)) from ex
    if not isinstance(payload, dict):
        raise InvalidArgumentValueError("{} must contain a JSON object.".format(path))
    if "definition" not in payload and "triggers" in payload:
        payload = {"definition": payload}
    definition = payload.get("definition")
    if not isinstance(definition, dict):
        raise InvalidArgumentValueError("{} must contain a 'definition' object.".format(path))
    triggers = definition.get("triggers")
    if not isinstance(triggers, dict) or not triggers:
        raise InvalidArgumentValueError("{} must define at least one trigger.".format(path))
    actions = definition.get("actions")
    if actions is not None and not isinstance(actions, dict):
        raise InvalidArgumentValueError("{} has a non-object 'actions'.".format(path))
    return payload


def validate_workflow_name(name):
    if not name:
        return
    if os.path.basename(name) != name or name in (".", "..") or not re.match(r"^[A-Za-z0-9][A-Za-z0-9._-]*$", name):
        raise InvalidArgumentValueError("Workflow name '{}' is not valid.".format(name))


def write_json_file(path, payload, force=False):
    existed = os.path.exists(path)
    if existed and not force:
        raise ValidationError("File exists and requires --force: {}".format(path))
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        content = json.dumps(payload, indent=2, sort_keys=False) + "\n"
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
    except OSError as ex:
        raise FileOperationError("Could not write file: {}".format(path)) from ex
    return {
        "path": os.path.abspath(path),
        "bytesWritten": len(content.encode("utf-8")),
        "action": "updated" if existed else "created"
    }


def discover_workflows(root, workflow=None, all_workflows=False):
    root = abs_path(root)
    if workflow and all_workflows:
        raise MutuallyExclusiveArgumentError("--workflow and --all cannot be used together.")
    if workflow:
        validate_workflow_name(workflow)
        return [(workflow, os.path.join(root, workflow, "workflow.json"))]
    found = []
    for name in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        candidate = os.path.join(root, name, "workflow.json")
        if os.path.isfile(candidate):
            found.append((name, candidate))
    if all_workflows:
        return found
    if len(found) == 1:
        return found
    if not found:
        raise ResourceNotFoundError("No workflow.json files were found under '{}'.".format(root))
    raise ValidationError("Multiple workflows found. Use --workflow or --all.")


def static_validate(root, workflow=None, all_workflows=False):
    findings = []
    workflows = discover_workflows(root, workflow, all_workflows)
    for workflow_name, path in workflows:
        _validate_one(workflow_name, path, findings)
    errors = len([item for item in findings if item["severity"] == "error"])
    warnings = len([item for item in findings if item["severity"] == "warning"])
    return {
        "valid": errors == 0,
        "summary": {"errors": errors, "warnings": warnings, "workflows": len(workflows)},
        "coverage": {
            "static": True,
            "runtime": False,
            "checks": {
                "jsonParse": True,
                "workflowSchema": True,
                "graphReferences": True,
                "connectionReferences": True,
                "appSettingReferences": True,
                "runtimeTemplate": False
            }
        },
        "findings": findings
    }


def _finding(findings, workflow, path, json_path, rule, severity, message, recommendation):
    findings.append({
        "workflow": workflow,
        "file": os.path.abspath(path),
        "jsonPath": json_path,
        "rule": rule,
        "severity": severity,
        "message": message,
        "recommendation": recommendation
    })


def _validate_one(workflow, path, findings):
    from ._json import strict_json_loads

    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = strict_json_loads(handle.read())
    except (ValueError, RecursionError) as ex:
        _finding(findings, workflow, path, "$", "json.invalid", "error", "workflow.json is not valid JSON: {}".format(ex), "Fix JSON syntax.")
        return
    except OSError as ex:
        _finding(findings, workflow, path, "$", "workflow.file_unreadable", "error", "workflow.json could not be read: {}".format(ex), "Check the path and permissions.")
        return
    validate_workflow_document(payload, workflow, path, findings)


def validate_workflow_document(payload, workflow, path, findings):
    if not isinstance(payload, dict):
        _finding(findings, workflow, path, "$", "workflow.root", "error", "workflow.json must be a JSON object.", "Use the Logic Apps Standard workflow.json object shape.")
        return
    kind = payload.get("kind")
    if kind not in ("Stateful", "Stateless"):
        _finding(findings, workflow, path, "$.kind", "workflow.kind.invalid", "error", "kind must be Stateful or Stateless.", "Set kind to Stateful or Stateless.")
    definition = payload.get("definition")
    if not isinstance(definition, dict):
        _finding(findings, workflow, path, "$.definition", "workflow.definition.missing", "error", "definition must be an object.", "Add a workflow definition object.")
        return
    triggers = definition.get("triggers")
    actions = definition.get("actions")
    if not isinstance(triggers, dict) or not triggers:
        _finding(findings, workflow, path, "$.definition.triggers", "workflow.triggers.missing", "error", "definition.triggers must be a non-empty object.", "Add at least one trigger.")
        triggers = {}
    if not isinstance(actions, dict):
        _finding(findings, workflow, path, "$.definition.actions", "workflow.actions.invalid", "error", "definition.actions must be an object.", "Use an object for actions.")
        actions = {}
    actions = actions or {}
    for trigger_name, trigger in triggers.items():
        if not isinstance(trigger, dict):
            _finding(findings, workflow, path, "$.definition.triggers.{}".format(trigger_name), "trigger.invalid", "error", "Trigger must be an object.", "Use an object trigger definition.")
            continue
        trigger_type = trigger.get("type")
        trigger_kind = trigger.get("kind")
        if trigger_type == "Request" and trigger_kind not in (None, "Http"):
            _finding(findings, workflow, path, "$.definition.triggers.{}.kind".format(trigger_name), "trigger.kind.warning", "warning", "Request trigger kind is usually Http.", "Confirm the trigger kind is intentional.")
    for action_name, action in actions.items():
        if not isinstance(action, dict):
            _finding(findings, workflow, path, "$.definition.actions.{}".format(action_name), "action.invalid", "error", "Action must be an object.", "Use an object action definition.")
            continue
        run_after = action.get("runAfter")
        if run_after is None:
            run_after = {}
        if not isinstance(run_after, dict):
            _finding(findings, workflow, path, "$.definition.actions.{}.runAfter".format(action_name), "graph.run_after.invalid", "error", "runAfter must be an object.", "Use action-name keys with dependency statuses.")
            continue
        for target in run_after:
            if target not in actions:
                _finding(findings, workflow, path, "$.definition.actions.{}.runAfter.{}".format(action_name, target), "graph.missing_action", "error", "runAfter references missing action '{}'.".format(target), "Reference an existing action name.")
    text = json.dumps(payload)
    if "@appsetting(" in text or "appsetting(" in text:
        _finding(findings, workflow, path, "$", "appsetting.offline_unverified", "warning", "App setting references cannot be resolved during offline validation.", "Run with --with-runtime or verify application settings separately.")
    if '"$connections"' in text:
        _finding(findings, workflow, path, "$", "connection.offline_unverified", "warning", "Connection references cannot be fully resolved during offline validation.", "Run with --with-runtime or verify connections separately.")


EXCLUDED_DIRS = {".git", ".hg", ".svn", "__pycache__", ".pytest_cache", ".mypy_cache", ".tox", "node_modules", ".azurelogicapps"}
EXCLUDED_FILES = {"local.settings.json"}
# Source-control and tooling metadata describes the working copy, not the app. The
# matching directories were already excluded, so shipping the dotfiles beside them was
# inconsistent as well as useless to the runtime.
METADATA_FILES = {".gitignore", ".gitattributes", ".hgignore", ".dockerignore", ".funcignore"}
EXCLUDED_SUFFIXES = (".pyc", ".pyo", ".log")
IGNORE_FILE = ".funcignore"
NORMALIZED_ZIP_DT = (1980, 1, 1, 0, 0, 0)


def deterministic_package(root, output_path, manifest_path=None, force=False):
    root = abs_path(root)
    if not os.path.isfile(os.path.join(root, "host.json")):
        raise ResourceNotFoundError("Logic Apps project not found at '{}'.".format(root))
    output_path = os.path.abspath(output_path)
    manifest_path = os.path.abspath(manifest_path or (output_path + ".manifest.json"))
    _distinct_package_outputs(output_path, manifest_path)
    if not force:
        for target in (output_path, manifest_path):
            if os.path.exists(target):
                raise ValidationError("Output exists and requires --force: {}".format(target))
    included, excluded = _walk_package(root, output_path, manifest_path)
    for item in included:
        _scan_secret(os.path.join(root, item["path"]), item["path"])
    try:
        os.makedirs(os.path.dirname(output_path) or os.curdir, exist_ok=True)
        with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for item in included:
                archive_path = item["path"]
                info = zipfile.ZipInfo(archive_path, NORMALIZED_ZIP_DT)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                with open(os.path.join(root, archive_path.replace("/", os.sep)), "rb") as handle:
                    archive.writestr(info, handle.read())
        content_hash = "sha256:" + _sha256_file(output_path)
        manifest_payload = {
            "contentHash": content_hash,
            "deterministic": True,
            "included": included,
            "excluded": excluded
        }
        with open(manifest_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(manifest_payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
    except OSError as ex:
        raise FileOperationError("Could not write package output.") from ex
    return {
        "archivePath": output_path,
        "manifestPath": manifest_path,
        "contentHash": content_hash,
        "bytesWritten": os.path.getsize(output_path),
        "fileCount": len(included),
        "excludedCount": len(excluded),
        "deterministic": True,
        "included": included,
        "excluded": excluded
    }


def _distinct_package_outputs(output_path, manifest_path):
    try:
        same = os.path.normcase(os.path.realpath(output_path)) == os.path.normcase(os.path.realpath(manifest_path))
        if not same and os.path.lexists(output_path) and os.path.lexists(manifest_path):
            same = os.path.samefile(output_path, manifest_path)
    except OSError as ex:
        raise FileOperationError("Could not verify distinct package and manifest destinations.") from ex
    if same:
        raise ValidationError("Package and manifest destinations must be distinct files.")


def _native_test_project(path):
    from . import _testing  # Reuse bounded, non-evaluating XML inspection.
    try:
        document = _testing._test_project_xml(_testing._read(path))  # pylint: disable=protected-access
    except _testing.InputError as ex:
        raise ValidationError(
            "Could not establish a dedicated native test directory from project metadata.") from ex
    declarations, sdk_reference = [], False
    for group in document:
        for element in group:
            tag = element.tag.rsplit("}", 1)[-1]
            if group.tag.rsplit("}", 1)[-1] == "PropertyGroup" and tag == "IsTestProject":
                declarations.append(not group.attrib and not element.attrib and not list(element) and
                                    (element.text or "").strip().lower() == "true")
            if (group.tag.rsplit("}", 1)[-1] == "ItemGroup" and tag == "PackageReference" and
                    not group.attrib and "Condition" not in element.attrib and
                    (element.get("Include") or "").lower() == _testing.protocol.SDK_PACKAGE.lower()):
                sdk_reference = True
    intent = sdk_reference or any(declarations)
    if intent and not all(declarations):
        raise ValidationError("Conflicting native test metadata requires a dedicated, unambiguous test directory.")
    return intent


def _dedicated_test_directory(directory, root, dirnames, filenames):
    names = {name.lower() for name in dirnames + filenames}
    marked = NATIVE_TEST_PROJECT_FILE.lower() in names or NATIVE_TEST_STATE_DIRECTORY in names
    projects = [name for name in filenames if name.lower().endswith(".csproj")]
    test_projects = [name for name in projects if _native_test_project(os.path.join(directory, name))]
    if not marked and not test_projects:
        return False
    if (directory == root or names.intersection(("host.json", "workflow.json")) or not test_projects or
            len(test_projects) != len(projects) or
            NATIVE_TEST_STATE_DIRECTORY in {name.lower() for name in filenames}):
        raise ValidationError(
            "Native test sources or state require a dedicated test directory, separate from runtime content.")
    artifact_dirs = {"bin", "obj", "fixtures", "testresults", NATIVE_TEST_STATE_DIRECTORY}
    for _current, children, files in os.walk(directory, onerror=_package_walk_error):
        children[:] = [name for name in children if name.lower() not in artifact_dirs]
        if any(name.lower() in ("host.json", "workflow.json") or
               name.lower().endswith((".dll", ".exe")) for name in files):
            raise ValidationError(
                "Ambiguous runtime content in a native test directory. Move it into a dedicated test directory.")
    return True


def _package_walk_error(error):
    raise FileOperationError("Could not inspect package input directories.") from error


def _walk_package(root, output_path, manifest_path):
    included = []
    excluded = []
    output_abs = os.path.abspath(output_path)
    manifest_abs = os.path.abspath(manifest_path)
    ignore_patterns = _read_ignore_file(root)
    for directory, dirnames, filenames in os.walk(root, onerror=_package_walk_error):
        if _dedicated_test_directory(directory, root, dirnames, filenames):
            excluded.append({"path": os.path.relpath(directory, root).replace(os.sep, "/"),
                             "reason": "native-test-project"})
            dirnames[:] = []
            continue
        dirnames[:] = sorted([name for name in dirnames if not _exclude_dir(name, directory, root, excluded)])
        for filename in sorted(filenames):
            full = os.path.abspath(os.path.join(directory, filename))
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            reason = _exclude_file(filename, full, output_abs, manifest_abs)
            if not reason and _matches_ignore(rel, ignore_patterns):
                reason = "ignoreFile"
            if reason:
                excluded.append({"path": rel, "reason": reason})
                continue
            size = os.path.getsize(full)
            included.append({"path": rel, "bytes": size, "sha256": _sha256_file(full), "class": _classify(rel)})
    return included, sorted(excluded, key=lambda item: item["path"])


def _read_ignore_file(root):
    """Patterns from an optional .funcignore, so local test payloads stay out of a package.

    Without this the only way to keep a scratch file out was to move it outside the
    project, because every unrecognized file was packaged as class "other".
    """
    path = os.path.join(root, IGNORE_FILE)
    try:
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except FileNotFoundError as ex:
        if not os.path.lexists(path):
            return []
        raise FileOperationError("Could not read existing .funcignore exclusions.") from ex
    except (OSError, UnicodeError) as ex:
        raise FileOperationError("Could not read existing .funcignore exclusions.") from ex
    patterns = []
    for line in lines:
        entry = line.strip()
        if entry and not entry.startswith("#"):
            patterns.append(entry.rstrip("/"))
    return patterns


def _matches_ignore(rel, patterns):
    if not patterns:
        return False
    candidates = [rel, os.path.basename(rel)]
    for pattern in patterns:
        for candidate in candidates:
            if fnmatch.fnmatch(candidate, pattern):
                return True
        # A bare directory name in the ignore file covers everything beneath it.
        if rel.startswith(pattern.rstrip("*").rstrip("/") + "/"):
            return True
    return False


def _exclude_dir(name, directory, root, excluded):
    if name not in EXCLUDED_DIRS:
        return False
    rel = os.path.relpath(os.path.join(directory, name), root).replace(os.sep, "/")
    reason = "source-control" if name in (".git", ".hg", ".svn") else "cache" if "cache" in name or name == "__pycache__" else "runtime-state" if name == ".azurelogicapps" else "cache"
    excluded.append({"path": rel, "reason": reason})
    return True


def _exclude_file(filename, full, output_abs, manifest_abs):
    if os.path.abspath(full) in (output_abs, manifest_abs):
        return "package-output"
    if filename.lower() in EXCLUDED_FILES:
        return "secret"
    if filename in METADATA_FILES:
        return "metadata"
    if filename.lower().endswith(".trx"):
        return "native-test-results"
    if filename.endswith(EXCLUDED_SUFFIXES):
        return "log" if filename.endswith(".log") else "cache"
    return None


def _classify(rel):
    lowered = rel.lower()
    if lowered == "host.json":
        return "hostConfiguration"
    if lowered.endswith("/workflow.json"):
        return "workflowDefinition"
    if lowered.endswith("parameters.json"):
        return "parameters"
    if lowered.endswith("connections.json"):
        return "connections"
    return "other"


SECRET_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in (r"AccountKey\s*=", r"SharedAccessSignature\s*=", r"client_secret", r"password\s*[:=]", r"[?&]sig=")]


def _scan_secret(path, rel):
    try:
        with open(path, "rb") as handle:
            data = handle.read(1024 * 1024)
    except OSError as ex:
        raise FileOperationError("Could not read package input: {}".format(rel)) from ex
    text = data.decode("utf-8", errors="ignore")
    if any(pattern.search(text) for pattern in SECRET_PATTERNS):
        raise ValidationError("Potential secret detected in package input: {}".format(rel))


def _sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()
