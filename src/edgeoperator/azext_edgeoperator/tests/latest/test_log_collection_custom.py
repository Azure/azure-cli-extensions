# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import io
import json
import tempfile
from copy import deepcopy

from unittest import TestCase
from unittest.mock import MagicMock, Mock, call, patch

from azure.cli.core.azclierror import (
    AzureResponseError,
    InvalidArgumentValueError,
    RequiredArgumentMissingError,
    MutuallyExclusiveArgumentError,
)

from azext_edgeoperator._format import transform_log_collection_list
from azext_edgeoperator.commands import load_command_table
from azext_edgeoperator.custom import (
    API_VERSION,
    collect_logs,
    collect_logs_indirect,
    list_log_collections,
    show_log_collection,
    wait_log_collection,
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
    response.content = json.dumps(body).encode("utf-8") if body is not None else b""
    return response


class LogCollectionCustomTest(TestCase):

    def setUp(self):
        from azure.cli.core import _session
        # CLI invocation tests initialize global sessions with temporary configuration paths.
        for session in vars(_session).values():
            if isinstance(session, _session.Session):
                session_patch = patch.dict(vars(session), deepcopy(vars(session)), clear=True)
                session_patch.start()
                self.addCleanup(session_patch.stop)
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

    def _completed_collection(self):
        job = {"id": JOB_RESOURCE_ID, "name": JOB_ID, "properties": {"provisioningState": "Succeeded"}}
        self.send_raw_request.side_effect = [
            self._accepted(),
            _response({"status": "Succeeded", "properties": {"resourceId": JOB_RESOURCE_ID}}),
            _response(job),
        ]
        return job

    def test_collect_waits_and_returns_resulting_job(self):
        job = {"id": JOB_RESOURCE_ID, "name": JOB_ID, "properties": {"provisioningState": "Succeeded"}}
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

    def test_collect_accepts_json_null_body(self):
        job = self._completed_collection()
        accepted = self._accepted()
        accepted.content = b"null"
        self.send_raw_request.side_effect = [
            accepted,
            _response({"status": "Succeeded", "properties": {"resourceId": JOB_RESOURCE_ID}}),
            _response(job),
        ]

        result = collect_logs(self.cmd, "2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z")

        self.assertEqual(result, job)
        accepted.json.assert_not_called()
        self.assertEqual(self.send_raw_request.call_count, 3)

    def test_collect_no_wait_sanitizes_operation_url(self):
        base = "https://management.example.com/providers/Microsoft.EdgeOperator/locations/local/operationStatuses/op1*ABC123"
        for query, expected in (
            ("?api-version=2026-06-01-preview&sig=secret&token=secret#fragment",
             "?api-version=2026-06-01-preview"),
            ("?sig=secret", "?api-version=" + API_VERSION),
        ):
            for body in (None, {"properties": {"resourceId": JOB_RESOURCE_ID}}):
                with self.subTest(query=query, body=body):
                    accepted = _response(body, {"Azure-AsyncOperation": base + query})
                    if body is None:
                        accepted.content = b"null"
                    self.send_raw_request.reset_mock(side_effect=True)
                    self.send_raw_request.return_value = accepted

                    result = collect_logs(
                        self.cmd, "2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z", no_wait=True,
                    )

                    self.assertEqual(result, {"status": "Accepted", "operationStatusUrl": base + expected})
                    self.send_raw_request.assert_called_once()
                    accepted.json.assert_not_called()
                    self.sleep.assert_not_called()

    def test_collect_no_wait_requires_operation_url(self):
        self.send_raw_request.return_value = _response()
        with self.assertRaisesRegex(AzureResponseError, "Azure-AsyncOperation"):
            collect_logs(self.cmd, "2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z", no_wait=True)
        self.send_raw_request.assert_called_once()
        self.sleep.assert_not_called()

    def test_cli_returns_completed_job_or_acceptance(self):
        from azure.cli.core import AzCli, MainCommandsLoader
        from azure.cli.core.commands import AzCliCommandInvoker
        from azure.cli.core.parser import AzCliCommandParser
        from azure.cli.core._help import AzCliHelp
        from azure.cli.core._output import AzOutputProducer
        from azext_edgeoperator import AldoCommandsLoader

        class LocalCommandsLoader(MainCommandsLoader):
            def load_command_table(self, args):
                loader = AldoCommandsLoader(self.cli_ctx)
                self.command_table.update(loader.load_command_table(args))
                self.cmd_to_loader_map = {name: [loader] for name in self.command_table}
                return self.command_table

        for command in ("collect", "collect-indirect"):
            for no_wait in (False, True):
                with self.subTest(command=command, no_wait=no_wait), \
                        tempfile.TemporaryDirectory(prefix="aldo-cli-test-") as config:
                    cli = AzCli(
                        cli_name="az", config_dir=config, config_env_var_prefix="AZURE",
                        commands_loader_cls=LocalCommandsLoader, invocation_cls=AzCliCommandInvoker,
                        parser_cls=AzCliCommandParser, output_cls=AzOutputProducer, help_cls=AzCliHelp,
                    )
                    cli.cloud.endpoints.resource_manager = "https://management.example.com/"
                    self.send_raw_request.reset_mock()
                    self.sleep.reset_mock()
                    job = self._completed_collection()
                    args = [
                        "aldo", "log-collection", command,
                        "--from-date", "2026-01-01T00:00:00Z", "--to-date", "2026-01-02T00:00:00Z",
                        "--output", "json",
                    ]
                    if command == "collect-indirect":
                        args.extend(["--save-to-path", "C:\\Logs"])
                    output = io.StringIO()

                    if no_wait:
                        args.append("--no-wait")
                        self.assertEqual(cli.invoke(args, out_file=output), 0)
                        self.assertEqual(json.loads(output.getvalue()), {
                            "status": "Accepted", "operationStatusUrl": STATUS_URL.split("&")[0],
                        })
                        self.send_raw_request.assert_called_once()
                        self.sleep.assert_not_called()
                        self.send_raw_request.reset_mock()
                        self.send_raw_request.side_effect = [
                            _response({"status": "Running"}, {"Retry-After": "2"}),
                            _response({"status": "Succeeded", "properties": {"resourceId": JOB_RESOURCE_ID}}),
                            _response(job),
                        ]
                        output = io.StringIO()
                        self.assertEqual(cli.invoke([
                            "aldo", "log-collection", "wait", "--operation-status-url",
                            STATUS_URL.split("&")[0], "--output", "json",
                        ], out_file=output), 0)
                        self.assertEqual(json.loads(output.getvalue()), job)
                        self.assertEqual(self.send_raw_request.call_count, 3)
                        self.sleep.assert_called_once_with(2)
                        continue

                    self.assertEqual(cli.invoke(args, out_file=output), 0)

                    self.assertEqual(json.loads(output.getvalue()), job)
                    self.assertNotIn(STATUS_URL, output.getvalue())
                    self.assertEqual(self.send_raw_request.call_count, 3)
                    self.assertEqual(self.send_raw_request.call_args_list[1].args[1:], ("GET", STATUS_URL))
                    self.sleep.assert_called_once_with(5)
                    self.send_raw_request.reset_mock(side_effect=True)
                    self.send_raw_request.return_value = _response(job)
                    output = io.StringIO()
                    self.assertEqual(cli.invoke([
                        "aldo", "log-collection", "wait", "--job-id", JOB_ID, "--created",
                    ], out_file=output), 0)
                    self.send_raw_request.assert_called_once()

    def test_wait_operation_uses_active_cloud_and_preserves_operation_name(self):
        operation_url = (
            "https://armmanagement.example.com/providers/Microsoft.EdgeOperator/locations/local/"
            "operationStatuses/op1*ABC123?api-version=2026-06-01-preview&sig=secret"
        )
        job = {"id": JOB_RESOURCE_ID, "name": JOB_ID}
        self.send_raw_request.side_effect = [
            _response({"status": "Running"}, {"Retry-After": "7"}),
            _response({
                "status": "Succeeded", "resourceId": "/not-the-collection",
                "properties": {"resourceId": JOB_RESOURCE_ID},
            }),
            _response(job),
        ]
        result = wait_log_collection(self.cmd, operation_status_url=operation_url)
        expected = operation_url.replace("armmanagement.example.com", "management.example.com").split("&")[0]
        self.assertEqual(result, job)
        self.assertEqual(self.send_raw_request.call_args_list, [
            call(self.cli_ctx, "GET", expected), call(self.cli_ctx, "GET", expected),
            call(self.cli_ctx, "GET", JOB_RESOURCE_ID + "?api-version=" + API_VERSION),
        ])
        self.sleep.assert_called_once_with(7)

    def test_wait_operation_reports_failures_and_missing_results(self):
        for operation, message in (
            ({"status": "Failed", "error": {"code": "CollectionFailed", "message": "Disk full."}}, "Disk full"),
            ({"status": "Canceled"}, "Canceled"),
            ({"status": "Succeeded"}, "properties.resourceId"),
            (None, "did not contain a status"),
        ):
            with self.subTest(operation=operation):
                self.send_raw_request.reset_mock(side_effect=True)
                self.send_raw_request.return_value = _response(operation)
                with self.assertRaisesRegex(AzureResponseError, message):
                    wait_log_collection(self.cmd, operation_status_url=STATUS_URL)
                self.send_raw_request.assert_called_once()

    def test_wait_validates_arguments_before_requesting(self):
        for args, error in (
            ({}, RequiredArgumentMissingError),
            ({"job_id": JOB_ID, "operation_status_url": STATUS_URL}, MutuallyExclusiveArgumentError),
            ({"operation_status_url": STATUS_URL, "created": True}, MutuallyExclusiveArgumentError),
            ({"operation_status_url": STATUS_URL, "timeout": 0}, InvalidArgumentValueError),
            ({"operation_status_url": STATUS_URL, "interval": 0}, InvalidArgumentValueError),
            ({"operation_status_url": "http://example.com/anything"}, InvalidArgumentValueError),
            ({"operation_status_url": "https://example.com/subscriptions/test"}, InvalidArgumentValueError),
        ):
            with self.subTest(args=args), self.assertRaises(error):
                wait_log_collection(self.cmd, **args)
        self.send_raw_request.assert_not_called()

    @patch("azext_edgeoperator.custom.time.monotonic", side_effect=[0, 0, 2])
    def test_wait_operation_timeout(self, _):
        self.send_raw_request.return_value = _response({"status": "Running"})
        with self.assertRaisesRegex(AzureResponseError, "timed out"):
            wait_log_collection(self.cmd, operation_status_url=STATUS_URL, timeout=1)
        self.send_raw_request.assert_called_once()
        self.cli_ctx.get_progress_controller.return_value.end.assert_called_once()

    def test_wait_operation_interval_override(self):
        self.send_raw_request.side_effect = [
            _response({"status": "Running"}, {"Retry-After": "7"}),
            _response({"status": "Succeeded", "properties": {"resourceId": JOB_RESOURCE_ID}}),
            _response({"name": JOB_ID}),
        ]
        wait_log_collection(self.cmd, operation_status_url=STATUS_URL, interval=3)
        self.sleep.assert_called_once_with(3)

    def test_wait_existing_job_preserves_created_condition(self):
        self.send_raw_request.return_value = _response({"properties": {"provisioningState": "Succeeded"}})
        result = wait_log_collection(self.cmd, job_id=JOB_ID, created=True)
        self.assertIsNone(result)
        self.send_raw_request.assert_called_once_with(
            self.cli_ctx, "GET", PROVIDER_URL + "logCollections/" + JOB_ID + "?api-version=" + API_VERSION,
        )

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

    def test_collect_raises_without_result_resource_id(self):
        operation = {"status": "Succeeded"}
        self.send_raw_request.side_effect = [self._accepted(), _response(operation)]

        with self.assertRaisesRegex(AzureResponseError, "properties.resourceId"):
            collect_logs(self.cmd, "2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z")
        self.assertEqual(self.send_raw_request.call_count, 2)

    def test_collect_raises_when_operation_is_canceled(self):
        self.send_raw_request.side_effect = [self._accepted(), _response({"status": "Canceled"})]

        with self.assertRaisesRegex(AzureResponseError, "Canceled"):
            collect_logs(self.cmd, "2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z")
        self.assertEqual(self.send_raw_request.call_count, 2)

    def test_collect_normalizes_dates_to_utc(self):
        self._completed_collection()

        collect_logs(self.cmd, "2026-01-01T02:00:00+02:00", "2026-01-02T00:00:00")

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
        job = self._completed_collection()

        result = collect_logs_indirect(
            self.cmd, "2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z", "C:\\Logs\\IndirectCollection",
            username="operator", password="secret", filter_roles=["Agents"]
        )

        self.assertEqual(result, job)
        self.assertEqual(self.send_raw_request.call_args_list[0].args[2],
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
        self._completed_collection()

        collect_logs_indirect(self.cmd, "2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z", "C:\\Logs")

        self.assertNotIn("userName", self._sent_body())
        self.assertNotIn("userPassword", self._sent_body())

    def test_collect_indirect_waits_and_fetches_exact_result(self):
        job = {"id": JOB_RESOURCE_ID, "name": JOB_ID, "properties": {"provisioningState": "Succeeded"}}
        self.send_raw_request.side_effect = [
            self._accepted(),
            _response({"status": "Succeeded", "properties": {"resourceId": JOB_RESOURCE_ID}}),
            _response(job),
        ]

        result = collect_logs_indirect(
            self.cmd, "2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z", "C:\\Logs",
        )

        self.assertEqual(result, job)
        self.assertEqual(self.send_raw_request.call_count, 3)
        self.assertEqual(self.send_raw_request.call_args_list[1:], [
            call(self.cli_ctx, "GET", STATUS_URL),
            call(self.cli_ctx, "GET", JOB_RESOURCE_ID + "?api-version=" + API_VERSION),
        ])

    @patch("knack.prompting.prompt_pass", return_value="prompted")
    def test_collect_indirect_prompts_for_missing_password(self, prompt_pass):
        self._completed_collection()

        collect_logs_indirect(self.cmd, "2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z", "C:\\Logs",
                              username="operator")

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

    def test_command_groups_preserve_existing_commands_and_add_only_log_collection(self):
        loader = MagicMock()

        load_command_table(loader, None)

        self.assertEqual(loader.command_group.call_args_list, [
            call("aldo system-readiness"),
            call("aldo observability-configuration"),
            call("aldo system-configuration"),
            call("aldo log-collection"),
        ])
        group = loader.command_group.return_value.__enter__.return_value
        group.custom_command.assert_any_call("collect", "collect_logs")
        group.custom_command.assert_any_call("collect-indirect", "collect_logs_indirect")
        group.custom_show_command.assert_any_call("show", "show_log_collection")
        group.custom_command.assert_any_call("list", "list_log_collections",
                                            table_transformer=transform_log_collection_list)
        group.custom_command.assert_any_call("wait", "wait_log_collection")
        group.custom_wait_command.assert_not_called()
