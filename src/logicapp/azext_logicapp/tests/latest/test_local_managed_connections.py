# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Offline local managed-connection scope, auth, file and failure contracts."""

import copy
import json
import os
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import subprocess
import unittest
from unittest import mock
from urllib.parse import urlunsplit

from azure.cli.core.azclierror import CLIError, CLIInternalError, ResourceNotFoundError

from azext_logicapp import _connection, _local_managed_connection as local, _managed_connection as managed, _workflow, custom

SUBSCRIPTION = "11111111-1111-1111-1111-111111111111"
OVERRIDE = "22222222-2222-2222-2222-222222222222"
KEY = "private-development-key-never-in-output"
CONNECTION_ID = "/subscriptions/{}/resourceGroups/rg/providers/Microsoft.Web/connections/conn".format(SUBSCRIPTION)
CONNECTOR_ID = "/subscriptions/{}/providers/Microsoft.Web/locations/eastus/managedApis/office365".format(SUBSCRIPTION)


class LocalManagedConnections(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.write("host.json", {"version": "2.0"})
        self.settings = {"IsEncrypted": False, "Values": {
            "WORKFLOWS_SUBSCRIPTION_ID": SUBSCRIPTION,
            "WORKFLOWS_RESOURCE_GROUP_NAME": "rg", "WORKFLOWS_LOCATION_NAME": "eastus",
            "KEEP_PRIVATE": "existing-secret",
        }}
        self.write("local.settings.json", self.settings)
        self.cmd = SimpleNamespace(cli_ctx=SimpleNamespace(data={}))
        self.profile = mock.Mock()
        self.profile.get_subscription.side_effect = lambda subscription: {"id": subscription, "tenantId": "tenant"}
        patches = [
            mock.patch.object(local, "Profile", return_value=self.profile),
            mock.patch.object(local, "is_tracked_by_git", return_value=False),
            mock.patch.object(managed, "_resolve_app_principal", side_effect=AssertionError("No deployed app")),
            mock.patch.object(managed, "_ConnectionsFile", side_effect=AssertionError("No remote VFS")),
        ]
        for patcher in patches:
            patcher.start()
            self.addCleanup(patcher.stop)
        self.resource = None
        self.calls = []
        self.on_put = None

    def write(self, filename, payload):
        (self.root / filename).write_text(json.dumps(payload), encoding="utf-8")

    def arm(self, _cmd, method, resource_id, body=None, sender=None):
        del sender
        self.calls.append((method, resource_id, copy.deepcopy(body)))
        self.assertNotIn("/sites/", resource_id)
        self.assertNotIn("/accessPolicies", resource_id)
        if resource_id.endswith("/listConnectionKeys"):
            self.assertEqual("POST", method)
            self.assertEqual({"validityTimeSpan": "7"}, body)
            return {"connectionKey": KEY}
        if method == "GET":
            if self.resource is None:
                raise ResourceNotFoundError("Not found")
            return copy.deepcopy(self.resource)
        if method == "PUT":
            self.resource = dict(copy.deepcopy(body), id=resource_id, name="conn", type="Microsoft.Web/connections")
            self.resource["properties"].update({"connectionRuntimeUrl": "https://connector.invalid/runtime",
                                               "overallStatus": "Connected", "statuses": [{"status": "Connected"}]})
            if self.on_put:
                self.on_put()
            return copy.deepcopy(self.resource)
        raise AssertionError((method, resource_id))

    def create(self, **kwargs):
        options = dict(cmd=self.cmd, resource_group_name=None, name=None, connection_name="conn",
                       connector="office365", location=None, auth_mode="raw", local_project=str(self.root))
        options.update(kwargs)
        with mock.patch.object(managed, "_arm", side_effect=self.arm):
            return managed.create_managed_connection(**options)

    def test_local_creation_uses_project_scope_and_stores_only_a_key_reference_in_connections(self):
        self.write("connections.json", {"serviceProviderConnections": {"keep": {"value": 1}},
                                       "managedApiConnections": {"other": {"value": 2}}})
        result = self.create(parameter=[["endpoint=example"]])
        self.assertEqual(CONNECTION_ID, result["connection"]["id"])
        self.assertIsNone(result["accessPolicy"])
        self.assertEqual("conn-connectionKey", result["developmentKey"]["appSetting"])
        self.assertNotIn(KEY, json.dumps(result))
        self.profile.get_subscription.assert_called_once_with(subscription=SUBSCRIPTION)
        document = json.loads((self.root / "connections.json").read_text(encoding="utf-8"))
        entry = document["managedApiConnections"]["conn"]
        self.assertEqual(CONNECTOR_ID, entry["api"]["id"])
        self.assertEqual({"type": "Raw", "scheme": "Key", "parameter": "@appsetting('conn-connectionKey')"},
                         entry["authentication"])
        self.assertNotIn(KEY, json.dumps(document))
        self.assertEqual({"value": 1}, document["serviceProviderConnections"]["keep"])
        self.assertEqual({"value": 2}, document["managedApiConnections"]["other"])
        settings = json.loads((self.root / "local.settings.json").read_text(encoding="utf-8"))
        self.assertEqual(KEY, settings["Values"].pop("conn-connectionKey"))
        self.assertEqual(self.settings, settings)
        self.assertIn("local.settings.json", (self.root / ".gitignore").read_text(encoding="utf-8"))
        self.assertEqual(["GET", "PUT", "GET", "POST"], [row[0] for row in self.calls])

    def test_command_overrides_scope_without_changing_project_settings_or_global_account(self):
        self.cmd.cli_ctx.data["subscription_id"] = OVERRIDE
        result = self.create(resource_group_name="override-rg", location="westus")
        self.assertIn("/subscriptions/" + OVERRIDE + "/resourceGroups/override-rg/", result["connection"]["id"])
        self.assertIn("/locations/westus/", result["api"]["id"])
        self.assertEqual({"subscription_id": OVERRIDE}, self.cmd.cli_ctx.data)
        saved = json.loads((self.root / "local.settings.json").read_text(encoding="utf-8"))
        self.assertEqual(SUBSCRIPTION, saved["Values"]["WORKFLOWS_SUBSCRIPTION_ID"])
        self.assertEqual("rg", saved["Values"]["WORKFLOWS_RESOURCE_GROUP_NAME"])

    def test_missing_invalid_encrypted_and_nonliteral_settings_fail_before_arm(self):
        cases = []
        for key in local.SCOPE_SETTINGS.values():
            missing = copy.deepcopy(self.settings)
            del missing["Values"][key]
            cases.append(missing)
            for invalid in ("", "  value", "@appsetting('scope')", {}, True):
                changed = copy.deepcopy(self.settings)
                changed["Values"][key] = invalid
                cases.append(changed)
        cases += [{"IsEncrypted": True, "Values": self.settings["Values"]},
                  {"Values": self.settings["Values"]}, {"IsEncrypted": False, "Values": []}]
        for settings in cases:
            with self.subTest(settings=settings):
                self.write("local.settings.json", settings)
                before = (self.root / "local.settings.json").read_bytes()
                with self.assertRaises(CLIError):
                    self.create()
                self.assertEqual(before, (self.root / "local.settings.json").read_bytes())
                self.assertEqual([], self.calls)

    def test_duplicate_invalid_json_and_shape_are_preserved_before_arm(self):
        cases = [
            ("local.settings.json", b'{"IsEncrypted":false,"Values":{},"Values":{}}'),
            ("connections.json", b'{"managedApiConnections":[]}'),
            ("connections.json", b'{"managedApiConnections":{},"x":NaN}'),
            ("connections.json", b'not-json'),
            (".gitignore", b"\xff"),
        ]
        for filename, content in cases:
            with self.subTest(filename=filename, content=content):
                self.write("local.settings.json", self.settings)
                (self.root / filename).write_bytes(content)
                with self.assertRaises(CLIError):
                    self.create()
                self.assertEqual(content, (self.root / filename).read_bytes())
                self.assertEqual([], self.calls)
                if filename != "local.settings.json":
                    (self.root / filename).unlink()

    def test_authentication_unsupported_locally_fails_without_azure_or_file_changes(self):
        for options in ({"auth_mode": "managed-identity"},
                        {"user_assigned_identity": "/subscriptions/identity"}):
            with self.subTest(options=options), self.assertRaises(CLIError):
                self.create(**options)
        self.assertEqual([], self.calls)
        self.assertFalse((self.root / "connections.json").exists())

    def test_missing_settings_does_not_fall_back_to_current_subscription(self):
        del self.settings["Values"]["WORKFLOWS_SUBSCRIPTION_ID"]
        self.write("local.settings.json", self.settings)
        with self.assertRaisesRegex(CLIError, "WORKFLOWS_SUBSCRIPTION_ID"):
            self.create()
        self.profile.get_subscription.assert_not_called()
        self.assertEqual([], self.calls)

    def test_missing_project_files_fail_before_arm(self):
        for filename in ("host.json", "local.settings.json"):
            with self.subTest(filename=filename):
                path = self.root / filename
                original = path.read_bytes()
                path.unlink()
                try:
                    with self.assertRaises(CLIError):
                        self.create()
                    self.assertEqual([], self.calls)
                finally:
                    path.write_bytes(original)

    def test_project_subscription_must_be_signed_in_and_match(self):
        self.profile.get_subscription.side_effect = CLIError("Sign in to the selected subscription.")
        with self.assertRaisesRegex(CLIError, "Sign in"):
            self.create()
        self.profile.get_subscription.side_effect = None
        self.profile.get_subscription.return_value = {"id": OVERRIDE}
        with self.assertRaisesRegex(CLIError, "does not match"):
            self.create()
        self.assertEqual([], self.calls)
        self.assertEqual(self.settings, json.loads((self.root / "local.settings.json").read_text(encoding="utf-8")))

    def test_explicit_scope_can_supply_all_missing_scope_settings(self):
        self.write("local.settings.json", {"IsEncrypted": False, "Values": {}})
        self.cmd.cli_ctx.data["subscription_id"] = OVERRIDE
        self.create(resource_group_name="rg", location="eastus")

    def test_connector_id_cannot_override_selected_subscription_or_location(self):
        for connector in (CONNECTOR_ID.replace(SUBSCRIPTION, OVERRIDE),
                          CONNECTOR_ID.replace("eastus", "westus"),
                          CONNECTOR_ID + "/nested", CONNECTOR_ID + "#fragment",
                          CONNECTOR_ID + "?private=query"):
            with self.subTest(connector=connector), self.assertRaises(CLIError):
                self.create(connector=connector)
        self.assertEqual([], self.calls)

    def test_existing_local_entry_or_key_requires_force_before_arm(self):
        for filename, payload in (
                ("connections.json", {"managedApiConnections": {"conn": {}}}),
                ("local.settings.json", {"IsEncrypted": False, "Values":
                                        dict(self.settings["Values"], **{"conn-connectionKey": "old"})})):
            with self.subTest(filename=filename):
                self.write(filename, payload)
                with self.assertRaisesRegex(CLIError, "--force"):
                    self.create()
                self.assertEqual([], self.calls)
                if filename == "connections.json":
                    (self.root / filename).unlink()
        self.create(force=True)
        self.assertTrue((self.root / "connections.json").is_file())

    def test_existing_azure_connection_is_not_overwritten_without_force(self):
        self.resource = {"id": CONNECTION_ID}
        with self.assertRaisesRegex(CLIError, "already exists"):
            self.create()
        self.assertEqual(["GET"], [row[0] for row in self.calls])
        self.assertFalse((self.root / "connections.json").exists())

    def test_oauth_consent_uses_selected_subscription_and_has_no_app_acl(self):
        def consent(*_args, **_kwargs):
            return {"status": "Connected"}

        with mock.patch.object(managed, "_resolve_consent_principal",
                               return_value={"objectId": "caller", "tenantId": "tenant"}) as caller:
            result = self.create(auth_mode="oauth", consent_runner=consent)
        caller.assert_called_once_with(self.cmd, subscription=SUBSCRIPTION)
        self.assertEqual("Connected", result["consent"]["status"])

    def test_caller_token_is_acquired_for_the_project_subscription(self):
        with mock.patch("azure.cli.core._profile.Profile") as profile, \
                mock.patch.object(managed, "_jwt_claims", return_value={"oid": "caller", "tid": "tenant"}):
            profile.return_value.get_raw_token.return_value = (("Bearer", "token", {}), SUBSCRIPTION, "tenant")
            self.assertEqual({"objectId": "caller", "tenantId": "tenant"},
                             managed._resolve_consent_principal(self.cmd, subscription=SUBSCRIPTION))
            profile.return_value.get_raw_token.assert_called_once_with(subscription=SUBSCRIPTION)

    def test_interleaved_local_change_is_retained_and_azure_resource_is_not_deleted(self):
        changed = b'{"external":"writer"}'
        self.on_put = lambda: (self.root / "connections.json").write_bytes(changed)
        before_settings = (self.root / "local.settings.json").read_bytes()
        with self.assertRaisesRegex(CLIInternalError, "No ARM resources were deleted"):
            self.create()
        self.assertEqual(changed, (self.root / "connections.json").read_bytes())
        self.assertEqual(before_settings, (self.root / "local.settings.json").read_bytes())
        self.assertIsNotNone(self.resource)
        self.assertFalse(any(row[0] == "DELETE" for row in self.calls))

    def test_bad_key_response_does_not_write_files_or_expose_response(self):
        send = self.arm
        for response in ({}, [], {"connectionKey": ""}, {"connectionKey": 42}):
            with self.subTest(response=response):
                def bad_key(cmd, method, resource_id, body=None, sender=None):
                    if resource_id.endswith("/listConnectionKeys"):
                        return response
                    return send(cmd, method, resource_id, body, sender)

                self.resource = None
                with mock.patch.object(managed, "_arm", side_effect=bad_key):
                    with self.assertRaises(CLIInternalError) as caught:
                        managed.create_managed_connection(
                            self.cmd, None, None, "conn", "office365", None, "raw",
                            local_project=str(self.root))
                self.assertNotIn(KEY, str(caught.exception))
                self.assertFalse((self.root / "connections.json").exists())
                self.assertNotIn(KEY, (self.root / "local.settings.json").read_text(encoding="utf-8"))

    def test_invalid_runtime_url_does_not_request_a_key_or_publish_wiring(self):
        send = self.arm
        credential_url = urlunsplit(("https", "user:secret@connector.invalid", "", "", ""))
        for url in (None, "https://", "http://connector.invalid", credential_url,
                    "https://connector.invalid/#fragment", "https://connector.invalid/\n"):
            with self.subTest(url=url):
                self.resource = None
                self.calls = []

                def invalid_url(cmd, method, resource_id, body=None, sender=None):
                    response = send(cmd, method, resource_id, body, sender)
                    response.setdefault("properties", {})["connectionRuntimeUrl"] = url
                    return response

                with mock.patch.object(managed, "_arm", side_effect=invalid_url):
                    with self.assertRaises(CLIInternalError):
                        managed.create_managed_connection(
                            self.cmd, None, None, "conn", "office365", None, "raw",
                            local_project=str(self.root))
                self.assertFalse(any(row[0] == "POST" for row in self.calls))
                self.assertFalse((self.root / "connections.json").exists())

    def test_partial_publication_is_reported_without_unsafe_file_rollback(self):
        replace = os.replace

        def fail_last(source, destination):
            if str(destination).endswith("connections.json"):
                raise PermissionError("locked")
            return replace(source, destination)

        with mock.patch.object(local.os, "replace", side_effect=fail_last):
            with self.assertRaisesRegex(CLIInternalError, "partially updated"):
                self.create()
        saved = json.loads((self.root / "local.settings.json").read_text(encoding="utf-8"))
        self.assertEqual(KEY, saved["Values"]["conn-connectionKey"])
        self.assertFalse((self.root / "connections.json").exists())
        self.assertEqual([], list((self.root / ".azurelogicapps").glob(".managed-connection-*")))

    def test_gitignore_reinforces_last_rule_and_preserves_unrelated_content(self):
        for ignore in ("# existing\nlocal.settings.json\n!local.settings.json\nother.txt\n",
                       " local.settings.json\n", "\tlocal.settings.json\n"):
            with self.subTest(ignore=ignore):
                (self.root / ".gitignore").write_text(ignore, encoding="utf-8")
                self.create(force=True)
                actual = (self.root / ".gitignore").read_text(encoding="utf-8")
                self.assertTrue(actual.startswith(ignore))
                self.assertEqual("local.settings.json", actual.splitlines()[-1])

    def test_actual_git_ignores_the_saved_key_file(self):
        import shutil

        git = shutil.which("git")
        if not git:
            self.skipTest("Git is not installed on this host.")
        subprocess.run([git, "init", "--quiet", str(self.root)], check=True, capture_output=True)
        for ignore in ("local.settings.json\n!local.settings.json\n",
                       " local.settings.json\n", "\tlocal.settings.json\n"):
            with self.subTest(ignore=ignore):
                (self.root / ".gitignore").write_text(ignore, encoding="utf-8")
                self.create(force=True)
                result = subprocess.run([git, "-C", str(self.root), "check-ignore", "local.settings.json"],
                                        capture_output=True, text=True, check=False)
                self.assertEqual(0, result.returncode, result.stderr)

    def test_git_tracking_exit_codes_distinguish_absence_from_failure(self):
        for code, expected in ((0, True), (1, False), (128, None), (129, None), (-9, None)):
            with self.subTest(code=code), \
                    mock.patch.object(_connection.shutil, "which", return_value="git"), \
                    mock.patch.object(_connection.subprocess, "run",
                                      return_value=SimpleNamespace(returncode=code)):
                self.assertIs(expected, _connection.is_tracked_by_git(str(self.root), "local.settings.json"))
        with mock.patch.object(_connection.shutil, "which", return_value="git"), \
                mock.patch.object(_connection.subprocess, "run", side_effect=OSError("unavailable")):
            self.assertIsNone(_connection.is_tracked_by_git(str(self.root), "local.settings.json"))
        with mock.patch.object(_connection.shutil, "which", return_value=None):
            self.assertIsNone(_connection.is_tracked_by_git(str(self.root), "local.settings.json"))

    def test_secret_staging_is_ignored_before_writing_and_after_cleanup_failure(self):
        import shutil

        git = shutil.which("git")
        if not git:
            self.skipTest("Git is not installed on this host.")
        subprocess.run([git, "init", "--quiet", str(self.root)], check=True, capture_output=True)
        (self.root / ".gitignore").write_text(
            "/.azurelogicapps/\nlocal.settings.json\n!/.azurelogicapps/\n!local.settings.json\n",
            encoding="utf-8")
        stage = tempfile.mkstemp
        unlink = os.unlink
        replace = os.replace
        staged_secret_paths = []

        def observe_stage(*args, **kwargs):
            handle, path = stage(*args, **kwargs)
            if (self.root / ".gitignore").read_text(encoding="utf-8").splitlines()[-1] == "local.settings.json":
                ignored = subprocess.run([git, "-C", str(self.root), "check-ignore", path],
                                         capture_output=True, check=False)
                self.assertEqual(0, ignored.returncode)
                staged_secret_paths.append(path)
            return handle, path

        def fail_secret_publication(source, destination):
            if str(destination).endswith("local.settings.json"):
                raise PermissionError("locked")
            return replace(source, destination)

        def retain_secret_stage(path, *args, **kwargs):
            if path in staged_secret_paths:
                raise PermissionError("locked")
            return unlink(path, *args, **kwargs)

        try:
            with mock.patch.object(local.tempfile, "mkstemp", side_effect=observe_stage), \
                    mock.patch.object(local.os, "replace", side_effect=fail_secret_publication), \
                    mock.patch.object(local.os, "unlink", side_effect=retain_secret_stage):
                with self.assertRaises(CLIInternalError):
                    self.create()
            self.assertEqual(2, len(staged_secret_paths))
            self.assertTrue(any(KEY.encode() in Path(path).read_bytes() for path in staged_secret_paths))
            subprocess.run([git, "-C", str(self.root), "add", "."], check=True, capture_output=True)
            tracked = subprocess.run([git, "-C", str(self.root), "ls-files"], check=True,
                                     capture_output=True, text=True).stdout.splitlines()
            self.assertNotIn("local.settings.json", tracked)
            self.assertFalse(any(path.startswith(".azurelogicapps/") for path in tracked))
        finally:
            for path in staged_secret_paths:
                if os.path.exists(path):
                    unlink(path)

    def test_nonregular_files_are_rejected_before_open_without_arm(self):
        lstat = os.lstat
        open_file = os.open
        for filename in ("host.json", "local.settings.json", "connections.json", ".gitignore"):
            with self.subTest(filename=filename):
                target = str(self.root / filename)

                def file_type(path):
                    if os.fspath(path) == target:
                        return SimpleNamespace(st_mode=stat.S_IFIFO, st_nlink=1, st_file_attributes=0)
                    return lstat(path)

                def never_open_fifo(path, *args, **kwargs):
                    self.assertNotEqual(target, os.fspath(path))
                    return open_file(path, *args, **kwargs)

                with mock.patch.object(local.os, "lstat", side_effect=file_type), \
                        mock.patch.object(local.os, "open", side_effect=never_open_fifo):
                    with self.assertRaisesRegex(CLIError, "regular"):
                        self.create()
                self.assertEqual([], self.calls)

    def test_ignore_publication_failure_prevents_secret_staging(self):
        replace = os.replace
        staged_payloads = []
        stage = tempfile.mkstemp

        def observe_stage(*args, **kwargs):
            handle, path = stage(*args, **kwargs)
            staged_payloads.append(path)
            return handle, path

        def refuse_ignore(source, destination):
            if str(destination).endswith(".gitignore"):
                self.assertNotIn(KEY.encode(), Path(source).read_bytes())
                raise PermissionError("locked")
            return replace(source, destination)

        with mock.patch.object(local.tempfile, "mkstemp", side_effect=observe_stage), \
                mock.patch.object(local.os, "replace", side_effect=refuse_ignore):
            with self.assertRaises(CLIInternalError):
                self.create()
        self.assertEqual(1, len(staged_payloads))
        self.assertFalse((self.root / "connections.json").exists())
        self.assertEqual(self.settings, json.loads((self.root / "local.settings.json").read_text(encoding="utf-8")))
        self.assertFalse(any(Path(path).exists() for path in staged_payloads))

    @unittest.skipUnless(hasattr(os, "mkfifo"), "This host does not support FIFO files.")
    def test_actual_fifo_is_rejected_without_opening_or_waiting_for_a_writer(self):
        target = self.root / "connections.json"
        os.mkfifo(target)
        with mock.patch.object(local.os, "open", side_effect=AssertionError("FIFO must not be opened")):
            with self.assertRaisesRegex(CLIError, "regular"):
                local._snapshot(str(target))

    @unittest.skipUnless(hasattr(os, "mkfifo") and hasattr(os, "O_NONBLOCK"),
                         "This host does not support nonblocking FIFO files.")
    def test_fifo_replacement_between_lstat_and_open_is_nonblocking_and_refused(self):
        target = self.root / "connections.json"
        target.write_text("{}", encoding="utf-8")
        open_file = os.open

        def replace_with_fifo(path, flags):
            self.assertTrue(flags & os.O_NONBLOCK)
            target.unlink()
            os.mkfifo(target)
            return open_file(path, flags)

        with mock.patch.object(local.os, "open", side_effect=replace_with_fifo):
            with self.assertRaisesRegex(CLIError, "regular"):
                local._snapshot(str(target))

    def test_packaging_does_not_export_local_key_or_private_state(self):
        self.create()
        result = _workflow.deterministic_package(
            str(self.root), str(self.root / "app.zip"), str(self.root / "manifest.json"))
        self.assertIn({"path": "local.settings.json", "reason": "secret"}, result["excluded"])
        self.assertFalse(any(row["path"].startswith(".azurelogicapps/") for row in result["included"]))
        import zipfile

        with zipfile.ZipFile(result["archivePath"]) as archive:
            self.assertIn("connections.json", archive.namelist())
            for filename in archive.namelist():
                self.assertNotIn(KEY.encode(), archive.read(filename))
        self.assertNotIn(KEY, (self.root / "manifest.json").read_text(encoding="utf-8"))

    def test_preflight_aliases_and_private_state_file_are_refused_before_arm(self):
        for filename in ("connections.json", "local.settings.json"):
            with self.subTest(filename=filename):
                target = self.root / filename
                original = target.read_bytes() if target.exists() else None
                other = self.root / "aliased.json"
                other.write_text("{}", encoding="utf-8")
                if target.exists():
                    target.unlink()
                try:
                    os.link(other, target)
                    with self.assertRaisesRegex(CLIError, "unaliased"):
                        self.create()
                    self.assertEqual(b"{}", other.read_bytes())
                    self.assertEqual([], self.calls)
                finally:
                    if target.exists():
                        target.unlink()
                    other.unlink()
                    if original is not None:
                        target.write_bytes(original)
        (self.root / ".azurelogicapps").write_text("not-a-directory", encoding="utf-8")
        with self.assertRaises(CLIError):
            self.create()
        self.assertEqual([], self.calls)

    def test_linked_connection_file_is_refused_without_touching_its_destination(self):
        other = self.root / "external.json"
        other.write_text("{}", encoding="utf-8")
        link = self.root / "connections.json"
        try:
            link.symlink_to(other)
        except OSError:
            self.skipTest("This host does not permit unprivileged symlinks.")
        with self.assertRaises(CLIError):
            self.create()
        self.assertEqual(b"{}", other.read_bytes())
        self.assertEqual([], self.calls)

    def test_changed_files_before_arm_put_do_not_authorize_mutation(self):
        before = self.arm

        def changed(cmd, method, resource_id, body=None, sender=None):
            if method == "GET":
                self.write("local.settings.json", {"external": "writer"})
            return before(cmd, method, resource_id, body, sender)

        with mock.patch.object(managed, "_arm", side_effect=changed):
            with self.assertRaises(CLIInternalError):
                managed.create_managed_connection(
                    self.cmd, None, None, "conn", "office365", None, "raw", local_project=str(self.root))
        self.assertEqual(["GET"], [row[0] for row in self.calls])

    def test_unknown_git_status_is_explicit_in_result(self):
        with mock.patch.object(local, "is_tracked_by_git", return_value=None):
            result = self.create()
        self.assertIsNone(result["protection"]["trackedByGit"])

    def test_tracked_settings_are_refused_before_creating_credentials(self):
        with mock.patch.object(local, "is_tracked_by_git", return_value=True):
            with self.assertRaisesRegex(CLIError, "tracked by Git"):
                self.create()
        self.assertEqual([], self.calls)

    def test_local_target_resolution_and_explicit_deployed_compatibility(self):
        target = {"target": {"kind": "local", "path": str(self.root)}}
        with mock.patch.object(custom, "get_context", return_value=(target, {})), \
                mock.patch.object(custom, "_connection_create_managed", return_value={}) as create:
            custom.connection_managed_create(self.cmd, "conn", "office365", "oauth", context="dev")
            self.assertEqual(str(self.root), create.call_args.kwargs["local_project"])
            custom.connection_managed_create(self.cmd, "conn", "office365", "oauth")
            self.assertEqual(str(self.root), create.call_args.kwargs["local_project"])
            custom.connection_managed_create(self.cmd, "conn", "office365", "oauth",
                                            logic_app_name="app", resource_group_name="rg", location="eastus")
            self.assertIsNone(create.call_args.kwargs["local_project"])
            self.assertEqual("app", create.call_args.args[1])
