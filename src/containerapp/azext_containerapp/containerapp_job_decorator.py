# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, broad-except, logging-format-interpolation, too-many-branches, too-many-boolean-expressions, no-else-return, logging-fstring-interpolation, too-many-locals

from typing import Dict, Any
from urllib.parse import urlparse

from azure.cli.core.azclierror import (
    RequiredArgumentMissingError, ValidationError, InvalidArgumentValueError)
from azure.cli.command_modules.containerapp.containerapp_job_decorator import ContainerAppJobCreateDecorator, \
    ContainerAppJobDecorator
from azure.cli.command_modules.containerapp._utils import safe_get, _convert_object_from_snake_to_camel_case, \
    _object_to_dict, _remove_additional_attributes, _remove_readonly_attributes, clean_null_values, \
    _populate_secret_values, _add_or_update_tags, ensure_workload_profile_supported, _add_or_update_env_vars, \
    parse_env_var_flags, _remove_env_vars, _get_acr_cred, store_as_secret_and_return_secret_ref, \
    parse_metadata_flags, parse_auth_flags, safe_set, _ensure_identity_resource_id, is_registry_msi_system, \
    create_acrpull_role_assignment, _ensure_location_allowed, get_default_workload_profile_name_from_env, \
    _infer_acr_credentials, set_managed_identity, parse_secret_flags, validate_container_app_name, AppType
from azure.cli.command_modules.containerapp._constants import (CONTAINER_APPS_RP, HELLO_WORLD_IMAGE)
from azure.cli.command_modules.containerapp._models import (
    ManualTriggerConfig as ManualTriggerModel,
    ScheduleTriggerConfig as ScheduleTriggerModel,
    EventTriggerConfig as EventTriggerModel,
    JobScale as JobScaleModel,
    JobConfiguration as JobConfigurationModel,
    JobTemplate as JobTemplateModel,
    ManagedServiceIdentity as ManagedServiceIdentityModel,
)
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.core.commands import AzCliCommand
from azure.core.exceptions import DeserializationError, ResourceNotFoundError
from azure.mgmt.core.tools import parse_resource_id, is_valid_resource_id

from knack.log import get_logger

from ._client_factory import handle_raw_exception, handle_non_404_status_code_exception
from ._constants import CONNECTED_ENVIRONMENT_RESOURCE_TYPE, \
    MANAGED_ENVIRONMENT_TYPE, CONNECTED_ENVIRONMENT_TYPE, ACR_IMAGE_SUFFIX
from ._clients import ManagedEnvironmentClient, ConnectedEnvironmentClient, ManagedEnvironmentPreviewClient
from ._decorator_utils import (create_deserializer,
                               process_loaded_yaml,
                               load_yaml_file)
from ._models import (
    RegistryCredentials as RegistryCredentialsModel,
    ContainerResources as ContainerResourcesModel,
    Container as ContainerModel,
    ScaleRule as ScaleRuleModel)
from ._utils import is_registry_msi_system_environment, env_has_managed_identity
from ._validators import validate_create

logger = get_logger(__name__)


class ContainerAppJobUpdateDecorator(ContainerAppJobDecorator):
    def __init__(
        self, cmd: AzCliCommand, client: Any, raw_parameters: Dict, models: str
    ):
        super().__init__(cmd, client, raw_parameters, models)
        self.containerappjob_def = {}
        self.new_containerappjob = {}

    def set_argument_container_name(self, container_name):
        self.set_param("container_name", container_name)

    def get_argument_set_env_vars(self):
        return self.get_param("set_env_vars")

    def get_argument_remove_env_vars(self):
        return self.get_param("remove_env_vars")

    def get_argument_replace_env_vars(self):
        return self.get_param("replace_env_vars")

    def get_argument_remove_all_env_vars(self):
        return self.get_param("remove_all_env_vars")

    def list_secrets(self, show_values=False):
        containerappjob_def = None
        try:
            containerappjob_def = self.client.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name())
        except Exception as e:
            handle_non_404_status_code_exception(e)

        if not containerappjob_def:
            raise ResourceNotFoundError("The containerapp '{}' does not exist".format(self.get_argument_name()))

        if not show_values:
            return safe_get(containerappjob_def, "properties", "configuration", "secrets", default=[])

        try:
            return self.client.list_secrets(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name())["value"]
        except Exception as e:
            handle_non_404_status_code_exception(e)

    def set_up_get_existing_secrets(self):
        if "secrets" not in self.containerappjob_def["properties"]["configuration"]:
            safe_set(self.containerappjob_def, "properties", "configuration", "secrets", value=[])
            safe_set(self.new_containerappjob, "properties", "configuration", "secrets", value=[])
        else:
            secrets = None
            try:
                secrets = self.client.list_secrets(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name())
            except Exception as e:  # pylint: disable=broad-except
                handle_raw_exception(e)

            safe_set(self.containerappjob_def, "properties", "configuration", "secrets", value=secrets["value"])
            safe_set(self.new_containerappjob, "properties", "configuration", "secrets", value=secrets["value"])

    def validate_arguments(self):
        # Check if containerapp job exists
        self.containerappjob_def = None
        try:
            self.containerappjob_def = self.client.show(cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name())
        except Exception as e:
            handle_non_404_status_code_exception(e)

        if not self.containerappjob_def:
            raise ResourceNotFoundError("The containerapps job '{}' does not exist".format(self.get_argument_name()))

    def construct_payload(self):
        if self.get_argument_yaml():
            return self.set_up_update_containerapp_job_yaml(name=self.get_argument_name(), file_name=self.get_argument_yaml())

        safe_set(self.new_containerappjob, "properties", "configuration", value={})

        # Doing this while API has bug. If env var is an empty string, API doesn't return "value" even though the "value" should be an empty string
        for container in safe_get(self.containerappjob_def, "properties", "template", "containers", default=[]):
            if "env" in container:
                for e in container["env"]:
                    if "value" not in e:
                        e["value"] = ""

        if self.get_argument_tags():
            _add_or_update_tags(self.new_containerappjob, self.get_argument_tags())

        if self.get_argument_workload_profile_name():
            self.new_containerappjob["properties"]["workloadProfileName"] = self.get_argument_workload_profile_name()

            parsed_managed_env = parse_resource_id(self.containerappjob_def["properties"]["environmentId"])
            managed_env_name = parsed_managed_env['name']
            managed_env_rg = parsed_managed_env['resource_group']
            managed_env_info = None
            try:
                managed_env_info = self.get_environment_client().show(cmd=self.cmd, resource_group_name=managed_env_rg, name=managed_env_name)
            except Exception as e:
                handle_non_404_status_code_exception(e)

            if not managed_env_info:
                raise ValidationError(
                    "Error parsing the managed environment '{}' from the specified containerappjob".format(
                        managed_env_name))

            ensure_workload_profile_supported(self.cmd, managed_env_name, managed_env_rg,
                                              self.get_argument_workload_profile_name(),
                                              managed_env_info)

        # replicaConfiguration
        self.set_up_replica_configurations()

        # triggerConfiguration
        self.set_up_trigger_configurations()

        # Containers
        self.set_up_container()

        # Registry
        self.set_up_registry()

    def should_update_container(self):
        return self.get_argument_image() \
            or self.get_argument_container_name() \
            or self.get_argument_set_env_vars() is not None \
            or self.get_argument_remove_env_vars() is not None \
            or self.get_argument_replace_env_vars() is not None \
            or self.get_argument_remove_all_env_vars() \
            or self.get_argument_cpu() \
            or self.get_argument_memory() \
            or self.get_argument_startup_command() is not None \
            or self.get_argument_args() is not None

    def set_up_container(self):
        if self.should_update_container():  # pylint: disable=too-many-nested-blocks
            safe_set(self.new_containerappjob, "properties", "template", "containers", value=self.containerappjob_def["properties"]["template"]["containers"])

            if not self.get_argument_container_name():
                if len(self.new_containerappjob["properties"]["template"]["containers"]) == 1:
                    container_name = self.new_containerappjob["properties"]["template"]["containers"][0]["name"]
                    self.set_argument_container_name(container_name)
                else:
                    raise ValidationError(
                        "Usage error: --container-name is required when adding or updating a container")

            # Check if updating existing container
            updating_existing_container = False
            for c in self.new_containerappjob["properties"]["template"]["containers"]:
                if c["name"].lower() == self.get_argument_container_name().lower():
                    updating_existing_container = True

                    if self.get_argument_image() is not None:
                        c["image"] = self.get_argument_image()

                    if self.get_argument_set_env_vars() is not None:
                        if "env" not in c or not c["env"]:
                            c["env"] = []
                        # env vars
                        _add_or_update_env_vars(c["env"], parse_env_var_flags(self.get_argument_set_env_vars()))

                    if self.get_argument_replace_env_vars() is not None:
                        # Remove other existing env_vars, then add them
                        c["env"] = []
                        _add_or_update_env_vars(c["env"], parse_env_var_flags(self.get_argument_replace_env_vars()))

                    if self.get_argument_remove_env_vars() is not None:
                        if "env" not in c or not c["env"]:
                            c["env"] = []
                        # env vars
                        _remove_env_vars(c["env"], self.get_argument_remove_env_vars())

                    if self.get_argument_remove_all_env_vars():
                        c["env"] = []

                    if self.get_argument_startup_command() is not None:
                        if isinstance(self.get_argument_startup_command(), list) and not self.get_argument_startup_command():
                            c["command"] = None
                        else:
                            c["command"] = self.get_argument_startup_command()
                    if self.get_argument_args() is not None:
                        if isinstance(self.get_argument_args(), list) and not self.get_argument_args():
                            c["args"] = None
                        else:
                            c["args"] = self.get_argument_args()
                    if self.get_argument_cpu() is not None or self.get_argument_memory() is not None:
                        if "resources" in c and c["resources"]:
                            if self.get_argument_cpu() is not None:
                                c["resources"]["cpu"] = self.get_argument_cpu()
                            if self.get_argument_memory() is not None:
                                c["resources"]["memory"] = self.get_argument_memory()
                        else:
                            c["resources"] = {
                                "cpu": self.get_argument_cpu(),
                                "memory": self.get_argument_memory()
                            }

            # If not updating existing container, add as new container
            if not updating_existing_container:
                if self.get_argument_image() is None:
                    raise ValidationError("Usage error: --image is required when adding a new container")

                resources_def = None
                if self.get_argument_cpu() is not None or self.get_argument_memory() is not None:
                    resources_def = ContainerResourcesModel
                    resources_def["cpu"] = self.get_argument_cpu()
                    resources_def["memory"] = self.get_argument_memory()

                container_def = ContainerModel
                container_def["name"] = self.get_argument_container_name()
                container_def["image"] = self.get_argument_image()
                container_def["env"] = []

                if self.get_argument_set_env_vars() is not None:
                    # env vars
                    _add_or_update_env_vars(container_def["env"], parse_env_var_flags(self.get_argument_set_env_vars()))

                if self.get_argument_replace_env_vars() is not None:
                    # env vars
                    _add_or_update_env_vars(container_def["env"], parse_env_var_flags(self.get_argument_replace_env_vars()))

                if self.get_argument_remove_env_vars() is not None:
                    # env vars
                    _remove_env_vars(container_def["env"], self.get_argument_remove_env_vars())

                if self.get_argument_remove_all_env_vars():
                    container_def["env"] = []

                if self.get_argument_startup_command() is not None:
                    if isinstance(self.get_argument_startup_command(), list) and not self.get_argument_startup_command():
                        container_def["command"] = None
                    else:
                        container_def["command"] = self.get_argument_startup_command()
                if self.get_argument_args() is not None:
                    if isinstance(self.get_argument_args(), list) and not self.get_argument_args():
                        container_def["args"] = None
                    else:
                        container_def["args"] = self.get_argument_args()
                if resources_def is not None:
                    container_def["resources"] = resources_def

                self.new_containerappjob["properties"]["template"]["containers"].append(container_def)

    def should_update_replica_configurations(self):
        return self.get_argument_replica_timeout() or self.get_argument_replica_retry_limit()

    def set_up_replica_configurations(self):
        if self.should_update_replica_configurations():
            if self.get_argument_replica_timeout() is not None or self.get_argument_replica_retry_limit() is not None:
                if self.get_argument_replica_timeout():
                    safe_set(self.new_containerappjob, "properties", "configuration", "replicaTimeout", value=self.get_argument_replica_timeout())
                if self.get_argument_replica_retry_limit():
                    safe_set(self.new_containerappjob, "properties", "configuration", "replicaRetryLimit", value=self.get_argument_replica_retry_limit())

    def should_update_trigger_configurations(self):
        return self.get_argument_replica_completion_count() \
            or self.get_argument_parallelism() \
            or self.get_argument_cron_expression() \
            or self.get_argument_scale_rule_name() \
            or self.get_argument_scale_rule_type() \
            or self.get_argument_scale_rule_auth() \
            or self.get_argument_polling_interval() \
            or self.get_argument_min_executions() is not None \
            or self.get_argument_max_executions() is not None

    def set_up_trigger_configurations(self):
        if self.should_update_trigger_configurations():  # pylint: disable=too-many-nested-blocks
            trigger_type = safe_get(self.containerappjob_def, "properties", "configuration", "triggerType")
            if trigger_type == "Manual":
                manual_trigger_config_def = safe_get(self.containerappjob_def, "properties", "configuration", "manualTriggerConfig")
                if self.get_argument_replica_completion_count() is not None or self.get_argument_parallelism() is not None:
                    if self.get_argument_replica_completion_count():
                        manual_trigger_config_def["replicaCompletionCount"] = self.get_argument_replica_completion_count()
                    if self.get_argument_parallelism():
                        manual_trigger_config_def["parallelism"] = self.get_argument_parallelism()
                safe_set(self.new_containerappjob, "properties", "configuration", "manualTriggerConfig", value=manual_trigger_config_def)

            if trigger_type == "Schedule":
                schedule_trigger_config_def = safe_get(self.containerappjob_def, "properties", "configuration", "scheduleTriggerConfig")
                if self.get_argument_replica_completion_count() is not None or self.get_argument_parallelism() is not None or self.get_argument_cron_expression() is not None:
                    if self.get_argument_replica_completion_count():
                        schedule_trigger_config_def["replicaCompletionCount"] = self.get_argument_replica_completion_count()
                    if self.get_argument_parallelism():
                        schedule_trigger_config_def["parallelism"] = self.get_argument_parallelism()
                    if self.get_argument_cron_expression():
                        schedule_trigger_config_def["cronExpression"] = self.get_argument_cron_expression()
                safe_set(self.new_containerappjob, "properties", "configuration", "scheduleTriggerConfig", value=schedule_trigger_config_def)

            if trigger_type == "Event":
                event_trigger_config_def = safe_get(self.containerappjob_def, "properties", "configuration", "eventTriggerConfig")
                if self.get_argument_replica_completion_count() is not None or self.get_argument_parallelism() is not None or self.get_argument_min_executions() is not None or self.get_argument_max_executions() is not None or self.get_argument_polling_interval() is not None or self.get_argument_scale_rule_name() is not None:
                    if self.get_argument_replica_completion_count():
                        event_trigger_config_def["replicaCompletionCount"] = self.get_argument_replica_completion_count()
                    if self.get_argument_parallelism():
                        event_trigger_config_def["parallelism"] = self.get_argument_parallelism()
                    # Scale
                    if "scale" not in event_trigger_config_def:
                        event_trigger_config_def["scale"] = {}
                    if self.get_argument_min_executions() is not None:
                        event_trigger_config_def["scale"]["minExecutions"] = self.get_argument_min_executions()
                    if self.get_argument_max_executions() is not None:
                        event_trigger_config_def["scale"]["maxExecutions"] = self.get_argument_max_executions()
                    if self.get_argument_polling_interval() is not None:
                        event_trigger_config_def["scale"]["pollingInterval"] = self.get_argument_polling_interval()
                    # ScaleRule
                    if self.get_argument_scale_rule_name():
                        scale_rule_type = self.get_argument_scale_rule_type().lower()
                        scale_rule_def = ScaleRuleModel
                        curr_metadata = {}
                        metadata_def = parse_metadata_flags(self.get_argument_scale_rule_metadata(), curr_metadata)
                        auth_def = parse_auth_flags(self.get_argument_scale_rule_auth())
                        scale_rule_def["name"] = self.get_argument_scale_rule_name()
                        scale_rule_def["type"] = scale_rule_type
                        scale_rule_def["metadata"] = metadata_def
                        scale_rule_def["auth"] = auth_def
                        if safe_get(event_trigger_config_def, "scale", "rules") is None:
                            event_trigger_config_def["scale"]["rules"] = []
                        existing_rules = event_trigger_config_def["scale"]["rules"]
                        updated_rule = False
                        for rule in existing_rules:
                            if rule["name"] == self.get_argument_scale_rule_name():
                                rule.update(scale_rule_def)
                                updated_rule = True
                                break
                        if not updated_rule:
                            existing_rules.append(scale_rule_def)

                safe_set(self.new_containerappjob, "properties", "configuration", "eventTriggerConfig", value=event_trigger_config_def)

    def should_update_registry(self):
        return self.get_argument_registry_server() \
            or self.get_argument_registry_user() \
            or self.get_argument_registry_pass()

    def set_up_registry(self):
        if self.should_update_registry():
            ori_registries = safe_get(self.containerappjob_def, "properties", "configuration", "registries", default=[])
            safe_set(self.new_containerappjob, "properties", "configuration", "registries", value=ori_registries)

            registries_def = ori_registries

            self.set_up_get_existing_secrets()

            if self.get_argument_registry_server():
                if not self.get_argument_registry_pass or not self.get_argument_registry_user():
                    if ACR_IMAGE_SUFFIX not in self.get_argument_registry_server():
                        raise RequiredArgumentMissingError(
                            'Registry url is required if using Azure Container Registry, otherwise Registry username and password are required if using Dockerhub')
                    logger.warning(
                        'No credential was provided to access Azure Container Registry. Trying to look up...')
                    parsed = urlparse(self.get_argument_registry_server())
                    registry_name = (parsed.netloc if parsed.scheme else parsed.path).split('.')[0]
                    registry_user, registry_pass, _ = _get_acr_cred(self.cmd.cli_ctx, registry_name)
                    self.set_argument_registry_user(registry_user)
                    self.set_argument_registry_pass(registry_pass)

                # Check if updating existing registry
                updating_existing_registry = False
                for r in registries_def:
                    if r['server'].lower() == self.get_argument_registry_server().lower():
                        updating_existing_registry = True
                        if self.get_argument_registry_user():
                            r["username"] = self.get_argument_registry_user()
                        if self.get_argument_registry_pass():
                            r["passwordSecretRef"] = store_as_secret_and_return_secret_ref(
                                self.new_containerappjob["properties"]["configuration"]["secrets"],
                                r["username"],
                                r["server"],
                                self.get_argument_registry_pass(),
                                update_existing_secret=True,
                                disable_warnings=True)

                # If not updating existing registry, add as new registry
                if not updating_existing_registry:
                    registry = RegistryCredentialsModel
                    registry["server"] = self.get_argument_registry_server()
                    registry["username"] = self.get_argument_registry_user()
                    registry["passwordSecretRef"] = store_as_secret_and_return_secret_ref(
                        self.new_containerappjob["properties"]["configuration"]["secrets"],
                        self.get_argument_registry_user(),
                        self.get_argument_registry_server(),
                        self.get_argument_registry_pass(),
                        update_existing_secret=True,
                        disable_warnings=True)

                    registries_def.append(registry)

    def set_up_update_containerapp_job_yaml(self, name, file_name):
        if self.get_argument_image() or self.get_argument_replica_timeout() or self.get_argument_replica_retry_limit() or \
                self.get_argument_set_env_vars() or self.get_argument_remove_env_vars() or self.get_argument_replace_env_vars() or self.get_argument_remove_all_env_vars() or self.get_argument_cpu() or self.get_argument_memory() or \
                self.get_argument_startup_command() or self.get_argument_args() or self.get_argument_tags():
            logger.warning(
                'Additional flags were passed along with --yaml. These flags will be ignored, and the configuration defined in the yaml will be used instead')
        yaml_containerappsjob = process_loaded_yaml(load_yaml_file(file_name))
        if not isinstance(yaml_containerappsjob, dict):  # pylint: disable=unidiomatic-typecheck
            raise ValidationError(
                'Invalid YAML provided. Please see https://aka.ms/azure-container-apps-yaml for a valid containerapps YAML spec.')

        if not yaml_containerappsjob.get('name'):
            yaml_containerappsjob['name'] = name
        elif yaml_containerappsjob.get('name').lower() != name.lower():
            logger.warning(
                'The app name provided in the --yaml file "{}" does not match the one provided in the --name flag "{}". The one provided in the --yaml file will be used.'.format(
                    yaml_containerappsjob.get('name'), name))
        name = yaml_containerappsjob.get('name')

        if not yaml_containerappsjob.get('type'):
            yaml_containerappsjob['type'] = 'Microsoft.App/jobs'
        elif yaml_containerappsjob.get('type').lower() != "microsoft.app/jobs":
            raise ValidationError('Containerapp type must be \"Microsoft.App/ContainerApps\"')

        existed_environment_id = self.containerappjob_def['properties']['environmentId']
        self.new_containerappjob = None

        # Deserialize the yaml into a ContainerApp object. Need this since we're not using SDK
        try:
            deserializer = create_deserializer(self.models)
            self.new_containerappjob = deserializer('ContainerAppsJob', yaml_containerappsjob)
        except DeserializationError as ex:
            raise ValidationError(
                'Invalid YAML provided. Please see https://aka.ms/azure-container-apps-yaml for a valid containerapps YAML spec.') from ex

        # Remove tags before converting from snake case to camel case, then re-add tags. We don't want to change the case of the tags. Need this since we're not using SDK
        tags = None
        if yaml_containerappsjob.get('tags'):
            tags = yaml_containerappsjob.get('tags')
            del yaml_containerappsjob['tags']

        self.new_containerappjob = _convert_object_from_snake_to_camel_case(_object_to_dict(self.new_containerappjob))
        self.new_containerappjob['tags'] = tags

        # After deserializing, some properties may need to be moved under the "properties" attribute. Need this since we're not using SDK
        self.new_containerappjob = process_loaded_yaml(self.new_containerappjob)

        # Remove "additionalProperties" and read-only attributes that are introduced in the deserialization. Need this since we're not using SDK
        _remove_additional_attributes(self.new_containerappjob)
        _remove_readonly_attributes(self.new_containerappjob)

        secret_values = self.list_secrets(show_values=True)
        _populate_secret_values(self.new_containerappjob, secret_values)

        # Clean null values since this is an update
        self.new_containerappjob = clean_null_values(self.new_containerappjob)

        # If job to be updated is of triggerType 'event' then update scale
        if safe_get(self.new_containerappjob, "properties", "configuration", "triggerType") and self.new_containerappjob["properties"]["configuration"]["triggerType"].lower() == "event":
            if safe_get(yaml_containerappsjob, "properties", "configuration", "eventTriggerConfig", "scale"):
                print("scale is present")
                self.new_containerappjob["properties"]["configuration"]["eventTriggerConfig"]["scale"] = yaml_containerappsjob["properties"]["configuration"]["eventTriggerConfig"]["scale"]

        # Remove the environmentId in the PATCH payload if it has not been changed
        if safe_get(self.new_containerappjob, "properties", "environmentId") and safe_get(self.new_containerappjob, "properties", "environmentId").lower() == existed_environment_id.lower():
            del self.new_containerappjob["properties"]['environmentId']

    def update(self):
        try:
            r = self.client.update(
                cmd=self.cmd, resource_group_name=self.get_argument_resource_group_name(), name=self.get_argument_name(), containerapp_job_envelope=self.new_containerappjob,
                no_wait=self.get_argument_no_wait())
            if not self.get_argument_no_wait() and "properties" in r and "provisioningState" in r["properties"] and r["properties"]["provisioningState"].lower() == "waiting":
                logger.warning('Containerapps job update in progress. Please monitor the update using `az containerapp job show -n {} -g {}`'.format(self.get_argument_name(), self.get_argument_resource_group_name()))
            return r
        except Exception as e:
            handle_raw_exception(e)


class ContainerAppJobPreviewCreateDecorator(ContainerAppJobCreateDecorator):
    # not craete role assignment if it's env system msi
    def check_create_acrpull_role_assignment(self):
        identity = self.get_argument_registry_identity()
        if identity and not is_registry_msi_system(identity) and not is_registry_msi_system_environment(identity):
            logger.info("Creating an acrpull role assignment for the registry identity")
            create_acrpull_role_assignment(self.cmd, self.get_argument_registry_server(), identity, skip_error=True)

    # not set up msi for current containerapp if it's env msi
    def set_up_registry_identity(self):
        identity = self.get_argument_registry_identity()
        if identity:
            if is_registry_msi_system(identity):
                set_managed_identity(self.cmd, self.get_argument_resource_group_name(), self.containerappjob_def, system_assigned=True)
            elif is_valid_resource_id(identity):
                parsed_managed_env = parse_resource_id(self.get_argument_managed_env())
                managed_env_name = parsed_managed_env['name']
                managed_env_rg = parsed_managed_env['resource_group']
                if not env_has_managed_identity(self.cmd, managed_env_rg, managed_env_name, identity):
                    set_managed_identity(self.cmd, self.get_argument_resource_group_name(), self.containerappjob_def, user_assigned=[identity])

    # copy from parent
    def parent_construct_payload(self):
        # preview logic
        self.check_create_acrpull_role_assignment()
        # end preview logic

        if self.get_argument_yaml():
            return self.set_up_create_containerapp_job_yaml(name=self.get_argument_name(), file_name=self.get_argument_yaml())

        if not self.get_argument_image():
            self.set_argument_image(HELLO_WORLD_IMAGE)

        # Validate managed environment
        parsed_managed_env = parse_resource_id(self.get_argument_managed_env())
        managed_env_name = parsed_managed_env['name']
        managed_env_rg = parsed_managed_env['resource_group']
        managed_env_info = None

        try:
            managed_env_info = self.get_environment_client().show(cmd=self.cmd, resource_group_name=managed_env_rg, name=managed_env_name)
        except:  # pylint: disable=bare-except
            pass

        if not managed_env_info:
            raise ValidationError(
                "The environment '{}' does not exist. Specify a valid environment".format(self.get_argument_managed_env()))

        location = managed_env_info["location"]
        _ensure_location_allowed(self.cmd, location, CONTAINER_APPS_RP, "jobs")

        if not self.get_argument_workload_profile_name() and "workloadProfiles" in managed_env_info:
            workload_profile_name = get_default_workload_profile_name_from_env(self.cmd, managed_env_info, managed_env_rg)
            self.set_augument_workload_profile_name(workload_profile_name)

        manualTriggerConfig_def = None
        if self.get_argument_trigger_type() is not None and self.get_argument_trigger_type().lower() == "manual":
            manualTriggerConfig_def = ManualTriggerModel
            manualTriggerConfig_def[
                "replicaCompletionCount"] = 0 if self.get_argument_replica_completion_count() is None else self.get_argument_replica_completion_count()
            manualTriggerConfig_def["parallelism"] = 0 if self.get_argument_parallelism() is None else self.get_argument_parallelism()

        scheduleTriggerConfig_def = None
        if self.get_argument_trigger_type() is not None and self.get_argument_trigger_type().lower() == "schedule":
            scheduleTriggerConfig_def = ScheduleTriggerModel
            scheduleTriggerConfig_def[
                "replicaCompletionCount"] = 0 if self.get_argument_replica_completion_count() is None else self.get_argument_replica_completion_count()
            scheduleTriggerConfig_def["parallelism"] = 0 if self.get_argument_parallelism() is None else self.get_argument_parallelism()
            scheduleTriggerConfig_def["cronExpression"] = self.get_argument_cron_expression()

        eventTriggerConfig_def = None
        if self.get_argument_trigger_type() is not None and self.get_argument_trigger_type().lower() == "event":
            scale_def = None
            if self.get_argument_min_executions() is not None or self.get_argument_max_executions() is not None or self.get_argument_polling_interval() is not None:
                scale_def = JobScaleModel
                scale_def["pollingInterval"] = self.get_argument_polling_interval()
                scale_def["minExecutions"] = self.get_argument_min_executions()
                scale_def["maxExecutions"] = self.get_argument_max_executions()

            if self.get_argument_scale_rule_name():
                scale_rule_type = self.get_argument_scale_rule_type().lower()
                scale_rule_def = ScaleRuleModel
                curr_metadata = {}
                metadata_def = parse_metadata_flags(self.get_argument_scale_rule_metadata(), curr_metadata)
                auth_def = parse_auth_flags(self.get_argument_scale_rule_auth())
                scale_rule_def["name"] = self.get_argument_scale_rule_name()
                scale_rule_def["type"] = scale_rule_type
                scale_rule_def["metadata"] = metadata_def
                scale_rule_def["auth"] = auth_def

                if not scale_def:
                    scale_def = JobScaleModel
                scale_def["rules"] = [scale_rule_def]

            eventTriggerConfig_def = EventTriggerModel
            eventTriggerConfig_def["replicaCompletionCount"] = self.get_argument_replica_completion_count()
            eventTriggerConfig_def["parallelism"] = self.get_argument_parallelism()
            eventTriggerConfig_def["scale"] = scale_def

        secrets_def = None
        if self.get_argument_secrets() is not None:
            secrets_def = parse_secret_flags(self.get_argument_secrets())

        registries_def = None
        if self.get_argument_registry_server() is not None and not is_registry_msi_system(self.get_argument_registry_identity()):
            registries_def = RegistryCredentialsModel
            registries_def["server"] = self.get_argument_registry_server()

            # Infer credentials if not supplied and its azurecr
            if (self.get_argument_registry_user() is None or self.get_argument_registry_pass() is None) and self.get_argument_registry_identity() is None:
                registry_user, registry_pass = _infer_acr_credentials(self.cmd, self.get_argument_registry_server(), self.get_argument_disable_warnings())
                self.set_argument_registry_user(registry_user)
                self.set_argument_registry_pass(registry_pass)

            if not self.get_argument_registry_identity():
                registries_def["username"] = self.get_argument_registry_user()

                if secrets_def is None:
                    secrets_def = []
                registries_def["passwordSecretRef"] = store_as_secret_and_return_secret_ref(secrets_def, self.get_argument_registry_user(),
                                                                                            self.get_argument_registry_server(),
                                                                                            self.get_argument_registry_pass(),
                                                                                            disable_warnings=self.get_argument_disable_warnings())
            else:
                registries_def["identity"] = self.get_argument_registry_identity()

        config_def = JobConfigurationModel
        config_def["secrets"] = secrets_def
        config_def["triggerType"] = self.get_argument_trigger_type()
        config_def["replicaTimeout"] = self.get_argument_replica_timeout()
        config_def["replicaRetryLimit"] = self.get_argument_replica_retry_limit()
        config_def["manualTriggerConfig"] = manualTriggerConfig_def
        config_def["scheduleTriggerConfig"] = scheduleTriggerConfig_def
        config_def["eventTriggerConfig"] = eventTriggerConfig_def
        config_def["registries"] = [registries_def] if registries_def is not None else None

        # Identity actions
        identity_def = ManagedServiceIdentityModel
        identity_def["type"] = "None"

        assign_system_identity = self.get_argument_system_assigned()
        if self.get_argument_user_assigned():
            assign_user_identities = [x.lower() for x in self.get_argument_user_assigned()]
        else:
            assign_user_identities = []

        if assign_system_identity and assign_user_identities:
            identity_def["type"] = "SystemAssigned, UserAssigned"
        elif assign_system_identity:
            identity_def["type"] = "SystemAssigned"
        elif assign_user_identities:
            identity_def["type"] = "UserAssigned"

        if assign_user_identities:
            identity_def["userAssignedIdentities"] = {}
            subscription_id = get_subscription_id(self.cmd.cli_ctx)

            for r in assign_user_identities:
                r = _ensure_identity_resource_id(subscription_id, self.get_argument_resource_group_name(), r)
                identity_def["userAssignedIdentities"][r] = {}  # pylint: disable=unsupported-assignment-operation

        resources_def = None
        if self.get_argument_cpu() is not None or self.get_argument_memory() is not None:
            resources_def = ContainerResourcesModel
            resources_def["cpu"] = self.get_argument_cpu()
            resources_def["memory"] = self.get_argument_memory()

        container_def = ContainerModel
        container_def["name"] = self.get_argument_container_name() if self.get_argument_container_name() else self.get_argument_name()
        container_def["image"] = self.get_argument_image() if not is_registry_msi_system(self.get_argument_registry_identity()) else HELLO_WORLD_IMAGE
        if self.get_argument_env_vars() is not None:
            container_def["env"] = parse_env_var_flags(self.get_argument_env_vars())
        if self.get_argument_startup_command() is not None:
            container_def["command"] = self.get_argument_startup_command()
        if self.get_argument_args() is not None:
            container_def["args"] = self.get_argument_args()
        if resources_def is not None:
            container_def["resources"] = resources_def

        template_def = JobTemplateModel
        template_def["containers"] = [container_def]

        self.containerappjob_def["location"] = location
        self.containerappjob_def["identity"] = identity_def
        self.containerappjob_def["properties"]["environmentId"] = self.get_argument_managed_env()
        self.containerappjob_def["properties"]["configuration"] = config_def
        self.containerappjob_def["properties"]["template"] = template_def
        self.containerappjob_def["tags"] = self.get_argument_tags()

        if self.get_argument_workload_profile_name():
            self.containerappjob_def["properties"]["workloadProfileName"] = self.get_argument_workload_profile_name()
            ensure_workload_profile_supported(self.cmd, managed_env_name, managed_env_rg, self.get_argument_workload_profile_name(),
                                              managed_env_info)

        # preview logic
        self.set_up_registry_identity()

    def construct_payload(self):
        self.parent_construct_payload()
        self.set_up_extended_location()
        if self.get_argument_scale_rule_identity():
            scaleRules = safe_get(self.containerappjob_def, "properties", "configuration", "eventTriggerConfig", "scale", "rules", default=[])
            if scaleRules and len(scaleRules) > 0:
                identity = self.get_argument_scale_rule_identity().lower()
                if identity != "system":
                    subscription_id = get_subscription_id(self.cmd.cli_ctx)
                    identity = _ensure_identity_resource_id(subscription_id, self.get_argument_resource_group_name(), identity)
                self.containerappjob_def["properties"]["configuration"]["eventTriggerConfig"]["scale"]["rules"][0]["identity"] = identity

    # copy from parent
    def parent_validate_arguments(self):
        validate_container_app_name(self.get_argument_name(), AppType.ContainerAppJob.name)
        # preview logic
        self.validate_create()
        # end preview logic
        if self.get_argument_yaml() is None:
            if self.get_argument_replica_timeout() is None:
                raise RequiredArgumentMissingError('Usage error: --replica-timeout is required')

            if self.get_argument_replica_retry_limit() is None:
                raise RequiredArgumentMissingError('Usage error: --replica-retry-limit is required')

            if self.get_argument_managed_env() is None:
                raise RequiredArgumentMissingError('Usage error: --environment is required if not using --yaml')

    def validate_create(self):
        validate_create(registry_identity=self.get_argument_registry_identity(), registry_pass=self.get_argument_registry_pass(), registry_user=self.get_argument_registry_user(), registry_server=self.get_argument_registry_server(), no_wait=self.get_argument_no_wait())

    def validate_arguments(self):
        self.parent_validate_arguments()
        if self.get_argument_yaml() is None:
            if self.get_argument_trigger_type() is None:
                raise RequiredArgumentMissingError('Usage error: --trigger-type is required')
        if self.get_argument_scale_rule_type() and self.get_argument_scale_rule_identity():
            scale_rule_type = self.get_argument_scale_rule_type().lower()
            if scale_rule_type == "http" or scale_rule_type == "tcp":
                raise InvalidArgumentValueError("--scale-rule-identity cannot be set when --scale-rule-type is 'http' or 'tcp'")

    def set_up_extended_location(self):
        if self.get_argument_environment_type() == CONNECTED_ENVIRONMENT_TYPE:
            if not self.containerappjob_def.get('extendedLocation'):
                env_id = safe_get(self.containerappjob_def, "properties", 'environmentId') or self.get_argument_managed_env()
                parsed_env = parse_resource_id(env_id)
                env_name = parsed_env['name']
                env_rg = parsed_env['resource_group']
                env_info = self.get_environment_client().show(cmd=self.cmd, resource_group_name=env_rg, name=env_name)
                self.containerappjob_def["extendedLocation"] = env_info["extendedLocation"]

    def get_environment_client(self):
        if self.get_argument_yaml():
            env = safe_get(self.containerappjob_def, "properties", "environmentId")
        else:
            env = self.get_argument_managed_env()

        environment_type = self.get_argument_environment_type()
        if not env and not environment_type:
            return ManagedEnvironmentClient

        parsed_env = parse_resource_id(env)

        # Validate environment type
        if parsed_env.get('resource_type').lower() == CONNECTED_ENVIRONMENT_RESOURCE_TYPE.lower():
            if environment_type == MANAGED_ENVIRONMENT_TYPE:
                logger.warning(f"User passed a connectedEnvironment resource id but did not specify --environment-type {CONNECTED_ENVIRONMENT_TYPE}. Using environment type {CONNECTED_ENVIRONMENT_TYPE}.")
            environment_type = CONNECTED_ENVIRONMENT_TYPE
        else:
            if environment_type == CONNECTED_ENVIRONMENT_TYPE:
                logger.warning(f"User passed a managedEnvironment resource id but specified --environment-type {CONNECTED_ENVIRONMENT_TYPE}. Using environment type {MANAGED_ENVIRONMENT_TYPE}.")
            environment_type = MANAGED_ENVIRONMENT_TYPE

        self.set_argument_environment_type(environment_type)
        self.set_argument_managed_env(env)

        if environment_type == CONNECTED_ENVIRONMENT_TYPE:
            return ConnectedEnvironmentClient
        else:
            return ManagedEnvironmentPreviewClient

    def get_argument_environment_type(self):
        return self.get_param("environment_type")

    def get_argument_scale_rule_identity(self):
        return self.get_param("scale_rule_identity")

    def set_argument_managed_env(self, managed_env):
        self.set_param("managed_env", managed_env)

    def set_argument_environment_type(self, environment_type):
        self.set_param("environment_type", environment_type)


class ContainerAppJobPreviewUpdateDecorator(ContainerAppJobUpdateDecorator):
    # pylint: disable=useless-super-delegation
    def construct_payload(self):
        super().construct_payload()

    def validate_arguments(self):
        super().validate_arguments()
        if self.get_argument_scale_rule_type() and self.get_argument_scale_rule_identity():
            scale_rule_type = self.get_argument_scale_rule_type().lower()
            if scale_rule_type == "http" or scale_rule_type == "tcp":
                raise InvalidArgumentValueError("--scale-rule-identity cannot be set when --scale-rule-type is 'http' or 'tcp'")

    def set_up_trigger_configurations(self):
        super().set_up_trigger_configurations()
        identity = self.get_argument_scale_rule_identity()
        if identity:
            trigger_type = safe_get(self.containerappjob_def, "properties", "configuration", "triggerType")
            if trigger_type == "Event":
                existing_rules = safe_get(self.containerappjob_def, "properties", "configuration", "eventTriggerConfig", "scale", "rules", default=[])
                if existing_rules and len(existing_rules) > 0:
                    identity = self.get_argument_scale_rule_identity().lower()
                    if identity != "system":
                        subscription_id = get_subscription_id(self.cmd.cli_ctx)
                        identity = _ensure_identity_resource_id(subscription_id, self.get_argument_resource_group_name(), identity)
                    for rule in existing_rules:
                        if rule["name"] == self.get_argument_scale_rule_name():
                            rule["identity"] = identity
                            break
                    safe_set(self.new_containerappjob, "properties", "configuration", "eventTriggerConfig", "scale", "rules", value=existing_rules)

    def should_update_trigger_configurations(self):
        return super().should_update_trigger_configurations() \
            or self.get_argument_scale_rule_identity()

    def get_argument_scale_rule_identity(self):
        return self.get_param("scale_rule_identity")
