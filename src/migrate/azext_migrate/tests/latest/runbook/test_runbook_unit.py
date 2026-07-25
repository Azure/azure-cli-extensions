# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import io
import json
import os
import copy
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
from azext_migrate.runbook.cmds import runbook as runbook_cmds
from azext_migrate.runbook.cmds import definition as definition_cmds
from azext_migrate.runbook.cmds import definition_step as step_cmds
from azext_migrate.runbook.cmds import (
    definition_workstream as workstream_cmds,
)
from azext_migrate.runbook.cmds import execution as execution_cmds
from azext_migrate.runbook.cmds import execution_step as execution_step_cmds
from azext_migrate.runbook.cmds import parameter as parameter_cmds
from azext_migrate.runbook.visualize import graph as visualize_graph
from azext_migrate.runbook.visualize import renderer as visualize_renderer
from azext_migrate.runbook.visualize import viewmodel as visualize_viewmodel
from azext_migrate.runbook.constants import (
    SCOPE_TYPE_WAVE,
    RUNBOOK_STATUS_VALUES,
    STEP_TYPE_APPROVAL,
    STEP_TYPE_CUSTOM_SCRIPT,
)
from azext_migrate.runbook.models import ExecutionAction
from azext_migrate.runbook.validators import (
    validate_generate,
    validate_step_add,
    validate_step_approve,
    validate_step_complete,
)

SUB = "00000000-0000-0000-0000-000000000000"
RG = "myRg"
PROJECT = "myProject"
RUNBOOK = "myRunbook"
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
                "ScopeType": SCOPE_TYPE_WAVE,
                "WaveId": "/waves/myWave"}}})

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
            ["Generating", "New", "ReadyToStart", "InExecution",
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

        self.assertEqual(
            result, {"properties": {"state": "ExecutionSucceeded"}})
        # Initial DELETE + two status polls.
        self.assertEqual(self.send.call_count, 3)
        polled_url = self.send.call_args_list[1][0][2]
        self.assertIn(
            "api-version=" + WAVE_OPERATIONS_API_VERSION, polled_url)

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

    def test_regenerate_posts_action(self):
        self.client.post_action.return_value = {"ok": True}
        result = runbook_cmds.regenerate(
            mock.Mock(), RG, PROJECT, RUNBOOK, no_wait=True)
        self.assertEqual(result, {"ok": True})
        self.client.post_action.assert_called_once_with(
            self._runbook_id(), 'Regenerate', no_wait=True)


class RunbookDefinitionTransformerTests(unittest.TestCase):

    def test_workstreams_flattened_to_steps(self):
        definition = {"workstreams": [
            {"id": "w1", "steps": [
                {"stepId": "s1", "displayName": "Step One",
                 "prerequisite": [{"step": "b"}],
                 "dependsOn": [{"step": "a"}],
                 "configurationStatus": "Configured",
                 "entities": ["e1", "e2"]}]},
            {"id": "w2", "steps": [{"stepId": "s2"}]},
        ]}
        rows = transformers.definition_table(definition)
        self.assertEqual([r["Step Id"] for r in rows], ["s1", "s2"])
        self.assertEqual([r["Workstream Id"] for r in rows], ["w1", "w2"])
        self.assertEqual(rows[0]["Step Name"], "Step One")
        self.assertEqual(rows[0]["Depends On"], "b a")
        self.assertEqual(rows[0]["Configuration Status"], "Configured")
        self.assertEqual(rows[0]["Workloads"], 2)
        self.assertEqual(rows[0]["Applications"], "-")

    def test_single_workstream(self):
        rows = transformers.definition_table(
            {"id": "w1", "steps": [{"id": "s1"}]})
        self.assertEqual([r["Step Id"] for r in rows], ["s1"])
        self.assertEqual(rows[0]["Workstream Id"], "w1")

    def test_single_step(self):
        rows = transformers.definition_table({"stepId": "s9"})
        self.assertEqual(rows[0]["Step Id"], "s9")

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
            "rb-x-spec.json": '{"runbookSpec": {"id": "r"}}',
        })
        spec = files.read_spec_json(zip_bytes)
        self.assertEqual(spec, {"runbookSpec": {"id": "r"}})

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

    def test_extract_parameters_file_by_content(self):
        zip_bytes = _make_zip({
            "runbook.json": '{"runbookSpec": {}}',
            "user-inputs.json": '{"runbookInputs": {"stepInputs": {}}}',
        })
        name, data = files.extract_parameters_file(zip_bytes)
        self.assertEqual(name, "user-inputs.json")
        self.assertIn(b"runbookInputs", data)

    def test_extract_parameters_file_none_when_only_spec(self):
        zip_bytes = _make_zip({"rb-x-spec.json": '{"runbookSpec": {}}'})
        self.assertIsNone(files.extract_parameters_file(zip_bytes))

    def test_read_spec_json_selects_spec_by_content(self):
        # Real service names the members runbook.json / user-inputs.json,
        # neither of which carries a -spec.json suffix. Selection must fall
        # back to content so the parameters file is never returned as the
        # definition.
        for members in (
                {"user-inputs.json": '{"runbookInputs": {"schema": {}}}',
                 "runbook.json":
                     '{"runbookSpec": {"workstreams": []}}'},
                {"runbook.json":
                     '{"runbookSpec": {"workstreams": []}}',
                 "user-inputs.json": '{"runbookInputs": {"schema": {}}}'}):
            spec = files.read_spec_json(_make_zip(members))
            self.assertIn("runbookSpec", spec)
            self.assertIn("workstreams", spec["runbookSpec"])

    def test_read_spec_json_none_when_only_parameters(self):
        zip_bytes = _make_zip({
            "user-inputs.json":
                '{"runbookInputs": {"stepInputs": {}}}'})
        self.assertIsNone(files.read_spec_json(zip_bytes))

    def test_extract_parameters_selects_inputs_by_content(self):
        # Mirror of the spec test: the params file must win over the spec
        # regardless of member ordering or non-standard names.
        for members in (
                {"runbook.json":
                     '{"runbookSpec": {"workstreams": []}}',
                 "user-inputs.json":
                     '{"runbookInputs": {"schema": {}}}'},
                {"user-inputs.json":
                     '{"runbookInputs": {"schema": {}}}',
                 "runbook.json":
                     '{"runbookSpec": {"workstreams": []}}'}):
            name, data = files.extract_parameters_file(_make_zip(members))
            self.assertEqual(name, "user-inputs.json")
            self.assertIn("runbookInputs", json.loads(data.decode()))

    def test_read_parameters_json_by_content(self):
        zip_bytes = _make_zip({
            "runbook.json": '{"runbookSpec": {"workstreams": []}}',
            "user-inputs.json":
                '{"runbookInputs": {"stepInputs": {"s1": {}}}}'})
        params = files.read_parameters_json(zip_bytes)
        self.assertEqual(params, {"stepInputs": {"s1": {}}})

    def test_parameters_excludes_derived_input(self):
        # The real archive ships runbook.json (spec), user-inputs.json and
        # derived-input.json (both runbookInputs-shaped). Only user-inputs
        # is the parameters file; derived-input must never be selected.
        zip_bytes = _make_zip({
            "runbook.json": '{"runbookSpec": {"workstreams": []}}',
            "derived-input.json":
                '{"runbookInputs": {"stepInputs": {"d": {}}}}',
            "user-inputs.json":
                '{"runbookInputs": {"stepInputs": {"u": {}}}}'})
        name, data = files.extract_parameters_file(zip_bytes)
        self.assertEqual(name, "user-inputs.json")
        self.assertEqual(
            files.read_parameters_json(zip_bytes), {"stepInputs": {"u": {}}})
        self.assertNotIn("derived", data.decode())

    def test_read_spec_ignores_input_documents(self):
        zip_bytes = _make_zip({
            "derived-input.json": '{"runbookInputs": {"schema": {}}}',
            "user-inputs.json": '{"runbookInputs": {"schema": {}}}',
            "runbook.json":
                '{"runbookSpec": {"workstreams": [{"id": "w1"}]}}'})
        spec = files.read_spec_json(zip_bytes)
        self.assertIn("runbookSpec", spec)

    def test_extract_definition_files_includes_inputs_not_derived(self):
        zip_bytes = _make_zip({
            "runbook.json": '{"runbookSpec": {"workstreams": []}}',
            "user-inputs.json": '{"runbookInputs": {}}',
            "derived-input.json": '{"runbookInputs": {}}',
            "runbook.md": "# docs",
        })
        with tempfile.TemporaryDirectory() as tmp:
            written = files.extract_definition_files(zip_bytes, tmp)
            names = sorted(os.path.basename(p) for p in written)
            self.assertEqual(
                names, ["runbook.json", "runbook.md", "user-inputs.json"])
            self.assertTrue(
                os.path.exists(os.path.join(tmp, "user-inputs.json")))
            self.assertFalse(
                os.path.exists(os.path.join(tmp, "derived-input.json")))



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
        self.client.post_action.return_value = {
            "downloadUrl": "https://blob/x"}
        zip_bytes = _make_zip({
            "rb-x-spec.json":
                '{"runbookSpec": {"workstreams": '
                '[{"id": "w1", "steps": []}]}}'})
        with mock.patch.object(
                definition_cmds.files, 'download_bytes',
                return_value=zip_bytes) as dl:
            result = definition_cmds.show(
                mock.Mock(), RG, PROJECT, RUNBOOK, workstream_id="w1")
        dl.assert_called_once_with("https://blob/x")
        self.client.post_action.assert_called_once_with(
            self._runbook_id(), 'GenerateDownloadUrl')
        self.assertEqual(result["id"], "w1")

    def test_show_raises_without_download_url(self):
        self.client.post_action.return_value = {"expiresAt": "t"}
        with self.assertRaises(CLIInternalError):
            definition_cmds.show(mock.Mock(), RG, PROJECT, RUNBOOK)

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
        body = models.build_add_step_body("Manual", "Step 1")
        self.assertEqual(body["stepName"], "Step 1")
        self.assertEqual(body["displayName"], "Step 1")
        self.assertEqual(body["stepRef"], "Manual")
        self.assertEqual(body["migrationEntityIds"], [])
        self.assertEqual(body["dependsOn"], [])
        self.assertNotIn("approvalType", body)

    def test_build_add_step_body_approval(self):
        body = models.build_add_step_body(
            "Approval", "Approve", approval_type="Full",
            depends_on=["s0"], step_description="desc")
        self.assertEqual(body["stepRef"], "Approval")
        self.assertEqual(body["approvalType"], "Full")
        self.assertEqual(body["dependsOn"], [{"Mode": 0, "stepId": "s0"}])
        self.assertEqual(body["description"], "desc")

    def test_build_add_step_body_custom_script(self):
        body = models.build_add_step_body(
            "CustomScript", "Run", run_mode="Once",
            execution_target="Appliance")
        self.assertEqual(body["runMode"], "Once")
        self.assertEqual(body["executionTarget"], "Appliance")

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
            "dependsOn": [{"Mode": 0, "stepId": "s0"}]})

    def test_build_delete_step_body(self):
        self.assertEqual(
            models.build_delete_step_body("s1"), {"stepId": "s1"})

    def test_build_split_workstream_body(self):
        body = models.build_split_workstream_body(
            "ws1", "new", ["e1", "e2"])
        self.assertEqual(body, {
            "sourceWorkstreamId": "ws1",
            "stepIds": [],
            "migrationEntityIds": ["e1", "e2"],
            "newWorkstreamName": "new"})

    def test_build_merge_workstreams_body(self):
        body = models.build_merge_workstreams_body(["w1", "w2"], "merged")
        self.assertEqual(body, {
            "workstreamId": ["w1", "w2"],
            "newWorkstreamName": "merged"})


class StepValidatorTests(unittest.TestCase):

    def _ns(self, **kwargs):
        defaults = dict(
            step_type=None, approval_type=None, run_mode=None,
            execution_target=None)
        defaults.update(kwargs)
        return SimpleNamespace(**defaults)

    def test_manual_ok(self):
        validate_step_add(self._ns(step_type="Manual"))

    def test_approval_requires_approval_type(self):
        with self.assertRaises(RequiredArgumentMissingError):
            validate_step_add(self._ns(step_type=STEP_TYPE_APPROVAL))

    def test_approval_ok_with_type(self):
        validate_step_add(self._ns(
            step_type=STEP_TYPE_APPROVAL, approval_type="Full"))

    def test_approval_type_rejected_for_manual(self):
        with self.assertRaises(InvalidArgumentValueError):
            validate_step_add(self._ns(
                step_type="Manual", approval_type="Full"))

    def test_run_mode_rejected_for_manual(self):
        with self.assertRaises(InvalidArgumentValueError):
            validate_step_add(self._ns(
                step_type="Manual", run_mode="Once"))

    def test_execution_target_rejected_for_approval(self):
        with self.assertRaises(InvalidArgumentValueError):
            validate_step_add(self._ns(
                step_type=STEP_TYPE_APPROVAL, approval_type="Full",
                execution_target="Appliance"))

    def test_custom_script_ok(self):
        validate_step_add(self._ns(
            step_type=STEP_TYPE_CUSTOM_SCRIPT, run_mode="Once",
            execution_target="Appliance"))


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
        result = step_cmds.add(
            mock.Mock(), RG, PROJECT, RUNBOOK, "Manual", "Step 1")
        self.assertEqual(result, {"ok": True})
        self.client.post_action.assert_called_once_with(
            self._runbook_id(), 'AddStep',
            models.build_add_step_body("Manual", "Step 1"))

    def test_update_posts_update_step(self):
        self.client.post_action.return_value = {"ok": True}
        step_cmds.update(
            mock.Mock(), RG, PROJECT, RUNBOOK, "s1", step_name="New")
        self.client.post_action.assert_called_once_with(
            self._runbook_id(), 'UpdateStep',
            {"stepId": "s1", "displayName": "New"})

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
        workstream_cmds.split(
            mock.Mock(), RG, PROJECT, RUNBOOK, "ws1", "new", ["e1"])
        self.client.post_action.assert_called_once_with(
            self._runbook_id(), 'SplitWorkstream',
            models.build_split_workstream_body("ws1", "new", ["e1"]))

    def test_merge_posts_merge_workstreams(self):
        self.client.post_action.return_value = {"ok": True}
        workstream_cmds.merge(
            mock.Mock(), RG, PROJECT, RUNBOOK, ["w1", "w2"], "merged")
        self.client.post_action.assert_called_once_with(
            self._runbook_id(), 'MergeWorkstreams',
            {"workstreamId": ["w1", "w2"],
             "newWorkstreamName": "merged"})


class ExecutionModelTests(unittest.TestCase):

    def test_start_body_is_empty_properties(self):
        self.assertEqual(
            models.build_start_execution_body(), {"properties": {}})

    def test_action_enum_values(self):
        self.assertEqual(int(ExecutionAction.START), 0)
        self.assertEqual(int(ExecutionAction.PAUSE), 1)
        self.assertEqual(int(ExecutionAction.RESUME), 2)
        self.assertEqual(int(ExecutionAction.CANCEL), 3)
        self.assertEqual(int(ExecutionAction.RETRY), 4)

    def test_perform_action_body_shape(self):
        body = models.build_perform_action_body(ExecutionAction.PAUSE)
        self.assertEqual(
            body,
            {"action": 1, "targetId": "", "migrationEntityIds": []})
        self.assertIsInstance(body["action"], int)

    def test_perform_action_body_with_target(self):
        body = models.build_perform_action_body(
            ExecutionAction.RESUME, target_id="t1", entity_ids=["e1"])
        self.assertEqual(
            body,
            {"action": 2, "targetId": "t1",
             "migrationEntityIds": ["e1"]})


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
        self.assertEqual(rows[0]["Id"], "s1")
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
        self.assertEqual(rows[0]["Id"], "s2")
        self.assertEqual(rows[0]["Step Status"], "Succeeded")


class ExecutionCommandTests(unittest.TestCase):

    def setUp(self):
        sub_patch = mock.patch.object(
            execution_cmds, 'get_subscription_id', return_value=SUB)
        self.addCleanup(sub_patch.stop)
        sub_patch.start()
        client_patch = mock.patch.object(execution_cmds, 'ArmClient')
        self.addCleanup(client_patch.stop)
        self.client = client_patch.start().return_value

    def _runbook_id(self):
        project = arm_ids.migrate_project_id(SUB, RG, PROJECT)
        return arm_ids.runbook_id(project, RUNBOOK)

    def test_start_puts_execution(self):
        self.client.put.return_value = {"ok": True}
        result = execution_cmds.start(mock.Mock(), RG, PROJECT, RUNBOOK)
        self.assertEqual(result, {"ok": True})
        self.client.put.assert_called_once()
        args, kwargs = self.client.put.call_args
        self.assertTrue(
            args[0].startswith(self._runbook_id() + '/executions/'))
        self.assertEqual(args[1], {"properties": {}})
        self.assertFalse(kwargs.get('no_wait'))

    def test_start_no_wait(self):
        execution_cmds.start(
            mock.Mock(), RG, PROJECT, RUNBOOK, no_wait=True)
        _, kwargs = self.client.put.call_args
        self.assertTrue(kwargs.get('no_wait'))

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
            'GenerateDownloadUrl')
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

    def test_pause_posts_perform_action(self):
        self.client.post_action.return_value = {"ok": True}
        execution_cmds.pause(mock.Mock(), RG, PROJECT, RUNBOOK, "e1")
        self.client.post_action.assert_called_once_with(
            arm_ids.execution_id(self._runbook_id(), "e1"),
            'PerformAction',
            {"action": 1, "targetId": "", "migrationEntityIds": []})

    def test_resume_posts_perform_action(self):
        self.client.post_action.return_value = {"ok": True}
        execution_cmds.resume(mock.Mock(), RG, PROJECT, RUNBOOK, "e1")
        _, args, _ = self.client.post_action.mock_calls[0]
        self.assertEqual(args[2]["action"], 2)

    def test_cancel_posts_perform_action(self):
        self.client.post_action.return_value = {"ok": True}
        execution_cmds.cancel(mock.Mock(), RG, PROJECT, RUNBOOK, "e1")
        _, args, _ = self.client.post_action.mock_calls[0]
        self.assertEqual(args[2]["action"], 3)


class ExecutionStepModelTests(unittest.TestCase):

    def test_build_retry_step_body(self):
        body = models.build_retry_step_body("step1")
        self.assertEqual(body, {
            "action": 4, "targetId": "step1",
            "migrationEntityIds": []})
        self.assertIsInstance(body["action"], int)

    def test_build_approve_step_body_full(self):
        body = models.build_approve_step_body("step1")
        self.assertEqual(body, {
            "action": "Approve", "targetId": "step1",
            "migrationEntityIds": []})

    def test_build_approve_step_body_partial(self):
        body = models.build_approve_step_body(
            "step1", entity_ids=["e1", "e2"])
        self.assertEqual(body["migrationEntityIds"], ["e1", "e2"])

    def test_build_complete_step_body(self):
        body = models.build_complete_step_body("step1", "done")
        self.assertEqual(body, {
            "action": "Complete", "targetId": "step1",
            "migrationEntityIds": [], "comment": "done"})


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
            {"action": 4, "targetId": "step1",
             "migrationEntityIds": []})

    def test_approve_posts_provide_approval(self):
        self.client.post_action.return_value = {"ok": True}
        execution_step_cmds.approve(
            mock.Mock(), RG, PROJECT, RUNBOOK, "e1", "step1",
            entities=["ent1"])
        self.client.post_action.assert_called_once_with(
            self._execution_id(), 'ProvideApproval',
            {"action": "Approve", "targetId": "step1",
             "migrationEntityIds": ["ent1"]})

    def test_complete_posts_update_step_status(self):
        self.client.post_action.return_value = {"ok": True}
        execution_step_cmds.complete(
            mock.Mock(), RG, PROJECT, RUNBOOK, "e1", "step1", "done")
        self.client.post_action.assert_called_once_with(
            self._execution_id(), 'UpdateStepStatus',
            {"action": "Complete", "targetId": "step1",
             "migrationEntityIds": [], "comment": "done"})


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
        self.client.post_action.return_value = {
            "downloadUrl": "https://blob/x"}
        zip_bytes = _make_zip({
            "runbook.json": '{"runbookSpec": {}}',
            "user-inputs.json": '{"runbookInputs": {"stepInputs": {}}}',
        })
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(
                    parameter_cmds.files, 'download_bytes',
                    return_value=zip_bytes) as dl:
                result = parameter_cmds.download(
                    mock.Mock(), RG, PROJECT, RUNBOOK, file=tmp)
            dl.assert_called_once_with("https://blob/x")
            self.client.post_action.assert_called_once_with(
                self._runbook_id(), 'GenerateDownloadUrl')
            expected = os.path.join(tmp, "user-inputs.json")
            self.assertEqual(result, {"path": expected})
            with open(expected) as handle:
                self.assertEqual(
                    handle.read(), '{"runbookInputs": {"stepInputs": {}}}')

    def test_download_raises_without_parameters_file(self):
        self.client.post_action.return_value = {
            "downloadUrl": "https://blob/x"}
        zip_bytes = _make_zip({"rb-x-spec.json": '{"runbookSpec": {}}'})
        with mock.patch.object(
                parameter_cmds.files, 'download_bytes',
                return_value=zip_bytes):
            with self.assertRaises(CLIInternalError):
                parameter_cmds.download(
                    mock.Mock(), RG, PROJECT, RUNBOOK)


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
        by_id = {row['Id']: row for row in rows}
        self.assertEqual(by_id['setup']['Step Status'], 'Completed')
        self.assertEqual(by_id['network']['Step Status'], 'Failed')
        self.assertEqual(by_id['cutover']['Step Status'], 'Blocked')

    def test_execution_table_formats_depends_on(self):
        rows = transformers.execution_table(_STATUS_DOC)
        by_id = {row['Id']: row for row in rows}
        self.assertEqual(by_id['dataSync']['Depends On'], 'setup network')
        self.assertEqual(by_id['setup']['Depends On'], '')

    def test_execution_table_workload_progress(self):
        rows = transformers.execution_table(_STATUS_DOC)
        by_id = {row['Id']: row for row in rows}
        self.assertEqual(
            by_id['dataSync']['Workload Progress'], '1/2 completed')
        self.assertIsNone(by_id['setup']['Workload Progress'])

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
        self.assertNotIn("http-equiv", html_text)

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
            self.assertNotIn("http-equiv", html_text)


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

    def test_definition_visualize_writes_html(self):
        zip_bytes = _make_zip({
            "rb-x-spec.json": json.dumps(
                {"runbookSpec": _DEFINITION_DOC}),
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
                json.dump({"runbookSpec": _DEFINITION_DOC}, handle)
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
                json.dump({"runbookSpec": _REAL_DEFINITION}, handle)
            with open(params_path, 'w', encoding='utf-8') as handle:
                json.dump({"runbookInputs": _REAL_PARAMS}, handle)
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
             "prerequisite": [], "dependsOn": []},
        ]},
        {"id": "workstream-1", "displayName": "waveapp", "steps": [
            {"stepId": "vm.agentless.prepareEntity-1",
             "displayName": "Prepare Entity",
             "stepRef": "vm.agentless.prepareEntity",
             "entities": [_ENT_A, _ENT_B],
             "prerequisite": [
                 {"step": "vm.agentless.setup-1", "mode": "step"}],
             "dependsOn": []},
            {"stepId": "common.approval-1", "displayName": "Approval Gate",
             "stepRef": "common.approval", "entities": [_ENT_A, _ENT_B],
             "prerequisite": [],
             "dependsOn": [{"step": "vm.agentless.prepareEntity-1",
                            "mode": "migrationEntity"}]},
            {"stepId": "vm.agentless.migration-1", "displayName": "Migration",
             "stepRef": "vm.agentless.migration",
             "entities": [_ENT_A, _ENT_B],
             "prerequisite": [{"step": "vm.agentless.prepareEntity-1",
                               "mode": "migrationEntity"}],
             "dependsOn": [{"step": "common.approval-1",
                            "mode": "migrationEntity"}]},
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
        step = {"prerequisite": [{"step": "a"}],
                "dependsOn": [{"step": "b"}]}
        self.assertEqual(deps_mod.merged_dep_ids(step), ["a", "b"])

    def test_dedupes_preserving_order(self):
        step = {"prerequisite": [{"step": "a"}, {"step": "b"}],
                "dependsOn": [{"step": "b"}, "c"]}
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
        self.assertEqual(migration["Workloads"], 2)
        self.assertEqual(migration["Applications"], "-")
        self.assertEqual(migration["Configuration Status"], "Configured")
        self.assertIn(
            "vm.agentless.prepareEntity-1", migration["Depends On"])
        self.assertIn("common.approval-1", migration["Depends On"])


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
        self.assertIn("Workstream: Initialization (1)", html_text)
        self.assertIn("Workstream: waveapp (3)", html_text)
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
            "runbookResourceId": "/subscriptions/s/rb/testrunbook",
            "metadata": {
                "waveId": "/subscriptions/s/waves/testwave",
                "generatedAt": "2026-07-25T06:51:42.6972548Z",
            },
            "stepLibraryVersions": {"vm.agentless": "1.0"},
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
            "runbookResourceId": "/subscriptions/s/rb/tr",
            "metadata": {"generatedAt": "2026-01-01T00:00:00Z"},
            "entities": [{"id": "e1", "displayName": "VM-App01"}],
            "workstreams": [
                {"id": "w0", "displayName": "Init", "steps": [
                    {"stepId": "s1", "displayName": "Prepare",
                     "stepRef": "vm.prep"},
                    {"stepId": "s2", "displayName": "Migrate",
                     "stepRef": "vm.migrate", "entities": ["e1"],
                     "prerequisite": [{"step": "s1", "mode": "Blocking"}],
                     "dependsOn": [{"step": "s1", "mode": "Soft"}]}]},
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
        self.assertIn("Workstream: Initialization (1)", html_text)
        self.assertIn("Workstream: waveapp (3)", html_text)
        self.assertIn('class="edge"', html_text)
        self.assertIn("vm.agentless.migration", html_text)

    def test_execution_grid_shows_progress_and_groups(self):
        view = visualize_viewmodel.build_execution_view(
            _STATUS_DOC, title="Exec")
        graph = visualize_graph.build_execution_graph(
            _STATUS_DOC, title="Exec")
        html_text = visualize_renderer.render(graph, view=view)
        self.assertIn("Workstream: Web tier (4)", html_text)
        self.assertIn("1/2 completed", html_text)
        self.assertNotIn("https://", html_text)


if __name__ == '__main__':
    unittest.main()
