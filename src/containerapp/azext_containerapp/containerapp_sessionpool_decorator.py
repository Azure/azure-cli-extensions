# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, broad-except, logging-format-interpolation, too-many-public-methods

import uuid
from copy import deepcopy
from knack.log import get_logger
from enum import Enum
from typing import Any, Dict
from msrestazure.tools import parse_resource_id
from azure.cli.core.util import send_raw_request
from azure.cli.core.azclierror import HTTPError
import json

from azure.cli.core.commands import AzCliCommand
from azure.cli.core.azclierror import ValidationError, RequiredArgumentMissingError
from azure.cli.command_modules.containerapp.base_resource import BaseResource
from azure.cli.command_modules.containerapp._models import (ContainerResources as ContainerResourcesModel,
                                                            Container as ContainerModel)
from azure.cli.command_modules.containerapp._constants import HELLO_WORLD_IMAGE
from azure.cli.command_modules.containerapp._utils import (parse_env_var_flags, parse_secret_flags,
                                                           store_as_secret_and_return_secret_ref,
                                                           _ensure_location_allowed, CONTAINER_APPS_RP,
                                                           validate_container_app_name,
                                                           safe_set, safe_get)
from azure.cli.command_modules.containerapp._clients import ManagedEnvironmentClient
from azure.cli.command_modules.containerapp._client_factory import handle_non_404_status_code_exception
from azure.cli.core.commands.client_factory import get_subscription_id

from ._models import SessionPool as SessionPoolModel
from ._client_factory import handle_raw_exception
from ._utils import AppType

SESSION_CREATOR_ROLE_ID = "0fb8eba5-a2bb-4abe-b1c1-49dfad359bb0"

logger = get_logger(__name__)


class ContainerType(Enum):
    PythonLTS = 0
    CustomContainer = 2


class SessionPoolPreviewDecorator(BaseResource):
    def __init__(self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str):
        super().__init__(cmd, client, raw_parameters, models)
        self.session_pool_def = deepcopy(SessionPoolModel)
        self.existing_pool_def = None

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

    # pylint: disable=no-self-use
    def get_environment_client(self):
        return ManagedEnvironmentClient


class SessionPoolCreateDecorator(SessionPoolPreviewDecorator):
    def validate_arguments(self):
        validate_container_app_name(self.get_argument_name(), AppType.SessionPool.name)
        container_type = self.get_argument_container_type()
        environment_name = self.get_argument_managed_env()

        location = self.get_argument_location()
        _ensure_location_allowed(self.cmd, location, CONTAINER_APPS_RP, "sessionPools")

        if container_type == ContainerType.CustomContainer.name:
            if environment_name is None:
                raise RequiredArgumentMissingError(
                    f'Must provide environment name when container type is {ContainerType.CustomContainer.name}')
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
            registry_def, updated_secret_def = self.set_up_registry_auth_configuration(secrets_def)
            secrets_def = updated_secret_def

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
        container_def["name"] = self.get_argument_container_name() if self.get_argument_container_name() else self.get_argument_name().lower()
        container_def["image"] = self.get_argument_image() if self.get_argument_image() else HELLO_WORLD_IMAGE
        if self.get_argument_env_vars() is not None:
            container_def["env"] = parse_env_var_flags(self.get_argument_env_vars())
        if self.get_argument_startup_command() is not None:
            container_def["command"] = self.get_argument_startup_command()
        if self.get_argument_args() is not None:
            container_def["args"] = self.get_argument_args()
        container_def["resources"] = self.set_up_resource()
        return container_def

    def set_up_secrets(self):
        secrets_def = None
        if self.get_argument_secrets() is not None:
            secrets_def = parse_secret_flags(self.get_argument_secrets())
        return secrets_def

    def set_up_registry_auth_configuration(self, secrets_def):
        registry_def = None
        if self.get_argument_registry_server() is not None:
            registry_def = {}
            registry_def["server"] = self.get_argument_registry_server()
            registry_def["username"] = self.get_argument_registry_user()

            if secrets_def is None:
                secrets_def = []
            registry_def["passwordSecretRef"] = store_as_secret_and_return_secret_ref(secrets_def,
                                                                                      self.get_argument_registry_user(),
                                                                                      self.get_argument_registry_server(),
                                                                                      self.get_argument_registry_pass())
        return registry_def, secrets_def

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
            self.get_environment_client().show(cmd=self.cmd, resource_group_name=managed_env_rg, name=managed_env_name)
        except Exception as e:
            handle_non_404_status_code_exception(e)

    def assign_session_create_role(self):
        # try to add user as session pool creator role to the session pool
        try:
            # get princpalId of the user
            principal_id_url = "https://graph.microsoft.com/v1.0/me"
            principal_id = send_raw_request(self.cmd.cli_ctx, "GET", principal_id_url).json()['id']
            management_hostname = self.cmd.cli_ctx.cloud.endpoints.resource_manager
            scope = "subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/sessionPools/{}".format(
                get_subscription_id(self.cmd.cli_ctx),
                self.get_argument_resource_group_name(),
                self.get_argument_name())
            role_assignment_fmt = "{}/{}/providers/Microsoft.Authorization/roleAssignments/{}?api-version=2022-04-01"
            role_assignment_url = role_assignment_fmt.format(
                management_hostname.strip('/'),
                scope,
                uuid.uuid4()
            )
            role_definition_id = "/{}/providers/Microsoft.Authorization/roleDefinitions/{}".format(
                scope,
                SESSION_CREATOR_ROLE_ID)
            send_raw_request(self.cmd.cli_ctx, "PUT", role_assignment_url, body=json.dumps({
                "properties": {
                    "roleDefinitionId": role_definition_id,
                    "principalId": principal_id
                }
            }))
        # if anything goes wrong print error but do not throw error
        except Exception as e:
            try:
                if isinstance(e, HTTPError):
                    error_code = json.loads(e.response.text)["error"]["code"]
                    if error_code == "RoleAssignmentExists":
                        pass
                else:
                    raise Exception(e)  # pylint: disable=broad-exception-raised
            except:  # pylint: disable=bare-except
                logger.warning("Could not add user as session pool creator role to the session pool, please follow the docs https://learn.microsoft.com/en-us/azure/container-apps/sessions-code-interpreter?tabs=azure-cli#authentication to add the needed roll for authentication")
                logger.warning(e)

    def create(self):
        try:
            create_result = self.client.create(
                cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                name=self.get_argument_name(),
                session_pool_envelope=self.session_pool_def, no_wait=self.get_argument_no_wait())
            try:
                self.assign_session_create_role()
            except Exception as e:
                logger.warning(e)
            return create_result
        except Exception as e:
            handle_raw_exception(e)


class SessionPoolUpdateDecorator(SessionPoolPreviewDecorator):
    def update(self):
        try:
            return self.client.update(
                cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(),
                name=self.get_argument_name(),
                session_pool_envelope=self.session_pool_def, no_wait=self.get_argument_no_wait())
        except Exception as e:
            handle_raw_exception(e)

    def construct_payload(self):
        self.session_pool_def = {}
        self.existing_pool_def = self.client.show(cmd=self.cmd,
                                                  resource_group_name=self.get_argument_resource_group_name(),
                                                  name=self.get_argument_name())

        if ((self.get_argument_container_type() is not None and safe_get(self.existing_pool_def, "properties", "containerType").lower() == self.get_argument_container_type().lower()) or
                (self.get_argument_managed_env() is not None and safe_get(self.existing_pool_def, "properties", "environmentId").lower() == self.get_argument_managed_env().lower())):
            raise ValidationError("containerType and environmentId cannot be updated.")

        self.set_up_dynamic_configuration()
        self.set_up_network_configuration()
        self.set_up_scale_configuration()
        self.set_up_secrets()
        self.set_up_custom_container_template(safe_get(self.session_pool_def, "properties", "secrets"))

    def set_up_dynamic_configuration(self):
        if self.get_argument_cooldown_period_in_seconds() is not None:
            dynamic_pool_def = {}
            dynamic_pool_def["cooldownPeriodInSeconds"] = self.get_argument_cooldown_period_in_seconds()
            safe_set(self.session_pool_def, "properties", "dynamicPoolConfiguration", value=dynamic_pool_def)

    def set_up_network_configuration(self):
        if self.get_argument_network_status() is not None:
            session_network_def = {}
            session_network_def['status'] = self.get_argument_network_status()
            safe_set(self.session_pool_def, "properties", "sessionNetworkConfiguration", value=session_network_def)

    def set_up_scale_configuration(self):
        if self.get_argument_max_concurrent_sessions() is not None or self.get_argument_ready_session_instances() is not None:
            session_scale_def = {}
            if self.get_argument_max_concurrent_sessions() is not None:
                session_scale_def["maxConcurrentSessions"] = self.get_argument_max_concurrent_sessions()
            if self.get_argument_ready_session_instances():
                session_scale_def["readySessionInstances"] = self.get_argument_ready_session_instances()
            safe_set(self.session_pool_def, "properties", "scaleConfiguration", value=session_scale_def)

    def set_up_custom_container_template(self, secrets_def):
        if self.has_registry_change() or self.has_container_change() or self.has_target_port_change():
            customer_container_template = self.existing_pool_def["properties"]["customContainerTemplate"]

            if (self.has_container_change() and self.get_argument_container_name() is None and
                    len(safe_get(customer_container_template, "containers")) > 1):
                raise ValidationError("Must provide container name if multiple containers provided")

            self.set_up_container(customer_container_template)
            self.set_up_ingress(customer_container_template)
            self.set_up_registry_auth_configuration(secrets_def, customer_container_template)

            safe_set(self.session_pool_def, "properties", "customContainerTemplate", value=customer_container_template)

    def set_up_container(self, customer_container_template):
        container_def = None
        containers = customer_container_template["containers"]
        if len(containers) == 1:
            container_def = containers[0]
        else:
            for i, c in containers:
                if c['name'].lower() == self.get_argument_container_name().lower():
                    container_def = containers[i]
            if container_def is None:
                raise ValidationError(f"Cannot find the corresponding container for container name {self.get_argument_container_name()}")

        # Update those properties when set, otherwise, we keep the original ones
        if self.get_argument_container_name() is not None:
            container_def["name"] = self.get_argument_container_name()
        if self.get_argument_image() is not None:
            container_def["image"] = self.get_argument_image()
        if self.get_argument_env_vars() is not None:
            container_def["env"] = parse_env_var_flags(self.get_argument_env_vars())
        if self.get_argument_startup_command() is not None:
            container_def["command"] = self.get_argument_startup_command()
        if self.get_argument_args() is not None:
            container_def["args"] = self.get_argument_args()
        if self.get_argument_cpu() is not None or self.get_argument_memory() is not None:
            if self.get_argument_cpu() is not None:
                container_def["resources"]["cpu"] = self.get_argument_cpu()
            if self.get_argument_memory() is not None:
                container_def["resources"]["memory"] = self.get_argument_memory()
        return container_def

    def set_up_registry_auth_configuration(self, secrets_def, customer_container_template):
        if self.get_argument_registry_server() is not None:
            safe_set(customer_container_template, "registryCredentials", "server", value=self.get_argument_registry_server())
        if self.get_argument_registry_user() is not None:
            safe_set(customer_container_template, "registryCredentials", "username", value=self.get_argument_registry_user())
        if secrets_def is None:
            secrets_def = []
        if self.get_argument_registry_pass() is not None:
            original_secrets = self.existing_pool_def["properties"]["secrets"]
            original_secrets_names = []
            for secret in original_secrets:
                original_secrets_names.append(secret["name"])
            safe_set(customer_container_template, "registryCredentials", "passwordSecretRef",
                     value=store_as_secret_and_return_secret_ref(secrets_def,
                                                                 customer_container_template["registryCredentials"]["username"],
                                                                 customer_container_template["registryCredentials"]["server"],
                                                                 self.get_argument_registry_pass()))
            new_secret_names = []
            for secret in secrets_def:
                new_secret_names.append(secret["name"])
            deleted_secrets = set(original_secrets_names).difference(new_secret_names)
            if len(deleted_secrets) > 0:
                logger.warning("the following secrets are going to be deleted: " + str(deleted_secrets) + " If this is not the intended behavior, please add the missing secrets into the --secrets flag.")  # pylint: disable=logging-not-lazy

            # Update the secrets to the patch payload.
            if len(secrets_def) > 0:
                safe_set(self.session_pool_def, "properties", "secrets", value=secrets_def)

    def set_up_ingress(self, customer_container_template):
        if self.get_argument_target_port() is not None:
            safe_set(customer_container_template, "ingress", "targetPort", value=self.get_argument_target_port())

    def set_up_secrets(self):
        if self.get_argument_secrets() is not None:
            secrets_def = parse_secret_flags(self.get_argument_secrets())
            safe_set(self.session_pool_def, "properties", "secrets", value=secrets_def)

    def has_container_change(self):
        return (self.get_argument_container_name() is not None or
                self.get_argument_image() is not None or
                self.get_argument_cpu() is not None or
                self.get_argument_memory() is not None or
                self.get_argument_env_vars() is not None or
                self.get_argument_args() is not None or
                self.get_argument_startup_command() is not None)

    def has_registry_change(self):
        return (self.get_argument_registry_server() is not None or
                self.get_argument_registry_user() is not None or
                self.get_argument_registry_pass() is not None)

    def has_target_port_change(self):
        return self.get_argument_target_port() is not None
