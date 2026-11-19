# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Read-only, local-only preflight. Never return configuration or process output."""

import os
import re
import shutil
import socket
import subprocess
import time
from collections import OrderedDict
from functools import partial
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPHandler, HTTPRedirectHandler, ProxyHandler, Request, build_opener

import psutil

from . import _context, _local
from ._http_deadline import DeadlineHTTPConnection, remaining_timeout
from ._json import strict_json_loads
from ._workflow import abs_path, discover_workflows, validate_workflow_document


REQUIREMENTS_SOURCE = (
    "https://learn.microsoft.com/azure/logic-apps/create-standard-workflows-visual-studio-code")
FUNCTIONS_SOURCE = "https://learn.microsoft.com/azure/azure-functions/functions-run-local"
_VERSION = re.compile(r"v?(\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?)")
_NAME = re.compile(r"^[A-Za-z0-9_$][A-Za-z0-9_.$:-]{0,255}$")
_CALL = re.compile(r"(appsetting|parameters)\(\s*'([A-Za-z0-9_$][A-Za-z0-9_.$:-]{0,255})'\s*\)",
                   re.IGNORECASE)
_EXACT_CALL = re.compile(r"^@(appsetting|parameters)\(\s*'([A-Za-z0-9_$][A-Za-z0-9_.$:-]{0,255})'\s*\)$",
                         re.IGNORECASE)
_BUNDLE_RANGE = re.compile(r"^\[(\d+)\.\*,\s*(\d+)\.0\.0\)$")
_MAX_JSON = 4 * 1024 * 1024


def _finding(rows, check, status, required, reason, action, **evidence):
    rows.append({"check": check, "status": status, "required": required,
                 "reason": reason, "recommendation": action, "evidence": evidence})


def _read_json(path, rows, check, required=True, optional=False):
    try:
        with open(path, "rb") as handle:
            content = handle.read(_MAX_JSON + 1)
        if len(content) > _MAX_JSON:
            _finding(rows, check, "unknown", required, "File exceeds the diagnostic size limit.",
                     "Inspect this file manually; doctor does not read files above 4 MiB.")
            return None
        payload = strict_json_loads(content.decode("utf-8-sig"))
    except FileNotFoundError:
        _finding(rows, check, "skipped" if optional else "fail", required,
                 "Optional file is absent." if optional else "Required file is absent.",
                 "No action needed." if optional else "Create or restore the required project file.")
        return None
    except (OSError, UnicodeError, ValueError, RecursionError):
        _finding(rows, check, "fail", required, "File cannot be read as valid UTF-8 JSON.",
                 "Check file permissions and JSON syntax; contents were not included.")
        return None
    if not isinstance(payload, dict):
        _finding(rows, check, "fail", required, "File must contain a JSON object.",
                 "Use the documented project file object shape.")
        return None
    pending = [(payload, 0)]
    while pending:
        node, depth = pending.pop()
        if depth > 128:
            _finding(rows, check, "unknown", required, "File exceeds the diagnostic nesting limit.",
                     "Inspect deeply nested content manually; doctor supports at most 128 levels.")
            return None
        if isinstance(node, dict):
            pending.extend((value, depth + 1) for value in node.values())
        elif isinstance(node, list):
            pending.extend((value, depth + 1) for value in node)
    _finding(rows, check, "pass", required, "File is a readable JSON object.",
             "No action needed.")
    return payload


def _target(rows, path, context, port):
    if context is not None and (path is not None or port is not None):
        _finding(rows, "target.local", "fail", True,
                 "--context cannot be combined with --path or --port.",
                 "Use the saved local target, or explicit --path/--port.")
        return None, None
    ctx = None
    if context is not None or path is None:
        try:
            ctx, _ = _context.get_context(context)
        except (OSError, TypeError, ValueError, _context.CLIError):
            _finding(rows, "target.local", "fail", True, "Context could not be resolved.",
                     "Check the named/active context and context store; doctor never changes it.")
            return None, None
    target = ctx.get("target") if isinstance(ctx, dict) else None
    if ctx is not None and (not isinstance(target, dict) or target.get("kind") != "local"):
        _finding(rows, "target.local", "fail", True, "Doctor only supports local contexts.",
                 "Pass --path for a local project or select a named local --context.")
        return None, None
    resolved_path = path if path is not None else (target.get("path") if target else os.curdir)
    if not isinstance(resolved_path, str) or not resolved_path:
        _finding(rows, "target.local", "fail", True, "Local target has no project path.",
                 "Use a local context with a project path, or pass --path.")
        return None, None
    try:
        resolved_port = _local.validate_port(port if port is not None else
                                             target.get("port") if target else None)
        root = abs_path(resolved_path)
    except (ValueError, OSError, _local.InvalidArgumentValueError):
        _finding(rows, "target.local", "fail", True, "Local project path or port is invalid.",
                 "Choose a valid local project path and a port between 1 and 65535.")
        return None, None
    _finding(rows, "target.local", "pass", True, "Selected a local project without changing context.",
             "No action needed.")
    return root, resolved_port


def _probe_version(path, environment, timeout):
    if os.path.splitext(path)[1].lower() == ".ps1":
        return None, "PowerShell-only launcher was not executed."
    environment = dict(environment, DOTNET_SKIP_FIRST_TIME_EXPERIENCE="1",
                       DOTNET_CLI_TELEMETRY_OPTOUT="1", DOTNET_NOLOGO="1",
                       FUNCTIONS_CORE_TOOLS_TELEMETRY_OPTOUT="1")
    try:
        result = subprocess.run([path, "--version"], env=environment, cwd=os.path.dirname(path),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                universal_newlines=True, errors="replace",
                                timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return None, "Version probe timed out."
    except (OSError, subprocess.SubprocessError):
        return None, "Version probe could not execute."
    if result.returncode:
        return None, "Version probe returned a nonzero exit."
    match = _VERSION.fullmatch((result.stdout or "").strip())
    return (match.group(1), "Version was read.") if match else (
        None, "Version probe output was not a recognized version; output was discarded.")


def _tools(rows, timeout, needs_azurite):
    func, source = _local.find_tool("core-tools")
    environment = _local.dependency_environment(func)
    versions = {}
    selections = {}
    for kind, executable in (("core-tools", "func"), ("node", "node"),
                             ("dotnet", "dotnet"), ("azurite", "azurite")):
        path = func if kind == "core-tools" else _local.find_tool(kind)[0] if kind == "azurite" else (
            shutil.which(executable, path=environment["PATH"]))
        required = kind in ("core-tools", "node")
        selections[kind] = path
        if kind == "azurite" and not needs_azurite:
            _finding(rows, "tools.azurite", "skipped", False,
                     "Local emulator tooling is not required by the evaluated storage configuration.",
                     "No action needed.")
            continue
        if not path:
            _finding(rows, "tools." + kind, "fail" if required else "warn", required,
                     "Tool is absent from the runtime child environment.",
                     _local._remediation(kind),  # pylint: disable=protected-access
                     path=None, version=None)
            continue
        child_environment = _local.dependency_environment(path) if kind == "azurite" else environment
        version, reason = _probe_version(path, child_environment, timeout)
        versions[kind] = version
        _finding(rows, "tools." + kind, "pass" if version else "unknown", required, reason,
                 "No action needed." if version else "Verify the selected executable manually.",
                 path=path, version=version, source=source if kind == "core-tools" else "child-path")
        if kind == "azurite":
            node = shutil.which("node", path=child_environment["PATH"])
            _finding(rows, "tools.azurite-node", "unknown" if node else "fail", bool(needs_azurite),
                     "Selected Node for the Azurite launcher; launcher-specific engine support is not certified."
                     if node else "Azurite launcher has no selected Node.",
                     "Check the installed Azurite package engines against this selected Node.",
                     path=node)
    version = versions.get("core-tools")
    status = "unknown" if not version else "pass" if version.split(".", 1)[0] == "4" else "fail"
    _finding(rows, "compatibility.functions-major", status, True,
             "Functions 4.x is the supported local tooling major; this does not certify a bundle pair.",
             "Select Functions Core Tools 4.x, then verify compatibility with the configured Workflows bundle.",
             source=FUNCTIONS_SOURCE)
    _finding(rows, "compatibility.tool-bundle", "unknown", True,
             "An exact selected Core Tools/Node/.NET/Workflows bundle compatibility matrix is not available locally.",
             "Compare the selected tools with Logic Apps Standard prerequisites and validate a local host separately.",
             source=REQUIREMENTS_SOURCE)
    return selections


def _bundle(rows, host, values=None):
    if any(name.lower().startswith("azurefunctionsjobhost__extensionbundle__")
           for name in set(os.environ).union(values or ())):
        _finding(rows, "configuration.bundle", "unknown", True, "A bundle configuration override is present.",
                 "Verify the effective bundle configuration manually; doctor does not infer override precedence.")
        _finding(rows, "bundle.cache", "skipped", True, "Effective bundle cache is not established.",
                 "Inspect the configured override separately.")
        return
    config = host.get("extensionBundle") if isinstance(host, dict) else None
    if not isinstance(config, dict) or config.get("id") != _local.BUNDLE_ID or not isinstance(config.get("version"), str):
        _finding(rows, "configuration.bundle", "fail" if host is not None else "unknown", True,
                 "Workflows extensionBundle id and version range were not found.",
                 "Configure the Microsoft.Azure.Functions.ExtensionBundle.Workflows bundle in host.json.")
        return
    _finding(rows, "configuration.bundle", "pass", True, "Workflows bundle id and range are configured.",
             "No action needed.")
    if config.get("downloadPath"):
        _finding(rows, "bundle.cache", "unknown", True, "A bundle cache/configuration override is present.",
                 "Verify the effective bundle configuration manually; doctor does not infer override precedence.")
        return
    match = _BUNDLE_RANGE.fullmatch(config["version"].replace(" ", ""))
    if not match:
        _finding(rows, "bundle.cache", "unknown", True, "Bundle range is outside doctor's supported range syntax.",
                 "Inspect the configured bundle range and cache manually; no bundle was downloaded.")
        return
    lower, upper = map(int, match.groups())
    if lower >= upper:
        _finding(rows, "configuration.bundle-range", "fail", True, "Bundle range is empty.",
                 "Set a nonempty supported bundle version range.")
        return
    cache = _local.bundle_install_root()
    try:
        names = os.listdir(cache)
    except FileNotFoundError:
        names = []
    except OSError:
        _finding(rows, "bundle.cache", "unknown", True, "Functions bundle cache could not be read.",
                 "Check access to the selected user's Functions bundle cache.")
        return
    candidates = [name for name in names if re.fullmatch(r"\d+\.\d+\.\d+", name) and
                  lower <= int(name.split(".", 1)[0]) < upper and
                  os.path.isfile(os.path.join(cache, name, "bin", "extensions.json"))]
    _finding(rows, "bundle.cache", "pass" if candidates else "unknown", True,
             "A matching cache directory has bin/extensions.json; loading was not tested." if candidates else
             "No matching complete cache entry was found; an offline launch may need a download.",
             "Verify bundle load with a separately started host; doctor never downloads bundles.",
             path=cache, versions=sorted(candidates))


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _strings(child)


def _references(rows, document, check, settings, parameters):
    missing = {"appsetting": set(), "parameters": set()}
    uncertain = False
    for text in _strings(document):
        if not text.startswith("@") or text.startswith("@@"):
            continue
        call = _EXACT_CALL.fullmatch(text)
        if not call:
            if _CALL.search(text) or re.search(r"\b(appsetting|parameters)\s*\(", text, re.IGNORECASE):
                uncertain = True
            continue
        kind, name = call.groups()
        kind = kind.lower()
        available = settings if kind == "appsetting" else parameters
        if available is None:
            uncertain = True
        elif name not in available:
            if any(key.casefold() == name.casefold() for key in available):
                uncertain = True
            else:
                missing[kind].add(name)
    _finding(rows, check, "fail" if any(missing.values()) else "unknown" if uncertain else "pass", True,
             "Literal references are missing." if any(missing.values()) else
             "Case-variant/dynamic/composite references or unavailable sources cannot be resolved offline." if uncertain else
             "No missing supported literal references were found; this is not expression evaluation.",
             "Define the listed names and inspect dynamic references manually." if any(missing.values()) or uncertain else
             "No action needed.",
             missingAppSettings=sorted(missing["appsetting"]), missingParameters=sorted(missing["parameters"]),
             unresolvedExpressions=uncertain)


def _configuration(rows, root):
    host = _read_json(os.path.join(root, "host.json"), rows, "configuration.host-json")
    if host is not None:
        _finding(rows, "configuration.host-version", "pass" if host.get("version") == "2.0" else "fail", True,
                 "Functions host schema version must be 2.0.", "Set host.json version to 2.0.")
    settings = _read_json(os.path.join(root, "local.settings.json"), rows, "configuration.local-settings")
    values = settings.get("Values") if settings else None
    if settings is not None:
        valid = isinstance(values, dict) and all(isinstance(value, str) for value in values.values())
        _finding(rows, "configuration.settings-values", "pass" if valid else "fail", True,
                 "Values must be an object containing string values.", "Use app setting names mapped to strings.")
        if not valid:
            values = None
        if settings.get("IsEncrypted") is not False:
            _finding(rows, "configuration.settings-encryption", "unknown", True,
                     "Settings are encrypted or IsEncrypted is absent; doctor does not decrypt them.",
                     "Inspect/decrypt settings separately before local preflight.")
            values = None
    if values is not None:
        _finding(rows, "configuration.worker", "pass" if values.get("FUNCTIONS_WORKER_RUNTIME") == "node" else "unknown",
                 True, "Standard local projects normally select the Node worker.",
                 "Confirm FUNCTIONS_WORKER_RUNTIME is appropriate for this Standard project.")
    available_settings = set(values).union(os.environ) if values is not None else None
    parameters_file = os.path.join(root, "parameters.json")
    parameters = _read_json(parameters_file, rows, "configuration.parameters", required=True, optional=True)
    parameter_names = set(parameters) if parameters is not None else set() if not os.path.exists(parameters_file) else None
    if parameters is not None:
        valid = all(isinstance(value, dict) and "value" in value for value in parameters.values())
        _finding(rows, "configuration.parameter-values", "pass" if valid else "fail", True,
                 "Project parameters must each have a value object entry.",
                 "Use parameters.json entries shaped as name: {type: ..., value: ...}.")
        _references(rows, parameters, "references.project-parameters", available_settings, parameter_names)
    connections = _read_json(os.path.join(root, "connections.json"), rows, "configuration.connections",
                             required=True, optional=True)
    if connections is not None:
        _references(rows, connections, "references.connections", available_settings, parameter_names)
    try:
        workflows = discover_workflows(root, all_workflows=True)
    except OSError:
        _finding(rows, "configuration.workflows", "fail", True, "Project workflow inventory could not be read.",
                 "Check project directory access.")
        workflows = []
    if not workflows:
        _finding(rows, "configuration.workflows", "fail", True, "No direct workflow.json files were found.",
                 "Add a workflow directory containing workflow.json.")
    for index, (name, path) in enumerate(workflows):
        check = "configuration.workflow.{}".format(index)
        if not _NAME.fullmatch(name):
            _finding(rows, check, "unknown", True, "Workflow name is outside the diagnostic name syntax.",
                     "Inspect the workflow manually.")
            continue
        document = _read_json(path, rows, check)
        if document is None:
            continue
        structural = []
        validate_workflow_document(document, name, path, structural)
        errors = sorted({item["rule"] for item in structural if item["severity"] == "error"})
        _finding(rows, check + ".structure", "fail" if errors else "pass", True,
                 "Basic workflow structure checks failed." if errors else "Basic workflow structure checks passed.",
                 "Correct the listed structural rules; business behavior was not tested." if errors else
                 "No action needed; business behavior was not tested.", workflow=name, rules=errors)
        declared = document.get("definition", {}).get("parameters", {}) if isinstance(document.get("definition"), dict) else {}
        available = set(parameter_names or ())
        if isinstance(declared, dict):
            available.update(key for key, value in declared.items()
                             if isinstance(value, dict) and "defaultValue" in value)
        _references(rows, document, "references.workflow.{}".format(index), available_settings,
                    available if parameter_names is not None else None)
    _bundle(rows, host, values)
    return values


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class _DeadlineHTTPHandler(HTTPHandler):
    def __init__(self, deadline):
        super().__init__()
        self.deadline = deadline

    def http_open(self, request):
        return self.do_open(partial(DeadlineHTTPConnection, deadline=self.deadline), request)


def _http_probe(url, timeout, host=False):
    """No proxies, redirects, credentials, or upstream text in diagnostic output."""
    deadline = time.monotonic() + timeout
    opener = build_opener(ProxyHandler({}), _NoRedirect(), _DeadlineHTTPHandler(deadline))
    try:
        response = opener.open(Request(url, method="GET"), timeout=timeout)
    except HTTPError as ex:
        response = ex
    except (URLError, OSError, ValueError):
        return {"reachable": False, "httpStatus": None, "identity": None, "service": None, "hostState": None}
    with response:
        try:
            remaining_timeout(deadline)
        except TimeoutError:
            return {"reachable": False, "httpStatus": None, "identity": None, "service": None, "hostState": None}
        server = response.headers.get("Server", "")
        banner = re.fullmatch(r"Azurite-(Blob|Queue|Table)/\d+\.\d+\.\d+", server)
        identity = "azurite" if banner else None
        state = None
        if host and response.code == 200:
            try:
                content = response.read(65537)
                payload = strict_json_loads(content) if len(content) <= 65536 else None
                remaining_timeout(deadline)
                if isinstance(payload, dict) and payload.get("state") in ("Running", "Starting", "Error", "Offline"):
                    state = payload["state"]
            except (OSError, ValueError, RecursionError):
                state = None
        return {"reachable": True, "httpStatus": response.code, "identity": identity,
                "service": banner.group(1).lower() if banner else None, "hostState": state}


def _ownership(rows, check, record_path, root=None, port=None):
    if not os.path.exists(record_path):
        _finding(rows, check, "unknown", False, "No CLI ownership record exists.",
                 "A listening port does not establish process ownership; doctor never terminates a process.")
        return None
    record = _read_json(record_path, rows, check + ".record", required=False)
    if record is None:
        return None
    verified = _local._record_matches(record)  # pylint: disable=protected-access
    project = record.get("projectPath")
    same_project = root is None or (isinstance(project, str) and
                                    os.path.normcase(abs_path(project)) == os.path.normcase(root))
    verified = verified and same_project and (port is None or record.get("port") == port)
    _finding(rows, check, "pass" if verified else "unknown", False,
             "Recorded PID and creation identity match a live process; service/listener identity is separate." if verified else
             "Record is stale, unverifiable, or belongs to another project; ownership is not established.",
             "No termination is performed or recommended from this finding.",
             ownership="verified-record" if verified else "unverified")
    return record if verified else None


def _port_listening(address, port, timeout):
    family = socket.AF_INET6 if address == "::1" else socket.AF_INET
    with socket.socket(family, socket.SOCK_STREAM) as probe:
        probe.settimeout(timeout)
        if probe.connect_ex((address, port)) == 0:
            return "listening"
    with socket.socket(family, socket.SOCK_STREAM) as probe:
        try:
            probe.bind((address, port))
            return "free"
        except OSError:
            return "occupied"


def _port_owner(record, port):
    if not record:
        return False
    try:
        for process in _local._runtime_process_records(record):  # pylint: disable=protected-access
            if not _local._record_matches(process):  # pylint: disable=protected-access
                continue
            owner = psutil.Process(process["pid"])
            get_connections = getattr(owner, "net_connections", None) or owner.connections
            connections = get_connections(kind="inet")
            if (any(item.status == psutil.CONN_LISTEN and item.laddr.port == port and
                    item.laddr.ip in ("127.0.0.1", "0.0.0.0") for item in connections) and
                    _local._record_matches(process)):  # pylint: disable=protected-access
                return True
    except (psutil.Error, OSError):
        return False
    return False


def _host(rows, root, port, timeout):
    record = _ownership(rows, "host.ownership", _local._record_file(port), root, port)  # pylint: disable=protected-access
    try:
        occupancy = _port_listening("127.0.0.1", port, timeout)
    except OSError:
        _finding(rows, "host.port", "unknown", False, "Host port could not be inspected.",
                 "Inspect the selected loopback port manually.", port=port)
        return
    _finding(rows, "host.port", "pass" if occupancy == "free" else "warn", False,
             "Host port is available for a new launch." if occupancy == "free" else
             "Host port is occupied; this alone does not identify Functions.",
             "No action needed." if occupancy == "free" else "Identify the listener before starting another host.",
             port=port, occupancy=occupancy)
    if occupancy != "listening":
        _finding(rows, "host.status", "skipped", False, "No accepting host listener; offline preflight remains valid.",
                 "Start a local runtime separately if a live status check is needed.")
        return
    observed = _http_probe("http://127.0.0.1:{}/admin/host/status".format(port), timeout, host=True)
    identified = _port_owner(record, port)
    state = observed["hostState"]
    status = "pass" if identified and state == "Running" else "warn" if identified and state in (
        "Starting", "Error", "Offline") else "unknown"
    _finding(rows, "host.status", status, False,
             "Verified recorded host reports Running; workflows were not executed." if status == "pass" else
             "Recorded host is not Running." if status == "warn" else
             "Loopback response does not establish a healthy Functions host for this project.",
             "Inspect this host separately; HTTP success or occupancy alone is not runtime identity.",
             port=port, reachable=observed["reachable"], httpStatus=observed["httpStatus"],
             hostState=state if identified else None, listenerMatchesRecord=identified)


def _storage_endpoints(values):
    if values is None:
        return None, "Storage settings could not be evaluated."
    raw = values.get("AzureWebJobsStorage")
    inherited = os.environ.get("AzureWebJobsStorage")
    if inherited is not None:
        if raw is not None and raw != inherited:
            return None, "Project and inherited storage settings differ; effective precedence is not certified."
        raw = inherited
    if not isinstance(raw, str) or not raw.strip():
        return None, "AzureWebJobsStorage is absent or empty; identity-based storage is not evaluated."
    if raw.strip().lower() == "true":
        raw = "UseDevelopmentStorage=true"
    fields = {}
    for part in raw.split(";"):
        if not part:
            continue
        key, sep, value = part.partition("=")
        if not sep or key.strip().lower() in fields:
            return None, "Storage connection syntax is ambiguous."
        fields[key.strip().lower()] = value.strip()
    if fields.get("usedevelopmentstorage", "").lower() == "true":
        if len(fields) > 1 or fields.get("developmentstorageproxyuri"):
            return None, "Development storage overrides are not probed."
        return [("blob", "127.0.0.1", 10000), ("queue", "127.0.0.1", 10001),
                ("table", "127.0.0.1", 10002)], None
    endpoints = []
    for service in ("blob", "queue", "table"):
        raw_endpoint = fields.get(service + "endpoint")
        if raw_endpoint is None:
            return None, "Storage does not declare all three explicit local endpoints; remote storage is never probed."
        try:
            url = urlsplit(raw_endpoint)
            if (url.scheme != "http" or url.hostname not in ("localhost", "127.0.0.1", "::1") or
                    url.username or url.password or url.query or url.fragment):
                return None, "Storage includes a nonlocal/unsupported endpoint; no endpoints were contacted."
            port = url.port or 80
            if not 1 <= port <= 65535:
                raise ValueError()
        except ValueError:
            return None, "Storage endpoint syntax is invalid; no endpoints were contacted."
        endpoints.append((service, "::1" if url.hostname == "::1" else "127.0.0.1", port))
    return endpoints, None


def _storage(rows, values, timeout):
    endpoints, reason = _storage_endpoints(values)
    if endpoints is None:
        missing = (values is not None and not values.get("AzureWebJobsStorage") and
                   not os.environ.get("AzureWebJobsStorage") and
                   not any(key.lower().startswith("azurewebjobsstorage__") for key in
                           set(values).union(os.environ)))
        _finding(rows, "storage.configuration", "fail" if missing else "unknown", True, reason,
                 "Configure local storage or verify remote/identity-based storage separately; doctor stays local-only.")
        return False
    _finding(rows, "storage.configuration", "pass", True, "All configured storage endpoints are literal loopback.",
             "No action needed.")
    _ownership(rows, "storage.ownership", _local._azurite_record_file())  # pylint: disable=protected-access
    for service, address, port in endpoints:
        try:
            occupancy = _port_listening(address, port, timeout)
        except OSError:
            occupancy = "unknown"
        observed = {"reachable": False, "httpStatus": None, "identity": None, "service": None}
        if occupancy == "listening":
            host = "[::1]" if address == "::1" else address
            observed = _http_probe("http://{}:{}/".format(host, port), timeout)
        identified = observed["identity"] == "azurite"
        status = "pass" if identified and observed["service"] == service else (
            "fail" if occupancy == "free" or identified else "unknown")
        _finding(rows, "storage." + service, status, True,
                 "Configured endpoint identifies as Azurite; authentication and storage operations were not tested."
                 if status == "pass" else "Configured endpoint identifies as a different Azurite service."
                 if identified else "Configured emulator endpoint is not listening." if status == "fail" else
                 "Configured storage port is occupied or unverifiable without Azurite identity evidence.",
                 "Start the emulator separately." if status == "fail" else
                 "Verify this endpoint separately; doctor does not send storage credentials or modify data.",
                 port=port, occupancy=occupancy, reachable=observed["reachable"],
                 httpStatus=observed["httpStatus"], identity=observed["identity"], service=observed["service"])
    return True


def doctor_report(path=None, context=None, port=None, probe_timeout=2, strict=False):
    rows = []
    coverage = {"projectFiles": False, "toolSelection": False, "storageConfiguration": False,
                "localStorageProbes": False, "localHostInspection": False,
                "cloud": False, "businessBehavior": False}
    if (not isinstance(probe_timeout, int) or isinstance(probe_timeout, bool) or
            not 1 <= probe_timeout <= 10):
        _finding(rows, "options.timeout", "fail", True, "--probe-timeout must be between 1 and 10 seconds.",
                 "Use a bounded probe timeout.")
        root, resolved_port = None, None
    else:
        root, resolved_port = _target(rows, path, context, port)
    if root is not None:
        if not os.path.isdir(root):
            _finding(rows, "configuration.project", "fail", True, "Selected project directory does not exist.",
                     "Choose an existing local project directory.")
        else:
            values = _configuration(rows, root)
            coverage["projectFiles"] = True
            local_storage = _storage(rows, values, probe_timeout)
            coverage["storageConfiguration"] = True
            coverage["localStorageProbes"] = local_storage
            _tools(rows, probe_timeout, local_storage)
            coverage["toolSelection"] = True
            _host(rows, root, resolved_port, probe_timeout)
            coverage["localHostInspection"] = True
    _finding(rows, "scope.business-behavior", "skipped", False, "Environment preflight does not test business behavior.",
             "Test workflow business scenarios separately.")
    counts = {status: sum(row["status"] == status for row in rows)
              for status in ("pass", "warn", "fail", "unknown", "skipped")}
    failed = any(row["required"] and row["status"] == "fail" for row in rows)
    incomplete = any(row["required"] and row["status"] == "unknown" for row in rows)
    strict_problem = strict and any(row["status"] in ("warn", "unknown", "fail") for row in rows)
    code = 1 if failed else 2 if incomplete or strict_problem else 0
    return {"schemaVersion": "1.0", "scope": "local-environment-preflight", "readOnly": True,
            "target": {"kind": "local", "projectPath": root, "port": resolved_port},
            "environmentHealth": "blocked" if failed else "unknown" if incomplete else "no-detected-blockers",
            "businessBehavior": "not-tested", "coverage": coverage,
            "summary": counts, "exitCode": code, "findings": rows}


def doctor_table_format(result):
    rows = []
    for row in result["findings"]:
        evidence = row["evidence"]
        details = ["{}: {}".format(label, evidence[key]) for key, label in (
            ("path", "Path"), ("version", "Version"), ("workflow", "Workflow"), ("port", "Port"))
            if evidence.get(key) is not None]
        details.extend("{}: {}".format(label, ", ".join(evidence[key])) for key, label in (
            ("missingAppSettings", "Missing app settings"), ("missingParameters", "Missing parameters"))
            if evidence.get(key))
        rows.append(OrderedDict((("Check", row["check"]), ("Status", row["status"]),
                                 ("Required", "yes" if row["required"] else "no"),
                                 ("Reason", " ".join([row["reason"]] + details)),
                                 ("Action", row["recommendation"]))))
    return rows


def finish_doctor_command(cmd, report):
    """Let normal JSON/query/table formatting finish before a diagnostic exit."""
    if report["exitCode"]:
        from knack.events import EVENT_CLI_POST_EXECUTE, EVENT_CLI_SUCCESSFUL_EXECUTE

        def cleanup(_cli, **_kwargs):
            cmd.cli_ctx.unregister_event(EVENT_CLI_SUCCESSFUL_EXECUTE, finish)
            cmd.cli_ctx.unregister_event(EVENT_CLI_POST_EXECUTE, cleanup)

        def finish(_cli, **_kwargs):
            cleanup(_cli)
            raise SystemExit(report["exitCode"])

        cmd.cli_ctx.register_event(EVENT_CLI_SUCCESSFUL_EXECUTE, finish)
        cmd.cli_ctx.register_event(EVENT_CLI_POST_EXECUTE, cleanup)
    return report
