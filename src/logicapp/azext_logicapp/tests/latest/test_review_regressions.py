# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import html
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import threading
import time
import unittest
from unittest import mock
from urllib.parse import urlencode
from urllib.request import urlopen
import zipfile

from azure.cli.core.azclierror import FileOperationError, ValidationError

from azext_logicapp import _managed_api, _oauth_consent, _test_scaffold, _workflow


class ConsentReviewTests(unittest.TestCase):
    def assert_accepted(self, listener):
        deadline = time.monotonic() + 1
        while listener._server._connection is None and time.monotonic() < deadline:
            time.sleep(0.005)
        self.assertIsNotNone(listener._server._connection)

    def test_consent_flow_timeout_closes_an_actual_accepted_idle_client(self):
        clients = []

        def arm(_method, _path, payload):
            url = payload["parameters"][0]["redirectUrl"]
            from urllib.parse import urlsplit
            target = urlsplit(url)
            client = socket.create_connection((target.hostname, target.port), timeout=2)
            clients.append(client)
            return {"value": [{"link": "https://example.invalid/synthetic-consent"}]}

        started = time.monotonic()
        try:
            with self.assertRaisesRegex(ValidationError, "Timed out"):
                _oauth_consent.run_consent_flow("connection", "object", "tenant", arm,
                                                no_browser=True, timeout=0.2)
            self.assertLess(time.monotonic() - started, 1.5)
            self.assertEqual(b"", clients[0].recv(1))
        finally:
            for client in clients:
                client.close()

    def test_callback_details_are_html_text_without_changing_protocol_values(self):
        hostile = '<script>alert("synthetic")</script><img src=x onerror="synthetic">&'
        for query in ({"error": hostile}, {"error": "denied", "error_description": hostile}):
            for method in ("GET", "POST"):
                with self.subTest(query=query, method=method), _oauth_consent.ConsentListener() as listener:
                    from urllib.request import Request
                    request = Request(listener.redirect_url + "?" + urlencode(query), method=method)
                    with urlopen(request, timeout=3) as response:
                        body = response.read()
                        self.assertEqual("text/html; charset=utf-8", response.headers["Content-Type"])
                        self.assertEqual(str(len(body)), response.headers["Content-Length"])
                        expected = _oauth_consent._SUCCESS_HTML.format(
                            heading="Authorization failed", detail=html.escape(hostile)).encode("utf-8")
                        self.assertEqual(expected, body)
                        self.assertNotIn(b"<script>", body)
                    self.assertEqual({"outcome": "error", "detail": hostile}, listener.wait(1))

    def test_idle_partial_and_trickled_requests_cannot_hold_consent_shutdown(self):
        for initial, trickle in ((b"", False), (b"GET /callback HTTP/1.1\r\nHost:", False),
                                 (b"GET /callback HTTP/1.1\r\nX-Slow: ", True)):
            with self.subTest(initial=initial, trickle=trickle):
                listener = _oauth_consent.ConsentListener().start()
                server_thread = listener._thread
                client = socket.create_connection(("127.0.0.1", listener.port), timeout=2)
                client.settimeout(2)
                if initial:
                    client.sendall(initial)
                self.assert_accepted(listener)
                done = threading.Event()

                def send_slowly():
                    while not done.wait(0.02):
                        try:
                            client.sendall(b"x")
                        except OSError:
                            return

                sender = threading.Thread(target=send_slowly, daemon=True)
                if trickle:
                    sender.start()
                timer = threading.Timer(2, client.close)
                timer.start()
                started = time.monotonic()
                try:
                    self.assertIsNone(listener.wait(0.15))
                    listener.stop()
                    self.assertLess(time.monotonic() - started, 1.5)
                    self.assertFalse(server_thread.is_alive())
                    with self.assertRaises(OSError):
                        socket.create_connection(("127.0.0.1", listener.port), timeout=0.3)
                finally:
                    done.set()
                    timer.cancel()
                    client.close()
                    if trickle:
                        sender.join(timeout=1)
                    listener.stop()

    def test_trickled_headers_have_an_absolute_read_deadline_without_shutdown(self):
        with _oauth_consent.ConsentListener() as listener:
            client = socket.create_connection(("127.0.0.1", listener.port), timeout=2)
            done = threading.Event()
            client.sendall(b"GET /callback HTTP/1.1\r\nX-Slow: ")
            self.assert_accepted(listener)

            def send_slowly():
                while not done.wait(0.02):
                    try:
                        client.sendall(b"x")
                    except OSError:
                        return

            sender = threading.Thread(target=send_slowly, daemon=True)
            sender.start()
            started = time.monotonic()
            try:
                self.assertEqual(b"", client.recv(1))
                self.assertLess(time.monotonic() - started, 1.5)
                self.assertIsNone(listener.wait(0))
            finally:
                done.set()
                client.close()
                sender.join(timeout=1)


class ManagedKindReviewTests(unittest.TestCase):
    def test_affirmative_trigger_evidence_wins_over_generic_or_action_metadata(self):
        for evidence in ({"kind": "trigger"}, {"properties": {"operationType": "Trigger"}},
                         {"properties": {"apiOperationType": "Trigger"}},
                         {"properties": {"capabilities": ["trigger"]}},
                         {"properties": {"isNotification": True}},
                         {"properties": {"isWebhook": True}}):
            for arm_type in (None, "Microsoft.Web/locations/managedApis/apiOperations"):
                item = {"name": "operation", "kind": "action", "properties": {"kind": "action"}}
                item.update(evidence)
                if arm_type:
                    item["type"] = arm_type
                with self.subTest(item=item):
                    self.assertEqual([], _managed_api._filter_operations([item], "action", None))
                    self.assertEqual([item], _managed_api._filter_operations([item], "trigger", None))

    def test_unspecified_and_positive_actions_keep_the_existing_fallback(self):
        for item in ({"name": "plain"}, {"kind": "action"}, {"properties": {"operationType": "Action"}},
                     {"type": "Microsoft.Web/locations/managedApis/apiOperations"}):
            with self.subTest(item=item):
                self.assertTrue(_managed_api._operation_matches_kind(item, "action"))
                self.assertFalse(_managed_api._operation_matches_kind(item, "trigger"))


class PackageReviewTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.app = self.root / "App"
        self.app.mkdir()
        (self.app / "host.json").write_text(json.dumps(_workflow.HOST_JSON), encoding="utf-8")
        self.archive = self.root / "package.zip"
        self.manifest = self.root / "manifest.json"

    def package(self, **kwargs):
        return _workflow.deterministic_package(str(self.app), str(self.archive),
                                               str(self.manifest), **kwargs)

    def assert_no_outputs(self):
        self.assertFalse(self.archive.exists())
        self.assertFalse(self.manifest.exists())

    def test_only_absent_ignore_file_can_disable_patterns(self):
        self.assertEqual([], _workflow._read_ignore_file(str(self.app)))
        ignored = self.app / ".funcignore"
        for data in (b"\xff\xfeinvalid", b"valid\n\xff"):
            ignored.write_bytes(data)
            with self.subTest(data=data), self.assertRaises(FileOperationError):
                self.package()
            self.assert_no_outputs()
        ignored.unlink()
        ignored.mkdir()
        with self.assertRaises(FileOperationError):
            self.package()
        self.assert_no_outputs()
        ignored.rmdir()
        ignored.write_text("private/\n*.sample\n", encoding="utf-8")
        real_open = open

        def deny(path, *args, **kwargs):
            if os.fspath(path) == str(ignored):
                raise PermissionError("Synthetic unreadable exclusions")
            return real_open(path, *args, **kwargs)

        with mock.patch("builtins.open", side_effect=deny), self.assertRaises(FileOperationError):
            self.package()
        self.assert_no_outputs()
        self.package()

    def test_dangling_ignore_symlink_is_not_a_genuinely_absent_file(self):
        ignored = self.app / ".funcignore"
        try:
            ignored.symlink_to(self.app / "missing-ignore")
        except OSError as error:
            self.skipTest("Host does not permit symlink creation: {}".format(error))
        with self.assertRaises(FileOperationError):
            self.package()
        self.assert_no_outputs()

    def test_case_equivalent_local_settings_are_unconditionally_secret(self):
        for name in ("Local.Settings.Json", "LOCAL.SETTINGS.JSON"):
            for parent in (self.app, self.app / "Nested"):
                parent.mkdir(exist_ok=True)
                path = parent / name
                path.write_text('{"Values":{"ApiToken":"synthetic-unrecognized-value"}}', encoding="utf-8")
                result = self.package(force=True)
                relative = path.relative_to(self.app).as_posix()
                self.assertIn({"path": relative, "reason": "secret"}, result["excluded"])
                with zipfile.ZipFile(self.archive) as archive:
                    self.assertNotIn(relative, archive.namelist())
                path.unlink()

    def assert_alias_refused(self, archive, manifest):
        before = archive.read_bytes() if archive.exists() else None
        with self.assertRaisesRegex(ValidationError, "distinct"):
            _workflow.deterministic_package(str(self.app), str(archive), str(manifest), force=True)
        if before is not None:
            self.assertEqual(before, archive.read_bytes())
            self.assertEqual(before, manifest.read_bytes())
        else:
            self.assertFalse(archive.exists())
            self.assertFalse(manifest.exists())

    def test_identical_and_normalized_output_paths_refuse_before_any_write(self):
        self.assert_alias_refused(self.archive, self.archive.parent / "absent" / ".." / self.archive.name)
        self.archive.write_bytes(b"ORIGINAL-ARCHIVE-BYTES")
        self.assert_alias_refused(self.archive, self.archive)
        if os.name == "nt":
            self.assert_alias_refused(self.archive, self.archive.with_name(self.archive.name.upper()))
        self.package(force=True)
        self.assertTrue(zipfile.is_zipfile(self.archive))

    def test_hardlink_output_alias_refuses_without_truncation(self):
        self.archive.write_bytes(b"ORIGINAL-HARDLINK-BYTES")
        os.link(self.archive, self.manifest)
        self.assert_alias_refused(self.archive, self.manifest)

    def test_symlink_and_parent_link_aliases_refuse_without_truncation(self):
        self.archive.write_bytes(b"ORIGINAL-SYMLINK-BYTES")
        alias = self.root / "alias"
        try:
            self.manifest.symlink_to(self.archive)
            alias.symlink_to(self.root, target_is_directory=True)
        except OSError as error:
            self.skipTest("Host does not permit symlink creation: {}".format(error))
        self.assert_alias_refused(self.archive, self.manifest)
        self.assert_alias_refused(self.archive, alias / self.archive.name)

    @unittest.skipUnless(os.name == "nt", "NTFS junction aliases")
    def test_parent_junction_output_alias_refuses_without_truncation(self):
        self.archive.write_bytes(b"ORIGINAL-JUNCTION-BYTES")
        junction = self.root / "junction"
        result = subprocess.run([os.environ["COMSPEC"], "/c", "mklink", "/J", str(junction), str(self.root)],
                                capture_output=True, check=False)
        self.assertEqual(0, result.returncode, result.stderr)
        try:
            self.assert_alias_refused(self.archive, junction / self.archive.name)
        finally:
            junction.rmdir()

    def test_native_markers_without_test_intent_cannot_hide_runtime_assemblies(self):
        directory = self.app / "lib"
        directory.mkdir()
        production = directory / "production.dll"
        production.write_bytes(b"ORDINARY-PRODUCTION-ASSEMBLY")
        for marker in (_test_scaffold.STATE_DIRECTORY, _test_scaffold.PROJECT_FILE):
            path = directory / marker
            if marker == _test_scaffold.STATE_DIRECTORY:
                path.mkdir()
            else:
                path.write_text("<Project />", encoding="utf-8")
            with self.subTest(marker=marker), self.assertRaisesRegex(ValidationError, "dedicated"):
                self.package()
            self.assert_no_outputs()
            self.assertEqual(b"ORDINARY-PRODUCTION-ASSEMBLY", production.read_bytes())
            if path.is_dir():
                path.rmdir()
            else:
                path.unlink()
        result = self.package()
        self.assertIn("lib/production.dll", [row["path"] for row in result["included"]])

    def test_conflicting_test_metadata_and_invalid_state_markers_refuse(self):
        directory = self.app / "Tests"
        directory.mkdir()
        project = directory / _test_scaffold.PROJECT_FILE
        for extra in ("<IsTestProject>false</IsTestProject>",
                      '<IsTestProject Condition="synthetic">true</IsTestProject>'):
            project.write_text("<Project><PropertyGroup><IsTestProject>true</IsTestProject>" +
                               extra + "</PropertyGroup></Project>", encoding="utf-8")
            with self.subTest(extra=extra), self.assertRaisesRegex(ValidationError, "dedicated"):
                self.package()
            self.assert_no_outputs()
        project.write_text("<Project><PropertyGroup><IsTestProject>true</IsTestProject>"
                           "</PropertyGroup></Project>", encoding="utf-8")
        (directory / _test_scaffold.STATE_DIRECTORY).write_text("not a state directory", encoding="utf-8")
        with self.assertRaisesRegex(ValidationError, "dedicated"):
            self.package()
        self.assert_no_outputs()

    def test_dedicated_test_intent_excludes_renamed_projects_and_generated_secrets(self):
        workflow = self.app / "Orders" / "workflow.json"
        workflow.parent.mkdir()
        workflow.write_text(json.dumps(_workflow.workflow_json("Stateful")), encoding="utf-8")
        created = _test_scaffold.create_project(str(self.app), "Orders")
        project = Path(created["testProject"])
        for state in (False, True):
            for filename in (_test_scaffold.PROJECT_FILE, "Existing.Native.csproj"):
                selected = project.with_name(filename)
                if selected != project:
                    project.rename(selected)
                for name in ("bin", "obj", "fixtures", _test_scaffold.STATE_DIRECTORY):
                    if name == _test_scaffold.STATE_DIRECTORY and not state:
                        continue
                    target = selected.parent / name / "nested"
                    target.mkdir(parents=True, exist_ok=True)
                    (target / "fixture.dll").write_bytes(b"TEST-BINARY-AND-SYNTHETIC-PRIVATE-FIXTURE")
                    (target / "workflow.json").write_text('{"fixture":"synthetic"}', encoding="utf-8")
                result = self.package(force=True)
                self.assertIn({"path": "Tests/Orders", "reason": "native-test-project"}, result["excluded"])
                with zipfile.ZipFile(self.archive) as archive:
                    self.assertFalse(any(name.startswith("Tests/Orders/") for name in archive.namelist()))
                if selected != project:
                    selected.rename(project)
        colocated = project.parent / "lib"
        colocated.mkdir()
        (colocated / "production.dll").write_bytes(b"RUNTIME-ASSEMBLY")
        with self.assertRaisesRegex(ValidationError, "dedicated"):
            self.package(force=True)
