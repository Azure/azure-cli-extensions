# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, super-with-arguments, too-many-instance-attributes, consider-using-f-string, no-else-return, no-self-use

import json
import time
import sys

from azure.cli.core.azclierror import AzureResponseError, ResourceNotFoundError
from azure.cli.core.util import send_raw_request
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.command_modules.containerapp._clients import (
    poll_status,
    poll_results,
    AuthClient,
    GitHubActionClient,
    ContainerAppClient,
    ContainerAppsJobClient,
    DaprComponentClient,
    ManagedEnvironmentClient,
    WorkloadProfileClient,
    StorageClient)

from knack.log import get_logger

logger = get_logger(__name__)

PREVIEW_API_VERSION = "2023-11-02-preview"
POLLING_TIMEOUT = 1500  # how many seconds before exiting
POLLING_SECONDS = 2  # how many seconds between requests
POLLING_TIMEOUT_FOR_MANAGED_CERTIFICATE = 1500  # how many seconds before exiting
POLLING_INTERVAL_FOR_MANAGED_CERTIFICATE = 4  # how many seconds between requests
HEADER_AZURE_ASYNC_OPERATION = "azure-asyncoperation"
HEADER_LOCATION = "location"


class GitHubActionPreviewClient(GitHubActionClient):
    api_version = PREVIEW_API_VERSION


# Clients for preview
class ContainerAppPreviewClient(ContainerAppClient):
    api_version = PREVIEW_API_VERSION


class ContainerAppsJobPreviewClient(ContainerAppsJobClient):
    api_version = PREVIEW_API_VERSION


class ContainerAppsResiliencyPreviewClient():
    api_version = PREVIEW_API_VERSION

    @classmethod
    def create_or_update(cls, cmd, resource_group_name, name, container_app_name, container_app_resiliency_envelope, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/resiliencyPolicies/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            container_app_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(container_app_resiliency_envelope))

        if no_wait:
            return r.json()
        elif r.status_code == 201:
            operation_url = r.headers.get(HEADER_AZURE_ASYNC_OPERATION)
            poll_status(cmd, operation_url)
            url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/resiliencyPolicies/{}?api-version={}"
            request_url = url_fmt.format(
                management_hostname.strip('/'),
                sub_id,
                resource_group_name,
                container_app_name,
                name,
                cls.api_version)

            r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def update(cls, cmd, resource_group_name, name, container_app_name, container_app_resiliency_envelope, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager

        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/resiliencyPolicies/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            container_app_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PATCH", request_url, body=json.dumps(container_app_resiliency_envelope))

        if no_wait:
            return
        elif r.status_code == 202:
            operation_url = r.headers.get(HEADER_LOCATION)
            response = poll_results(cmd, operation_url)
            if response is None:
                raise ResourceNotFoundError("Could not find the app resiliency policy")
            else:
                return response

        return r.json()

    @classmethod
    def delete(cls, cmd, resource_group_name, name, container_app_name, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/resiliencyPolicies/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            container_app_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "DELETE", request_url)

        if no_wait:
            return  # API doesn't return JSON (it returns no content)
        elif r.status_code in [200, 201, 202, 204]:
            if r.status_code == 202:
                operation_url = r.headers.get(HEADER_LOCATION)
                poll_results(cmd, operation_url)
                logger.warning('App Resiliency Policy successfully deleted')

    @classmethod
    def show(cls, cmd, resource_group_name, name, container_app_name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/resiliencyPolicies/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            container_app_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def list(cls, cmd, resource_group_name, container_app_name):
        policy_list = []
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/resiliencyPolicies?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            container_app_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        r = r.json()

        for policy in r["value"]:
            policy_list.append(policy)

        return policy_list


class DaprComponentResiliencyPreviewClient():
    api_version = PREVIEW_API_VERSION

    @classmethod
    def create_or_update(cls, cmd, name, resource_group_name, dapr_component_name, environment_name, component_resiliency_envelope, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/daprComponents/{}/resiliencyPolicies/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            dapr_component_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(component_resiliency_envelope))

        if no_wait:
            return r.json()
        elif r.status_code == 201:
            operation_url = r.headers.get(HEADER_AZURE_ASYNC_OPERATION)
            poll_status(cmd, operation_url)
            url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/daprComponents/{}/resiliencyPolicies/{}?api-version={}"
            request_url = url_fmt.format(
                management_hostname.strip('/'),
                sub_id,
                resource_group_name,
                environment_name,
                dapr_component_name,
                name,
                cls.api_version)

            r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def delete(cls, cmd, name, resource_group_name, dapr_component_name, environment_name, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/daprComponents/{}/resiliencyPolicies/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            dapr_component_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "DELETE", request_url)

        if no_wait:
            return  # API doesn't return JSON (it returns no content)
        elif r.status_code in [200, 201, 202, 204]:
            if r.status_code == 202:
                operation_url = r.headers.get(HEADER_LOCATION)
                poll_results(cmd, operation_url)
                logger.warning('Dapr Component Resiliency Policy successfully deleted')

    @classmethod
    def show(cls, cmd, name, resource_group_name, dapr_component_name, environment_name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/daprComponents/{}/resiliencyPolicies/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            dapr_component_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def list(cls, cmd, resource_group_name, dapr_component_name, environment_name):
        policy_list = []
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/daprComponents/{}/resiliencyPolicies?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            dapr_component_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        r = r.json()

        for policy in r["value"]:
            policy_list.append(policy)

        return policy_list


class SubscriptionPreviewClient():
    api_version = PREVIEW_API_VERSION

    @classmethod
    def show_custom_domain_verification_id(cls, cmd):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        request_url = f"{management_hostname}subscriptions/{sub_id}/providers/Microsoft.App/getCustomDomainVerificationId?api-version={cls.api_version}"

        r = send_raw_request(cmd.cli_ctx, "POST", request_url)
        return r.json()

    @classmethod
    def list_usages(cls, cmd, location):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        request_url = f"{management_hostname}subscriptions/{sub_id}/providers/Microsoft.App/locations/{location}/usages?api-version={cls.api_version}"

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        return r.json()


class StoragePreviewClient(StorageClient):
    api_version = PREVIEW_API_VERSION


class ManagedEnvironmentPreviewClient(ManagedEnvironmentClient):
    api_version = PREVIEW_API_VERSION

    @classmethod
    def update(cls, cmd, resource_group_name, name, managed_environment_envelope, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PATCH", request_url, body=json.dumps(managed_environment_envelope))

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
    def list_usages(cls, cmd, resource_group_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/usages?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        return r.json()


class AuthPreviewClient(AuthClient):
    api_version = PREVIEW_API_VERSION


class ConnectedEnvironmentClient():
    api_version = PREVIEW_API_VERSION

    @classmethod
    def create(cls, cmd, resource_group_name, name, connected_environment_envelope, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(connected_environment_envelope))

        if no_wait:
            return r.json()
        elif r.status_code == 201:
            operation_url = r.headers.get(HEADER_AZURE_ASYNC_OPERATION)
            poll_status(cmd, operation_url)
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def update(cls, cmd, resource_group_name, name, managed_environment_envelope, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PATCH", request_url, body=json.dumps(managed_environment_envelope))

        if no_wait:
            return
        elif r.status_code == 202:
            operation_url = r.headers.get(HEADER_LOCATION)
            response = poll_results(cmd, operation_url)
            if response is None:
                raise ResourceNotFoundError("Could not find a connected environment")
            else:
                return response

        return r.json()

    @classmethod
    def delete(cls, cmd, resource_group_name, name, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "DELETE", request_url)

        if no_wait:
            return  # API doesn't return JSON (it returns no content)
        elif r.status_code in [200, 201, 202, 204]:
            if r.status_code == 202:
                operation_url = r.headers.get(HEADER_LOCATION)
                poll_results(cmd, operation_url)
                logger.warning('Connected environment successfully deleted')
        return

    @classmethod
    def show(cls, cmd, resource_group_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        return r.json()

    @classmethod
    def list_by_subscription(cls, cmd, formatter=lambda x: x):
        env_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        request_url = "{}/subscriptions/{}/providers/Microsoft.App/connectedEnvironments?api-version={}".format(
            management_hostname.strip('/'),
            sub_id,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        j = r.json()
        for env in j["value"]:
            formatted = formatter(env)
            env_list.append(formatted)

        while j.get("nextLink") is not None:
            request_url = j["nextLink"]
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)
            j = r.json()
            for env in j["value"]:
                formatted = formatter(env)
                env_list.append(formatted)

        return env_list

    @classmethod
    def list_by_resource_group(cls, cmd, resource_group_name, formatter=lambda x: x):
        env_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        j = r.json()
        for env in j["value"]:
            formatted = formatter(env)
            env_list.append(formatted)

        while j.get("nextLink") is not None:
            request_url = j["nextLink"]
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)
            j = r.json()
            for env in j["value"]:
                formatted = formatter(env)
                env_list.append(formatted)

        return env_list


class ConnectedEnvCertificateClient():
    api_version = PREVIEW_API_VERSION

    @classmethod
    def show_certificate(cls, cmd, resource_group_name, name, certificate_name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/certificates/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            certificate_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url, body=None)
        return r.json()

    @classmethod
    def list_certificates(cls, cmd, resource_group_name, name, formatter=lambda x: x):
        certs_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/certificates?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url, body=None)
        j = r.json()
        for cert in j["value"]:
            formatted = formatter(cert)
            certs_list.append(formatted)
        return certs_list

    @classmethod
    def create_or_update_certificate(cls, cmd, resource_group_name, name, certificate_name, certificate):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/certificates/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            certificate_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(certificate))
        return r.json()

    @classmethod
    def delete_certificate(cls, cmd, resource_group_name, name, certificate_name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/certificates/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            certificate_name,
            cls.api_version)

        return send_raw_request(cmd.cli_ctx, "DELETE", request_url, body=None)

    @classmethod
    def check_name_availability(cls, cmd, resource_group_name, name, name_availability_request):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = PREVIEW_API_VERSION
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/checkNameAvailability?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "POST", request_url, body=json.dumps(name_availability_request))
        return r.json()


class ConnectedEnvDaprComponentClient():
    api_version = PREVIEW_API_VERSION

    @classmethod
    def create_or_update(cls, cmd, resource_group_name, environment_name, name, dapr_component_envelope):

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/daprComponents/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(dapr_component_envelope))

        return r.json()

    @classmethod
    def delete(cls, cmd, resource_group_name, environment_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/daprComponents/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            name,
            cls.api_version)

        send_raw_request(cmd.cli_ctx, "DELETE", request_url)
        return

    @classmethod
    def show(cls, cmd, resource_group_name, environment_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/daprComponents/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        return r.json()

    @classmethod
    def list(cls, cmd, resource_group_name, environment_name, formatter=lambda x: x):
        app_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        request_url = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/daprComponents?api-version={}".format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            cls.api_version)

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


class ConnectedEnvStorageClient():
    api_version = PREVIEW_API_VERSION

    @classmethod
    def create_or_update(cls, cmd, resource_group_name, env_name, name, storage_envelope):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/storages/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            env_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(storage_envelope))

        return r.json()

    @classmethod
    def delete(cls, cmd, resource_group_name, env_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/storages/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            env_name,
            name,
            cls.api_version)

        send_raw_request(cmd.cli_ctx, "DELETE", request_url)

        return

    @classmethod
    def show(cls, cmd, resource_group_name, env_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/storages/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            env_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        return r.json()

    @classmethod
    def list(cls, cmd, resource_group_name, env_name, formatter=lambda x: x):
        env_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/storages?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            env_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        j = r.json()
        for env in j["value"]:
            formatted = formatter(env)
            env_list.append(formatted)

        while j.get("nextLink") is not None:
            request_url = j["nextLink"]
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)
            j = r.json()
            for env in j["value"]:
                formatted = formatter(env)
                env_list.append(formatted)

        return env_list


class DaprComponentPreviewClient(DaprComponentClient):
    api_version = PREVIEW_API_VERSION


class BuilderClient():
    api_version = PREVIEW_API_VERSION

    @classmethod
    def list(cls, cmd, resource_group_name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/builders?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            cls.api_version)
        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        return r.json()

    @classmethod
    def create(cls, cmd, builder_name, resource_group_name, environment_name, location, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/builders/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            builder_name,
            cls.api_version)
        body_data = {
            "location": location,
            "properties": {
                "environmentId": f"/subscriptions/{sub_id}/resourceGroups/{resource_group_name}/providers/Microsoft.App/managedEnvironments/{environment_name}"
            }
        }

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(body_data))

        if no_wait:
            return r.json()
        elif r.status_code == 201:
            operation_url = r.headers.get(HEADER_AZURE_ASYNC_OPERATION)
            poll_status(cmd, operation_url)
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()


class BuildClient():
    api_version = PREVIEW_API_VERSION

    @classmethod
    def create(cls, cmd, builder_name, build_name, resource_group_name, location, build_env_vars, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/builders/{}/builds/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            builder_name,
            build_name,
            cls.api_version)
        body_data = {
            "location": location,
            "properties": {
                "configuration": {
                    "environmentVariables": build_env_vars
                }
            }
        }

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(body_data))

        if no_wait:
            return r.json()
        elif r.status_code == 201:
            operation_url = r.headers.get(HEADER_AZURE_ASYNC_OPERATION)
            poll_status(cmd, operation_url)
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def get(cls, cmd, builder_name, build_name, resource_group_name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/builders/{}/builds/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            builder_name,
            build_name,
            cls.api_version)
        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        return r.json()

    @classmethod
    def list_auth_token(cls, cmd, builder_name, build_name, resource_group_name, location):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/builders/{}/builds/{}/listAuthToken?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            builder_name,
            build_name,
            cls.api_version)
        body_data = {
            "location": location,
            "properties": {}
        }
        r = send_raw_request(cmd.cli_ctx, "POST", request_url, body=json.dumps(body_data))
        return r.json()


class JavaComponentPreviewClient():
    api_version = PREVIEW_API_VERSION

    @classmethod
    def create(cls, cmd, resource_group_name, environment_name, name, java_component_envelope, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/javaComponents/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(java_component_envelope))

        if no_wait:
            return r.json()
        elif r.status_code == 201:
            operation_url = r.headers.get(HEADER_AZURE_ASYNC_OPERATION)
            poll_status(cmd, operation_url)
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def update(cls, cmd, resource_group_name, environment_name, name, java_component_envelope, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/javaComponents/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PATCH", request_url, body=json.dumps(java_component_envelope))

        if no_wait:
            return
        elif r.status_code == 202:
            operation_url = r.headers.get(HEADER_LOCATION)
            response = poll_results(cmd, operation_url)
            if response is None:
                raise ResourceNotFoundError("Could not find the Java component")
            else:
                return response

        return r.json()

    @classmethod
    def delete(cls, cmd, resource_group_name, environment_name, name, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/javaComponents/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "DELETE", request_url)

        if no_wait:
            return  # API doesn't return JSON (it returns no content)
        elif r.status_code in [200, 201, 202, 204]:
            if r.status_code == 202:
                operation_url = r.headers.get(HEADER_LOCATION)
                poll_results(cmd, operation_url)
                logger.warning('Java component successfully deleted')

    @classmethod
    def show(cls, cmd, resource_group_name, environment_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/javaComponents/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def list(cls, cmd, resource_group_name, environment_name):
        java_component_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/javaComponents?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        r = r.json()

        for component in r["value"]:
            java_component_list.append(component)

        return java_component_list
