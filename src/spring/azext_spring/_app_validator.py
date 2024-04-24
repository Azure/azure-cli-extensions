# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-few-public-methods, unused-argument, redefined-builtin
from knack.log import get_logger
from azure.cli.core.azclierror import InvalidArgumentValueError
from msrestazure.azure_exceptions import CloudError
from azure.core.exceptions import ResourceNotFoundError
from ._resource_quantity import (validate_cpu as validate_cpu_value, validate_memory as validate_memory_value)
from ._client_factory import cf_spring
from ._build_service import (DEFAULT_BUILD_SERVICE_NAME)
from ._utils import get_spring_sku


logger = get_logger(__name__)


# pylint: disable=line-too-long,raise-missing-from
NO_PRODUCTION_DEPLOYMENT_ERROR = "No production deployment found, use --deployment to specify deployment or create deployment with: az spring app deployment create"
NO_PRODUCTION_DEPLOYMENT_SET_ERROR = "This app has no production deployment, use \"az spring app deployment create\" to create a deployment and \"az spring app set-deployment\" to set production deployment."


def fulfill_deployment_param(cmd, namespace):
    client = cf_spring(cmd.cli_ctx)
    name = _get_app_name_from_namespace(namespace)
    if not name or not namespace.service or not namespace.resource_group:
        return
    if namespace.deployment:
        namespace.deployment = _ensure_deployment_exist(client, namespace.resource_group, namespace.service, name, namespace.deployment)
    else:
        namespace.deployment = _ensure_active_deployment_exist_and_get(client, namespace.resource_group, namespace.service, name)


def fulfill_deployment_param_or_warning(cmd, namespace):
    client = cf_spring(cmd.cli_ctx)
    name = _get_app_name_from_namespace(namespace)
    if not name or not namespace.service or not namespace.resource_group:
        return
    if namespace.deployment:
        namespace.deployment = _ensure_deployment_exist(client, namespace.resource_group, namespace.service, name, namespace.deployment)
    else:
        namespace.deployment = _get_active_deployment(client, namespace.resource_group, namespace.service, name)
        if not namespace.deployment:
            logger.warning(NO_PRODUCTION_DEPLOYMENT_SET_ERROR)


def active_deployment_exist(cmd, namespace):
    name = _get_app_name_from_namespace(namespace)
    if not name or not namespace.service or not namespace.resource_group:
        return
    client = cf_spring(cmd.cli_ctx)
    deployment = _get_active_deployment(client, namespace.resource_group, namespace.service, name)
    if not deployment:
        raise InvalidArgumentValueError(NO_PRODUCTION_DEPLOYMENT_SET_ERROR)


def active_deployment_exist_or_warning(cmd, namespace):
    name = _get_app_name_from_namespace(namespace)
    if not name or not namespace.service or not namespace.resource_group:
        return
    client = cf_spring(cmd.cli_ctx)
    deployment = _get_active_deployment(client, namespace.resource_group, namespace.service, name)
    if not deployment:
        logger.warning(NO_PRODUCTION_DEPLOYMENT_SET_ERROR)


def ensure_not_active_deployment(cmd, namespace):
    """
    Validate namespace.deployment is not active
    """
    if not namespace.deployment or not namespace.resource_group or not namespace.service or not namespace.name:
        return
    client = cf_spring(cmd.cli_ctx)
    deployment = _ensure_deployment_exist(client, namespace.resource_group, namespace.service, namespace.name, namespace.deployment)
    if deployment.properties.active:
        raise InvalidArgumentValueError('Deployment {} is already the production deployment'.format(deployment.name))


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
    try:
        deployments = client.deployments.list(resource_group, service, name)
        return next(iter(x for x in deployments if x.properties.active), None)
    except ResourceNotFoundError:
        raise InvalidArgumentValueError('App {} not found'.format(name))


def validate_deloy_path(cmd, namespace):
    arguments = [namespace.artifact_path, namespace.source_path, namespace.container_image]
    if all(not x for x in arguments):
        raise InvalidArgumentValueError('One of --artifact-path, --source-path, --container-image must be provided.')
    _deploy_path_mutual_exclusive(arguments)
    _validate_container_registry(cmd, namespace)


def validate_deloyment_create_path(cmd, namespace):
    arguments = [namespace.artifact_path, namespace.source_path, namespace.container_image]
    _deploy_path_mutual_exclusive(arguments)
    _validate_container_registry(cmd, namespace)


def _deploy_path_mutual_exclusive(args):
    valued_args = [x for x in args if x]
    if len(valued_args) > 1:
        raise InvalidArgumentValueError('At most one of --artifact-path, --source-path, --container-image must be provided.')


def validate_cpu(namespace):
    namespace.cpu = validate_cpu_value(namespace.cpu)


def validate_build_cpu(namespace):
    namespace.build_cpu = validate_cpu_value(namespace.build_cpu)


def validate_memory(namespace):
    namespace.memory = validate_memory_value(namespace.memory)


def validate_build_memory(namespace):
    namespace.build_memory = validate_memory_value(namespace.build_memory)


def _get_app_name_from_namespace(namespace):
    if hasattr(namespace, 'app'):
        return namespace.app
    elif hasattr(namespace, 'name'):
        return namespace.name
    return None


def _validate_container_registry(cmd, namespace):
    client = cf_spring(cmd.cli_ctx)
    sku = get_spring_sku(client, namespace.resource_group, namespace.service)
    if sku.name == 'E0':
        try:
            build_service = client.build_service.get_build_service(namespace.resource_group,
                                                                   namespace.service,
                                                                   DEFAULT_BUILD_SERVICE_NAME)
            if build_service.properties.container_registry:
                if namespace.source_path or namespace.artifact_path:
                    raise InvalidArgumentValueError(
                        "The instance using your own container registry can only use '--container-image' to deploy."
                        " See more details in https://learn.microsoft.com/en-us/azure/spring-apps/how-to-deploy-with-custom-container-image?tabs=azure-cli")
        except ResourceNotFoundError:
            if namespace.source_path or namespace.artifact_path:
                raise InvalidArgumentValueError(
                    "The instance without build service can only use '--container-image' to deploy."
                    " See more details in https://learn.microsoft.com/en-us/azure/spring-apps/how-to-deploy-with-custom-container-image?tabs=azure-cli")
