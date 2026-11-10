# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json

from unittest import TestCase
from unittest.mock import Mock, call, patch

from azure.cli.core.azclierror import (
    AzureResponseError,
    InvalidArgumentValueError,
    RequiredArgumentMissingError,
)

from azext_edgeoperator._format import transform_log_collection_list
from azext_edgeoperator.custom import (
    API_VERSION,
    collect_logs,
    collect_logs_indirect,
    list_log_collections,
    show_log_collection,
)

SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"
JOB_ID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
PROVIDER_URL = "https://management.example.com/subscriptions/{}/providers/Microsoft.EdgeOperator/".format(
    SUBSCRIPTION_ID
)
STATUS_URL = (
    "https://management.example.com/providers/Microsoft.EdgeOperator/locations/local/operationStatuses/op1"
    "?api-version=2026-06-01-preview&sig=redacted"
)
JOB_RESOURCE_ID = "/subscriptions/{}/providers/Microsoft.EdgeOperator/logCollections/{}".format(
    SUBSCRIPTION_ID, JOB_ID
)


def _response(body=None, headers=None):
    response = Mock()
    response.headers = headers or {}
    response.json.return_value = body
    return response


class LogCollectionCustomTest(TestCase):

    def setUp(self):
        subscription_patch = patch("azext_edgeoperator.custom.get_subscription_id")
        subscription_patch.start().return_value = SUBSCRIPTION_ID
        self.addCleanup(subscription_patch.stop)
        request_patch = patch("azext_edgeoperator.custom.send_raw_request")
        self.send_raw_request = request_patch.start()
        self.addCleanup(request_patch.stop)
        sleep_patch = patch("azext_edgeoperator.custom.time.sleep")
        self.sleep = sleep_patch.start()
        self.addCleanup(sleep_patch.stop)
        self.cli_ctx = Mock()
        self.cli_ctx.cloud.endpoints.resource_manager = "https://management.example.com/"
        self.cmd = Mock(cli_ctx=self.cli_ctx)

    def _sent_body(self, index=0):
        return json.loads(self.send_raw_request.call_args_list[index].kwargs["body"])

    def _accepted(self, retry_after="5"):
        return _response(headers={"Azure-AsyncOperation": STATUS_URL, "Retry-After": retry_after})

    def test_collect_waits_and_returns_resulting_job(self):
        job = {"id": JOB_RESOURCE_ID, "properties": {"provisioningState": "Succeeded"}}
        self.send_raw_request.side_effect = [
            self._accepted(),
            _response({"status": "InProgress"}, {"Retry-After": "2"}),
            _response({"status": "Succeeded", "properties": {"resourceId": JOB_RESOURCE_ID}}),
            _response(job),
        ]

        result = collect_logs(self.cmd, "2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z", filter_roles=["Agents"])

        self.assertEqual(result, job)
        post, first_poll, second_poll, get_job = self.send_raw_request.call_args_list
        self.assertEqual(post.args, (self.cli_ctx, "POST", PROVIDER_URL + "collectLogs?api-version=" + API_VERSION))
        self.assertEqual(self._sent_body(), {
            "fromDate": "2026-01-01T00:00:00Z",
            "toDate": "2026-01-02T00:00:00Z",
            "filterRoles": ["Agents"],
        })
        self.assertEqual(first_poll, call(self.cli_ctx, "GET", STATUS_URL))
        self.assertEqual(second_poll, call(self.cli_ctx, "GET", STATUS_URL))
        self.assertEqual(get_job, call(self.cli_ctx, "GET", JOB_RESOURCE_ID + "?api-version=" + API_VERSION))
        self.assertEqual(self.sleep.call_args_list, [call(5), call(2)])

    def test_collect_uses_default_poll_interval_without_valid_retry_after(self):
        self.send_raw_request.side_effect = [
            self._accepted(retry_after="soon"),
            _response({"status": "Succeeded", "properties": {"resourceId": JOB_RESOURCE_ID}}),
            _response({}),
        ]

        collect_logs(self.cmd, "2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z")

        self.sleep.assert_called_once_with(30)

    def test_collect_no_wait_returns_after_acceptance(self):
        self.send_raw_request.return_value = self._accepted()

        result = collect_logs(self.cmd, "2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z", no_wait=True)

        self.assertIsNone(result)
        self.send_raw_request.assert_called_once()
        self.sleep.assert_not_called()
        self.assertNotIn("filterRoles", self._sent_body())

    def test_collect_raises_when_operation_fails(self):
        self.send_raw_request.side_effect = [
            self._accepted(),
            _response({"status": "Failed", "error": {"code": "CollectionFailed", "message": "Disk full."}}),
        ]

        with self.assertRaisesRegex(AzureResponseError, "Failed.*CollectionFailed: Disk full."):
            collect_logs(self.cmd, "2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z")

    def test_collect_raises_without_async_operation_header(self):
        self.send_raw_request.return_value = _response(headers={"Location": STATUS_URL})

        with self.assertRaisesRegex(AzureResponseError, "Azure-AsyncOperation"):
            collect_logs(self.cmd, "2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z")

    def test_collect_returns_operation_status_without_resource_id(self):
        operation = {"status": "Succeeded"}
        self.send_raw_request.side_effect = [self._accepted(), _response(operation)]

        self.assertEqual(collect_logs(self.cmd, "2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z"), operation)

    def test_collect_normalizes_dates_to_utc(self):
        self.send_raw_request.return_value = self._accepted()

        collect_logs(self.cmd, "2026-01-01T02:00:00+02:00", "2026-01-02T00:00:00", no_wait=True)

        self.assertEqual(self._sent_body(), {
            "fromDate": "2026-01-01T00:00:00Z",
            "toDate": "2026-01-02T00:00:00Z",
        })

    def test_collect_rejects_invalid_time_range(self):
        for from_date, to_date, message in (
            ("2026-01-02T00:00:00Z", "2026-01-01T00:00:00Z", "--to-date must be later"),
            ("2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z", "--to-date must be later"),
            ("yesterday", "2026-01-01T00:00:00Z", "--from-date must be an ISO 8601"),
        ):
            with self.subTest(from_date=from_date, to_date=to_date):
                with self.assertRaisesRegex(InvalidArgumentValueError, message):
                    collect_logs(self.cmd, from_date, to_date)
        self.send_raw_request.assert_not_called()

    def test_collect_indirect_sends_destination_and_credentials(self):
        self.send_raw_request.return_value = self._accepted()

        collect_logs_indirect(
            self.cmd, "2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z", "C:\\Logs\\IndirectCollection",
            username="operator", password="secret", filter_roles=["Agents"], no_wait=True
        )

        self.assertEqual(self.send_raw_request.call_args.args[2],
                         PROVIDER_URL + "collectLogsIndirect?api-version=" + API_VERSION)
        self.assertEqual(self._sent_body(), {
            "fromDate": "2026-01-01T00:00:00Z",
            "toDate": "2026-01-02T00:00:00Z",
            "saveToPath": "C:\\Logs\\IndirectCollection",
            "userName": "operator",
            "userPassword": "secret",
            "filterRoles": ["Agents"],
        })

    def test_collect_indirect_omits_credentials_when_not_given(self):
        self.send_raw_request.return_value = self._accepted()

        collect_logs_indirect(self.cmd, "2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z", "C:\\Logs", no_wait=True)

        self.assertNotIn("userName", self._sent_body())
        self.assertNotIn("userPassword", self._sent_body())

    @patch("knack.prompting.prompt_pass", return_value="prompted")
    def test_collect_indirect_prompts_for_missing_password(self, prompt_pass):
        self.send_raw_request.return_value = self._accepted()

        collect_logs_indirect(self.cmd, "2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z", "C:\\Logs",
                              username="operator", no_wait=True)

        prompt_pass.assert_called_once()
        self.assertEqual(self._sent_body()["userPassword"], "prompted")

    def test_collect_indirect_requires_password_without_terminal(self):
        from knack.prompting import NoTTYException
        with patch("knack.prompting.prompt_pass", side_effect=NoTTYException):
            with self.assertRaisesRegex(RequiredArgumentMissingError, "--password"):
                collect_logs_indirect(self.cmd, "2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z", "C:\\Logs",
                                      username="operator")
        self.send_raw_request.assert_not_called()

    def test_collect_indirect_rejects_empty_destination(self):
        with self.assertRaisesRegex(InvalidArgumentValueError, "--save-to-path"):
            collect_logs_indirect(self.cmd, "2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z", "  ")
        self.send_raw_request.assert_not_called()

    def test_show_gets_job_by_guid(self):
        result = show_log_collection(self.cmd, JOB_ID)

        self.send_raw_request.assert_called_once_with(
            self.cli_ctx, "GET", PROVIDER_URL + "logCollections/{}?api-version={}".format(JOB_ID, API_VERSION)
        )
        self.assertEqual(result, self.send_raw_request.return_value.json.return_value)

    def test_show_rejects_non_guid_job_id(self):
        with self.assertRaisesRegex(InvalidArgumentValueError, "GUID"):
            show_log_collection(self.cmd, "not-a-guid")
        self.send_raw_request.assert_not_called()

    def test_list_encodes_from_date_and_follows_next_link(self):
        next_link = PROVIDER_URL + "logCollections?api-version=" + API_VERSION + "&page=2"
        self.send_raw_request.side_effect = [
            _response({"value": [{"name": "job1"}], "nextLink": next_link}),
            _response({"value": [{"name": "job2"}]}),
        ]

        result = list_log_collections(self.cmd, "2026-01-01T00:00:00+00:00")

        self.assertEqual(result, [{"name": "job1"}, {"name": "job2"}])
        self.assertEqual(self.send_raw_request.call_args_list, [
            call(self.cli_ctx, "GET", PROVIDER_URL + "logCollections?api-version={}&fromDate={}".format(
                API_VERSION, "2026-01-01T00%3A00%3A00Z")),
            call(self.cli_ctx, "GET", next_link),
        ])

    def test_list_table_format(self):
        rows = transform_log_collection_list([{
            "name": JOB_ID,
            "properties": {"provisioningState": "Succeeded", "state": "Completed", "jobType": "OnDemand",
                           "startTime": "2026-01-01T00:00:00Z", "endTime": None},
        }, {"name": "job-without-properties"}])

        self.assertEqual(list(rows[0].items()), [
            ("Name", JOB_ID), ("ProvisioningState", "Succeeded"), ("State", "Completed"),
            ("JobType", "OnDemand"), ("StartTime", "2026-01-01T00:00:00Z"), ("EndTime", None),
        ])
        self.assertEqual(rows[1]["Name"], "job-without-properties")
        self.assertIsNone(rows[1]["State"])
