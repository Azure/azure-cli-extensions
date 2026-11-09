# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest import mock

from azure.cli.core.mock import DummyCli

from azext_resiliency.custom import OPERATION_ID_QUERY_COMMANDS

REPORT_URL = "https://contosoreports.blob.core.windows.net/reports/drill-report.pdf?sv=2024-01-01&sig=abc123"
LIST_REPORT_DOWNLOAD_URL = "resiliency drill drill-run list-report-download-url"


class _CompletedPolling:  # pylint: disable=too-few-public-methods
    """Stands in for the LRO polling of a completed operation whose final body is `body`."""

    def __init__(self, operation, body):
        self._operation = operation
        self._body = body

    def run(self):
        self._operation.deserialize_http_content = lambda session: self._body
        self._operation.on_200(None)

    def resource(self):
        return None


class ResiliencyCustomOutputTest(unittest.TestCase):

    def test_list_report_download_url_returns_url(self):
        """downloadUrl is marked secret in the spec; the command must still return it unchanged."""
        command_cls = OPERATION_ID_QUERY_COMMANDS[LIST_REPORT_DOWNLOAD_URL]
        operation_cls = command_cls.DrillRunsListReportDownloadUrl

        def fake_call(operation, *args, **kwargs):  # pylint: disable=unused-argument
            return _CompletedPolling(operation, {"downloadUrl": REPORT_URL})

        cli = DummyCli()
        # No login or network: the operation never builds a real HTTP client or sends a request.
        with mock.patch("azure.cli.core.aaz._command_ctx.AAZCommandCtx.get_http_client", return_value=None), \
                mock.patch.object(operation_cls, "__call__", fake_call):
            exit_code = cli.invoke(LIST_REPORT_DOWNLOAD_URL.split() + [
                "--service-group-name", "sg1", "--drill-name", "drill1", "--drill-run-name", "run1",
                "--operation-id", "3f1c2a4b-5d6e-4f70-8a9b-0c1d2e3f4a5b",
            ])

        self.assertEqual(exit_code, 0)
        self.assertEqual(cli.result.result, {"downloadUrl": REPORT_URL})
        # The response schema keeps the secret marker; only the command output shows it.
        self.assertTrue(operation_cls._build_schema_on_200().download_url._flags.get("secret"))  # pylint: disable=protected-access


if __name__ == "__main__":
    unittest.main()
