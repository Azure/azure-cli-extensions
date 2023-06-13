
import json

from azure.cli.core.azclierror import AzureResponseError, ResourceNotFoundError
from azure.cli.core.util import send_raw_request
from azure.cli.core.commands.client_factory import get_subscription_id
from knack.log import get_logger

from ._utils import (_get_azext_module, GA_CONTAINERAPP_EXTENSION_NAME)

logger = get_logger(__name__)

PREVIEW_API_VERSION = "2023-04-01-preview"
CURRENT_API_VERSION = "2023-04-01-preview"
POLLING_TIMEOUT = 600  # how many seconds before exiting
POLLING_SECONDS = 2  # how many seconds between requests
POLLING_TIMEOUT_FOR_MANAGED_CERTIFICATE = 1500  # how many seconds before exiting
POLLING_INTERVAL_FOR_MANAGED_CERTIFICATE = 4  # how many seconds between requests
HEADER_AZURE_ASYNC_OPERATION = "azure-asyncoperation"
HEADER_LOCATION = "location"


def poll_status(cmd, request_url):
    azext_client = _get_azext_module(
        GA_CONTAINERAPP_EXTENSION_NAME, "azext_containerapp._clients")
    return azext_client.poll_status(cmd, request_url)


def poll_results(cmd, request_url):
    azext_client = _get_azext_module(
        GA_CONTAINERAPP_EXTENSION_NAME, "azext_containerapp._clients")
    return azext_client.poll_results(cmd, request_url)


class ContainerAppClient():
    @classmethod
    def create_or_update(cls, cmd, resource_group_name, name, container_app_envelope, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = CURRENT_API_VERSION
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(container_app_envelope))

        if no_wait:
            return r.json()
        elif r.status_code == 201:
            operation_url = r.headers.get(HEADER_AZURE_ASYNC_OPERATION)
            poll_status(cmd, operation_url)
            url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}?api-version={}"
            request_url = url_fmt.format(
                management_hostname.strip('/'),
                sub_id,
                resource_group_name,
                name,
                api_version)
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def update(cls, cmd, resource_group_name, name, container_app_envelope, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager

        api_version = CURRENT_API_VERSION

        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "PATCH", request_url, body=json.dumps(container_app_envelope))

        if no_wait:
            return
        elif r.status_code == 202:
            operation_url = r.headers.get(HEADER_LOCATION)
            response = poll_results(cmd, operation_url)
            if response is None:
                raise ResourceNotFoundError("Could not find a container app")
            else:
                return response

        return r.json()

    @classmethod
    def delete(cls, cmd, resource_group_name, name, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = CURRENT_API_VERSION
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "DELETE", request_url)

        if no_wait:
            return  # API doesn't return JSON (it returns no content)
        elif r.status_code in [200, 201, 202, 204]:
            if r.status_code == 202:
                operation_url = r.headers.get(HEADER_LOCATION)
                poll_results(cmd, operation_url)
                logger.warning('Containerapp successfully deleted')

    @classmethod
    def show(cls, cmd, resource_group_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = CURRENT_API_VERSION
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        return r.json()

    @classmethod
    def list_by_subscription(cls, cmd, formatter=lambda x: x):
        app_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = CURRENT_API_VERSION
        sub_id = get_subscription_id(cmd.cli_ctx)
        request_url = "{}/subscriptions/{}/providers/Microsoft.App/containerApps?api-version={}".format(
            management_hostname.strip('/'),
            sub_id,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        j = r.json()
        for app in j["value"]:
            formatted = formatter(app)
            app_list.append(formatted)

        while j.get("nextLink") is not None:
            request_url = j["nextLink"]
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)
            j = r.json()
            for app in j["value"]:
                formatted = formatter(app)
                app_list.append(formatted)

        return app_list

    @classmethod
    def list_by_resource_group(cls, cmd, resource_group_name, formatter=lambda x: x):
        app_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = CURRENT_API_VERSION
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        j = r.json()
        for app in j["value"]:
            formatted = formatter(app)
            app_list.append(formatted)

        while j.get("nextLink") is not None:
            request_url = j["nextLink"]
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)
            j = r.json()
            for app in j["value"]:
                formatted = formatter(app)
                app_list.append(formatted)

        return app_list

    @classmethod
    def list_secrets(cls, cmd, resource_group_name, name):

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = CURRENT_API_VERSION
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/listSecrets?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "POST", request_url, body=None)
        return r.json()

    @classmethod
    def list_revisions(cls, cmd, resource_group_name, name, formatter=lambda x: x):

        revisions_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = CURRENT_API_VERSION
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/revisions?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        j = r.json()
        for app in j["value"]:
            formatted = formatter(app)
            revisions_list.append(formatted)

        while j.get("nextLink") is not None:
            request_url = j["nextLink"]
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)
            j = r.json()
            for app in j["value"]:
                formatted = formatter(app)
                revisions_list.append(formatted)

        return revisions_list

    @classmethod
    def show_revision(cls, cmd, resource_group_name, container_app_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = CURRENT_API_VERSION
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/revisions/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            container_app_name,
            name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        return r.json()

    @classmethod
    def restart_revision(cls, cmd, resource_group_name, container_app_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = CURRENT_API_VERSION
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/revisions/{}/restart?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            container_app_name,
            name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "POST", request_url)
        return r.json()

    @classmethod
    def activate_revision(cls, cmd, resource_group_name, container_app_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = CURRENT_API_VERSION
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/revisions/{}/activate?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            container_app_name,
            name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "POST", request_url)
        return r.json()

    @classmethod
    def deactivate_revision(cls, cmd, resource_group_name, container_app_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = CURRENT_API_VERSION
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/revisions/{}/deactivate?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            container_app_name,
            name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "POST", request_url)
        return r.json()

    @classmethod
    def list_replicas(cls, cmd, resource_group_name, container_app_name, revision_name):
        replica_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/revisions/{}/replicas?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            container_app_name,
            revision_name,
            CURRENT_API_VERSION)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        j = r.json()
        for replica in j["value"]:
            replica_list.append(replica)

        while j.get("nextLink") is not None:
            request_url = j["nextLink"]
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)
            j = r.json()
            for replica in j["value"]:
                replica_list.append(replica)

        return replica_list

    @classmethod
    def get_replica(cls, cmd, resource_group_name, container_app_name, revision_name, replica_name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/revisions/{}/replicas/{}/?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            container_app_name,
            revision_name,
            replica_name,
            CURRENT_API_VERSION)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        return r.json()

    @classmethod
    def get_auth_token(cls, cmd, resource_group_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/getAuthToken?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            CURRENT_API_VERSION)

        r = send_raw_request(cmd.cli_ctx, "POST", request_url)
        return r.json()

    @classmethod
    def validate_domain(cls, cmd, resource_group_name, name, hostname):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/listCustomHostNameAnalysis?api-version={}&customHostname={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            CURRENT_API_VERSION,
            hostname)

        r = send_raw_request(cmd.cli_ctx, "POST", request_url)
        return r.json()
