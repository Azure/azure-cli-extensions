# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, consider-using-f-string, logging-format-interpolation, inconsistent-return-statements, broad-except, bare-except, too-many-statements, too-many-locals, too-many-boolean-expressions, too-many-branches, too-many-nested-blocks, pointless-statement, expression-not-assigned, unbalanced-tuple-unpacking, unsupported-assignment-operation

import sys
import time
from urllib.parse import urlparse
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor

from azure.cli.core import telemetry as telemetry_core
from azure.cli.command_modules.containerapp._utils import safe_set, safe_get

from azure.cli.core.azclierror import (
    RequiredArgumentMissingError,
    ResourceNotFoundError,
    ValidationError,
    CLIError,
    CLIInternalError,
    InvalidArgumentValueError,
    ResourceNotFoundError)
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.command_modules.containerapp.custom import set_secrets, open_containerapp_in_browser, create_deserializer
from azure.cli.command_modules.containerapp.containerapp_job_decorator import ContainerAppJobDecorator
from azure.cli.command_modules.containerapp.containerapp_decorator import BaseContainerAppDecorator
from azure.cli.command_modules.containerapp.containerapp_env_decorator import ContainerAppEnvUpdateDecorator, ContainerAppEnvDecorator
from azure.cli.command_modules.containerapp._decorator_utils import load_yaml_file
from azure.cli.command_modules.containerapp._github_oauth import get_github_access_token
from azure.cli.command_modules.containerapp._utils import (_validate_subscription_registered,
                                                           _convert_object_from_snake_to_camel_case,
                                                           _object_to_dict, _remove_additional_attributes,
                                                           raise_missing_token_suggestion,
                                                           _remove_dapr_readonly_attributes,
                                                           _get_acr_cred, safe_get, await_github_action, repo_url_to_name,
                                                           validate_container_app_name, register_provider_if_needed,
                                                           generate_randomized_cert_name, load_cert_file,
                                                           generate_randomized_managed_cert_name,
                                                           check_managed_cert_name_availability, prepare_managed_certificate_envelop,
                                                           trigger_workflow, _ensure_identity_resource_id,
                                                           AppType)

from knack.log import get_logger
from knack.prompting import prompt_y_n

from msrestazure.tools import parse_resource_id, is_valid_resource_id
from msrest.exceptions import DeserializationError

from .containerapp_env_certificate_decorator import ContainerappPreviewEnvCertificateListDecorator, \
    ContainerappEnvCertificatePreviweUploadDecorator
from .connected_env_decorator import ConnectedEnvironmentDecorator, ConnectedEnvironmentCreateDecorator
from .containerapp_job_decorator import ContainerAppJobPreviewCreateDecorator
from .containerapp_env_decorator import ContainerappEnvPreviewCreateDecorator, ContainerappEnvPreviewUpdateDecorator
from .containerapp_resiliency_decorator import (
    ContainerAppResiliencyPreviewCreateDecorator,
    ContainerAppResiliencyPreviewShowDecorator,
    ContainerAppResiliencyPreviewDeleteDecorator,
    ContainerAppResiliencyPreviewListDecorator,
    ContainerAppResiliencyPreviewUpdateDecorator)
from .daprcomponent_resiliency_decorator import (
    DaprComponentResiliencyPreviewCreateDecorator,
    DaprComponentResiliencyPreviewDeleteDecorator,
    DaprComponentResiliencyPreviewShowDecorator,
    DaprComponentResiliencyPreviewListDecorator,
    DaprComponentResiliencyPreviewUpdateDecorator
)
from .containerapp_env_telemetry_decorator import (
    ContainerappEnvTelemetryDataDogPreviewSetDecorator,
    ContainerappEnvTelemetryAppInsightsPreviewSetDecorator,
    ContainerappEnvTelemetryOtlpPreviewSetDecorator,
    APP_INSIGHTS_DEST,
    DATA_DOG_DEST
)
from .containerapp_auth_decorator import ContainerAppPreviewAuthDecorator
from .containerapp_decorator import ContainerAppPreviewCreateDecorator, ContainerAppPreviewListDecorator, ContainerAppPreviewUpdateDecorator
from .containerapp_env_storage_decorator import ContainerappEnvStorageDecorator
from .java_component_decorator import JavaComponentDecorator
from ._client_factory import handle_raw_exception, handle_non_404_status_code_exception
from ._clients import (
    GitHubActionPreviewClient,
    ContainerAppPreviewClient,
    AuthPreviewClient,
    SubscriptionPreviewClient,
    StoragePreviewClient,
    ContainerAppsJobPreviewClient,
    ContainerAppsResiliencyPreviewClient,
    DaprComponentResiliencyPreviewClient,
    ManagedEnvironmentPreviewClient,
    ConnectedEnvDaprComponentClient,
    ConnectedEnvironmentClient,
    ConnectedEnvStorageClient,
    ConnectedEnvCertificateClient,
    JavaComponentPreviewClient
)
from ._dev_service_utils import DevServiceUtils
from ._models import (
    GitHubActionConfiguration,
    RegistryInfo as RegistryInfoModel,
    AzureCredentials as AzureCredentialsModel,
    SourceControl as SourceControlModel,
    ContainerAppCertificateEnvelope as ContainerAppCertificateEnvelopeModel,
    AzureFileProperties as AzureFilePropertiesModel
)

from ._utils import connected_env_check_cert_name_availability, get_oryx_run_image_tags, patchable_check, get_pack_exec_path, is_docker_running, parse_build_env_vars

from ._constants import (CONTAINER_APPS_RP,
                         NAME_INVALID, NAME_ALREADY_EXISTS, ACR_IMAGE_SUFFIX, DEV_POSTGRES_IMAGE, DEV_POSTGRES_SERVICE_TYPE,
                         DEV_POSTGRES_CONTAINER_NAME, DEV_REDIS_IMAGE, DEV_REDIS_SERVICE_TYPE, DEV_REDIS_CONTAINER_NAME, DEV_KAFKA_CONTAINER_NAME,
                         DEV_KAFKA_IMAGE, DEV_KAFKA_SERVICE_TYPE, DEV_MARIADB_CONTAINER_NAME, DEV_MARIADB_IMAGE, DEV_MARIADB_SERVICE_TYPE, DEV_QDRANT_IMAGE,
                         DEV_QDRANT_CONTAINER_NAME, DEV_QDRANT_SERVICE_TYPE, DEV_WEAVIATE_IMAGE, DEV_WEAVIATE_CONTAINER_NAME, DEV_WEAVIATE_SERVICE_TYPE,
                         DEV_MILVUS_IMAGE, DEV_MILVUS_CONTAINER_NAME, DEV_MILVUS_SERVICE_TYPE, DEV_SERVICE_LIST, CONTAINER_APPS_SDK_MODELS, BLOB_STORAGE_TOKEN_STORE_SECRET_SETTING_NAME,
                         DAPR_SUPPORTED_STATESTORE_DEV_SERVICE_LIST, DAPR_SUPPORTED_PUBSUB_DEV_SERVICE_LIST, AZURE_FILE_STORAGE_TYPE, NFS_AZURE_FILE_STORAGE_TYPE,
                         JAVA_COMPONENT_CONFIG, JAVA_COMPONENT_EUREKA)


logger = get_logger(__name__)

def list_all_services(cmd, environment_name, resource_group_name):
    services = list_containerapp(cmd, resource_group_name=resource_group_name, managed_env=environment_name)
    dev_service_list = []

    for service in services:
        service_type = safe_get(service, "properties", "configuration", "service", "type", default="")
        if service_type in DEV_SERVICE_LIST:
            dev_service_list.append(service)

    return dev_service_list


def create_redis_service(cmd, service_name, environment_name, resource_group_name, no_wait=False,
                         disable_warnings=True):
    return DevServiceUtils.create_service(cmd, service_name, environment_name, resource_group_name, no_wait,
                                          disable_warnings, DEV_REDIS_IMAGE, DEV_REDIS_SERVICE_TYPE,
                                          DEV_REDIS_CONTAINER_NAME)


def delete_redis_service(cmd, service_name, resource_group_name, no_wait=False):
    return DevServiceUtils.delete_service(cmd, service_name, resource_group_name, no_wait, DEV_REDIS_SERVICE_TYPE)


def create_postgres_service(cmd, service_name, environment_name, resource_group_name, no_wait=False,
                            disable_warnings=True):
    return DevServiceUtils.create_service(cmd, service_name, environment_name, resource_group_name, no_wait,
                                          disable_warnings, DEV_POSTGRES_IMAGE, DEV_POSTGRES_SERVICE_TYPE,
                                          DEV_POSTGRES_CONTAINER_NAME)


def delete_postgres_service(cmd, service_name, resource_group_name, no_wait=False):
    return DevServiceUtils.delete_service(cmd, service_name, resource_group_name, no_wait, DEV_POSTGRES_SERVICE_TYPE)


def create_kafka_service(cmd, service_name, environment_name, resource_group_name, no_wait=False,
                         disable_warnings=True):
    return DevServiceUtils.create_service(cmd, service_name, environment_name, resource_group_name, no_wait,
                                          disable_warnings, DEV_KAFKA_IMAGE, DEV_KAFKA_SERVICE_TYPE,
                                          DEV_KAFKA_CONTAINER_NAME)


def delete_kafka_service(cmd, service_name, resource_group_name, no_wait=False):
    return DevServiceUtils.delete_service(cmd, service_name, resource_group_name, no_wait, DEV_KAFKA_SERVICE_TYPE)


def create_mariadb_service(cmd, service_name, environment_name, resource_group_name, no_wait=False,
                           disable_warnings=True):
    return DevServiceUtils.create_service(cmd, service_name, environment_name, resource_group_name, no_wait,
                                          disable_warnings, DEV_MARIADB_IMAGE, DEV_MARIADB_SERVICE_TYPE,
                                          DEV_MARIADB_CONTAINER_NAME)


def delete_mariadb_service(cmd, service_name, resource_group_name, no_wait=False):
    return DevServiceUtils.delete_service(cmd, service_name, resource_group_name, no_wait, DEV_MARIADB_SERVICE_TYPE)


def create_qdrant_service(cmd, service_name, environment_name, resource_group_name, no_wait=False,
                          disable_warnings=True):
    return DevServiceUtils.create_service(cmd, service_name, environment_name, resource_group_name, no_wait,
                                          disable_warnings, DEV_QDRANT_IMAGE, DEV_QDRANT_SERVICE_TYPE,
                                          DEV_QDRANT_CONTAINER_NAME)


def delete_qdrant_service(cmd, service_name, resource_group_name, no_wait=False):
    return DevServiceUtils.delete_service(cmd, service_name, resource_group_name, no_wait, DEV_QDRANT_SERVICE_TYPE)


def create_weaviate_service(cmd, service_name, environment_name, resource_group_name, no_wait=False,
                            disable_warnings=True):
    return DevServiceUtils.create_service(cmd, service_name, environment_name, resource_group_name, no_wait,
                                          disable_warnings, DEV_WEAVIATE_IMAGE, DEV_WEAVIATE_SERVICE_TYPE,
                                          DEV_WEAVIATE_CONTAINER_NAME)


def delete_weaviate_service(cmd, service_name, resource_group_name, no_wait=False):
    return DevServiceUtils.delete_service(cmd, service_name, resource_group_name, no_wait, DEV_WEAVIATE_SERVICE_TYPE)


def create_milvus_service(cmd, service_name, environment_name, resource_group_name, no_wait=False,
                          disable_warnings=True):
    return DevServiceUtils.create_service(cmd, service_name, environment_name, resource_group_name, no_wait,
                                          disable_warnings, DEV_MILVUS_IMAGE, DEV_MILVUS_SERVICE_TYPE,
                                          DEV_MILVUS_CONTAINER_NAME)


def delete_milvus_service(cmd, service_name, resource_group_name, no_wait=False):
    return DevServiceUtils.delete_service(cmd, service_name, resource_group_name, no_wait, DEV_MILVUS_SERVICE_TYPE)


def create_container_app_resiliency(cmd, name, resource_group_name, container_app_name,
                                    yaml=None,
                                    no_wait=False,
                                    disable_warnings=False,
                                    tcp_retry_max_connect_attempts=None,
                                    circuit_breaker_consecutive_errors=None,
                                    circuit_breaker_interval=None,
                                    circuit_breaker_max_ejection=None,
                                    tcp_connection_pool_max_connections=None,
                                    http_connection_pool_http1_max_pending_req=None,
                                    http_connection_pool_http2_max_req=None,
                                    timeout_response_in_seconds=None,
                                    timeout_connection_in_seconds=None,
                                    http_retry_max=None,
                                    http_retry_delay_in_milliseconds=None,
                                    http_retry_interval_in_milliseconds=None,
                                    http_retry_status_codes=None,
                                    http_retry_errors=None,
                                    default=False):
    raw_parameters = locals()
    containerapp_resiliency_create_decorator = ContainerAppResiliencyPreviewCreateDecorator(
        cmd=cmd,
        client=ContainerAppsResiliencyPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_resiliency_create_decorator.validate_arguments()
    containerapp_resiliency_create_decorator.construct_payload()
    return containerapp_resiliency_create_decorator.create()


def update_container_app_resiliency(cmd, name, resource_group_name, container_app_name,
                                    yaml=None,
                                    no_wait=False,
                                    disable_warnings=False,
                                    tcp_retry_max_connect_attempts=None,
                                    circuit_breaker_consecutive_errors=None,
                                    circuit_breaker_interval=None,
                                    circuit_breaker_max_ejection=None,
                                    tcp_connection_pool_max_connections=None,
                                    http_connection_pool_http1_max_pending_req=None,
                                    http_connection_pool_http2_max_req=None,
                                    timeout_response_in_seconds=None,
                                    timeout_connection_in_seconds=None,
                                    http_retry_max=None,
                                    http_retry_delay_in_milliseconds=None,
                                    http_retry_interval_in_milliseconds=None,
                                    http_retry_status_codes=None,
                                    http_retry_errors=None):

    raw_parameters = locals()
    containerapp_resiliency_update_decorator = ContainerAppResiliencyPreviewUpdateDecorator(
        cmd=cmd,
        client=ContainerAppsResiliencyPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_resiliency_update_decorator.validate_arguments()
    containerapp_resiliency_update_decorator.construct_payload()
    return containerapp_resiliency_update_decorator.update()


def delete_container_app_resiliency(cmd, name, resource_group_name, container_app_name, no_wait=False):

    raw_parameters = locals()
    containerapp_resiliency_delete_decorator = ContainerAppResiliencyPreviewDeleteDecorator(
        cmd=cmd,
        client=ContainerAppsResiliencyPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )

    return containerapp_resiliency_delete_decorator.delete()


def show_container_app_resiliency(cmd, name, resource_group_name, container_app_name):

    raw_parameters = locals()
    containerapp_resiliency_show_decorator = ContainerAppResiliencyPreviewShowDecorator(
        cmd=cmd,
        client=ContainerAppsResiliencyPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )

    return containerapp_resiliency_show_decorator.show()


def list_container_app_resiliencies(cmd, resource_group_name, container_app_name):

    raw_parameters = locals()
    containerapp_resiliency_list_decorator = ContainerAppResiliencyPreviewListDecorator(
        cmd=cmd,
        client=ContainerAppsResiliencyPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )

    return containerapp_resiliency_list_decorator.list()


def create_dapr_component_resiliency(cmd, name, resource_group_name, dapr_component_name, environment,
                                     yaml=None,
                                     no_wait=False,
                                     disable_warnings=False,
                                     in_timeout_response_in_seconds=None,
                                     out_timeout_response_in_seconds=None,
                                     in_http_retry_max=None,
                                     out_http_retry_max=None,
                                     in_http_retry_delay_in_milliseconds=None,
                                     out_http_retry_delay_in_milliseconds=None,
                                     in_http_retry_interval_in_milliseconds=None,
                                     out_http_retry_interval_in_milliseconds=None,
                                     in_circuit_breaker_consecutive_errors=None,
                                     out_circuit_breaker_consecutive_errors=None,
                                     in_circuit_breaker_interval=None,
                                     out_circuit_breaker_interval=None,
                                     in_circuit_breaker_timeout=None,
                                     out_circuit_breaker_timeout=None):
    raw_parameters = locals()
    component_resiliency_create_decorator = DaprComponentResiliencyPreviewCreateDecorator(
        cmd=cmd,
        client=DaprComponentResiliencyPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    component_resiliency_create_decorator.validate_arguments()
    component_resiliency_create_decorator.construct_payload()
    return component_resiliency_create_decorator.create()


def update_dapr_component_resiliency(cmd, name, resource_group_name, dapr_component_name, environment,
                                     yaml=None,
                                     no_wait=False,
                                     disable_warnings=False,
                                     in_timeout_response_in_seconds=None,
                                     out_timeout_response_in_seconds=None,
                                     in_http_retry_max=None,
                                     out_http_retry_max=None,
                                     in_http_retry_delay_in_milliseconds=None,
                                     out_http_retry_delay_in_milliseconds=None,
                                     in_http_retry_interval_in_milliseconds=None,
                                     out_http_retry_interval_in_milliseconds=None,
                                     in_circuit_breaker_consecutive_errors=None,
                                     out_circuit_breaker_consecutive_errors=None,
                                     in_circuit_breaker_interval=None,
                                     out_circuit_breaker_interval=None,
                                     in_circuit_breaker_timeout=None,
                                     out_circuit_breaker_timeout=None):

    raw_parameters = locals()
    component_resiliency_update_decorator = DaprComponentResiliencyPreviewUpdateDecorator(
        cmd=cmd,
        client=DaprComponentResiliencyPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    component_resiliency_update_decorator.validate_arguments()
    component_resiliency_update_decorator.construct_payload()
    return component_resiliency_update_decorator.update()


def delete_dapr_component_resiliency(cmd, name, resource_group_name, environment, dapr_component_name, no_wait=False):

    raw_parameters = locals()
    containerapp_resiliency_delete_decorator = DaprComponentResiliencyPreviewDeleteDecorator(
        cmd=cmd,
        client=DaprComponentResiliencyPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )

    return containerapp_resiliency_delete_decorator.delete()


def show_dapr_component_resiliency(cmd, name, resource_group_name, environment, dapr_component_name, no_wait=False):

    raw_parameters = locals()
    containerapp_resiliency_show_decorator = DaprComponentResiliencyPreviewShowDecorator(
        cmd=cmd,
        client=DaprComponentResiliencyPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )

    return containerapp_resiliency_show_decorator.show()


def list_dapr_component_resiliencies(cmd, resource_group_name, dapr_component_name, environment, no_wait=False):

    raw_parameters = locals()
    containerapp_resiliency_list_decorator = DaprComponentResiliencyPreviewListDecorator(
        cmd=cmd,
        client=DaprComponentResiliencyPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )

    return containerapp_resiliency_list_decorator.list()


def create_containerapp(cmd,
                        name,
                        resource_group_name,
                        yaml=None,
                        image=None,
                        container_name=None,
                        managed_env=None,
                        min_replicas=None,
                        max_replicas=None,
                        scale_rule_name=None,
                        scale_rule_type=None,
                        scale_rule_http_concurrency=None,
                        scale_rule_metadata=None,
                        scale_rule_auth=None,
                        target_port=None,
                        exposed_port=None,
                        transport="auto",
                        ingress=None,
                        allow_insecure=False,
                        revisions_mode="single",
                        secrets=None,
                        env_vars=None,
                        cpu=None,
                        memory=None,
                        registry_server=None,
                        registry_user=None,
                        registry_pass=None,
                        dapr_enabled=False,
                        dapr_app_port=None,
                        dapr_app_id=None,
                        dapr_app_protocol=None,
                        dapr_http_read_buffer_size=None,
                        dapr_http_max_request_size=None,
                        dapr_log_level=None,
                        dapr_enable_api_logging=False,
                        service_type=None,
                        service_bindings=None,
                        customized_keys=None,
                        revision_suffix=None,
                        startup_command=None,
                        args=None,
                        tags=None,
                        no_wait=False,
                        system_assigned=False,
                        disable_warnings=False,
                        user_assigned=None,
                        registry_identity=None,
                        workload_profile_name=None,
                        termination_grace_period=None,
                        secret_volume_mount=None,
                        environment_type="managed",
                        source=None,
                        artifact=None,
                        build_env_vars=None,
                        repo=None,
                        token=None,
                        branch=None,
                        context_path=None,
                        service_principal_client_id=None,
                        service_principal_client_secret=None,
                        service_principal_tenant_id=None,
                        max_inactive_revisions=None):
    raw_parameters = locals()

    containerapp_create_decorator = ContainerAppPreviewCreateDecorator(
        cmd=cmd,
        client=ContainerAppPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_create_decorator.register_provider(CONTAINER_APPS_RP)
    containerapp_create_decorator.validate_arguments()

    containerapp_create_decorator.construct_payload()
    r = containerapp_create_decorator.create()
    containerapp_create_decorator.construct_for_post_process(r)
    r = containerapp_create_decorator.post_process(r)
    return r


def update_containerapp_logic(cmd,
                              name,
                              resource_group_name,
                              yaml=None,
                              image=None,
                              container_name=None,
                              min_replicas=None,
                              max_replicas=None,
                              scale_rule_name=None,
                              scale_rule_type="http",
                              scale_rule_http_concurrency=None,
                              scale_rule_metadata=None,
                              scale_rule_auth=None,
                              service_bindings=None,
                              customized_keys=None,
                              unbind_service_bindings=None,
                              set_env_vars=None,
                              remove_env_vars=None,
                              replace_env_vars=None,
                              remove_all_env_vars=False,
                              cpu=None,
                              memory=None,
                              revision_suffix=None,
                              startup_command=None,
                              args=None,
                              tags=None,
                              no_wait=False,
                              from_revision=None,
                              ingress=None,
                              target_port=None,
                              workload_profile_name=None,
                              termination_grace_period=None,
                              registry_server=None,
                              registry_user=None,
                              registry_pass=None,
                              secret_volume_mount=None,
                              source=None,
                              artifact=None,
                              build_env_vars=None,
                              max_inactive_revisions=None,
                              force_single_container_updates=False):
    raw_parameters = locals()

    containerapp_update_decorator = ContainerAppPreviewUpdateDecorator(
        cmd=cmd,
        client=ContainerAppPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_update_decorator.register_provider(CONTAINER_APPS_RP)
    containerapp_update_decorator.validate_arguments()

    containerapp_update_decorator.construct_payload()
    r = containerapp_update_decorator.update()
    r = containerapp_update_decorator.post_process(r)
    return r


def update_containerapp(cmd,
                        name,
                        resource_group_name,
                        yaml=None,
                        image=None,
                        container_name=None,
                        min_replicas=None,
                        max_replicas=None,
                        scale_rule_name=None,
                        scale_rule_type=None,
                        scale_rule_http_concurrency=None,
                        scale_rule_metadata=None,
                        scale_rule_auth=None,
                        unbind_service_bindings=None,
                        service_bindings=None,
                        customized_keys=None,
                        set_env_vars=None,
                        remove_env_vars=None,
                        replace_env_vars=None,
                        remove_all_env_vars=False,
                        cpu=None,
                        memory=None,
                        revision_suffix=None,
                        startup_command=None,
                        args=None,
                        tags=None,
                        workload_profile_name=None,
                        termination_grace_period=None,
                        no_wait=False,
                        secret_volume_mount=None,
                        source=None,
                        artifact=None,
                        build_env_vars=None,
                        max_inactive_revisions=None):
    _validate_subscription_registered(cmd, CONTAINER_APPS_RP)

    return update_containerapp_logic(cmd=cmd,
                                     name=name,
                                     resource_group_name=resource_group_name,
                                     yaml=yaml,
                                     image=image,
                                     container_name=container_name,
                                     min_replicas=min_replicas,
                                     max_replicas=max_replicas,
                                     scale_rule_name=scale_rule_name,
                                     scale_rule_type=scale_rule_type,
                                     scale_rule_http_concurrency=scale_rule_http_concurrency,
                                     scale_rule_metadata=scale_rule_metadata,
                                     scale_rule_auth=scale_rule_auth,
                                     service_bindings=service_bindings,
                                     customized_keys=customized_keys,
                                     unbind_service_bindings=unbind_service_bindings,
                                     set_env_vars=set_env_vars,
                                     remove_env_vars=remove_env_vars,
                                     replace_env_vars=replace_env_vars,
                                     remove_all_env_vars=remove_all_env_vars,
                                     cpu=cpu,
                                     memory=memory,
                                     revision_suffix=revision_suffix,
                                     startup_command=startup_command,
                                     args=args,
                                     tags=tags,
                                     workload_profile_name=workload_profile_name,
                                     termination_grace_period=termination_grace_period,
                                     no_wait=no_wait,
                                     secret_volume_mount=secret_volume_mount,
                                     source=source,
                                     artifact=artifact,
                                     build_env_vars=build_env_vars,
                                     max_inactive_revisions=max_inactive_revisions)


def show_containerapp(cmd, name, resource_group_name, show_secrets=False):
    raw_parameters = locals()
    containerapp_base_decorator = BaseContainerAppDecorator(
        cmd=cmd,
        client=ContainerAppPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_base_decorator.validate_subscription_registered(CONTAINER_APPS_RP)

    return containerapp_base_decorator.show()


def list_containerapp(cmd, resource_group_name=None, managed_env=None, environment_type="all"):
    raw_parameters = locals()
    containerapp_list_decorator = ContainerAppPreviewListDecorator(
        cmd=cmd,
        client=ContainerAppPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_list_decorator.validate_subscription_registered(CONTAINER_APPS_RP)

    return containerapp_list_decorator.list()


def show_custom_domain_verification_id(cmd):
    _validate_subscription_registered(cmd, CONTAINER_APPS_RP)
    try:
        r = SubscriptionPreviewClient.show_custom_domain_verification_id(cmd)
        return r
    except CLIError as e:
        handle_raw_exception(e)


def list_usages(cmd, location):
    _validate_subscription_registered(cmd, CONTAINER_APPS_RP)
    try:
        r = SubscriptionPreviewClient.list_usages(cmd, location)
        return r
    except CLIError as e:
        handle_raw_exception(e)


def list_environment_usages(cmd, resource_group_name, name):
    _validate_subscription_registered(cmd, CONTAINER_APPS_RP)
    try:
        r = ManagedEnvironmentPreviewClient.list_usages(cmd, resource_group_name, name)
        return r
    except CLIError as e:
        handle_raw_exception(e)


def delete_containerapp(cmd, name, resource_group_name, no_wait=False):
    raw_parameters = locals()
    containerapp_base_decorator = BaseContainerAppDecorator(
        cmd=cmd,
        client=ContainerAppPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_base_decorator.validate_subscription_registered(CONTAINER_APPS_RP)

    return containerapp_base_decorator.delete()


def create_managed_environment(cmd,
                               name,
                               resource_group_name,
                               logs_destination="log-analytics",
                               storage_account=None,
                               logs_customer_id=None,
                               logs_key=None,
                               location=None,
                               instrumentation_key=None,
                               infrastructure_subnet_resource_id=None,
                               infrastructure_resource_group=None,
                               docker_bridge_cidr=None,
                               platform_reserved_cidr=None,
                               platform_reserved_dns_ip=None,
                               internal_only=False,
                               tags=None,
                               disable_warnings=False,
                               zone_redundant=False,
                               hostname=None,
                               certificate_file=None,
                               certificate_password=None,
                               certificate_identity = None,
                               certificate_key_vault_url=None,
                               enable_workload_profiles=True,
                               mtls_enabled=None,
                               enable_dedicated_gpu=False,
                               no_wait=False,
                               logs_dynamic_json_columns=False,
                               system_assigned=False,
                               user_assigned=None):
    raw_parameters = locals()
    containerapp_env_create_decorator = ContainerappEnvPreviewCreateDecorator(
        cmd=cmd,
        client=ManagedEnvironmentPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_env_create_decorator.validate_arguments()
    containerapp_env_create_decorator.register_provider(CONTAINER_APPS_RP)

    containerapp_env_create_decorator.construct_payload()
    r = containerapp_env_create_decorator.create()
    r = containerapp_env_create_decorator.post_process(r)

    return r


def update_managed_environment(cmd,
                               name,
                               resource_group_name,
                               logs_destination=None,
                               storage_account=None,
                               logs_customer_id=None,
                               logs_key=None,
                               hostname=None,
                               certificate_file=None,
                               certificate_password=None,
                               certificate_identity = None,
                               certificate_key_vault_url=None,
                               tags=None,
                               workload_profile_type=None,
                               workload_profile_name=None,
                               min_nodes=None,
                               max_nodes=None,
                               mtls_enabled=None,
                               no_wait=False,
                               logs_dynamic_json_columns=None):
    raw_parameters = locals()
    containerapp_env_update_decorator = ContainerappEnvPreviewUpdateDecorator(
        cmd=cmd,
        client=ManagedEnvironmentPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_env_update_decorator.validate_arguments()
    containerapp_env_update_decorator.construct_payload()
    r = containerapp_env_update_decorator.update()
    r = containerapp_env_update_decorator.post_process(r)

    return r


def show_managed_environment(cmd, name, resource_group_name):
    raw_parameters = locals()
    containerapp_env_decorator = ContainerAppEnvDecorator(
        cmd=cmd,
        client=ManagedEnvironmentPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_env_decorator.validate_subscription_registered(CONTAINER_APPS_RP)

    return containerapp_env_decorator.show()


def list_managed_environments(cmd, resource_group_name=None):
    raw_parameters = locals()
    containerapp_env_decorator = ContainerAppEnvDecorator(
        cmd=cmd,
        client=ManagedEnvironmentPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_env_decorator.validate_subscription_registered(CONTAINER_APPS_RP)

    return containerapp_env_decorator.list()


def delete_managed_environment(cmd, name, resource_group_name, no_wait=False):
    raw_parameters = locals()
    containerapp_env_decorator = ContainerAppEnvDecorator(
        cmd=cmd,
        client=ManagedEnvironmentPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_env_decorator.validate_subscription_registered(CONTAINER_APPS_RP)

    return containerapp_env_decorator.delete()


def show_storage(cmd, name, storage_name, resource_group_name):
    _validate_subscription_registered(cmd, CONTAINER_APPS_RP)

    raw_parameters = locals()
    containerapp_env_storage_decorator = ContainerappEnvStorageDecorator(
        cmd=cmd,
        client=StoragePreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )

    return containerapp_env_storage_decorator.show()


def list_storage(cmd, name, resource_group_name):
    _validate_subscription_registered(cmd, CONTAINER_APPS_RP)

    raw_parameters = locals()
    containerapp_env_storage_decorator = ContainerappEnvStorageDecorator(
        cmd=cmd,
        client=StoragePreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )

    return containerapp_env_storage_decorator.list()


def create_or_update_storage(cmd, storage_name, resource_group_name, name, storage_type=None,
                             azure_file_account_name=None, azure_file_share_name=None, azure_file_account_key=None,
                             server=None, access_mode=None, no_wait=False):  # pylint: disable=redefined-builtin
    _validate_subscription_registered(cmd, CONTAINER_APPS_RP)

    raw_parameters = locals()
    containerapp_env_storage_decorator = ContainerappEnvStorageDecorator(
        cmd=cmd,
        client=StoragePreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_env_storage_decorator.register_provider(CONTAINER_APPS_RP)
    containerapp_env_storage_decorator.validate_arguments()
    containerapp_env_storage_decorator.construct_payload()
    return containerapp_env_storage_decorator.create_or_update()


def remove_storage(cmd, storage_name, name, resource_group_name):
    _validate_subscription_registered(cmd, CONTAINER_APPS_RP)

    raw_parameters = locals()
    containerapp_env_storage_decorator = ContainerappEnvStorageDecorator(
        cmd=cmd,
        client=StoragePreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )

    return containerapp_env_storage_decorator.delete()


def create_containerappsjob(cmd,
                            name,
                            resource_group_name,
                            yaml=None,
                            image=None,
                            container_name=None,
                            managed_env=None,
                            trigger_type=None,
                            replica_timeout=1800,
                            replica_retry_limit=0,
                            replica_completion_count=1,
                            parallelism=1,
                            cron_expression=None,
                            secrets=None,
                            env_vars=None,
                            cpu=None,
                            memory=None,
                            registry_server=None,
                            registry_user=None,
                            registry_pass=None,
                            startup_command=None,
                            args=None,
                            scale_rule_metadata=None,
                            scale_rule_name=None,
                            scale_rule_type=None,
                            scale_rule_auth=None,
                            polling_interval=30,
                            min_executions=0,
                            max_executions=10,
                            tags=None,
                            no_wait=False,
                            system_assigned=False,
                            disable_warnings=False,
                            user_assigned=None,
                            registry_identity=None,
                            workload_profile_name=None,
                            environment_type="managed"):
    raw_parameters = locals()
    containerapp_job_create_decorator = ContainerAppJobPreviewCreateDecorator(
        cmd=cmd,
        client=ContainerAppsJobPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_job_create_decorator.register_provider(CONTAINER_APPS_RP)
    containerapp_job_create_decorator.validate_arguments()

    containerapp_job_create_decorator.construct_payload()
    r = containerapp_job_create_decorator.create()
    containerapp_job_create_decorator.construct_for_post_process(r)
    r = containerapp_job_create_decorator.post_process(r)

    return r


def show_containerappsjob(cmd, name, resource_group_name):
    raw_parameters = locals()
    containerapp_job_decorator = ContainerAppJobDecorator(
        cmd=cmd,
        client=ContainerAppsJobPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_job_decorator.validate_subscription_registered(CONTAINER_APPS_RP)

    return containerapp_job_decorator.show()


def list_containerappsjob(cmd, resource_group_name=None):
    raw_parameters = locals()
    containerapp_job_decorator = ContainerAppJobDecorator(
        cmd=cmd,
        client=ContainerAppsJobPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_job_decorator.validate_subscription_registered(CONTAINER_APPS_RP)

    return containerapp_job_decorator.list()


def delete_containerappsjob(cmd, name, resource_group_name, no_wait=False):
    raw_parameters = locals()
    containerapp_job_decorator = ContainerAppJobDecorator(
        cmd=cmd,
        client=ContainerAppsJobPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_job_decorator.validate_subscription_registered(CONTAINER_APPS_RP)

    return containerapp_job_decorator.delete()


def create_or_update_github_action(cmd,
                                   name,
                                   resource_group_name,
                                   repo_url,
                                   registry_url=None,
                                   registry_username=None,
                                   registry_password=None,
                                   branch=None,
                                   token=None,
                                   login_with_github=False,
                                   image=None,
                                   context_path=None,
                                   build_env_vars=None,
                                   service_principal_client_id=None,
                                   service_principal_client_secret=None,
                                   service_principal_tenant_id=None,
                                   trigger_existing_workflow=False,
                                   no_wait=False):
    from azure.cli.command_modules.containerapp.custom import _validate_github

    if not token and not login_with_github:
        raise_missing_token_suggestion()
    elif not token:
        scopes = ["admin:repo_hook", "repo", "workflow"]
        token = get_github_access_token(cmd, scopes)
    elif token and login_with_github:
        logger.warning("Both token and --login-with-github flag are provided. Will use provided token")

    repo = repo_url_to_name(repo_url)
    repo_url = f"https://github.com/{repo}"  # allow specifying repo as <user>/<repo> without the full github url

    branch = _validate_github(repo, branch, token)

    source_control_info = None

    try:
        source_control_info = GitHubActionPreviewClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)

    except Exception as ex:
        if not service_principal_client_id or not service_principal_client_secret or not service_principal_tenant_id:
            raise RequiredArgumentMissingError('Service principal client ID, secret and tenant ID are required to add github actions for the first time. Please create one using the command \"az ad sp create-for-rbac --name {{name}} --role contributor --scopes /subscriptions/{{subscription}}/resourceGroups/{{resourceGroup}} --sdk-auth\"') from ex
        source_control_info = SourceControlModel

    # Need to trigger the workflow manually if it already exists (performing an update)
    try:
        workflow_name = GitHubActionPreviewClient.get_workflow_name(cmd=cmd, repo=repo, branch_name=branch, container_app_name=name, token=token)
        if workflow_name is not None:
            if trigger_existing_workflow:
                trigger_workflow(token, repo, workflow_name, branch)
            return source_control_info
    except:  # pylint: disable=bare-except
        pass

    source_control_info["properties"]["repoUrl"] = repo_url
    source_control_info["properties"]["branch"] = branch

    azure_credentials = None

    if service_principal_client_id or service_principal_client_secret or service_principal_tenant_id:
        azure_credentials = AzureCredentialsModel
        azure_credentials["clientId"] = service_principal_client_id
        azure_credentials["clientSecret"] = service_principal_client_secret
        azure_credentials["tenantId"] = service_principal_tenant_id
        azure_credentials["subscriptionId"] = get_subscription_id(cmd.cli_ctx)

    # Registry
    if registry_username is None or registry_password is None:
        # If registry is Azure Container Registry, we can try inferring credentials
        if not registry_url or ACR_IMAGE_SUFFIX not in registry_url:
            raise RequiredArgumentMissingError('Registry url is required if using Azure Container Registry, otherwise Registry username and password are required if using Dockerhub')
        logger.warning('No credential was provided to access Azure Container Registry. Trying to look up...')
        parsed = urlparse(registry_url)
        registry_name = (parsed.netloc if parsed.scheme else parsed.path).split('.')[0]

        try:
            registry_username, registry_password, _ = _get_acr_cred(cmd.cli_ctx, registry_name)
        except Exception as ex:
            raise RequiredArgumentMissingError('Failed to retrieve credentials for container registry. Please provide the registry username and password') from ex

    registry_info = RegistryInfoModel
    registry_info["registryUrl"] = registry_url
    registry_info["registryUserName"] = registry_username
    registry_info["registryPassword"] = registry_password

    github_action_configuration = GitHubActionConfiguration
    github_action_configuration["registryInfo"] = registry_info
    github_action_configuration["azureCredentials"] = azure_credentials
    github_action_configuration["contextPath"] = context_path
    github_action_configuration["buildEnvironmentVariables"] = parse_build_env_vars(build_env_vars)
    github_action_configuration["image"] = image

    source_control_info["properties"]["githubActionConfiguration"] = github_action_configuration

    headers = ["x-ms-github-auxiliary={}".format(token)]

    try:
        logger.warning("Creating Github action...")
        r = GitHubActionPreviewClient.create_or_update(cmd=cmd, resource_group_name=resource_group_name, name=name, github_action_envelope=source_control_info, headers=headers, no_wait=no_wait)
        if not no_wait:
            WORKFLOW_POLL_RETRY = 6
            WORKFLOW_POLL_SLEEP = 10

            # Poll for the workflow file just created (may take up to 30s)
            for _ in range(0, WORKFLOW_POLL_RETRY):
                time.sleep(WORKFLOW_POLL_SLEEP)
                workflow_name = GitHubActionPreviewClient.get_workflow_name(cmd=cmd, repo=repo, branch_name=branch, container_app_name=name, token=token)
                if workflow_name is not None:
                    await_github_action(token, repo, workflow_name)
                    return r

            raise ValidationError(
                "Exhausted the number of re-tries allotted to polling the creation of the workflow file for Container App '{}' in .github/workflow folder for repo '{}'. ".format(name, repo) +
                "Please check the provided repository '{}' for the GitHub Action workflow that was created and the status of it. If this file was removed, please use the 'az containerapp github-action delete' command to disconnect the removed workflow file connection.".format(repo))
        return r
    except Exception as e:
        handle_raw_exception(e)


def list_replicas(cmd, resource_group_name, name, revision=None):

    try:
        app = ContainerAppPreviewClient.show(cmd, resource_group_name, name)
        if not revision:
            revision = app["properties"]["latestRevisionName"]
        return ContainerAppPreviewClient.list_replicas(cmd=cmd,
                                                       resource_group_name=resource_group_name,
                                                       container_app_name=name,
                                                       revision_name=revision)
    except Exception as e:
        handle_raw_exception(e)


def count_replicas(cmd, resource_group_name, name, revision=None):

    try:
        app = ContainerAppPreviewClient.show(cmd, resource_group_name, name)
        if not revision:
            revision = safe_get(app, "properties", "latestRevisionName")
            if not revision:
                raise ValidationError("No revision found for containerapp.")
    except Exception as e:
        handle_raw_exception(e)

    try:
        count = len(ContainerAppPreviewClient.list_replicas(cmd=cmd,
                                                            resource_group_name=resource_group_name,
                                                            container_app_name=name,
                                                            revision_name=revision))
        return count
    except Exception as e:
        handle_raw_exception(e)


def get_replica(cmd, resource_group_name, name, replica, revision=None):

    try:
        app = ContainerAppPreviewClient.show(cmd, resource_group_name, name)
        if not revision:
            revision = app["properties"]["latestRevisionName"]
        return ContainerAppPreviewClient.get_replica(cmd=cmd,
                                                     resource_group_name=resource_group_name,
                                                     container_app_name=name,
                                                     revision_name=revision,
                                                     replica_name=replica)
    except Exception as e:
        handle_raw_exception(e)


def containerapp_up(cmd,
                    name,
                    resource_group_name=None,
                    environment=None,
                    location=None,
                    registry_server=None,
                    image=None,
                    source=None,
                    artifact=None,
                    build_env_vars=None,
                    ingress=None,
                    target_port=None,
                    registry_user=None,
                    registry_pass=None,
                    env_vars=None,
                    logs_customer_id=None,
                    logs_key=None,
                    repo=None,
                    token=None,
                    branch=None,
                    browse=False,
                    context_path=None,
                    workload_profile_name=None,
                    service_principal_client_id=None,
                    service_principal_client_secret=None,
                    service_principal_tenant_id=None,
                    custom_location_id=None,
                    connected_cluster_id=None):
    from ._up_utils import (_validate_up_args, _validate_custom_location_connected_cluster_args, _reformat_image, _get_dockerfile_content, _get_ingress_and_target_port,
                            ResourceGroup, Extension, CustomLocation, ContainerAppEnvironment, ContainerApp, _get_registry_from_app,
                            _get_registry_details, _create_github_action, _set_up_defaults, up_output,
                            check_env_name_on_rg, get_token, _has_dockerfile)
    from azure.cli.command_modules.containerapp._github_oauth import cache_github_token
    HELLOWORLD = "mcr.microsoft.com/k8se/quickstart"
    dockerfile = "Dockerfile"  # for now the dockerfile name must be "Dockerfile" (until GH actions API is updated)

    register_provider_if_needed(cmd, CONTAINER_APPS_RP)
    _validate_up_args(cmd, source, artifact, build_env_vars, image, repo, registry_server)
    _validate_custom_location_connected_cluster_args(cmd,
                                                     env=environment,
                                                     resource_group_name=resource_group_name,
                                                     location=location,
                                                     custom_location_id=custom_location_id,
                                                     connected_cluster_id=connected_cluster_id)
    if artifact:
        # Artifact is mostly a convenience argument provided to use --source specifically with a single artifact file.
        # At this point we know for sure that source isn't set (else _validate_up_args would have failed), so we can build with this value.
        source = artifact
    validate_container_app_name(name, AppType.ContainerApp.name)
    check_env_name_on_rg(cmd, environment, resource_group_name, location, custom_location_id, connected_cluster_id)

    image = _reformat_image(source, repo, image)
    token = get_token(cmd, repo, token)

    if image and HELLOWORLD in image.lower():
        ingress = "external" if not ingress else ingress
        target_port = 80 if not target_port else target_port

    if image:
        if ingress and not target_port:
            target_port = 80
            logger.warning("No ingress provided, defaulting to port 80. Try `az containerapp up --ingress %s --target-port <port>` to set a custom port.", ingress)

    # Check if source contains a Dockerfile
    # and ignore checking if Dockerfile exists in repo since GitHub action inherently checks for it.
    if _has_dockerfile(source, dockerfile):
        dockerfile_content = _get_dockerfile_content(repo, branch, token, source, context_path, dockerfile)
        ingress, target_port = _get_ingress_and_target_port(ingress, target_port, dockerfile_content)

    resource_group = ResourceGroup(cmd, name=resource_group_name, location=location)
    custom_location = CustomLocation(cmd, name=custom_location_id, resource_group_name=resource_group_name, connected_cluster_id=connected_cluster_id)
    extension = Extension(cmd, logs_rg=resource_group_name, logs_location=location, logs_share_key=logs_key, logs_customer_id=logs_customer_id, connected_cluster_id=connected_cluster_id)
    env = ContainerAppEnvironment(cmd, environment, resource_group, location=location, logs_key=logs_key, logs_customer_id=logs_customer_id, custom_location_id=custom_location_id, connected_cluster_id=connected_cluster_id)
    app = ContainerApp(cmd, name, resource_group, None, image, env, target_port, registry_server, registry_user, registry_pass, env_vars, workload_profile_name, ingress)

    # Check and see if registry username and passwords are specified. If so, set is_registry_server_params_set to True to use those creds.
    is_registry_server_params_set = bool(registry_server and registry_user and registry_pass)
    _set_up_defaults(cmd, name, resource_group_name, logs_customer_id, location, resource_group, env, app, custom_location, extension, is_registry_server_params_set)

    if app.check_exists():
        if app.get()["properties"]["provisioningState"] == "InProgress":
            raise ValidationError("Containerapp has an existing provisioning in progress. Please wait until provisioning has completed and rerun the command.")

    resource_group.create_if_needed()
    extension.create_if_needed()
    custom_location.create_if_needed()
    env.create_if_needed(name)

    if source or repo:
        if not registry_server:
            _get_registry_from_app(app, source)  # if the app exists, get the registry
        _get_registry_details(cmd, app, source)  # fetch ACR creds from arguments registry arguments

    force_single_container_updates = False
    if source:
        force_single_container_updates = app.run_source_to_cloud_flow(source, dockerfile, build_env_vars, can_create_acr_if_needed=True, registry_server=registry_server)
        app.set_force_single_container_updates(force_single_container_updates)
    else:
        app.create_acr_if_needed()

    app.create(no_registry=bool(repo or force_single_container_updates))
    if repo:
        _create_github_action(app, env, service_principal_client_id, service_principal_client_secret,
                              service_principal_tenant_id, branch, token, repo, context_path, build_env_vars)
        cache_github_token(cmd, token, repo)

    if browse:
        open_containerapp_in_browser(cmd, app.name, app.resource_group.name)

    up_output(app, no_dockerfile=(source and not _has_dockerfile(source, dockerfile)))


def containerapp_up_logic(cmd, resource_group_name, name, managed_env, image, env_vars, ingress, target_port, registry_server, registry_user, workload_profile_name, registry_pass, environment_type=None, force_single_container_updates=False):
    containerapp_def = None
    try:
        containerapp_def = ContainerAppPreviewClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except:
        pass

    if containerapp_def:
        return update_containerapp_logic(cmd=cmd, name=name, resource_group_name=resource_group_name, image=image, replace_env_vars=env_vars, ingress=ingress, target_port=target_port,
                                         registry_server=registry_server, registry_user=registry_user, registry_pass=registry_pass, workload_profile_name=workload_profile_name, container_name=name, force_single_container_updates=force_single_container_updates)
    return create_containerapp(cmd=cmd, name=name, resource_group_name=resource_group_name, managed_env=managed_env, image=image, env_vars=env_vars, ingress=ingress, target_port=target_port, registry_server=registry_server, registry_user=registry_user, registry_pass=registry_pass, workload_profile_name=workload_profile_name, environment_type=environment_type)


def create_managed_certificate(cmd, name, resource_group_name, hostname, validation_method, certificate_name=None):
    if certificate_name and not check_managed_cert_name_availability(cmd, resource_group_name, name, certificate_name):
        raise ValidationError(f"Certificate name '{certificate_name}' is not available.")
    cert_name = certificate_name
    while not cert_name:
        cert_name = generate_randomized_managed_cert_name(hostname, resource_group_name)
        if not check_managed_cert_name_availability(cmd, resource_group_name, name, certificate_name):
            cert_name = None
    certificate_envelop = prepare_managed_certificate_envelop(cmd, name, resource_group_name, hostname, validation_method.upper())
    try:
        r = ManagedEnvironmentPreviewClient.create_or_update_managed_certificate(cmd, resource_group_name, name, cert_name, certificate_envelop, True, validation_method.upper() == 'TXT')
        return r
    except Exception as e:
        handle_raw_exception(e)


def list_certificates(cmd, name, resource_group_name, location=None, certificate=None, thumbprint=None, managed_certificates_only=False, private_key_certificates_only=False):
    raw_parameters = locals()

    containerapp_env_certificate_list_decorator = ContainerappPreviewEnvCertificateListDecorator(
        cmd=cmd,
        client=ManagedEnvironmentPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_env_certificate_list_decorator.validate_subscription_registered(CONTAINER_APPS_RP)
    containerapp_env_certificate_list_decorator.validate_arguments()

    return containerapp_env_certificate_list_decorator.list()


def upload_certificate(cmd, name, resource_group_name, certificate_file=None, certificate_name=None, certificate_password=None, location=None, prompt=False, certificate_identity = None, certificate_key_vault_url=None):
    raw_parameters = locals()

    containerapp_env_certificate_upload_decorator = ContainerappEnvCertificatePreviweUploadDecorator(
        cmd=cmd,
        client=ManagedEnvironmentPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_env_certificate_upload_decorator.validate_subscription_registered(CONTAINER_APPS_RP)
    containerapp_env_certificate_upload_decorator.validate_arguments()
    containerapp_env_certificate_upload_decorator.construct_payload()

    return containerapp_env_certificate_upload_decorator.create_or_update()


def delete_certificate(cmd, resource_group_name, name, location=None, certificate=None, thumbprint=None):
    from azure.cli.command_modules.containerapp.custom import delete_certificate_logic

    delete_certificate_logic(cmd=cmd, resource_group_name=resource_group_name, name=name, cert_name=certificate, location=location, certificate=certificate, thumbprint=thumbprint)


def bind_hostname(cmd, resource_group_name, name, hostname, thumbprint=None, certificate=None, location=None, environment=None, validation_method=None):
    from azure.cli.command_modules.containerapp.custom import bind_hostname_logic

    return bind_hostname_logic(cmd=cmd, resource_group_name=resource_group_name, name=name, hostname=hostname, thumbprint=thumbprint, certificate=certificate, location=location, environment=environment, validation_method=validation_method)


def update_auth_config(cmd, resource_group_name, name, set_string=None, enabled=None,
                       runtime_version=None, config_file_path=None, unauthenticated_client_action=None,
                       redirect_provider=None, require_https=None,
                       proxy_convention=None, proxy_custom_host_header=None,
                       proxy_custom_proto_header=None, excluded_paths=None,
                       token_store=None, sas_url_secret=None, sas_url_secret_name=None,
                       yes=False):
    raw_parameters = locals()
    containerapp_auth_decorator = ContainerAppPreviewAuthDecorator(
        cmd=cmd,
        client=AuthPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )

    containerapp_auth_decorator.construct_payload()
    if containerapp_auth_decorator.get_argument_token_store() and containerapp_auth_decorator.get_argument_sas_url_secret() is not None:
        set_secrets(cmd, name, resource_group_name, secrets=[f"{BLOB_STORAGE_TOKEN_STORE_SECRET_SETTING_NAME}={containerapp_auth_decorator.get_argument_sas_url_secret()}"], no_wait=True, disable_max_length=True)
    return containerapp_auth_decorator.create_or_update()


def show_auth_config(cmd, resource_group_name, name):
    raw_parameters = locals()
    containerapp_auth_decorator = ContainerAppPreviewAuthDecorator(
        cmd=cmd,
        client=AuthPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )

    return containerapp_auth_decorator.show()


# Compose
def create_containerapps_from_compose(cmd,  # pylint: disable=R0914
                                      resource_group_name,
                                      managed_env,
                                      compose_file_path='./docker-compose.yml',
                                      registry_server=None,
                                      registry_user=None,
                                      registry_pass=None,
                                      transport_mapping=None,
                                      location=None,
                                      tags=None):
    from pycomposefile import ComposeFile

    from azure.cli.command_modules.containerapp._compose_utils import (create_containerapps_compose_environment,
                                                                       build_containerapp_from_compose_service,
                                                                       check_supported_platform,
                                                                       warn_about_unsupported_elements,
                                                                       resolve_ingress_and_target_port,
                                                                       resolve_registry_from_cli_args,
                                                                       resolve_transport_from_cli_args,
                                                                       resolve_service_startup_command,
                                                                       resolve_cpu_configuration_from_service,
                                                                       resolve_memory_configuration_from_service,
                                                                       resolve_replicas_from_service,
                                                                       resolve_environment_from_service,
                                                                       resolve_secret_from_service)
    from ._compose_utils import validate_memory_and_cpu_setting

    # Validate managed environment
    parsed_managed_env = parse_resource_id(managed_env)
    managed_env_name = parsed_managed_env['name']
    env_rg = parsed_managed_env.get('resource_group', resource_group_name)

    try:
        managed_environment = show_managed_environment(cmd=cmd,
                                                       name=managed_env_name,
                                                       resource_group_name=env_rg)
    except CLIInternalError:  # pylint: disable=W0702
        logger.info(  # pylint: disable=W1203
            f"Creating the Container Apps managed environment {managed_env_name} under {env_rg} in {location}.")
        managed_environment = create_containerapps_compose_environment(cmd,
                                                                       managed_env_name,
                                                                       env_rg,
                                                                       tags=tags)

    compose_yaml = load_yaml_file(compose_file_path)
    parsed_compose_file = ComposeFile(compose_yaml)
    logger.info(parsed_compose_file)
    containerapps_from_compose = []
    # Using the key to iterate to get the service name
    # pylint: disable=C0201,C0206
    for service_name in parsed_compose_file.ordered_services.keys():
        service = parsed_compose_file.services[service_name]
        if not check_supported_platform(service.platform):
            message = "Unsupported platform found. "
            message += "Azure Container Apps only supports linux/amd64 container images."
            raise InvalidArgumentValueError(message)
        image = service.image
        warn_about_unsupported_elements(service)
        logger.info(  # pylint: disable=W1203
            f"Creating the Container Apps instance for {service_name} under {resource_group_name} in {location}.")
        ingress_type, target_port = resolve_ingress_and_target_port(service)
        registry, registry_username, registry_password = resolve_registry_from_cli_args(registry_server, registry_user, registry_pass)  # pylint: disable=C0301
        transport_setting = resolve_transport_from_cli_args(service_name, transport_mapping)
        startup_command, startup_args = resolve_service_startup_command(service)
        cpu, memory = validate_memory_and_cpu_setting(
            resolve_cpu_configuration_from_service(service),
            resolve_memory_configuration_from_service(service),
            managed_environment
        )
        replicas = resolve_replicas_from_service(service)
        environment = resolve_environment_from_service(service)
        secret_vars, secret_env_ref = resolve_secret_from_service(service, parsed_compose_file.secrets)
        if environment is not None and secret_env_ref is not None:
            environment.extend(secret_env_ref)
        elif secret_env_ref is not None:
            environment = secret_env_ref
        if service.build is not None:
            logger.warning("Build configuration defined for this service.")
            logger.warning("The build will be performed by Azure Container Registry.")
            context = service.build.context
            dockerfile = "Dockerfile"
            if service.build.dockerfile is not None:
                dockerfile = service.build.dockerfile
            image, registry, registry_username, registry_password = build_containerapp_from_compose_service(
                cmd,
                service_name,
                context,
                dockerfile,
                resource_group_name,
                managed_env,
                location,
                image,
                target_port,
                ingress_type,
                registry,
                registry_username,
                registry_password,
                environment)
        containerapps_from_compose.append(
            create_containerapp(cmd,
                                service_name,
                                resource_group_name,
                                image=image,
                                container_name=service.container_name,
                                managed_env=managed_environment["id"],
                                ingress=ingress_type,
                                target_port=target_port,
                                registry_server=registry,
                                registry_user=registry_username,
                                registry_pass=registry_password,
                                transport=transport_setting,
                                startup_command=startup_command,
                                args=startup_args,
                                cpu=cpu,
                                memory=memory,
                                env_vars=environment,
                                secrets=secret_vars,
                                min_replicas=replicas,
                                max_replicas=replicas, )
        )
    return containerapps_from_compose


def set_workload_profile(cmd, resource_group_name, env_name, workload_profile_name, workload_profile_type=None, min_nodes=None, max_nodes=None):
    return update_managed_environment(cmd, env_name, resource_group_name, workload_profile_type=workload_profile_type, workload_profile_name=workload_profile_name, min_nodes=min_nodes, max_nodes=max_nodes)


def patch_list(cmd, resource_group_name=None, managed_env=None, show_all=False):
    # Ensure that Docker is running locally before attempting to use the pack CLI
    if is_docker_running() is False:
        logger.error("Please install or start Docker and try again.")
        return

    # Ensure that the pack CLI is installed locally
    pack_exec_path = get_pack_exec_path()
    if pack_exec_path is None:
        return

    # List all Container Apps in the given resource group and managed environment
    logger.warning("Listing container apps...")
    ca_list = list_containerapp(cmd, resource_group_name, managed_env)

    # Fetch all images currently deployed to containers for the listed Container Apps
    imgs = []
    if ca_list:
        for ca in ca_list:
            id_parts = parse_resource_id(ca["id"])
            resource_group_name = id_parts.get('resource_group')
            container_app_name = id_parts.get('name')
            managed_env_id_parts = parse_resource_id(ca["properties"]["environmentId"])
            managed_env_name = managed_env_id_parts.get('name')
            containers = safe_get(ca, "properties", "template", "containers")
            for container in containers:
                result = dict(
                    imageName=container["image"],
                    targetContainerName=container["name"],
                    targetContainerAppName=container_app_name,
                    targetContainerAppEnvironmentName=managed_env_name,
                    targetResourceGroup=resource_group_name)
                imgs.append(result)

    # Iterate over each image and execute the `pack inspect` command to fetch the run image used (if previously built via buildpacks)
    results = []
    inspect_results = []
    logger.warning("Inspecting container apps images...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        [executor.submit(patch_get_image_inspection, pack_exec_path, img, inspect_results) for img in imgs]

    # Fetch the list of Oryx-based run images that could be used to patch previously built images
    oryx_run_images = get_oryx_run_image_tags()

    # Start checking if the images are based on an Oryx image
    results = []
    logger.warning("Checking for patches...")
    for inspect_result in inspect_results:
        results.append(_get_patchable_check_result(inspect_result, oryx_run_images))
    if show_all is False:
        results = [result for result in results if result["id"] is not None]
    if not results:
        logger.warning("No container apps available to patch at this time. Use --show-all to show the container apps that cannot be patched.")
    return results


def _get_patchable_check_result(inspect_result, oryx_run_images):
    # Define reasons for patchable check failure
    failed_reason = "Failed to inspect the image. Please make sure that you are authenticated to the container registry and that the image exists."
    not_based_on_oryx_reason = "Image not based on an Oryx runtime."
    mcr_check_reason = "Image does not have a base pulled from a supported platform MCR repository."

    # Define base result object
    result = dict(
        targetContainerName=inspect_result["targetContainerName"],
        targetContainerAppName=inspect_result["targetContainerAppName"],
        targetContainerAppEnvironmentName=inspect_result["targetContainerAppEnvironmentName"],
        targetResourceGroup=inspect_result["targetResourceGroup"],
        oldRunImage=None,
        newRunImage=None,
        id=None,
    )

    # Check if the image was previously found
    if inspect_result["remote_info"] == 401:
        result.update(
            targetImageName=inspect_result["image_name"],
            reason=failed_reason
        )
        return result

    # Divide run-images into different parts by "/"
    run_images_props = inspect_result["remote_info"]["run_images"]

    # Check if a base run image was found for the image
    if run_images_props is None:
        result.update(
            targetImageName=inspect_result["image_name"],
            reason=not_based_on_oryx_reason)
        return result

    # Define the MCR repositories that are supported for patching
    mcr_repos = ["oryx/dotnetcore", "oryx/node", "oryx/python", "azure-buildpacks/java"]

    # Iterate over each base run image found to see if a patch can be applied
    for run_images_prop in run_images_props:
        base_run_image_name = run_images_prop["name"]
        if any(base_run_image_name.find(repo) != -1 for repo in mcr_repos):
            return patchable_check(base_run_image_name, oryx_run_images, inspect_result=inspect_result)

        # Not based on a supported MCR repository
        result.update(
            oldRunImage=inspect_result["remote_info"]["run_images"],
            reason=mcr_check_reason)
        return result


def patch_get_image_inspection(pack_exec_path, img, info_list):
    # Execute the 'pack inspect' command on an image and return the result (with additional Container App metadata)
    with subprocess.Popen(pack_exec_path + " inspect-image " + img["imageName"] + " --output json", shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE) as img_info:
        img_info_out, img_info_err = img_info.communicate()
        if img_info_err.find(b"status code 401 Unauthorized") != -1 or img_info_err.find(b"unable to find image") != -1:
            inspect_result = dict(remote_info=401, image_name=img["imageName"])
        else:
            inspect_result = json.loads(img_info_out)
        inspect_result.update({
            "targetContainerName": img["targetContainerName"],
            "targetContainerAppName": img["targetContainerAppName"],
            "targetContainerAppEnvironmentName": img["targetContainerAppEnvironmentName"],
            "targetResourceGroup": img["targetResourceGroup"]
        })
    info_list.append(inspect_result)


def patch_interactive(cmd, resource_group_name=None, managed_env=None, show_all=False):
    if is_docker_running() is False:
        logger.error("Please install or start Docker and try again.")
        return
    patchable_check_results = patch_list(cmd, resource_group_name, managed_env, show_all=show_all)
    pack_exec_path = get_pack_exec_path()
    if pack_exec_path is None:
        return
    if patchable_check_results is None:
        return
    patchable_check_results_json = json.dumps(patchable_check_results, indent=2)
    without_unpatchable_results = []
    without_unpatchable_results = [result for result in patchable_check_results if result["id"] is not None]
    if without_unpatchable_results == [] and (patchable_check_results is None or show_all is False):
        return
    logger.warning(patchable_check_results_json)
    if without_unpatchable_results == []:
        return
    user_input = input("Do you want to apply all the patches or specify by id? (y/n/id)\n")
    patch_apply_handle_input(cmd, patchable_check_results, user_input, pack_exec_path)


def patch_apply(cmd, resource_group_name=None, managed_env=None, show_all=False):
    if is_docker_running() is False:
        logger.error("Please install or start Docker and try again.")
        return
    patchable_check_results = patch_list(cmd, resource_group_name, managed_env, show_all=show_all)
    pack_exec_path = get_pack_exec_path()
    if pack_exec_path is None:
        return
    if patchable_check_results is None:
        return
    patchable_check_results_json = json.dumps(patchable_check_results, indent=2)
    without_unpatchable_results = []
    without_unpatchable_results = [result for result in patchable_check_results if result["id"] is not None]
    if without_unpatchable_results == [] and (patchable_check_results is None or show_all is False):
        return
    logger.warning(patchable_check_results_json)
    if without_unpatchable_results == []:
        return
    patch_apply_handle_input(cmd, patchable_check_results, "y", pack_exec_path)


def patch_apply_handle_input(cmd, patch_check_list, method, pack_exec_path):
    input_method = method.strip().lower()
    # Track number of times patches were applied successfully.
    patch_apply_count = 0
    if input_method == "y":
        telemetry_record_method = "y"
        for patch_check in patch_check_list:
            if patch_check["id"] and patch_check["newRunImage"]:
                patch_cli_call(cmd,
                               patch_check["targetResourceGroup"],
                               patch_check["targetContainerAppName"],
                               patch_check["targetContainerName"],
                               patch_check["targetImageName"],
                               patch_check["newRunImage"],
                               pack_exec_path)
                # Increment patch_apply_count with every successful patch.
                patch_apply_count += 1
    elif input_method == "n":
        telemetry_record_method = "n"
        logger.warning("No patch applied.")
        return
    else:
        # Check if method is an existing id in the list
        for patch_check in patch_check_list:
            if patch_check["id"] == input_method:
                patch_cli_call(cmd,
                               patch_check["targetResourceGroup"],
                               patch_check["targetContainerAppName"],
                               patch_check["targetContainerName"],
                               patch_check["targetImageName"],
                               patch_check["newRunImage"],
                               pack_exec_path)
                patch_apply_count += 1
                telemetry_record_method = input_method
                break
        else:
            telemetry_record_method = "invalid"
            logger.error("Invalid patch method or id.")
    patch_apply_properties = {
        'Context.Default.AzureCLI.PatchUserResponse': telemetry_record_method,
        'Context.Default.AzureCLI.PatchApplyCount': patch_apply_count
    }
    telemetry_core.add_extension_event('containerapp', patch_apply_properties)
    return


def patch_cli_call(cmd, resource_group, container_app_name, container_name, target_image_name, new_run_image, pack_exec_path):
    try:
        logger.warning("Applying patch for container app: " + container_app_name + " container: " + container_name)
        subprocess.run(f"{pack_exec_path} rebase -q {target_image_name} --run-image {new_run_image} --force", shell=True, check=True)
        new_target_image_name = target_image_name.split(":")[0] + ":" + new_run_image.split(":")[1]
        subprocess.run(f"docker tag {target_image_name} {new_target_image_name}", shell=True, check=True)
        logger.debug(f"Publishing {new_target_image_name} to registry...")
        subprocess.run(f"docker push -q {new_target_image_name}", shell=True, check=True)
        logger.warning("Patch applied and published successfully.\nNew image: " + new_target_image_name)
    except Exception:
        logger.error("Error: Failed to apply patch and publish. Check if registry is logged in and has write access.")
        raise
    try:
        logger.warning("Patching container app: " + container_app_name + " container: " + container_name)
        logger.info("Creating new revision with image: " + new_target_image_name)
        update_info_json = update_containerapp(cmd,
                                               name=container_app_name,
                                               resource_group_name=resource_group,
                                               container_name=container_name,
                                               image=new_target_image_name)
        logger.warning(json.dumps(update_info_json, indent=2))
        logger.warning("Container app revision created successfully from the patched image.")
        return
    except Exception:
        logger.error("Error: Failed to create new revision with the container app.")
        raise


def show_connected_environment(cmd, name, resource_group_name):
    raw_parameters = locals()
    connected_env_decorator = ConnectedEnvironmentDecorator(
        cmd=cmd,
        client=ConnectedEnvironmentClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    connected_env_decorator.validate_subscription_registered(CONTAINER_APPS_RP)

    return connected_env_decorator.show()


def list_connected_environments(cmd, resource_group_name=None, custom_location=None):
    raw_parameters = locals()
    connected_env_decorator = ConnectedEnvironmentDecorator(
        cmd=cmd,
        client=ConnectedEnvironmentClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    connected_env_decorator.validate_subscription_registered(CONTAINER_APPS_RP)

    return connected_env_decorator.list()


def delete_connected_environment(cmd, name, resource_group_name, no_wait=False):
    raw_parameters = locals()
    connected_env_decorator = ConnectedEnvironmentDecorator(
        cmd=cmd,
        client=ConnectedEnvironmentClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    connected_env_decorator.validate_subscription_registered(CONTAINER_APPS_RP)

    return connected_env_decorator.delete()


def create_connected_environment(cmd,
                                 name,
                                 resource_group_name,
                                 custom_location,
                                 location=None,
                                 dapr_ai_connection_string=None,
                                 static_ip=None,
                                 tags=None,
                                 no_wait=False):
    raw_parameters = locals()
    connected_env_create_decorator = ConnectedEnvironmentCreateDecorator(
        cmd=cmd,
        client=ConnectedEnvironmentClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    connected_env_create_decorator.validate_arguments()
    connected_env_create_decorator.register_provider(CONTAINER_APPS_RP)

    connected_env_create_decorator.construct_payload()
    r = connected_env_create_decorator.create()

    return r


def connected_env_list_dapr_components(cmd, resource_group_name, environment_name):
    _validate_subscription_registered(cmd, CONTAINER_APPS_RP)

    return ConnectedEnvDaprComponentClient.list(cmd, resource_group_name, environment_name)


def connected_env_show_dapr_component(cmd, resource_group_name, dapr_component_name, environment_name):
    _validate_subscription_registered(cmd, CONTAINER_APPS_RP)

    return ConnectedEnvDaprComponentClient.show(cmd, resource_group_name, environment_name, name=dapr_component_name)


def connected_env_remove_dapr_component(cmd, resource_group_name, dapr_component_name, environment_name):
    _validate_subscription_registered(cmd, CONTAINER_APPS_RP)

    try:
        r = ConnectedEnvDaprComponentClient.delete(cmd, resource_group_name, environment_name, name=dapr_component_name)
        logger.warning("Dapr componenet successfully deleted.")
        return r
    except Exception as e:
        handle_raw_exception(e)


def connected_env_create_or_update_dapr_component(cmd, resource_group_name, environment_name, dapr_component_name, yaml):
    _validate_subscription_registered(cmd, CONTAINER_APPS_RP)

    yaml_dapr_component = load_yaml_file(yaml)
    if type(yaml_dapr_component) != dict:  # pylint: disable=unidiomatic-typecheck
        raise ValidationError('Invalid YAML provided. Please see https://learn.microsoft.com/en-us/azure/container-apps/dapr-overview?tabs=bicep1%2Cyaml#component-schema for a valid Dapr Component YAML spec.')

    # Deserialize the yaml into a DaprComponent object. Need this since we're not using SDK
    try:
        deserializer = create_deserializer()
        daprcomponent_def = deserializer('DaprComponent', yaml_dapr_component)
    except DeserializationError as ex:
        raise ValidationError('Invalid YAML provided. Please see https://learn.microsoft.com/en-us/azure/container-apps/dapr-overview?tabs=bicep1%2Cyaml#component-schema for a valid Dapr Component YAML spec.') from ex

    daprcomponent_def = _convert_object_from_snake_to_camel_case(_object_to_dict(daprcomponent_def))

    # Remove "additionalProperties" and read-only attributes that are introduced in the deserialization. Need this since we're not using SDK
    _remove_additional_attributes(daprcomponent_def)
    _remove_dapr_readonly_attributes(daprcomponent_def)

    if not daprcomponent_def["ignoreErrors"]:
        daprcomponent_def["ignoreErrors"] = False

    dapr_component_envelope = {"properties": daprcomponent_def}

    try:
        r = ConnectedEnvDaprComponentClient.create_or_update(cmd, resource_group_name=resource_group_name,
                                                             environment_name=environment_name,
                                                             dapr_component_envelope=dapr_component_envelope,
                                                             name=dapr_component_name)
        return r
    except Exception as e:
        handle_raw_exception(e)


def connected_env_list_certificates(cmd, name, resource_group_name, location=None, certificate=None, thumbprint=None):
    _validate_subscription_registered(cmd, CONTAINER_APPS_RP)

    def location_match(c):
        return c["location"] == location or not location

    def thumbprint_match(c):
        return c["properties"]["thumbprint"] == thumbprint or not thumbprint

    def both_match(c):
        return location_match(c) and thumbprint_match(c)

    if certificate:
        if is_valid_resource_id(certificate):
            certificate_name = parse_resource_id(certificate)["resource_name"]
        else:
            certificate_name = certificate
        try:
            r = ConnectedEnvCertificateClient.show_certificate(cmd, resource_group_name, name, certificate_name)
            return [r] if both_match(r) else []
        except Exception as e:
            handle_raw_exception(e)
    else:
        try:
            r = ConnectedEnvCertificateClient.list_certificates(cmd, resource_group_name, name)
            return list(filter(both_match, r))
        except Exception as e:
            handle_raw_exception(e)


def connected_env_upload_certificate(cmd, name, resource_group_name, certificate_file, certificate_name=None, certificate_password=None, location=None, prompt=False):
    _validate_subscription_registered(cmd, CONTAINER_APPS_RP)

    blob, thumbprint = load_cert_file(certificate_file, certificate_password)

    cert_name = None
    if certificate_name:
        name_availability = connected_env_check_cert_name_availability(cmd, resource_group_name, name, certificate_name)
        if not name_availability["nameAvailable"]:
            if name_availability["reason"] == NAME_ALREADY_EXISTS:
                msg = '{}. If continue with this name, it will be overwritten by the new certificate file.\nOverwrite?'
                overwrite = True
                if prompt:
                    overwrite = prompt_y_n(msg.format(name_availability["message"]))
                else:
                    logger.warning('{}. It will be overwritten by the new certificate file.'.format(name_availability["message"]))
                if overwrite:
                    cert_name = certificate_name
            else:
                raise ValidationError(name_availability["message"])
        else:
            cert_name = certificate_name

    while not cert_name:
        random_name = generate_randomized_cert_name(thumbprint, name, resource_group_name)
        check_result = connected_env_check_cert_name_availability(cmd, resource_group_name, name, random_name)
        if check_result["nameAvailable"]:
            cert_name = random_name
        elif not check_result["nameAvailable"] and (check_result["reason"] == NAME_INVALID):
            raise ValidationError(check_result["message"])

    certificate = ContainerAppCertificateEnvelopeModel
    certificate["properties"]["password"] = certificate_password
    certificate["properties"]["value"] = blob
    certificate["location"] = location
    if not certificate["location"]:
        try:
            env = ConnectedEnvironmentClient.show(cmd, resource_group_name, name)
            certificate["location"] = env["location"]
        except Exception as e:
            handle_raw_exception(e)

    try:
        r = ConnectedEnvCertificateClient.create_or_update_certificate(cmd, resource_group_name, name, cert_name, certificate)
        return r
    except Exception as e:
        handle_raw_exception(e)


def connected_env_delete_certificate(cmd, resource_group_name, name, certificate=None, thumbprint=None):
    _validate_subscription_registered(cmd, CONTAINER_APPS_RP)

    if not certificate and not thumbprint:
        raise RequiredArgumentMissingError('Please specify at least one of parameters: --certificate and --thumbprint')
    certs = connected_env_list_certificates(cmd, name, resource_group_name, certificate=certificate, thumbprint=thumbprint)
    for cert in certs:
        try:
            ConnectedEnvCertificateClient.delete_certificate(cmd, resource_group_name, name, cert["name"])
            logger.warning('Successfully deleted certificate: {}'.format(cert["name"]))
        except Exception as e:
            handle_raw_exception(e)


def connected_env_show_storage(cmd, name, storage_name, resource_group_name):
    _validate_subscription_registered(cmd, CONTAINER_APPS_RP)

    try:
        return ConnectedEnvStorageClient.show(cmd, resource_group_name, name, storage_name)
    except CLIError as e:
        handle_raw_exception(e)


def connected_env_list_storages(cmd, name, resource_group_name):
    _validate_subscription_registered(cmd, CONTAINER_APPS_RP)

    try:
        return ConnectedEnvStorageClient.list(cmd, resource_group_name, name)
    except CLIError as e:
        handle_raw_exception(e)


def connected_env_create_or_update_storage(cmd, storage_name, resource_group_name, name, azure_file_account_name=None, azure_file_share_name=None, azure_file_account_key=None, access_mode=None):  # pylint: disable=redefined-builtin
    _validate_subscription_registered(cmd, CONTAINER_APPS_RP)

    r = None

    try:
        r = ConnectedEnvStorageClient.show(cmd, resource_group_name, name, storage_name)
    except:
        pass

    if r:
        logger.warning("Only AzureFile account keys can be updated. In order to change the AzureFile share name or account name, please delete this storage and create a new one.")

    storage_def = AzureFilePropertiesModel
    storage_def["accountKey"] = azure_file_account_key
    storage_def["accountName"] = azure_file_account_name
    storage_def["shareName"] = azure_file_share_name
    storage_def["accessMode"] = access_mode
    storage_envelope = {}
    storage_envelope["properties"] = {}
    storage_envelope["properties"]["azureFile"] = storage_def

    try:
        return ConnectedEnvStorageClient.create_or_update(cmd, resource_group_name, name, storage_name, storage_envelope)
    except CLIError as e:
        handle_raw_exception(e)


def connected_env_remove_storage(cmd, storage_name, name, resource_group_name):
    _validate_subscription_registered(cmd, CONTAINER_APPS_RP)

    try:
        return ConnectedEnvStorageClient.delete(cmd, resource_group_name, name, storage_name)
    except CLIError as e:
        handle_raw_exception(e)


def init_dapr_components(cmd, resource_group_name, environment_name, statestore="redis", pubsub="redis"):
    _validate_subscription_registered(cmd, CONTAINER_APPS_RP)

    if statestore not in DAPR_SUPPORTED_STATESTORE_DEV_SERVICE_LIST:
        raise ValidationError(
            f"Statestore {statestore} is not supported. Supported statestores are {', '.join(DAPR_SUPPORTED_STATESTORE_DEV_SERVICE_LIST)}."
        )
    if pubsub not in DAPR_SUPPORTED_PUBSUB_DEV_SERVICE_LIST:
        raise ValidationError(
            f"Pubsub {pubsub} is not supported. Supported pubsubs are {', '.join(DAPR_SUPPORTED_PUBSUB_DEV_SERVICE_LIST)}."
        )

    from ._dapr_utils import DaprUtils

    statestore_metadata = {"actorStateStore": "true"}
    statestore_service_id, statestore_component_id = DaprUtils.create_dapr_component_with_service(
        cmd, "state", statestore, resource_group_name, environment_name, component_metadata=statestore_metadata)

    if statestore == pubsub:
        # For cases where statestore and pubsub are the same, we don't need to create another service.
        # E.g. Redis can be used for both statestore and pubsub.
        pubsub_service_id, pubsub_component_id = DaprUtils.create_dapr_component_with_service(
            cmd, "pubsub", pubsub, resource_group_name, environment_name, service_id=statestore_service_id)
    else:
        pubsub_service_id, pubsub_component_id = DaprUtils.create_dapr_component_with_service(
            cmd, "pubsub", pubsub, resource_group_name, environment_name)

    return {
        "message": "Operation successful.",
        "resources": {
            # Remove duplicates for services like Redis, which can be used for both statestore and pubsub
            "devServices": list(set([statestore_service_id, pubsub_service_id])),
            "daprComponents": [statestore_component_id, pubsub_component_id]
        }
    }


def assign_env_managed_identity(cmd, name, resource_group_name, system_assigned=False, user_assigned=None, no_wait=False):
    _validate_subscription_registered(cmd, CONTAINER_APPS_RP)
    managed_env_def = None

    try:
        managed_env_def = ManagedEnvironmentPreviewClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except:
        pass

    if not managed_env_def:
        raise ResourceNotFoundError("The containerapp env '{}' does not exist".format(name))

    assign_system_identity = system_assigned
    if not user_assigned:
        user_assigned = []
    assign_user_identities = [x.lower() for x in user_assigned]
    if assign_user_identities:
        assign_id_size = len(assign_user_identities)

        # Remove duplicate identities that are passed and notify
        assign_user_identities = list(set(assign_user_identities))
        if assign_id_size != len(assign_user_identities):
            logger.warning("At least one identity was passed twice.")

    is_system_identity_changed = assign_system_identity
    to_add_user_assigned_identity = []

    # If identity not returned
    try:
        managed_env_def["identity"]
        managed_env_def["identity"]["type"]
    except:
        managed_env_def["identity"] = {}
        managed_env_def["identity"]["type"] = "None"
    payload = {"identity": {"type": managed_env_def["identity"]["type"]}}

    # check system identity is already assigned
    if assign_system_identity and managed_env_def["identity"]["type"].__contains__("SystemAssigned"):
        is_system_identity_changed = False
        logger.warning("System identity is already assigned to containerapp environment")

    # check user identity is already assigned
    if assign_user_identities:
        if "userAssignedIdentities" not in managed_env_def["identity"]:
            managed_env_def["identity"]["userAssignedIdentities"] = {}

        subscription_id = get_subscription_id(cmd.cli_ctx)

        for r in assign_user_identities:
            r = _ensure_identity_resource_id(subscription_id, resource_group_name, r).replace("resourceGroup", "resourcegroup")
            isExisting = False

            for old_user_identity in managed_env_def["identity"]["userAssignedIdentities"]:
                if old_user_identity.lower() == r.lower():
                    isExisting = True
                    logger.warning("User identity %s is already assigned to containerapp environment", old_user_identity)
                    break

            if not isExisting:
                to_add_user_assigned_identity.append(r)

    # no changes to containerapp environment
    if (not is_system_identity_changed) and (not to_add_user_assigned_identity):
        logger.warning("No managed identities changes to containerapp environment", old_user_identity)
        return managed_env_def

    if to_add_user_assigned_identity:
        payload["identity"]["userAssignedIdentities"] = {k: {} for k in to_add_user_assigned_identity}

    # Assign correct type
    try:
        if managed_env_def["identity"]["type"] != "None":
            payload["identity"]["type"] = managed_env_def["identity"]["type"]
            if managed_env_def["identity"]["type"] == "SystemAssigned" and assign_user_identities:
                payload["identity"]["type"] = "SystemAssigned,UserAssigned"
            if managed_env_def["identity"]["type"] == "UserAssigned" and assign_system_identity:
                payload["identity"]["type"] = "SystemAssigned,UserAssigned"

        else:
            if assign_system_identity and assign_user_identities:
                payload["identity"]["type"] = "SystemAssigned,UserAssigned"
            elif assign_system_identity:
                payload["identity"]["type"] = "SystemAssigned"
            elif assign_user_identities:
                payload["identity"]["type"] = "UserAssigned"
    except:
        # Always returns "type": "None" when CA has no previous identities
        pass

    try:
        r = ManagedEnvironmentPreviewClient.update(
            cmd=cmd, resource_group_name=resource_group_name, name=name, managed_environment_envelope=payload, no_wait=no_wait)
        return r["identity"]
    except Exception as e:
        handle_raw_exception(e)


def remove_env_managed_identity(cmd, name, resource_group_name, system_assigned=False, user_assigned=None, no_wait=False):
    _validate_subscription_registered(cmd, CONTAINER_APPS_RP)

    remove_system_identity = system_assigned
    remove_user_identities = user_assigned

    if user_assigned:
        remove_id_size = len(remove_user_identities)

        # Remove duplicate identities that are passed and notify
        remove_user_identities = list(set(remove_user_identities))
        if remove_id_size != len(remove_user_identities):
            logger.warning("At least one identity was passed twice.")

    managed_env_def = None
    # Get containerapp env properties of CA we are updating
    try:
        managed_env_def = ManagedEnvironmentPreviewClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except:
        pass

    if not managed_env_def:
        raise ResourceNotFoundError("The containerapp env '{}' does not exist".format(name))

    # If identity not returned
    try:
        managed_env_def["identity"]
        managed_env_def["identity"]["type"]
    except:
        managed_env_def["identity"] = {}
        managed_env_def["identity"]["type"] = "None"
    payload = {"identity": {"type": managed_env_def["identity"]["type"]}}

    if managed_env_def["identity"]["type"] == "None":
        raise InvalidArgumentValueError("The containerapp env {} has no system or user assigned identities.".format(name))

    if remove_system_identity:
        if managed_env_def["identity"]["type"] == "UserAssigned":
            raise InvalidArgumentValueError("The containerapp job {} has no system assigned identities.".format(name))
        payload["identity"]["type"] = ("None" if payload["identity"]["type"] == "SystemAssigned" else "UserAssigned")

    #  Remove all user identities
    if isinstance(user_assigned, list) and not user_assigned:
        logger.warning("remvoe all user identities.")
        payload["identity"]["type"] = ("None" if payload["identity"]["type"] == "UserAssigned" else "SystemAssigned")
        remove_user_identities = []

    if remove_user_identities:
        payload["identity"]["userAssignedIdentities"] = {}
        subscription_id = get_subscription_id(cmd.cli_ctx)
        try:
            managed_env_def["identity"]["userAssignedIdentities"]
        except:
            managed_env_def["identity"]["userAssignedIdentities"] = {}
        for remove_id in remove_user_identities:
            given_id = remove_id
            remove_id = _ensure_identity_resource_id(subscription_id, resource_group_name, remove_id)
            wasRemoved = False

            for old_user_identity in managed_env_def["identity"]["userAssignedIdentities"]:
                if old_user_identity.lower() == remove_id.lower():
                    payload["identity"]["userAssignedIdentities"][old_user_identity] = None
                    wasRemoved = True
                    break

            if not wasRemoved:
                raise InvalidArgumentValueError("The containerapp job does not have specified user identity '{}' assigned, so it cannot be removed.".format(given_id))

        # all user identities are removed
        if len(managed_env_def["identity"]["userAssignedIdentities"]) == len(payload["identity"]["userAssignedIdentities"]):
            payload["identity"].pop("userAssignedIdentities", None)
            payload["identity"]["type"] = ("None" if payload["identity"]["type"] == "UserAssigned" else "SystemAssigned")
        else:
            payload["identity"]["type"] = ("UserAssigned" if payload["identity"]["type"] == "UserAssigned" else "SystemAssigned,UserAssigned")
    try:
        r = ManagedEnvironmentPreviewClient.update(
            cmd=cmd, resource_group_name=resource_group_name, name=name, managed_environment_envelope=payload, no_wait=no_wait)
    except Exception as e:
        handle_raw_exception(e)

    try:
        return r["identity"]
    except:
        r["identity"] = {}
        r["identity"]["type"] = "None"
        return r["identity"]


def show_env_managed_identity(cmd, name, resource_group_name):
    _validate_subscription_registered(cmd, CONTAINER_APPS_RP)

    try:
        r = ManagedEnvironmentPreviewClient.show(cmd=cmd, resource_group_name=resource_group_name, name=name)
    except CLIError as e:
        handle_raw_exception(e)

    try:
        return r["identity"]
    except:
        r["identity"] = {}
        r["identity"]["type"] = "None"
        return r["identity"]


def list_java_components(cmd, environment_name, resource_group_name):
    raw_parameters = locals()
    java_component_decorator = JavaComponentDecorator(
        cmd=cmd,
        client=JavaComponentPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    return java_component_decorator.list()


def show_java_component(cmd, java_component_name, environment_name, resource_group_name, target_java_component_type):
    raw_parameters = locals()
    java_component_decorator = JavaComponentDecorator(
        cmd=cmd,
        client=JavaComponentPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    result = java_component_decorator.show()

    current_type = safe_get(result, "properties", "componentType")
    if current_type and target_java_component_type.lower() != current_type.lower():
        raise ResourceNotFoundError(f"(JavaComponentNotFound) JavaComponent '{java_component_name}' was not found.")

    return result


def delete_java_component(cmd, java_component_name, environment_name, resource_group_name, target_java_component_type, no_wait):
    raw_parameters = locals()
    java_component_decorator = JavaComponentDecorator(
        cmd=cmd,
        client=JavaComponentPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )

    result = None
    try:
        result = java_component_decorator.client.show(cmd, resource_group_name, environment_name, java_component_name)
    except Exception as e:
        handle_non_404_status_code_exception(e)

    current_type = safe_get(result, "properties", "componentType")
    if current_type and target_java_component_type.lower() != current_type.lower():
        raise ResourceNotFoundError(f"(JavaComponentNotFound) JavaComponent '{java_component_name}' was not found.")

    return java_component_decorator.delete()


def create_java_component(cmd, java_component_name, environment_name, resource_group_name, target_java_component_type, configuration, no_wait):
    raw_parameters = locals()
    java_component_decorator = JavaComponentDecorator(
        cmd=cmd,
        client=JavaComponentPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    java_component_decorator.construct_payload()
    return java_component_decorator.create()


def update_java_component(cmd, java_component_name, environment_name, resource_group_name, target_java_component_type, configuration, no_wait):
    raw_parameters = locals()
    java_component_decorator = JavaComponentDecorator(
        cmd=cmd,
        client=JavaComponentPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    java_component_decorator.construct_payload()
    return java_component_decorator.update()


def create_config_server_for_spring(cmd, java_component_name, environment_name, resource_group_name, configuration=None, no_wait=False):
    return create_java_component(cmd, java_component_name, environment_name, resource_group_name, JAVA_COMPONENT_CONFIG, configuration, no_wait)


def update_config_server_for_spring(cmd, java_component_name, environment_name, resource_group_name, configuration=None, no_wait=False):
    return update_java_component(cmd, java_component_name, environment_name, resource_group_name, JAVA_COMPONENT_CONFIG, configuration, no_wait)


def show_config_server_for_spring(cmd, java_component_name, environment_name, resource_group_name):
    return show_java_component(cmd, java_component_name, environment_name, resource_group_name, JAVA_COMPONENT_CONFIG)


def delete_config_server_for_spring(cmd, java_component_name, environment_name, resource_group_name, no_wait=False):
    return delete_java_component(cmd, java_component_name, environment_name, resource_group_name, JAVA_COMPONENT_CONFIG, no_wait)


def create_eureka_server_for_spring(cmd, java_component_name, environment_name, resource_group_name, configuration=None, no_wait=False):
    return create_java_component(cmd, java_component_name, environment_name, resource_group_name, JAVA_COMPONENT_EUREKA, configuration, no_wait)


def update_eureka_server_for_spring(cmd, java_component_name, environment_name, resource_group_name, configuration=None, no_wait=False):
    return update_java_component(cmd, java_component_name, environment_name, resource_group_name, JAVA_COMPONENT_EUREKA, configuration, no_wait)


def show_eureka_server_for_spring(cmd, java_component_name, environment_name, resource_group_name):
    return show_java_component(cmd, java_component_name, environment_name, resource_group_name, JAVA_COMPONENT_EUREKA)


def delete_eureka_server_for_spring(cmd, java_component_name, environment_name, resource_group_name, no_wait=False):
    return delete_java_component(cmd, java_component_name, environment_name, resource_group_name, JAVA_COMPONENT_EUREKA, no_wait)


def set_environment_telemetry_data_dog(cmd,
                                       name,
                                       resource_group_name,
                                       site=None,
                                       key=None,
                                       enable_open_telemetry_traces=None,
                                       enable_open_telemetry_metrics=None,
                                       no_wait=False):
    raw_parameters = locals()
    containerapp_env_telemetry_data_dog_decorator = ContainerappEnvTelemetryDataDogPreviewSetDecorator(
        cmd=cmd,
        client=ManagedEnvironmentPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_env_telemetry_data_dog_decorator.register_provider(CONTAINER_APPS_RP)

    containerapp_env_telemetry_data_dog_decorator.construct_payload()
    r = containerapp_env_telemetry_data_dog_decorator.update()
    
    return r


def delete_environment_telemetry_data_dog(cmd,
                                          name,
                                          resource_group_name,
                                          no_wait=False):
    raw_parameters = locals()
    raw_parameters["site"] = ""
    raw_parameters["key"] = ""
    raw_parameters["enable_open_telemetry_traces"] = False
    raw_parameters["enable_open_telemetry_metrics"] = False
    containerapp_env_telemetry_data_dog_decorator = ContainerappEnvTelemetryDataDogPreviewSetDecorator(
        cmd=cmd,
        client=ManagedEnvironmentPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_env_telemetry_data_dog_decorator.register_provider(CONTAINER_APPS_RP)

    containerapp_env_telemetry_data_dog_decorator.construct_payload()
    r = containerapp_env_telemetry_data_dog_decorator.update()
    
    return r


def show_environment_telemetry_data_dog(cmd,
                                        name,
                                        resource_group_name):
    raw_parameters = locals()

    containerapp_env_telemetry_data_dog_decorator = ContainerappEnvTelemetryDataDogPreviewSetDecorator(
        cmd=cmd,
        client=ManagedEnvironmentPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    
    containerapp_env_def = None
    try:
        containerapp_env_def = containerapp_env_telemetry_data_dog_decorator.show()
    except Exception as e:
        handle_non_404_status_code_exception(e)

    r = safe_get(containerapp_env_def, "properties", "openTelemetryConfiguration", "destinationsConfiguration", "dataDogConfiguration")
    if r is None:
        raise ValidationError("The containerapp environment '{}' does not have data dog enabled.".format(name))

    return containerapp_env_def


def set_environment_telemetry_app_insights(cmd,
                                           name,
                                           resource_group_name,
                                           connection_string=None,
                                           enable_open_telemetry_traces=None,
                                           enable_open_telemetry_logs=None,
                                           no_wait=False):
    raw_parameters = locals()
    containerapp_env_telemetry_app_insights_decorator = ContainerappEnvTelemetryAppInsightsPreviewSetDecorator(
        cmd=cmd,
        client=ManagedEnvironmentPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_env_telemetry_app_insights_decorator.register_provider(CONTAINER_APPS_RP)

    containerapp_env_telemetry_app_insights_decorator.construct_payload()
    r = containerapp_env_telemetry_app_insights_decorator.update()
    
    return r


def delete_environment_telemetry_app_insights(cmd,
                                              name,
                                              resource_group_name,
                                              no_wait=False):
    raw_parameters = locals()
    raw_parameters["connection_string"] = ""
    raw_parameters["enable_open_telemetry_traces"] = False
    raw_parameters["enable_open_telemetry_logs"] = False
    containerapp_env_telemetry_app_insights_decorator = ContainerappEnvTelemetryAppInsightsPreviewSetDecorator(
        cmd=cmd,
        client=ManagedEnvironmentPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_env_telemetry_app_insights_decorator.register_provider(CONTAINER_APPS_RP)

    containerapp_env_telemetry_app_insights_decorator.construct_payload()
    r = containerapp_env_telemetry_app_insights_decorator.update()
    
    return r


def show_environment_telemetry_app_insights(cmd,
                                            name,
                                            resource_group_name):
    raw_parameters = locals()

    containerapp_env_telemetry_app_insights_decorator = ContainerappEnvTelemetryAppInsightsPreviewSetDecorator(
        cmd=cmd,
        client=ManagedEnvironmentPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    
    containerapp_env_def = None
    try:
        containerapp_env_def = containerapp_env_telemetry_app_insights_decorator.show()
    except Exception as e:
        handle_non_404_status_code_exception(e)

    r = safe_get(containerapp_env_def, "properties", "appInsightsConfiguration")

    if r is None:
        raise ValidationError("The containerapp environment '{}' does not have app insights enabled.".format(name))

    if not containerapp_env_def:
        raise ResourceNotFoundError("The containerapp environment '{}' does not exist".format(name))

    return containerapp_env_def


def add_environment_telemetry_otlp(cmd,
                                   name,
                                   resource_group_name,
                                   otlp_name,
                                   endpoint,
                                   insecure=False,
                                   enable_open_telemetry_traces=False,
                                   enable_open_telemetry_logs=False,
                                   enable_open_telemetry_metrics=False,
                                   headers=None,
                                   no_wait=False):
    raw_parameters = locals()
    containerapp_env_telemetry_otlp_decorator = ContainerappEnvTelemetryOtlpPreviewSetDecorator(
        cmd=cmd,
        client=ManagedEnvironmentPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_env_telemetry_otlp_decorator.register_provider(CONTAINER_APPS_RP)

    r = {}

    try:
        r = containerapp_env_telemetry_otlp_decorator.show()
    except CLIError as e:
        handle_raw_exception(e)

    existing_otlps = safe_get(r, "properties", "openTelemetryConfiguration", "destinationsConfiguration", "otlpConfigurations")
    if existing_otlps is not None:
        otlp = [p for p in existing_otlps if p["name"].lower() == otlp_name.lower()]

        if otlp:
            raise ValidationError(f"Otlp entry with name --otlp-name {otlp_name} already exist, please retry with different name")

    containerapp_env_telemetry_otlp_decorator.construct_payload()
    r = containerapp_env_telemetry_otlp_decorator.update()
    
    return r


def update_environment_telemetry_otlp(cmd,
                                      name,
                                      resource_group_name,
                                      otlp_name,
                                      endpoint=None,
                                      insecure=None,
                                      enable_open_telemetry_traces=None,
                                      enable_open_telemetry_logs=None,
                                      enable_open_telemetry_metrics=None,
                                      headers=None,
                                      no_wait=False):
    raw_parameters = locals()
    containerapp_env_telemetry_otlp_decorator = ContainerappEnvTelemetryOtlpPreviewSetDecorator(
        cmd=cmd,
        client=ManagedEnvironmentPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_env_telemetry_otlp_decorator.register_provider(CONTAINER_APPS_RP)

    r = {}

    try:
        r = containerapp_env_telemetry_otlp_decorator.show()
    except Exception as e:
        handle_non_404_status_code_exception(e)

    existing_otlps = safe_get(r, "properties", "openTelemetryConfiguration", "destinationsConfiguration", "otlpConfigurations")
    if existing_otlps is not None:
        otlp = [p for p in existing_otlps if p["name"].lower() == otlp_name.lower()]

        if not otlp:
            raise ValidationError(f"Otlp entry with name --otlp-name {otlp_name} does not exist, please make sure the {otlp_name} already added")

    containerapp_env_telemetry_otlp_decorator.construct_payload()
    r = containerapp_env_telemetry_otlp_decorator.update()
    
    return r


def remove_environment_telemetry_otlp(cmd,
                                      name,
                                      resource_group_name,
                                      otlp_name,
                                      no_wait=False):
    raw_parameters = locals()
    raw_parameters["enable_open_telemetry_traces"] = False
    raw_parameters["enable_open_telemetry_logs"] = False
    raw_parameters["enable_open_telemetry_metrics"] = False
    containerapp_env_telemetry_otlp_decorator = ContainerappEnvTelemetryOtlpPreviewSetDecorator(
        cmd=cmd,
        client=ManagedEnvironmentPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    containerapp_env_telemetry_otlp_decorator.register_provider(CONTAINER_APPS_RP)

    containerapp_env_telemetry_otlp_decorator.construct_remove_payload()
    r = containerapp_env_telemetry_otlp_decorator.update()
    
    return r


def show_environment_telemetry_otlp(cmd,
                                    name,
                                    resource_group_name,
                                    otlp_name):
    raw_parameters = locals()

    containerapp_env_telemetry_otlp_decorator = ContainerappEnvTelemetryOtlpPreviewSetDecorator(
        cmd=cmd,
        client=ManagedEnvironmentPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    
    containerapp_env_def = None
    try:
        containerapp_env_def = containerapp_env_telemetry_otlp_decorator.show()
    except Exception as e:
        handle_non_404_status_code_exception(e)

    if not containerapp_env_def:
        raise ResourceNotFoundError("The containerapp environment '{}' does not exist".format(name))

    existing_otlps = safe_get(containerapp_env_def, "properties", "openTelemetryConfiguration", "destinationsConfiguration", "otlpConfigurations")
    if existing_otlps is not None:
        otlp = [p for p in existing_otlps if p["name"].lower() == otlp_name.lower()]

        if not otlp:
            raise ResourceNotFoundError(f"Otlp entry with name --otlp-name {otlp_name} does not exist, please retry with different name")
        
        existing_otlps = otlp
        safe_set(containerapp_env_def, "properties", "openTelemetryConfiguration", "destinationsConfiguration", "otlpConfigurations", value=existing_otlps)

    return containerapp_env_def


def list_environment_telemetry_otlp(cmd,
                                    name,
                                    resource_group_name):
    raw_parameters = locals()

    containerapp_env_telemetry_otlp_decorator = ContainerappEnvTelemetryOtlpPreviewSetDecorator(
        cmd=cmd,
        client=ManagedEnvironmentPreviewClient,
        raw_parameters=raw_parameters,
        models=CONTAINER_APPS_SDK_MODELS
    )
    
    containerapp_env_def = None
    try:
        containerapp_env_def = containerapp_env_telemetry_otlp_decorator.show()
    except Exception as e:
        handle_non_404_status_code_exception(e)

    return containerapp_env_def

