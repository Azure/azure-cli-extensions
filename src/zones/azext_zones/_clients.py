from azure.cli.core.util import send_raw_request
from azure.cli.core.commands.client_factory import get_subscription_id


API_VERSION = "2022-10-01"


class ARGClient():

    @classmethod
    def query(cls, cmd, query):
        management_hostname = cmd.cli_ctx.cloud.endpoints.management
        api_version = API_VERSION
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = ("{}/providers/Microsoft.ResourceGraph/resources?api-version={}")
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            api_version)

        requestBody = {
            "subscriptions": [sub_id],
            "query": query,
            "options": {
                "resultFormat": "objectArray"
            }
        }

        r = send_raw_request(cmd.cli_ctx, "POST", request_url, body=requestBody)
        return r.json()
