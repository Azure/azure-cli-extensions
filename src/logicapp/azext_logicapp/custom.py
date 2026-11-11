# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=redefined-builtin,import-error,no-name-in-module

import json
import os
import sys
from knack.log import get_logger

from azure.cli.core.azclierror import ClientRequestError, InvalidArgumentValueError, MutuallyExclusiveArgumentError, RequiredArgumentMissingError, ValidationError
from azure.cli.core.util import user_confirmation

from ._constants import DEFAULT_LOCAL_PORT, LOGICAPP_REDACTION_SENTINEL
from ._connection import (
    connection_delete as _connection_delete,
    connection_list as _connection_list, connection_show as _connection_show,
    connection_test as _connection_test, create_local_connection, reject_secret_shaped_name)
from ._context import get_context, store_path
from . import _context
from ._dependencies import INSTALLABLE_KINDS, install_dependency, refusal_message, uninstall_dependency
from ._local import dependencies_root, dependency_report, find_tool, start_runtime, stop_runtime, show_runtime, validate_port
from ._identity import apply_identity, get_identity, plan_assign, plan_remove
from ._paging import operation_kind
from . import _managed_api
from . import _managed_connection
from . import _workflow_discovery
from . import _workflow_mutation
from . import _workflow_state
from . import _run_execution
from ._runtime_client import (
    build_runtime_client, operation_group_operation_path, operation_group_operations_path,
    operation_group_path, operation_groups_path, page_items, run_action_path, run_actions_path,
    trigger_run_path, workflow_run_path, workflow_runs_path)
from ._workflow_validation import validate_runtime_workflow
from ._workflow import HOST_JSON, LOCAL_SETTINGS_JSON, abs_path, create_workflow_file, deterministic_package, static_validate, validate_workflow_name, workflow_json, write_json_file

logger = get_logger(__name__)


def _test_project_root(path, context):
    if path is not None and (not isinstance(path, str) or not path.strip()):
        raise InvalidArgumentValueError("--path must name a local project; omit it to use a local context.")
    try:
        return _project_path_from_context(path, context)
    except MutuallyExclusiveArgumentError as ex:
        raise MutuallyExclusiveArgumentError(
            "Workflow testing requires a local project. Select a local context or pass explicit --path "
            "without a cloud --context.") from ex


def _test_output_path(root, value):
    if isinstance(value, str):
        if os.path.splitdrive(value)[0] and not os.path.isabs(value):
            raise InvalidArgumentValueError(
                "Test output paths must be fully qualified or relative to the selected local project, "
                "not drive-relative.")
        return os.path.join(root, value)
    return value


def test_create(cmd, workflow, path=None, context=None, output_path=None, trigger=None):
    del cmd
    from ._test_scaffold import create_project
    root = _test_project_root(path, context)
    return create_project(root, workflow, _test_output_path(root, output_path), trigger)


def test_run(cmd, workflow, path=None, context=None, test_project=None, accept_sdk_terms=False,
             trust_project=False, restore=False, nuget_config=None, timeout=300, report_path=None):
    from ._runtime_doctor import finish_doctor_command
    from ._sdk_testing import run_report
    root = _test_project_root(path, context)
    return finish_doctor_command(cmd, run_report(
        root, workflow, test_project, accept_sdk_terms, trust_project, restore, nuget_config,
        timeout, _test_output_path(root, report_path)))


def test_plan(cmd, path=None, workflow=None, test_project=None, report_path=None, force=False,
              strict=False, context=None):
    from ._runtime_doctor import finish_doctor_command
    from ._testing import plan_report
    root = _test_project_root(path, context)
    report_path = _test_output_path(root, report_path)
    return finish_doctor_command(cmd, plan_report(root, workflow, test_project, report_path, force, strict))


def test_results_show(cmd, result_file, workflow_file=None):
    from ._runtime_doctor import finish_doctor_command
    from ._testing import results_report
    return finish_doctor_command(cmd, results_report(result_file, workflow_file))


def project_create(cmd, path, workflow=None, workflow_kind="Stateful", adopt=False, force=False):
    del cmd
    root = abs_path(path)
    workflow_kind = _workflow_kind_value(workflow_kind)
    validate_workflow_name(workflow)
    if os.path.exists(root):
        entries = [name for name in os.listdir(root) if name not in (".", "..")]
        recognized = os.path.isfile(os.path.join(root, "host.json"))
        if entries and not recognized and not adopt:
            raise ValidationError("Directory is non-empty; use --adopt to initialize it as a Logic Apps project.")
    else:
        os.makedirs(root)
    files = []
    item = write_json_file(os.path.join(root, "host.json"), HOST_JSON, force=force)
    item["class"] = "hostConfiguration"
    files.append(item)
    item = write_json_file(os.path.join(root, "local.settings.json"), LOCAL_SETTINGS_JSON, force=force)
    item["class"] = "localSettings"
    files.append(item)
    if workflow:
        item = write_json_file(os.path.join(root, workflow, "workflow.json"), workflow_json(workflow_kind), force=force)
        item["class"] = "workflowDefinition"
        files.append(item)
    return {"path": root, "workflow": workflow, "workflowKind": workflow_kind if workflow else None, "files": files}


def workflow_create(cmd, path=None, workflow=None, kind=None, file=None, force=False, context=None):
    del cmd
    root = _project_path_from_context(path, context)
    return create_workflow_file(root, workflow, workflow_kind=_workflow_kind_value(kind) if kind else None,
                                definition_file=file, force=force)


def workflow_list(cmd, resource_group_name=None, name=None, local=False, port=None,
                  host_key=None, context=None, max_items=None, next_token=None):
    client, _ = _client_from_target(cmd, resource_group_name, name, local, port, host_key, context)
    return _workflow_discovery.list_workflows(client, max_items, next_token)


def workflow_show(cmd, workflow, resource_group_name=None, name=None, local=False, port=None,
                  host_key=None, context=None):
    validate_workflow_name(workflow)
    client, _ = _client_from_target(cmd, resource_group_name, name, local, port, host_key, context)
    return _workflow_discovery.show_workflow(client, workflow)


def workflow_export(cmd, workflow, output_path, force=False, resource_group_name=None, name=None,
                    local=False, port=None, host_key=None, context=None):
    validate_workflow_name(workflow)
    _workflow_discovery.export_destination(output_path, force)
    client, _ = _client_from_target(cmd, resource_group_name, name, local, port, host_key, context)
    return _workflow_discovery.export_workflow(client, workflow, output_path, force)


def workflow_set(cmd, workflow, file, if_match=None, yes=False, allow_non_atomic=False,
                 resource_group_name=None, name=None, local=False, port=None, host_key=None, context=None):
    validate_workflow_name(workflow)
    client, _ = _client_from_target(cmd, resource_group_name, name, local, port, host_key, context)
    return _workflow_mutation.set_workflow(client, workflow, file, if_match, yes, allow_non_atomic)


def workflow_delete(cmd, workflow, if_match=None, yes=False, allow_non_atomic=False,
                    resource_group_name=None, name=None, local=False, port=None, host_key=None, context=None):
    validate_workflow_name(workflow)
    client, _ = _client_from_target(cmd, resource_group_name, name, local, port, host_key, context)
    return _workflow_mutation.delete_workflow(client, workflow, if_match, yes, allow_non_atomic)


def workflow_enable(cmd, workflow, yes=False, allow_non_atomic=False, resource_group_name=None,
                    name=None, local=False, port=None, host_key=None, context=None):
    validate_workflow_name(workflow)
    client, _ = _client_from_target(cmd, resource_group_name, name, local, port, host_key, context)
    return _workflow_state.set_workflow_state(client, workflow, "Enabled", yes, allow_non_atomic)


def workflow_disable(cmd, workflow, yes=False, allow_non_atomic=False, resource_group_name=None,
                     name=None, local=False, port=None, host_key=None, context=None):
    validate_workflow_name(workflow)
    client, _ = _client_from_target(cmd, resource_group_name, name, local, port, host_key, context)
    return _workflow_state.set_workflow_state(client, workflow, "Disabled", yes, allow_non_atomic)


def connection_create(cmd, name, connector, secret=None, path=None, secret_parameter=None,
                      parameter_set=None, parameter=None, app_setting=None,
                      force=False, no_gitignore=False, context=None,
                      managed_api=False, resource_group_name=None, connection_name=None,
                      location=None, auth_mode=None, display_name=None,
                      user_assigned_identity=None, no_browser=False, consent_timeout=None):
    if managed_api:
        logger.warning(
            "connection create --managed-api is deprecated. Use connection managed create "
            "--name CONNECTION --logic-app-name APP. Legacy --name still identifies the app.")
        return _connection_create_managed(
            cmd, name, connector, resource_group_name=resource_group_name,
            connection_name=connection_name, location=location, auth_mode=auth_mode,
            display_name=display_name, parameter=parameter, secret_parameter=secret_parameter,
            parameter_set=parameter_set, user_assigned_identity=user_assigned_identity,
            force=force, secret=secret, path=path, context=context, app_setting=app_setting,
            no_browser=no_browser, consent_timeout=consent_timeout)
    del cmd
    for flag, value in (("--connection-name", connection_name), ("--location", location),
                        ("--auth-mode", auth_mode), ("--display-name", display_name),
                        ("--user-assigned-identity", user_assigned_identity),
                        ("--consent-timeout", consent_timeout)):
        if value:
            raise MutuallyExclusiveArgumentError(
                "{} applies only to 'az logicapp connection create --managed-api'.".format(flag))
    if no_browser:
        raise MutuallyExclusiveArgumentError(
            "--no-browser applies only to 'az logicapp connection create --managed-api "
            "--auth-mode oauth'.")
    reject_secret_shaped_name(name, "--name")
    reject_secret_shaped_name(connector, "--connector")
    root = _project_path_from_context(path, context)
    secret_value = None
    if secret:
        reject_secret_shaped_name(secret, "--secret")
        secret_value = _read_secret_from_stdin(secret)
    return create_local_connection(root, name, connector, secret_setting=secret, secret_value=secret_value,
                                   secret_parameter=secret_parameter or "connectionString",
                                   parameter_set=parameter_set or "connectionString",
                                   parameters=parameter, app_settings=app_setting,
                                   force=force, manage_gitignore=not no_gitignore)


def connection_managed_create(cmd, name, connector, auth_mode, logic_app_name=None,
                              resource_group_name=None, location=None, display_name=None,
                              parameter=None, secret_parameter=None,
                              parameter_set=None, user_assigned_identity=None, no_browser=False,
                              consent_timeout=None, force=False, path=None, context=None):
    if path is not None and (not isinstance(path, str) or not path.strip()):
        raise InvalidArgumentValueError("--path must identify an existing local project.")
    if logic_app_name is not None and (path is not None or context is not None):
        raise MutuallyExclusiveArgumentError("--logic-app-name cannot be combined with --path or --context.")
    selected = None
    if context is not None or (path is None and logic_app_name is None):
        selected, _ = get_context(context)
    if logic_app_name is None and getattr(resource_group_name, "is_default", False):
        resource_group_name = None
    local_project = None
    if selected:
        target = selected["target"]
        if target["kind"] == "local":
            local_project = abs_path(path if path is not None else target["path"])
        else:
            if path is not None or resource_group_name is not None:
                raise MutuallyExclusiveArgumentError("A cloud --context cannot be combined with --path or --resource-group.")
            logic_app_name, resource_group_name = target["logicAppName"], target["resourceGroup"]
    elif path is not None:
        local_project = abs_path(path)
    elif logic_app_name is None:
        raise RequiredArgumentMissingError(
            "Choose a local --path/--context or a deployed --logic-app-name/--context.")
    return _connection_create_managed(
        cmd, logic_app_name, connector, resource_group_name=resource_group_name,
        connection_name=name, location=location, auth_mode=auth_mode,
        display_name=display_name, parameter=parameter, secret_parameter=secret_parameter,
        parameter_set=parameter_set, user_assigned_identity=user_assigned_identity,
        no_browser=no_browser, consent_timeout=consent_timeout, force=force, local_project=local_project)


def _connection_create_managed(cmd, name, connector, resource_group_name=None, connection_name=None,
                               location=None, auth_mode=None, display_name=None, parameter=None,
                               secret_parameter=None, parameter_set=None,
                               user_assigned_identity=None, force=False, secret=None, path=None,
                               context=None, app_setting=None, no_browser=False,
                               consent_timeout=None, local_project=None):
    for flag, value in (("--secret", secret), ("--path", path), ("--context", context),
                        ("--app-setting", app_setting)):
        if value:
            raise MutuallyExclusiveArgumentError(
                "{} applies to local project connections and cannot be combined with "
                "--managed-api.".format(flag))
    required = [("--connection-name", connection_name), ("--auth-mode", auth_mode)]
    if local_project is None:
        required += [("--resource-group", resource_group_name), ("--location", location)]
    missing = [flag for flag, value in required if not value]
    if missing:
        raise RequiredArgumentMissingError(
            "Managed connection creation requires {}. For a deployed target, --logic-app-name "
            "identifies the app and --name identifies the connection. In legacy --managed-api mode, "
            "--name identifies the app and --connection-name identifies the connection.".format(
                ", ".join(missing)))
    secret_value = None
    if secret_parameter:
        secret_value = _read_secret_from_stdin(secret_parameter)
    if auth_mode != "oauth":
        for flag, value in (("--no-browser", no_browser), ("--consent-timeout", consent_timeout)):
            if value:
                raise MutuallyExclusiveArgumentError(
                    "{} applies only to --auth-mode oauth.".format(flag))
    return _managed_connection.create_managed_connection(
        cmd, resource_group_name, name, connection_name, connector, location, auth_mode,
        display_name=display_name, parameter=parameter, secret_parameter=secret_parameter,
        secret_value=secret_value, parameter_set=parameter_set,
        user_assigned_identity=user_assigned_identity, force=force,
        no_browser=no_browser, consent_timeout=consent_timeout,
        **({"local_project": local_project} if local_project is not None else {}))


def connection_acl_list(cmd, resource_group_name, connection):
    return _managed_connection.acl_list(cmd, resource_group_name, connection)


def connection_acl_show(cmd, resource_group_name, connection, policy):
    return _managed_connection.acl_show(cmd, resource_group_name, connection, policy)


def connection_acl_add(cmd, resource_group_name, connection, object_id, tenant_id=None,
                       policy=None, location=None):
    return _managed_connection.acl_add(cmd, resource_group_name, connection, object_id,
                                       tenant_id=tenant_id, policy=policy, location=location)


def connection_acl_remove(cmd, resource_group_name, connection, policy, yes=False):
    user_confirmation(
        "Remove access policy '{}' from connection '{}'? The principal it names will lose access "
        "to this connection.".format(policy, connection), yes)
    return _managed_connection.acl_remove(cmd, resource_group_name, connection, policy)


def connection_list(cmd, resource_group_name, name, max_items=None, next_token=None, show_runtime_urls=False):
    return _connection_list(cmd, resource_group_name, name, max_items=max_items, next_token=next_token,
                            show_runtime_urls=show_runtime_urls)


def connection_show(cmd, resource_group_name, name, connection, connection_class=None, show_runtime_urls=False):
    return _connection_show(cmd, resource_group_name, name, connection, connection_class=connection_class,
                            show_runtime_urls=show_runtime_urls)


def connection_test(cmd, resource_group_name, name, connection, connection_class=None):
    return _connection_test(cmd, resource_group_name, name, connection, connection_class=connection_class)


def connection_delete(cmd, resource_group_name, name, connection, connection_class=None,
                      keep_resource=False, yes=False):
    user_confirmation(
        "Remove connection '{conn}' from '{app}'? Workflows that reference it will fail until they "
        "are updated. A managed API connection is deleted only when this entry establishes "
        "exclusive system-assigned identity ownership. Shared user-assigned identity access "
        "is retained.".format(conn=connection, app=name), yes)
    return _connection_delete(cmd, resource_group_name, name, connection,
                              connection_class=connection_class, keep_resource=keep_resource)


def _read_secret_from_stdin(setting_name):
    """D135: the value never appears on the command line, so it arrives on stdin."""
    if sys.stdin is None or sys.stdin.isatty():
        raise RequiredArgumentMissingError(
            "The value for '{0}' must be supplied on standard input, so it never appears in shell history.\n"
            "  PowerShell:  $env:SB | az logicapp connection create ... --secret {0}\n"
            "  bash:        printf '%s' \"$SB\" | az logicapp connection create ... --secret {0}".format(setting_name))
    value = sys.stdin.read()
    if value.endswith("\r\n"):
        value = value[:-2]
    elif value.endswith("\n"):
        value = value[:-1]
    value = value.strip("\ufeff")
    if not value.strip():
        raise ValidationError("The secret value read from standard input was empty.")
    return value


def context_create(cmd, name, path=None, resource_group_name=None, logic_app_name=None, port=None, use=False):
    del cmd
    return _context.create_context(name, path, resource_group_name, logic_app_name,
                                   DEFAULT_LOCAL_PORT if port is None else port, use)


def context_use(cmd, name):
    del cmd
    return _context.use_context(name)


def context_list(cmd):
    del cmd
    return _context.list_contexts()


def context_show(cmd, name=None):
    del cmd
    return _context.show_context(name)


def context_update(cmd, name, kind=None, path=None, port=None, resource_group_name=None, logic_app_name=None, yes=False):
    return _context.update_context(cmd, name, kind, path, port, resource_group_name, logic_app_name, yes)


def context_delete(cmd, name, yes=False):
    return _context.delete_context(cmd, name, yes)


def workflow_validate(cmd, path=None, workflow=None, all=False, with_runtime=False, fail_on_warning=False, resource_group_name=None, name=None, local=False, port=None, host_key=None, context=None):
    root = _project_path_from_context(path, context, allow_cloud=with_runtime)
    report = static_validate(root, workflow=workflow, all_workflows=all)
    if with_runtime:
        client, resolved = _client_from_target(cmd, resource_group_name, name, local, port, host_key, context)
        checked = 0
        if workflow:
            target_workflows = [(workflow, os.path.join(root, workflow, "workflow.json"))]
        else:
            target_workflows = list(_discover_for_runtime(root, all))
        for workflow_name, workflow_path in target_workflows:
            resolved_path = workflow_path or os.path.join(root, workflow_name, "workflow.json")
            try:
                body = _runtime_validate_body(resolved_path, workflow_name, root)
                validate_runtime_workflow(client, workflow_name, body)
                checked += 1
            except _workflow_mutation._REQUEST_ERRORS as ex:
                report["findings"].append({"workflow": workflow_name, "file": os.path.abspath(resolved_path), "jsonPath": "$", "rule": "validation.runtime_failed", "severity": "error", "message": str(ex), "recommendation": "Fix the runtime validation error and retry."})
        report["coverage"]["runtime"] = True
        report["coverage"]["checks"]["runtimeTemplate"] = bool(target_workflows) and checked == len(target_workflows)
        report["coverage"]["target"] = resolved
        _recount(report)
    if report["summary"]["errors"] or (fail_on_warning and report["summary"]["warnings"]):
        raise ValidationError(json.dumps(report, separators=(",", ":")))
    return report


def deployment_package(cmd, path=None, output_path=None, manifest=None, force=False):
    del cmd
    return deterministic_package(path or os.curdir, output_path, manifest_path=manifest, force=force)


def dependency_check(cmd, kind=None, path=None, context=None):
    del cmd
    project_path = None
    resolved = path or _project_path_from_context(None, context) if (path or context) else _active_context_path()
    if resolved and os.path.isdir(os.path.expanduser(resolved)):
        project_path = os.path.abspath(os.path.expanduser(resolved))
    return dependency_report(kind=kind, project_path=project_path)


def dependency_install(cmd, kind=None, version=None, target_dir=None, source_url=None,
                       gh_token=None, force=False, yes=False):
    del cmd
    kinds = _install_kinds(kind)
    if source_url and len(kinds) != 1:
        raise MutuallyExclusiveArgumentError("--source-url applies to a single dependency; pass exactly one --kind.")
    if version and len(kinds) != 1:
        raise MutuallyExclusiveArgumentError("--version applies to a single dependency; pass exactly one --kind.")

    root = os.path.abspath(os.path.expanduser(target_dir)) if target_dir else dependencies_root()

    # An acceptable tool already on PATH is not replaced silently. Downloading a second
    # Node.js over a working one wastes time and bandwidth and leaves two copies whose
    # precedence is not obvious. --force or an explicit --version still installs.
    planned, skipped = [], []
    for item in kinds:
        existing_path, existing_source = (None, None) if (force or version) else find_tool(item)
        if existing_path:
            skipped.append({
                "kind": item, "result": "skipped", "reason": "alreadyPresent",
                "path": existing_path, "source": existing_source,
                "message": "{} is already available; pass --force to install a CLI-managed copy "
                           "anyway.".format(item)
            })
        else:
            planned.append(item)

    if not planned:
        return {"root": root, "value": skipped}

    user_confirmation(
        "This downloads third-party software from its publisher and installs it under {}. "
        "That folder is shared with Visual Studio Code's Azure Logic Apps extension. Continue?".format(root),
        yes)

    installed = []
    for item in planned:
        installed.append(install_dependency(
            item, version=version, root=root, source_url=source_url, gh_token=gh_token, force=force))
    return {"root": root, "value": skipped + installed}


def dependency_uninstall(cmd, kind=None, target_dir=None, yes=False):
    del cmd
    kinds = _install_kinds(kind)
    root = os.path.abspath(os.path.expanduser(target_dir)) if target_dir else dependencies_root()
    user_confirmation(
        "This removes only what 'az logicapp dependency install' recorded installing under {}. "
        "Anything you or Visual Studio Code installed is left alone. Continue?".format(root),
        yes)
    return {"root": root, "value": [uninstall_dependency(item, root=root) for item in kinds]}


def _install_kinds(kind):
    """Resolve --kind for the install/uninstall pair.

    Defaulting to every installable kind rather than every known kind keeps the
    no-argument case from failing on the two this CLI deliberately will not install.
    """
    if not kind:
        return list(INSTALLABLE_KINDS)
    requested = [kind] if isinstance(kind, str) else list(kind)
    for item in requested:
        message = refusal_message(item)
        if message:
            raise InvalidArgumentValueError(message)
        if item not in INSTALLABLE_KINDS:
            raise InvalidArgumentValueError(
                "Unknown dependency kind '{}'. Installable kinds: {}.".format(item, ", ".join(INSTALLABLE_KINDS)))
    seen = []
    for item in requested:
        if item not in seen:
            seen.append(item)
    return seen


def connector_list(cmd, resource_group_name=None, name=None, local=False, port=None, host_key=None, context=None, workflow_kind=None, max_items=None, next_token=None):
    del workflow_kind
    client, _ = _client_from_target(cmd, resource_group_name, name, local, port, host_key, context)
    payload = client.list(operation_groups_path(), next_token=next_token, max_items=max_items)
    return {
        "value": _value(payload),
        "nextContinuationToken": payload.get("nextContinuationToken") if isinstance(payload, dict) else None,
    }


def connector_show(cmd, connector, resource_group_name=None, name=None, local=False, port=None, host_key=None, context=None):
    client, _ = _client_from_target(cmd, resource_group_name, name, local, port, host_key, context)
    return client.get(operation_group_path(connector))


# The runtime's TriggerType enum is NotSpecified/Batch/Single, so a trigger is exactly an
# operation whose properties.trigger is batch or single.
_RUNTIME_TRIGGER_VALUES = ("batch", "single")


def _runtime_operation_is_trigger(item):
    """Classify a built-in operation using the field the runtime actually sets.

    ``properties.trigger`` is an explicit discriminator on the runtime's ServiceOperation,
    so unlike the managed-connector catalog -- where the shape varies and the kind has to
    be inferred from several candidate fields -- this needs no guessing.
    """
    properties = item.get("properties") if isinstance(item, dict) else None
    trigger = (properties or {}).get("trigger") if isinstance(properties, dict) else None
    return str(trigger or "").strip().lower() in _RUNTIME_TRIGGER_VALUES


def _runtime_operation_matches(item, needle):
    properties = item.get("properties") if isinstance(item, dict) else None
    properties = properties if isinstance(properties, dict) else {}
    haystack = " ".join(str(value or "") for value in (
        item.get("name") if isinstance(item, dict) else None,
        item.get("id") if isinstance(item, dict) else None,
        properties.get("summary"),
        properties.get("description")))
    return needle in haystack.lower()


def connector_operation_list(cmd, connector, resource_group_name=None, name=None, local=False, port=None,
                             host_key=None, context=None, kind="all", search=None,
                             max_items=None, next_token=None):
    kind = operation_kind(kind)
    client, _ = _client_from_target(cmd, resource_group_name, name, local, port, host_key, context)
    payload = client.get(operation_group_operations_path(connector))
    items = _value(payload)

    # Filtering happens before paging: paging the unfiltered list would cut pages from a
    # set the caller never asked for, so --max-items and --kind together would drop
    # matches silently.
    if search:
        needle = str(search).strip().lower()
        items = [item for item in items if _runtime_operation_matches(item, needle)]
    if kind != "all":
        want_trigger = kind == "trigger"
        items = [item for item in items if _runtime_operation_is_trigger(item) == want_trigger]

    page, next_page_token = page_items(items, next_token=next_token, max_items=max_items)
    # Built explicitly rather than copied from the upstream payload: dict(payload) leaked
    # whatever else the runtime happened to return (a meaningless skipToken, for one) and
    # would silently grow new keys as the runtime evolves.
    return {
        "connector": connector,
        "kind": kind,
        "value": page,
        "nextContinuationToken": next_page_token,
    }


def connector_operation_show(cmd, connector, operation, resource_group_name=None, name=None, local=False,
                             port=None, host_key=None, context=None):
    client, _ = _client_from_target(cmd, resource_group_name, name, local, port, host_key, context)
    return client.get(operation_group_operation_path(connector, operation))


def connector_managed_list(cmd, location, search=None, max_items=None, next_token=None):
    return _managed_api.connector_managed_list(
        cmd, location, search=search, max_items=max_items, next_token=next_token)


def connector_managed_show(cmd, connector, location=None):
    return _managed_api.connector_managed_show(cmd, connector, location=location)


def connector_managed_operation_list(cmd, connector, location=None, kind="all", search=None,
                                     max_items=None, next_token=None):
    return _managed_api.connector_managed_operation_list(
        cmd, connector, location=location, kind=kind, search=search, max_items=max_items, next_token=next_token)


def connector_managed_operation_show(cmd, connector, operation, location=None):
    return _managed_api.connector_managed_operation_show(cmd, connector, operation, location=location)


def runtime_doctor(cmd, path=None, context=None, port=None, probe_timeout=2, strict=False):
    from ._runtime_doctor import doctor_report, finish_doctor_command
    return finish_doctor_command(cmd, doctor_report(path, context, port, probe_timeout, strict))


def runtime_start(cmd, path=None, port=None, background=False, ready_timeout=30, no_azurite=False):
    root, port = _local_lifecycle_target(path, port, require_path=True)
    return start_runtime(cmd, root, port=port, background=background,
                         ready_timeout=ready_timeout, no_azurite=no_azurite)


def runtime_show(cmd, port=None):
    del cmd
    _, port = _local_lifecycle_target(None, port)
    return show_runtime(port=port)


def runtime_stop(cmd, port=None, all=False):
    del cmd
    if not all:
        _, port = _local_lifecycle_target(None, port)
    elif port is not None:
        validate_port(port)
    return stop_runtime(port=port, all_records=all)


def run_start(cmd, workflow, trigger, payload_file=None, resource_group_name=None, name=None, local=False, port=None, host_key=None, context=None):
    client, _ = _client_from_target(cmd, resource_group_name, name, local, port, host_key, context)
    body = _load_payload(payload_file) if payload_file else None
    response = client.post_with_headers(trigger_run_path(workflow, trigger), body=body)
    payload = response.get("payload") or {}
    props = _properties(payload)
    run_id = _header(response.get("headers"), "x-ms-workflow-run-id") or _field(payload, "name") or _field(props, "name") or _field(props, "runId")
    result = {"triggerName": trigger, "workflow": workflow, "runId": run_id, "status": _field(props, "status") or _field(payload, "status") or ("Accepted" if run_id else "AcceptedNewRunIdUnknown")}
    if not run_id:
        result["message"] = "Trigger run request was accepted, but the platform response did not identify the new run id."
    return result


def run_show(cmd, workflow, run_id, show_content_urls=False, resource_group_name=None, name=None, local=False, port=None, host_key=None, context=None):
    client, _ = _client_from_target(cmd, resource_group_name, name, local, port, host_key, context)
    payload = client.get(workflow_run_path(workflow, run_id))
    return _run_show_response(payload, workflow, run_id, show_content_urls)


def run_wait(cmd, workflow, run_id, timeout=300, interval=5, resource_group_name=None,
             name=None, local=False, port=None, host_key=None, context=None):
    _run_execution.validate_execution_options(workflow, run_id, timeout, interval)
    client, _ = _client_from_target(cmd, resource_group_name, name, local, port, host_key, context)
    report = _run_execution.wait_run(client, workflow, run_id, timeout, interval)
    return _run_execution.finish_execution_command(cmd, report)


def run_cancel(cmd, workflow, run_id, yes=False, wait=False, timeout=300, interval=5,
               resource_group_name=None, name=None, local=False, port=None, host_key=None, context=None):
    _run_execution.validate_execution_options(workflow, run_id, timeout, interval)
    client, _ = _client_from_target(cmd, resource_group_name, name, local, port, host_key, context)
    report = _run_execution.cancel_run(client, workflow, run_id, yes, wait, timeout, interval)
    return _run_execution.finish_execution_command(cmd, report)


def trigger_history_resubmit(cmd, workflow, trigger, history_name, yes=False, resource_group_name=None,
                             name=None, local=False, port=None, host_key=None, context=None):
    _run_execution.validate_history_options(workflow, trigger, history_name)
    client, _ = _client_from_target(cmd, resource_group_name, name, local, port, host_key, context)
    report = _run_execution.resubmit_trigger_history(client, workflow, trigger, history_name, yes)
    return _run_execution.finish_execution_command(cmd, report)


def run_resubmit(cmd, workflow, run_id, action, yes=False, resource_group_name=None,
                 name=None, local=False, port=None, host_key=None, context=None):
    _run_execution.validate_action_resubmit_options(workflow, run_id, action)
    client, _ = _client_from_target(cmd, resource_group_name, name, local, port, host_key, context)
    report = _run_execution.resubmit_run_action(client, workflow, run_id, action, yes)
    return _run_execution.finish_execution_command(cmd, report)


def run_list(cmd, workflow, status=None, max_items=None, next_token=None, resource_group_name=None, name=None, local=False, port=None, host_key=None, context=None):
    client, _ = _client_from_target(cmd, resource_group_name, name, local, port, host_key, context)
    params = {}
    if max_items is not None:
        params["$top"] = _positive_int(max_items, "--max-items")
    if status:
        params["$filter"] = "status eq '{}'".format(_run_status_value(status))
    if next_token:
        # This one is the service's own opaque $skiptoken, not the CLI's offset
        # envelope, so it is passed straight through rather than decoded.
        params["$skiptoken"] = next_token
    payload = client.get(workflow_runs_path(workflow), params=params or None)
    items = payload.get("value") if isinstance(payload, dict) else payload
    return {
        "value": [_run_list_item(item, workflow) for item in (items or [])],
        "nextContinuationToken": _skiptoken(payload),
    }


def run_action_list(cmd, workflow, run_id, show_content_urls=False, max_items=None, next_token=None, resource_group_name=None, name=None, local=False, port=None, host_key=None, context=None):
    client, _ = _client_from_target(cmd, resource_group_name, name, local, port, host_key, context)
    if max_items is not None:
        max_items = _positive_int(max_items, "--max-items")
    payload = client.list(run_actions_path(workflow, run_id), next_token=next_token, max_items=max_items)
    return {
        "value": [_run_action_response(item, workflow, run_id, show_content_urls) for item in (payload.get("value") or [])],
        "nextContinuationToken": payload.get("nextContinuationToken"),
    }


def run_action_show(cmd, workflow, run_id, action, show_content_urls=False, resource_group_name=None, name=None, local=False, port=None, host_key=None, context=None):
    client, _ = _client_from_target(cmd, resource_group_name, name, local, port, host_key, context)
    payload = client.get(run_action_path(workflow, run_id, action))
    return _run_action_response(payload, workflow, run_id, show_content_urls, action=action)


def run_action_show_content(cmd, workflow, run_id, action, content="outputs", max_bytes=None, resource_group_name=None, name=None, local=False, port=None, host_key=None, context=None):
    client, _ = _client_from_target(cmd, resource_group_name, name, local, port, host_key, context)
    # azure-cli hands back a str subclass for an unsupplied default, which
    # serializes as {"isDefault": true} rather than the value it stands for.
    content = str(content)
    payload = client.get(run_action_path(workflow, run_id, action))
    props = _properties(payload or {})
    link_key = "{}Link".format(content)
    link = _field(props, link_key)
    uri = link.get("uri") if isinstance(link, dict) else None
    if not uri:
        raise ValidationError(
            "Action '{action}' recorded no {content} content, so there is nothing to download. A failed "
            "action's error text and retry attempts are on the action itself: "
            "az logicapp run action show --workflow {workflow} --run-id {run_id} --action {action}".format(
                action=action, content=content, workflow=workflow, run_id=run_id))
    if max_bytes is not None:
        max_bytes = _positive_int(max_bytes, "--max-bytes")
    raw = client.get_raw_url(uri, max_bytes=max_bytes)
    body = raw.get("content") or b""
    if not isinstance(body, bytes):
        body = body.encode("utf-8")
    received = len(body)
    content_size = _field(link, "contentSize") if isinstance(link, dict) else None
    # The runtime does not always honour the Range header, so cap the payload here
    # rather than reporting a truncation that did not happen.
    truncated = isinstance(content_size, int) and received < content_size
    if max_bytes is not None and received > max_bytes:
        body = body[:max_bytes]
        truncated = True
    text = body.decode("utf-8", errors="replace")
    result = {
        "workflow": workflow,
        "runId": run_id,
        "action": action,
        "content": content,
        "contentSize": content_size,
        "truncated": truncated,
    }
    if truncated:
        result["body"] = text
        return result
    try:
        result["body"] = json.loads(text) if text else None
    except ValueError:
        result["body"] = text
    return result


def identity_assign(cmd, resource_group_name, name, system_assigned=False, user_assigned=None):
    current = get_identity(cmd, resource_group_name, name)
    return apply_identity(cmd, resource_group_name, name, plan_assign(current, system_assigned, user_assigned))


def identity_show(cmd, resource_group_name, name):
    return get_identity(cmd, resource_group_name, name)


def identity_remove(cmd, resource_group_name, name, system_assigned=False, user_assigned=None):
    current = get_identity(cmd, resource_group_name, name)
    return apply_identity(cmd, resource_group_name, name, plan_remove(current, system_assigned, user_assigned))


def _positive_int(value, flag):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise InvalidArgumentValueError("{} expects a positive integer. Received: {}".format(flag, value))
    if parsed <= 0:
        raise InvalidArgumentValueError("{} expects a positive integer. Received: {}".format(flag, value))
    return parsed


def _run_status_value(status):
    known = ["Succeeded", "Failed", "Running", "Cancelled", "Waiting", "Skipped", "Suspended", "TimedOut", "Aborted", "Faulted"]
    for candidate in known:
        if candidate.lower() == str(status).strip().lower():
            return candidate
    raise InvalidArgumentValueError(
        "--status expects one of: {}. Received: {}".format(", ".join(known), status))


def _skiptoken(payload):
    """Return the platform's own continuation token for the next page of runs.

    Runs page server-side: the platform hands back a ``nextLink`` carrying a
    ``$skiptoken``. Re-deriving a token client-side would silently skip runs
    that were created between pages.
    """
    if not isinstance(payload, dict):
        return None
    next_link = payload.get("nextLink")
    if not next_link:
        return None
    from urllib.parse import parse_qs, urlparse
    tokens = parse_qs(urlparse(next_link).query).get("$skiptoken")
    return tokens[0] if tokens else None


def _run_list_item(raw, workflow):
    props = _properties(raw or {})
    return {
        "runId": _field(raw, "name") or _field(props, "name") or _field(props, "runId"),
        "workflow": workflow,
        "workflowVersion": _workflow_version(props),
        "status": _field(props, "status"),
        "code": _field(props, "code"),
        "error": _field(props, "error"),
        "startTime": _field(props, "startTime"),
        "endTime": _field(props, "endTime"),
        "triggerName": _trigger_name(props),
    }


def _trigger_name(props):
    trigger = _field(props, "trigger")
    if isinstance(trigger, dict):
        return _field(trigger, "name")
    return None


def _run_action_response(raw, workflow, run_id, show_content_urls, action=None):
    props = _properties(raw or {})
    containers = [value for key, value in (raw or {}).items()
                  if str(key).casefold() == "properties"] if isinstance(raw, dict) else []
    source = containers[0] if len(containers) == 1 else (props if not containers else {})
    eligibility = [value for key, value in source.items()
                   if str(key).casefold() == "canresubmit"] if isinstance(source, dict) else []
    can_resubmit = eligibility[0] if len(eligibility) == 1 and isinstance(eligibility[0], bool) else None
    return {
        "action": _field(raw, "name") or _field(props, "name") or action,
        "workflow": workflow,
        "runId": run_id,
        "status": _field(props, "status"),
        "code": _field(props, "code"),
        "error": _field(props, "error"),
        "startTime": _field(props, "startTime"),
        "endTime": _field(props, "endTime"),
        "trackingId": _field(props, "trackingId"),
        "correlation": _field(props, "correlation"),
        "canResubmit": can_resubmit,
        "retryHistory": _redact(_field(props, "retryHistory"), show_content_urls),
        "inputsLink": _redact({"inputsLink": _field(props, "inputsLink")}, show_content_urls).get("inputsLink"),
        "outputsLink": _redact({"outputsLink": _field(props, "outputsLink")}, show_content_urls).get("outputsLink"),
    }


def _project_path_from_context(path, context, allow_cloud=False):
    ctx = None
    if context is not None or not path:
        ctx, _ = get_context(context)
    target = ctx.get("target", {}) if ctx else None
    if target and target.get("kind") != "local":
        if allow_cloud and path:
            return abs_path(path)
        raise MutuallyExclusiveArgumentError(
            "A cloud context cannot select a local project. Use a local context or explicit --path. "
            "With cloud runtime validation, pass --path and --with-runtime together.")
    return abs_path(path or (target.get("path") if target else None) or os.curdir)


def _local_lifecycle_target(path, port, require_path=False):
    ctx, _ = get_context(None) if path is None and (port is None or require_path) else (None, None)
    target = ctx.get("target", {}) if ctx else None
    if target and target.get("kind") != "local":
        raise MutuallyExclusiveArgumentError(
            "Runtime lifecycle commands require a local target. Select a local context "
            "or pass explicit --path/--port.")
    root = abs_path(path or (target.get("path") if target else None) or os.curdir)
    return root, validate_port(port if port is not None else target.get("port") if target else None)


def _active_context_path():
    ctx, _ = get_context(None)
    if ctx and ctx.get("target", {}).get("kind") == "local":
        return ctx["target"].get("path")
    return None


def _client_from_target(cmd, resource_group_name=None, name=None, local=False, port=None, host_key=None, context=None):
    explicit_cloud = resource_group_name is not None or name is not None
    explicit_local = bool(local)
    if context is not None:
        if explicit_cloud or explicit_local:
            raise MutuallyExclusiveArgumentError("--context cannot be combined with explicit target flags.")
        if port is not None:
            raise MutuallyExclusiveArgumentError("--port cannot be combined with --context; use the saved port.")
        ctx, _ = get_context(context)
        return _client_from_context(cmd, ctx, host_key=host_key), ctx.get("target")
    if explicit_cloud or explicit_local:
        return build_runtime_client(cmd, resource_group_name, name, local=local, port=port, host_key=host_key), {"kind": "local" if local else "cloud"}
    if port is not None:
        raise RequiredArgumentMissingError("--port requires --local; contexts use their saved port.")
    ctx, _ = get_context(None)
    if not ctx:
        raise RequiredArgumentMissingError("A target is required. Use --local, --resource-group/--name, or --context.")
    return _client_from_context(cmd, ctx, host_key=host_key), ctx.get("target")


def _client_from_context(cmd, context, host_key=None):
    target = context.get("target", {})
    if target.get("kind") == "local":
        return build_runtime_client(cmd, local=True, port=target.get("port"), host_key=host_key)
    return build_runtime_client(cmd, resource_group_name=target.get("resourceGroup"),
                                name=target.get("logicAppName"), host_key=host_key)


def _discover_for_runtime(root, all_workflows):
    from ._workflow import discover_workflows
    return discover_workflows(root, all_workflows=all_workflows)


def _runtime_validate_body(workflow_path, workflow_name, root):
    from ._json import strict_json_loads

    path = workflow_path or os.path.join(root, workflow_name, "workflow.json")
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = strict_json_loads(handle.read())
    except (ValueError, UnicodeError, RecursionError):
        raise ClientRequestError(
            "The authored workflow is not valid JSON. No runtime validation request was attempted.") from None
    except OSError:
        raise ClientRequestError(
            "The authored workflow could not be read. No runtime validation request was attempted.") from None
    if isinstance(payload, dict) and "properties" in payload:
        return payload
    properties = {}
    if isinstance(payload, dict):
        if "definition" in payload:
            properties["definition"] = payload["definition"]
            if payload.get("kind"):
                properties["kind"] = payload["kind"]
        else:
            properties["definition"] = payload
    else:
        properties["definition"] = payload
    return {"properties": properties}


def _load_payload(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except ValueError as ex:
        raise ValidationError("payload-file must contain valid JSON") from ex
    except OSError as ex:
        raise ValidationError("payload-file could not be read: {}".format(ex)) from ex


def _recount(report):
    report["summary"]["errors"] = len([item for item in report["findings"] if item["severity"] == "error"])
    report["summary"]["warnings"] = len([item for item in report["findings"] if item["severity"] == "warning"])
    report["valid"] = report["summary"]["errors"] == 0


def _run_show_response(raw, workflow, run_id, show_content_urls):
    props = _properties(raw or {})
    result = {
        "runId": _field(raw, "name") or _field(props, "name") or _field(props, "runId") or run_id,
        "workflow": workflow,
        "workflowVersion": _workflow_version(props),
        "status": _field(props, "status") or _field(raw, "status"),
        "code": _field(props, "code") or _field(raw, "code"),
        "error": _field(props, "error") or _field(raw, "error"),
        "startTime": _field(props, "startTime"),
        "endTime": _field(props, "endTime"),
        "waitEndTime": _field(props, "waitEndTime"),
        "correlation": _field(props, "correlation"),
        "correlationId": _field(props, "correlationId"),
        "trigger": _redact(_field(props, "trigger"), show_content_urls),
        "outputs": _redact(_field(props, "outputs"), show_content_urls),
        "previousRunId": _field(props, "previousRunId") or _field(props, "sourceTriggerHistoryName"),
    }
    return result


def _workflow_version(props):
    workflow = _field(props, "workflow")
    if isinstance(workflow, dict):
        return _field(workflow, "name") or _version_from_id(_field(workflow, "id"))
    return None


def _version_from_id(value):
    if isinstance(value, str) and "/versions/" in value.lower():
        return value.rstrip("/").split("/")[-1]
    return None


def _redact(value, show_content_urls):
    if show_content_urls or value is None:
        return value
    if isinstance(value, dict):
        result = {}
        for key, inner in value.items():
            if str(key).lower().endswith("link") and isinstance(inner, dict) and "uri" in inner:
                replacement = dict(inner)
                replacement["uri"] = LOGICAPP_REDACTION_SENTINEL
                result[key] = replacement
            else:
                result[key] = _redact(inner, show_content_urls)
        return result
    if isinstance(value, list):
        return [_redact(item, show_content_urls) for item in value]
    return value


def _properties(raw):
    if not isinstance(raw, dict):
        return {}
    return raw.get("properties") if isinstance(raw.get("properties"), dict) else raw


def _field(source, name, default=None):
    if not isinstance(source, dict):
        return default
    if name in source:
        return source[name]
    lowered = name.lower()
    for key, value in source.items():
        if str(key).lower() == lowered:
            return value
    return default


def _value(payload):
    if payload is None:
        return []
    if isinstance(payload, list):
        return payload
    return payload.get("value", []) if isinstance(payload, dict) else []


def _header(headers, name):
    if not headers:
        return None
    lowered = name.lower()
    for key, value in dict(headers).items():
        if str(key).lower() == lowered:
            if isinstance(value, (list, tuple)):
                return str(value[0]) if value else None
            return str(value)
    return None


def store_show_path():
    return store_path()


def _workflow_kind_value(value):
    if type(value) is str:  # pylint: disable=unidiomatic-typecheck
        return value or "Stateful"
    return "Stateful"
