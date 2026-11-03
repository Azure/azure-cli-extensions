# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError as HTTPURLError, URLError
from urllib.request import Request, urlopen

import psutil

# pylint: disable=import-error,no-name-in-module
from azure.cli.core.azclierror import CLIError, FileOperationError, InvalidArgumentValueError, ValidationError

from ._constants import DEFAULT_LOCAL_PORT
from ._context import _store_lock
from ._json import json_equal


DEPENDENCY_KINDS = ("core-tools", "node", "dotnet", "azurite", "bundle")

# The kinds 'dependency install' can install, and the order it installs them in.
# Azurite follows Node.js because it is installed with the npm that ships alongside it.
#
# This lives here, rather than in _dependencies, so that the "installableByCli" flag
# 'dependency check' reports and the set 'dependency install' accepts cannot drift
# apart -- they did, and check went on calling Azurite uninstallable after it was not.
# _dependencies re-exports it; nothing should define a second copy.
INSTALLABLE_KINDS = ("core-tools", "node", "azurite", "bundle")

STATE_DIR = os.path.join(os.path.expanduser("~"), ".azurelogicapps", "runtimes")

# Azurite binds these fixed ports. They are not configurable here on purpose: the
# storage connection string the emulator is addressed by ("UseDevelopmentStorage=true")
# hard-codes them, so a differently-ported emulator would not be the one the runtime
# talks to.
AZURITE_PORTS = {"blob": 10000, "queue": 10001, "table": 10002}

# Executable each dependency is found by, and the folder it lands in under the
# managed dependency root when the tooling installs it there.
_TOOL_EXECUTABLES = {
    "core-tools": "func",
    "node": "node",
    "dotnet": "dotnet",
    "azurite": "azurite"
}
# Folder each dependency lands in under the shared root. These are the names
# Visual Studio Code's Azure Logic Apps extension uses. D122 chose a shared root so a
# developer who has already set up VS Code is not made to download everything twice,
# and that only works if the folder names match -- "Node" never did.
_MANAGED_SUBDIRS = {
    "core-tools": "FuncCoreTools",
    "node": "NodeJs",
    "dotnet": "DotNetSDK",
    "azurite": "Azurite"
}

BUNDLE_ID = "Microsoft.Azure.Functions.ExtensionBundle.Workflows"


def managed_subdir(kind):
    return _MANAGED_SUBDIRS.get(kind)


def bundle_install_root():
    """Where Functions Core Tools keeps downloaded extension bundles."""
    return os.path.join(
        os.path.expanduser("~"), ".azure-functions-core-tools", "Functions", "ExtensionBundles", BUNDLE_ID)


def dependencies_root():
    """Directory the tooling installs dependencies into.

    LA_DEPENDENCIES_PATH overrides it. This is reported as "root" by
    dependency check, so discovery has to actually look here.
    """
    override = os.environ.get("LA_DEPENDENCIES_PATH")
    if override:
        return os.path.abspath(os.path.expanduser(override))
    return os.path.join(os.path.expanduser("~"), ".azurelogicapps", "dependencies")


def find_tool(kind, root=None):
    """Locate a dependency's executable.

    Returns (path, source), where source is "path" when it came from PATH,
    "managed" when it came from the managed dependency root, and "not-found"
    when it is absent.

    A tool installed under the managed root is not on PATH, so searching PATH
    alone reports it missing even though the CLI knows exactly where it is.

    shutil.which does the platform-specific work: PATHEXT on Windows, the
    executable bit elsewhere.
    """
    executable = _TOOL_EXECUTABLES.get(kind)
    if not executable:
        return None, "not-found"

    found = shutil.which(executable)
    if found:
        return found, "path"

    root = root or dependencies_root()
    candidates = [root]
    subdir = _MANAGED_SUBDIRS.get(kind)
    if subdir:
        managed = os.path.join(root, subdir)
        # Node's archives keep the executable in a bin/ folder on Linux and macOS,
        # but directly at the top level on Windows.
        candidates = [managed, os.path.join(managed, "bin")] + candidates
    existing = [item for item in candidates if os.path.isdir(item)]
    if existing:
        found = shutil.which(executable, path=os.pathsep.join(existing))
        if found:
            return found, "managed"

    return None, "not-found"


def dependency_environment(executable=None, root=None):
    """Child-only PATH, using the same PATH-first discovery as dependency check.

    npm's launcher must use its own adjacent Node.js when present, including an
    explicit install root. Other launchers need the independently managed Node.js
    and .NET paths; none of these directories are added to the user's environment.
    """
    environment = os.environ.copy()
    paths = [os.path.dirname(os.path.abspath(executable))] if executable else []
    for kind in ("node", "dotnet", "core-tools", "azurite"):
        path = find_tool(kind, root=root)[0] if root else find_tool(kind)[0]
        if path:
            directory = os.path.dirname(os.path.abspath(path))
            if directory not in paths:
                paths.append(directory)
    inherited = environment.get("PATH", "")
    if inherited:
        paths.append(inherited)
    environment["PATH"] = os.pathsep.join(paths)
    return environment


def validate_port(port):
    port = DEFAULT_LOCAL_PORT if port is None else port
    try:
        value = int(port)
    except (TypeError, ValueError) as ex:
        raise InvalidArgumentValueError("--port must be between 1 and 65535.") from ex
    if value < 1 or value > 65535:
        raise InvalidArgumentValueError("--port must be between 1 and 65535.")
    return value


def local_settings_values(project_path):
    """``Values`` from a project's local.settings.json, or None when unreadable.

    None means "unknown", which is deliberately distinct from an empty mapping: the
    caller must not conclude anything about storage configuration from a file it could
    not read.
    """
    if not project_path:
        return None
    settings_file = os.path.join(project_path, "local.settings.json")
    if not os.path.isfile(settings_file):
        return None
    try:
        with open(settings_file, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return None
    values = payload.get("Values")
    return values if isinstance(values, dict) else None


def uses_development_storage(project_path):
    """Whether AzureWebJobsStorage points at the local emulator. None when unknown.

    Azurite is only needed when storage resolves to the emulator. Reporting it as
    flatly optional told a developer using development storage that a missing Azurite
    did not matter, when in fact the host could not start; reporting it as flatly
    required would nag every developer who had pointed the project at a real storage
    account.
    """
    values = local_settings_values(project_path)
    if values is None:
        return None
    raw = values.get("AzureWebJobsStorage")
    if raw is None:
        return None
    return str(raw).strip().lower() in ("usedevelopmentstorage=true", "true")


def dependency_report(kind=None, project_path=None):
    requested = kind or list(DEPENDENCY_KINDS)
    development_storage = uses_development_storage(project_path)
    rows = [_detect(item, development_storage=development_storage) for item in requested]
    return {
        "root": dependencies_root(),
        "environmentOverride": os.environ.get("LA_DEPENDENCIES_PATH"),
        "projectPath": project_path,
        "usesDevelopmentStorage": development_storage,
        "value": rows
    }


def _detect(kind, development_storage=None):
    if kind not in DEPENDENCY_KINDS:
        raise InvalidArgumentValueError("Unknown dependency kind '{}'.".format(kind))
    path, source = _dependency_path(kind)
    version = _dependency_version(path, kind)
    if kind == "azurite":
        # Unknown project storage keeps the historical answer rather than guessing.
        required = bool(development_storage)
        required_when = ("Required while AzureWebJobsStorage is UseDevelopmentStorage=true. "
                         "Pass --path to evaluate a specific project.")
    else:
        required = True
        required_when = None
    return {
        "kind": kind,
        "displayName": {
            "core-tools": "Azure Functions Core Tools",
            "node": "Node.js",
            "dotnet": ".NET SDK",
            "azurite": "Azurite storage emulator",
            "bundle": "Logic Apps Workflows extension bundle"
        }[kind],
        "state": "present" if path else "missing",
        "version": version,
        "path": path,
        "source": source,
        "required": required,
        "requiredWhen": required_when,
        "installableByCli": kind in INSTALLABLE_KINDS,
        "remediation": None if path else _remediation(kind)
    }


def _dependency_path(kind):
    if kind != "bundle":
        return find_tool(kind)
    bundle_root = bundle_install_root()
    if os.path.isdir(bundle_root):
        return bundle_root, "path"
    managed_bundle = os.path.join(dependencies_root(), "ExtensionBundles", BUNDLE_ID)
    if os.path.isdir(managed_bundle):
        return managed_bundle, "managed"
    return None, "not-found"


def _dependency_version(path, kind):
    if not path or kind == "bundle":
        return None
    executable = path
    if os.path.splitext(executable)[1].lower() == ".ps1":
        return None
    try:
        completed = subprocess.run([executable, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   universal_newlines=True, timeout=20,
                                   check=False, env=dependency_environment(executable))
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    text = (completed.stdout or "").strip()
    return text.splitlines()[0].lstrip("v") if text else None


def _remediation(kind):
    return {
        "core-tools": "Run 'az logicapp dependency install --kind core-tools'.",
        "node": "Run 'az logicapp dependency install --kind node'.",
        "dotnet": "Install the .NET SDK from https://dotnet.microsoft.com/download. "
                  "This CLI does not install it; see 'az logicapp dependency install --help'.",
        "azurite": "Run 'az logicapp dependency install --kind azurite'. Azurite is only needed when "
                   "workflows use the local storage emulator.",
        "bundle": "Run 'az logicapp dependency install --kind bundle', or start the runtime once with "
                  "Functions Core Tools to download it."
    }[kind]


def azurite_endpoint(service="blob"):
    return "http://127.0.0.1:{}".format(AZURITE_PORTS[service])


def probe_azurite(timeout=2.0):
    """Server banner of the Azurite blob service, or None when it is not there.

    Deliberately stronger than "something is listening on 10000". An unrelated service
    holding the port would otherwise read as a running emulator, the CLI would skip
    starting one, and the runtime would then fail against a storage endpoint that is
    not storage at all. Azurite answers the blob root with 400 and a
    ``Server: Azurite-Blob/<version>`` header, so the header is the thing to check --
    the status code is not.
    """
    request = Request(azurite_endpoint("blob") + "/", method="GET")
    try:
        with urlopen(request, timeout=timeout) as response:  # nosec B310 - fixed localhost scheme
            headers = response.headers
    except HTTPURLError as ex:
        headers = getattr(ex, "headers", None)
    except (URLError, OSError, ValueError):
        return None
    server = (headers.get("Server") if headers else None) or ""
    return server if server.lower().startswith("azurite") else None


def azurite_status(prober=None):
    """Whether the emulator is up, and whether its ports are occupied by anything else."""
    server = (prober or probe_azurite)()
    return {
        "ports": dict(AZURITE_PORTS),
        "blobEndpoint": azurite_endpoint("blob"),
        "running": bool(server),
        "server": server,
        "portsInUse": sorted(port for port in AZURITE_PORTS.values() if not _port_free(port))
    }


def azurite_workspace():
    """Where the emulator keeps its data files.

    Not the project directory: Azurite writes ``__blobstorage__``, ``__queuestorage__``
    and ``__azurite_db_*.json`` into its working directory, and littering -- possibly
    committing -- those into a developer's project is not acceptable. A single shared
    location is also the honest model, because the ports are fixed and global, so one
    emulator instance necessarily serves every project on the machine.
    """
    return os.path.join(STATE_DIR, "azurite")


def _azurite_record_file():
    return os.path.join(STATE_DIR, "azurite.json")


def read_azurite_record():
    return _read_state_record(_azurite_record_file(), "Could not read Azurite state record.")


def _write_azurite_record(record):
    _write_state_record(_azurite_record_file(), record, "Could not write Azurite state record.")


def _clear_azurite_record():
    try:
        os.remove(_azurite_record_file())
    except OSError:
        pass


def _wait_for_azurite(pid, timeout, prober=None):
    """Wait until *our* emulator answers.

    Liveness is checked alongside the banner, not merely as a loop exit. A spawned
    Azurite that dies immediately -- which is exactly what happens when the ports are
    already bound -- would otherwise be reported as started, because the probe finds
    the banner of the emulator that already owned the port. That produced a state
    record naming a dead pid and a caller convinced it had started something.
    """
    deadline = time.monotonic() + max(0, timeout or 0)
    prober = prober or probe_azurite
    while True:
        alive = _is_running(pid) if pid else True
        server = prober()
        if server:
            return server if alive else None
        if not alive:
            return None
        if time.monotonic() >= deadline:
            return None
        time.sleep(0.5)


def start_azurite(azurite_path=None, timeout=30, prober=None):
    """Start the emulator in the background and wait until it answers.

    Returns the state record. Raises when the process could not be spawned; a spawn
    that succeeds but never serves is reported as ``failed`` rather than raised, so the
    caller can decide whether that is fatal.
    """
    read_azurite_record()
    azurite = azurite_path or find_tool("azurite")[0]
    if not azurite:
        raise ValidationError("Azurite is required for local development storage. " + _remediation("azurite"))
    workspace = azurite_workspace()
    os.makedirs(workspace, exist_ok=True)
    os.makedirs(STATE_DIR, exist_ok=True)
    log_path = os.path.join(STATE_DIR, "azurite.log")
    log_handle = open(log_path, "ab")  # pylint: disable=consider-using-with
    creationflags = 0
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
    argv = [
        azurite,
        "--location", workspace,
        "--blobPort", str(AZURITE_PORTS["blob"]),
        "--queuePort", str(AZURITE_PORTS["queue"]),
        "--tablePort", str(AZURITE_PORTS["table"]),
        "--skipApiVersionCheck"
    ]
    try:
        proc = subprocess.Popen(argv, cwd=workspace, stdout=log_handle, stderr=subprocess.STDOUT,
                                creationflags=creationflags, env=dependency_environment(azurite))
    except OSError as ex:
        log_handle.close()
        raise CLIError("Azurite failed to start. See {}.".format(log_path)) from ex
    log_handle.close()
    record = {
        "pid": proc.pid,
        "processCreateTimeUtc": process_create_time_utc(proc.pid),
        "ports": dict(AZURITE_PORTS),
        "workspace": workspace,
        "logPath": log_path,
        "server": None,
        "startedByCli": True,
        "startedAtUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }
    try:
        if not record["processCreateTimeUtc"] and proc.poll() is None:
            raise CLIError("Could not verify the Azurite process identity. The launch was cancelled.")
        _remember_runtime_children(record)
        if _runtime_has_live_process(record):
            # A zero readiness timeout is not an exit. Retain a verifiable live
            # launch even when it has not opened its ports yet.
            _write_azurite_record(record)
        record["server"] = _wait_for_azurite(proc.pid, timeout, prober=prober)
        _remember_runtime_children(record)
        if _runtime_has_live_process(record):
            _write_azurite_record(record)
        else:
            _clear_azurite_record()
    except BaseException:
        _terminate_launched_process(proc, record)
        if _runtime_has_live_process(record) or _unverified_cleanup_pending(record) or proc.poll() is None:
            record["cleanupPending"] = True
            _write_azurite_record(record)
        else:
            _clear_azurite_record()
        raise
    return record


def stop_azurite():
    """Stop the emulator, but only the one this CLI started.

    Identity is matched on pid *and* process creation time for the same reason the
    runtime records do: a recycled pid would otherwise make us kill an unrelated
    process. An emulator the developer started themselves -- from VS Code, or a
    terminal -- has no record here and is deliberately left alone.
    """
    try:
        record = read_azurite_record()
    except FileOperationError:
        return {"stopped": False, "reason": "invalid-record",
                "remediation": "Inspect the unreadable Azurite ownership record manually; it was retained."}
    if not record:
        return {"stopped": False, "reason": "not-started-by-cli"}
    if not _runtime_has_live_process(record):
        if _unverified_cleanup_pending(record):
            return {"stopped": False, "reason": "identity-unverified", "pid": record.get("pid"),
                    "remediation": "A cancelled launch could not be cleaned up or identified. "
                                   "Stop that process yourself before removing its record."}
        _clear_azurite_record()
        return {"stopped": False, "reason": "not-running", "pid": record.get("pid")}
    pid = record.get("pid")
    _remember_runtime_children(record)
    try:
        for process_record in _runtime_process_records(record):
            if _record_matches(process_record):
                _terminate_record_process(record, process_record)
    except (OSError, subprocess.SubprocessError):
        record["cleanupPending"] = True
        _write_azurite_record(record)
        return {"stopped": False, "reason": "cleanup-pending", "pid": pid,
                "remediation": "A process could not be safely stopped. Its ownership record was retained."}
    deadline = time.monotonic() + 5
    while (_runtime_has_live_process(record) or _unverified_cleanup_pending(record)) and time.monotonic() < deadline:
        time.sleep(0.1)
    owned_still_live = _runtime_has_live_process(record) or _unverified_cleanup_pending(record)
    if owned_still_live:
        _write_azurite_record(record)
    else:
        _clear_azurite_record()
    # Verify, because the kill reporting success is not the same as the emulator being
    # gone: that exact gap is how an orphaned child kept the ports bound while 'stop'
    # returned stopped=true.
    still_serving = bool(probe_azurite(timeout=2.0))
    result = {"stopped": not still_serving and not owned_still_live, "pid": pid, "ports": record.get("ports")}
    if still_serving or owned_still_live:
        result["reason"] = "still-serving"
        result["remediation"] = ("Azurite is still answering on port {} after the recorded process was "
                                 "stopped. A process outside this CLI may now own it.".format(AZURITE_PORTS["blob"]))
    return result


def ensure_azurite(project_path, enable=True, starter=None, prober=None, timeout=30):
    """Make sure Azurite is available before the runtime needs it.

    Returns the dependency entry to report, never raising: a storage emulator that
    could not be started is worth a clear warning, but it is not a reason to refuse to
    start a runtime the developer may be about to point at something else.
    """
    development_storage = uses_development_storage(project_path)
    entry = {"kind": "azurite", "usesDevelopmentStorage": development_storage, "ports": dict(AZURITE_PORTS)}
    azurite_path = find_tool("azurite")[0]
    if not enable:
        # Still worth saying whether it is there, because --no-azurite suppresses the
        # start, not the fact that the runtime is about to need one.
        status = azurite_status(prober)
        entry.update({
            "state": "skipped",
            "severity": "info" if (status["running"] or development_storage is False) else "warning",
            "running": status["running"],
            "reason": "--no-azurite was specified"
        })
        return entry
    if development_storage is False:
        # A project pointed at a real storage account has no use for the emulator.
        return None
    status = azurite_status(prober)
    try:
        owner = read_azurite_record()
    except FileOperationError:
        entry.update({"state": "failed", "severity": "warning", "startedByCli": False,
                      "reason": "invalid-record",
                      "remediation": "Inspect the unreadable Azurite ownership record manually; "
                                     "no new emulator was started and the record was retained."})
        return entry
    if not status["running"] and owner and _runtime_has_live_process(owner):
        owner_pid = next(item["pid"] for item in _runtime_process_records(owner) if _record_matches(item))
        server = _wait_for_azurite(owner_pid, timeout, prober=prober)
        if server:
            status.update({"running": True, "server": server})
        else:
            entry.update({"state": "failed", "severity": "warning", "startedByCli": True,
                          "pid": owner_pid, "logPath": owner.get("logPath"),
                          "remediation": "The existing CLI Azurite launch has not answered yet. "
                                         "Check {} before retrying.".format(owner.get("logPath"))})
            return entry
    if not status["running"] and owner and _unverified_cleanup_pending(owner):
        entry.update({"state": "failed", "severity": "warning", "startedByCli": False,
                      "pid": owner.get("pid"),
                      "remediation": "A previous Azurite launch could not be identified or cleaned up. "
                                     "Stop it yourself before retrying."})
        return entry
    if status["running"]:
        # 'startedByCli' must mean the same thing here as it does in 'runtime show':
        # does this CLI own the emulator, and may 'stop' release it? Reporting it as
        # "what this invocation did" made a second 'runtime start' say false about an
        # emulator the first one had started, so the output told the developer nothing
        # would stop it moments before 'runtime stop' did. What this invocation did is
        # already carried by 'state'.
        entry.update({
            "state": "already-running",
            "severity": "info",
            "startedByCli": bool(owner and _runtime_has_live_process(owner)),
            "server": status["server"],
            "blobEndpoint": status["blobEndpoint"]
        })
        return entry
    if not azurite_path:
        entry.update({
            "state": "missing",
            # Unknown storage configuration is not a reason to nag: 'info' when we
            # could not read local.settings.json, 'warning' only when we know.
            "severity": "warning" if development_storage else "info",
            "remediation": _remediation("azurite")
        })
        return entry
    if status["portsInUse"]:
        entry.update({
            "state": "port-conflict",
            "severity": "warning",
            "portsInUse": status["portsInUse"],
            "remediation": "Ports {} are in use by a process that is not Azurite. Stop it, then start the "
                           "runtime again.".format(", ".join(str(p) for p in status["portsInUse"]))
        })
        return entry
    if development_storage is None:
        # We could not read the storage setting. Starting a background server process
        # on a guess is a bigger imposition than saying so, so report and move on.
        entry.update({
            "state": "not-started",
            "severity": "info",
            "reason": "Could not determine AzureWebJobsStorage from local.settings.json.",
            "remediation": "Start it with 'az logicapp runtime start' once the project declares "
                           "\"AzureWebJobsStorage\": \"UseDevelopmentStorage=true\"."
        })
        return entry
    try:
        record = (starter or start_azurite)(azurite_path=azurite_path, timeout=timeout, prober=prober)
    except (CLIError, OSError) as ex:
        entry.update({"state": "failed", "severity": "warning", "error": str(ex)})
        return entry
    if not record.get("server"):
        entry.update({
            "state": "failed",
            "severity": "warning",
            "pid": record.get("pid"),
            "logPath": record.get("logPath"),
            "remediation": "Azurite was launched but did not answer on port {} within {}s. Check {}.".format(
                AZURITE_PORTS["blob"], timeout, record.get("logPath"))
        })
        return entry
    entry.update({
        "state": "started",
        "severity": "info",
        "startedByCli": True,
        "pid": record.get("pid"),
        "server": record.get("server"),
        "workspace": record.get("workspace"),
        "logPath": record.get("logPath"),
        "blobEndpoint": azurite_endpoint("blob")
    })
    return entry


def start_runtime(cmd, path, port=None, background=False, ready_timeout=30, no_azurite=False):
    port = validate_port(port)
    project_path = os.path.abspath(os.path.expanduser(path or os.curdir))
    if not os.path.isfile(os.path.join(project_path, "host.json")):
        raise ValidationError("Logic Apps project is missing host.json: {}".format(project_path))
    if not _port_free(port):
        raise ValidationError("Port {} is already in use.".format(port))
    existing = _read_record(port)
    consumer = {"pid": existing.get("consumerPid"),
                "processCreateTimeUtc": existing.get("consumerProcessCreateTimeUtc")} if existing else {}
    if existing and (_runtime_has_live_process(existing) or _record_matches(consumer) or
                     _unverified_cleanup_pending(existing)):
        raise ValidationError("A CLI runtime is already starting or running on port {}.".format(port))
    func, _ = find_tool("core-tools")
    if not func:
        raise ValidationError(
            "Azure Functions Core Tools are required to start the runtime. "
            "Looked on PATH and under {}. "
            "Run 'az logicapp dependency install --kind core-tools' to install them, "
            "or set LA_DEPENDENCIES_PATH to the directory holding it.".format(dependencies_root()))
    consumer_time = process_create_time_utc(os.getpid())
    if not consumer_time:
        raise CLIError("Could not verify the CLI process identity; the runtime was not started.")
    log_path = os.path.join(STATE_DIR, "runtime-{}.log".format(port)) if background else None
    record = {
        "pid": None,
        "processCreateTimeUtc": None,
        "consumerPid": os.getpid(),
        "consumerProcessCreateTimeUtc": consumer_time,
        "launchId": uuid.uuid4().hex,
        "background": bool(background),
        "port": port,
        "projectPath": project_path,
        "logPath": log_path,
        "cliVersion": _cli_version(cmd),
        "startedAtUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }
    # Register before storage acquisition: another CLI must not release shared
    # storage in the interval between ensuring it and launching this host.
    _write_record(port, record)
    warnings = []
    proc = None
    keep_running = False
    try:
        azurite_entry = ensure_azurite(project_path, enable=not no_azurite, timeout=ready_timeout)
        if azurite_entry:
            warnings.append(azurite_entry)
        argv = [func, "host", "start", "--port", str(port)]
        environment = dependency_environment(func)
        if background:
            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
            with open(log_path, "ab") as log_handle:
                proc = subprocess.Popen(argv, cwd=project_path, stdout=log_handle, stderr=subprocess.STDOUT,
                                        creationflags=creationflags, env=environment)
        else:
            proc = subprocess.Popen(argv, cwd=project_path, env=environment)
        record["pid"] = proc.pid
        record["processCreateTimeUtc"] = process_create_time_utc(proc.pid)
        _remember_runtime_children(record)
        _write_record(port, record)
        if not record["processCreateTimeUtc"] and proc.poll() is None:
            raise CLIError("Could not verify the runtime process identity. The launch was cancelled.")
        if background:
            readiness = _wait_for_ready(port, proc.pid, ready_timeout)
            status = "failed" if proc.poll() is not None else ("running" if readiness[1] else "starting")
            _remove_consumer(record)
            _remember_runtime_children(record)
            if status != "failed":
                _write_record(port, record)
                keep_running = True
            payload = _start_payload(status, project_path, port, True, proc.pid,
                                     record["processCreateTimeUtc"], _record_file(port), log_path, warnings,
                                     readiness=readiness)
            if status != "running":
                payload["message"] = (
                    "The runtime process {} but its management endpoint did not respond within {}s. "
                    "Check the log at {}.".format(
                        "exited" if status == "failed" else "is up", ready_timeout, log_path))
            return payload
        try:
            returncode = _wait_foreground_runtime(proc, record)
        except KeyboardInterrupt:
            returncode = 0
        _terminate_launched_process(proc, record)
        still_live = _runtime_has_live_process(record) or _unverified_cleanup_pending(record) or proc.poll() is None
        payload = _start_payload("stopped" if returncode == 0 and not still_live else "failed",
                                 project_path, port, False, None, None, None, None, warnings)
        if still_live:
            payload.update({"recordPath": _record_file(port), "pid": proc.pid,
                            "processCreateTimeUtc": record["processCreateTimeUtc"],
                            "message": "Runtime cleanup left a live process. Its record was retained; "
                                       "use 'az logicapp runtime stop' to retry."})
        return payload
    except OSError as ex:
        raise CLIError("Runtime failed to start.") from ex
    finally:
        if not keep_running:
            if proc is not None:
                _terminate_launched_process(proc, record)
            _finish_runtime_record(record, proc)


def _remove_consumer(record):
    record.pop("consumerPid", None)
    record.pop("consumerProcessCreateTimeUtc", None)


def _runtime_process_records(record):
    if not _record_shape_valid(record):
        raise FileOperationError("Invalid process ownership record; it was retained.")
    return [record] + record.get("childProcesses", [])


def _runtime_has_live_process(record):
    return any(_record_matches(item) for item in _runtime_process_records(record))


def _unverified_cleanup_pending(record):
    # Existence only withholds shared storage; it never grants ownership or
    # permission to terminate a PID whose creation time could not be verified.
    processes = _runtime_process_records(record)
    if record.get("cleanupPending"):
        return any(_process_may_exist(item.get("pid")) for item in processes)
    if record.get("consumerPid"):
        processes.append({"pid": record["consumerPid"],
                          "processCreateTimeUtc": record.get("consumerProcessCreateTimeUtc")})
    return any(_process_identity_uncertain(item) for item in processes)


def _process_identity_uncertain(record):
    pid = record.get("pid")
    if not _valid_record_pid(pid):
        return False
    expected = record.get("processCreateTimeUtc")
    return (not isinstance(expected, str) or not expected.strip() or
            process_create_time_utc(pid) is None) and _process_may_exist(pid)


def _process_may_exist(pid):
    if not _valid_record_pid(pid):
        return False
    try:
        exists = psutil.pid_exists(pid)
    except (psutil.Error, OSError):
        return True
    if exists and sys.platform == "win32":
        # Windows retains exited process objects while handles are open. A PID
        # in that table is not evidence of a running or unverifiable process.
        _, exited = _windows_process_snapshot(pid)
        if exited:
            return False
    return exists


def _remember_runtime_children(record):
    children = [item for item in record.get("childProcesses", []) if _record_matches(item) or
                _process_identity_uncertain(item) or
                (record.get("cleanupPending") and _process_may_exist(item["pid"]))]
    if _record_matches(record):
        try:
            descendants = psutil.Process(record["pid"]).children(recursive=True)
        except psutil.Error:
            descendants = []
        snapshot = [(record["pid"], 0, record["processCreateTimeUtc"])]
        observed = []
        for child in descendants:
            if not _valid_record_pid(child.pid) or child.pid == record["pid"]:
                continue
            try:
                creation_time = process_create_time_utc(child.pid)
                parent_pid = child.ppid()
                if not child.is_running():
                    continue
            except psutil.Error:
                creation_time, parent_pid = None, None
            observed.append({"pid": child.pid, "processCreateTimeUtc": None,
                             "cleanupPending": True})
            if _valid_record_pid(parent_pid):
                snapshot.append((child.pid, parent_pid, creation_time))
        # Enumeration can cross a recycled root/child PID. Only a still-matching
        # root and current ancestry/birth chain authorize adopting new identities.
        excluded = set()
        proven = (_descendant_process_records(record["pid"], record["processCreateTimeUtc"], snapshot,
                                              excluded=excluded)
                  if _record_matches(record) else [])
        identities = {item["pid"]: item for item in proven}
        known = {item["pid"] for item in children}
        for candidate in observed:
            if candidate["pid"] not in known and candidate["pid"] not in excluded:
                children.append(identities.get(candidate["pid"], candidate))
                known.add(candidate["pid"])
    if children:
        record["childProcesses"] = children
    else:
        record.pop("childProcesses", None)


def _wait_foreground_runtime(proc, record):
    while True:
        try:
            return proc.wait(timeout=0.5)
        except subprocess.TimeoutExpired:
            previous = list(record.get("childProcesses", []))
            _remember_runtime_children(record)
            if record.get("childProcesses", []) != previous:
                _write_record(record["port"], record)


def _terminate_launched_process(proc, record):
    _remember_runtime_children(record)
    if proc.poll() is None:
        try:
            if _record_matches(record):
                _terminate_record_process(record, record)
            else:
                # The Popen handle still identifies our own child when querying its
                # creation time failed. It never authorizes a kill from a stale file.
                proc.terminate()
        except (OSError, subprocess.SubprocessError):
            pass
    for child in record.get("childProcesses", []):
        if _record_matches(child):
            try:
                _terminate_record_process(record, child)
            except (OSError, subprocess.SubprocessError):
                continue
    try:
        proc.wait(timeout=5)
    except (OSError, subprocess.SubprocessError):
        pass


def _finish_runtime_record(record, proc):
    _remove_consumer(record)
    still_live = (_runtime_has_live_process(record) or _unverified_cleanup_pending(record) or
                  (proc is not None and proc.poll() is None))
    if still_live:
        # A failed cleanup must remain discoverable, including a shim's still-live
        # child; otherwise a later stop could tear down the storage it still needs.
        record["cleanupPending"] = True
        _write_record(record["port"], record)
        return
    current = _read_record(record["port"])
    if current and current.get("launchId") == record["launchId"]:
        try:
            os.remove(_record_file(record["port"]))
        except FileNotFoundError:
            pass
    _release_azurite_if_idle()


def _azurite_view():
    status = azurite_status()
    record = read_azurite_record()
    started_by_cli = bool(record and _runtime_has_live_process(record))
    return {
        "running": status["running"],
        "server": status["server"],
        "blobEndpoint": status["blobEndpoint"],
        "ports": status["ports"],
        "startedByCli": started_by_cli,
        "pid": record.get("pid") if started_by_cli else None,
        "workspace": record.get("workspace") if started_by_cli else None,
        "logPath": record.get("logPath") if started_by_cli else None
    }


def show_runtime(port=None):
    port = validate_port(port)
    record = _read_record(port)
    listening, reachable, probe_error = _readiness(port)
    endpoint = management_endpoint(port)
    azurite = _azurite_view()
    readiness = {"listening": listening, "managementEndpointReachable": reachable,
                 "managementEndpoint": endpoint, "lastProbeError": probe_error}
    if not record:
        state = "running" if reachable else ("starting" if listening else "stopped")
        return {"port": port, "state": state, "status": state, "listening": listening, "pid": None, "processCreateTimeUtc": None, "startedByCli": False, "recordPath": None, "projectPath": None, "logPath": None, "managementEndpoint": endpoint, "readiness": readiness, "azurite": azurite}
    live = _record_matches(record)
    if not live:
        state = "stale-record"
    else:
        state = "running" if reachable else "starting"
    return {"port": port, "state": state, "status": state, "listening": listening, "pid": record.get("pid"), "processCreateTimeUtc": record.get("processCreateTimeUtc"), "startedByCli": live, "recordPath": _record_file(port), "projectPath": record.get("projectPath"), "logPath": record.get("logPath"), "readiness": readiness, "managementEndpoint": endpoint, "azurite": azurite}


def stop_runtime(port=None, all_records=False):
    if all_records:
        ports = [_port_from_record_name(name) for name in os.listdir(STATE_DIR)] if os.path.isdir(STATE_DIR) else []
        ports = [item for item in ports if item is not None]
    else:
        ports = [validate_port(port)]
    stopped = []
    refused = []
    for item_port in ports:
        try:
            record = _read_record(item_port)
        except FileOperationError:
            refused.append(_refusal(item_port, None, "runtime.invalid_record",
                                    "Could not read runtime state record; it was retained."))
            continue
        if not record:
            refused.append(_refusal(item_port, None, "runtime.no_record", "No CLI runtime record exists for this port."))
            continue
        original = copy.deepcopy(record)
        if not _runtime_has_live_process(record):
            if record.get("cleanupPending"):
                try:
                    _remove_runtime_record(item_port, original, recover=True)
                except CLIError as ex:
                    refused.append(_refusal(item_port, record.get("pid"), "runtime.cleanup_pending", str(ex)))
                    continue
                stopped.append({"port": item_port, "pid": record.get("pid"),
                                "processCreateTimeUtc": record.get("processCreateTimeUtc"),
                                "result": "already-exited", "recordPath": _record_file(item_port)})
                continue
            refused.append(_refusal(item_port, record.get("pid"), "runtime.identity_mismatch", "The recorded process identity no longer matches a live process."))
            continue
        try:
            _remember_runtime_children(record)
            for process_record in _runtime_process_records(record):
                if _record_matches(process_record):
                    _terminate_record_process(record, process_record)
            deadline = time.monotonic() + 5
            while _runtime_has_live_process(record) and time.monotonic() < deadline:
                time.sleep(0.1)
            if _runtime_has_live_process(record) or _unverified_cleanup_pending(record):
                raise OSError("The runtime still has a live process; its record was retained.")
            _remove_runtime_record(item_port, original)
            stopped.append({"port": item_port, "pid": record.get("pid"), "processCreateTimeUtc": record.get("processCreateTimeUtc"), "result": "terminated", "recordPath": _record_file(item_port)})
        except FileOperationError as ex:
            refused.append(_refusal(item_port, record.get("pid"), "runtime.record_changed", str(ex)))
        except (OSError, CLIError, subprocess.SubprocessError) as ex:
            record["cleanupPending"] = True
            try:
                _write_record(item_port, record, expected=original)
            except CLIError as write_error:
                refused.append(_refusal(item_port, record.get("pid"), "runtime.record_changed", str(write_error)))
            else:
                refused.append(_refusal(item_port, record.get("pid"), "runtime.stop_failed", str(ex)))
    if refused and not stopped:
        raise CLIError(refused[0]["message"])
    result = {"stopped": stopped, "refused": refused}
    if stopped:
        # The emulator is shared by every local runtime on the machine, so it can only
        # be released once nothing is left using it. Stopping it alongside the first
        # runtime would have pulled storage out from under any other still running.
        azurite = _release_azurite_if_idle()
        if azurite:
            result["azurite"] = azurite
    return result


def _remove_runtime_record(port, expected, recover=False):
    with _store_lock(_record_file(port), label="Logic Apps runtime ownership state"):
        current = _read_record(port)
        if not json_equal(current, expected):
            raise FileOperationError("Runtime ownership record changed during cleanup; no record was removed. Inspect it and retry.")
        if recover:
            processes = _runtime_process_records(current)
            if current.get("consumerPid"):
                processes.append({"pid": current["consumerPid"]})
            if any(_process_may_exist(item.get("pid")) for item in processes) or not _port_free(port):
                raise CLIError("Runtime cleanup is still pending: a recorded process or launch consumer may be running, "
                               "or the port is occupied. Its record was retained; inspect it and retry after it exits.")
        os.remove(_record_file(port))


def _live_runtime_records():
    if not os.path.isdir(STATE_DIR):
        return []
    live = []
    for name in os.listdir(STATE_DIR):
        item_port = _port_from_record_name(name)
        if item_port is None:
            continue
        try:
            record = _read_record(item_port)
        except FileOperationError:
            # Corruption cannot prove that a runtime has stopped using storage.
            live.append(item_port)
            continue
        consumer = {"pid": record.get("consumerPid"), "processCreateTimeUtc": record.get("consumerProcessCreateTimeUtc")} if record else {}
        if record and (_runtime_has_live_process(record) or _record_matches(consumer) or
                       _unverified_cleanup_pending(record)):
            live.append(item_port)
    return live


def _release_azurite_if_idle():
    try:
        if not read_azurite_record():
            return None
    except FileOperationError:
        return {"stopped": False, "reason": "invalid-record"}
    remaining = _live_runtime_records()
    if remaining:
        return {"stopped": False, "reason": "runtimes-still-running", "ports": remaining}
    return stop_azurite()


def _start_payload(status, project_path, port, background, pid, create_time, record_path, log_path, dependencies,
                   readiness=None):
    if readiness is None:
        listening, reachable, probe_error = _readiness(port)
    else:
        listening, reachable, probe_error = readiness
    endpoint = management_endpoint(port)
    return {
        "status": status,
        # 'state', top-level 'listening' and 'managementEndpoint' are aliases that
        # 'runtime show' already used for the same concepts. Emitting both from
        # both commands means a script that starts the runtime and then polls it
        # can read one set of field names throughout, which it previously could
        # not: start spelled them status/readiness.listening and show spelled
        # them state/listening, so the poll silently read nothing.
        "state": status,
        "projectPath": project_path,
        "port": port,
        "background": background,
        "pid": pid,
        "processCreateTimeUtc": create_time,
        "recordPath": record_path,
        "logPath": log_path,
        "dependencies": dependencies,
        "listening": listening,
        "managementEndpoint": endpoint,
        "readiness": {
            "listening": listening,
            "managementEndpointReachable": reachable,
            "managementEndpoint": endpoint,
            "lastProbeError": probe_error,
        }
    }


def _port_free(port):
    """Whether nothing is serving on the port.

    This used to decide by binding with ``SO_REUSEADDR``. On Windows that option means
    "let me bind even though someone else already has this address", which is the
    opposite of its Unix meaning, so any server that also set it -- the Functions host
    among them -- read as absent. ``runtime show`` then reported ``stopped`` for a
    runtime that was up and answering. Connecting is the claim actually being made, so
    make it directly, and keep a bind (without the option) to catch a socket that is
    bound but not yet accepting.
    """
    port = int(port)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.5)
        if probe.connect_ex(("127.0.0.1", port)) == 0:
            return False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def management_endpoint(port):
    return "http://localhost:{}/runtime/webhooks/workflow/api/management".format(port)


def probe_management_endpoint(port, timeout=2.0):
    """Actually call the management endpoint. Returns (reachable, lastProbeError).

    This used to be an alias for "something is bound to the port", which is a weaker
    claim than the field name made: any unrelated process holding the port read as
    reachable, and a host that was still starting up -- or had failed after binding --
    read as ready. An HTTP status, including 401 or 404, proves the workflow runtime is
    answering; a transport error does not.
    """
    url = "{}/workflows".format(management_endpoint(port))
    try:
        with urlopen(url, timeout=timeout):  # nosec B310 - fixed localhost scheme
            return True, None
    except HTTPURLError as ex:
        # The host answered; the status is irrelevant to reachability.
        return True, None if getattr(ex, "code", None) else str(ex)
    except URLError as ex:
        return False, str(getattr(ex, "reason", ex))
    except (OSError, ValueError) as ex:
        return False, str(ex)


def _readiness(port, probe=True):
    listening = not _port_free(port)
    if not listening:
        return False, False, "Nothing is listening on port {}.".format(port)
    if not probe:
        return listening, False, None
    reachable, error = probe_management_endpoint(port)
    return listening, reachable, error


def _wait_for_ready(port, pid, timeout):
    """Poll until the management endpoint answers, the process dies, or time runs out.

    Returns as soon as the host is ready, so a healthy start is not slowed down; only a
    start that never becomes ready pays the full timeout.
    """
    deadline = time.monotonic() + max(0, timeout or 0)
    readiness = _readiness(port)
    while time.monotonic() < deadline:
        if readiness[1]:
            return readiness
        if not _is_running(pid):
            return _readiness(port)
        time.sleep(1)
        readiness = _readiness(port)
    return readiness


def _record_file(port):
    return os.path.join(STATE_DIR, "runtime-{}.json".format(int(port)))


def _write_record(port, record, expected=None):
    _write_state_record(_record_file(port), record, "Could not write runtime state record.", expected=expected)


def _write_state_record(path, record, message, expected=None):
    staging = "{}.{}.write".format(path, uuid.uuid4().hex)
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        with _store_lock(path, label="Logic Apps runtime ownership state"):
            if expected is not None and not json_equal(_read_state_record(path, message), expected):
                raise FileOperationError("Runtime ownership record changed during cleanup; no record was written. Inspect it and retry.")
            with open(staging, "x", encoding="utf-8") as handle:
                json.dump(record, handle, indent=2, sort_keys=True)
                handle.write("\n")
            # Readers must always see a complete consumer record while a foreground
            # host updates its child identities, not a transient partial JSON file.
            os.replace(staging, path)
    except FileOperationError:
        raise
    except (OSError, CLIError) as ex:
        raise FileOperationError(message) from ex
    finally:
        try:
            os.remove(staging)
        except OSError:
            pass


def _read_record(port):
    return _read_state_record(_record_file(port), "Could not read runtime state record.")


def _unique_record_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate ownership record member.")
        result[key] = value
    return result


def _invalid_record_constant(_value):
    raise ValueError("Nonstandard ownership record value.")


def _read_state_record(path, message):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            record = json.load(handle, object_pairs_hook=_unique_record_object,
                               parse_constant=_invalid_record_constant)
    except FileNotFoundError:
        return None
    except (OSError, UnicodeError, ValueError, RecursionError) as ex:
        raise FileOperationError(message) from ex
    if not _record_shape_valid(record):
        raise FileOperationError(message)
    return record


def _valid_record_pid(pid, pending=False):
    return (pending and pid is None) or (isinstance(pid, int) and not isinstance(pid, bool) and pid > 0)


def _record_shape_valid(record):
    if not isinstance(record, dict) or "pid" not in record or not _valid_record_pid(record["pid"], pending=True):
        return False
    identities = [(record, "processCreateTimeUtc")]
    if "consumerPid" in record:
        if not _valid_record_pid(record["consumerPid"]):
            return False
        identities.append((record, "consumerProcessCreateTimeUtc"))
    children = record.get("childProcesses", [])
    if not isinstance(children, list):
        return False
    seen = {record["pid"]}
    for child in children:
        if not isinstance(child, dict) or not _valid_record_pid(child.get("pid")) or "childProcesses" in child:
            return False
        if child["pid"] in seen:
            return False
        seen.add(child["pid"])
        identities.append((child, "processCreateTimeUtc"))
    for item, name in identities:
        if item.get(name) is not None and not isinstance(item[name], str):
            return False
        if "cleanupPending" in item and not isinstance(item["cleanupPending"], bool):
            return False
    return True


def _port_from_record_name(name):
    if not name.startswith("runtime-") or not name.endswith(".json"):
        return None
    try:
        return int(name[len("runtime-"):-len(".json")])
    except ValueError:
        return None


def _record_matches(record):
    if not _record_shape_valid(record):
        return False
    pid = record.get("pid")
    expected = record.get("processCreateTimeUtc")
    if not isinstance(expected, str) or not expected.strip():
        return False
    actual = process_create_time_utc(pid)
    return bool(actual and actual == expected and _is_running(pid))


def _is_running(pid):
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
        return False
    if sys.platform == "win32":
        return process_create_time_utc(pid) is not None
    try:
        return psutil.Process(pid).status() not in (psutil.STATUS_ZOMBIE, psutil.STATUS_DEAD)
    except (psutil.Error, OSError):
        return False


def process_create_time_utc(pid):
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
        return None
    if sys.platform == "win32":
        return _windows_process_create_time_utc(pid)
    try:
        process = psutil.Process(pid)
        if process.status() in (psutil.STATUS_ZOMBIE, psutil.STATUS_DEAD):
            return None
        return datetime.fromtimestamp(process.create_time(), timezone.utc).isoformat().replace("+00:00", "Z")
    except (psutil.Error, OSError, OverflowError, TypeError, ValueError):
        return None


def _windows_process_create_time_utc(pid):
    return _windows_process_snapshot(pid)[0]


def _windows_process_snapshot(pid):
    # CIM's CreationDate has microsecond precision, formatted as seven fractional
    # digits. Keep that representation so existing verified Windows records match.
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.GetProcessTimes.argtypes = (wintypes.HANDLE,) + (ctypes.POINTER(wintypes.FILETIME),) * 4
    kernel32.GetProcessTimes.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel32.CloseHandle.restype = wintypes.BOOL
    handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not handle:
        return None, False
    try:
        creation, exit_time, kernel, user = (wintypes.FILETIME() for _ in range(4))
        if not kernel32.GetProcessTimes(handle, ctypes.byref(creation), ctypes.byref(exit_time),
                                        ctypes.byref(kernel), ctypes.byref(user)):
            return None, False
        if exit_time.dwHighDateTime or exit_time.dwLowDateTime:
            return None, True
        ticks = (creation.dwHighDateTime << 32) | creation.dwLowDateTime
        seconds, fraction = divmod(ticks - 116444736000000000, 10000000)
        value = datetime.fromtimestamp(seconds, timezone.utc)
        return "{}.{:06d}0Z".format(value.strftime("%Y-%m-%dT%H:%M:%S"), fraction // 10), False
    except (OSError, OverflowError, ValueError):
        return None, False
    finally:
        kernel32.CloseHandle(handle)


def _process_tree_snapshot():
    """Capture parentage and original CIM creation identities in the same snapshot."""
    script = ("Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,"
              "@{Name='ProcessCreateTimeUtc';Expression={if ($_.CreationDate) {"
              "$_.CreationDate.ToUniversalTime().ToString('o').Replace('+00:00','Z')}}} "
              "| ConvertTo-Json -Compress")
    try:
        completed = subprocess.run([_powershell_executable(), "-NoProfile", "-Command", script],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   universal_newlines=True, timeout=30, check=False)
    except (OSError, subprocess.SubprocessError) as ex:
        raise OSError("Could not verify the process tree; no processes were stopped.") from ex
    if completed.returncode:
        raise OSError("Could not verify the process tree; no processes were stopped.")
    try:
        payload = json.loads(completed.stdout or "[]")
    except (ValueError, RecursionError) as ex:
        raise OSError("Could not verify the process tree; no processes were stopped.") from ex
    if isinstance(payload, dict):
        payload = [payload]
    if not isinstance(payload, list):
        raise OSError("Could not verify the process tree; no processes were stopped.")
    pairs = []
    seen = set()
    for item in payload:
        if not isinstance(item, dict):
            raise OSError("Could not verify the process tree; no processes were stopped.")
        pid, parent = item.get("ProcessId"), item.get("ParentProcessId")
        if (not isinstance(pid, int) or isinstance(pid, bool) or pid < 0 or
                not isinstance(parent, int) or isinstance(parent, bool) or parent < 0 or pid in seen):
            raise OSError("Could not verify the process tree; no processes were stopped.")
        seen.add(pid)
        pairs.append((pid, parent, item.get("ProcessCreateTimeUtc")))
    return pairs


def _descendant_pids(pid):
    """Descendants of pid, deepest level first. Windows only; [] elsewhere.

    Needed because the tools this CLI launches on Windows are ``.cmd`` shims: killing
    the recorded pid kills the shim and reparents the process that is actually serving,
    which then keeps the port bound forever. Observed with Azurite -- 'stop' reported
    success, the pid was gone, and the emulator was still answering.
    """
    if sys.platform != "win32":
        return []
    children = {}
    try:
        snapshot = _process_tree_snapshot()
    except OSError:
        return []
    for item in snapshot:
        children.setdefault(item[1], []).append(item[0])
    levels = []
    frontier = [int(pid)]
    seen = {int(pid)}
    while frontier:
        nxt = []
        for current in frontier:
            for child in children.get(current, []):
                if child not in seen:
                    seen.add(child)
                    nxt.append(child)
        if nxt:
            levels.append(nxt)
        frontier = nxt
    return [item for level in reversed(levels) for item in level]


def _creation_datetime(value):
    if not isinstance(value, str):
        return None
    match = re.fullmatch(
        r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,7}))?(Z|[+-]\d{2}:\d{2})", value)
    if not match:
        return None
    try:
        base, fraction, offset = match.groups()
        zone = timezone.utc
        if offset != "Z":
            hours, minutes = int(offset[1:3]), int(offset[4:6])
            if hours > 23 or minutes > 59:
                return None
            delta = timedelta(hours=hours, minutes=minutes)
            zone = timezone(-delta if offset[0] == "-" else delta)
        return datetime.strptime(base, "%Y-%m-%dT%H:%M:%S").replace(
            microsecond=int(((fraction or "") + "000000")[:6]), tzinfo=zone)
    except (ValueError, OverflowError):
        return None


def _descendant_process_records(pid, expected, snapshot, excluded=None):
    children = {}
    identities = {}
    for item in snapshot:
        child, parent = item[:2]
        children.setdefault(parent, []).append(child)
        identities[child] = item[2] if len(item) == 3 else None
    if identities.get(pid) != expected:
        raise OSError("The parent process identity changed; no processes were stopped.")
    records = []
    excluded = set() if excluded is None else excluded
    frontier = [(pid, _creation_datetime(expected))]
    seen = {pid}
    while frontier:
        next_level = []
        level = []
        for parent, parent_created in frontier:
            for child in children.get(parent, []):
                if child in seen:
                    continue
                seen.add(child)
                created = _creation_datetime(identities.get(child))
                # Stale PPIDs can refer to a newer, unrelated parent after PID
                # reuse. Exclude only a still-verifiable earlier incarnation.
                preexisting = parent in excluded or (parent_created is not None and created is not None and
                                                     created < parent_created)
                if preexisting and _record_matches({"pid": child, "processCreateTimeUtc": identities[child]}):
                    excluded.add(child)
                    next_level.append((child, created))
                    continue
                proven = parent not in excluded and parent_created is not None and created is not None and created >= parent_created
                record = {"pid": child, "processCreateTimeUtc": identities[child] if proven else None}
                if not proven:
                    record["cleanupPending"] = True
                level.append(record)
                next_level.append((child, created if proven else None))
        records = level + records
        frontier = next_level
    return records


class _ProcessCleanupError(OSError):
    def __init__(self, children):
        super().__init__("A process could not be safely stopped; its ownership record was retained.")
        self.children = children


def _terminate_record_process(record, process_record):
    try:
        expected = process_record.get("processCreateTimeUtc")
        if not isinstance(expected, str) or not expected.strip():
            raise OSError("Could not verify the recorded process identity; no process was stopped.")
        children = _terminate(process_record["pid"], expected=expected)
    except _ProcessCleanupError as ex:
        children = ex.children
        record["cleanupPending"] = True
        failure = ex
    except (OSError, subprocess.SubprocessError):
        record["cleanupPending"] = True
        raise
    else:
        failure = None
    if children:
        recorded = record.setdefault("childProcesses", [])
        known = {item["pid"] for item in recorded}
        for child in children:
            if child["pid"] != record["pid"] and child["pid"] not in known:
                recorded.append(child)
                known.add(child["pid"])
    if failure:
        raise failure


def _stop_process(pid, check, expected=None):
    if not _valid_record_pid(pid) or _creation_datetime(expected) is None:
        raise OSError("Could not verify the process identity; no process was stopped.")
    # Keep the queried process object/handle through the signal, rather than
    # starting PowerShell with a raw PID that could recycle while it launches.
    script = ("$process = Get-Process -Id {} -ErrorAction Stop; "
              "$created = $process.StartTime.ToUniversalTime(); "
              "$created = $created.AddTicks(-($created.Ticks % 10)); "
              "if ($created.ToString('o').Replace('+00:00','Z') -ne '{}') "
              "{{ throw 'Process creation identity changed; no process was stopped.' }}; "
              "Stop-Process -InputObject $process -Force -ErrorAction Stop").format(
                  pid, expected.replace("'", "''"))
    subprocess.run([_powershell_executable(), "-NoProfile", "-Command", script],
                   check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def _powershell_executable():
    return shutil.which("powershell") or os.path.join(
        os.environ.get("SystemRoot", r"C:\Windows"), "System32", "WindowsPowerShell", "v1.0", "powershell.exe")


def _wait_for_recorded_exit(record):
    deadline = time.monotonic() + 5
    while _process_may_exist(record["pid"]):
        actual = process_create_time_utc(record["pid"])
        expected = record.get("processCreateTimeUtc")
        if actual and actual != expected:
            return False
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.1)
    return True


def _terminate(pid, expected=None):
    if sys.platform == "win32":
        # Snapshot before killing: once the parent is gone its children are reparented
        # and the relationship is no longer discoverable.
        if expected is None:
            expected = process_create_time_utc(pid)
        if not isinstance(expected, str) or not expected.strip():
            raise OSError("Could not verify the process identity; no processes were stopped.")
        descendants = _descendant_process_records(pid, expected, _process_tree_snapshot())
        if not _record_matches({"pid": pid, "processCreateTimeUtc": expected}):
            raise OSError("The parent process identity changed; no processes were stopped.")
        try:
            _stop_process(pid, check=True, expected=expected)
        except (OSError, subprocess.SubprocessError) as ex:
            if not _wait_for_recorded_exit({"pid": pid, "processCreateTimeUtc": expected}):
                raise _ProcessCleanupError(descendants) from ex
        refused = False
        for child in descendants:
            if _record_matches(child):
                try:
                    _stop_process(child["pid"], check=True, expected=child["processCreateTimeUtc"])
                except (OSError, subprocess.SubprocessError):
                    if not _wait_for_recorded_exit(child):
                        child["cleanupPending"] = True
                        refused = True
            elif not _wait_for_recorded_exit(child):
                child["cleanupPending"] = True
                refused = True
        if refused:
            raise _ProcessCleanupError(descendants)
        return descendants
    if expected is not None and not _record_matches({"pid": pid, "processCreateTimeUtc": expected}):
        raise OSError("The process identity changed; no process was stopped.")
    os.kill(int(pid), 15)
    return None


def _refusal(port, pid, code, message):
    return {"port": port, "pid": pid, "reasonCode": code, "message": message, "alternate": "Stop the process yourself or use the tool that started it."}


def _cli_version(cmd):
    try:
        return cmd.cli_ctx.data.get("version")
    except AttributeError:
        return None
