from unittest import TestCase
from unittest.mock import Mock, patch

from azext_edgeoperator.custom import API_VERSION, show_system_readiness


class SystemReadinessCustomTest(TestCase):

    @patch("azext_edgeoperator.custom.send_raw_request")
    @patch("azext_edgeoperator.custom.get_subscription_id")
    def test_show_uses_singleton_resource(self, get_subscription_id, send_raw_request):
        get_subscription_id.return_value = "00000000-0000-0000-0000-000000000000"
        response = Mock()
        response.json.return_value = {"properties": {"systemReady": True}}
        send_raw_request.return_value = response

        cli_ctx = Mock()
        cli_ctx.cloud.endpoints.resource_manager = "https://management.example.com/"
        cmd = Mock(cli_ctx=cli_ctx)

        result = show_system_readiness(cmd)

        expected_url = (
            "https://management.example.com/subscriptions/"
            "00000000-0000-0000-0000-000000000000/providers/Microsoft.EdgeOperator/"
            "systemReadiness/default?api-version={}"
        ).format(API_VERSION)
        send_raw_request.assert_called_once_with(cli_ctx, "GET", expected_url)
        self.assertTrue(result["properties"]["systemReady"])
