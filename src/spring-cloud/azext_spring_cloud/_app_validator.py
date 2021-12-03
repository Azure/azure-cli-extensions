# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-few-public-methods, unused-argument, redefined-builtin

from azure.cli.core.azclierror import InvalidArgumentValueError
from msrestazure.azure_exceptions import CloudError
from ._client_factory import cf_spring_cloud


# pylint: disable=line-too-long,raise-missing-from
NO_PRODUCTION_DEPLOYMENT_ERROR = "No production deployment found, use --deployment to specify deployment or create deployment with: az spring-cloud app deployment create"


def fulfill_deployment_param(cmd, namespace):
    client = cf_spring_cloud(cmd.cli_ctx)
    if not namespace.name or not namespace.service or not namespace.resource_group:
        return
    if namespace.deployment:
        namespace.deployment = _ensure_deployment_exist(client, namespace.resource_group, namespace.service, namespace.name, namespace.deployment)
    else:
        namespace.deployment = _ensure_active_deployment_exist_and_get(client, namespace.resource_group, namespace.service, namespace.name)


def _ensure_deployment_exist(client, resource_group, service, app, deployment):
    try:
        return client.deployments.get(resource_group, service, app, deployment)
    except CloudError:
        raise InvalidArgumentValueError('Deployment {} not found under app {}'.format(deployment, app))


def _ensure_active_deployment_exist_and_get(client, resource_group, service, name):
    deployment_resource = _get_active_deployment(client, resource_group, service, name)
    if not deployment_resource:
        raise InvalidArgumentValueError(NO_PRODUCTION_DEPLOYMENT_ERROR)
    return deployment_resource


def _get_active_deployment(client, resource_group, service, name):
    deployments = client.deployments.list(resource_group, service, name)
    return next(iter(x for x in deployments if x.properties.active), None)
