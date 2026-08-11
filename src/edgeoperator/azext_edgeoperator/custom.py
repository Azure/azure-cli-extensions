from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.util import send_raw_request


API_VERSION = "2026-06-01-preview"


def _system_readiness_url(cmd):
    endpoint = cmd.cli_ctx.cloud.endpoints.resource_manager.rstrip("/")
    subscription_id = get_subscription_id(cmd.cli_ctx)
    return (
        "{}/subscriptions/{}/providers/Microsoft.EdgeOperator/"
        "systemReadiness/default?api-version={}"
    ).format(endpoint, subscription_id, API_VERSION)


def show_system_readiness(cmd):
    response = send_raw_request(cmd.cli_ctx, "GET", _system_readiness_url(cmd))
    return response.json()
