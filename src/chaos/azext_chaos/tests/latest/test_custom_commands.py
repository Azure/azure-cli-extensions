# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from collections import OrderedDict
from unittest.mock import MagicMock, patch, PropertyMock

from knack.util import CLIError

# Knack prefixes logger names with 'cli.' — this is the logger name used
# by custom.py via ``get_logger(__name__)``.
_LOGGER_NAME = 'cli.azext_chaos.custom'


# ── Helpers ──────────────────────────────────────────────────────────────

def _make_cmd():
    """Create a mock cmd object with cli_ctx."""
    cmd = MagicMock()
    cmd.cli_ctx = MagicMock()
    return cmd


def _make_response(json_body=None, status_code=200, headers=None, text="{}"):
    """Create a mock HTTP response."""
    resp = MagicMock()
    resp.json.return_value = json_body or {}
    resp.status_code = status_code
    resp.headers = headers or {}
    resp.text = text
    return resp


_EVAL_ERROR_MSG = (
    "Cannot validate the scenario configuration cfg1 for scenario s1 "
    "in workspace ws1 because the scenario is not evaluated yet. "
    "Please wait for the evaluation process to complete."
)


def _successful_validation_result():
    return {
        "name": "latest",
        "properties": {
            "status": "Succeeded",
            "startTime": "2026-01-01T00:00:00Z",
            "endTime": "2026-01-01T00:01:00Z",
            "errors": [],
            "validationErrors": {"errors": []},
        },
    }


def _failed_validation_result():
    return {
        "name": "latest",
        "properties": {
            "status": "Failed",
            "startTime": "2026-01-01T00:00:00Z",
            "endTime": "2026-01-01T00:01:00Z",
            "errors": [{"code": "PermissionError", "message": "Missing role"}],
            "validationErrors": {"errors": []},
        },
    }


# ── workspace refresh-recommendation ─────────────────────────────────────
# NOTE: ``workspace_refresh_recommendations`` (the free function) was retired
# in favor of the AAZ-subclass-with-post-hook pattern:
# ``WorkspaceRefreshRecommendation`` overrides ``post_operations`` to call
# ``_check_inner_lro``. Tests for the surface behaviors moved as follows:
#   - Success-message + --no-wait tests: covered by AAZ framework + the
#     subclass-overrides registration test in test_command_registration.py.
#   - Inner-LRO failure detection: tests now exercise ``_check_inner_lro``
#     directly (see ``TestRefreshRecommendationsInnerLRO`` further below).
#     This is the actual diagnostic surface the user cares about; instantiating
#     the full AAZCommand subclass would require a real loader infrastructure
#     for marginal added coverage.


# ── scenario config validate ─────────────────────────────────────────────

class TestScenarioConfigValidate(unittest.TestCase):

    @patch('azext_chaos.custom._poll_or_return')
    @patch('azext_chaos.custom.send_raw_request')
    def test_auto_fetch_validation_result(self, mock_send, mock_poll_or_return):
        """E3-T2: default mode fetches validations/latest."""
        from azext_chaos.custom import scenario_config_validate

        mock_poll_or_return.return_value = None
        # First call = POST validate, second call = GET validations/latest
        mock_send.side_effect = [
            _make_response(),  # POST
            _make_response(json_body=_successful_validation_result()),  # GET
        ]

        cmd = _make_cmd()
        result = scenario_config_validate(
            cmd, 'myRG', 'myWS', 'ZoneDown', 'zone1'
        )

        self.assertEqual(result["properties"]["status"], "Succeeded")
        self.assertEqual(mock_send.call_count, 2)

    @patch('azext_chaos.custom.send_raw_request')
    def test_no_wait_skips_auto_fetch(self, mock_send):
        """E3-T2: --no-wait returns without fetching validation result."""
        from azext_chaos.custom import scenario_config_validate

        mock_send.return_value = _make_response()
        cmd = _make_cmd()

        with self.assertLogs(_LOGGER_NAME, level='WARNING') as cm:
            scenario_config_validate(
                cmd, 'myRG', 'myWS', 'ZoneDown', 'zone1', no_wait=True
            )

        self.assertEqual(mock_send.call_count, 1)
        log_output = '\n'.join(cm.output)
        self.assertIn('show-validation', log_output)

    @patch('azext_chaos.custom._poll_or_return')
    @patch('azext_chaos.custom.send_raw_request')
    def test_evaluation_error_rewriting(self, mock_send, mock_poll_or_return):
        """E3-T2: evaluation-state error is rewritten with actionable hint."""
        from azext_chaos.custom import scenario_config_validate

        mock_poll_or_return.return_value = None
        validation_result = {
            "name": "latest",
            "properties": {
                "status": "Failed",
                "errors": [{
                    "code": "ResourceStateNotReady",
                    "message": _EVAL_ERROR_MSG,
                }],
                "validationErrors": {"errors": []},
            },
        }
        mock_send.side_effect = [
            _make_response(),  # POST
            _make_response(json_body=validation_result),  # GET
        ]

        cmd = _make_cmd()
        with self.assertRaises(CLIError) as ctx:
            scenario_config_validate(cmd, 'myRG', 'myWS', 'ZoneDown', 'zone1')

        error_msg = str(ctx.exception)
        self.assertIn('refresh-recommendation', error_msg)
        self.assertIn('evaluate-scenarios', error_msg)
        self.assertIn('show-evaluation', error_msg)

    @patch('azext_chaos.custom._poll_or_return')
    @patch('azext_chaos.custom.send_raw_request')
    def test_evaluation_error_in_validation_errors(self, mock_send, mock_poll_or_return):
        """E3-T2: evaluation error in validationErrors is also detected."""
        from azext_chaos.custom import scenario_config_validate

        mock_poll_or_return.return_value = None
        validation_result = {
            "name": "latest",
            "properties": {
                "status": "Failed",
                "errors": [],
                "validationErrors": {
                    "errors": [{
                        "code": "ResourceStateNotReady",
                        "message": _EVAL_ERROR_MSG,
                    }],
                },
            },
        }
        mock_send.side_effect = [
            _make_response(),  # POST
            _make_response(json_body=validation_result),  # GET
        ]

        cmd = _make_cmd()
        with self.assertRaises(CLIError) as ctx:
            scenario_config_validate(cmd, 'myRG', 'myWS', 'ZoneDown', 'zone1')

        self.assertIn('refresh-recommendation', str(ctx.exception))

    @patch('azext_chaos.custom._poll_or_return')
    @patch('azext_chaos.custom.send_raw_request')
    def test_non_succeeded_status_triggers_eval_check(self, mock_send, mock_poll_or_return):
        """E3-T2: non-standard status (e.g., Canceled) is also treated as failure."""
        from azext_chaos.custom import scenario_config_validate

        mock_poll_or_return.return_value = None
        validation_result = {
            "name": "latest",
            "properties": {
                "status": "Canceled",
                "errors": [],
                "validationErrors": {"errors": []},
            },
        }
        mock_send.side_effect = [
            _make_response(),  # POST
            _make_response(json_body=validation_result),  # GET
        ]

        cmd = _make_cmd()
        # Should return the result (no eval error, but status != Succeeded
        # triggers eval check; no eval error found so result is returned)
        result = scenario_config_validate(cmd, 'myRG', 'myWS', 'ZoneDown', 'zone1')
        self.assertEqual(result["properties"]["status"], "Canceled")


# ── scenario run start ───────────────────────────────────────────────────

class TestScenarioRunStart(unittest.TestCase):

    @patch('azext_chaos.custom._poll_or_return')
    @patch('azext_chaos.custom.send_raw_request')
    def test_default_validates_then_executes(self, mock_send, mock_poll_or_return):
        """E3-T3: default mode calls validate, then execute."""
        from azext_chaos.custom import scenario_run_start

        run_result = {
            "name": "run-id-123",
            "properties": {"status": "Running"},
        }
        mock_send.side_effect = [
            _make_response(),  # POST validate
            _make_response(json_body=_successful_validation_result()),  # GET val
            _make_response(headers={"Location": "/runs/run-id-123"}),  # POST exec
        ]
        # _poll_or_return called twice: once for validate, once for execute
        mock_poll_or_return.side_effect = [None, run_result]

        cmd = _make_cmd()
        with self.assertLogs(_LOGGER_NAME, level='WARNING') as cm:
            scenario_run_start(
                cmd, 'myRG', 'myWS', 'ZoneDown', 'zone1'
            )

        # 3 calls: POST validate, GET validations/latest, POST execute
        self.assertEqual(mock_send.call_count, 3)
        log_output = '\n'.join(cm.output)
        self.assertIn('run-id-123', log_output)
        self.assertIn('scenario run show', log_output)

    @patch('azext_chaos.custom._poll_or_return')
    @patch('azext_chaos.custom.send_raw_request')
    def test_skip_validation_skips_validate(self, mock_send, mock_poll_or_return):
        """E3-T3: --skip-validation goes directly to execute."""
        from azext_chaos.custom import scenario_run_start

        run_result = {
            "name": "run-id-456",
            "properties": {"status": "Running"},
        }
        mock_send.side_effect = [
            _make_response(headers={"Location": "/runs/run-id-456"}),  # POST exec
        ]
        mock_poll_or_return.return_value = run_result

        cmd = _make_cmd()
        with self.assertLogs(_LOGGER_NAME, level='WARNING'):
            scenario_run_start(
                cmd, 'myRG', 'myWS', 'ZoneDown', 'zone1',
                skip_validation=True
            )

        # Only 1 call: POST execute
        self.assertEqual(mock_send.call_count, 1)

    @patch('azext_chaos.custom._poll_or_return')
    @patch('azext_chaos.custom.send_raw_request')
    def test_validation_failure_aborts(self, mock_send, mock_poll_or_return):
        """E3-T3: validation failure exits non-zero, no execute."""
        from azext_chaos.custom import scenario_run_start

        mock_poll_or_return.return_value = None
        mock_send.side_effect = [
            _make_response(),  # POST validate
            _make_response(json_body=_failed_validation_result()),  # GET val
        ]

        cmd = _make_cmd()
        with self.assertRaises(CLIError) as ctx:
            scenario_run_start(cmd, 'myRG', 'myWS', 'ZoneDown', 'zone1')

        self.assertIn('Validation failed', str(ctx.exception))
        # Only 2 calls: POST validate, GET validations/latest — no execute
        self.assertEqual(mock_send.call_count, 2)

    @patch('azext_chaos.custom._poll_or_return')
    @patch('azext_chaos.custom.send_raw_request')
    def test_no_wait_returns_run_id_from_location(self, mock_send, mock_poll_or_return):
        """E3-T3: --no-wait parses run ID from Location header."""
        from azext_chaos.custom import scenario_run_start

        location_url = (
            "/subscriptions/sub1/resourceGroups/myRG/"
            "providers/Microsoft.Chaos/workspaces/myWS/"
            "scenarios/ZoneDown/scenarioRuns/run-abc-123"
            "?api-version=2026-05-01-preview"
        )
        mock_poll_or_return.return_value = None
        mock_send.side_effect = [
            _make_response(),  # POST validate
            _make_response(json_body=_successful_validation_result()),  # GET val
            _make_response(headers={"Location": location_url}),  # POST exec
        ]

        cmd = _make_cmd()
        with self.assertLogs(_LOGGER_NAME, level='WARNING') as cm:
            result = scenario_run_start(
                cmd, 'myRG', 'myWS', 'ZoneDown', 'zone1',
                no_wait=True
            )

        self.assertEqual(result["runId"], "run-abc-123")
        log_output = '\n'.join(cm.output)
        self.assertIn('run-abc-123', log_output)

    @patch('azext_chaos.custom.send_raw_request')
    def test_skip_validation_no_wait(self, mock_send):
        """E3-T3: --skip-validation --no-wait is fire-and-forget."""
        from azext_chaos.custom import scenario_run_start

        location_url = (
            "/subscriptions/sub1/resourceGroups/myRG/"
            "providers/Microsoft.Chaos/workspaces/myWS/"
            "scenarios/ZoneDown/scenarioRuns/run-fast-789"
        )
        mock_send.side_effect = [
            _make_response(headers={"Location": location_url}),  # POST exec
        ]

        cmd = _make_cmd()
        with self.assertLogs(_LOGGER_NAME, level='WARNING'):
            result = scenario_run_start(
                cmd, 'myRG', 'myWS', 'ZoneDown', 'zone1',
                skip_validation=True, no_wait=True
            )

        # Only 1 call: POST execute
        self.assertEqual(mock_send.call_count, 1)
        self.assertEqual(result["runId"], "run-fast-789")

    @patch('azext_chaos.custom._poll_or_return')
    @patch('azext_chaos.custom.send_raw_request')
    def test_evaluation_error_in_preflight(self, mock_send, mock_poll_or_return):
        """E3-T3: evaluation-state error during pre-flight."""
        from azext_chaos.custom import scenario_run_start

        mock_poll_or_return.return_value = None
        validation_result = {
            "name": "latest",
            "properties": {
                "status": "Failed",
                "errors": [{
                    "code": "ResourceStateNotReady",
                    "message": _EVAL_ERROR_MSG,
                }],
                "validationErrors": {"errors": []},
            },
        }
        mock_send.side_effect = [
            _make_response(),  # POST validate
            _make_response(json_body=validation_result),  # GET val
        ]

        cmd = _make_cmd()
        with self.assertRaises(CLIError) as ctx:
            scenario_run_start(cmd, 'myRG', 'myWS', 'ZoneDown', 'zone1')

        error_msg = str(ctx.exception)
        self.assertIn('refresh-recommendation', error_msg)
        self.assertIn('evaluate-scenarios', error_msg)
        # Should not proceed to execute
        self.assertEqual(mock_send.call_count, 2)

    @patch('azext_chaos.custom._poll_or_return')
    @patch('azext_chaos.custom.send_raw_request')
    def test_run_id_surfacing_full_poll(self, mock_send, mock_poll_or_return):
        """E3-T3: run ID is read from ScenarioRun body after full LRO poll."""
        from azext_chaos.custom import scenario_run_start

        run_result = {
            "name": "polled-run-id",
            "id": "/subscriptions/sub1/providers/.../scenarioRuns/polled-run-id",
            "properties": {"status": "Running"},
        }
        mock_send.side_effect = [
            _make_response(),  # POST validate
            _make_response(json_body=_successful_validation_result()),  # GET val
            _make_response(headers={"Location": "/runs/polled-run-id"}),  # POST exec
        ]
        mock_poll_or_return.side_effect = [None, run_result]

        cmd = _make_cmd()
        with self.assertLogs(_LOGGER_NAME, level='WARNING') as cm:
            result = scenario_run_start(
                cmd, 'myRG', 'myWS', 'ZoneDown', 'zone1'
            )

        self.assertEqual(result["name"], "polled-run-id")
        log_output = '\n'.join(cm.output)
        self.assertIn('polled-run-id', log_output)
        self.assertIn('scenario run show', log_output)


# ── scenario run cancel ──────────────────────────────────────────────────

class TestScenarioRunCancel(unittest.TestCase):

    @patch('azext_chaos.custom._poll_or_return')
    @patch('azext_chaos.custom.send_raw_request')
    def test_cancel_success_message(self, mock_send, mock_poll_or_return):
        """E3-T4: verify cancellation confirmation message."""
        from azext_chaos.custom import scenario_run_cancel

        mock_send.return_value = _make_response()
        mock_poll_or_return.return_value = None

        cmd = _make_cmd()
        with self.assertLogs(_LOGGER_NAME, level='WARNING') as cm:
            result = scenario_run_cancel(
                cmd, 'myRG', 'myWS', 'ZoneDown',
                '12345678-1234-1234-1234-123456789012'
            )

        self.assertIsNone(result)
        log_output = '\n'.join(cm.output)
        self.assertIn('12345678-1234-1234-1234-123456789012', log_output)
        self.assertIn('cancelled', log_output.lower())

    @patch('azext_chaos.custom.send_raw_request')
    def test_cancel_no_wait(self, mock_send):
        """E3-T4: --no-wait returns immediately."""
        from azext_chaos.custom import scenario_run_cancel

        mock_send.return_value = _make_response(
            json_body={"status": "cancelling"}, text='{"status": "cancelling"}'
        )

        cmd = _make_cmd()
        result = scenario_run_cancel(
            cmd, 'myRG', 'myWS', 'ZoneDown',
            '12345678-1234-1234-1234-123456789012',
            no_wait=True
        )
        self.assertEqual(result, {"status": "cancelling"})


# ── Internal helpers ─────────────────────────────────────────────────────

class TestInternalHelpers(unittest.TestCase):

    def test_is_evaluation_error_true(self):
        from azext_chaos.custom import _is_evaluation_error
        self.assertTrue(_is_evaluation_error(_EVAL_ERROR_MSG))

    def test_is_evaluation_error_false(self):
        from azext_chaos.custom import _is_evaluation_error
        self.assertFalse(_is_evaluation_error("Permission denied"))

    def test_is_evaluation_error_none(self):
        from azext_chaos.custom import _is_evaluation_error
        self.assertFalse(_is_evaluation_error(None))

    def test_extract_run_id_from_location(self):
        from azext_chaos.custom import _extract_run_id_from_location
        url = (
            "/subscriptions/sub1/resourceGroups/myRG/"
            "providers/Microsoft.Chaos/workspaces/myWS/"
            "scenarios/ZoneDown/scenarioRuns/my-run-id"
            "?api-version=2026-05-01-preview"
        )
        self.assertEqual(_extract_run_id_from_location(url), "my-run-id")

    def test_extract_run_id_empty(self):
        from azext_chaos.custom import _extract_run_id_from_location
        self.assertIsNone(_extract_run_id_from_location(""))
        self.assertIsNone(_extract_run_id_from_location(None))

    def test_make_evaluation_hint_content(self):
        from azext_chaos.custom import _make_evaluation_hint
        hint = _make_evaluation_hint("myWS", "myRG")
        self.assertIn("refresh-recommendation", hint)
        self.assertIn("evaluate-scenarios", hint)
        self.assertIn("show-evaluation", hint)
        self.assertIn("myWS", hint)
        self.assertIn("myRG", hint)


class TestTableFormat(unittest.TestCase):

    def test_validation_show_table_format_no_mutation(self):
        """validation_show_table_format must not inject keys into the input dict."""
        from azext_chaos._table_format import validation_show_table_format
        result = {
            "name": "latest",
            "properties": {
                "status": "Succeeded",
                "startTime": "2026-01-01T00:00:00Z",
                "endTime": "2026-01-01T00:01:00Z",
                "errors": [],
                "validationErrors": {"errors": []},
            },
        }
        original_keys = set(result.keys())
        validation_show_table_format(result)
        self.assertEqual(set(result.keys()), original_keys)


# ── Help entries ─────────────────────────────────────────────────────────

class TestHelpEntries(unittest.TestCase):

    def test_refresh_recommendation_help_exists(self):
        from azext_chaos._help import helps
        self.assertIn('chaos workspace refresh-recommendation', helps)

    def test_validate_help_exists(self):
        from azext_chaos._help import helps
        self.assertIn('chaos scenario config validate', helps)

    def test_run_start_help_exists(self):
        from azext_chaos._help import helps
        self.assertIn('chaos scenario run start', helps)
        help_text = helps['chaos scenario run start']
        self.assertIn('--skip-validation', help_text)
        self.assertIn('--no-wait', help_text)

    def test_run_start_help_shows_all_four_pairings(self):
        from azext_chaos._help import helps
        help_text = helps['chaos scenario run start']
        # Verify all 4 example pairings exist
        self.assertIn('--skip-validation --no-wait', help_text)
        # Check that individual flags appear in examples
        examples_with_skip = help_text.count('--skip-validation')
        examples_with_no_wait = help_text.count('--no-wait')
        self.assertGreaterEqual(examples_with_skip, 3)  # 2 examples + long desc
        self.assertGreaterEqual(examples_with_no_wait, 3)

    def test_run_cancel_help_exists(self):
        from azext_chaos._help import helps
        self.assertIn('chaos scenario run cancel', helps)

    def test_evaluate_scenarios_alias_help(self):
        from azext_chaos._help import helps
        self.assertIn('chaos workspace evaluate-scenarios', helps)
        self.assertIn(
            'Alias of `az chaos workspace refresh-recommendation`',
            helps['chaos workspace evaluate-scenarios']
        )


# ── _poll_or_return unit tests ───────────────────────────────────────────

class TestPollOrReturn(unittest.TestCase):

    def test_200_returns_json_body(self):
        """E2-T11: status 200 returns JSON body directly (no polling)."""
        from azext_chaos.custom import _poll_or_return
        cmd = _make_cmd()
        resp = _make_response(json_body={"key": "value"}, status_code=200,
                              text='{"key": "value"}')
        result = _poll_or_return(cmd, resp)
        self.assertEqual(result, {"key": "value"})

    def test_200_empty_text_returns_none(self):
        """E2-T12: status 200 with empty text returns None."""
        from azext_chaos.custom import _poll_or_return
        cmd = _make_cmd()
        resp = _make_response(status_code=200, text="")
        result = _poll_or_return(cmd, resp)
        self.assertIsNone(result)

    @patch('azext_chaos.custom.time.sleep')
    @patch('azext_chaos.custom.send_raw_request')
    def test_202_async_operation_polls_until_succeeded(self, mock_send, mock_sleep):
        """E2-T13: status 202 + Azure-AsyncOperation polls until Succeeded."""
        from azext_chaos.custom import _poll_or_return
        cmd = _make_cmd()
        initial = _make_response(
            status_code=202,
            headers={"Azure-AsyncOperation": "https://mgmt.azure.com/poll"},
            text=""
        )
        # First poll: InProgress, second poll: Succeeded
        mock_send.side_effect = [
            _make_response(json_body={"status": "InProgress"}, text='{"status": "InProgress"}'),
            _make_response(json_body={"status": "Succeeded"}, text='{"status": "Succeeded"}'),
        ]
        result = _poll_or_return(cmd, initial)
        self.assertEqual(result, {"status": "Succeeded"})
        self.assertEqual(mock_send.call_count, 2)

    @patch('azext_chaos.custom.time.sleep')
    @patch('azext_chaos.custom.send_raw_request')
    def test_202_location_polls_until_200(self, mock_send, mock_sleep):
        """E2-T14: status 202 + Location polls until 200."""
        from azext_chaos.custom import _poll_or_return
        cmd = _make_cmd()
        initial = _make_response(
            status_code=202,
            headers={"Location": "https://mgmt.azure.com/location"},
            text=""
        )
        # First poll: 202, second poll: 200
        mock_send.side_effect = [
            _make_response(status_code=202, headers={}, text=""),
            _make_response(status_code=200, json_body={"done": True}, text='{"done": true}'),
        ]
        result = _poll_or_return(cmd, initial)
        self.assertEqual(result, {"done": True})
        self.assertEqual(mock_send.call_count, 2)

    @patch('azext_chaos.custom.time.sleep')
    @patch('azext_chaos.custom.send_raw_request')
    def test_202_async_operation_failed_raises(self, mock_send, mock_sleep):
        """E2-T15: status 202 + Azure-AsyncOperation, terminal Failed raises CLIError."""
        from azext_chaos.custom import _poll_or_return
        cmd = _make_cmd()
        initial = _make_response(
            status_code=202,
            headers={"Azure-AsyncOperation": "https://mgmt.azure.com/poll"},
            text=""
        )
        mock_send.return_value = _make_response(
            json_body={"status": "Failed", "error": {"message": "something broke"}},
            text='{"status": "Failed"}'
        )
        with self.assertRaises(CLIError) as ctx:
            _poll_or_return(cmd, initial)
        self.assertIn("something broke", str(ctx.exception))

    @patch('azext_chaos.custom.time.sleep')
    @patch('azext_chaos.custom.send_raw_request')
    def test_202_both_headers_async_then_location(self, mock_send, mock_sleep):
        """E2-T16: both headers — uses Azure-AsyncOperation, then final GET to Location."""
        from azext_chaos.custom import _poll_or_return
        cmd = _make_cmd()
        initial = _make_response(
            status_code=202,
            headers={
                "Azure-AsyncOperation": "https://mgmt.azure.com/poll",
                "Location": "https://mgmt.azure.com/resource",
            },
            text=""
        )
        # Async poll succeeds, then final GET to Location
        mock_send.side_effect = [
            _make_response(json_body={"status": "Succeeded"}, text='{"status": "Succeeded"}'),
            _make_response(json_body={"id": "resource-1"}, text='{"id": "resource-1"}'),
        ]
        result = _poll_or_return(cmd, initial)
        self.assertEqual(result, {"id": "resource-1"})
        # Verify second call was to Location URL
        self.assertEqual(mock_send.call_count, 2)
        second_call_url = mock_send.call_args_list[1][0][2]
        self.assertEqual(second_call_url, "https://mgmt.azure.com/resource")

    def test_202_no_polling_headers_returns_body(self):
        """E2-T17: status 202 + no polling headers returns body (sync fallback)."""
        from azext_chaos.custom import _poll_or_return
        cmd = _make_cmd()
        resp = _make_response(
            status_code=202, json_body={"accepted": True},
            headers={}, text='{"accepted": true}'
        )
        result = _poll_or_return(cmd, resp)
        self.assertEqual(result, {"accepted": True})

    def test_500_raises_cli_error(self):
        """E2-T18: status 500 raises CLIError with error body."""
        from azext_chaos.custom import _poll_or_return
        cmd = _make_cmd()
        resp = _make_response(
            status_code=500,
            json_body={"error": {"message": "Internal server error"}},
            text='{"error": {"message": "Internal server error"}}'
        )
        with self.assertRaises(CLIError) as ctx:
            _poll_or_return(cmd, resp)
        self.assertIn("Internal server error", str(ctx.exception))
        self.assertIn("500", str(ctx.exception))

    @patch('azext_chaos.custom.time.sleep')
    @patch('azext_chaos.custom.send_raw_request')
    @patch('azext_chaos.custom._LRO_TIMEOUT_SECONDS', 10)
    @patch('azext_chaos.custom._LRO_POLL_INTERVAL_SECONDS', 11)
    def test_async_operation_timeout_raises(self, mock_send, mock_sleep):
        """Timeout after _LRO_TIMEOUT_SECONDS raises CLIError."""
        from azext_chaos.custom import _poll_or_return
        cmd = _make_cmd()
        initial = _make_response(
            status_code=202,
            headers={"Azure-AsyncOperation": "https://mgmt.azure.com/poll"},
            text=""
        )
        # Always return InProgress
        mock_send.return_value = _make_response(
            json_body={"status": "InProgress"}, text='{"status": "InProgress"}'
        )
        with self.assertRaises(CLIError) as ctx:
            _poll_or_return(cmd, initial)
        self.assertIn("timed out", str(ctx.exception))

    @patch('azext_chaos.custom.time.sleep')
    @patch('azext_chaos.custom.send_raw_request')
    def test_location_poll_bad_retry_after_ignored(self, mock_send, mock_sleep):
        """Non-integer Retry-After header (e.g. HTTP-date) is silently ignored."""
        from azext_chaos.custom import _poll_or_return
        cmd = _make_cmd()
        initial = _make_response(
            status_code=202,
            headers={"Location": "https://mgmt.azure.com/location"},
            text=""
        )
        # First poll: 202 with HTTP-date Retry-After, second poll: 200
        mock_send.side_effect = [
            _make_response(
                status_code=202,
                headers={"Retry-After": "Tue, 19 May 2026 00:00:00 GMT"},
                text=""
            ),
            _make_response(
                status_code=200,
                json_body={"done": True},
                text='{"done": true}'
            ),
        ]
        result = _poll_or_return(cmd, initial)
        self.assertEqual(result, {"done": True})


# ── Integration-level regression tests ───────────────────────────────────

class TestLROIntegrationRegression(unittest.TestCase):

    # ``test_workspace_refresh_200_no_attribute_error`` was removed when the
    # ``workspace_refresh_recommendations`` free function was retired. The AAZ
    # framework now owns the LRO polling (including the 200-without-poll
    # short-circuit), so the regression cannot reoccur via our code paths.

    @patch('azext_chaos.custom.time.sleep')
    @patch('azext_chaos.custom.send_raw_request')
    def test_scenario_run_start_202_location_polls(self, mock_send, mock_sleep):
        """E2-T20: scenario_run_start with 202 + Location header polls correctly."""
        from azext_chaos.custom import scenario_run_start

        run_result = {"name": "run-202", "properties": {"status": "Running"}}
        mock_send.side_effect = [
            # POST validate → 200 (sync)
            _make_response(status_code=200, text=""),
            # GET validations/latest
            _make_response(json_body=_successful_validation_result()),
            # POST execute → 202 + Location
            _make_response(
                status_code=202,
                headers={"Location": "https://mgmt.azure.com/runs/run-202"},
                text=""
            ),
            # Poll Location → 200 with result
            _make_response(
                status_code=200, json_body=run_result,
                text='{"name": "run-202"}'
            ),
        ]

        cmd = _make_cmd()
        with self.assertLogs(_LOGGER_NAME, level='WARNING') as cm:
            result = scenario_run_start(
                cmd, 'myRG', 'myWS', 'ZoneDown', 'zone1'
            )

        self.assertEqual(result["name"], "run-202")
        log_output = '\n'.join(cm.output)
        self.assertIn('run-202', log_output)

# ── URL segment assertions (EPIC-001) ────────────────────────────────────


class TestUrlSegments(unittest.TestCase):
    """Assert every custom command builds ARM URLs with the correct path segments.

    The GW routes use /configurations/{configurationName}/ and /runs/{runName}/,
    NOT /scenarioConfigurations/ or /scenarioRuns/.
    """

    @patch('azext_chaos.custom._poll_or_return')
    @patch('azext_chaos.custom.send_raw_request')
    def test_scenario_config_validate_url(self, mock_send, mock_poll_or_return):
        """E1-T7: scenario_config_validate uses /configurations/, not /scenarioConfigurations/."""
        from azext_chaos.custom import scenario_config_validate

        mock_poll_or_return.return_value = None
        mock_send.side_effect = [
            _make_response(),
            _make_response(json_body=_successful_validation_result()),
        ]

        scenario_config_validate(_make_cmd(), 'rg', 'ws', 'sc', 'cfg')

        urls = [call.args[2] for call in mock_send.call_args_list]
        for url in urls:
            self.assertIn('/configurations/', url)
            self.assertNotIn('/scenarioConfigurations/', url)

    @patch('azext_chaos.custom.send_raw_request')
    def test_scenario_config_show_validation_url(self, mock_send):
        """E1-T7: scenario_config_show_validation uses /configurations/."""
        from azext_chaos.custom import scenario_config_show_validation

        mock_send.return_value = _make_response()
        scenario_config_show_validation(_make_cmd(), 'rg', 'ws', 'sc', 'cfg')

        url = mock_send.call_args.args[2]
        self.assertIn('/configurations/', url)
        self.assertNotIn('/scenarioConfigurations/', url)

    @patch('azext_chaos.custom.send_raw_request')
    def test_scenario_config_show_permission_fix_url(self, mock_send):
        """E1-T7: scenario_config_show_permission_fix uses /configurations/."""
        from azext_chaos.custom import scenario_config_show_permission_fix

        mock_send.return_value = _make_response()
        scenario_config_show_permission_fix(_make_cmd(), 'rg', 'ws', 'sc', 'cfg')

        url = mock_send.call_args.args[2]
        self.assertIn('/configurations/', url)
        self.assertNotIn('/scenarioConfigurations/', url)

    @patch('azext_chaos.custom._poll_or_return')
    @patch('azext_chaos.custom.send_raw_request')
    def test_scenario_run_start_url(self, mock_send, mock_poll_or_return):
        """E1-T7: scenario_run_start uses /configurations/, not /scenarioConfigurations/."""
        from azext_chaos.custom import scenario_run_start

        mock_poll_or_return.side_effect = [None, {"name": "r1", "properties": {}}]
        mock_send.side_effect = [
            _make_response(),
            _make_response(json_body=_successful_validation_result()),
            _make_response(headers={"Location": "/runs/r1"}),
        ]

        with self.assertLogs(_LOGGER_NAME, level='WARNING'):
            scenario_run_start(_make_cmd(), 'rg', 'ws', 'sc', 'cfg')

        urls = [call.args[2] for call in mock_send.call_args_list]
        for url in urls:
            self.assertIn('/configurations/', url)
            self.assertNotIn('/scenarioConfigurations/', url)

    @patch('azext_chaos.custom._poll_or_return')
    @patch('azext_chaos.custom.send_raw_request')
    def test_scenario_run_cancel_url(self, mock_send, mock_poll_or_return):
        """E1-T7: scenario_run_cancel uses /runs/, not /scenarioRuns/."""
        from azext_chaos.custom import scenario_run_cancel

        mock_send.return_value = _make_response()
        mock_poll_or_return.return_value = None

        with self.assertLogs(_LOGGER_NAME, level='WARNING'):
            scenario_run_cancel(_make_cmd(), 'rg', 'ws', 'sc', 'run1')

        url = mock_send.call_args.args[2]
        self.assertIn('/runs/', url)
        self.assertNotIn('/scenarioRuns/', url)


# ── EPIC-003: fix-permissions investigation tests ────────────────────────

class TestFixPermissionsPreOperations(unittest.TestCase):
    """E3-T5: Tests for fix-permissions pre_operations hint and help text."""

    def test_fix_permissions_pre_operations_logs_hint(self):
        """E3-T5: the runtime command logs an info-level troubleshooting hint.

        The hint moved out of the (now pristine) AAZ ``pre_operations`` and
        lives in the custom command ``scenario_config_fix_permissions`` that
        supersedes the aaz registration.  See README §"Modifying the
        AAZ-generated code" and ``CODEGEN_SOURCE.md`` item 7.
        """
        import inspect
        from azext_chaos.custom import scenario_config_fix_permissions

        source = inspect.getsource(scenario_config_fix_permissions)
        self.assertIn('logger.info', source,
                      "scenario_config_fix_permissions should log a hint about prerequisites")
        self.assertIn('404', source,
                      "Hint should explain the 404 NotFound failure mode")

    def test_fix_permissions_aaz_pre_operations_is_pristine(self):
        """The AAZ-generated FixPermissions.pre_operations must be a no-op.

        Behavioral hints belong in the custom command, not the aaz module.
        """
        import inspect
        from azext_chaos.aaz.latest.chaos.scenario.config._fix_permissions import FixPermissions

        class_source = inspect.getsource(FixPermissions)
        self.assertNotIn('logger', class_source,
                         "FixPermissions class must not reference logger (aaz pristine)")
        self.assertNotIn('get_logger', class_source,
                         "FixPermissions module must not import get_logger (aaz pristine)")

    def test_fix_permissions_help_mentions_no_prior_validation(self):
        """E3-T5: help text documents that no prior validation is required."""
        from knack.help_files import helps
        # Force module load to register help entries
        import azext_chaos._help  # noqa: F401

        help_text = helps.get('chaos scenario config fix-permissions', '')
        self.assertIn('NOT required', help_text,
                      "Help text should state that prior validate is NOT required")

    def test_fix_permissions_help_mentions_404_cause(self):
        """E3-T5: help text documents 404 means missing resource."""
        from knack.help_files import helps
        import azext_chaos._help  # noqa: F401

        help_text = helps.get('chaos scenario config fix-permissions', '')
        self.assertIn('404', help_text,
                      "Help text should mention 404 NotFound cause")

    def test_fix_permissions_body_shape_is_top_level(self):
        """E3-T3: body serializes whatIf at top level, not under properties."""
        from azext_chaos.aaz.latest.chaos.scenario.config._fix_permissions import FixPermissions
        import inspect
        source = inspect.getsource(
            FixPermissions.ScenarioConfigurationsFixResourcePermissions.content.fget
        )
        # Body uses client_flatten=True and sets "whatIf" directly
        self.assertIn('client_flatten', source)
        self.assertIn('"whatIf"', source)
        # Should NOT wrap in "properties"
        self.assertNotIn('"properties"', source)


# ── Regression tests for the test-report follow-ups ──────────────────────


class TestScenarioConfigFixPermissions(unittest.TestCase):
    """H1 follow-up: custom fix-permissions handler that bypasses the
    AAZ-generated LRO poller's mishandling of the SAS-signed Location URL."""

    @patch('azext_chaos.custom._poll_or_return')
    @patch('azext_chaos.custom.send_raw_request')
    def test_default_polls_then_fetches_latest(self, mock_send, mock_poll):
        from azext_chaos.custom import scenario_config_fix_permissions

        mock_poll.return_value = None
        latest_body = {
            "name": "latest",
            "properties": {
                "state": "Succeeded",
                "summary": "Assigned 1 role",
                "whatIfMode": False,
                "roleAssignments": [{"roleDefinitionId": "abc"}],
            },
        }
        mock_send.side_effect = [
            _make_response(status_code=202),  # POST fixResourcePermissions
            _make_response(json_body=latest_body),  # GET .../fixResourcePermissions/latest
        ]

        cmd = _make_cmd()
        result = scenario_config_fix_permissions(
            cmd, 'myRG', 'myWS', 'ZoneDown-1.0', 'cfg-1'
        )

        self.assertEqual(result, latest_body)
        # POST + GET = 2 send calls; poll invoked once on the 202.
        self.assertEqual(mock_send.call_count, 2)
        mock_poll.assert_called_once()
        # POST URL hits the right path; body is {"whatIf": false} by default.
        post_call = mock_send.call_args_list[0]
        post_url = post_call.args[2]
        self.assertIn('/fixResourcePermissions?', post_url)
        post_body = post_call.kwargs.get('body')
        self.assertEqual(post_body, '{"whatIf": false}')
        # GET URL is the /latest singleton.
        get_url = mock_send.call_args_list[1].args[2]
        self.assertIn('/fixResourcePermissions/latest?', get_url)

    @patch('azext_chaos.custom._poll_or_return')
    @patch('azext_chaos.custom.send_raw_request')
    def test_what_if_propagates_to_body(self, mock_send, mock_poll):
        from azext_chaos.custom import scenario_config_fix_permissions

        mock_poll.return_value = None
        mock_send.side_effect = [
            _make_response(status_code=202),
            _make_response(json_body={"properties": {"state": "Succeeded"}}),
        ]

        scenario_config_fix_permissions(
            _make_cmd(), 'myRG', 'myWS', 'ZoneDown-1.0', 'cfg-1',
            what_if=True,
        )

        post_body = mock_send.call_args_list[0].kwargs.get('body')
        self.assertEqual(post_body, '{"whatIf": true}')

    @patch('azext_chaos.custom.send_raw_request')
    def test_no_wait_skips_poll_and_latest_get(self, mock_send):
        from azext_chaos.custom import scenario_config_fix_permissions

        mock_send.return_value = _make_response(
            status_code=202, json_body={"status": "InProgress"}
        )

        cmd = _make_cmd()
        with self.assertLogs(_LOGGER_NAME, level='WARNING') as cm:
            result = scenario_config_fix_permissions(
                cmd, 'myRG', 'myWS', 'ZoneDown-1.0', 'cfg-1',
                no_wait=True,
            )

        # Only the POST was issued.
        self.assertEqual(mock_send.call_count, 1)
        self.assertEqual(result, {"status": "InProgress"})
        self.assertIn('show-permission-fix', '\n'.join(cm.output))

    def test_registered_as_custom_command(self):
        """Verify commands.py overrides the AAZ fix-permissions registration."""
        from azext_chaos.commands import load_command_table
        mock_loader = MagicMock()
        mock_loader.command_table = {}
        with patch('azext_chaos.commands._register_aaz_subclass_overrides'):
            load_command_table(mock_loader, None)
        ctx = mock_loader.command_group.return_value.__enter__.return_value
        custom_cmds = [(c.args[0], c.args[1])
                       for c in ctx.custom_command.call_args_list]
        self.assertIn(
            ('fix-permissions', 'scenario_config_fix_permissions'),
            custom_cmds,
            'fix-permissions must be registered as a custom command to bypass '
            'the AAZ-generated LRO poller (test-report finding H1).',
        )


class TestRefreshRecommendationsInnerLRO(unittest.TestCase):
    """M1 follow-up: surface inner discovery/evaluation failures even when the
    outer refreshRecommendations LRO reports Succeeded."""

    @patch('azext_chaos.custom.send_raw_request')
    def test_inner_discovery_failed_raises(self, mock_send):
        from azext_chaos.custom import _check_inner_lro

        mock_send.return_value = _make_response(json_body={
            "properties": {
                "status": "Failed",
                "errors": [{
                    "errorCode": "ResourceDiscoveryPermissionError",
                    "errorMessage": "Status: 403 (Forbidden)",
                }],
            },
        })

        with self.assertRaises(CLIError) as ctx:
            _check_inner_lro(_make_cmd().cli_ctx, 'myRG', 'myWS',
                             "/discoveries/latest", "resource discovery")

        err = str(ctx.exception)
        self.assertIn('resource discovery', err)
        self.assertIn('ResourceDiscoveryPermissionError', err)
        # Friendly hint must point at ARG propagation
        self.assertIn('Azure Resource Graph', err)

    @patch('azext_chaos.custom.send_raw_request')
    def test_inner_evaluation_failed_raises(self, mock_send):
        from azext_chaos.custom import _check_inner_lro

        mock_send.return_value = _make_response(json_body={
            "properties": {
                "status": "Failed",
                "errors": [{"errorCode": "X", "errorMessage": "boom"}],
            }
        })

        with self.assertRaises(CLIError) as ctx:
            _check_inner_lro(_make_cmd().cli_ctx, 'myRG', 'myWS',
                             "/evaluations/latest", "scenario evaluation")

        self.assertIn('scenario evaluation', str(ctx.exception))

    @patch('azext_chaos.custom.send_raw_request')
    def test_inner_404_does_not_raise(self, mock_send):
        """A /latest 404 on a brand-new workspace must not flip the command
        to non-zero — only an explicit Failed inner status does."""
        from azext_chaos.custom import _check_inner_lro

        # 404 on /latest: empty text → silently treated as "no result yet".
        mock_send.return_value = _make_response(
            status_code=404, text="", json_body={},
        )
        # Should not raise.
        _check_inner_lro(_make_cmd().cli_ctx, 'myRG', 'myWS',
                         "/discoveries/latest", "resource discovery")

    @patch('azext_chaos.custom.send_raw_request')
    def test_inner_succeeded_does_not_raise(self, mock_send):
        """A Succeeded inner status must not flip the command to non-zero."""
        from azext_chaos.custom import _check_inner_lro

        mock_send.return_value = _make_response(
            json_body={"properties": {"status": "Succeeded"}},
        )
        # Should not raise.
        _check_inner_lro(_make_cmd().cli_ctx, 'myRG', 'myWS',
                         "/discoveries/latest", "resource discovery")

    # ``test_inner_check_skipped_for_no_wait`` was removed: the AAZ
    # framework now owns the polling lifecycle. When ``--no-wait`` is
    # passed, ``post_operations`` is not invoked at all (the framework
    # short-circuits after the initial POST), so the inner-LRO checks are
    # naturally skipped. There is no custom code path to exercise.


class TestExtractRunIdRobust(unittest.TestCase):
    """M2 follow-up: run-id parser handles operation-URL Locations and
    --no-wait always returns a parseable shape."""

    def test_extract_from_scenario_runs_segment(self):
        from azext_chaos.custom import _extract_run_id_from_location
        url = (
            "https://management.azure.com/subscriptions/sub1/resourceGroups/"
            "myRG/providers/Microsoft.Chaos/workspaces/myWS/"
            "scenarios/ZoneDown-1.0/scenarioRuns/abc-123?api-version=..."
        )
        self.assertEqual(_extract_run_id_from_location(url), "abc-123")

    def test_extract_from_runs_segment_legacy(self):
        """Backwards-compat: some Location headers use /runs/ not /scenarioRuns/."""
        from azext_chaos.custom import _extract_run_id_from_location
        url = (
            "/subscriptions/sub1/resourceGroups/myRG/providers/Microsoft.Chaos/"
            "workspaces/myWS/scenarios/ZoneDown-1.0/runs/legacy-run-77"
        )
        self.assertEqual(_extract_run_id_from_location(url), "legacy-run-77")

    def test_extract_returns_none_for_operation_url(self):
        """Operation-status Location URLs do not embed the run id."""
        from azext_chaos.custom import _extract_run_id_from_location
        url = (
            "/subscriptions/sub1/providers/Microsoft.Chaos/locations/westus2/"
            "operationResults/00000000-0000-0000-0000-000000000000"
        )
        self.assertIsNone(_extract_run_id_from_location(url))

    def test_extract_handles_no_input(self):
        from azext_chaos.custom import _extract_run_id_from_location
        self.assertIsNone(_extract_run_id_from_location(None))
        self.assertIsNone(_extract_run_id_from_location(""))

    @patch('azext_chaos.custom.send_raw_request')
    def test_async_op_fallback_reads_run_id_from_body(self, mock_send):
        from azext_chaos.custom import _fetch_run_id_from_async_op
        mock_send.return_value = _make_response(
            json_body={"properties": {"runId": "from-async-op"}}
        )
        self.assertEqual(
            _fetch_run_id_from_async_op(_make_cmd(), 'https://x/op'),
            "from-async-op",
        )

    @patch('azext_chaos.custom.send_raw_request')
    def test_async_op_fallback_handles_failures_silently(self, mock_send):
        from azext_chaos.custom import _fetch_run_id_from_async_op
        mock_send.side_effect = RuntimeError("network")
        self.assertIsNone(
            _fetch_run_id_from_async_op(_make_cmd(), 'https://x/op')
        )

    @patch('azext_chaos.custom._fetch_run_id_from_async_op')
    @patch('azext_chaos.custom._poll_or_return')
    @patch('azext_chaos.custom.send_raw_request')
    def test_run_start_no_wait_returns_parseable_shape_when_run_id_unknown(
        self, mock_send, mock_poll, mock_async_fallback,
    ):
        """Even if neither Location nor Azure-AsyncOperation surface the run
        id, --no-wait must return a parseable JSON shape (not None / empty)."""
        from azext_chaos.custom import scenario_run_start

        mock_poll.return_value = None
        mock_async_fallback.return_value = None  # fallback also fails
        op_url = (
            "/subscriptions/sub1/providers/Microsoft.Chaos/locations/westus2/"
            "operationResults/op-xyz"
        )
        mock_send.side_effect = [
            _make_response(),  # POST validate
            _make_response(json_body=_successful_validation_result()),  # GET validation
            _make_response(headers={  # POST execute
                "Location": op_url,
                "Azure-AsyncOperation": op_url,
            }),
        ]

        with self.assertLogs(_LOGGER_NAME, level='WARNING') as cm:
            result = scenario_run_start(
                _make_cmd(), 'myRG', 'myWS', 'ZoneDown', 'cfg-1',
                no_wait=True,
            )

        self.assertIsInstance(result, dict)
        self.assertIsNone(result['runId'])
        self.assertEqual(result['operationStatusUrl'], op_url)
        # Guidance message points the user at `run list` for recovery.
        self.assertIn('scenario run list', '\n'.join(cm.output))

    @patch('azext_chaos.custom._poll_or_return')
    @patch('azext_chaos.custom.send_raw_request')
    def test_run_start_no_wait_falls_back_to_async_op_body(
        self, mock_send, mock_poll,
    ):
        from azext_chaos.custom import scenario_run_start

        mock_poll.return_value = None
        # Location is an operation URL (no /runs/ segment), so the parser
        # fails. Then the async-op fallback GET retrieves the runId.
        op_url = (
            "/subscriptions/sub1/providers/Microsoft.Chaos/locations/westus2/"
            "operationResults/op-xyz"
        )
        mock_send.side_effect = [
            _make_response(headers={
                "Location": op_url,
                "Azure-AsyncOperation": op_url,
            }),  # POST execute
            _make_response(json_body={  # GET async-op (fallback)
                "properties": {"runId": "found-via-fallback"}
            }),
        ]

        result = scenario_run_start(
            _make_cmd(), 'myRG', 'myWS', 'ZoneDown', 'cfg-1',
            skip_validation=True, no_wait=True,
        )

        self.assertEqual(result['runId'], 'found-via-fallback')


if __name__ == '__main__':
    unittest.main()
