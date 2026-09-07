# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest import mock

from azext_migrate.runbook.cmds import runbook as runbook_cmds
from azext_migrate.runbook.cmds import execution_step as execution_step_cmds

SUB = "00000000-0000-0000-0000-000000000000"
RG = "myRg"
PROJECT = "myProject"
RUNBOOK = "myRunbook"
WAVE = "myWave"

PROJECT_ID = (
    f"/subscriptions/{SUB}/resourceGroups/{RG}/providers/"
    f"Microsoft.Migrate/migrateProjects/{PROJECT}")
RUNBOOK_ID = f"{PROJECT_ID}/runbooks/{RUNBOOK}"
EXECUTION_ID = f"{RUNBOOK_ID}/executions/exec1"


def _mock_cmd():
    cmd = mock.Mock()
    cmd.cli_ctx.cloud.endpoints.resource_manager = (
        "https://management.azure.com")
    return cmd


class RunbookCrudScenarioTest(unittest.TestCase):
    """Exercises the runbook generate/show/list/delete orchestration."""

    def setUp(self):
        self.cmd = _mock_cmd()
        sub_patch = mock.patch(
            'azext_migrate.runbook.cmds.runbook.get_subscription_id',
            return_value=SUB)
        self.addCleanup(sub_patch.stop)
        sub_patch.start()

        client_patch = mock.patch(
            'azext_migrate.runbook.cmds.runbook.ArmClient')
        self.addCleanup(client_patch.stop)
        self.client_cls = client_patch.start()
        self.client = self.client_cls.return_value

    def test_runbook_crud(self):
        generated = {
            "id": RUNBOOK_ID, "name": RUNBOOK,
            "properties": {"status": "Generating", "scope": {
                "scopeType": "Wave",
                "waveId": f"{PROJECT_ID}/waves/{WAVE}"}}}
        self.client.put.return_value = generated

        result = runbook_cmds.generate(
            self.cmd, RG, PROJECT, RUNBOOK, WAVE)

        self.assertEqual(result, generated)
        put_id, put_body = self.client.put.call_args[0]
        self.assertEqual(put_id, RUNBOOK_ID)
        self.assertEqual(
            put_body["properties"]["scope"]["waveId"],
            f"{PROJECT_ID}/waves/{WAVE}")

        self.client.get.return_value = generated
        shown = runbook_cmds.show(self.cmd, RG, PROJECT, RUNBOOK)
        self.assertEqual(shown["name"], RUNBOOK)
        self.client.get.assert_called_once_with(RUNBOOK_ID)

        self.client.list.return_value = [
            generated,
            {"name": "other", "properties": {
                "status": "NotConfigured", "scope": {
                    "waveId": f"{PROJECT_ID}/waves/otherWave"}}}]
        filtered = runbook_cmds.list_(
            self.cmd, RG, PROJECT, wave_name=WAVE)
        self.assertEqual([r["name"] for r in filtered], [RUNBOOK])
        self.client.list.assert_called_once_with(
            f"{PROJECT_ID}/runbooks")

        by_status = runbook_cmds.list_(
            self.cmd, RG, PROJECT, status="NotConfigured")
        self.assertEqual([r["name"] for r in by_status], ["other"])

        self.client.delete.return_value = None
        runbook_cmds.delete(self.cmd, RG, PROJECT, RUNBOOK)
        self.client.delete.assert_called_once_with(
            RUNBOOK_ID, no_wait=False)


class ExecutionStepScenarioTest(unittest.TestCase):
    """Exercises the retry/approve/complete step-action orchestration."""

    def setUp(self):
        self.cmd = _mock_cmd()
        sub_patch = mock.patch(
            'azext_migrate.runbook.cmds.execution.get_subscription_id',
            return_value=SUB)
        self.addCleanup(sub_patch.stop)
        sub_patch.start()

        client_patch = mock.patch(
            'azext_migrate.runbook.cmds.execution_step.ArmClient')
        self.addCleanup(client_patch.stop)
        self.client = client_patch.start().return_value

    def test_execution_step_actions(self):
        self.client.post_action.return_value = {"stepId": "step1"}

        execution_step_cmds.retry(
            self.cmd, RG, PROJECT, RUNBOOK, "exec1", "step1")
        resource_id, action, body = self.client.post_action.call_args[0]
        self.assertEqual(resource_id, EXECUTION_ID)
        self.assertEqual(action, 'PerformAction')
        self.assertEqual(body["action"], "Retry")
        self.assertEqual(body["targetId"], "step1")

        execution_step_cmds.approve(
            self.cmd, RG, PROJECT, RUNBOOK, "exec1", "step1",
            entities=["ent1"])
        _, action, body = self.client.post_action.call_args[0]
        self.assertEqual(action, 'ProvideApproval')
        self.assertEqual(body["action"], "Approve")
        self.assertEqual(body["migrationEntityIds"], ["ent1"])

        execution_step_cmds.complete(
            self.cmd, RG, PROJECT, RUNBOOK, "exec1", "step1", "done")
        _, action, body = self.client.post_action.call_args[0]
        self.assertEqual(action, 'UpdateStepStatus')
        self.assertEqual(body["action"], "Complete")
        self.assertEqual(body["comment"], "done")


if __name__ == '__main__':
    unittest.main()
