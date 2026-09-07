# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import io
import json
import os
import copy
import re
import tempfile
import unittest
import zipfile
from types import SimpleNamespace
from unittest import mock

from azure.cli.core.azclierror import (
    AzureResponseError,
    CLIInternalError,
    InvalidArgumentValueError,
    RequiredArgumentMissingError,
)
from knack.util import CLIError

from azext_migrate.shared import arm_ids
from azext_migrate.shared import arm_client as arm_client_mod
from azext_migrate.shared import files
from azext_migrate.shared.arm_client import ArmClient
from azext_migrate.shared.constants import WAVE_OPERATIONS_API_VERSION
from azext_migrate.runbook import models, transformers
from azext_migrate.runbook import deps as deps_mod
from azext_migrate.runbook import config_status as config_status_mod
from azext_migrate.runbook import validators as validators_mod
from azext_migrate.runbook.cmds import runbook as runbook_cmds
from azext_migrate.runbook.cmds import definition as definition_cmds
from azext_migrate.runbook.cmds import definition_step as step_cmds
from azext_migrate.runbook.cmds import (
    definition_workstream as workstream_cmds,
)
from azext_migrate.runbook.cmds import execution as execution_cmds
from azext_migrate.runbook.cmds import execution_step as execution_step_cmds
from azext_migrate.runbook.cmds import parameter as parameter_cmds
from azext_migrate.runbook.cmds import (
    execution_parameter as execution_parameter_cmds)
from azext_migrate.runbook.visualize import graph as visualize_graph
from azext_migrate.runbook.visualize import renderer as visualize_renderer
from azext_migrate.runbook.visualize import viewmodel as visualize_viewmodel
from azext_migrate.runbook.configure import renderer as configure_renderer
from azext_migrate.runbook.constants import (
    SCOPE_TYPE_WAVE,
    RUNBOOK_STATUS_VALUES,
)
from azext_migrate.runbook.models import ExecutionAction
from azext_migrate.runbook.validators import (
    validate_generate,
    validate_step_approve,
    validate_step_complete,
)

SUB = "00000000-0000-0000-0000-000000000000"
RG = "myRg"
PROJECT = "myProject"
RUNBOOK = "myRunbook"
ARTIFACT = "rb-art-1"
WAVE = "myWave"


class RunbookArmIdTests(unittest.TestCase):

    def test_migrate_project_id(self):
        project = arm_ids.migrate_project_id(SUB, RG, PROJECT)
        self.assertEqual(
            project,
            f"/subscriptions/{SUB}/resourceGroups/{RG}/providers/"
            f"Microsoft.Migrate/migrateProjects/{PROJECT}")

    def test_runbook_id(self):
        project = arm_ids.migrate_project_id(SUB, RG, PROJECT)
        self.assertEqual(
            arm_ids.runbook_id(project, RUNBOOK),
            f"{project}/runbooks/{RUNBOOK}")

    def test_with_api_version_no_query(self):
        self.assertEqual(
            arm_ids.with_api_version("/a/b", "2020-06-01-preview"),
            "/a/b?api-version=2020-06-01-preview")

    def test_with_api_version_existing_query(self):
        self.assertEqual(
            arm_ids.with_api_version("/a/b?x=1", "2020-06-01-preview"),
            "/a/b?x=1&api-version=2020-06-01-preview")


class RunbookModelTests(unittest.TestCase):

    def test_wave_id(self):
        project = arm_ids.migrate_project_id(SUB, RG, PROJECT)
        self.assertEqual(
            models.wave_id(project, WAVE),
            f"{project}/waves/{WAVE}")

    def test_build_generate_body(self):
        body = models.build_generate_body("/waves/myWave")
        self.assertEqual(
            body,
            {"properties": {"scope": {
                "scopeType": SCOPE_TYPE_WAVE,
                "waveId": "/waves/myWave"}}})

    def test_build_update_body_empty(self):
        self.assertEqual(
            models.build_update_body(), {"properties": {}})

    def test_build_update_body_with_description(self):
        self.assertEqual(
            models.build_update_body(description="new desc"),
            {"properties": {"description": "new desc"}})


class RunbookTransformerTests(unittest.TestCase):

    def test_single_runbook(self):
        item = {"name": RUNBOOK, "properties": {"state": "Ready"}}
        row = transformers.runbook_table(item)
        self.assertEqual(row["Name"], RUNBOOK)
        self.assertEqual(row["State"], "Ready")

    def test_runbook_list(self):
        items = [
            {"name": "r1", "properties": {"state": "Ready"}},
            {"name": "r2", "properties": {"state": "Generating"}},
        ]
        rows = transformers.runbook_table(items)
        self.assertEqual([r["Name"] for r in rows], ["r1", "r2"])

    def test_missing_properties(self):
        row = transformers.runbook_table({"name": "r1"})
        self.assertIsNone(row["State"])


class RunbookValidatorTests(unittest.TestCase):

    def test_validate_generate_ok(self):
        validate_generate(SimpleNamespace(wave_name=WAVE))

    def test_validate_generate_missing_wave(self):
        with self.assertRaises(RequiredArgumentMissingError):
            validate_generate(SimpleNamespace(wave_name=None))


class RunbookStatusChoiceTests(unittest.TestCase):

    def test_status_values(self):
        self.assertEqual(
            RUNBOOK_STATUS_VALUES,
            ["Generating", "NotConfigured", "ReadyToStart", "InExecution",
             "Paused", "Completed", "Failed"])


def _fake_response(status_code, headers=None, body=None):
    resp = mock.Mock()
    resp.status_code = status_code
    resp.headers = headers or {}
    resp.content = b'{}' if body is not None else b''
    resp.json.return_value = body if body is not None else {}
    return resp


def _arm_client():
    cmd = mock.Mock()
    cmd.cli_ctx.cloud.endpoints.resource_manager = (
        "https://management.azure.com")
    return ArmClient(cmd)


class ArmClientPollApiVersionTests(unittest.TestCase):

    def test_rewrites_waveoperations_api_version(self):
        url = ("https://management.azure.com/subscriptions/s/providers/"
               "Microsoft.Migrate/migrateProjects/p/WaveOperations/op"
               "?api-version=2020-06-01-preview&c=SIG&s=SIG2")
        rewritten = arm_client_mod._rewrite_poll_api_version(url)
        self.assertIn(
            "api-version=" + WAVE_OPERATIONS_API_VERSION, rewritten)
        self.assertNotIn("api-version=2020-06-01-preview", rewritten)
        # Signed token must be preserved untouched.
        self.assertIn("&c=SIG&s=SIG2", rewritten)

    def test_rewrites_any_poll_url_api_version(self):
        url = "https://x/operationstatus/o?api-version=2020-06-01-preview"
        rewritten = arm_client_mod._rewrite_poll_api_version(url)
        self.assertEqual(
            rewritten,
            "https://x/operationstatus/o?api-version="
            + WAVE_OPERATIONS_API_VERSION)

    def test_appends_api_version_when_missing(self):
        url = "https://x/operationstatus/o"
        rewritten = arm_client_mod._rewrite_poll_api_version(url)
        self.assertEqual(
            rewritten,
            "https://x/operationstatus/o?api-version="
            + WAVE_OPERATIONS_API_VERSION)


class ArmClientLroTests(unittest.TestCase):

    def setUp(self):
        sleep_patch = mock.patch.object(arm_client_mod._time, 'sleep')
        self.addCleanup(sleep_patch.stop)
        sleep_patch.start()
        send_patch = mock.patch.object(
            arm_client_mod, 'send_raw_request')
        self.addCleanup(send_patch.stop)
        self.send = send_patch.start()

    def test_delete_polls_until_succeeded(self):
        async_url = ("https://management.azure.com/.../WaveOperations/op"
                     "?api-version=2020-06-01-preview")
        accepted = _fake_response(
            201, headers={'Azure-AsyncOperation': async_url},
            body={"properties": {"state": "ExecutionSucceeded"}})
        running = _fake_response(200, body={"status": "Running"})
        done = _fake_response(200, body={"status": "Succeeded"})
        self.send.side_effect = [accepted, running, done]

        result = _arm_client().delete("/runbooks/r")

        # A completed delete renders nothing (not the stale accepted body).
        self.assertIsNone(result)
        # Initial DELETE + two status polls.
        self.assertEqual(self.send.call_count, 3)
        polled_url = self.send.call_args_list[1][0][2]
        self.assertIn(
            "api-version=" + WAVE_OPERATIONS_API_VERSION, polled_url)

    def test_poll_uses_async_uri_as_is_when_rewrite_disabled(self):
        async_url = ("https://management.azure.com/.../operationStatuses/op"
                     "?api-version=2026-06-01-preview")
        accepted = _fake_response(
            202, headers={'Azure-AsyncOperation': async_url}, body={})
        done = _fake_response(
            200, body={"status": "Succeeded",
                       "properties": {"sasUrl": "https://blob/x"}})
        self.send.side_effect = [accepted, done]

        cmd = mock.Mock()
        cmd.cli_ctx.cloud.endpoints.resource_manager = (
            "https://management.azure.com")
        client = ArmClient(cmd, rewrite_poll_api_version=False)
        result = client.post_action(
            "/artifacts/a", 'generateDownloadUrl', {},
            return_final_poll=True)

        self.assertEqual(
            (result.get("properties") or {}).get("sasUrl"),
            "https://blob/x")
        polled_url = self.send.call_args_list[1][0][2]
        self.assertIn("api-version=2026-06-01-preview", polled_url)
        self.assertNotIn(WAVE_OPERATIONS_API_VERSION, polled_url)

    def test_delete_raises_on_failed_operation(self):
        async_url = ("https://management.azure.com/.../WaveOperations/op"
                     "?api-version=2020-06-01-preview")
        accepted = _fake_response(
            202, headers={'Azure-AsyncOperation': async_url}, body={})
        failed = _fake_response(200, body={
            "status": "Failed",
            "error": {"code": "BadThing", "message": "it broke"}})
        self.send.side_effect = [accepted, failed]

        with self.assertRaises(AzureResponseError):
            _arm_client().delete("/runbooks/r")

    def test_delete_no_wait_skips_polling(self):
        async_url = "https://x/WaveOperations/op?api-version=x"
        accepted = _fake_response(
            202, headers={'Azure-AsyncOperation': async_url}, body={})
        self.send.side_effect = [accepted]

        _arm_client().delete("/runbooks/r", no_wait=True)

        self.assertEqual(self.send.call_count, 1)

    def test_list_reroutes_foreign_next_link_to_arm(self):
        # Migrate paging can return a nextLink on an internal backend host;
        # called directly it 500s (missing partition-key header). list()
        # must re-route the follow-up page through the ARM endpoint.
        page1 = _fake_response(200, body={
            "value": [{"name": "a"}],
            "nextLink": (
                "https://wave.ecy.prod.migration.windowsazure.com"
                "/subscriptions/s/resourceGroups/rg/providers/"
                "Microsoft.Migrate/migrateProjects/p/runbooks"
                "?api-version=2020-06-01-preview&continuationToken=TOKEN")})
        page2 = _fake_response(200, body={"value": [{"name": "b"}]})
        self.send.side_effect = [page1, page2]

        items = _arm_client().list("/runbooks")

        self.assertEqual([i["name"] for i in items], ["a", "b"])
        page2_url = self.send.call_args_list[1][0][2]
        self.assertTrue(page2_url.startswith("https://management.azure.com/"))
        self.assertIn("continuationToken=TOKEN", page2_url)
        self.assertNotIn("windowsazure.com", page2_url)


class RunbookWaitTests(unittest.TestCase):

    def setUp(self):
        sub_patch = mock.patch.object(
            runbook_cmds, 'get_subscription_id', return_value=SUB)
        self.addCleanup(sub_patch.stop)
        sub_patch.start()
        sleep_patch = mock.patch.object(runbook_cmds.time, 'sleep')
        self.addCleanup(sleep_patch.stop)
        sleep_patch.start()
        client_patch = mock.patch.object(runbook_cmds, 'ArmClient')
        self.addCleanup(client_patch.stop)
        self.client = client_patch.start().return_value

    def _wait(self, **kwargs):
        return runbook_cmds.wait(
            mock.Mock(), RG, PROJECT, RUNBOOK, **kwargs)

    def test_requires_a_condition(self):
        with self.assertRaises(InvalidArgumentValueError):
            self._wait()

    def test_created_returns_when_succeeded(self):
        self.client.get_or_none.return_value = {
            "properties": {"provisioningState": "Succeeded"}}
        self.assertIsNone(self._wait(created=True))
        self.assertEqual(self.client.get_or_none.call_count, 1)

    def test_deleted_returns_when_absent(self):
        self.client.get_or_none.return_value = None
        self.assertIsNone(self._wait(deleted=True))

    def test_exists_returns_when_present(self):
        self.client.get_or_none.return_value = {"properties": {}}
        self.assertIsNone(self._wait(exists=True))

    def test_failed_provisioning_raises(self):
        self.client.get_or_none.return_value = {
            "properties": {"provisioningState": "Failed"}}
        with self.assertRaises(AzureResponseError):
            self._wait(created=True)

    def test_custom_condition_met(self):
        self.client.get_or_none.return_value = {
            "properties": {"state": "ExecutionSucceeded"}}
        self.assertIsNone(self._wait(
            custom="properties.state=='ExecutionSucceeded'"))

    def test_times_out_when_never_satisfied(self):
        self.client.get_or_none.return_value = {
            "properties": {"provisioningState": "InProgress"}}
        with self.assertRaises(CLIError):
            self._wait(created=True, interval=1, timeout=2)


class RunbookUpdateRegenerateTests(unittest.TestCase):

    def setUp(self):
        sub_patch = mock.patch.object(
            runbook_cmds, 'get_subscription_id', return_value=SUB)
        self.addCleanup(sub_patch.stop)
        sub_patch.start()
        client_patch = mock.patch.object(runbook_cmds, 'ArmClient')
        self.addCleanup(client_patch.stop)
        self.client = client_patch.start().return_value

    def _runbook_id(self):
        project = arm_ids.migrate_project_id(SUB, RG, PROJECT)
        return arm_ids.runbook_id(project, RUNBOOK)

    def test_update_calls_patch_with_body(self):
        self.client.patch.return_value = {"ok": True}
        result = runbook_cmds.update(
            mock.Mock(), RG, PROJECT, RUNBOOK, description="d")
        self.assertEqual(result, {"ok": True})
        self.client.patch.assert_called_once_with(
            self._runbook_id(), {"properties": {"description": "d"}})

    def test_regenerate_deletes_then_regenerates(self):
        wave_id = (arm_ids.migrate_project_id(SUB, RG, PROJECT)
                   + '/waves/wave-1')
        self.client.get.return_value = {
            "properties": {"scope": {
                "scopeType": "Wave", "waveId": wave_id}}}
        self.client.put.return_value = {"ok": True}
        result = runbook_cmds.regenerate(
            mock.Mock(), RG, PROJECT, RUNBOOK, no_wait=True)
        self.assertEqual(result, {"ok": True})
        self.client.get.assert_called_once_with(self._runbook_id())
        self.client.delete.assert_called_once_with(self._runbook_id())
        self.client.put.assert_called_once_with(
            self._runbook_id(),
            models.build_generate_body(wave_id),
            no_wait=True)

    def test_regenerate_raises_without_scope(self):
        self.client.get.return_value = {"properties": {}}
        with self.assertRaises(CLIError):
            runbook_cmds.regenerate(mock.Mock(), RG, PROJECT, RUNBOOK)

    def test_regenerate_opens_definition_view_by_default(self):
        wave_id = (arm_ids.migrate_project_id(SUB, RG, PROJECT)
                   + '/waves/w')
        self.client.get.return_value = {
            "properties": {"scope": {"waveId": wave_id}}}
        self.client.put.return_value = {"ok": True}
        with mock.patch.object(
                runbook_cmds, '_open_definition_view') as ov:
            runbook_cmds.regenerate(mock.Mock(), RG, PROJECT, RUNBOOK)
        ov.assert_called_once()

    def test_regenerate_no_visualize_skips_view(self):
        wave_id = (arm_ids.migrate_project_id(SUB, RG, PROJECT)
                   + '/waves/w')
        self.client.get.return_value = {
            "properties": {"scope": {"waveId": wave_id}}}
        self.client.put.return_value = {"ok": True}
        with mock.patch.object(
                runbook_cmds, '_open_definition_view') as ov:
            runbook_cmds.regenerate(
                mock.Mock(), RG, PROJECT, RUNBOOK, no_visualize=True)
        ov.assert_not_called()


class RunbookDefinitionTransformerTests(unittest.TestCase):

    def test_workstreams_flattened_to_steps(self):
        definition = {"workstreams": [
            {"id": "w1", "steps": [
                {"stepId": "s1", "displayName": "Step One",
                 "prerequisites": [{"stepId": "b"}],
                 "dependsOn": [{"stepId": "a"}],
                 "configurationStatus": "Configured",
                 "entities": ["e1", "e2"]}]},
            {"id": "w2", "steps": [{"stepId": "s2"}]},
        ]}
        rows = transformers.definition_table(definition)
        self.assertEqual([r["Step Id"] for r in rows], ["s1", "s2"])
        self.assertEqual([r["Workstream Id"] for r in rows], ["w1", "w2"])
        self.assertEqual(rows[0]["Step Name"], "Step One")
        self.assertEqual(rows[0]["Depends On"], "b\na")
        self.assertEqual(rows[0]["Configuration Status"], "Configured")
        self.assertEqual(rows[0]["Entities"], 2)
        self.assertEqual(rows[0]["Applications"], 0)

    def test_applications_count_from_affected_entity_groups(self):
        definition = {
            "workstreams": [{"id": "w1", "steps": [
                {"stepId": "s1",
                 "affectedEntityGroups": ["group-app", "group-db"]},
                {"stepId": "s2", "affectedEntityGroups": ["group-app"]},
                {"stepId": "s3"}]}]}
        rows = transformers.definition_table(definition)
        self.assertEqual(rows[0]["Applications"], 2)
        self.assertEqual(rows[1]["Applications"], 1)
        self.assertEqual(rows[2]["Applications"], 0)

    def test_single_workstream(self):
        rows = transformers.definition_table(
            {"id": "w1", "steps": [{"id": "s1"}]})
        self.assertEqual([r["Step Id"] for r in rows], ["s1"])
        self.assertEqual(rows[0]["Workstream Id"], "w1")

    def test_single_step(self):
        rows = transformers.definition_table({"stepId": "s9"})
        self.assertEqual(rows[0]["Step Id"], "s9")

    def test_empty_workstream_still_shows_a_row(self):
        rows = transformers.definition_table({"workstreams": [
            {"id": "w1", "steps": [{"stepId": "s1"}]},
            {"id": "w-empty", "displayName": "Unmapped", "steps": []},
        ]})
        self.assertEqual(
            [r["Workstream Id"] for r in rows], ["w1", "w-empty"])
        empty = rows[1]
        self.assertEqual(empty["Step Id"], "")
        self.assertEqual(empty["Step Name"], "(no steps)")

    def test_empty_definition(self):
        self.assertEqual(transformers.definition_table({}), [])

    def test_parameters_document_does_not_fabricate_row(self):
        # A parameters/inputs document must never be rendered as a single
        # bogus step row (regression: -o table showed one empty 3-column
        # row when the parameters file was mis-selected as the definition).
        params = {"runbookInputs": {
            "schema": {"vm.agentless.setup": {}},
            "stepInputs": {"vm.agentless.setup-1": {}}}}
        self.assertEqual(transformers.definition_table(params), [])


class DefinitionProjectionTests(unittest.TestCase):

    def setUp(self):
        self.definition = {"workstreams": [
            {"id": "w1", "steps": [{"id": "s1"}, {"stepId": "s2"}]},
            {"id": "w2", "steps": [{"id": "s3"}]},
        ]}

    def test_full_definition_returned(self):
        result = definition_cmds._project_definition(
            self.definition, None, None)
        self.assertEqual(result, self.definition)

    def test_filter_by_workstream(self):
        result = definition_cmds._project_definition(
            self.definition, "w2", None)
        self.assertEqual(result["id"], "w2")

    def test_filter_by_step_id(self):
        result = definition_cmds._project_definition(
            self.definition, None, "s2")
        self.assertEqual(result["stepId"], "s2")

    def test_step_id_no_match(self):
        result = definition_cmds._project_definition(
            self.definition, None, "missing")
        self.assertEqual(result, {})

    def test_workstream_no_match(self):
        result = definition_cmds._project_definition(
            self.definition, "missing", None)
        self.assertEqual(result, {})


def _make_zip(members):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as archive:
        for name, content in members.items():
            archive.writestr(name, content)
    return buffer.getvalue()


class FilesTests(unittest.TestCase):

    def test_extract_sas_url_top_level(self):
        self.assertEqual(
            files.extract_sas_url({"downloadUrl": "https://x"}),
            "https://x")

    def test_extract_sas_url_in_properties(self):
        self.assertEqual(
            files.extract_sas_url(
                {"properties": {"sasUri": "https://y"}}),
            "https://y")

    def test_extract_sas_url_none(self):
        self.assertIsNone(files.extract_sas_url({"other": 1}))

    def test_read_spec_json_prefers_spec_suffix(self):
        zip_bytes = _make_zip({
            "extra.json": '{"a": 1}',
            "rb-x-spec.json": '{"spec": {"id": "r"}}',
        })
        spec = files.read_spec_json(zip_bytes)
        self.assertEqual(spec, {"spec": {"id": "r"}})

    def test_read_status_json_raw_status_doc(self):
        raw = json.dumps({"state": "InProgress"}).encode('utf-8')
        self.assertEqual(
            files.read_status_json(raw), {"state": "InProgress"})

    def test_read_status_json_raw_rejects_parameters(self):
        raw = json.dumps({"inputs": {"schema": {}}}).encode('utf-8')
        with self.assertRaises(CLIInternalError):
            files.read_status_json(raw)

    def test_read_status_json_zip_prefers_status_member(self):
        zip_bytes = _make_zip({
            "spec.json": '{"runbookSpec": {"workstreams": []}}',
            "inputs.json": '{"runbookInputs": {"schema": {}}}',
            "executionStatus.json": '{"workstreams": [{"steps": []}]}',
        })
        self.assertEqual(
            files.read_status_json(zip_bytes),
            {"workstreams": [{"steps": []}]})

    def test_read_status_json_zip_inputs_only_raises(self):
        # A not-yet-run execution archive (definition + parameters, no
        # status) must not be mistaken for a status document.
        zip_bytes = _make_zip({
            "spec.json": '{"spec": {"workstreams": []}}',
            "inputs.json": '{"inputs": {"schema": {}}}',
            "system-derived-inputs.json": '{"inputs": {"schema": {}}}',
        })
        with self.assertRaises(CLIInternalError):
            files.read_status_json(zip_bytes)

    def test_extract_definition_files_flattens_hostile_path(self):
        # Zip-slip is designed out: a member with a traversal path is
        # written by its base name, staying inside the destination.
        zip_bytes = _make_zip({
            "runbook.json": '{"runbookSpec": {}}',
            "../../evil.md": "# bad",
        })
        with tempfile.TemporaryDirectory() as tmp:
            written = files.extract_definition_files(zip_bytes, tmp)
            for path in written:
                self.assertEqual(
                    os.path.commonpath([tmp, os.path.abspath(path)]), tmp)
            self.assertTrue(os.path.isfile(os.path.join(tmp, "evil.md")))

    def test_extract_definition_files_round_trip(self):
        zip_bytes = _make_zip({
            "rb-x-spec.json": '{"spec": {"workstreams": []}}',
            "rb-x-input.json": '{"inputs": {"a": 1}}',
            "docs/readme.md": "# hello",
        })
        with tempfile.TemporaryDirectory() as tmp:
            written = files.extract_definition_files(zip_bytes, tmp)
            self.assertEqual(len(written), 3)
            for path in written:
                self.assertTrue(os.path.isfile(path))
            self.assertEqual(
                sorted(os.path.basename(p) for p in written),
                ["rb-x-input.json", "rb-x-spec.json", "readme.md"])
            with open(os.path.join(tmp, "readme.md")) as handle:
                self.assertEqual(handle.read(), "# hello")

    def test_extract_definition_files_flattens_paths(self):
        zip_bytes = _make_zip({
            "../evil-spec.json": '{"spec": {}}',
            "../../notes.md": "# n",
        })
        with tempfile.TemporaryDirectory() as tmp:
            written = files.extract_definition_files(zip_bytes, tmp)
            self.assertEqual(len(written), 2)
            for path in written:
                self.assertTrue(os.path.isfile(path))
                self.assertEqual(
                    os.path.dirname(os.path.abspath(path)),
                    os.path.abspath(tmp))

    def test_extract_parameters_file_by_content(self):
        zip_bytes = _make_zip({
            "runbook.json": '{"spec": {}}',
            "user-inputs.json": '{"inputs": {"stepInputs": {}}}',
        })
        name, data = files.extract_parameters_file(zip_bytes)
        self.assertEqual(name, "user-inputs.json")
        self.assertIn(b"inputs", data)

    def test_extract_parameters_file_none_when_only_spec(self):
        zip_bytes = _make_zip({"rb-x-spec.json": '{"runbookSpec": {}}'})
        self.assertIsNone(files.extract_parameters_file(zip_bytes))

    def test_read_spec_json_selects_spec_by_content(self):
        # The service members carry no -spec.json suffix, so selection must
        # fall back to content (name-agnostic) rather than a filename match,
        # ensuring the parameters file is never returned as the definition.
        for members in (
                {"user-inputs.json": '{"inputs": {"schema": {}}}',
                 "runbook.json":
                     '{"spec": {"workstreams": []}}'},
                {"runbook.json":
                     '{"spec": {"workstreams": []}}',
                 "user-inputs.json": '{"inputs": {"schema": {}}}'}):
            spec = files.read_spec_json(_make_zip(members))
            self.assertIn("spec", spec)
            self.assertIn("workstreams", spec["spec"])

    def test_read_spec_json_none_when_only_parameters(self):
        zip_bytes = _make_zip({
            "user-inputs.json":
                '{"runbookInputs": {"stepInputs": {}}}'})
        self.assertIsNone(files.read_spec_json(zip_bytes))

    def test_describe_archive_reports_member_roles(self):
        zip_bytes = _make_zip({
            "spec.json": '{"spec": {"workstreams": []}}',
            "inputs.json": '{"inputs": {"schema": {}}}',
            "runbook.md": "# docs"})
        summary = files.describe_archive(zip_bytes)
        self.assertIn('spec.json (definition)', summary)
        self.assertIn('inputs.json (parameters)', summary)
        self.assertIn('runbook.md (docs)', summary)

    def test_describe_archive_flags_unrecognized_member(self):
        # A stale/mismatched contract (old runbookSpec key) is not a spec.
        zip_bytes = _make_zip({
            "runbook.json": '{"runbookSpec": {"workstreams": []}}'})
        self.assertIn('runbook.json (unrecognized)',
                      files.describe_archive(zip_bytes))

    def test_describe_archive_raw_blob(self):
        self.assertEqual(
            files.describe_archive(b'{"spec": {}}'), 'raw non-archive blob')

    def test_extract_parameters_selects_inputs_by_content(self):
        # Mirror of the spec test: the params file must win over the spec
        # regardless of member ordering or non-standard names.
        for members in (
                {"runbook.json":
                 '{"spec": {"workstreams": []}}',
                 "user-inputs.json":
                 '{"inputs": {"schema": {}}}'},
                {"user-inputs.json":
                 '{"inputs": {"schema": {}}}',
                 "runbook.json":
                 '{"spec": {"workstreams": []}}'}):
            name, data = files.extract_parameters_file(_make_zip(members))
            self.assertEqual(name, "user-inputs.json")
            self.assertIn("inputs", json.loads(data.decode()))

    def test_read_parameters_json_by_content(self):
        zip_bytes = _make_zip({
            "runbook.json": '{"spec": {"workstreams": []}}',
            "user-inputs.json":
                '{"inputs": {"stepInputs": {"s1": {}}}}'})
        params = files.read_parameters_json(zip_bytes)
        self.assertEqual(params, {"stepInputs": {"s1": {}}})

    def test_parameters_excludes_derived_input(self):
        # The real archive ships spec.json (spec), inputs.json and
        # system-derived-inputs.json (both runbookInputs-shaped). Only the
        # user inputs file is the parameters file; the derived inputs must
        # never be selected.
        zip_bytes = _make_zip({
            "spec.json": '{"spec": {"workstreams": []}}',
            "system-derived-inputs.json":
                '{"inputs": {"stepInputs": {"d": {}}}}',
            "inputs.json":
                '{"inputs": {"stepInputs": {"u": {}}}}'})
        name, data = files.extract_parameters_file(zip_bytes)
        self.assertEqual(name, "inputs.json")
        self.assertEqual(
            files.read_parameters_json(zip_bytes), {"stepInputs": {"u": {}}})
        self.assertNotIn("derived", data.decode())

    def test_read_spec_ignores_input_documents(self):
        zip_bytes = _make_zip({
            "system-derived-inputs.json": '{"inputs": {"schema": {}}}',
            "inputs.json": '{"inputs": {"schema": {}}}',
            "spec.json":
                '{"spec": {"workstreams": [{"id": "w1"}]}}'})
        spec = files.read_spec_json(zip_bytes)
        self.assertIn("spec", spec)

    def test_extract_definition_files_includes_inputs_not_derived(self):
        zip_bytes = _make_zip({
            "spec.json": '{"spec": {"workstreams": []}}',
            "inputs.json": '{"inputs": {}}',
            "system-derived-inputs.json": '{"inputs": {}}',
            "runbook.md": "# docs",
        })
        with tempfile.TemporaryDirectory() as tmp:
            written = files.extract_definition_files(zip_bytes, tmp)
            names = sorted(os.path.basename(p) for p in written)
            self.assertEqual(
                names, ["inputs.json", "runbook.md", "spec.json"])
            self.assertTrue(
                os.path.exists(os.path.join(tmp, "inputs.json")))
            self.assertFalse(
                os.path.exists(
                    os.path.join(tmp, "system-derived-inputs.json")))

    def test_read_spec_json_accepts_raw_blob(self):
        raw = b'{"runbookSpec": {"workstreams": [{"id": "w1"}]}}'
        self.assertEqual(
            files.read_spec_json(raw),
            {"runbookSpec": {"workstreams": [{"id": "w1"}]}})

    def test_extract_parameters_file_none_for_raw_blob(self):
        self.assertIsNone(
            files.extract_parameters_file(b'{"runbookSpec": {}}'))

    def test_extract_definition_files_writes_raw_blob(self):
        raw = b'{"runbookSpec": {"workstreams": []}}'
        with tempfile.TemporaryDirectory() as tmp:
            written = files.extract_definition_files(raw, tmp)
            self.assertEqual(
                [os.path.basename(p) for p in written], ["runbook.json"])
            with open(written[0], "rb") as handle:
                self.assertEqual(handle.read(), raw)


class DefinitionCommandTests(unittest.TestCase):

    def setUp(self):
        sub_patch = mock.patch.object(
            definition_cmds, 'get_subscription_id', return_value=SUB)
        self.addCleanup(sub_patch.stop)
        sub_patch.start()
        client_patch = mock.patch.object(definition_cmds, 'ArmClient')
        self.addCleanup(client_patch.stop)
        self.client = client_patch.start().return_value

    def _runbook_id(self):
        project = arm_ids.migrate_project_id(SUB, RG, PROJECT)
        return arm_ids.runbook_id(project, RUNBOOK)

    def test_show_projects_runbook_spec(self):
        self.client.get.return_value = {
            "properties": {"artifactId": ARTIFACT}}
        self.client.post_action.return_value = {
            "downloadUrl": "https://blob/x"}
        zip_bytes = _make_zip({
            "rb-x-spec.json":
                '{"spec": {"workstreams": '
                '[{"id": "w1", "steps": []}]}}'})
        with mock.patch.object(
                definition_cmds.files, 'download_bytes',
                return_value=zip_bytes) as dl:
            result = definition_cmds.show(
                mock.Mock(), RG, PROJECT, RUNBOOK, workstream_id="w1")
        dl.assert_called_once_with("https://blob/x")
        project = arm_ids.migrate_project_id(SUB, RG, PROJECT)
        self.client.post_action.assert_called_once_with(
            arm_ids.artifact_id(project, ARTIFACT), 'generateDownloadUrl',
            {"mode": "Directory"},
            return_final_poll=True)
        self.assertEqual(result["id"], "w1")

    def test_show_raises_without_download_url(self):
        self.client.post_action.return_value = {"expiresAt": "t"}
        with self.assertRaises(CLIInternalError):
            definition_cmds.show(mock.Mock(), RG, PROJECT, RUNBOOK)

    def test_show_raises_when_no_definition_in_archive(self):
        self.client.get.return_value = {
            "properties": {"artifactId": ARTIFACT}}
        self.client.post_action.return_value = {
            "downloadUrl": "https://blob/x"}
        zip_bytes = _make_zip({"user-inputs.json": '{"runbookInputs": {}}'})
        with mock.patch.object(
                definition_cmds.files, 'download_bytes',
                return_value=zip_bytes):
            with self.assertRaises(CLIInternalError):
                definition_cmds.show(mock.Mock(), RG, PROJECT, RUNBOOK)

    def test_show_uses_full_artifact_arm_id_as_is(self):
        full_id = (
            "/subscriptions/other/resourceGroups/rg2/providers"
            "/Microsoft.Migrate/migrateProjects/p2/artifacts/art9")
        self.client.get.return_value = {
            "properties": {"artifactId": full_id}}
        self.client.post_action.return_value = {
            "downloadUrl": "https://blob/x"}
        with mock.patch.object(
                definition_cmds.files, 'download_bytes',
                return_value=_make_zip({
                    "s.json": '{"spec": {"workstreams": []}}'})):
            definition_cmds.show(mock.Mock(), RG, PROJECT, RUNBOOK)
        called_id = self.client.post_action.call_args[0][0]
        self.assertEqual(called_id, full_id)

    def test_download_writes_files(self):
        self.client.post_action.return_value = {
            "downloadUrl": "https://blob/x"}
        with mock.patch.object(
                definition_cmds.files, 'download_bytes',
                return_value=b'zip'), \
                mock.patch.object(
                definition_cmds.files, 'extract_definition_files',
                return_value=["/tmp/runbook.json", "/tmp/readme.md"]) as ex:
            result = definition_cmds.download(
                mock.Mock(), RG, PROJECT, RUNBOOK, destination="/tmp")
        ex.assert_called_once_with(b'zip', "/tmp")
        self.assertEqual(result, [
            {"kind": "definition", "path": "/tmp/runbook.json"},
            {"kind": "documentation", "path": "/tmp/readme.md"},
        ])


class StepModelTests(unittest.TestCase):

    def test_build_add_step_body_manual(self):
        body = models.build_add_step_body("Manual", "Step 1", "ws1")
        self.assertEqual(body, {
            "workstreamId": "ws1",
            "displayName": "Step 1",
            "description": "",
            "stepRef": "common.manual",
            "dependsOn": [],
        })

    def test_build_add_step_body_approval(self):
        body = models.build_add_step_body(
            "Approval", "Approve", "ws1",
            depends_on=["s0"], step_description="desc",
            migration_entity_ids=["e1", "e2"])
        self.assertEqual(body, {
            "workstreamId": "ws1",
            "displayName": "Approve",
            "description": "desc",
            "stepRef": "common.approval",
            "dependsOn": [{"waitFor": "Step", "stepId": "s0"}],
            "entities": ["e1", "e2"],
        })

    def test_build_update_step_body_minimal(self):
        self.assertEqual(
            models.build_update_step_body("s1"), {"stepId": "s1"})

    def test_build_update_step_body_full(self):
        body = models.build_update_step_body(
            "s1", step_name="New", step_description="d",
            depends_on=["s0"])
        self.assertEqual(body, {
            "stepId": "s1", "displayName": "New",
            "description": "d",
            "dependsOn": [{"waitFor": "Step", "stepId": "s0"}]})

    def test_build_delete_step_body(self):
        self.assertEqual(
            models.build_delete_step_body("s1"), {"stepId": "s1"})

    def test_build_split_workstream_body(self):
        body = models.build_split_workstream_body(
            "ws1", "new", ["e1", "e2"])
        self.assertEqual(body, {
            "sourceWorkstreamId": "ws1",
            "stepIds": ["e1", "e2"],
            "displayName": "new"})

    def test_build_merge_workstreams_body(self):
        body = models.build_merge_workstreams_body(["w1", "w2"], "merged")
        self.assertEqual(body, {
            "workstreamIds": ["w1", "w2"],
            "displayName": "merged"})

    def test_build_merge_workstreams_body_requires_name(self):
        with self.assertRaises(TypeError):
            models.build_merge_workstreams_body(["w1", "w2"])


class StepCommandTests(unittest.TestCase):

    def setUp(self):
        sub_patch = mock.patch.object(
            definition_cmds, 'get_subscription_id', return_value=SUB)
        self.addCleanup(sub_patch.stop)
        sub_patch.start()
        client_patch = mock.patch.object(step_cmds, 'ArmClient')
        self.addCleanup(client_patch.stop)
        self.client = client_patch.start().return_value

    def _runbook_id(self):
        project = arm_ids.migrate_project_id(SUB, RG, PROJECT)
        return arm_ids.runbook_id(project, RUNBOOK)

    def test_add_posts_add_step(self):
        self.client.post_action.return_value = {"ok": True}
        definition = {"workstreams": [{"id": "ws1", "steps": [
            {"stepId": "s-new", "displayName": "Step 1"}]}]}
        with mock.patch.object(
                step_cmds, '_load_definition', return_value=definition):
            result = step_cmds.add(
                mock.Mock(), RG, PROJECT, RUNBOOK, "Manual", "Step 1", "ws1")
        self.client.post_action.assert_called_once_with(
            self._runbook_id(), 'AddStep',
            models.build_add_step_body("Manual", "Step 1", "ws1"))
        # Returns the freshly-added step (projected), not the raw response.
        self.assertEqual(result.get("stepId"), "s-new")

    def test_add_falls_back_to_workstream(self):
        self.client.post_action.return_value = {"ok": True}
        definition = {"workstreams": [{"id": "ws1", "displayName": "Init",
                                       "steps": [{"stepId": "other"}]}]}
        with mock.patch.object(
                step_cmds, '_load_definition', return_value=definition):
            result = step_cmds.add(
                mock.Mock(), RG, PROJECT, RUNBOOK, "Manual", "Absent", "ws1")
        self.assertEqual(result.get("id"), "ws1")

    def test_update_posts_update_step(self):
        self.client.post_action.return_value = {"ok": True}
        definition = {"workstreams": [{"id": "ws1", "steps": [
            {"stepId": "s1", "displayName": "New"}]}]}
        with mock.patch.object(
                step_cmds, '_load_definition', return_value=definition):
            result = step_cmds.update(
                mock.Mock(), RG, PROJECT, RUNBOOK, "s1", step_name="New")
        self.client.post_action.assert_called_once_with(
            self._runbook_id(), 'UpdateStep',
            {"stepId": "s1", "displayName": "New"})
        self.assertEqual(result.get("stepId"), "s1")

    def test_remove_posts_delete_step(self):
        self.client.post_action.return_value = {"ok": True}
        step_cmds.remove(mock.Mock(), RG, PROJECT, RUNBOOK, "s1")
        self.client.post_action.assert_called_once_with(
            self._runbook_id(), 'DeleteStep', {"stepId": "s1"})


class WorkstreamCommandTests(unittest.TestCase):

    def setUp(self):
        sub_patch = mock.patch.object(
            definition_cmds, 'get_subscription_id', return_value=SUB)
        self.addCleanup(sub_patch.stop)
        sub_patch.start()
        client_patch = mock.patch.object(workstream_cmds, 'ArmClient')
        self.addCleanup(client_patch.stop)
        self.client = client_patch.start().return_value

    def _runbook_id(self):
        project = arm_ids.migrate_project_id(SUB, RG, PROJECT)
        return arm_ids.runbook_id(project, RUNBOOK)

    def test_split_posts_split_workstream(self):
        self.client.post_action.return_value = {"ok": True}
        definition = {"workstreams": [
            {"id": "ws1", "displayName": "src", "steps": []},
            {"id": "ws-new", "displayName": "new",
             "steps": [{"stepId": "e1"}]}]}
        with mock.patch.object(
                workstream_cmds, '_load_definition',
                return_value=definition):
            result = workstream_cmds.split(
                mock.Mock(), RG, PROJECT, RUNBOOK, "ws1", "new", ["e1"])
        self.client.post_action.assert_called_once_with(
            self._runbook_id(), 'SplitWorkstream',
            models.build_split_workstream_body("ws1", "new", ["e1"]))
        # Shows the new workstream (matched by name), projected.
        self.assertEqual(result.get("id"), "ws-new")

    def test_merge_posts_merge_workstreams(self):
        self.client.post_action.return_value = {"ok": True}
        definition = {"workstreams": [
            {"id": "w1", "displayName": "merged", "steps": []}]}
        with mock.patch.object(
                workstream_cmds, '_load_definition',
                return_value=definition):
            result = workstream_cmds.merge(
                mock.Mock(), RG, PROJECT, RUNBOOK, ["w1", "w2"], "merged")
        self.client.post_action.assert_called_once_with(
            self._runbook_id(), 'MergeWorkstreams',
            {"workstreamIds": ["w1", "w2"],
             "displayName": "merged"})
        self.assertEqual(result.get("id"), "w1")


class ExecutionModelTests(unittest.TestCase):

    def test_build_artifact_download_url_body(self):
        self.assertEqual(
            models.build_artifact_download_url_body(mode="Directory"),
            {"mode": "Directory"})
        self.assertEqual(
            models.build_artifact_download_url_body(
                mode="File", path="inputs.json"),
            {"mode": "File", "path": "inputs.json"})
        self.assertEqual(
            models.build_artifact_upload_url_body("inputs.json"),
            {"path": "inputs.json"})

    def test_action_enum_values(self):
        self.assertEqual(ExecutionAction.START.value, "Start")
        self.assertEqual(ExecutionAction.PAUSE.value, "Pause")
        self.assertEqual(ExecutionAction.RESUME.value, "Resume")
        self.assertEqual(ExecutionAction.CANCEL.value, "Cancel")
        self.assertEqual(ExecutionAction.RETRY.value, "Retry")

    def test_perform_action_body_shape(self):
        body = models.build_perform_action_body(ExecutionAction.PAUSE)
        self.assertEqual(
            body,
            {"action": "Pause", "targetId": "",
             "entities": []})
        self.assertIsInstance(body["action"], str)

    def test_perform_action_body_with_target(self):
        body = models.build_perform_action_body(
            ExecutionAction.RESUME, target_id="t1", entity_ids=["e1"])
        self.assertEqual(
            body,
            {"action": "Resume", "targetId": "t1",
             "entities": ["e1"]})


class ExecutionTransformerTests(unittest.TestCase):

    def test_flattens_workstream_steps(self):
        result = {
            "workstreams": [
                {"steps": [
                    {"id": "s1", "displayName": "Step 1",
                     "status": "Running",
                     "workloadProgress": "1/2"},
                ]},
            ],
        }
        rows = transformers.execution_table(result)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["Step Id"], "s1")
        self.assertEqual(rows[0]["Step Status"], "Running")
        self.assertEqual(rows[0]["Workload Progress"], "1/2")

    def test_unwraps_properties(self):
        result = {
            "properties": {
                "steps": [
                    {"stepId": "s2", "stepName": "Step 2",
                     "stepStatus": "Succeeded"},
                ],
            },
        }
        rows = transformers.execution_table(result)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["Step Id"], "s2")
        self.assertEqual(rows[0]["Step Status"], "Succeeded")


class ExecutionsListTransformerTests(unittest.TestCase):

    def test_lists_one_row_per_execution(self):
        result = [
            {"name": "e1", "properties": {
                "status": "Completed",
                "provisioningState": "Succeeded",
                "startTime": "2026-01-01T10:00:00Z",
                "endTime": "2026-01-01T10:05:00Z"}},
            {"name": "e2", "properties": {"status": "InProgress"}},
        ]
        rows = transformers.executions_table(result)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["Name"], "e1")
        self.assertEqual(rows[0]["Status"], "Completed")
        self.assertEqual(rows[0]["ProvisioningState"], "Succeeded")
        self.assertEqual(rows[0]["StartTime"], "2026-01-01T10:00:00Z")
        self.assertEqual(rows[0]["EndTime"], "2026-01-01T10:05:00Z")
        self.assertEqual(rows[1]["Name"], "e2")
        self.assertEqual(rows[1]["Status"], "InProgress")

    def test_single_execution_dict(self):
        rows = transformers.executions_table(
            {"name": "e9", "properties": {"state": "Queued"}})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["Name"], "e9")
        self.assertEqual(rows[0]["Status"], "Queued")


class ExecutionCommandTests(unittest.TestCase):

    def setUp(self):
        sub_patch = mock.patch.object(
            execution_cmds, 'get_subscription_id', return_value=SUB)
        self.addCleanup(sub_patch.stop)
        sub_patch.start()
        client_patch = mock.patch.object(execution_cmds, 'ArmClient')
        self.addCleanup(client_patch.stop)
        self.client = client_patch.start().return_value
        open_patch = mock.patch.object(
            execution_cmds, '_open_execution_view')
        self.addCleanup(open_patch.stop)
        self.open_view = open_patch.start()
        emit_patch = mock.patch.object(
            execution_cmds, '_emit_execution')
        self.addCleanup(emit_patch.stop)
        self.emit = emit_patch.start()

    def _runbook_id(self):
        project = arm_ids.migrate_project_id(SUB, RG, PROJECT)
        return arm_ids.runbook_id(project, RUNBOOK)

    def test_start_posts_execute_action(self):
        self.client.post_action.return_value = {"ok": True}
        result = execution_cmds.start(mock.Mock(), RG, PROJECT, RUNBOOK)
        self.assertEqual(result, {"ok": True})
        self.client.post_action.assert_called_once_with(
            self._runbook_id(), 'execute', no_wait=False)

    def test_start_no_wait(self):
        self.client.post_action.return_value = {"ok": True}
        execution_cmds.start(
            mock.Mock(), RG, PROJECT, RUNBOOK, no_wait=True)
        _, kwargs = self.client.post_action.call_args
        self.assertTrue(kwargs.get('no_wait'))

    def test_start_final_get_reads_execution(self):
        # After the execute action settles, start re-reads the created
        # execution, emits it to stdout, then opens the live watch view.
        self.client.post_action.return_value = {"name": "e5"}
        fresh = {"name": "e5", "properties": {"status": "InProgress"}}
        self.client.get.return_value = fresh
        result = execution_cmds.start(mock.Mock(), RG, PROJECT, RUNBOOK)
        self.assertIsNone(result)
        self.client.get.assert_called_once_with(
            arm_ids.execution_id(self._runbook_id(), "e5"))
        self.emit.assert_called_once_with(mock.ANY, fresh)

    def test_start_no_wait_skips_final_get(self):
        self.client.post_action.return_value = {"name": "e5"}
        execution_cmds.start(
            mock.Mock(), RG, PROJECT, RUNBOOK, no_wait=True)
        self.client.get.assert_not_called()

    def test_start_uses_execution_id_from_resource_id(self):
        # Async path: the final operation status carries the full resource
        # id (no bare 'name'); start extracts the trailing GUID from it.
        exec_arm = arm_ids.execution_id(self._runbook_id(), "exec-guid-9")
        self.client.post_action.return_value = {"id": exec_arm}
        fresh = {"name": "exec-guid-9"}
        self.client.get.return_value = fresh
        execution_cmds.start(mock.Mock(), RG, PROJECT, RUNBOOK)
        self.client.get.assert_called_once_with(exec_arm)
        self.emit.assert_called_once_with(mock.ANY, fresh)

    def test_start_opens_execution_view(self):
        self.client.post_action.return_value = {"name": "e5"}
        self.client.get.return_value = {"name": "e5"}
        execution_cmds.start(mock.Mock(), RG, PROJECT, RUNBOOK)
        self.open_view.assert_called_once()

    def test_start_no_wait_skips_execution_view(self):
        self.client.post_action.return_value = {"name": "e5"}
        execution_cmds.start(
            mock.Mock(), RG, PROJECT, RUNBOOK, no_wait=True)
        self.open_view.assert_not_called()

    def test_start_no_visualize_returns_execution_without_view(self):
        # --no-visualize re-reads the execution and returns it for normal
        # output, but never opens the blocking watch view.
        self.client.post_action.return_value = {"name": "e5"}
        fresh = {"name": "e5", "properties": {"status": "InProgress"}}
        self.client.get.return_value = fresh
        result = execution_cmds.start(
            mock.Mock(), RG, PROJECT, RUNBOOK, no_visualize=True)
        self.assertEqual(result, fresh)
        self.open_view.assert_not_called()
        self.emit.assert_not_called()

    def test_list_calls_executions_collection(self):
        self.client.list.return_value = []
        execution_cmds.list_(mock.Mock(), RG, PROJECT, RUNBOOK)
        self.client.list.assert_called_once_with(
            self._runbook_id() + '/executions')

    def test_show_returns_execution(self):
        self.client.post_action.return_value = {"downloadUrl": "https://b/x"}
        status = {"state": "InProgress", "id": "e1"}
        with mock.patch.object(
                execution_cmds.files, 'download_bytes',
                return_value=json.dumps(status).encode('utf-8')) as dl:
            result = execution_cmds.show(
                mock.Mock(), RG, PROJECT, RUNBOOK, "e1")
        self.assertEqual(result, status)
        self.client.post_action.assert_called_once_with(
            arm_ids.execution_id(self._runbook_id(), "e1"),
            'GenerateDownloadUrl',
            {"mode": "File", "path": "executionStatus.json"})
        dl.assert_called_once_with("https://b/x")

    def test_show_projects_step(self):
        status = {
            "workstreams": [
                {"steps": [{"id": "s1"}, {"id": "s2"}]},
            ],
        }
        self.client.post_action.return_value = {"downloadUrl": "https://b/x"}
        with mock.patch.object(
                execution_cmds.files, 'download_bytes',
                return_value=json.dumps(status).encode('utf-8')):
            result = execution_cmds.show(
                mock.Mock(), RG, PROJECT, RUNBOOK, "e1", step_id="s2")
        self.assertEqual(result, {"id": "s2"})

    def test_show_raises_for_inputs_only_archive(self):
        # A not-yet-run execution's download archive contains only the input
        # parameters (no status.json); show must raise rather than return the
        # inputs blob as if it were a status document.
        self.client.post_action.return_value = {"downloadUrl": "https://b/x"}
        inputs_zip = _make_zip({
            "user-inputs.json": '{"inputs": {"schema": {}}}'})
        with mock.patch.object(
                execution_cmds.files, 'download_bytes',
                return_value=inputs_zip):
            with self.assertRaises(CLIInternalError):
                execution_cmds.show(
                    mock.Mock(), RG, PROJECT, RUNBOOK, "e1")
        self.client.get.assert_not_called()

    def test_pause_posts_perform_action(self):
        self.client.post_action.return_value = {"ok": True}
        execution_cmds.pause(mock.Mock(), RG, PROJECT, RUNBOOK, "e1")
        self.client.post_action.assert_called_once_with(
            arm_ids.execution_id(self._runbook_id(), "e1"),
            'PerformAction',
            {"action": "Pause", "targetId": "",
             "entities": []})

    def test_resume_posts_perform_action(self):
        self.client.post_action.return_value = {"ok": True}
        execution_cmds.resume(mock.Mock(), RG, PROJECT, RUNBOOK, "e1")
        _, args, _ = self.client.post_action.mock_calls[0]
        self.assertEqual(args[2]["action"], "Resume")

    def test_cancel_posts_perform_action(self):
        self.client.post_action.return_value = {"ok": True}
        execution_cmds.cancel(mock.Mock(), RG, PROJECT, RUNBOOK, "e1")
        _, args, _ = self.client.post_action.mock_calls[0]
        self.assertEqual(args[2]["action"], "Cancel")


class ExecutionStepModelTests(unittest.TestCase):

    def test_build_retry_step_body(self):
        body = models.build_retry_step_body("step1")
        self.assertEqual(body, {
            "action": "Retry", "targetId": "step1",
            "entities": []})
        self.assertIsInstance(body["action"], str)

    def test_build_approve_step_body_full(self):
        body = models.build_approve_step_body("step1")
        self.assertEqual(body, {
            "action": "Approve", "targetId": "step1",
            "entities": []})

    def test_build_approve_step_body_partial(self):
        body = models.build_approve_step_body(
            "step1", entity_ids=["e1", "e2"])
        self.assertEqual(body["entities"], ["e1", "e2"])

    def test_build_complete_step_body(self):
        body = models.build_complete_step_body("step1", "done")
        self.assertEqual(body, {
            "action": "Complete", "targetId": "step1",
            "entities": [], "comment": "done"})


class ExecutionStepValidatorTests(unittest.TestCase):

    def test_approve_full_ok(self):
        validate_step_approve(
            SimpleNamespace(entities=None, all_ready=False))

    def test_approve_entities_ok(self):
        validate_step_approve(
            SimpleNamespace(entities=["e1"], all_ready=False))

    def test_approve_all_ready_ok(self):
        validate_step_approve(
            SimpleNamespace(entities=None, all_ready=True))

    def test_approve_entities_and_all_ready_rejected(self):
        with self.assertRaises(InvalidArgumentValueError):
            validate_step_approve(
                SimpleNamespace(entities=["e1"], all_ready=True))

    def test_complete_requires_comment(self):
        with self.assertRaises(RequiredArgumentMissingError):
            validate_step_complete(SimpleNamespace(comment=None))

    def test_complete_ok_with_comment(self):
        validate_step_complete(SimpleNamespace(comment="done"))


class ExecutionStepCommandTests(unittest.TestCase):

    def setUp(self):
        sub_patch = mock.patch.object(
            execution_cmds, 'get_subscription_id', return_value=SUB)
        self.addCleanup(sub_patch.stop)
        sub_patch.start()
        client_patch = mock.patch.object(execution_step_cmds, 'ArmClient')
        self.addCleanup(client_patch.stop)
        self.client = client_patch.start().return_value

    def _execution_id(self):
        project = arm_ids.migrate_project_id(SUB, RG, PROJECT)
        runbook = arm_ids.runbook_id(project, RUNBOOK)
        return arm_ids.execution_id(runbook, "e1")

    def test_retry_posts_perform_action(self):
        self.client.post_action.return_value = {"ok": True}
        result = execution_step_cmds.retry(
            mock.Mock(), RG, PROJECT, RUNBOOK, "e1", "step1")
        self.assertEqual(result, {"ok": True})
        self.client.post_action.assert_called_once_with(
            self._execution_id(), 'PerformAction',
            {"action": "Retry", "targetId": "step1",
             "entities": []})

    def test_approve_posts_provide_approval(self):
        self.client.post_action.return_value = {"ok": True}
        execution_step_cmds.approve(
            mock.Mock(), RG, PROJECT, RUNBOOK, "e1", "step1",
            entities=["ent1"])
        self.client.post_action.assert_called_once_with(
            self._execution_id(), 'ProvideApproval',
            {"action": "Approve", "targetId": "step1",
             "entities": ["ent1"]})

    def test_complete_posts_update_step_status(self):
        self.client.post_action.return_value = {"ok": True}
        execution_step_cmds.complete(
            mock.Mock(), RG, PROJECT, RUNBOOK, "e1", "step1", "done")
        self.client.post_action.assert_called_once_with(
            self._execution_id(), 'UpdateStepStatus',
            {"action": "Complete", "targetId": "step1",
             "entities": [], "comment": "done"})


_CFG_INPUTS = {
    "runbookId": (
        "/subscriptions/s/resourceGroups/myRg/providers/Microsoft.Migrate"
        "/migrateProjects/myProject/runbooks/testrunbook"),
    "waveId": (
        "/subscriptions/s/resourceGroups/myRg/providers/Microsoft.Migrate"
        "/migrateProjects/myProject/waves/wave-1"),
    "inputs": {
        "schema": {"vm.agentless.setup": {"applianceName": {
            "type": "string", "required": True, "scope": "Appliance",
            "isEditable": False}}},
        "stepInputs": {"vm.agentless.setup-001": {
            "applianceName": "appl-1"}},
    },
}
_CFG_SPEC = {"spec": {
    "entities": [{"displayName": "vm1"}],
    "workstreams": [{"steps": [
        {"stepId": "vm.agentless.setup-001", "entities": []}]}]}}


class ParameterCommandTests(unittest.TestCase):

    def setUp(self):
        sub_patch = mock.patch.object(
            definition_cmds, 'get_subscription_id', return_value=SUB)
        self.addCleanup(sub_patch.stop)
        sub_patch.start()
        client_patch = mock.patch.object(definition_cmds, 'ArmClient')
        self.addCleanup(client_patch.stop)
        self.client = client_patch.start().return_value

    def _runbook_id(self):
        project = arm_ids.migrate_project_id(SUB, RG, PROJECT)
        return arm_ids.runbook_id(project, RUNBOOK)

    def test_download_writes_parameters_file(self):
        self.client.get.return_value = {
            "properties": {"artifactId": ARTIFACT}}
        self.client.post_action.return_value = {
            "downloadUrl": "https://blob/x"}
        zip_bytes = _make_zip({
            "inputs.json": json.dumps(_CFG_INPUTS),
            "schema.json": json.dumps({"vm.agentless.setup": {}})})
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(
                    parameter_cmds.files, 'download_bytes',
                    return_value=zip_bytes) as dl:
                result = parameter_cmds.download(
                    mock.Mock(), RG, PROJECT, RUNBOOK, directory=tmp)
            dl.assert_called_once_with("https://blob/x")
            project = arm_ids.migrate_project_id(SUB, RG, PROJECT)
            self.client.post_action.assert_called_once_with(
                arm_ids.artifact_id(project, ARTIFACT),
                'generateDownloadUrl',
                {"mode": "Directory"},
                return_final_poll=True)
            names = sorted(os.path.basename(r['path']) for r in result)
            self.assertEqual(names, ['inputs.json', 'schema.json'])
            for row in result:
                self.assertEqual(row['kind'], 'parameters')
                self.assertTrue(os.path.isfile(row['path']))

    def test_upload_posts_generate_upload_url(self):
        project = arm_ids.migrate_project_id(SUB, RG, PROJECT)
        runbook_id = arm_ids.runbook_id(project, RUNBOOK)
        with mock.patch.object(parameter_cmds, 'ArmClient') as client_cls:
            client = client_cls.return_value
            client.post_action.side_effect = [
                {"uploadUrl": "https://blob/u"}, {"status": "ok"}]
            client.get.return_value = {"name": RUNBOOK, "latest": True}
            with tempfile.TemporaryDirectory() as tmp:
                src = os.path.join(tmp, "inputs.json")
                with open(src, "wb") as handle:
                    handle.write(b'{"runbookInputs": {}}')
                with mock.patch.object(
                        parameter_cmds.files, 'upload_bytes') as up:
                    result = parameter_cmds.upload(
                        mock.Mock(), RG, PROJECT, RUNBOOK, src)
                up.assert_called_once_with(
                    "https://blob/u", b'{"runbookInputs": {}}')
            self.assertEqual(
                client.post_action.call_args_list[0],
                mock.call(runbook_id, 'GenerateUploadUrl',
                          {"path": "inputs.json"}))
            self.assertEqual(
                client.post_action.call_args_list[1],
                mock.call(runbook_id, 'ValidateInput'))
            # Upload returns a fresh GET of the runbook, not the echoed body.
            client.get.assert_called_once_with(runbook_id)
            self.assertEqual(result, {"name": RUNBOOK, "latest": True})

    def test_configure_writes_html(self):
        self.client.get.return_value = {
            "properties": {"artifactId": ARTIFACT}}
        self.client.post_action.return_value = {
            "downloadUrl": "https://blob/x"}
        zip_bytes = _make_zip({
            "inputs.json": json.dumps(_CFG_INPUTS),
            "spec.json": json.dumps(_CFG_SPEC)})
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(
                    parameter_cmds.files, 'download_bytes',
                    return_value=zip_bytes), \
                    mock.patch.object(
                        parameter_cmds.files, 'open_in_browser') as op:
                result = parameter_cmds.configure(
                    mock.Mock(), RG, PROJECT, RUNBOOK, file=tmp)
            path = result['path']
            self.assertTrue(path.endswith('.html'))
            self.assertTrue(os.path.isfile(path))
            # A real, editable inputs.json is written next to the editor and
            # its path is surfaced (so upload --file points at a real file).
            inputs_path = result['inputsPath']
            self.assertTrue(inputs_path.endswith('inputs.json'))
            self.assertTrue(os.path.isfile(inputs_path))
            with open(path, encoding='utf-8') as handle:
                html_text = handle.read()
            self.assertIn('vm.agentless.setup-001', html_text)
            self.assertIn('inputsPath', html_text)
            self.assertNotIn('__RUNBOOK_DATA__', html_text)
            op.assert_called_once()

    def test_configure_from_file_skips_service(self):
        with tempfile.TemporaryDirectory() as tmp:
            ip = os.path.join(tmp, 'inputs.json')
            sp = os.path.join(tmp, 'spec.json')
            with open(ip, 'w', encoding='utf-8') as handle:
                json.dump(_CFG_INPUTS, handle)
            with open(sp, 'w', encoding='utf-8') as handle:
                json.dump(_CFG_SPEC, handle)
            with mock.patch.object(parameter_cmds, 'ArmClient') as client, \
                    mock.patch.object(
                        parameter_cmds.files, 'download_bytes') as dl, \
                    mock.patch.object(
                        parameter_cmds.files, 'open_in_browser'):
                result = parameter_cmds.configure(
                    mock.Mock(), file=tmp, from_file=ip, spec_file=sp)
            client.assert_not_called()
            dl.assert_not_called()
            self.assertTrue(result['path'].endswith('.html'))


class ExecutionParameterCommandTests(unittest.TestCase):

    def setUp(self):
        sub_patch = mock.patch.object(
            execution_cmds, 'get_subscription_id', return_value=SUB)
        self.addCleanup(sub_patch.stop)
        sub_patch.start()
        client_patch = mock.patch.object(
            execution_parameter_cmds, 'ArmClient')
        self.addCleanup(client_patch.stop)
        self.client = client_patch.start().return_value

    def _execution_id(self):
        project = arm_ids.migrate_project_id(SUB, RG, PROJECT)
        runbook = arm_ids.runbook_id(project, RUNBOOK)
        return arm_ids.execution_id(runbook, "e1")

    def test_download_writes_input_file(self):
        self.client.post_action.return_value = {
            "downloadUrl": "https://blob/x"}
        zip_bytes = _make_zip({"inputs.json": json.dumps(_CFG_INPUTS)})
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(
                    execution_parameter_cmds.files, 'download_bytes',
                    return_value=zip_bytes) as dl:
                result = execution_parameter_cmds.download(
                    mock.Mock(), RG, PROJECT, RUNBOOK, "e1", directory=tmp)
            dl.assert_called_once_with("https://blob/x")
            self.client.post_action.assert_called_once_with(
                self._execution_id(), 'GenerateDownloadUrl',
                {"mode": "Directory"})
            names = sorted(os.path.basename(r['path']) for r in result)
            self.assertEqual(names, ['inputs.json'])
            self.assertEqual(result[0]['kind'], 'parameters')

    def test_upload_puts_input_file(self):
        self.client.post_action.return_value = {
            "uploadUrl": "https://blob/u"}
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "input.json")
            with open(src, "wb") as handle:
                handle.write(b'{"runbookInputs": {}}')
            with mock.patch.object(
                    execution_parameter_cmds.files, 'upload_bytes') as up:
                result = execution_parameter_cmds.upload(
                    mock.Mock(), RG, PROJECT, RUNBOOK, "e1", src)
            self.client.post_action.assert_called_once_with(
                self._execution_id(), 'GenerateUploadUrl',
                {"path": "inputs.json"})
            up.assert_called_once_with(
                "https://blob/u", b'{"runbookInputs": {}}')
            self.assertEqual(result, {"status": "uploaded"})

    def test_configure_writes_html(self):
        self.client.post_action.return_value = {
            "downloadUrl": "https://blob/x"}
        blob = json.dumps(_CFG_INPUTS).encode('utf-8')
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(
                    execution_parameter_cmds.files, 'download_bytes',
                    return_value=blob), \
                    mock.patch.object(
                        execution_parameter_cmds.files,
                        'open_in_browser') as op:
                result = execution_parameter_cmds.configure(
                    mock.Mock(), RG, PROJECT, RUNBOOK, "e1", file=tmp)
            path = result['path']
            self.assertTrue(path.endswith('.html'))
            with open(path, encoding='utf-8') as handle:
                self.assertIn('vm.agentless.setup-001', handle.read())
            op.assert_called_once()

    def test_configure_from_file_skips_service(self):
        with tempfile.TemporaryDirectory() as tmp:
            ip = os.path.join(tmp, 'inputs.json')
            with open(ip, 'w', encoding='utf-8') as handle:
                json.dump(_CFG_INPUTS, handle)
            with mock.patch.object(
                    execution_parameter_cmds.files, 'download_bytes') as dl, \
                    mock.patch.object(
                        execution_parameter_cmds.files, 'open_in_browser'):
                result = execution_parameter_cmds.configure(
                    mock.Mock(), RG, PROJECT, RUNBOOK, file=tmp,
                    from_file=ip)
            dl.assert_not_called()
            self.assertTrue(result['path'].endswith('.html'))


class ConfigureRendererTests(unittest.TestCase):

    def test_build_meta_parses_ids_when_args_absent(self):
        meta = configure_renderer.build_meta(
            None, None, None, _CFG_INPUTS)
        self.assertEqual(meta['resourceGroup'], 'myRg')
        self.assertEqual(meta['project'], 'myProject')
        self.assertEqual(meta['runbook'], 'testrunbook')
        self.assertEqual(meta['wave'], 'wave-1')

    def test_build_meta_prefers_explicit_args(self):
        meta = configure_renderer.build_meta(
            'argRg', 'argProj', 'argRb', _CFG_INPUTS)
        self.assertEqual(meta['resourceGroup'], 'argRg')
        self.assertEqual(meta['project'], 'argProj')
        self.assertEqual(meta['runbook'], 'argRb')

    def test_render_embeds_data_and_escapes_script(self):
        root = {"runbookId": "/x", "inputs": {"schema": {},
                "stepInputs": {"s-1": {"note": "</script><b>x"}}}}
        html_text = configure_renderer.render(root, None, {"runbook": "r"})
        self.assertNotIn('__RUNBOOK_DATA__', html_text)
        self.assertNotIn('</script><b>x', html_text)
        self.assertIn('\\u003c', html_text)
        self.assertIn('s-1', html_text)

    def test_normalize_doc_unwraps_inputs(self):
        doc = configure_renderer._normalize_doc(_CFG_INPUTS)
        self.assertEqual(
            doc['stepInputs'], {"vm.agentless.setup-001": {
                "applianceName": "appl-1"}})
        self.assertIn('vm.agentless.setup', doc['schema'])
        self.assertTrue(doc['runbookId'].endswith('testrunbook'))

    def test_normalize_spec_unwraps_payload(self):
        spec = configure_renderer._normalize_spec(_CFG_SPEC)
        self.assertEqual(spec['entities'], [{"displayName": "vm1"}])
        self.assertEqual(len(spec['workstreams']), 1)

    def test_render_uses_separate_schema_doc(self):
        root = {"runbookId": "/x",
                "inputs": {"stepInputs": {"vm.agentless.setup-001": {}}}}
        schema = {"vm.agentless.setup": {"applianceName": {
            "type": "string", "required": True}}}
        html_text = configure_renderer.render(
            root, None, {"runbook": "r"}, schema_doc=schema)
        self.assertIn('applianceName', html_text)
        self.assertIn('vm.agentless.setup-001', html_text)

    def test_render_emits_csp_and_per_file_nonce(self):
        root = {"runbookId": "/x",
                "inputs": {"stepInputs": {"s-1": {}}}}
        html_text = configure_renderer.render(root, None, {"runbook": "r"})
        self.assertNotIn('__CSP_NONCE__', html_text)
        self.assertIn(
            '<meta http-equiv="Content-Security-Policy"', html_text)
        # The nonce on the <script> tag must also appear in script-src, and
        # 'unsafe-inline' must not weaken the script policy.
        match = re.search(r'<script nonce="([A-Za-z0-9_-]+)"', html_text)
        self.assertIsNotNone(match)
        nonce = match.group(1)
        self.assertIn("script-src 'nonce-%s'" % nonce, html_text)
        self.assertNotIn("script-src 'unsafe-inline'", html_text)

    def test_render_nonce_is_unique_per_file(self):
        root = {"runbookId": "/x",
                "inputs": {"stepInputs": {"s-1": {}}}}
        first = re.search(
            r'<script nonce="([A-Za-z0-9_-]+)"',
            configure_renderer.render(root, None, {"runbook": "r"})).group(1)
        second = re.search(
            r'<script nonce="([A-Za-z0-9_-]+)"',
            configure_renderer.render(root, None, {"runbook": "r"})).group(1)
        self.assertNotEqual(first, second)

    def test_render_ships_client_side_escaper(self):
        # The page builds its UI from the embedded JSON via innerHTML, so the
        # client-side esc() guard must be present and applied at render time.
        root = {"runbookId": "/x",
                "inputs": {"stepInputs": {"s-1": {}}}}
        html_text = configure_renderer.render(root, None, {"runbook": "r"})
        self.assertIn("replace(/</g, '&lt;')", html_text)
        self.assertIn("replace(/>/g, '&gt;')", html_text)

    def test_render_has_phase1_ui(self):
        # Phase 1 UX: legend, workload-override pane, JSON popover button,
        # spec-driven labels, and no per-field Appliance/Entity scope pill.
        root = {"runbookId": "/x",
                "inputs": {"stepInputs": {"s-1": {}}}}
        html_text = configure_renderer.render(root, None, {"runbook": "r"})
        self.assertIn('Workload level overrides', html_text)
        self.assertIn('View updated parameters file', html_text)
        self.assertIn('function stepLabel(', html_text)
        self.assertIn('id="genAt"', html_text)
        self.assertIn("'Must match: '", html_text)
        self.assertNotIn('scope-pill', html_text)
        self.assertNotIn('id="validateBtn"', html_text)

    def test_render_has_phase23_ui(self):
        # Phase 2/3: structured grid/kv editors, issues navigator, search,
        # and accessibility roles.
        root = {"runbookId": "/x",
                "inputs": {"stepInputs": {"s-1": {}}}}
        html_text = configure_renderer.render(root, None, {"runbook": "r"})
        self.assertIn('function gridCtrl(', html_text)
        self.assertIn('function kvCtrl(', html_text)
        self.assertIn('function showIssues(', html_text)
        self.assertIn('const matchField', html_text)
        self.assertIn('id="issuePop"', html_text)
        self.assertIn('aria-modal="true"', html_text)


_DEFINITION_DOC = {
    "workstreams": [
        {
            "id": "ws1",
            "displayName": "Web tier",
            "steps": [
                {"id": "s1", "displayName": "Prepare", "dependsOn": []},
                {"id": "s2", "displayName": "Migrate",
                 "dependsOn": [{"stepId": "s1"}]},
                {"id": "s3", "displayName": "Cutover",
                 "dependsOn": ["s1", "s2"]},
            ],
        }
    ]
}


# Mirrors the execution status.json shape: top-level state/workstreams,
# steps keyed by stepId/displayName/state, dependsOn as objects with a
# "step" key, and per-entity progress under entityExecutions.
_STATUS_DOC = {
    "state": "InProgress",
    "workstreams": [
        {
            "id": "ws1",
            "displayName": "Web tier",
            "steps": [
                {"stepId": "setup", "displayName": "Setup",
                 "state": "Completed", "dependsOn": []},
                {"stepId": "network", "displayName": "Network",
                 "state": "Failed", "dependsOn": []},
                {"stepId": "dataSync", "displayName": "Data sync",
                 "state": "InProgress",
                 "dependsOn": [
                     {"step": "setup", "mode": "step"},
                     {"step": "network", "mode": "perEntity"},
                 ],
                 "entityExecutions": [
                     {"entityId": "e1", "state": "Completed"},
                     {"entityId": "e2", "state": "InProgress"},
                 ]},
                {"stepId": "cutover", "displayName": "Cutover",
                 "state": "Blocked",
                 "dependsOn": [{"step": "dataSync", "mode": "step"}]},
            ],
        }
    ],
}


# Rich failure shape: failed step with a per-entity attempt timeline
# (fail then recover) plus a downstream skipped step with a statusReason.
_STATUS_DETAIL_DOC = {
    "status": "Failed",
    "workstreams": [{
        "id": "ws1", "displayName": "Unmapped",
        "steps": [
            {"stepId": "dataSync-1", "displayName": "Data Sync",
             "status": "Failed",
             "errorDetails": {
                 "code": "StepFailed",
                 "message": "invalid parameter logStorageAccountId"},
             "entityExecutions": [
                 {"entity": "vm-a", "status": "Failed",
                  "errorDetails": {
                      "code": "StepFailed",
                      "message": "invalid parameter logStorageAccountId"},
                  "totalAttempts": 0,
                  "attempts": [
                      {"attemptNumber": 1, "status": "Failed",
                       "errorDetails": {"code": "StepFailed",
                                        "message": "boom"}},
                      {"attemptNumber": 2, "status": "Completed"}]}],
             "attempts": []},
            {"stepId": "test-1", "displayName": "Test Migration",
             "status": "Skipped",
             "statusReason": "Dependency dataSync-1 failed",
             "entityExecutions": [
                 {"entity": "vm-a", "status": "Skipped",
                  "statusReason": "Dependency dataSync-1 failed",
                  "attempts": [{"attemptNumber": 1, "status": "Skipped"}]}]},
        ],
    }],
}


# Execution status carrying the service-provided step aggregate counts and the
# per-entity ``toolReportedMigrationStatus`` field.
_STATUS_TOOL_DOC = {
    "stepsCompleted": 2,
    "stepsInProgress": 1,
    "stepsAwaitingUserAction": 0,
    "stepsFailed": 0,
    "stepsNotStarted": 1,
    "status": "InProgress",
    "startTime": "2026-08-21T10:00:00Z",
    "lastUpdatedTime": "2026-08-21T10:30:00Z",
    "workstreams": [{
        "id": "workstream-1", "displayName": "waveapp",
        "status": "InProgress",
        "steps": [{
            "stepId": "vm.agentless.migration-1", "displayName": "Migration",
            "stepRef": "vm.agentless.migration", "status": "InProgress",
            "entities": ["web-vm-01", "db-vm-02"],
            "entitiesCompleted": 1,
            "entityExecutions": [
                {"entity": "web-vm-01",
                 "toolReportedMigrationStatus": "MigrationSucceeded",
                 "status": "Completed"},
                {"entity": "db-vm-02",
                 "toolReportedMigrationStatus": "Migrating",
                 "status": "InProgress"}]}],
    }],
}


class ExecutionStatusParsingTests(unittest.TestCase):

    def test_read_status_json_raw_bytes(self):
        parsed = files.read_status_json(
            json.dumps(_STATUS_DOC).encode('utf-8'))
        self.assertEqual(parsed["state"], "InProgress")

    def test_read_status_json_from_zip(self):
        zip_bytes = _make_zip({"status.json": json.dumps(_STATUS_DOC)})
        parsed = files.read_status_json(zip_bytes)
        self.assertEqual(parsed["state"], "InProgress")

    def test_execution_table_renders_without_crash(self):
        rows = transformers.execution_table(_STATUS_DOC)
        by_id = {row['Step Id']: row for row in rows}
        self.assertEqual(by_id['setup']['Step Status'], 'Completed')
        self.assertEqual(by_id['network']['Step Status'], 'Failed')
        self.assertEqual(by_id['cutover']['Step Status'], 'Blocked')

    def test_execution_table_formats_depends_on(self):
        rows = transformers.execution_table(_STATUS_DOC)
        by_id = {row['Step Id']: row for row in rows}
        self.assertEqual(
            by_id['dataSync']['Depends On'],
            'Web tier:Setup\nWeb tier:Network')
        self.assertEqual(by_id['setup']['Depends On'], '')

    def test_execution_table_workload_progress(self):
        rows = transformers.execution_table(_STATUS_DOC)
        by_id = {row['Step Id']: row for row in rows}
        self.assertEqual(
            by_id['dataSync']['Workload Progress'], '1/2 completed')
        self.assertIsNone(by_id['setup']['Workload Progress'])

    def test_execution_table_surfaces_error_and_retries(self):
        rows = transformers.execution_table(_STATUS_DETAIL_DOC)
        by_id = {row['Step Id']: row for row in rows}
        # One failed attempt on the entity -> 1 retry; error message shown.
        self.assertEqual(by_id['dataSync-1']['Retries'], 1)
        self.assertIn('logStorageAccountId', by_id['dataSync-1']['Details'])
        # A skipped step shows its statusReason and no retries.
        self.assertEqual(by_id['test-1']['Retries'], 0)
        self.assertIn('Dependency', by_id['test-1']['Details'])

    def test_execution_view_captures_error_retry_attempts(self):
        view = visualize_viewmodel.build_execution_view(
            _STATUS_DETAIL_DOC, title='X')
        steps = {s.id: s for ws in view.workstreams for s in ws.steps}
        ds = steps['dataSync-1']
        self.assertIn('logStorageAccountId', ds.error)
        self.assertEqual(ds.retry_count, 1)
        ent = ds.entities[0]
        self.assertEqual(ent.status, 'Failed')
        self.assertIn('logStorageAccountId', ent.error)
        self.assertEqual(len(ent.attempts), 2)
        self.assertEqual(
            steps['test-1'].status_reason, 'Dependency dataSync-1 failed')

    def test_execution_render_shows_error_and_attempts(self):
        graph = visualize_graph.build_execution_graph(
            _STATUS_DETAIL_DOC, title='X')
        view = visualize_viewmodel.build_execution_view(
            _STATUS_DETAIL_DOC, title='X')
        html_text = visualize_renderer.render(graph, view=view)
        self.assertIn('logStorageAccountId', html_text)
        self.assertIn('Attempt 1', html_text)
        self.assertIn('class="retry"', html_text)
        self.assertIn('Dependency', html_text)

    def test_execution_overview_uses_service_counts(self):
        overview = transformers.execution_overview(_STATUS_TOOL_DOC)
        self.assertEqual(overview['State'], 'InProgress')
        self.assertEqual(overview['Completed'], 2)
        self.assertEqual(overview['In Progress'], 1)
        self.assertEqual(overview['Awaiting Action'], 0)
        self.assertEqual(overview['Failed'], 0)
        self.assertEqual(overview['Not Started'], 1)
        self.assertEqual(overview['Last Updated'], '2026-08-21T10:30:00Z')

    def test_execution_table_omits_tool_reported_status(self):
        # Tool status is per-entity and belongs only in the step side-pane,
        # never in the (per-step) status table.
        rows = transformers.execution_table(_STATUS_TOOL_DOC)
        by_id = {row['Step Id']: row for row in rows}
        progress = by_id['vm.agentless.migration-1']['Workload Progress']
        self.assertEqual(progress, '1/2 completed')
        self.assertNotIn('MigrationSucceeded', progress)
        self.assertNotIn('Migrating', progress)

    def test_execution_view_summary_uses_service_counts(self):
        view = visualize_viewmodel.build_execution_view(
            _STATUS_TOOL_DOC, title='X')
        summary = dict(view.summary)
        self.assertEqual(summary['State'], 'InProgress')
        self.assertEqual(summary['Completed'], 2)
        self.assertEqual(summary['In progress'], 1)
        self.assertEqual(summary['Not started'], 1)
        meta = dict(view.meta)
        self.assertEqual(meta['Started'], '2026-08-21T10:00:00Z')
        self.assertEqual(meta['Last updated'], '2026-08-21T10:30:00Z')

    def test_execution_view_captures_tool_reported_status(self):
        view = visualize_viewmodel.build_execution_view(
            _STATUS_TOOL_DOC, title='X')
        steps = {s.id: s for ws in view.workstreams for s in ws.steps}
        entities = {e.name: e
                    for e in steps['vm.agentless.migration-1'].entities}
        self.assertEqual(
            entities['web-vm-01'].tool_status, 'MigrationSucceeded')
        self.assertEqual(entities['db-vm-02'].tool_status, 'Migrating')

    def test_execution_render_shows_tool_reported_status(self):
        graph = visualize_graph.build_execution_graph(
            _STATUS_TOOL_DOC, title='X')
        view = visualize_viewmodel.build_execution_view(
            _STATUS_TOOL_DOC, title='X')
        html_text = visualize_renderer.render(graph, view=view)
        self.assertIn('Migrating', html_text)
        self.assertIn('MigrationSucceeded', html_text)

    def test_execution_overview_absent_counts_returns_state_only(self):
        # _STATUS_DOC carries no stepsX aggregates or timestamps.
        overview = transformers.execution_overview(_STATUS_DOC)
        self.assertEqual(overview.get('State'), 'InProgress')
        self.assertNotIn('Completed', overview)
        self.assertNotIn('Start Time', overview)

    def test_execution_overview_empty_for_non_dict(self):
        self.assertEqual(dict(transformers.execution_overview(None)), {})
        self.assertEqual(dict(transformers.execution_overview([])), {})

    def test_execution_table_progress_without_tool_status(self):
        # Entities lacking toolReportedMigrationStatus render plainly.
        rows = transformers.execution_table(_STATUS_DOC)
        by_id = {row['Step Id']: row for row in rows}
        self.assertEqual(
            by_id['dataSync']['Workload Progress'], '1/2 completed')

    def test_execution_view_summary_falls_back_when_counts_absent(self):
        view = visualize_viewmodel.build_execution_view(
            _STATUS_DOC, title='X')
        summary = dict(view.summary)
        self.assertEqual(summary.get('State'), 'InProgress')
        # No service counts -> self-counted per-status keys instead.
        self.assertIn('Failed', summary)
        meta = dict(view.meta)
        self.assertNotIn('Started', meta)
        self.assertNotIn('Last updated', meta)

    def test_execution_view_entity_tool_status_none_when_absent(self):
        view = visualize_viewmodel.build_execution_view(
            _STATUS_DOC, title='X')
        steps = {s.id: s for ws in view.workstreams for s in ws.steps}
        for entity in steps['dataSync'].entities:
            self.assertIsNone(entity.tool_status)

    def test_execution_graph_edges_from_step_key(self):
        graph = visualize_graph.build_execution_graph(_STATUS_DOC)
        edges = {(e.source, e.target) for e in graph.edges}
        self.assertIn(('setup', 'dataSync'), edges)
        self.assertIn(('network', 'dataSync'), edges)
        self.assertIn(('dataSync', 'cutover'), edges)
        by_id = {n.id: n for n in graph.nodes}
        self.assertEqual(by_id['network'].status, 'Failed')
        self.assertEqual(by_id['cutover'].status, 'Blocked')


class VisualizeGraphTests(unittest.TestCase):

    def test_build_definition_graph_nodes_and_edges(self):
        graph = visualize_graph.build_definition_graph(_DEFINITION_DOC)
        self.assertEqual({n.id for n in graph.nodes}, {"s1", "s2", "s3"})
        self.assertEqual(len(graph.edges), 3)
        by_id = {n.id: n for n in graph.nodes}
        self.assertEqual(by_id["s1"].name, "Prepare")
        self.assertEqual(by_id["s1"].group, "Web tier")

    def test_topological_layering(self):
        graph = visualize_graph.build_definition_graph(_DEFINITION_DOC)
        layer = {n.id: n.layer for n in graph.nodes}
        self.assertEqual(layer["s1"], 0)
        self.assertEqual(layer["s2"], 1)
        self.assertEqual(layer["s3"], 2)

    def test_cycle_detection_raises(self):
        doc = {"steps": [
            {"id": "a", "dependsOn": ["b"]},
            {"id": "b", "dependsOn": ["a"]},
        ]}
        with self.assertRaises(InvalidArgumentValueError):
            visualize_graph.build_definition_graph(doc)

    def test_dangling_dependency_is_dropped(self):
        doc = {"steps": [
            {"id": "a", "dependsOn": ["missing"]},
        ]}
        graph = visualize_graph.build_definition_graph(doc)
        self.assertEqual(len(graph.nodes), 1)
        self.assertEqual(graph.edges, [])
        self.assertEqual(graph.nodes[0].layer, 0)

    def test_execution_graph_carries_status(self):
        doc = {"properties": {"steps": [
            {"id": "a", "displayName": "A", "status": "Succeeded"},
            {"id": "b", "displayName": "B", "status": "Running",
             "dependsOn": ["a"]},
        ]}}
        graph = visualize_graph.build_execution_graph(doc)
        by_id = {n.id: n for n in graph.nodes}
        self.assertEqual(by_id["a"].status, "Succeeded")
        self.assertEqual(by_id["b"].status, "Running")


class VisualizeRendererTests(unittest.TestCase):

    def test_escapes_malicious_step_name(self):
        doc = {"steps": [
            {"id": "s1", "displayName": "<script>alert(1)</script>"},
        ]}
        graph = visualize_graph.build_definition_graph(doc)
        html_text = visualize_renderer.render(graph)
        self.assertNotIn("<script>alert(1)</script>", html_text)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html_text)

    def test_output_is_self_contained(self):
        graph = visualize_graph.build_definition_graph(_DEFINITION_DOC)
        html_text = visualize_renderer.render(graph)
        self.assertNotIn("http://", html_text)
        self.assertNotIn("https://", html_text)
        self.assertNotIn("src=", html_text)
        self.assertIn("<svg", html_text)

    def test_empty_graph_renders_message(self):
        graph = visualize_graph.build_definition_graph({})
        html_text = visualize_renderer.render(graph)
        self.assertIn("no steps", html_text.lower())

    def test_no_auto_reload_by_default(self):
        graph = visualize_graph.build_definition_graph(_DEFINITION_DOC)
        html_text = visualize_renderer.render(graph)
        self.assertNotIn('http-equiv="refresh"', html_text)

    def test_auto_reload_meta_when_interval_set(self):
        graph = visualize_graph.build_definition_graph(_DEFINITION_DOC)
        html_text = visualize_renderer.render(graph, refresh_interval=5)
        self.assertIn(
            '<meta http-equiv="refresh" content="5" />', html_text)
        # The auto-reload must stay offline (no URL to fetch).
        self.assertNotIn("http://", html_text)
        self.assertNotIn("https://", html_text)

    def test_auto_reload_omitted_for_non_positive_interval(self):
        graph = visualize_graph.build_definition_graph(_DEFINITION_DOC)
        for value in (0, -1, None, "x"):
            html_text = visualize_renderer.render(
                graph, refresh_interval=value)
            self.assertNotIn('http-equiv="refresh"', html_text)

    def test_render_emits_csp_and_per_file_nonce(self):
        graph = visualize_graph.build_definition_graph(_DEFINITION_DOC)
        html_text = visualize_renderer.render(graph)
        self.assertNotIn('$nonce', html_text)
        self.assertIn(
            '<meta http-equiv="Content-Security-Policy"', html_text)
        match = re.search(r'<script nonce="([A-Za-z0-9_-]+)"', html_text)
        self.assertIsNotNone(match)
        nonce = match.group(1)
        self.assertIn("script-src 'nonce-%s'" % nonce, html_text)
        self.assertNotIn("script-src 'unsafe-inline'", html_text)

    def test_render_nonce_is_unique_per_file(self):
        graph = visualize_graph.build_definition_graph(_DEFINITION_DOC)
        first = re.search(
            r'<script nonce="([A-Za-z0-9_-]+)"',
            visualize_renderer.render(graph)).group(1)
        second = re.search(
            r'<script nonce="([A-Za-z0-9_-]+)"',
            visualize_renderer.render(graph)).group(1)
        self.assertNotEqual(first, second)


class VisualizeCommandTests(unittest.TestCase):

    def setUp(self):
        sub_patch = mock.patch.object(
            definition_cmds, 'get_subscription_id', return_value=SUB)
        self.addCleanup(sub_patch.stop)
        sub_patch.start()
        exec_sub_patch = mock.patch.object(
            execution_cmds, 'get_subscription_id', return_value=SUB)
        self.addCleanup(exec_sub_patch.stop)
        exec_sub_patch.start()
        # visualize opens by default; stub the launch so tests never spawn a
        # browser (and never fail on a headless CI agent).
        for module in (definition_cmds, execution_cmds):
            open_patch = mock.patch.object(
                module.files, 'open_in_browser', return_value=True)
            self.addCleanup(open_patch.stop)
            open_patch.start()

    def test_definition_visualize_fails_when_browser_cannot_open(self):
        zip_bytes = _make_zip({"rb-x-spec.json": json.dumps(
            {"spec": _DEFINITION_DOC})})
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(definition_cmds, 'ArmClient') as client, \
                    mock.patch.object(
                        definition_cmds.files, 'download_bytes',
                        return_value=zip_bytes), \
                    mock.patch.object(
                        definition_cmds.files, 'open_in_browser',
                        side_effect=CLIInternalError('no browser')):
                client.return_value.post_action.return_value = {
                    "downloadUrl": "https://blob/x"}
                with self.assertRaises(CLIInternalError):
                    definition_cmds.visualize(
                        mock.Mock(), RG, PROJECT, RUNBOOK, file=tmp)

    def test_definition_visualize_no_open_skips_browser(self):
        zip_bytes = _make_zip({"rb-x-spec.json": json.dumps(
            {"spec": _DEFINITION_DOC})})
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(definition_cmds, 'ArmClient') as client, \
                    mock.patch.object(
                        definition_cmds.files, 'download_bytes',
                        return_value=zip_bytes), \
                    mock.patch.object(
                        definition_cmds.files, 'open_in_browser') as op:
                client.return_value.post_action.return_value = {
                    "downloadUrl": "https://blob/x"}
                result = definition_cmds.visualize(
                    mock.Mock(), RG, PROJECT, RUNBOOK, file=tmp,
                    no_open=True)
            op.assert_not_called()
            self.assertTrue(result['path'].endswith('.html'))

    def test_definition_visualize_writes_html(self):
        zip_bytes = _make_zip({
            "rb-x-spec.json": json.dumps(
                {"spec": _DEFINITION_DOC}),
        })
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(definition_cmds, 'ArmClient') as client, \
                    mock.patch.object(
                        definition_cmds.files, 'download_bytes',
                        return_value=zip_bytes):
                client.return_value.post_action.return_value = {
                    "downloadUrl": "https://blob/x"}
                result = definition_cmds.visualize(
                    mock.Mock(), RG, PROJECT, RUNBOOK, file=tmp)
            path = result['path']
            self.assertTrue(os.path.isfile(path))
            with open(path, encoding='utf-8') as handle:
                self.assertIn("<svg", handle.read())

    def test_execution_visualize_writes_html(self):
        execution_doc = {"steps": [
            {"stepId": "a", "displayName": "A", "state": "Completed"},
        ]}
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(execution_cmds, 'ArmClient') as client, \
                    mock.patch.object(
                        execution_cmds.files, 'download_bytes',
                        return_value=json.dumps(
                            execution_doc).encode('utf-8')):
                client.return_value.post_action.return_value = {
                    "downloadUrl": "https://blob/x"}
                result = execution_cmds.visualize(
                    mock.Mock(), RG, PROJECT, RUNBOOK, "e1", file=tmp)
            path = result['path']
            self.assertTrue(os.path.isfile(path))
            with open(path, encoding='utf-8') as handle:
                self.assertIn("Completed", handle.read())

    def test_definition_visualize_from_local_file(self):
        # --from-file renders a local spec JSON with no service calls.
        with tempfile.TemporaryDirectory() as tmp:
            spec_path = os.path.join(tmp, 'rb-local-spec.json')
            with open(spec_path, 'w', encoding='utf-8') as handle:
                json.dump({"spec": _DEFINITION_DOC}, handle)
            with mock.patch.object(
                    definition_cmds, 'ArmClient') as client, \
                    mock.patch.object(
                        definition_cmds.files, 'download_bytes') as dl:
                result = definition_cmds.visualize(
                    mock.Mock(), file=tmp, from_file=spec_path)
            client.assert_not_called()
            dl.assert_not_called()
            path = result['path']
            self.assertTrue(os.path.isfile(path))
            with open(path, encoding='utf-8') as handle:
                self.assertIn("<svg", handle.read())

    def test_definition_visualize_from_local_file_with_parameters(self):
        # A local parameters file feeds per-step configuration status.
        with tempfile.TemporaryDirectory() as tmp:
            spec_path = os.path.join(tmp, 'rb-local-spec.json')
            params_path = os.path.join(tmp, 'rb-local-parameters.json')
            with open(spec_path, 'w', encoding='utf-8') as handle:
                json.dump({"spec": _REAL_DEFINITION}, handle)
            with open(params_path, 'w', encoding='utf-8') as handle:
                json.dump({"inputs": _REAL_PARAMS}, handle)
            result = definition_cmds.visualize(
                mock.Mock(), file=tmp, from_file=spec_path,
                parameters_file=params_path)
            path = result['path']
            with open(path, encoding='utf-8') as handle:
                html_text = handle.read()
            self.assertIn("Configured", html_text)

    def test_execution_visualize_from_local_file(self):
        execution_doc = {"steps": [
            {"stepId": "a", "displayName": "A", "state": "Completed"},
        ]}
        with tempfile.TemporaryDirectory() as tmp:
            status_path = os.path.join(tmp, 'status.json')
            with open(status_path, 'w', encoding='utf-8') as handle:
                json.dump(execution_doc, handle)
            with mock.patch.object(
                    execution_cmds, 'ArmClient') as client, \
                    mock.patch.object(
                        execution_cmds.files, 'download_bytes') as dl:
                result = execution_cmds.visualize(
                    mock.Mock(), file=tmp, from_file=status_path)
            client.assert_not_called()
            dl.assert_not_called()
            path = result['path']
            self.assertTrue(os.path.isfile(path))
            with open(path, encoding='utf-8') as handle:
                self.assertIn("Completed", handle.read())


# --------------------------------------------------------------------------
# Real-shape definition + parameters fixtures (mirror migrate/spec/*.json)
# --------------------------------------------------------------------------
_ENT_A = ("/subscriptions/s/resourcegroups/rg/providers/microsoft.migrate/"
          "migrateprojects/p/migrationentities/aaa")
_ENT_B = ("/subscriptions/s/resourcegroups/rg/providers/microsoft.migrate/"
          "migrateprojects/p/migrationentities/bbb")

# Steps use prerequisite/dependsOn objects, a stepRef, and an entities[] list
# of ARM ids, exactly like the real runbook definition document.
_REAL_DEFINITION = {
    "entities": [
        {"id": _ENT_A, "displayName": "vm-a"},
        {"id": _ENT_B, "displayName": "vm-b"},
    ],
    "workstreams": [
        {"id": "workstream-0", "displayName": "Initialization", "steps": [
            {"stepId": "vm.agentless.setup-1", "displayName": "Setup",
             "stepRef": "vm.agentless.setup", "entities": [],
             "prerequisites": [], "dependsOn": []},
        ]},
        {"id": "workstream-1", "displayName": "waveapp", "steps": [
            {"stepId": "vm.agentless.prepareEntity-1",
             "displayName": "Prepare Entity",
             "stepRef": "vm.agentless.prepareEntity",
             "entities": [_ENT_A, _ENT_B],
             "prerequisites": [
                 {"stepId": "vm.agentless.setup-1", "waitFor": "wholeStep"}],
             "dependsOn": []},
            {"stepId": "common.approval-1", "displayName": "Approval Gate",
             "stepRef": "common.approval", "entities": [_ENT_A, _ENT_B],
             "prerequisites": [],
             "dependsOn": [{"stepId": "vm.agentless.prepareEntity-1",
                            "waitFor": "sameEntity"}]},
            {"stepId": "vm.agentless.migration-1", "displayName": "Migration",
             "stepRef": "vm.agentless.migration",
             "entities": [_ENT_A, _ENT_B],
             "prerequisites": [{"stepId": "vm.agentless.prepareEntity-1",
                               "waitFor": "sameEntity"}],
             "dependsOn": [{"stepId": "common.approval-1",
                            "waitFor": "sameEntity"}]},
        ]},
    ],
}

# setup-1 is all-null (NotConfigured); prepareEntity-1 has the Appliance field
# set but the per-entity field null (Partial (1/2)); migration-1 is fully set
# (Configured); common.approval-1 has no required inputs (Configured).
_REAL_PARAMS = {
    "schema": {
        "vm.agentless.setup": {
            "applianceName": {"required": True, "scope": "Appliance"},
            "storageAccountId": {"required": True, "scope": "Appliance"},
        },
        "vm.agentless.prepareEntity": {
            "storageAccountId": {"required": True, "scope": "Appliance"},
            "targetNetworkId": {"required": True, "scope": "Entity"},
        },
        "vm.agentless.migration": {
            "licenseType": {"required": True, "scope": "Appliance"},
        },
        "common.approval": {},
    },
    "stepInputs": {
        "vm.agentless.setup-1": {
            "applianceName": None, "storageAccountId": None},
        "vm.agentless.prepareEntity-1": {
            "storageAccountId": "sa1",
            "workloadOverrides": {
                _ENT_A: {"targetNetworkId": None},
                _ENT_B: {"targetNetworkId": None},
            }},
        "vm.agentless.migration-1": {"licenseType": "PAYG"},
        "common.approval-1": {},
    },
}


def _real_step(step_id):
    for workstream in _REAL_DEFINITION["workstreams"]:
        for step in workstream["steps"]:
            if step["stepId"] == step_id:
                return step
    raise KeyError(step_id)


def _annotated_definition():
    definition = copy.deepcopy(_REAL_DEFINITION)
    config_status_mod.annotate(definition, _REAL_PARAMS)
    return definition


class DepsHelperTests(unittest.TestCase):

    def test_merges_prerequisite_and_depends_on(self):
        step = {"prerequisites": [{"stepId": "a"}],
                "dependsOn": [{"stepId": "b"}]}
        self.assertEqual(deps_mod.merged_dep_ids(step), ["a", "b"])

    def test_dedupes_preserving_order(self):
        step = {"prerequisites": [{"stepId": "a"}, {"stepId": "b"}],
                "dependsOn": [{"stepId": "b"}, "c"]}
        self.assertEqual(deps_mod.merged_dep_ids(step), ["a", "b", "c"])

    def test_handles_missing_and_blank(self):
        self.assertEqual(deps_mod.merged_dep_ids({}), [])
        self.assertEqual(
            deps_mod.merged_dep_ids({"dependsOn": [{}, "", None]}), [])


class ConfigStatusTests(unittest.TestCase):

    def test_not_configured_when_all_null(self):
        self.assertEqual(
            config_status_mod.compute(
                _real_step("vm.agentless.setup-1"), _REAL_PARAMS),
            "NotConfigured")

    def test_partial_when_some_set(self):
        self.assertEqual(
            config_status_mod.compute(
                _real_step("vm.agentless.prepareEntity-1"), _REAL_PARAMS),
            "Partial (1/2)")

    def test_configured_when_all_set(self):
        self.assertEqual(
            config_status_mod.compute(
                _real_step("vm.agentless.migration-1"), _REAL_PARAMS),
            "Configured")

    def test_configured_when_no_required_inputs(self):
        self.assertEqual(
            config_status_mod.compute(
                _real_step("common.approval-1"), _REAL_PARAMS),
            "Configured")

    def test_unknown_without_params(self):
        self.assertEqual(
            config_status_mod.compute(
                _real_step("vm.agentless.setup-1"), None),
            "Unknown")

    def test_annotate_stamps_every_step(self):
        definition = _annotated_definition()
        statuses = {
            step["stepId"]: step["configurationStatus"]
            for ws in definition["workstreams"] for step in ws["steps"]}
        self.assertEqual(statuses["vm.agentless.setup-1"], "NotConfigured")
        self.assertEqual(
            statuses["vm.agentless.prepareEntity-1"], "Partial (1/2)")
        self.assertEqual(statuses["vm.agentless.migration-1"], "Configured")


class DefinitionGraphMergedDepsTests(unittest.TestCase):

    def test_edges_include_prerequisite_and_depends_on(self):
        graph = visualize_graph.build_definition_graph(_REAL_DEFINITION)
        edges = {(e.source, e.target) for e in graph.edges}
        self.assertIn(
            ("vm.agentless.setup-1", "vm.agentless.prepareEntity-1"), edges)
        self.assertIn(
            ("vm.agentless.prepareEntity-1", "common.approval-1"), edges)
        self.assertIn(
            ("vm.agentless.prepareEntity-1", "vm.agentless.migration-1"),
            edges)
        self.assertIn(
            ("common.approval-1", "vm.agentless.migration-1"), edges)


class DefinitionTableRealShapeTests(unittest.TestCase):

    def test_rows_use_entities_and_merged_deps(self):
        rows = transformers.definition_table(_annotated_definition())
        by_id = {row["Step Id"]: row for row in rows}
        migration = by_id["vm.agentless.migration-1"]
        self.assertEqual(migration["Entities"], 2)
        self.assertEqual(migration["Applications"], 0)
        self.assertEqual(migration["Configuration Status"], "Configured")
        self.assertIn(
            "waveapp:Prepare Entity", migration["Depends On"])
        self.assertIn("waveapp:Approval Gate", migration["Depends On"])


class VisualizeGridTests(unittest.TestCase):

    def _definition_view(self):
        return visualize_viewmodel.build_definition_view(
            _annotated_definition(), title="Def")

    def test_definition_view_groups_by_workstream(self):
        view = self._definition_view()
        self.assertEqual(
            [ws.name for ws in view.workstreams],
            ["Initialization", "waveapp"])
        self.assertEqual(view.step_count, 4)

    def test_definition_grid_is_default_and_offline(self):
        view = self._definition_view()
        graph = visualize_graph.build_definition_graph(
            _REAL_DEFINITION, title="Def")
        html_text = visualize_renderer.render(graph, view=view)
        self.assertIn(
            'Workstream: Initialization'
            '<span class="id-badge" title="Workstream id">'
            'workstream-0</span> (1)', html_text)
        self.assertIn(
            'Workstream: waveapp'
            '<span class="id-badge" title="Workstream id">'
            'workstream-1</span> (3)', html_text)
        self.assertIn("NotConfigured", html_text)
        self.assertIn('data-view="grid"', html_text)
        self.assertIn('data-view="diagram"', html_text)
        self.assertNotIn("http://", html_text)
        self.assertNotIn("https://", html_text)
        self.assertNotIn("src=", html_text)

    def test_definition_grid_has_portal_columns_and_stepref(self):
        view = self._definition_view()
        graph = visualize_graph.build_definition_graph(
            _REAL_DEFINITION, title="Def")
        html_text = visualize_renderer.render(graph, view=view)
        # Column header row matches the portal grid titles.
        self.assertIn('class="grid__head"', html_text)
        self.assertIn(">Steps<", html_text)
        self.assertIn(">Configuration status<", html_text)
        self.assertIn(">Step dependency<", html_text)
        self.assertIn(">Entities<", html_text)
        # Steps render as grid rows carrying the stepRef badge.
        self.assertIn('class="row__ref"', html_text)
        self.assertIn("vm.agentless.setup", html_text)

    def test_definition_metadata_header_renders(self):
        document = {
            "runbookId": "/subscriptions/s/rb/testrunbook",
            "waveId": "/subscriptions/s/waves/testwave",
            "generatedAt": "2026-07-25T06:51:42.6972548Z",
            "stepLibraryVersions": [
                {"namespace": "vm.agentless", "version": "1.0"}],
            "workstreams": [
                {"id": "w0", "displayName": "Init", "steps": [
                    {"stepId": "s1", "displayName": "Setup"}]},
            ],
        }
        view = visualize_viewmodel.build_definition_view(
            document, title="Def")
        graph = visualize_graph.build_definition_graph(document, title="Def")
        html_text = visualize_renderer.render(graph, view=view)
        self.assertIn('class="tab-meta"', html_text)
        self.assertIn("Runbook version", html_text)
        self.assertIn("vm.agentless 1.0", html_text)
        self.assertIn("Runbook resource id", html_text)
        self.assertIn("/subscriptions/s/rb/testrunbook", html_text)
        self.assertIn("Wave id", html_text)
        # generatedAt drives the header timestamp (normalised, offline)
        # and also appears as a dedicated metadata field.
        self.assertIn("2026-07-25 06:51:42 UTC", html_text)
        self.assertIn(">Generated<", html_text)

    def test_definition_rows_open_detail_drawer(self):
        document = {
            "runbookId": "/subscriptions/s/rb/tr",
            "generatedAt": "2026-01-01T00:00:00Z",
            "entities": [{"id": "e1", "displayName": "VM-App01"}],
            "workstreams": [
                {"id": "w0", "displayName": "Init", "steps": [
                    {"stepId": "s1", "displayName": "Prepare",
                     "stepRef": "vm.prep"},
                    {"stepId": "s2", "displayName": "Migrate",
                     "stepRef": "vm.migrate", "entities": ["e1"],
                     "prerequisites": [{"stepId": "s1", "waitFor": "wholeStep"}],
                     "dependsOn": [{"stepId": "s1", "waitFor": "sameEntity"}]}]},
            ],
        }
        view = visualize_viewmodel.build_definition_view(
            document, title="Def")
        graph = visualize_graph.build_definition_graph(document, title="Def")
        html_text = visualize_renderer.render(graph, view=view)
        # Rows are keyboard-accessible buttons wired to hidden detail blocks.
        self.assertIn('data-step="0"', html_text)
        self.assertIn('data-step="1"', html_text)
        self.assertIn('role="button"', html_text)
        self.assertIn('id="detail-1"', html_text)
        self.assertIn('class="drawer"', html_text)
        # The detail block carries the step's full context.
        self.assertIn("Step type", html_text)
        self.assertIn("vm.migrate", html_text)
        self.assertIn("VM-App01", html_text)
        self.assertIn("Prepare (Blocking)", html_text)
        self.assertIn("Prepare (Soft)", html_text)
        # Everything stays offline/self-contained.
        self.assertNotIn("https://", html_text)
        self.assertNotIn("http://", html_text)

    def test_definition_grid_and_drawer_show_applications(self):
        document = {
            "entityGroups": [
                {"id": "group-app", "displayName": "Application Tier"},
                {"id": "group-db", "displayName": "DB Tier"}],
            "workstreams": [{"id": "w0", "displayName": "Init", "steps": [
                {"stepId": "s1", "displayName": "Migrate",
                 "affectedEntityGroups": ["group-app", "group-db"]},
                {"stepId": "s2", "displayName": "Setup"}]}],
        }
        view = visualize_viewmodel.build_definition_view(
            document, title="Def")
        graph = visualize_graph.build_definition_graph(document, title="Def")
        html_text = visualize_renderer.render(graph, view=view)
        # Grid header + per-step Applications COUNT (not the full list).
        self.assertIn('class="col-apps">Applications<', html_text)
        self.assertIn('class="col-apps">2<', html_text)
        self.assertIn('class="col-apps">0<', html_text)
        # The full application list appears only in the detail drawer.
        self.assertNotIn('class="col-apps">Application Tier', html_text)
        self.assertIn("Application Tier", html_text)
        self.assertIn("DB Tier", html_text)

    def test_definition_renders_brand_bar_and_cli_help(self):
        document = {
            "workstreams": [
                {"id": "w0", "displayName": "Init", "steps": [
                    {"stepId": "s1", "displayName": "Setup"}]},
            ],
        }
        view = visualize_viewmodel.build_definition_view(
            document, title="Def")
        graph = visualize_graph.build_definition_graph(document, title="Def")
        html_text = visualize_renderer.render(graph, view=view)
        self.assertIn("Azure Migrate Runbook Viewer", html_text)
        self.assertIn('class="how-bar"', html_text)
        self.assertIn(
            "az migrate runbook execution start", html_text)
        self.assertIn(
            "az migrate runbook definition step add", html_text)

    def test_diagram_uses_workstream_swimlanes(self):
        graph = visualize_graph.build_definition_graph(
            _REAL_DEFINITION, title="Def")
        html_text = visualize_renderer.render(graph)
        # The SVG groups steps into labelled workstream bands and keeps
        # the dependency edges + per-step info (stepRef sub-label).
        self.assertIn('class="lane"', html_text)
        self.assertIn(
            'Workstream: Initialization'
            '<tspan class="svg-id"> workstream-0</tspan> (1)', html_text)
        self.assertIn(
            'Workstream: waveapp'
            '<tspan class="svg-id"> workstream-1</tspan> (3)', html_text)
        self.assertIn('class="edge"', html_text)
        self.assertIn("vm.agentless.migration", html_text)

    def test_diagram_swimlanes_follow_document_order(self):
        # Even when dependency-layer/id sorting would reverse them, the
        # diagram bands must follow the source workstream order so the
        # diagram is not reversed relative to the grid. Here both steps are
        # layer 0, and the second workstream's step id ('aaa') sorts before
        # the first ('zzz'); band order must still be Setup then Cleanup.
        document = {
            "workstreams": [
                {"id": "w0", "displayName": "Setup", "steps": [
                    {"stepId": "zzz", "displayName": "Prepare"}]},
                {"id": "w1", "displayName": "Cleanup", "steps": [
                    {"stepId": "aaa", "displayName": "Cleanup step"}]},
            ],
        }
        graph = visualize_graph.build_definition_graph(document, title="Def")
        html_text = visualize_renderer.render(graph)
        setup_at = html_text.find('Workstream: Setup')
        cleanup_at = html_text.find('Workstream: Cleanup')
        self.assertNotEqual(setup_at, -1)
        self.assertNotEqual(cleanup_at, -1)
        self.assertLess(setup_at, cleanup_at)

    def test_execution_grid_shows_progress_and_groups(self):
        view = visualize_viewmodel.build_execution_view(
            _STATUS_DOC, title="Exec")
        graph = visualize_graph.build_execution_graph(
            _STATUS_DOC, title="Exec")
        html_text = visualize_renderer.render(graph, view=view)
        self.assertIn(
            'Workstream: Web tier'
            '<span class="id-badge" title="Workstream id">'
            'ws1</span> (4)', html_text)
        self.assertIn("1/2 completed", html_text)
        self.assertNotIn("https://", html_text)


class VisualizeWorkstreamIdTests(unittest.TestCase):
    """The visualize output must surface the workstream id so users can
    copy it into ``runbook split`` / ``runbook merge``."""

    def _render(self, document):
        from azext_migrate.runbook.visualize import (
            graph as graph_mod,
            renderer as renderer_mod,
            viewmodel as viewmodel_mod,
        )
        graph = graph_mod.build_definition_graph(document)
        view = viewmodel_mod.build_definition_view(document, 't')
        return renderer_mod.render(graph, view)

    def test_workstream_id_in_visualize_header(self):
        document = {'workstreams': [{
            'id': 'ws-abc123',
            'displayName': 'Migration',
            'steps': [{'id': 's1', 'displayName': 'Cutover',
                       'configurationStatus': 'Configured'}],
        }]}
        html = self._render(document)
        # Grid header shows the workstream id as a greyish badge.
        self.assertIn(
            '<span class="id-badge" title="Workstream id">ws-abc123</span>',
            html)
        # SVG band shows the same id as a muted tspan.
        self.assertIn('<tspan class="svg-id"> ws-abc123</tspan>', html)

    def test_workstream_id_and_name_are_html_escaped(self):
        document = {'workstreams': [{
            'id': '<script>x</script>',
            'displayName': '<b>ws</b>',
            'steps': [{'id': 's1', 'displayName': 'a'}],
        }]}
        html = self._render(document)
        self.assertNotIn('<script>x</script>', html)
        self.assertIn('&lt;script&gt;x&lt;/script&gt;', html)


class _RecordingGroup:
    """Minimal stand-in for an Azure CLI command group context manager."""

    def __init__(self, name, recorded):
        self._name = name
        self._recorded = recorded

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def custom_command(self, name, *_args, **_kwargs):
        self._recorded.append('%s %s' % (self._name, name))

    def custom_show_command(self, name, *_args, **_kwargs):
        self._recorded.append('%s %s' % (self._name, name))


class _RecordingLoader:
    def __init__(self):
        self.recorded = []

    def command_group(self, name, **_kwargs):
        return _RecordingGroup(name, self.recorded)


class CommandRegistrationTests(unittest.TestCase):
    def _registered_commands(self):
        from azext_migrate.runbook import commands as runbook_commands
        loader = _RecordingLoader()
        runbook_commands.load_runbook_command_table(loader)
        return loader.recorded

    def test_visualize_and_step_commands_registered(self):
        commands = self._registered_commands()
        for expected in (
                'migrate runbook definition visualize',
                'migrate runbook execution visualize',
                'migrate runbook execution step retry',
                'migrate runbook execution step approve',
                'migrate runbook execution step complete',
                'migrate runbook parameter download',
                'migrate runbook parameter upload',
                'migrate runbook execution parameter download',
                'migrate runbook execution parameter upload'):
            self.assertIn(expected, commands)


class RunbookValidatorTests(unittest.TestCase):

    def test_definition_visualize_requires_identity(self):
        ns = SimpleNamespace(from_file=None, resource_group_name=None,
                             project_name=None, runbook_name=None)
        with self.assertRaises(RequiredArgumentMissingError):
            validators_mod.validate_definition_visualize(ns)

    def test_definition_visualize_from_file_ok(self):
        validators_mod.validate_definition_visualize(
            SimpleNamespace(from_file='x.json'))

    def test_execution_visualize_requires_execution_id(self):
        ns = SimpleNamespace(from_file=None, resource_group_name=RG,
                             project_name=PROJECT, runbook_name=RUNBOOK,
                             execution_id=None)
        with self.assertRaises(RequiredArgumentMissingError):
            validators_mod.validate_execution_visualize(ns)

    def test_execution_visualize_full_identity_ok(self):
        validators_mod.validate_execution_visualize(
            SimpleNamespace(from_file=None, resource_group_name=RG,
                            project_name=PROJECT, runbook_name=RUNBOOK,
                            execution_id='e1'))

    def test_execution_visualize_from_file_ok(self):
        validators_mod.validate_execution_visualize(
            SimpleNamespace(from_file='x.json'))


class ExecutionHelperTests(unittest.TestCase):

    def test_status_payload_unwraps_execution_status(self):
        payload = execution_cmds._status_payload({
            'generatedAt': 't', 'runbookId': 'r',
            'executionStatus': {'status': 'InProgress'}})
        self.assertEqual(payload['status'], 'InProgress')
        self.assertEqual(payload['generatedAt'], 't')
        self.assertEqual(payload['runbookId'], 'r')

    def test_status_payload_unwraps_properties(self):
        payload = execution_cmds._status_payload({
            'executionId': 'e', 'properties': {'status': 'Completed'}})
        self.assertEqual(payload['status'], 'Completed')
        self.assertEqual(payload['executionId'], 'e')

    def test_status_payload_passthrough(self):
        self.assertIsNone(execution_cmds._status_payload(None))
        bare = {'workstreams': []}
        self.assertIs(execution_cmds._status_payload(bare), bare)

    def test_execution_id_from_result_variants(self):
        self.assertEqual(
            execution_cmds._execution_id_from_result({'name': 'e1'}), 'e1')
        self.assertEqual(
            execution_cmds._execution_id_from_result(
                {'id': '/a/executions/e2'}), 'e2')
        self.assertEqual(
            execution_cmds._execution_id_from_result(
                {'properties': {'executionId': 'e3'}}), 'e3')
        self.assertIsNone(execution_cmds._execution_id_from_result('x'))

    def test_project_filters_step(self):
        doc = {'workstreams': [{'steps': [
            {'stepId': 's1'}, {'stepId': 's2'}]}]}
        self.assertEqual(
            execution_cmds._project(doc, 's2'), {'stepId': 's2'})

    def test_project_flat_and_not_found(self):
        doc = {'steps': [{'id': 'a'}]}
        self.assertEqual(execution_cmds._project(doc, 'a'), {'id': 'a'})
        self.assertIs(execution_cmds._project(doc, 'zzz'), doc)
        self.assertIs(execution_cmds._project(doc, None), doc)
        self.assertEqual(execution_cmds._project('x', 'a'), 'x')

    def test_terminal_states(self):
        self.assertTrue(execution_cmds._terminal({'status': 'Completed'}))
        self.assertTrue(
            execution_cmds._terminal({'properties': {'state': 'Failed'}}))
        self.assertFalse(execution_cmds._terminal({'status': 'InProgress'}))
        self.assertFalse(execution_cmds._terminal({}))

    def test_render_does_not_crash(self):
        execution_cmds._render(_STATUS_TOOL_DOC)
        execution_cmds._render({})


class ExecutionStatusCommandTests(unittest.TestCase):

    def setUp(self):
        sub_patch = mock.patch.object(
            execution_cmds, 'get_subscription_id', return_value=SUB)
        self.addCleanup(sub_patch.stop)
        sub_patch.start()
        client_patch = mock.patch.object(execution_cmds, 'ArmClient')
        self.addCleanup(client_patch.stop)
        self.client = client_patch.start().return_value

    def _exec_id(self):
        project = arm_ids.migrate_project_id(SUB, RG, PROJECT)
        return arm_ids.execution_id(
            arm_ids.runbook_id(project, RUNBOOK), 'e1')

    def test_status_download_url_error_when_no_sas(self):
        self.client.post_action.return_value = {}
        with self.assertRaises(CLIInternalError):
            execution_cmds._status_download_url(mock.Mock(), self._exec_id())

    def test_status_download_url_returns_sas(self):
        self.client.post_action.return_value = {
            'properties': {'sasUrl': 'https://x/blob'}}
        self.assertEqual(
            execution_cmds._status_download_url(mock.Mock(), self._exec_id()),
            'https://x/blob')

    def test_fetch_status_downloads_and_unwraps(self):
        with mock.patch.object(execution_cmds, '_status_download_url',
                               return_value='https://x'), \
             mock.patch.object(execution_cmds.files, 'download_bytes',
                               return_value=b'{}'), \
             mock.patch.object(
                 execution_cmds.files, 'read_status_json',
                 return_value={'executionStatus': {'status': 'InProgress'}}):
            result = execution_cmds._fetch_status(
                mock.Mock(), self._exec_id())
        self.assertEqual(result['status'], 'InProgress')

    def test_show_returns_projected_status(self):
        with mock.patch.object(
                execution_cmds, '_fetch_status',
                return_value={'workstreams': [
                    {'steps': [{'stepId': 's1'}]}]}):
            result = execution_cmds.show(
                mock.Mock(), RG, PROJECT, RUNBOOK, 'e1', step_id='s1')
        self.assertEqual(result, {'stepId': 's1'})

    def test_pause_resume_cancel_perform_action(self):
        for fn in (execution_cmds.pause, execution_cmds.resume,
                   execution_cmds.cancel):
            self.client.post_action.reset_mock()
            self.client.post_action.return_value = {'ok': True}
            self.assertEqual(
                fn(mock.Mock(), RG, PROJECT, RUNBOOK, 'e1'), {'ok': True})
            self.client.post_action.assert_called_once()

    def test_visualize_from_file_writes_and_opens(self):
        status = {'executionStatus': {'status': 'InProgress',
                                      'workstreams': []}}
        with mock.patch.object(execution_cmds.files, 'read_json_file',
                               return_value=status), \
             mock.patch.object(execution_cmds.files, 'resolve_output_path',
                               return_value='out.html'), \
             mock.patch.object(execution_cmds.files, 'write_text',
                               return_value='out.html'), \
             mock.patch.object(execution_cmds.files,
                               'open_in_browser') as browser:
            result = execution_cmds.visualize(
                mock.Mock(), runbook_name=RUNBOOK, execution_id='e1',
                from_file='f.json')
        self.assertEqual(result, {'path': 'out.html'})
        browser.assert_called_once()

    def test_visualize_service_path_writes_and_opens(self):
        with mock.patch.object(
                execution_cmds, '_fetch_status',
                return_value={'status': 'InProgress', 'workstreams': []}), \
             mock.patch.object(execution_cmds.files, 'resolve_output_path',
                               return_value='out.html'), \
             mock.patch.object(execution_cmds.files, 'write_text',
                               return_value='out.html'), \
             mock.patch.object(execution_cmds.files,
                               'open_in_browser') as browser:
            result = execution_cmds.visualize(
                mock.Mock(), RG, PROJECT, RUNBOOK, 'e1')
        self.assertEqual(result, {'path': 'out.html'})
        browser.assert_called_once()


class ConfigStatusBranchTests(unittest.TestCase):

    def test_is_empty_variants(self):
        self.assertTrue(config_status_mod._is_empty(''))
        self.assertTrue(config_status_mod._is_empty('  '))
        self.assertTrue(config_status_mod._is_empty([]))
        self.assertFalse(config_status_mod._is_empty('x'))
        self.assertFalse(config_status_mod._is_empty([1]))

    def test_compute_unknown_when_no_inputs(self):
        self.assertEqual(
            config_status_mod.compute({'stepId': 's'}, None),
            config_status_mod.UNKNOWN)

    def test_compute_unknown_when_untracked(self):
        self.assertEqual(
            config_status_mod.compute(
                {'stepId': 's', 'stepRef': 't'}, {'stepInputs': {}}),
            config_status_mod.UNKNOWN)

    def test_compute_configured_when_no_required(self):
        self.assertEqual(
            config_status_mod.compute(
                {'stepId': 's', 'stepRef': 't'},
                {'stepInputs': {'s': {}}, 'schema': {}}),
            config_status_mod.CONFIGURED)

    def test_compute_partial_and_not_configured(self):
        schema = {'t': {'a': {'required': True}, 'b': {'required': True}}}
        partial = config_status_mod.compute(
            {'stepId': 's', 'stepRef': 't'},
            {'schema': schema, 'stepInputs': {'s': {'a': 'x'}}})
        self.assertTrue(partial.startswith('Partial'))
        self.assertEqual(
            config_status_mod.compute(
                {'stepId': 's', 'stepRef': 't'},
                {'schema': schema, 'stepInputs': {'s': {}}}),
            config_status_mod.NOT_CONFIGURED)

    def test_compute_entity_scope(self):
        schema = {'t': {'a': {'required': True, 'scope': 'Entity'}}}
        step = {'stepId': 's', 'stepRef': 't', 'entities': ['vm1']}
        self.assertEqual(
            config_status_mod.compute(step, {
                'schema': schema,
                'stepInputs': {'s': {'workloadOverrides': {'vm1': {}}}}}),
            config_status_mod.NOT_CONFIGURED)
        self.assertEqual(
            config_status_mod.compute(step, {
                'schema': schema,
                'stepInputs': {
                    's': {'workloadOverrides': {'vm1': {'a': 'x'}}}}}),
            config_status_mod.CONFIGURED)

    def test_compute_entity_scope_no_entities(self):
        schema = {'t': {'a': {'required': True, 'scope': 'Entity'}}}
        self.assertEqual(
            config_status_mod.compute(
                {'stepId': 's', 'stepRef': 't', 'entities': []},
                {'schema': schema, 'stepInputs': {'s': {}}}),
            config_status_mod.NOT_CONFIGURED)

    def test_annotate_non_dict_passthrough(self):
        self.assertIsNone(config_status_mod.annotate(None, {}))


class TransformerBranchTests(unittest.TestCase):

    def test_execution_table_single_step_dict(self):
        rows = transformers.execution_table(
            {'stepId': 's1', 'status': 'Completed'})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['Step Id'], 's1')

    def test_workload_progress_explicit_scalar(self):
        rows = transformers.execution_table(
            {'steps': [{'stepId': 's', 'workloadProgress': '5 of 5'}]})
        self.assertEqual(rows[0]['Workload Progress'], '5 of 5')

    def test_workload_progress_none_without_entities(self):
        rows = transformers.execution_table({'steps': [{'stepId': 's'}]})
        self.assertIsNone(rows[0]['Workload Progress'])


class DepsBranchTests(unittest.TestCase):

    def test_dep_labels_execution_properties_envelope(self):
        labels = deps_mod.build_dep_labels({'properties': {'workstreams': [
            None,
            {'displayName': 'WS', 'steps': [
                {'stepId': 's1', 'displayName': 'Step One'}]}]}})
        self.assertEqual(labels['s1'], 'WS:Step One')

    def test_dep_labels_flat_steps_no_workstream(self):
        labels = deps_mod.build_dep_labels(
            {'steps': [{'stepId': 's2', 'displayName': 'Solo'}]})
        self.assertEqual(labels['s2'], 'Solo')

    def test_dep_labels_non_dict_document(self):
        self.assertEqual(deps_mod.build_dep_labels([1, 2]), {})


class ViewmodelBranchTests(unittest.TestCase):

    def test_unwrap_properties_envelope(self):
        view = visualize_viewmodel.build_execution_view(
            {'properties': {'status': 'InProgress', 'workstreams': [
                {'displayName': 'W', 'steps': [
                    {'stepId': 's', 'status': 'Completed'}]}]}}, title='X')
        self.assertEqual(view.workstreams[0].name, 'W')

    def test_progress_text_explicit_scalar(self):
        view = visualize_viewmodel.build_execution_view(
            {'workstreams': [{'steps': [
                {'stepId': 's', 'workloadProgress': '3 of 3'}]}]}, title='X')
        self.assertEqual(
            view.workstreams[0].steps[0].workload_progress, '3 of 3')

    def test_entity_status_dict_shape(self):
        view = visualize_viewmodel.build_execution_view(
            {'workstreams': [{'steps': [{'stepId': 's', 'entityExecutions': [
                {'entity': 'e1', 'status': {'state': 'Completed'}}]}]}]},
            title='X')
        self.assertEqual(
            view.workstreams[0].steps[0].entities[0].status, 'Completed')


if __name__ == '__main__':
    unittest.main()
