# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, unused-argument

from knack.log import get_logger
from urllib.parse import urlparse

from azure.cli.core.azclierror import (InvalidArgumentValueError,
                                       MutuallyExclusiveArgumentError, RequiredArgumentMissingError,
                                       ResourceNotFoundError, ValidationError, CLIError)
from azure.core.exceptions import HttpResponseError
from azure.cli.command_modules.containerapp._utils import is_registry_msi_system, safe_get
from azure.cli.command_modules.containerapp._validators import _validate_revision_exists, _validate_replica_exists, \
    _validate_container_exists
from azure.mgmt.core.tools import is_valid_resource_id
from ._constants import ACR_IMAGE_SUFFIX, \
    CONNECTED_ENVIRONMENT_TYPE, \
    EXTENDED_LOCATION_RP, CUSTOM_LOCATION_RESOURCE_TYPE, MAXIMUM_SECRET_LENGTH, CONTAINER_APPS_RP, \
    CONNECTED_ENVIRONMENT_RESOURCE_TYPE, MANAGED_ENVIRONMENT_RESOURCE_TYPE, MANAGED_ENVIRONMENT_TYPE, \
    RUNTIME_GENERIC

logger = get_logger(__name__)


# called directly from custom method bc otherwise it disrupts the --environment auto RID functionality
def validate_create(registry_identity, registry_pass, registry_user, registry_server, no_wait, revisions_mode=None, target_label=None, source=None, artifact=None, repo=None, yaml=None, environment_type=None):
    from ._utils import is_registry_msi_system_environment

    if source and repo:
        raise MutuallyExclusiveArgumentError("Usage error: --source and --repo cannot be used together. Can either deploy from a local directory or a GitHub repository")
    if (source or repo) and yaml:
        raise MutuallyExclusiveArgumentError("Usage error: --source or --repo cannot be used with --yaml together. Can either deploy from a local directory or provide a yaml file")
    if (source or repo) and environment_type == CONNECTED_ENVIRONMENT_TYPE:
        raise MutuallyExclusiveArgumentError("Usage error: --source or --repo cannot be used with --environment-type connectedEnvironment together. Please use --environment-type managedEnvironment")
    if repo:
        if not registry_server:
            raise RequiredArgumentMissingError('Usage error: --registry-server is required while using --repo')
        if ACR_IMAGE_SUFFIX not in registry_server:
            raise InvalidArgumentValueError("Usage error: --registry-server: expected an ACR registry (*.azurecr.io) for --repo")
    if repo and registry_server and "azurecr.io" in registry_server:
        parsed = urlparse(registry_server)
        registry_name = (parsed.netloc if parsed.scheme else parsed.path).split(".")[0]
        if registry_name and len(registry_name) > MAXIMUM_SECRET_LENGTH:
            raise ValidationError(f"--registry-server ACR name must be less than {MAXIMUM_SECRET_LENGTH} "
                                  "characters when using --repo")
    if registry_identity and (registry_pass or registry_user):
        raise MutuallyExclusiveArgumentError("Cannot provide both registry identity and username/password")
    if is_registry_msi_system(registry_identity) and no_wait:
        raise MutuallyExclusiveArgumentError("--no-wait is not supported with system registry identity")
    if registry_identity and not is_valid_resource_id(registry_identity) and not is_registry_msi_system(registry_identity) and not is_registry_msi_system_environment(registry_identity):
        raise InvalidArgumentValueError("--registry-identity must be an identity resource ID or 'system' or 'system-environment'")
    if registry_identity and ACR_IMAGE_SUFFIX not in (registry_server or ""):
        raise InvalidArgumentValueError("--registry-identity: expected an ACR registry (*.azurecr.io) for --registry-server")
    if target_label and (not revisions_mode or revisions_mode.lower() != 'labels'):
        raise InvalidArgumentValueError("--target-label must only be specified with --revisions-mode labels.")


def validate_runtime(runtime, enable_java_metrics, enable_java_agent):
    def is_java_enhancement_enabled():
        return enable_java_agent is not None or enable_java_metrics is not None

    if runtime is None:
        return
    if runtime.lower() == RUNTIME_GENERIC and is_java_enhancement_enabled():
        raise ValidationError("Usage error: --runtime java is required when using --enable-java-metrics or --enable-java-agent")


def validate_env_name_or_id(cmd, namespace):
    from azure.cli.core.commands.client_factory import get_subscription_id
    from azure.mgmt.core.tools import resource_id, parse_resource_id

    if not namespace.managed_env:
        return

    # Set environment type
    environment_type = None

    if namespace.__dict__.get("environment_type"):
        environment_type = namespace.environment_type

    if is_valid_resource_id(namespace.managed_env):
        env_dict = parse_resource_id(namespace.managed_env)
        resource_type = env_dict.get("resource_type")
        if resource_type:
            if CONNECTED_ENVIRONMENT_RESOURCE_TYPE.lower() == resource_type.lower():
                environment_type = CONNECTED_ENVIRONMENT_TYPE
            if MANAGED_ENVIRONMENT_RESOURCE_TYPE.lower() == resource_type.lower():
                environment_type = MANAGED_ENVIRONMENT_TYPE

    # Validate resource id / format resource id
    if environment_type == CONNECTED_ENVIRONMENT_TYPE:
        if not is_valid_resource_id(namespace.managed_env):
            namespace.managed_env = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace=CONTAINER_APPS_RP,
                type=CONNECTED_ENVIRONMENT_RESOURCE_TYPE,
                name=namespace.managed_env
            )
    else:
        if not is_valid_resource_id(namespace.managed_env):
            namespace.managed_env = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace=CONTAINER_APPS_RP,
                type=MANAGED_ENVIRONMENT_RESOURCE_TYPE,
                name=namespace.managed_env
            )


def validate_env_name_or_id_for_up(cmd, namespace):
    from azure.cli.core.commands.client_factory import get_subscription_id
    from azure.mgmt.core.tools import resource_id, parse_resource_id

    if not namespace.environment:
        return

    # Set environment type
    environment_type = None

    if is_valid_resource_id(namespace.environment):
        env_dict = parse_resource_id(namespace.environment)
        resource_type = env_dict.get("resource_type")
        if resource_type:
            if CONNECTED_ENVIRONMENT_RESOURCE_TYPE.lower() == resource_type.lower():
                environment_type = CONNECTED_ENVIRONMENT_TYPE
            if MANAGED_ENVIRONMENT_RESOURCE_TYPE.lower() == resource_type.lower():
                environment_type = MANAGED_ENVIRONMENT_TYPE

    if namespace.__dict__.get("custom_location") or namespace.__dict__.get("connected_cluster_id"):
        environment_type = CONNECTED_ENVIRONMENT_TYPE

    # Validate resource id / format resource id
    if environment_type == CONNECTED_ENVIRONMENT_TYPE:
        if not is_valid_resource_id(namespace.environment):
            namespace.environment = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace=CONTAINER_APPS_RP,
                type=CONNECTED_ENVIRONMENT_RESOURCE_TYPE,
                name=namespace.environment
            )
    elif environment_type == MANAGED_ENVIRONMENT_TYPE:
        if not is_valid_resource_id(namespace.environment):
            namespace.environment = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace=CONTAINER_APPS_RP,
                type=MANAGED_ENVIRONMENT_RESOURCE_TYPE,
                name=namespace.environment
            )


def validate_custom_location_name_or_id(cmd, namespace):
    from azure.cli.core.commands.client_factory import get_subscription_id
    from azure.mgmt.core.tools import resource_id

    if not namespace.custom_location or not namespace.resource_group_name:
        return

    if not is_valid_resource_id(namespace.custom_location):
        namespace.custom_location = resource_id(
            subscription=get_subscription_id(cmd.cli_ctx),
            resource_group=namespace.resource_group_name,
            namespace=EXTENDED_LOCATION_RP,
            type=CUSTOM_LOCATION_RESOURCE_TYPE,
            name=namespace.custom_location
        )


def validate_build_env_vars(cmd, namespace):
    env_list = namespace.build_env_vars

    if not env_list:
        return

    env_pairs = {}

    for pair in env_list:
        key_val = pair.split('=', 1)
        if len(key_val) <= 1:
            raise ValidationError("Build environment variables must be in the format \"<key>=<value>\".")
        if key_val[0] in env_pairs:
            raise ValidationError(
                "Duplicate build environment variable {env} found, environment variable names must be unique.".format(
                    env=key_val[0]))
        env_pairs[key_val[0]] = key_val[1]


def validate_otlp_headers(cmd, namespace):
    headers = namespace.headers

    if not headers:
        return

    header_pairs = {}

    for pair in headers:
        key_val = pair.split('=', 1)
        if len(key_val) != 2:
            raise ValidationError("Otlp headers must be in the format \"<key>=<value>\".")
        if key_val[0] in header_pairs:
            raise ValidationError(
                "Duplicate headers {header} found, header names must be unique.".format(
                    header=key_val[0]))
        header_pairs[key_val[0]] = key_val[1]


def validate_target_port_range(cmd, namespace):
    target_port = namespace.target_port
    if target_port is not None:
        if target_port < 1 or target_port > 65535:
            raise ValidationError("Port must be in range [1, 65535].")


def validate_session_timeout_in_seconds(cmd, namespace):
    timeout_in_seconds = namespace.timeout_in_seconds
    if timeout_in_seconds is not None:
        if timeout_in_seconds <= 0 or timeout_in_seconds > 220:
            raise ValidationError("Timeout in seconds must be in range [1, 220].")


def validate_debug(cmd, namespace):
    logger.warning("Validating...")
    revision_already_set = bool(namespace.revision)
    replica_already_set = bool(namespace.replica)
    container_already_set = bool(namespace.container)
    _set_debug_defaults(cmd, namespace)
    if revision_already_set:
        _validate_revision_exists(cmd, namespace)
    if replica_already_set:
        _validate_replica_exists(cmd, namespace)
    if container_already_set:
        _validate_container_exists(cmd, namespace)


def _set_debug_defaults(cmd, namespace):
    from ._clients import ContainerAppPreviewClient

    app = ContainerAppPreviewClient.show(cmd, namespace.resource_group_name, namespace.name)
    if not app:
        raise ResourceNotFoundError("Could not find a container app")

    from azure.mgmt.core.tools import parse_resource_id
    parsed_env = parse_resource_id(safe_get(app, "properties", "environmentId"))
    resource_type = parsed_env.get("resource_type")
    if resource_type:
        if CONNECTED_ENVIRONMENT_RESOURCE_TYPE.lower() == resource_type.lower():
            raise ValidationError(
                "The app belongs to ConnectedEnvironment, which is not support debug console. Please use the apps belong to ManagedEnvironment.")

    if not namespace.revision:
        namespace.revision = app.get("properties", {}).get("latestRevisionName")
        if not namespace.revision:
            raise ResourceNotFoundError("Could not find a revision")
    if not namespace.replica:
        replicas = ContainerAppPreviewClient.list_replicas(
            cmd=cmd,
            resource_group_name=namespace.resource_group_name,
            container_app_name=namespace.name,
            revision_name=namespace.revision
        )
        if not replicas:
            raise ResourceNotFoundError("Could not find an active replica")
        namespace.replica = replicas[0]["name"]
        if not namespace.container and replicas[0]["properties"]["containers"]:
            namespace.container = replicas[0]["properties"]["containers"][0]["name"]
    if not namespace.container:
        revision = ContainerAppPreviewClient.show_revision(
            cmd,
            resource_group_name=namespace.resource_group_name,
            container_app_name=namespace.name,
            name=namespace.revision
        )
        revision_containers = safe_get(revision, "properties", "template", "containers")
        if revision_containers:
            namespace.container = revision_containers[0]["name"]


def validate_container_app_exists(cmd, resource_group_name, container_app_name):
    from ._client_factory import handle_raw_exception
    from ._clients import ContainerAppPreviewClient

    try:
        logger.debug("Attempting to retrieve container app '%s'", container_app_name)
        containerapp_def = ContainerAppPreviewClient.show(
            cmd=cmd,
            resource_group_name=resource_group_name,
            name=container_app_name
        )
        logger.debug("Successfully retrieved container app definition for '%s'", container_app_name)
    except HttpResponseError as e:
        logger.debug("Failed to retrieve container app '%s': %s", container_app_name, str(e))
        handle_raw_exception(e)

    if not containerapp_def:
        logger.debug("Container app '%s' not found in resource group '%s'", container_app_name, resource_group_name)
        raise CLIError(f"The containerapp '{container_app_name}' does not exist in resource group '{resource_group_name}'.")

    return containerapp_def


def validate_revision_and_get_name(cmd, resource_group_name, container_app_name, provided_revision_name=None):

    logger.debug("Validating revision for container app: name='%s', resource_group='%s', provided_revision='%s'", container_app_name, resource_group_name, provided_revision_name)

    containerapp_def = validate_container_app_exists(
        cmd=cmd,
        resource_group_name=resource_group_name,
        container_app_name=container_app_name)

    active_revision_mode = safe_get(containerapp_def, "properties", "configuration", "activeRevisionsMode", default="single")
    logger.debug("Container app revision mode: '%s'", active_revision_mode)

    if active_revision_mode.lower() != "single":
        if not provided_revision_name:
            logger.debug("No revision name provided for multiple revision mode container app")
            raise ValidationError("Revision name is required when active revision mode is not 'single'.")
        return provided_revision_name, active_revision_mode
    if not provided_revision_name:
        logger.debug("No revision name provided - attempting to determine latest revision")
        revision_name = safe_get(containerapp_def, "properties", "latestRevisionName")
        logger.debug("Latest revision name from properties: '%s'", revision_name)

        if not revision_name:
            revision_name = safe_get(containerapp_def, "properties", "latestReadyRevisionName")
            logger.debug("Latest ready revision name: '%s'", revision_name)

        if not revision_name or revision_name is None:
            logger.debug("Could not determine any revision name from container app properties")
            raise ValidationError("Could not determine the latest revision name. Please provide --revision.")
        return revision_name, active_revision_mode
    logger.debug("Using provided revision name: '%s'", provided_revision_name)
    return provided_revision_name, active_revision_mode


def validate_functionapp_kind(cmd, resource_group_name, container_app_name):

    containerapp_def = validate_container_app_exists(
        cmd=cmd,
        resource_group_name=resource_group_name,
        container_app_name=container_app_name
    )

    kind = safe_get(containerapp_def, "kind")

    if kind and kind.lower() == "functionapp":
        logger.debug("Container app '%s' validated as Azure Function App", container_app_name)
        return

    logger.debug("Container app '%s' is not a function app - validation failed", container_app_name)
    raise ValidationError(
        f"The containerapp '{container_app_name}' is not an Azure Functions on Container App."
    )


def validate_basic_arguments(resource_group_name, container_app_name, **kwargs):
    if not resource_group_name:
        logger.debug("Resource group name validation failed - empty or None")
        raise ValidationError("Resource group name is required.")

    if not container_app_name:
        logger.debug("Container app name validation failed - empty or None")
        raise ValidationError("Container app name is required.")

    # Validate additional arguments
    for arg_name, arg_value in kwargs.items():
        if not arg_value:
            logger.debug("Additional argument validation failed: '%s' is empty or None", arg_name)
            raise ValidationError(f"{arg_name.replace('_', ' ').title()} is required.")
