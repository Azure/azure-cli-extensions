# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import shutil
import subprocess
import sys
import time
import unittest
import uuid
import warnings
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import psutil
from azure.cli.core.azclierror import CLIError, FileOperationError

from azext_logicapp import _dependencies, _local, _runtime_doctor


class IsolatedRuntimeTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parent / ".test-work-runtime" / uuid.uuid4().hex
        self.root.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, self.root)
        self.state = self.root / "state"
        self.state.mkdir()
        self.project = self.root / "project"
        self.project.mkdir()
        (self.project / "host.json").write_text("{}", encoding="utf-8")
        self.patch(_local, "STATE_DIR", str(self.state))

    def patch(self, obj, name, *args, **kwargs):
        patcher = mock.patch.object(obj, name, *args, **kwargs)
        value = patcher.start()
        self.addCleanup(patcher.stop)
        return value

    def write_record(self, port, pid, creation_time, **extra):
        record = {"pid": pid, "processCreateTimeUtc": creation_time, "port": port}
        record.update(extra)
        _local._write_record(port, record)
        return record


class SubprocessCompatibilityTests(IsolatedRuntimeTest):
    def test_production_probes_and_identity_stop_use_python36_subprocess_keywords(self):
        created = "2026-10-06T15:00:00.1234560Z"
        calls = []

        def python36_run(args, stdout=None, stderr=None, universal_newlines=False,
                         timeout=None, check=False, env=None, cwd=None, errors=None):
            calls.append((args, universal_newlines))
            self.assertEqual(subprocess.PIPE, stdout)
            self.assertEqual(subprocess.PIPE, stderr)
            output = json.dumps([{"ProcessId": 1234, "ParentProcessId": 1,
                                  "ProcessCreateTimeUtc": created}]) if "-Command" in args else "4.15.2\n"
            return SimpleNamespace(returncode=0, stdout=output, stderr="")

        self.patch(_local.subprocess, "run", side_effect=python36_run)
        self.patch(_local, "dependency_environment", return_value={})
        self.patch(_local, "_powershell_executable", return_value="powershell")
        self.assertEqual("4.15.2", _local._dependency_version("func", "core-tools"))
        self.assertEqual("4.15.2", _runtime_doctor._probe_version("func", {}, 2)[0])
        self.assertEqual([(1234, 1, created)], _local._process_tree_snapshot())
        _local._stop_process(1234, check=False, expected=created)
        self.assertEqual([True, True, True, False], [call[1] for call in calls])

    def test_aware_identity_parser_preserves_precision_and_rejects_unproven_timestamps(self):
        for value in ("2026-10-06T15:00:00.1234560Z", "2026-10-06T15:00:00.1234567+00:00"):
            parsed = _local._creation_datetime(value)
            self.assertEqual(123456, parsed.microsecond)
            self.assertEqual(0, parsed.utcoffset().total_seconds())
        self.assertEqual(3600, _local._creation_datetime(
            "2026-10-06T15:00:00+01:00").utcoffset().total_seconds())
        for value in (None, "", "2026-10-06T15:00:00", "2026-13-06T15:00:00Z",
                      "2026-10-06T15:00:00+24:00", "2026-10-06T15:00:00+00:99"):
            with self.subTest(value=value):
                self.assertIsNone(_local._creation_datetime(value))


class PortableIdentityTests(IsolatedRuntimeTest):
    def test_real_current_process_has_stable_verifiable_identity(self):
        creation_time = _local.process_create_time_utc(os.getpid())
        self.assertIsNotNone(creation_time)
        self.assertTrue(_local._record_matches({"pid": os.getpid(), "processCreateTimeUtc": creation_time}))
        self.assertFalse(_local._record_matches({"pid": os.getpid(), "processCreateTimeUtc": None}))

    def test_linux_and_macos_creation_times_distinguish_recycled_pids(self):
        for platform in ("linux", "darwin"):
            with self.subTest(platform=platform), mock.patch.object(_local.sys, "platform", platform), \
                    mock.patch.object(_local.psutil, "Process") as process:
                process.return_value.status.return_value = psutil.STATUS_RUNNING
                process.return_value.create_time.return_value = 1800000000.123456
                creation_time = _local.process_create_time_utc(1234)
                self.assertTrue(creation_time.endswith("Z"))
                record = {"pid": 1234, "processCreateTimeUtc": creation_time}
                self.assertTrue(_local._record_matches(record))
                process.return_value.create_time.return_value = 1800000010.123456
                self.assertFalse(_local._record_matches(record))

    def test_unknown_legacy_timestamps_fail_closed_on_linux_and_macos(self):
        killed = self.patch(_local, "_terminate")
        for platform in ("linux", "darwin"):
            for expected in (None, "", "2020-01-01T00:00:00Z"):
                with self.subTest(platform=platform, expected=expected), \
                        mock.patch.object(_local.sys, "platform", platform), \
                        mock.patch.object(_local.psutil, "Process", side_effect=psutil.AccessDenied(1234)):
                    record = self.write_record(17071, 1234, expected)
                    self.assertFalse(_local._record_matches(record))
                    with self.assertRaises(CLIError):
                        _local.stop_runtime(17071)
                    _local._write_azurite_record(record)
                    self.assertFalse(_local.stop_azurite()["stopped"])
        killed.assert_not_called()

    def test_zombies_and_invalid_pids_are_not_owned(self):
        with mock.patch.object(_local.sys, "platform", "linux"), \
                mock.patch.object(_local.psutil, "Process") as process:
            process.return_value.status.return_value = psutil.STATUS_ZOMBIE
            self.assertIsNone(_local.process_create_time_utc(1234))
            self.assertFalse(_local._is_running(1234))
            for pid in (None, 0, -1, True, "1234"):
                self.assertIsNone(_local.process_create_time_utc(pid))
                self.assertFalse(_local._is_running(pid))

    def test_linux_and_macos_termination_rechecks_saved_identity_before_signal(self):
        killed = self.patch(_local.os, "kill")
        expected = "2026-10-06T15:00:00.123456Z"
        for platform in ("linux", "darwin"):
            with self.subTest(platform=platform), mock.patch.object(_local.sys, "platform", platform), \
                    mock.patch.object(_local, "_is_running", return_value=True):
                for actual in (None, "2026-10-06T15:00:01.123456Z"):
                    with self.subTest(actual=actual), \
                            mock.patch.object(_local, "process_create_time_utc", return_value=actual):
                        with self.assertRaises(OSError):
                            _local._terminate(480001, expected=expected)
                        killed.assert_not_called()
                with mock.patch.object(_local, "process_create_time_utc", return_value=expected):
                    _local._terminate(480001, expected=expected)
                killed.assert_called_once_with(480001, 15)
                killed.reset_mock()
                _local._terminate(480001)
                killed.assert_called_once_with(480001, 15)
                killed.reset_mock()

    @unittest.skipUnless(sys.platform == "win32", "Windows legacy identity format")
    def test_native_windows_timestamp_matches_existing_cim_records(self):
        script = ("(Get-CimInstance Win32_Process -Filter \"ProcessId={}\").CreationDate."
                  "ToUniversalTime().ToString('o')").format(os.getpid())
        completed = subprocess.run(["powershell", "-NoProfile", "-Command", script],
                                   capture_output=True, text=True, check=True, timeout=20)
        legacy = completed.stdout.strip().replace("+00:00", "Z")
        self.assertEqual(_local.process_create_time_utc(os.getpid()), legacy)
        self.assertTrue(_local._record_matches({"pid": os.getpid(), "processCreateTimeUtc": legacy}))
        signal_query = ("$created = (Get-Process -Id {}).StartTime.ToUniversalTime(); "
                        "$created.AddTicks(-($created.Ticks % 10)).ToString('o')").format(os.getpid())
        completed = subprocess.run(["powershell", "-NoProfile", "-Command", signal_query],
                                   capture_output=True, text=True, check=True, timeout=20)
        self.assertEqual(legacy, completed.stdout.strip().replace("+00:00", "Z"))


class MalformedOwnershipRecordTests(IsolatedRuntimeTest):
    PORT = 17071
    PID = 480001
    CREATED = "2026-10-06T15:00:00.1234560Z"
    PRIVATE = "private-authored-record-content"

    def setUp(self):
        super().setUp()
        self.signal = self.patch(_local, "_terminate")
        self.patch(_local, "_readiness", return_value=(False, False, "fixture"))
        self.patch(_local, "_port_free", return_value=True)
        self.patch(_local, "find_tool", return_value=(str(self.root / "tool.cmd"), "managed"))
        self.patch(_local, "azurite_status", return_value={
            "running": False, "server": None, "blobEndpoint": "fixture", "ports": _local.AZURITE_PORTS,
            "portsInUse": []})
        self.spawn = self.patch(_local.subprocess, "Popen")
        (self.project / "local.settings.json").write_text(
            json.dumps({"Values": {"AzureWebJobsStorage": "UseDevelopmentStorage=true"}}), encoding="utf-8")

    def malformed_payloads(self):
        for root in ([], None, True, 4, self.PRIVATE, {}):
            yield json.dumps(root).encode()
        base = {"pid": self.PID, "processCreateTimeUtc": self.CREATED, "private": self.PRIVATE}
        for children in (None, {}, [None], [[]], [True], [{"pid": True}], [{"pid": 0}],
                         [{"pid": -1}], [{"pid": 480002.0}], [{"pid": "480002"}],
                         [{"pid": 480002, "processCreateTimeUtc": {"private": self.PRIVATE}}],
                         [{"pid": 480002, "childProcesses": []}],
                         [{"pid": self.PID}],
                         [{"pid": 480002}, {"pid": 480002}]):
            yield json.dumps(dict(base, childProcesses=children)).encode()
        for field, values in (
                ("pid", (False, -1, 0, 480001.0, "480001", {}, [])),
                ("processCreateTimeUtc", (True, 1.0, {}, [[[[self.PRIVATE]]]])),
                ("consumerPid", (None, True, 0, -1, 480001.0, {}, [])),
                ("consumerProcessCreateTimeUtc", (True, {}, [])),
                ("cleanupPending", ("true", None, 1))):
            for value in values:
                record = dict(base)
                if field == "consumerProcessCreateTimeUtc":
                    record["consumerPid"] = 480010
                record[field] = value
                yield json.dumps(record).encode()
        yield ('{"pid":480001,"pid":480002,"private":"' + self.PRIVATE + '"}').encode()
        yield b'{"pid":480001,"processCreateTimeUtc":NaN}'
        yield b'{"pid":480001,"private":"\xff"}'
        yield b'{"pid":480001,"processCreateTimeUtc":' + b'[' * 1100 + b'0' + b']' * 1100 + b'}'
        yield ('{"private":"' + self.PRIVATE).encode()

    def test_corrupt_runtime_records_refuse_without_signalling_or_losing_storage_guards(self):
        runtime_path = Path(_local._record_file(self.PORT))
        _local._write_azurite_record({"pid": 480003, "processCreateTimeUtc": self.CREATED})
        storage_before = Path(_local._azurite_record_file()).read_bytes()
        for identity in (self.CREATED, None, "2026-10-07T15:00:00.1234560Z"):
            with mock.patch.object(_local, "process_create_time_utc", return_value=identity), \
                    mock.patch.object(_local, "_is_running", return_value=True):
                for payload in self.malformed_payloads():
                    with self.subTest(identity=identity, payload=payload[:70]):
                        runtime_path.write_bytes(payload)
                        for operation in (lambda: _local._read_record(self.PORT),
                                          lambda: _local.show_runtime(self.PORT),
                                          lambda: _local.stop_runtime(self.PORT),
                                          lambda: _local.start_runtime(None, str(self.project), port=self.PORT)):
                            with self.assertRaises(CLIError) as error:
                                operation()
                            self.assertNotIn(self.PRIVATE, str(error.exception))
                        self.assertEqual(_local._live_runtime_records(), [self.PORT])
                        self.assertEqual(_local._release_azurite_if_idle()["ports"], [self.PORT])
                        self.assertEqual(runtime_path.read_bytes(), payload)
                        self.assertEqual(Path(_local._azurite_record_file()).read_bytes(), storage_before)
        self.signal.assert_not_called()
        self.spawn.assert_not_called()

    def test_corrupt_azurite_records_are_not_absent_and_cannot_be_overwritten_or_cleared(self):
        record_path = Path(_local._azurite_record_file())
        starter = mock.Mock()
        for identity in (self.CREATED, None, "2026-10-07T15:00:00.1234560Z"):
            with mock.patch.object(_local, "process_create_time_utc", return_value=identity), \
                    mock.patch.object(_local, "_is_running", return_value=True):
                for payload in self.malformed_payloads():
                    with self.subTest(identity=identity, payload=payload[:70]):
                        record_path.write_bytes(payload)
                        with self.assertRaises(FileOperationError) as error:
                            _local.read_azurite_record()
                        self.assertNotIn(self.PRIVATE, str(error.exception))
                        self.assertEqual(_local.stop_azurite()["reason"], "invalid-record")
                        self.assertEqual(_local._release_azurite_if_idle()["reason"], "invalid-record")
                        entry = _local.ensure_azurite(str(self.project), starter=starter)
                        self.assertEqual(entry["state"], "failed")
                        self.assertEqual(entry["reason"], "invalid-record")
                        self.assertNotIn(self.PRIVATE, json.dumps(entry))
                        with self.assertRaises(FileOperationError):
                            _local.start_azurite(str(self.root / "tool.cmd"))
                        self.assertEqual(record_path.read_bytes(), payload)
        starter.assert_not_called()
        self.signal.assert_not_called()
        self.spawn.assert_not_called()

    def test_doctor_does_not_report_corrupt_child_ownership_as_verified(self):
        record = {"pid": self.PID, "processCreateTimeUtc": self.CREATED, "childProcesses": None,
                  "private": self.PRIVATE}
        record_path = Path(_local._record_file(self.PORT))
        record_path.write_text(json.dumps(record), encoding="utf-8")
        with mock.patch.object(_local, "process_create_time_utc", return_value=self.CREATED), \
                mock.patch.object(_local, "_is_running", return_value=True):
            self.assertFalse(_local._record_matches(record))
            rows = []
            self.assertIsNone(_runtime_doctor._ownership(rows, "host.ownership", str(record_path)))
        self.assertEqual(rows[-1]["status"], "unknown")
        self.assertNotIn(self.PRIVATE, json.dumps(rows))
        self.signal.assert_not_called()

    def test_missing_records_remain_distinct_from_corrupt_records(self):
        self.assertIsNone(_local._read_record(self.PORT))
        self.assertIsNone(_local.read_azurite_record())
        self.assertEqual(_local.show_runtime(self.PORT)["state"], "stopped")
        self.assertEqual(_local.stop_azurite()["reason"], "not-started-by-cli")
        self.assertEqual(_local._live_runtime_records(), [])
        self.signal.assert_not_called()

    def test_unknown_existing_identity_retains_records_and_shared_storage(self):
        runtime = self.write_record(self.PORT, self.PID, None)
        _local._write_azurite_record(runtime)
        with mock.patch.object(_local, "process_create_time_utc", return_value=None), \
                mock.patch.object(_local.psutil, "pid_exists", return_value=True):
            self.assertEqual(_local._live_runtime_records(), [self.PORT])
            self.assertEqual(_local.stop_azurite()["reason"], "identity-unverified")
            with self.assertRaises(CLIError):
                _local.stop_runtime(self.PORT)
        self.assertEqual(_local.read_azurite_record(), runtime)
        self.assertEqual(_local._read_record(self.PORT), runtime)
        self.signal.assert_not_called()

    def test_stop_all_reports_corrupt_record_and_preserves_storage_after_stopping_valid_runtime(self):
        self.write_record(self.PORT, self.PID, self.CREATED)
        corrupt_path = Path(_local._record_file(self.PORT + 1))
        corrupt_path.write_text('["{}"]'.format(self.PRIVATE), encoding="utf-8")
        _local._write_azurite_record({"pid": 480003, "processCreateTimeUtc": self.CREATED})
        live = {self.PID: self.CREATED, 480003: self.CREATED}

        def stop(pid, expected=None):
            self.assertEqual(expected, self.CREATED)
            live.pop(pid)

        self.signal.side_effect = stop
        with mock.patch.object(_local, "process_create_time_utc", side_effect=live.get), \
                mock.patch.object(_local, "_is_running", side_effect=lambda pid: pid in live), \
                mock.patch.object(_local.psutil, "Process",
                                  return_value=mock.Mock(children=mock.Mock(return_value=[]))):
            result = _local.stop_runtime(all_records=True)
        self.assertEqual(len(result["stopped"]), 1)
        self.assertEqual(result["refused"][0]["reasonCode"], "runtime.invalid_record")
        self.assertEqual(result["azurite"]["ports"], [self.PORT + 1])
        self.assertNotIn(self.PRIVATE, json.dumps(result))
        self.assertTrue(corrupt_path.exists())
        self.assertIsNotNone(_local.read_azurite_record())
        self.signal.assert_called_once_with(self.PID, expected=self.CREATED)


class WindowsDescendantIdentityTests(IsolatedRuntimeTest):
    PARENT = 480001
    CHILD = 480002
    GRANDCHILD = 480003
    SIBLING = 480004
    CREATED = "2026-10-06T15:00:00.1234560Z"
    REPLACEMENT = "2026-10-06T15:00:01.1234560Z"

    def setUp(self):
        super().setUp()
        self.live = {self.PARENT: self.CREATED, self.CHILD: self.CREATED,
                     self.GRANDCHILD: self.CREATED, self.SIBLING: self.CREATED}
        self.patch(_local.sys, "platform", "win32")
        self.patch(_local, "_powershell_executable", return_value="powershell")
        self.patch(_local, "process_create_time_utc", side_effect=lambda pid: self.live.get(pid))
        self.patch(_local, "_is_running", side_effect=lambda pid: pid in self.live)
        self.patch(_local.psutil, "pid_exists", side_effect=lambda pid: pid in self.live)
        self.native_snapshot = self.patch(
            _local, "_windows_process_snapshot", side_effect=lambda pid: (self.live.get(pid), False))
        self.patch(_local.psutil, "Process", return_value=mock.Mock(children=mock.Mock(return_value=[])))
        self.patch(_local, "probe_azurite", return_value=None)
        self.real_snapshot = _local._process_tree_snapshot
        self.patch(_local, "_process_tree_snapshot", side_effect=self.snapshot)
        self.stopped = []
        self.real_stop = _local._stop_process
        self.stop = self.patch(_local, "_stop_process", side_effect=self.signal)
        self.on_parent_stop = None

    def snapshot(self):
        return [(self.PARENT, 1, self.CREATED), (self.CHILD, self.PARENT, self.CREATED),
                (self.GRANDCHILD, self.CHILD, self.CREATED), (self.SIBLING, 1, self.CREATED)]

    def signal(self, pid, check, expected=None):
        self.assertTrue(check)
        self.assertEqual(self.live[pid], expected)
        self.stopped.append(pid)
        self.live.pop(pid)
        if pid == self.PARENT and self.on_parent_stop:
            self.on_parent_stop()

    def test_mocked_exit_probe_tracks_fixture_state_without_native_process_access(self):
        with mock.patch("ctypes.WinDLL", create=True,
                        side_effect=AssertionError("Mocked process fixture reached native Windows APIs")):
            for present, created in ((True, self.CREATED), (True, self.REPLACEMENT),
                                     (True, None), (False, None)):
                with self.subTest(present=present, created=created):
                    if present:
                        self.live[self.CHILD] = created
                    else:
                        self.live.pop(self.CHILD)
                    self.native_snapshot.reset_mock()
                    self.assertEqual(present, _local._process_may_exist(self.CHILD))
                    if present:
                        self.native_snapshot.assert_called_once_with(self.CHILD)
                    else:
                        self.native_snapshot.assert_not_called()
                    self.assertEqual((created, False), _local._windows_process_snapshot(self.CHILD))

    def test_verified_original_descendants_are_stopped_deepest_first_not_siblings(self):
        _local._terminate(self.PARENT)
        self.assertEqual(self.stopped, [self.PARENT, self.GRANDCHILD, self.CHILD])
        self.assertIn(self.SIBLING, self.live)
        self.assertEqual(self.stop.call_args_list[-1].kwargs["expected"], self.CREATED)

    def test_recycled_descendant_is_not_signalled_and_runtime_storage_guard_survives(self):
        self.on_parent_stop = lambda: self.live.update({self.CHILD: self.REPLACEMENT})
        self.write_record(17071, self.PARENT, self.CREATED)
        _local._write_azurite_record({"pid": self.SIBLING, "processCreateTimeUtc": self.CREATED})
        storage_before = Path(_local._azurite_record_file()).read_bytes()
        with self.assertRaises(CLIError):
            _local.stop_runtime(17071)
        self.assertEqual(self.stopped, [self.PARENT, self.GRANDCHILD])
        record = _local._read_record(17071)
        child = next(item for item in record["childProcesses"] if item["pid"] == self.CHILD)
        self.assertEqual(child["processCreateTimeUtc"], self.CREATED)
        self.assertTrue(record["cleanupPending"])
        self.assertFalse(_local._record_matches(child))
        self.assertEqual(_local._live_runtime_records(), [17071])
        self.assertEqual(_local._release_azurite_if_idle()["ports"], [17071])
        self.assertEqual(Path(_local._azurite_record_file()).read_bytes(), storage_before)
        with self.assertRaises(CLIError):
            _local.stop_runtime(17071)
        self.assertNotIn(self.CHILD, self.stopped)

    def test_unknown_descendant_birth_is_nonowning_and_emulator_cleanup_is_truthful(self):
        self.patch(_local, "_process_tree_snapshot", return_value=[
            (self.PARENT, 1, self.CREATED), (self.CHILD, self.PARENT, None)])
        _local._write_azurite_record({"pid": self.PARENT, "processCreateTimeUtc": self.CREATED})
        result = _local.stop_azurite()
        self.assertFalse(result["stopped"])
        self.assertEqual(result["reason"], "cleanup-pending")
        self.assertEqual(self.stopped, [self.PARENT])
        retained = _local.read_azurite_record()
        self.assertTrue(retained["cleanupPending"])
        self.assertIsNone(retained["childProcesses"][0]["processCreateTimeUtc"])
        self.assertEqual(_local.stop_azurite()["reason"], "identity-unverified")
        self.assertEqual(self.stopped, [self.PARENT])

    def test_parent_pid_recycled_before_snapshot_cannot_authorize_descendants(self):
        def recycled_snapshot():
            self.live[self.PARENT] = self.REPLACEMENT
            return [(self.PARENT, 1, self.REPLACEMENT), (self.CHILD, self.PARENT, self.CREATED)]

        self.patch(_local, "_process_tree_snapshot", side_effect=recycled_snapshot)
        with self.assertRaises(OSError):
            _local._terminate(self.PARENT)
        self.stop.assert_not_called()

    def test_saved_root_identity_is_not_replaced_by_current_recycled_identity(self):
        self.live[self.PARENT] = self.REPLACEMENT
        self.patch(_local, "_process_tree_snapshot", return_value=[
            (self.PARENT, 1, self.REPLACEMENT), (self.CHILD, self.PARENT, self.REPLACEMENT)])
        with self.assertRaises(OSError):
            _local._terminate(self.PARENT, expected=self.CREATED)
        self.stop.assert_not_called()
        self.assertEqual(self.stopped, [])

    def test_saved_root_recycled_between_snapshot_and_signal_is_not_stopped(self):
        def recycled_after_snapshot():
            snapshot = self.snapshot()
            self.live[self.PARENT] = self.REPLACEMENT
            return snapshot

        self.patch(_local, "_process_tree_snapshot", side_effect=recycled_after_snapshot)
        with self.assertRaises(OSError):
            _local._terminate(self.PARENT, expected=self.CREATED)
        self.stop.assert_not_called()
        self.assertEqual(self.stopped, [])

    def test_root_recycle_during_record_driven_stop_preserves_saved_identity_and_storage(self):
        real_terminate = _local._terminate
        storage_path = Path(_local._azurite_record_file())
        for stage in ("before-query", "after-snapshot", "at-native-signal"):
            with self.subTest(stage=stage):
                self.live = {self.PARENT: self.CREATED, self.CHILD: self.CREATED,
                             self.GRANDCHILD: self.CREATED, self.SIBLING: self.CREATED}
                self.stopped.clear()
                self.stop.reset_mock()
                self.write_record(17071, self.PARENT, self.CREATED)
                _local._write_azurite_record({"pid": self.SIBLING, "processCreateTimeUtc": self.CREATED})
                storage_before = storage_path.read_bytes()

                def terminate(pid, expected=None):
                    self.assertEqual(expected, self.CREATED)
                    if stage == "before-query":
                        self.live[self.PARENT] = self.REPLACEMENT
                    return real_terminate(pid, expected=expected)

                def snapshot():
                    rows = self.snapshot()
                    if stage == "before-query":
                        rows[0] = (self.PARENT, 1, self.REPLACEMENT)
                    if stage == "after-snapshot":
                        self.live[self.PARENT] = self.REPLACEMENT
                    return rows

                def native_signal(pid, check, expected=None):
                    if stage == "at-native-signal":
                        self.live[self.PARENT] = self.REPLACEMENT
                    if self.live.get(pid) != expected:
                        raise OSError("Process creation identity changed; no process was stopped.")
                    return self.signal(pid, check, expected=expected)

                self.stop.side_effect = native_signal
                with mock.patch.object(_local, "_terminate", side_effect=terminate) as terminated, \
                        mock.patch.object(_local, "_process_tree_snapshot", side_effect=snapshot):
                    with self.assertRaises(CLIError):
                        _local.stop_runtime(17071)
                terminated.assert_called_once_with(self.PARENT, expected=self.CREATED)
                self.assertEqual(self.stopped, [])
                if stage == "at-native-signal":
                    self.stop.assert_called_once_with(self.PARENT, check=True, expected=self.CREATED)
                else:
                    self.stop.assert_not_called()
                record = _local._read_record(17071)
                self.assertEqual(record["pid"], self.PARENT)
                self.assertEqual(record["processCreateTimeUtc"], self.CREATED)
                self.assertTrue(record["cleanupPending"])
                self.assertFalse(_local._record_matches(record))
                self.assertEqual(_local._live_runtime_records(), [17071])
                self.assertEqual(_local._release_azurite_if_idle()["ports"], [17071])
                self.assertEqual(storage_path.read_bytes(), storage_before)
                self.assertEqual(self.live[self.PARENT], self.REPLACEMENT)

    def test_record_without_original_creation_identity_cannot_adopt_a_current_root(self):
        record = {"pid": self.PARENT, "processCreateTimeUtc": None}
        with self.assertRaises(OSError):
            _local._terminate_record_process(record, record)
        self.assertTrue(record["cleanupPending"])
        self.assertEqual(self.stopped, [])
        self.stop.assert_not_called()

    def test_process_born_before_recycled_parent_is_not_owned(self):
        self.live[self.PARENT] = self.REPLACEMENT
        self.patch(_local, "_process_tree_snapshot", return_value=[
            (self.PARENT, 1, self.REPLACEMENT), (self.CHILD, self.PARENT, self.CREATED)])
        _local._terminate(self.PARENT)
        self.assertEqual(self.stopped, [self.PARENT])
        self.assertIn(self.CHILD, self.live)

    def test_preexisting_process_subtree_is_neither_owned_nor_a_cleanup_guard(self):
        self.live[self.PARENT] = self.REPLACEMENT
        self.patch(_local, "_process_tree_snapshot", return_value=[
            (self.PARENT, 1, self.REPLACEMENT), (self.CHILD, self.PARENT, self.CREATED),
            (self.GRANDCHILD, self.CHILD, self.CREATED)])
        _local._terminate(self.PARENT, expected=self.REPLACEMENT)
        self.assertEqual(self.stopped, [self.PARENT])
        self.assertIn(self.CHILD, self.live)
        self.assertIn(self.GRANDCHILD, self.live)

    def test_changed_or_unverifiable_preexisting_snapshot_remains_a_cleanup_guard(self):
        self.live[self.PARENT] = self.REPLACEMENT
        for actual in (None, self.REPLACEMENT):
            with self.subTest(actual=actual):
                self.live[self.PARENT] = self.REPLACEMENT
                self.live[self.CHILD] = actual
                self.stopped.clear()
                self.patch(_local, "_process_tree_snapshot", return_value=[
                    (self.PARENT, 1, self.REPLACEMENT), (self.CHILD, self.PARENT, self.CREATED)])
                with self.assertRaises(OSError):
                    _local._terminate(self.PARENT, expected=self.REPLACEMENT)
                self.assertEqual(self.stopped, [self.PARENT])
                self.assertIn(self.CHILD, self.live)

    def test_already_exited_children_do_not_make_verified_cleanup_fail(self):
        self.on_parent_stop = lambda: (self.live.pop(self.CHILD), self.live.pop(self.GRANDCHILD))
        _local._terminate(self.PARENT)
        self.assertEqual(self.stopped, [self.PARENT])

    def test_child_exiting_during_native_signal_is_not_retained_as_unverified(self):
        def signal(pid, check, expected=None):
            if pid == self.GRANDCHILD:
                self.live.pop(pid)
                raise subprocess.CalledProcessError(1, "fixture exited before Get-Process")
            return self.signal(pid, check, expected)

        self.stop.side_effect = signal
        _local._terminate(self.PARENT)
        self.assertEqual(self.stopped, [self.PARENT, self.CHILD])

    def test_parent_exiting_during_native_signal_still_cleans_verified_children(self):
        def signal(pid, check, expected=None):
            if pid == self.PARENT:
                self.live.pop(pid)
                raise subprocess.CalledProcessError(1, "fixture exited before Get-Process")
            return self.signal(pid, check, expected)

        self.stop.side_effect = signal
        _local._terminate(self.PARENT, expected=self.CREATED)
        self.assertEqual(self.stopped, [self.GRANDCHILD, self.CHILD])

    def test_cycle_does_not_grant_ownership_to_unrelated_processes_or_loop(self):
        self.patch(_local, "_process_tree_snapshot", return_value=[
            (self.PARENT, self.CHILD, self.CREATED), (self.CHILD, self.PARENT, self.CREATED)])
        _local._terminate(self.PARENT)
        self.assertEqual(self.stopped, [self.PARENT, self.CHILD])

    def test_pid_only_legacy_snapshot_does_not_grant_child_termination(self):
        self.patch(_local, "_process_tree_snapshot", return_value=[
            (self.PARENT, 1, self.CREATED), (self.CHILD, self.PARENT)])
        with self.assertRaises(OSError):
            _local._terminate(self.PARENT)
        self.assertEqual(self.stopped, [self.PARENT])
        self.assertIn(self.CHILD, self.live)

    def test_unknown_tree_retains_original_guard_without_any_signal(self):
        self.patch(_local, "_process_tree_snapshot", side_effect=OSError("Process tree unavailable."))
        self.write_record(17071, self.PARENT, self.CREATED)
        with self.assertRaises(CLIError):
            _local.stop_runtime(17071)
        self.stop.assert_not_called()
        self.assertTrue(_local._read_record(17071)["cleanupPending"])
        self.assertEqual(_local._live_runtime_records(), [17071])

    def test_native_signal_command_rechecks_microsecond_birth_using_process_object(self):
        runner = self.patch(_local.subprocess, "run", return_value=subprocess.CompletedProcess([], 0))
        self.real_stop(self.CHILD, check=True, expected=self.CREATED)
        script = runner.call_args.args[0][-1]
        self.assertIn(self.CREATED, script)
        self.assertIn("Get-Process -Id {}".format(self.CHILD), script)
        self.assertIn("AddTicks(-($created.Ticks % 10))", script)
        self.assertIn("Stop-Process -InputObject $process", script)
        self.assertNotIn("Stop-Process -Id", script)
        runner.assert_called_once()

    def test_cim_snapshot_keeps_original_birth_and_rejects_invalid_identity_shapes(self):
        payload = [{"ProcessId": self.PARENT, "ParentProcessId": 1, "ProcessCreateTimeUtc": self.CREATED},
                   {"ProcessId": self.CHILD, "ParentProcessId": self.PARENT,
                    "ProcessCreateTimeUtc": self.CREATED}]
        runner = self.patch(_local.subprocess, "run",
                            return_value=subprocess.CompletedProcess([], 0, json.dumps(payload)))
        self.assertEqual(self.real_snapshot(), [(self.PARENT, 1, self.CREATED),
                                                (self.CHILD, self.PARENT, self.CREATED)])
        self.assertIn("CreationDate.ToUniversalTime().ToString('o')", runner.call_args.args[0][-1])
        for invalid in (None, True, 42, [None], [{"ProcessId": True, "ParentProcessId": 1}],
                        [{"ProcessId": -1, "ParentProcessId": 1}],
                        [{"ProcessId": self.CHILD, "ParentProcessId": 1.0}], payload + [payload[0]]):
            with self.subTest(payload=invalid):
                runner.return_value = subprocess.CompletedProcess([], 0, json.dumps(invalid))
                with self.assertRaises(OSError):
                    self.real_snapshot()
        runner.return_value = subprocess.CompletedProcess([], 1, "private-process-output")
        with self.assertRaises(OSError) as error:
            self.real_snapshot()
        self.assertNotIn("private-process-output", str(error.exception))
        self.stop.assert_not_called()


class RuntimeCleanupRecoveryTests(IsolatedRuntimeTest):
    PORT = 17071
    PARENT = 480001
    CHILD = 480002
    CONSUMER = 480003
    CREATED = "2026-10-06T15:00:00.1234560Z"
    REPLACEMENT = "2026-10-07T15:00:00.1234560Z"

    def setUp(self):
        super().setUp()
        self.live = {}
        self.patch(_local, "process_create_time_utc", side_effect=self.live.get)
        self.patch(_local, "_is_running", side_effect=lambda pid: pid in self.live)
        self.patch(_local.psutil, "pid_exists", side_effect=lambda pid: pid in self.live)
        self.patch(_local, "_port_free", return_value=True)
        self.release = self.patch(_local, "_release_azurite_if_idle", return_value=None)
        self.signal = self.patch(_local, "_terminate")
        self.record = self.write_record(
            self.PORT, self.PARENT, self.CREATED, cleanupPending=True, launchId="failed-launch",
            childProcesses=[{"pid": self.CHILD, "processCreateTimeUtc": self.CREATED}])
        self.before = Path(_local._record_file(self.PORT)).read_bytes()

    def assert_retained(self):
        with self.assertRaises(CLIError):
            _local.stop_runtime(self.PORT)
        self.assertEqual(self.before, Path(_local._record_file(self.PORT)).read_bytes())
        self.signal.assert_not_called()
        self.release.assert_not_called()

    def test_retry_recovers_exact_failed_receipt_after_all_recorded_processes_exit(self):
        result = _local.stop_runtime(self.PORT)
        self.assertEqual("already-exited", result["stopped"][0]["result"])
        self.assertEqual([], result["refused"])
        self.assertIsNone(_local._read_record(self.PORT))
        self.signal.assert_not_called()
        self.release.assert_called_once()

    def test_recycled_parent_or_child_cannot_authorize_cleanup_or_shared_storage_release(self):
        for pid in (self.PARENT, self.CHILD):
            with self.subTest(pid=pid):
                self.live = {pid: self.REPLACEMENT}
                self.assert_retained()

    def test_unverifiable_process_keeps_receipt_and_storage_guard(self):
        self.patch(_local.psutil, "pid_exists", return_value=True)
        self.assert_retained()

    def test_process_existence_probe_failure_keeps_receipt(self):
        self.patch(_local.psutil, "pid_exists", side_effect=psutil.AccessDenied(self.PARENT))
        self.assert_retained()

    def test_running_or_recycled_launch_consumer_prevents_receipt_recovery(self):
        self.record.update(consumerPid=self.CONSUMER, consumerProcessCreateTimeUtc=self.CREATED)
        _local._write_record(self.PORT, self.record)
        self.before = Path(_local._record_file(self.PORT)).read_bytes()
        for actual in (self.CREATED, self.REPLACEMENT, None):
            with self.subTest(actual=actual):
                self.live = {self.CONSUMER: actual}
                self.assert_retained()

    def test_occupied_port_prevents_recovery_without_attempting_a_signal(self):
        self.patch(_local, "_port_free", return_value=False)
        self.assert_retained()

    def test_ordinary_stale_receipt_does_not_gain_cleanup_authority(self):
        self.record.pop("cleanupPending")
        _local._write_record(self.PORT, self.record)
        self.before = Path(_local._record_file(self.PORT)).read_bytes()
        self.assert_retained()

    def test_concurrent_replacement_is_retained_not_deleted_or_overwritten(self):
        replacement = dict(self.record, launchId="new-launch", pid=self.CONSUMER)

        def replace(_record):
            _local._write_record(self.PORT, replacement)
            return False

        self.patch(_local, "_runtime_has_live_process", side_effect=replace)
        with self.assertRaisesRegex(CLIError, "changed during cleanup"):
            _local.stop_runtime(self.PORT)
        self.assertEqual(replacement, _local._read_record(self.PORT))
        self.signal.assert_not_called()
        self.release.assert_not_called()

    def test_failed_stop_does_not_overwrite_a_new_launch_receipt(self):
        self.live[self.PARENT] = self.CREATED
        replacement = dict(self.record, launchId="new-launch", pid=self.CONSUMER)
        self.patch(_local.psutil, "Process", return_value=mock.Mock(children=mock.Mock(return_value=[])))

        def signal(_pid, expected=None):
            self.assertEqual(self.CREATED, expected)
            _local._write_record(self.PORT, replacement)
            raise OSError("fixture interrupted cleanup")

        self.signal.side_effect = signal
        with self.assertRaisesRegex(CLIError, "changed during cleanup"):
            _local.stop_runtime(self.PORT)
        self.assertEqual(replacement, _local._read_record(self.PORT))
        self.release.assert_not_called()

    def test_receipt_removal_error_retains_recoverable_failed_stop(self):
        self.record.pop("cleanupPending")
        _local._write_record(self.PORT, self.record)
        self.live[self.PARENT] = self.CREATED
        self.patch(_local.psutil, "Process", return_value=mock.Mock(children=mock.Mock(return_value=[])))

        def signal(pid, expected=None):
            self.assertEqual(self.CREATED, expected)
            self.live.pop(pid)

        self.signal.side_effect = signal
        remove = _local.os.remove

        def fail_receipt(path):
            if path == _local._record_file(self.PORT):
                raise PermissionError("fixture removal failure")
            return remove(path)

        with mock.patch.object(_local.os, "remove", side_effect=fail_receipt):
            with self.assertRaises(CLIError):
                _local.stop_runtime(self.PORT)
        self.assertTrue(_local._read_record(self.PORT)["cleanupPending"])
        self.release.assert_not_called()
        self.assertEqual("already-exited", _local.stop_runtime(self.PORT)["stopped"][0]["result"])
        self.assertIsNone(_local._read_record(self.PORT))
        self.signal.assert_called_once_with(self.PARENT, expected=self.CREATED)

    def test_stop_all_recovers_only_finished_receipts_and_reports_other_refusals(self):
        other = self.write_record(self.PORT + 1, self.CONSUMER, self.CREATED, cleanupPending=True)
        self.live[self.CONSUMER] = self.REPLACEMENT
        result = _local.stop_runtime(all_records=True)
        self.assertEqual([self.PORT], [item["port"] for item in result["stopped"]])
        self.assertEqual("already-exited", result["stopped"][0]["result"])
        self.assertEqual([self.PORT + 1], [item["port"] for item in result["refused"]])
        self.assertEqual(other, _local._read_record(self.PORT + 1))
        self.signal.assert_not_called()

    def test_native_recovery_lock_rechecks_receipt_after_independent_writer_finishes(self):
        replacement = dict(self.record, launchId="new-launch")
        script = (
            "import sys; from azext_logicapp import _local; "
            "_local.STATE_DIR = sys.argv[1]; port = int(sys.argv[2]); "
            "expected = _local._read_record(port); print('waiting', flush=True); "
            "_local._remove_runtime_record(port, expected, recover=True)"
        )
        environment = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[3]),
                           PYTHONDONTWRITEBYTECODE="1")
        process = None
        try:
            with _local._store_lock(_local._record_file(self.PORT)):
                process = subprocess.Popen(
                    [sys.executable, "-c", script, str(self.state), str(self.PORT)],
                    env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    universal_newlines=True)
                self.assertEqual("waiting", process.stdout.readline().strip())
                self.assertIsNone(process.poll())
                Path(_local._record_file(self.PORT)).write_text(json.dumps(replacement), encoding="utf-8")
            _, stderr = process.communicate(timeout=20)
            self.assertNotEqual(0, process.returncode)
            self.assertIn("changed during cleanup", stderr)
            self.assertEqual(replacement, _local._read_record(self.PORT))
        finally:
            if process is not None and process.poll() is None:
                process.terminate()
                process.communicate(timeout=10)


class WindowsExitedProcessTests(IsolatedRuntimeTest):
    @unittest.skipUnless(sys.platform == "win32", "Native Windows exit timestamp with held handle")
    def test_exited_process_object_is_not_a_live_or_unverified_storage_consumer(self):
        process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
        try:
            created = _local.process_create_time_utc(process.pid)
            self.assertIsNotNone(created)
            self.assertTrue(_local._process_may_exist(process.pid))
            process.terminate()
            process.wait(timeout=10)
            # The held handle still exposes the native exit timestamp, even
            # when a conservative PID-presence probe reports the object.
            self.assertEqual((None, True), _local._windows_process_snapshot(process.pid))
            self.assertIsNone(_local.process_create_time_utc(process.pid))
            self.assertFalse(_local._process_may_exist(process.pid))
            with mock.patch.object(_local.psutil, "pid_exists", return_value=True):
                self.assertFalse(_local._process_may_exist(process.pid))
            self.write_record(17071, process.pid, created, cleanupPending=True)
            self.patch(_local, "_port_free", return_value=True)
            self.patch(_local, "_release_azurite_if_idle", return_value=None)
            signal = self.patch(_local, "_terminate")
            self.assertEqual("already-exited", _local.stop_runtime(17071)["stopped"][0]["result"])
            self.assertIsNone(_local._read_record(17071))
            signal.assert_not_called()
        finally:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=10)

    def test_unavailable_windows_exit_timestamp_is_not_proof_of_exit(self):
        self.patch(_local.sys, "platform", "win32")
        self.patch(_local.psutil, "pid_exists", return_value=True)
        self.patch(_local, "_windows_process_snapshot", return_value=(None, False))
        self.assertTrue(_local._process_may_exist(480001))


class DependencyEnvironmentTests(IsolatedRuntimeTest):
    def tool(self, root, kind):
        directory = root / _local.managed_subdir(kind)
        directory.mkdir(parents=True, exist_ok=True)
        name = {"node": "node", "dotnet": "dotnet", "core-tools": "func", "azurite": "azurite"}[kind]
        executable = directory / (name + ".CMD" if os.name == "nt" else name)
        executable.write_text("", encoding="utf-8")
        executable.chmod(0o755)
        return executable

    def test_managed_paths_are_child_only_and_honor_environment_override(self):
        managed = self.root / "managed"
        tools = {kind: self.tool(managed, kind) for kind in ("node", "dotnet", "core-tools", "azurite")}
        with mock.patch.dict(os.environ, {"PATH": "", "LA_DEPENDENCIES_PATH": str(managed)}):
            before = os.environ.copy()
            environment = _local.dependency_environment(str(tools["azurite"]))
            self.assertEqual(os.environ.copy(), before)
            self.assertEqual(shutil.which("node", path=environment["PATH"]), str(tools["node"]))
            self.assertEqual(shutil.which("dotnet", path=environment["PATH"]), str(tools["dotnet"]))
            self.assertEqual(_local.find_tool("node"), (str(tools["node"]), "managed"))

    def test_path_node_precedence_is_preserved_for_runtime_launchers(self):
        managed = self.root / "managed"
        managed_node = self.tool(managed, "node")
        func = self.tool(managed, "core-tools")
        user_node = self.tool(self.root / "user", "node")
        with mock.patch.dict(os.environ, {"PATH": str(user_node.parent), "LA_DEPENDENCIES_PATH": str(managed)}):
            environment = _local.dependency_environment(str(func))
            self.assertEqual(shutil.which("node", path=environment["PATH"]), str(user_node))
            self.assertNotEqual(shutil.which("node", path=environment["PATH"]), str(managed_node))

    def test_npm_uses_its_explicit_root_not_environment_override(self):
        explicit = self.root / "explicit"
        explicit_node = self.tool(explicit, "node")
        ignored_node = self.tool(self.root / "override", "node")
        npm = explicit_node.parent / ("npm.CMD" if os.name == "nt" else "npm")
        npm.write_text("", encoding="utf-8")
        npm.chmod(0o755)
        with mock.patch.dict(os.environ, {"PATH": str(ignored_node.parent),
                                          "LA_DEPENDENCIES_PATH": str(ignored_node.parent.parent)}):
            self.assertEqual(_dependencies._resolve_npm(str(explicit)), str(npm))
            runner = self.patch(_dependencies.subprocess, "run",
                                return_value=subprocess.CompletedProcess([], 0, "ok"))
            self.assertEqual(_dependencies._run_npm(str(npm), ["--version"]), (True, "ok"))
            environment = runner.call_args.kwargs["env"]
            self.assertEqual(shutil.which("node", path=environment["PATH"]), str(explicit_node))
            self.assertEqual(os.environ["PATH"], str(ignored_node.parent))

    def test_dependency_version_probe_receives_managed_node_environment(self):
        managed = self.root / "managed"
        node = self.tool(managed, "node")
        azurite = self.tool(managed, "azurite")
        runner = self.patch(_local.subprocess, "run",
                            return_value=subprocess.CompletedProcess([], 0, "3.35.0\n"))
        with mock.patch.dict(os.environ, {"PATH": "", "LA_DEPENDENCIES_PATH": str(managed)}):
            self.assertEqual(_local._dependency_version(str(azurite), "azurite"), "3.35.0")
            self.assertEqual(shutil.which("node", path=runner.call_args.kwargs["env"]["PATH"]), str(node))


class FakeProcess:
    def __init__(self, pid, live):
        self.pid = pid
        self.live = live
        self.returncode = None
        self.on_wait = None
        self.terminated = False

    def poll(self):
        if self.pid not in self.live and self.returncode is None:
            self.returncode = 0
        return self.returncode

    def wait(self, timeout=None):
        if self.poll() is not None:
            return self.returncode
        if self.on_wait:
            return self.on_wait(timeout)
        raise subprocess.TimeoutExpired("fixture", timeout)

    def terminate(self):
        self.terminated = True
        self.live.pop(self.pid, None)
        self.returncode = 0


class PendingAzuriteTests(IsolatedRuntimeTest):
    def test_zero_timeout_live_emulator_is_reused_not_overwritten_by_a_second_launch(self):
        (self.project / "local.settings.json").write_text(
            json.dumps({"Values": {"AzureWebJobsStorage": "UseDevelopmentStorage=true"}}), encoding="utf-8")
        _local._write_azurite_record({"pid": 480003, "processCreateTimeUtc": "2026-10-06T15:00:00Z",
                                     "server": None, "logPath": "fixture.log"})
        self.patch(_local, "find_tool", return_value=(str(self.root / "azurite.cmd"), "managed"))
        self.patch(_local, "process_create_time_utc", return_value="2026-10-06T15:00:00Z")
        self.patch(_local, "_is_running", return_value=True)
        self.patch(_local, "_port_free", return_value=True)
        starter = mock.Mock(side_effect=AssertionError("must not spawn a second emulator"))
        result = _local.ensure_azurite(str(self.project), starter=starter, prober=lambda: None, timeout=0)
        self.assertEqual(result["state"], "failed")
        self.assertTrue(result["startedByCli"])
        self.assertEqual(result["pid"], 480003)
        starter.assert_not_called()
        self.assertEqual(_local.read_azurite_record()["pid"], 480003)

    def test_pending_emulator_that_becomes_ready_is_reported_as_owned(self):
        (self.project / "local.settings.json").write_text(
            json.dumps({"Values": {"AzureWebJobsStorage": "UseDevelopmentStorage=true"}}), encoding="utf-8")
        _local._write_azurite_record({"pid": 480003, "processCreateTimeUtc": "2026-10-06T15:00:00Z"})
        self.patch(_local, "find_tool", return_value=(str(self.root / "azurite.cmd"), "managed"))
        self.patch(_local, "process_create_time_utc", return_value="2026-10-06T15:00:00Z")
        self.patch(_local, "_is_running", return_value=True)
        self.patch(_local, "_port_free", return_value=True)
        prober = mock.Mock(side_effect=[None, "Azurite-Blob/fixture"])
        starter = mock.Mock(side_effect=AssertionError("must not spawn a second emulator"))
        result = _local.ensure_azurite(str(self.project), starter=starter, prober=prober, timeout=0)
        self.assertEqual(result["state"], "already-running")
        self.assertTrue(result["startedByCli"])
        starter.assert_not_called()


class ForegroundConsumerTests(IsolatedRuntimeTest):
    HOST = 480001
    OTHER_HOST = 480002
    STORAGE = 480003
    CHILD = 480004
    CREATION_TIME = "2026-10-06T15:00:00.1234567Z"

    def setUp(self):
        super().setUp()
        self.live = {os.getpid(): self.CREATION_TIME, self.HOST: self.CREATION_TIME,
                     self.OTHER_HOST: self.CREATION_TIME, self.STORAGE: self.CREATION_TIME}
        self.proc = FakeProcess(self.HOST, self.live)
        self.spawn = self.patch(_local.subprocess, "Popen", return_value=self.proc)
        self.patch(_local, "find_tool", return_value=(str(self.root / "func.cmd"), "managed"))
        self.patch(_local, "_port_free", return_value=True)
        self.patch(_local, "_readiness", return_value=(False, False, "fixture"))
        self.patch(_local, "process_create_time_utc", side_effect=lambda pid: self.live.get(pid))
        self.patch(_local, "_is_running", side_effect=lambda pid: pid in self.live)
        self.patch(_local.psutil, "Process", return_value=mock.Mock(children=mock.Mock(return_value=[])))
        self.ensure = self.patch(_local, "ensure_azurite", return_value={"kind": "azurite", "state": "already-running"})
        self.patch(_local, "probe_azurite", return_value=None)
        self.killed = []
        self.patch(_local, "_terminate", side_effect=self.terminate)
        _local._write_azurite_record({"pid": self.STORAGE, "processCreateTimeUtc": self.CREATION_TIME})

    def terminate(self, pid, expected=None):
        self.assertEqual(expected, self.CREATION_TIME)
        self.killed.append(pid)
        self.live.pop(pid, None)

    def start(self, background=False, ready_timeout=0):
        return _local.start_runtime(None, str(self.project), port=17071, background=background,
                                    ready_timeout=ready_timeout)

    def exit_host(self, returncode=0):
        self.live.pop(self.HOST, None)
        self.proc.returncode = returncode
        return returncode

    def test_stopping_background_host_keeps_storage_for_attached_foreground(self):
        self.write_record(17072, self.OTHER_HOST, self.CREATION_TIME)

        def wait(_timeout):
            record = _local._read_record(17071)
            self.assertEqual(record["pid"], self.HOST)
            self.assertEqual(record["consumerPid"], os.getpid())
            result = _local.stop_runtime(17072)
            self.assertEqual(result["azurite"]["reason"], "runtimes-still-running")
            self.assertEqual(result["azurite"]["ports"], [17071])
            self.assertNotIn(self.STORAGE, self.killed)
            return self.exit_host()

        self.proc.on_wait = wait
        result = self.start()
        self.assertEqual(result["status"], "stopped")
        self.assertEqual(self.killed, [self.OTHER_HOST, self.STORAGE])
        self.assertIsNone(_local._read_record(17071))
        self.assertIsNone(_local.read_azurite_record())
        self.assertNotIn("creationflags", self.spawn.call_args.kwargs)
        self.assertNotIn("stdout", self.spawn.call_args.kwargs)
        self.assertIn("env", self.spawn.call_args.kwargs)

    def test_consumer_is_registered_before_storage_acquisition_without_owning_cli_pid(self):
        self.write_record(17072, self.OTHER_HOST, self.CREATION_TIME)

        def ensure(*_args, **_kwargs):
            record = _local._read_record(17071)
            self.assertIsNone(record["pid"])
            self.assertEqual(record["consumerPid"], os.getpid())
            result = _local.stop_runtime(17072)
            self.assertEqual(result["azurite"]["ports"], [17071])
            with self.assertRaises(CLIError):
                _local.stop_runtime(17071)
            self.assertNotIn(os.getpid(), self.killed)
            return None

        self.ensure.side_effect = ensure
        self.proc.on_wait = lambda _timeout: self.exit_host()
        self.assertEqual(self.start()["status"], "stopped")
        self.assertEqual(self.killed, [self.OTHER_HOST, self.STORAGE])

    def test_foreground_nonzero_exit_cleans_record_and_storage(self):
        self.proc.on_wait = lambda _timeout: self.exit_host(2)
        self.assertEqual(self.start()["status"], "failed")
        self.assertIsNone(_local._read_record(17071))
        self.assertEqual(self.killed, [self.STORAGE])

    def test_interrupt_terminates_own_host_and_releases_storage(self):
        self.proc.on_wait = mock.Mock(side_effect=KeyboardInterrupt)
        self.assertEqual(self.start()["status"], "stopped")
        self.assertEqual(self.killed, [self.HOST, self.STORAGE])
        self.assertIsNone(_local._read_record(17071))

    def test_foreground_exit_does_not_stop_unowned_storage(self):
        _local._clear_azurite_record()
        self.proc.on_wait = lambda _timeout: self.exit_host()
        self.assertEqual(self.start()["status"], "stopped")
        self.assertEqual(self.killed, [])

    def test_host_spawn_failure_releases_its_lease_and_owned_storage(self):
        self.spawn.side_effect = OSError("fixture spawn failure")
        with self.assertRaises(CLIError):
            self.start()
        self.assertIsNone(_local._read_record(17071))
        self.assertEqual(self.killed, [self.STORAGE])

    def test_host_spawn_failure_does_not_release_another_consumers_storage(self):
        self.write_record(17072, self.OTHER_HOST, self.CREATION_TIME)
        self.spawn.side_effect = OSError("fixture spawn failure")
        with self.assertRaises(CLIError):
            self.start()
        self.assertIsNone(_local._read_record(17071))
        self.assertIsNotNone(_local.read_azurite_record())
        self.assertEqual(self.killed, [])

    def test_record_write_failure_after_spawn_terminates_child_and_cleans_lease(self):
        real_write = _local._write_record
        calls = []

        def write(port, record):
            calls.append(port)
            if len(calls) == 2:
                raise FileOperationError("fixture write failure")
            return real_write(port, record)

        self.patch(_local, "_write_record", side_effect=write)
        with self.assertRaises(FileOperationError):
            self.start()
        self.assertEqual(self.killed, [self.HOST, self.STORAGE])
        self.assertIsNone(_local._read_record(17071))

    def test_unknown_host_identity_cancels_spawn_using_own_popen_handle(self):
        self.patch(_local, "process_create_time_utc",
                   side_effect=lambda pid: None if pid == self.HOST else self.live.get(pid))
        with self.assertRaises(CLIError):
            self.start()
        self.assertTrue(self.proc.terminated)
        self.assertNotIn(self.HOST, self.killed)
        self.assertEqual(self.killed, [self.STORAGE])
        self.assertIsNone(_local._read_record(17071))

    def test_unknown_identity_failed_cleanup_retains_nonowning_storage_guard(self):
        self.patch(_local, "process_create_time_utc",
                   side_effect=lambda pid: None if pid == self.HOST else self.live.get(pid))
        self.patch(_local.psutil, "pid_exists", side_effect=lambda pid: pid in self.live)
        self.proc.terminate = mock.Mock(side_effect=OSError("fixture cannot terminate child"))
        with self.assertRaises(CLIError):
            self.start()
        record = _local._read_record(17071)
        self.assertTrue(record["cleanupPending"])
        self.assertFalse(_local._record_matches(record))
        self.assertEqual(_local._live_runtime_records(), [17071])
        self.assertIsNotNone(_local.read_azurite_record())
        with self.assertRaises(CLIError):
            _local.stop_runtime(17071)
        self.assertEqual(self.killed, [])

    def test_failed_foreground_cleanup_retains_still_live_child(self):
        self.live[self.CHILD] = self.CREATION_TIME
        child = mock.Mock(pid=self.CHILD)
        child.ppid.return_value = self.HOST
        child.is_running.return_value = True
        self.patch(_local.psutil, "Process", return_value=mock.Mock(children=mock.Mock(return_value=[child])))

        def terminate(pid, expected=None):
            if pid == self.CHILD:
                raise OSError("fixture child refuses termination")
            self.terminate(pid, expected=expected)

        self.patch(_local, "_terminate", side_effect=terminate)
        self.proc.on_wait = lambda _timeout: self.exit_host()
        result = self.start()
        self.assertEqual(result["status"], "failed")
        record = _local._read_record(17071)
        self.assertNotIn("consumerPid", record)
        self.assertEqual(record["childProcesses"][0]["pid"], self.CHILD)
        self.assertEqual(_local._live_runtime_records(), [17071])
        self.assertIsNotNone(_local.read_azurite_record())
        self.assertNotIn(self.STORAGE, self.killed)

    def test_zero_ready_timeout_keeps_live_background_host_record_and_storage(self):
        result = self.start(background=True, ready_timeout=0)
        self.assertEqual(result["status"], "starting")
        record = _local._read_record(17071)
        self.assertEqual(record["pid"], self.HOST)
        self.assertNotIn("consumerPid", record)
        self.assertIsNotNone(_local.read_azurite_record())
        self.assertEqual(self.killed, [])
        self.assertIn("env", self.spawn.call_args.kwargs)
        self.assertTrue(_local.stop_runtime(17071)["azurite"]["stopped"])

    def test_background_start_that_exits_releases_record_and_storage(self):
        self.patch(_local, "_wait_for_ready",
                   side_effect=lambda *_args: (self.exit_host(1) == 0, False, "fixture"))
        result = self.start(background=True)
        self.assertEqual(result["status"], "failed")
        self.assertIsNone(_local._read_record(17071))
        self.assertEqual(self.killed, [self.STORAGE])

    def test_zero_azurite_timeout_keeps_live_launch_record_for_later_cleanup(self):
        _local._clear_azurite_record()
        self.spawn.return_value = FakeProcess(self.STORAGE, self.live)
        record = _local.start_azurite(str(self.root / "azurite.cmd"), timeout=0, prober=lambda: None)
        self.assertIsNone(record["server"])
        self.assertEqual(_local.read_azurite_record()["pid"], self.STORAGE)
        self.assertTrue(_local.stop_azurite()["stopped"])
        self.assertEqual(self.killed, [self.STORAGE])

    def test_storage_probe_exception_cleans_owned_launch(self):
        _local._clear_azurite_record()
        self.spawn.return_value = FakeProcess(self.STORAGE, self.live)
        with self.assertRaises(OSError):
            _local.start_azurite(str(self.root / "azurite.cmd"), timeout=0,
                                 prober=mock.Mock(side_effect=OSError("fixture probe failure")))
        self.assertEqual(self.killed, [self.STORAGE])
        self.assertIsNone(_local.read_azurite_record())


class ChildObservationIdentityTests(IsolatedRuntimeTest):
    PARENT = 780001
    CHILD = 780002
    GRANDCHILD = 780003
    STORAGE = 780004
    CREATED = "2026-10-09T12:00:00.0000000Z"
    REPLACEMENT = "2026-10-09T12:01:00.0000000Z"

    def setUp(self):
        super().setUp()
        self.live = {self.PARENT: self.CREATED, self.CHILD: self.CREATED,
                     self.GRANDCHILD: self.CREATED, self.STORAGE: self.CREATED}
        self.patch(_local, "process_create_time_utc", side_effect=self.live.get)
        self.patch(_local, "_is_running", side_effect=lambda pid: pid in self.live)
        self.patch(_local.psutil, "pid_exists", side_effect=lambda pid: pid in self.live)
        self.parent = mock.Mock(children=mock.Mock(return_value=[]))
        self.patch(_local.psutil, "Process", return_value=self.parent)
        self.record = {"pid": self.PARENT, "processCreateTimeUtc": self.CREATED,
                       "port": 17071, "launchId": "original-launch"}
        self.signal = self.patch(_local, "_terminate", side_effect=AssertionError("No adopted replacement signals"))

    def child(self, pid, parent):
        child = mock.Mock(pid=pid)
        child.ppid.return_value = parent
        child.is_running.return_value = True
        return child

    def test_recycled_root_cannot_authorize_new_descendants_and_preserves_storage_guard(self):
        child = self.child(self.CHILD, self.PARENT)

        def enumerate_replacement(recursive):
            self.assertTrue(recursive)
            self.live[self.PARENT] = self.REPLACEMENT
            self.live[self.CHILD] = self.REPLACEMENT
            return [child]

        self.parent.children.side_effect = enumerate_replacement
        _local._write_record(17071, self.record)
        _local._write_azurite_record({"pid": self.STORAGE, "processCreateTimeUtc": self.CREATED})
        storage = Path(_local._azurite_record_file()).read_bytes()
        _local._remember_runtime_children(self.record)
        observed = self.record["childProcesses"][0]
        self.assertIsNone(observed["processCreateTimeUtc"])
        self.assertTrue(observed["cleanupPending"])
        process = mock.Mock(pid=self.PARENT)
        process.poll.return_value = 0
        _local._terminate_launched_process(process, self.record)
        _local._finish_runtime_record(self.record, process)
        self.signal.assert_not_called()
        self.assertTrue(_local._read_record(17071)["cleanupPending"])
        self.assertEqual([17071], _local._live_runtime_records())
        self.assertEqual(storage, Path(_local._azurite_record_file()).read_bytes())

    def test_child_recycled_before_object_construction_cannot_adopt_unrelated_ancestry(self):
        self.live[self.CHILD] = self.REPLACEMENT
        self.parent.children.return_value = [self.child(self.CHILD, 1)]
        _local._remember_runtime_children(self.record)
        observed = self.record["childProcesses"][0]
        self.assertIsNone(observed["processCreateTimeUtc"])
        self.assertTrue(observed["cleanupPending"])
        self.assertFalse(_local._record_matches(observed))

    def test_child_recycled_after_enumeration_is_not_adopted(self):
        child = self.child(self.CHILD, self.PARENT)
        child.is_running.return_value = False
        self.parent.children.return_value = [child]
        _local._remember_runtime_children(self.record)
        self.assertNotIn("childProcesses", self.record)

    def test_verified_nested_ancestry_adopts_original_creation_identities(self):
        self.parent.children.return_value = [self.child(self.CHILD, self.PARENT),
                                             self.child(self.GRANDCHILD, self.CHILD)]
        _local._remember_runtime_children(self.record)
        self.assertEqual({self.CHILD, self.GRANDCHILD},
                         {item["pid"] for item in self.record["childProcesses"]})
        for child in self.record["childProcesses"]:
            self.assertEqual(self.CREATED, child["processCreateTimeUtc"])
            self.assertNotIn("cleanupPending", child)

    def test_unreadable_child_ancestry_retains_nonowning_cleanup_guard(self):
        child = self.child(self.CHILD, self.PARENT)
        child.ppid.side_effect = psutil.AccessDenied(self.CHILD)
        self.parent.children.return_value = [child]
        _local._remember_runtime_children(self.record)
        observed = self.record["childProcesses"][0]
        self.assertIsNone(observed["processCreateTimeUtc"])
        self.assertTrue(_local._unverified_cleanup_pending(self.record))

    def test_verified_preexisting_process_is_not_adopted_from_a_reused_parent_pid(self):
        self.live[self.PARENT] = self.REPLACEMENT
        self.record["processCreateTimeUtc"] = self.REPLACEMENT
        self.parent.children.return_value = [self.child(self.CHILD, self.PARENT),
                                             self.child(self.GRANDCHILD, self.CHILD)]
        _local._remember_runtime_children(self.record)
        self.assertNotIn("childProcesses", self.record)
        self.signal.assert_not_called()


class WindowsManagedLauncherTests(IsolatedRuntimeTest):
    @unittest.skipUnless(sys.platform == "win32", "Actual npm-generated Windows shim")
    def test_actual_azurite_shim_runs_with_managed_node_on_clean_path(self):
        node = shutil.which("node")
        if not node or Path(node).suffix.lower() != ".exe":
            self.skipTest("A Node.js executable is needed for this isolated shim fixture")
        node_version = subprocess.check_output([node, "--version"], text=True).strip()
        node_major = int(node_version.lstrip("v").split(".", 1)[0])
        managed = self.root / "managed"
        node_dir = managed / "NodeJs"
        launcher_dir = managed / "Azurite"
        node_dir.mkdir(parents=True)
        launcher_dir.mkdir()
        shutil.copyfile(node, node_dir / "node.exe")
        launcher = launcher_dir / "azurite.cmd"

        def shim(path, script):
            path.write_text(
                '@ECHO off\r\nSETLOCAL\r\nSET "dp0=%~dp0"\r\n'
                'IF EXIST "%dp0%node.exe" (SET "_prog=%dp0%node.exe") ELSE (SET "_prog=node")\r\n'
                '"%_prog%" "%dp0%{}" %*\r\n'.format(script), encoding="utf-8")

        shim(launcher, "launcher.js")
        proof = launcher_dir / "node-proof.json"
        (launcher_dir / "launcher.js").write_text(
            "require('fs').writeFileSync({}, JSON.stringify(process.execPath)); "
            "setInterval(() => {{}}, 1000);\n".format(json.dumps(str(proof))), encoding="utf-8")
        npm = node_dir / "npm.cmd"
        shim(npm, "npm.js")
        (node_dir / "npm.js").write_text('console.log("node: \'" + process.versions.node + "\'");',
                                         encoding="utf-8")
        func_dir = managed / "FuncCoreTools"
        func_dir.mkdir()
        func = func_dir / "func.cmd"
        shim(func, "host.js")
        host_proof = func_dir / "host-proof.json"
        host_script = "require('fs').writeFileSync({}, JSON.stringify(process.execPath));\n".format(
            json.dumps(str(host_proof)))
        (func_dir / "host.js").write_text(host_script, encoding="utf-8")
        with mock.patch.dict(os.environ, {"PATH": "", "LA_DEPENDENCIES_PATH": str(managed)}), \
                mock.patch.object(_local, "probe_azurite", return_value=None), \
                mock.patch.object(_local, "ensure_azurite", return_value=None), \
                mock.patch.object(_local, "_readiness", return_value=(False, False, "isolated shim")), \
                warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            self.assertEqual(_dependencies._npm_node_major(str(npm)), node_major)
            record = _local.start_azurite(str(launcher), timeout=0, prober=lambda: None)
            try:
                self.assertIsNone(record["server"])
                self.assertTrue(_local._record_matches(record))
                deadline = time.monotonic() + 10
                while time.monotonic() < deadline and not proof.exists():
                    time.sleep(0.1)
                self.assertEqual(str(node_dir / "node.exe").lower(),
                                 json.loads(proof.read_text(encoding="utf-8")).lower())
                self.assertEqual(os.environ["PATH"], "")
            finally:
                stopped = _local.stop_azurite()
                self.assertTrue(stopped["stopped"], stopped)
            self.assertIsNone(_local.read_azurite_record())
            foreground = _local.start_runtime(None, str(self.project), port=17073)
            self.assertEqual(foreground["status"], "stopped")
            self.assertEqual(json.loads(host_proof.read_text(encoding="utf-8")).lower(),
                             str(node_dir / "node.exe").lower())
            host_proof.unlink()
            (func_dir / "host.js").write_text(host_script + "setInterval(() => {}, 1000);\n", encoding="utf-8")
            background = _local.start_runtime(None, str(self.project), port=17074, background=True, ready_timeout=0)
            try:
                self.assertEqual(background["status"], "starting")
                deadline = time.monotonic() + 10
                while time.monotonic() < deadline and not host_proof.exists():
                    time.sleep(0.1)
                self.assertEqual(json.loads(host_proof.read_text(encoding="utf-8")).lower(),
                                 str(node_dir / "node.exe").lower())
                self.assertEqual(os.environ["PATH"], "")
            finally:
                self.assertEqual(len(_local.stop_runtime(17074)["stopped"]), 1)


if __name__ == "__main__":
    unittest.main()
