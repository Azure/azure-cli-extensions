# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from knack.log import get_logger
from enum import Enum
from typing import Any, Dict
from msrestazure.tools import parse_resource_id

from azure.cli.core.commands import AzCliCommand
from azure.cli.core.azclierror import ValidationError, CLIInternalError, RequiredArgumentMissingError
from azure.cli.command_modules.containerapp.base_resource import BaseResource
from azure.cli.command_modules.containerapp._models import (ContainerResources as ContainerResourcesModel,
                                                            Container as ContainerModel)
from azure.cli.command_modules.containerapp._constants import HELLO_WORLD_IMAGE
from azure.cli.command_modules.containerapp._utils import (parse_env_var_flags, parse_secret_flags, store_as_secret_and_return_secret_ref,
                                                            _ensure_location_allowed, CONTAINER_APPS_RP, validate_container_app_name,
                                                           safe_set)
from azure.cli.command_modules.containerapp._clients import ManagedEnvironmentClient
from azure.cli.command_modules.containerapp._client_factory import handle_non_404_status_code_exception


from ._models import SessionPool as SessionPoolModel
from ._client_factory import handle_raw_exception
from ._utils import AppType

logger = get_logger(__name__)


class ContainerType(Enum):
    PythonLTS = 0
    CustomContainer = 2


class SessionPoolPreviewDecorator(BaseResource):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.session_pool_def = SessionPoolModel

    def get_argument_name(self):
        return self.get_param('name')

    def get_argument_resource_group_name(self):
        return self.get_param('resource_group_name')

    def get_argument_location(self):
        return self.get_param("location")

    def get_argument_managed_env(self):
        return self.get_param('managed_env')

    def get_argument_container_type(self):
        return self.get_param('container_type')

    def set_argument_container_type(self, container_type):
        return self.set_param('container_type', container_type)

    def get_argument_cooldown_period_in_seconds(self):
        return self.get_param('cooldown_period')

    def set_argument_cooldown_period_in_seconds(self, period):
        return self.set_param('cooldown_period', period)

    def get_argument_secrets(self):
        return self.get_param('secrets')

    def get_argument_network_status(self):
        return self.get_param('network_status')

    def set_argument_network_status(self, network_status):
        self.set_param('network_status', network_status)

    def get_argument_max_concurrent_sessions(self):
        return self.get_param('max_concurrent_sessions')

    def set_argument_max_concurrent_sessions(self, max_concurrent_sessions):
        self.set_param('max_concurrent_sessions', max_concurrent_sessions)

    def get_argument_ready_session_instances(self):
        return self.get_param('ready_session_instances')

    def set_argument_ready_session_instances(self, ready_session_instances):
        self.set_param('ready_session_instances', ready_session_instances)

    def get_argument_image(self):
        return self.get_param('image')

    def get_argument_container_name(self):
        return self.get_param('container_name')

    def get_argument_cpu(self):
        return self.get_param('cpu')

    def get_argument_memory(self):
        return self.get_param('memory')

    def get_argument_env_vars(self):
        return self.get_param('env_vars')

    def get_argument_startup_command(self):
        return self.get_param('startup_command')

    def get_argument_args(self):
        return self.get_param('args')

    def get_argument_target_port(self):
        return self.get_param('target_port')

    def get_argument_registry_server(self):
        return self.get_param("registry_server")

    def get_argument_registry_pass(self):
        return self.get_param("registry_pass")

    def get_argument_registry_user(self):
        return self.get_param("registry_user")

    def get_environment_client(self):
        return ManagedEnvironmentClient

    def set_up_secrets(self):
        secrets_def = None
        if self.get_argument_secrets() is not None:
            secrets_def = parse_secret_flags(self.get_argument_secrets())
        return secrets_def

    def set_up_registry_auth_configuration(self, secrets_def):
        registry_def = None
        if self.get_argument_registry_server() is not None:
            registry_def = {}
            registry_def["registryServer"] = self.get_argument_registry_server()
            registry_def["username"] = self.get_argument_registry_user()

            if secrets_def is None:
                secrets_def = []
            registry_def["passwordSecretRef"] = store_as_secret_and_return_secret_ref(secrets_def,
                                                                                      self.get_argument_registry_user(),
                                                                                      self.get_argument_registry_server(),
                                                                                      self.get_argument_registry_pass())
        return registry_def


class SessionPoolCreateDecorator(SessionPoolPreviewDecorator):
    def validate_arguments(self):
        validate_container_app_name(self.get_argument_name(), AppType.SessionPool.name)
        container_type = self.get_argument_container_type()
        environment_name = self.get_argument_managed_env()

        location = self.get_argument_location()
        _ensure_location_allowed(self.cmd, location, CONTAINER_APPS_RP, "sessionPools")

        if container_type == ContainerType.CustomContainer.name:
            if environment_name is None:
                raise RequiredArgumentMissingError(f'Must provide environment name when container type is {ContainerType.CustomContainer.name}')
        else:
            if environment_name is not None:
                raise ValidationError(f"Do not pass environment name when using container type {container_type}")

    def construct_payload(self):
        self.session_pool_def["location"] = self.get_argument_location()

        # We only support 'Dynamic' type in CLI
        self.session_pool_def["properties"]["poolManagementType"] = "Dynamic"
        self.session_pool_def["properties"]["environmentId"] = self.get_argument_managed_env()
        if self.get_argument_container_type() is None:
            self.set_argument_container_type(ContainerType.PythonLTS.name)
        self.session_pool_def["properties"]["containerType"] = self.get_argument_container_type()

        dynamic_pool_def = self.set_up_dynamic_configuration()
        session_network_def = self.set_up_network_configuration()
        session_scale_def = self.set_up_scale_configuration()
        secrets_def = self.set_up_secrets()

        # CustomerContainerTemplate
        customer_container_template = None
        if self.get_argument_container_type() == ContainerType.CustomContainer.name:
            customer_container_template = {}
            self.validate_environment()

            container_def = self.set_up_container()
            ingress_def = self.set_up_ingress()
            registry_def = self.set_up_registry_auth_configuration(secrets_def)

            customer_container_template["containers"] = [container_def]
            customer_container_template["ingress"] = ingress_def
            customer_container_template["registryCredentials"] = registry_def

        safe_set(self.session_pool_def, "properties", "customContainerTemplate", value=customer_container_template)
        safe_set(self.session_pool_def, "properties", "secrets", value=secrets_def)
        safe_set(self.session_pool_def, "properties", "dynamicPoolConfiguration", value=dynamic_pool_def)
        safe_set(self.session_pool_def, "properties", "sessionNetworkConfiguration", value=session_network_def)
        safe_set(self.session_pool_def, "properties", "scaleConfiguration", value=session_scale_def)

    def set_up_dynamic_configuration(self):
        dynamic_pool_def = {}
        dynamic_pool_def["executionType"] = "Timed"
        if self.get_argument_cooldown_period_in_seconds() is None:
            self.set_argument_cooldown_period_in_seconds(300)
        dynamic_pool_def["cooldownPeriodInSeconds"] = self.get_argument_cooldown_period_in_seconds()
        return dynamic_pool_def

    def set_up_network_configuration(self):
        session_network_def = {}
        if self.get_argument_network_status() is None:
            self.set_argument_network_status("EgressDisabled")
        session_network_def['status'] = self.get_argument_network_status()
        return session_network_def

    def set_up_scale_configuration(self):
        session_scale_def = {}
        if self.get_argument_max_concurrent_sessions() is None:
            self.set_argument_max_concurrent_sessions(10)
        if self.get_argument_ready_session_instances() is None:
            self.set_argument_ready_session_instances(5)
        session_scale_def["maxConcurrentSessions"] = self.get_argument_max_concurrent_sessions()
        session_scale_def["readySessionInstances"] = self.get_argument_ready_session_instances()
        return session_scale_def

    def set_up_resource(self):
        resources_def = None
        if self.get_argument_cpu() is not None or self.get_argument_memory() is not None:
            resources_def = ContainerResourcesModel
            resources_def["cpu"] = self.get_argument_cpu()
            resources_def["memory"] = self.get_argument_memory()
        return resources_def

    def set_up_container(self):
        container_def = ContainerModel
        container_def["name"] = self.get_argument_container_name() if self.get_argument_container_name() else self.get_argument_name()
        container_def["image"] = self.get_argument_image() if self.get_argument_image() else HELLO_WORLD_IMAGE
        if self.get_argument_env_vars() is not None:
            container_def["env"] = parse_env_var_flags(self.get_argument_env_vars())
        if self.get_argument_startup_command() is not None:
            container_def["command"] = self.get_argument_startup_command()
        if self.get_argument_args() is not None:
            container_def["args"] = self.get_argument_args()
        container_def["resources"] = self.set_up_resource()
        return container_def

    def set_up_ingress(self):
        if self.get_argument_target_port() is None:
            raise RequiredArgumentMissingError("Required argument 'target_port' is not specified.")
        ingress_def = {}
        ingress_def["targetPort"] = self.get_argument_target_port()
        return ingress_def

    def validate_environment(self):
        # Validate managed environment
        parsed_managed_env = parse_resource_id(self.get_argument_managed_env())
        managed_env_name = parsed_managed_env['name']
        managed_env_rg = parsed_managed_env['resource_group']
        try:
            managed_env_info = self.get_environment_client().show(cmd=self.cmd, resource_group_name=managed_env_rg,
                                                                  name=managed_env_name)
        except Exception as e:
            handle_non_404_status_code_exception(e)

    def create(self):
        try:
            return self.client.create(
                cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                name=self.get_argument_name(),
                session_pool_envelope=self.session_pool_def, no_wait=self.get_argument_no_wait())
        except Exception as e:
            handle_raw_exception(e)


class SessionPoolUpdateDecorator(SessionPoolPreviewDecorator):
    def update(self):
        try:
            logger.warning(self.session_pool_def)
            return self.client.update(
                cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                name=self.get_argument_name(),
                session_pool_envelope=self.session_pool_def, no_wait=self.get_argument_no_wait())
        except Exception as e:
            handle_raw_exception(e)

    def construct_payload(self):
        self.session_pool_def = {}
        self.session_pool_def["location"] = self.get_argument_location()

        dynamic_pool_def = self.set_up_dynamic_configuration()
        session_network_def = self.set_up_network_configuration()
        session_scale_def = self.set_up_scale_configuration()
        secrets_def = self.set_up_secrets()

        # CustomerContainerTemplate
        customer_container_template = {}
        container_def = self.set_up_container()
        ingress_def = self.set_up_ingress()
        registry_def = self.set_up_registry_auth_configuration(secrets_def)
        if registry_def is None and ingress_def is None and container_def is None:
            customer_container_template = None
        else:
            if container_def is not None:
                customer_container_template["containers"] = [container_def]
            if ingress_def is not None:
                customer_container_template["ingress"] = ingress_def
            if registry_def is not None:
                customer_container_template["registryCredentials"] = registry_def

        if self.get_argument_container_type() is not None:
            safe_set(self.session_pool_def, "properties", "containerType", value=self.get_argument_container_type())
        if self.get_argument_managed_env() is not None:
            safe_set(self.session_pool_def, "properties", "environmentId", value=self.get_argument_managed_env())
        if customer_container_template is not None:
            safe_set(self.session_pool_def, "properties", "customContainerTemplate", value=customer_container_template)
        if secrets_def is not None:
            safe_set(self.session_pool_def, "properties", "secrets", value=secrets_def)
        if dynamic_pool_def is not None:
            safe_set(self.session_pool_def, "properties", "dynamicPoolConfiguration", value=dynamic_pool_def)
        if session_network_def is not None:
            safe_set(self.session_pool_def, "properties", "sessionNetworkConfiguration", value=session_network_def)
        if session_scale_def is not None:
            safe_set(self.session_pool_def, "properties", "scaleConfiguration", value=session_scale_def)

    def set_up_dynamic_configuration(self):
        dynamic_pool_def = None
        if self.get_argument_cooldown_period_in_seconds() is not None:
            dynamic_pool_def = {}
            dynamic_pool_def["cooldownPeriodInSeconds"] = self.get_argument_cooldown_period_in_seconds()
        return dynamic_pool_def

    def set_up_network_configuration(self):
        session_network_def = None
        if self.get_argument_network_status() is not None:
            session_network_def = {}
            session_network_def['status'] = self.get_argument_network_status()
        return session_network_def

    def set_up_scale_configuration(self):
        session_scale_def = None
        if self.get_argument_max_concurrent_sessions() is not None or self.get_argument_ready_session_instances() is not None:
            session_scale_def = {}
            if self.get_argument_max_concurrent_sessions() is not None:
                session_scale_def["maxConcurrentSessions"] = self.get_argument_max_concurrent_sessions()
            if self.get_argument_ready_session_instances():
                session_scale_def["readySessionInstances"] = self.get_argument_ready_session_instances()
        return session_scale_def

    def set_up_container(self):
        container_def = {}
        container_has_update = False
        if self.get_argument_container_name() is not None:
            container_def["name"] = self.get_argument_container_name()
            container_has_update = True
        if self.get_argument_image() is not None:
            container_def["image"] = self.get_argument_image()
            container_has_update = True
        if self.get_argument_env_vars() is not None:
            container_def["env"] = parse_env_var_flags(self.get_argument_env_vars())
            container_has_update = True
        if self.get_argument_startup_command() is not None:
            container_def["command"] = self.get_argument_startup_command()
            container_has_update = True
        if self.get_argument_args() is not None:
            container_def["args"] = self.get_argument_args()
            container_has_update = True
        if self.get_argument_cpu() is not None or self.get_argument_memory() is not None:
            resources_def = ContainerResourcesModel
            if self.get_argument_cpu() is not None:
                resources_def["cpu"] = self.get_argument_cpu()
            if self.get_argument_memory() is not None:
                resources_def["memory"] = self.get_argument_memory()
            container_def["resources"] = resources_def
            container_has_update = True
        if not container_has_update:
            container_def = None
        return container_def

    def set_up_ingress(self):
        ingress_def = None
        if self.get_argument_target_port() is not None:
            ingress_def = {}
            ingress_def["targetPort"] = self.get_argument_target_port()
        return ingress_def
