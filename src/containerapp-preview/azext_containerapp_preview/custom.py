# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from knack.log import get_logger

from ._clients import ContainerAppClient
from ._constants import CONTAINER_APPS_RP
from .containerapp_decorator import ContainerAppPreviewCreateDecorator, get_containerapp_base_decorator

logger = get_logger(__name__)


def show_containerapp(cmd, name, resource_group_name, show_secrets=False):
    raw_parameters = locals()
    containerapp_base_decorator = get_containerapp_base_decorator(cmd, raw_parameters)
    containerapp_base_decorator.validate_subscription_registered(CONTAINER_APPS_RP)
    return containerapp_base_decorator.show_containerapp()


def list_containerapp(cmd, resource_group_name=None, managed_env=None):
    raw_parameters = locals()
    containerapp_base_decorator = get_containerapp_base_decorator(cmd, raw_parameters)
    containerapp_base_decorator.validate_subscription_registered(CONTAINER_APPS_RP)
    return containerapp_base_decorator.list_containerapp()


def delete_containerapp(cmd, name, resource_group_name, no_wait=False):
    raw_parameters = locals()
    containerapp_base_decorator = get_containerapp_base_decorator(cmd, raw_parameters)
    containerapp_base_decorator.validate_subscription_registered(CONTAINER_APPS_RP)
    return containerapp_base_decorator.delete_containerapp()


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
                        environment_type="managed"):
    raw_parameters = locals()
    containerapp_preview_create_decorator = ContainerAppPreviewCreateDecorator(
        cmd=cmd,
        client=ContainerAppClient,
        raw_parameters=raw_parameters,
        models="azext_containerapp_preview._sdk_models"
    )
    containerapp_preview_create_decorator.register_provider(CONTAINER_APPS_RP)
    containerapp_preview_create_decorator.validate_arguments()
    containerapp_preview_create_decorator.construct_containerapp()
    r = containerapp_preview_create_decorator.create_containerapp()
    containerapp_preview_create_decorator.construct_containerapp_for_post_process(r)
    r = containerapp_preview_create_decorator.post_process_containerapp(r)
    return r
