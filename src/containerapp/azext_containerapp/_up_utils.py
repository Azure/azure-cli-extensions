# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, consider-using-f-string, no-else-return, duplicate-string-formatting-argument, expression-not-assigned, too-many-locals, logging-fstring-interpolation, arguments-differ, abstract-method, logging-format-interpolation, broad-except
from random import randint
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse
import os
import subprocess
import tempfile
import uuid
import requests

from azure.cli.core.azclierror import (
    RequiredArgumentMissingError,
    ValidationError,
    InvalidArgumentValueError,
    MutuallyExclusiveArgumentError,
    CLIError,
)
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.command_modules.appservice._create_util import (
    check_resource_group_exists,
)
from azure.cli.command_modules.acr.custom import acr_show
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.command_modules.containerapp._github_oauth import load_github_token_from_cache, get_github_access_token
from azure.cli.command_modules.containerapp._utils import (
    get_profile_username,
    create_resource_group,
    get_resource_group,
    queue_acr_build,
    _get_acr_cred,
    create_new_acr,
    _get_default_containerapps_location,
    safe_get,
    is_int,
    create_service_principal_for_github_action,
    repo_url_to_name,
    get_container_app_if_exists,
    get_containerapps_job_if_exists,
    _ensure_location_allowed,
    register_provider_if_needed,
    format_location
)
from azure.core.exceptions import HttpResponseError
from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from knack.log import get_logger

from msrestazure.tools import parse_resource_id, is_valid_resource_id, resource_id

from ._client_factory import handle_non_404_status_code_exception
from ._clients import ContainerAppPreviewClient, GitHubActionClient, ContainerAppsJobClient, \
    ConnectedEnvironmentClient, ManagedEnvironmentPreviewClient

from ._utils import (
    get_pack_exec_path,
    is_docker_running,
    get_pack_exec_path, _validate_custom_loc_and_location, _validate_connected_k8s_exists, get_custom_location,
    create_extension, create_custom_location, get_cluster_extension, validate_environment_location,
    list_environment_locations, get_randomized_name_with_dash, get_randomized_name, get_connected_k8s,
    list_cluster_extensions, list_custom_location
)

from ._constants import (MAXIMUM_SECRET_LENGTH,
                         LOG_ANALYTICS_RP,
                         CONTAINER_APPS_RP,
                         ACR_IMAGE_SUFFIX,
                         ACR_TASK_TEMPLATE,
                         DEFAULT_PORT,
                         ACA_BUILDER_BULLSEYE_IMAGE,
                         ACA_BUILDER_BOOKWORM_IMAGE, EXTENDED_LOCATION_RP, KUBERNETES_CONFIGURATION_RP,
                         CONNECTED_ENVIRONMENT_TYPE, CUSTOM_LOCATION_RESOURCE_TYPE, MANAGED_ENVIRONMENT_TYPE,
                         CONNECTED_ENVIRONMENT_RESOURCE_TYPE, MANAGED_ENVIRONMENT_RESOURCE_TYPE,
                         CONTAINER_APP_EXTENSION_TYPE, DEFAULT_CONNECTED_CLUSTER_EXTENSION_NAME,
                         DEFAULT_CONNECTED_CLUSTER_EXTENSION_NAMESPACE)

from .custom import (
    create_managed_environment,
    create_containerappsjob,
    containerapp_up_logic,
    list_containerapp,
    list_managed_environments,
    create_or_update_github_action, create_connected_environment, list_connected_environments,
)

from ._cloud_build_utils import (
    run_cloud_build
)

logger = get_logger(__name__)


class ResourceGroup:
    def __init__(self, cmd, name: str, location: str, exists: bool = None):
        self.cmd = cmd
        self.name = name
        self.location = _get_default_containerapps_location(cmd, location)
        if self.location.lower() == "northcentralusstage":
            self.location = "eastus"
        self.exists = exists

        self.check_exists()

    def create(self):
        g = create_resource_group(self.cmd, self.name, self.location)
        self.exists = True
        return g

    def _get(self):
        return get_resource_group(self.cmd, self.name)

    def get(self):
        r = None
        try:
            r = self._get()
        except:  # pylint: disable=bare-except
            pass
        return r

    def check_exists(self) -> bool:
        if self.name is None:
            self.exists = False
        else:
            self.exists = check_resource_group_exists(self.cmd, self.name)
        return self.exists

    def create_if_needed(self):
        if not self.check_exists():
            if not self.name:
                self.name = get_randomized_name(get_profile_username())
            logger.warning(f"Creating resource group '{self.name}'")
            self.create()
        else:
            logger.warning(f"Using resource group '{self.name}'")  # TODO use .info()


class Resource:
    def __init__(
        self, cmd, name: str, resource_group: "ResourceGroup", exists: bool = None
    ):
        self.cmd = cmd
        self.name = name
        self.resource_group = resource_group
        self.exists = exists

        self.check_exists()

    def create(self, *args, **kwargs):
        raise NotImplementedError()

    def _get(self):
        raise NotImplementedError()

    def get(self):
        r = None
        try:
            r = self._get()
        except:  # pylint: disable=bare-except
            pass
        return r

    def check_exists(self):
        if self.name is None or self.resource_group.name is None:
            self.exists = False
        else:
            self.exists = self.get() is not None
        return self.exists


class ContainerAppEnvironment(Resource):
    def __init__(
        self,
        cmd,
        name: str,
        resource_group: "ResourceGroup",
        exists: bool = None,
        location=None,
        logs_key=None,
        logs_customer_id=None,
        custom_location_id=None,
        connected_cluster_id=None,
    ):
        self.resource_type = None
        super().__init__(cmd, name, resource_group, exists)
        if is_valid_resource_id(name):
            env_dict = parse_resource_id(name)
            self.name = env_dict["name"]
            if "resource_group" in env_dict:
                rg = env_dict["resource_group"]
                if resource_group.name != rg:
                    self.resource_group = ResourceGroup(cmd, rg, location)
            if "resource_type" in env_dict:
                if env_dict["resource_type"].lower() == CONNECTED_ENVIRONMENT_RESOURCE_TYPE.lower():
                    self.resource_type = CONNECTED_ENVIRONMENT_RESOURCE_TYPE
                else:
                    self.resource_type = MANAGED_ENVIRONMENT_RESOURCE_TYPE

        if self.resource_type is None:
            if custom_location_id or connected_cluster_id:
                self.resource_type = CONNECTED_ENVIRONMENT_RESOURCE_TYPE

        self.location = location
        self.logs_key = logs_key
        self.logs_customer_id = logs_customer_id
        self.custom_location_id = custom_location_id

    def set_name(self, name_or_rid):
        if is_valid_resource_id(name_or_rid):
            env_dict = parse_resource_id(name_or_rid)
            self.name = env_dict["name"]
            self.resource_type = env_dict["resource_type"]
            if "resource_group" in parse_resource_id(name_or_rid):
                rg = parse_resource_id(name_or_rid)["resource_group"]
                if self.resource_group.name != rg:
                    self.resource_group = ResourceGroup(
                        self.cmd,
                        rg,
                        self.location,
                    )
        else:
            self.name = name_or_rid

    def is_connected_environment(self):
        if self.resource_type and self.resource_type == CONNECTED_ENVIRONMENT_RESOURCE_TYPE:
            return True
        return False

    def _get(self):
        if self.is_connected_environment():
            return ConnectedEnvironmentClient.show(
                self.cmd, self.resource_group.name, self.name
            )
        return ManagedEnvironmentPreviewClient.show(
            self.cmd, self.resource_group.name, self.name
        )

    def create_if_needed(self, app_name):
        if not self.check_exists():
            if self.name is None:
                self.name = "{}-env".format(app_name).replace("_", "-")
            logger.warning(
                f"Creating {type(self).__name__} '{self.name}' in resource group {self.resource_group.name}"
            )
            self.create()
        else:
            logger.warning(
                f"Using {type(self).__name__} '{self.name}' in resource group {self.resource_group.name}"
            )  # TODO use .info()

    def create(self):
        register_provider_if_needed(self.cmd, LOG_ANALYTICS_RP)
        # for creating connected environment, the location infer from custom location
        if self.is_connected_environment():
            self.location = validate_environment_location(self.cmd, self.location, CONNECTED_ENVIRONMENT_RESOURCE_TYPE)
            env = create_connected_environment(
                self.cmd,
                self.name,
                location=self.location,
                custom_location=self.custom_location_id,
                resource_group_name=self.resource_group.name,
            )
            return env

        if self.location:
            self.location = validate_environment_location(self.cmd, self.location)

            env = create_managed_environment(
                self.cmd,
                self.name,
                location=self.location,
                resource_group_name=self.resource_group.name,
                logs_key=self.logs_key,
                logs_customer_id=self.logs_customer_id,
                disable_warnings=True,
            )
            self.exists = True

            return env
        else:
            res_locations = list_environment_locations(self.cmd)
            for loc in res_locations:
                try:
                    env = create_managed_environment(
                        self.cmd,
                        self.name,
                        location=loc,
                        resource_group_name=self.resource_group.name,
                        logs_key=self.logs_key,
                        logs_customer_id=self.logs_customer_id,
                        disable_warnings=True,
                    )

                    self.exists = True
                    self.location = loc

                    return env
                except Exception as ex:
                    logger.info(
                        f"Failed to create ManagedEnvironment in {loc} due to {ex}"
                    )
            raise ValidationError("Can not find a region with quota to create ManagedEnvironment")

    def get_rid(self):
        rid = self.name
        if not is_valid_resource_id(self.name):
            rid = resource_id(
                subscription=get_subscription_id(self.cmd.cli_ctx),
                resource_group=self.resource_group.name,
                namespace=CONTAINER_APPS_RP,
                type=self.resource_type if self.resource_type else MANAGED_ENVIRONMENT_RESOURCE_TYPE,
                name=self.name,
            )
        return rid


class ContainerAppsJob(Resource):  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        cmd,
        name: str,
        resource_group: "ResourceGroup",
        exists: bool = None,
        image=None,
        env: "ContainerAppEnvironment" = None,
        target_port=None,
        registry_server=None,
        registry_user=None,
        registry_pass=None,
        env_vars=None,
        trigger_type=None,
        replica_timeout=None,
        replica_retry_limit=None,
        replica_completion_count=None,
        parallelism=None,
        cron_expression=None,
    ):

        super().__init__(cmd, name, resource_group, exists)
        self.image = image
        self.env = env
        self.target_port = target_port
        self.registry_server = registry_server
        self.registry_user = registry_user
        self.registry_pass = registry_pass
        self.env_vars = env_vars
        self.trigger_type = trigger_type,
        self.replica_timeout = replica_timeout,
        self.replica_retry_limit = replica_retry_limit
        self.replica_completion_count = replica_completion_count
        self.parallelism = parallelism
        self.cron_expression = cron_expression
        self.should_create_acr = False
        self.acr: "AzureContainerRegistry" = None

    def _get(self):
        return ContainerAppsJobClient.show(self.cmd, self.resource_group.name, self.name)

    def create(self, no_registry=False):
        # no_registry: don't pass in a registry during create even if the app has one (used for GH actions)
        if get_containerapps_job_if_exists(self.cmd, self.resource_group.name, self.name):
            logger.warning(
                f"Updating Containerapps job {self.name} in resource group {self.resource_group.name}"
            )
        else:
            logger.warning(
                f"Creating Containerapps job {self.name} in resource group {self.resource_group.name}"
            )

        return create_containerappsjob(
            cmd=self.cmd,
            name=self.name,
            resource_group_name=self.resource_group.name,
            image=self.image,
            managed_env=self.env.get_rid(),
            registry_server=None if no_registry else self.registry_server,
            registry_pass=None if no_registry else self.registry_pass,
            registry_user=None if no_registry else self.registry_user,
            env_vars=self.env_vars,
            trigger_type=self.trigger_type,
            replica_timeout=self.replica_timeout,
            replica_retry_limit=self.replica_retry_limit,
            replica_completion_count=self.replica_completion_count,
            parallelism=self.parallelism,
            cron_expression=self.cron_expression
        )


class AzureContainerRegistry(Resource):
    def __init__(self, name: str, resource_group: "ResourceGroup"):  # pylint: disable=super-init-not-called

        self.name = name
        self.resource_group = resource_group


class ContainerApp(Resource):  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        cmd,
        name: str,
        resource_group: "ResourceGroup",
        exists: bool = None,
        image=None,
        env: "ContainerAppEnvironment" = None,
        target_port=None,
        registry_server=None,
        registry_user=None,
        registry_pass=None,
        env_vars=None,
        workload_profile_name=None,
        ingress=None,
        force_single_container_updates=None
    ):

        super().__init__(cmd, name, resource_group, exists)
        self.image = image
        self.env = env
        self.target_port = target_port
        self.registry_server = registry_server
        self.registry_user = registry_user
        self.registry_pass = registry_pass
        self.env_vars = env_vars
        self.ingress = ingress
        self.workload_profile_name = workload_profile_name
        self.force_single_container_updates = force_single_container_updates

        self.should_create_acr = False
        self.acr: "AzureContainerRegistry" = None

    def _get(self):
        return ContainerAppPreviewClient.show(self.cmd, self.resource_group.name, self.name)

    def create(self, no_registry=False):
        # no_registry: don't pass in a registry during create even if the app has one (used for GH actions)
        if get_container_app_if_exists(self.cmd, self.resource_group.name, self.name):
            logger.warning(
                f"Updating Containerapp {self.name} in resource group {self.resource_group.name}"
            )
        else:
            logger.warning(
                f"Creating Containerapp {self.name} in resource group {self.resource_group.name}"
            )

        return containerapp_up_logic(
            cmd=self.cmd,
            name=self.name,
            resource_group_name=self.resource_group.name,
            image=self.image,
            managed_env=self.env.get_rid(),
            target_port=self.target_port,
            registry_server=None if no_registry else self.registry_server,
            registry_pass=None if no_registry else self.registry_pass,
            registry_user=None if no_registry else self.registry_user,
            env_vars=self.env_vars,
            workload_profile_name=self.workload_profile_name,
            ingress=self.ingress,
            environment_type=CONNECTED_ENVIRONMENT_TYPE if self.env.is_connected_environment() else MANAGED_ENVIRONMENT_TYPE,
            force_single_container_updates=self.force_single_container_updates
        )

    def set_force_single_container_updates(self, force_single_container_updates):
        self.force_single_container_updates = force_single_container_updates

    def create_acr_if_needed(self):
        if self.should_create_acr:
            logger.warning(
                f"Creating Azure Container Registry {self.acr.name} in resource group "
                f"{self.acr.resource_group.name}"
            )
            self.create_acr()

    def create_acr(self):
        registry_rg = self.resource_group
        url = self.registry_server
        registry_name = url[: url.rindex(ACR_IMAGE_SUFFIX)]
        location = "eastus"
        if self.env.location and self.env.location.lower() != "northcentralusstage":
            location = self.env.location
        registry_def = create_new_acr(
            self.cmd, registry_name, registry_rg.name, location
        )
        self.registry_server = registry_def.login_server

        if not self.acr:
            self.acr = AzureContainerRegistry(registry_name, registry_rg)

        self.registry_user, self.registry_pass, _ = _get_acr_cred(
            self.cmd.cli_ctx, registry_name
        )

    def _docker_push_to_container_registry(self, image_name, forced_acr_login=False):
        from azure.cli.command_modules.acr.custom import acr_login
        from azure.cli.core.profiles import ResourceType

        command = ['docker', 'push', image_name]
        logger.debug(f"Calling '{' '.join(command)}'")
        logger.warning(f"Built image {image_name} locally using buildpacks, attempting to push to registry...")
        try:
            with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
                _, stderr = process.communicate()
                if process.returncode != 0:
                    docker_push_error = stderr.decode('utf-8')
                    if not forced_acr_login and ".azurecr.io/" in image_name and "unauthorized" in docker_push_error:
                        # Couldn't push to ACR because the user isn't authenticated. Let's try to login to ACR and retrigger the docker push
                        logger.warning(f"The current user isn't authenticated to the {self.acr.name} ACR instance. Triggering an ACR login and retrying to push the image...")
                        # Logic to login to ACR
                        task_command_kwargs = {"resource_type": ResourceType.MGMT_CONTAINERREGISTRY, 'operation_group': 'webhooks'}
                        old_command_kwargs = {}
                        for key in task_command_kwargs:  # pylint: disable=consider-using-dict-items
                            old_command_kwargs[key] = self.cmd.command_kwargs.get(key)
                            self.cmd.command_kwargs[key] = task_command_kwargs[key]
                        if self.acr and self.acr.name is not None:
                            acr_login(self.cmd, self.acr.name)
                        for k, v in old_command_kwargs.items():
                            self.cmd.command_kwargs[k] = v

                        self._docker_push_to_container_registry(image_name, True)
                    else:
                        raise CLIError(f"Error thrown when running 'docker push': {docker_push_error}")
                logger.debug(f"Successfully pushed image {image_name} to the container registry.")
        except Exception as ex:
            raise CLIError(f"Unable to run 'docker push' command to push image to the container registry: {ex}") from ex

    def build_container_from_source_with_cloud_build_service(self, source, build_env_vars, location):
        logger.warning("Using the Cloud Build Service to build container image...")

        run_full_id = uuid.uuid4().hex
        logs_file_path = os.path.join(tempfile.gettempdir(), f"{'build{}'.format(run_full_id)[:12]}.txt")
        logs_file = open(logs_file_path, "w", encoding="utf-8")

        try:
            resource_group_name = self.resource_group.name
            return run_cloud_build(self.cmd, source, build_env_vars, location, resource_group_name, self.env.name, run_full_id, logs_file, logs_file_path)
        except Exception as exception:
            logs_file.close()
            raise exception

    def build_container_from_source_with_buildpack(self, image_name, source, cache_image_name, build_env_vars):  # pylint: disable=too-many-statements
        # Ensure that Docker is running
        if not is_docker_running():
            raise ValidationError("Docker is not running. Please start Docker to use buildpacks.")

        # Ensure that the pack CLI is installed
        pack_exec_path = get_pack_exec_path()
        if pack_exec_path is None:
            raise ValidationError("The pack CLI could not be installed.")

        logger.info("Docker is running and pack CLI is installed; attempting to use buildpacks to build container image...")

        registry_name = self.registry_server.lower()
        image_name = f"{registry_name}/{image_name}"
        cache_image_name = f"{registry_name}/{cache_image_name}"
        builder_image_list = [ACA_BUILDER_BULLSEYE_IMAGE, ACA_BUILDER_BOOKWORM_IMAGE]
        default_builder_image = builder_image_list[0]

        # Ensure that the default builder is trusted (this DOES NOT affect calls using different builders)
        command = [pack_exec_path, 'config', 'default-builder', default_builder_image]
        logger.debug(f"Calling '{' '.join(command)}'")
        try:
            with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
                _, stderr = process.communicate()
                if process.returncode != 0:
                    raise CLIError(f"Error thrown when running 'pack config': {stderr.decode('utf-8')}")
                logger.debug(f"Successfully set the default builder to {default_builder_image}.")
        except Exception as ex:
            raise ValidationError(f"Unable to run 'pack config' command to set default builder: {ex}") from ex

        # If the user specifies a target port, pass it to the buildpack
        if self.target_port:
            command.extend(['--env', f"ORYX_RUNTIME_PORT={self.target_port}"])

        logger.warning("Selecting a compatible builder for the provided application source...")
        could_build_image = False
        for builder_image in builder_image_list:
            # Run 'pack build' to produce a runnable application image for the Container App
            # Specify the image as the 'build-cache' image to ensure that the local cache is used for build layers
            command = [pack_exec_path, 'build', cache_image_name, '--builder', builder_image, '--path', source, '--tag', image_name]

            # Pass the subscription ID and caller ID to the buildpack
            sub_id = get_subscription_id(self.cmd.cli_ctx)
            command.extend(['--env', f"BP_SUBSCRIPTION_ID={sub_id}"])
            from azure.cli.core import __version__ as core_version
            command.extend(['--env', f"CALLER_ID=AZURECLI/{core_version}"])

            # If the user specifies environment variables, pass it to the buildpack
            if build_env_vars:
                for env_var in build_env_vars:
                    command.extend(['--env', f"{env_var}"])

            logger.debug(f"Calling '{' '.join(command)}'")
            try:
                is_non_supported_platform = False
                is_non_supported_os = False
                with subprocess.Popen(command, stdout=subprocess.PIPE) as process:
                    # Stream output of 'pack build' to warning stream
                    while process.stdout.readable():
                        line = process.stdout.readline()
                        if not line:
                            break

                        stdout_line = str(line.strip(), 'utf-8')
                        logger.warning(stdout_line)

                        # Check if the application is targeting a platform that's found in the current builder,
                        # specifically, if none of the buildpacks in the current builder are able to detect a platform
                        # for the given app source, then we are unable to build the app with the current builder
                        if not is_non_supported_platform and "No buildpack groups passed detection" in stdout_line:
                            is_non_supported_platform = True

                        # Check if the application has a version that it can target from the current builder,
                        # specifically, if we cannot find a valid Oryx runtime image for the given platform version and
                        # Debian flavor combination, then we are unable to build the app with the current builder
                        if not is_non_supported_os and "failed to pull run image" in stdout_line:
                            is_non_supported_os = True

                    # Update the result of process.returncode
                    process.communicate()
                    if is_non_supported_platform:
                        raise ValidationError(f"Builder {builder_image} does not support the platform targeted in the provided source code.")

                    if is_non_supported_os:
                        raise ValidationError(f"Builder {builder_image} does not support the version detected for the given operating system.")

                    if process.returncode != 0:
                        raise CLIError("Non-zero exit code returned from 'pack build'; please check the above output for more details.")

                    could_build_image = True
                    logger.debug(f"Successfully built image {image_name} using buildpacks.")
                    break
            except Exception as ex:
                logger.warning(f"Unable to run 'pack build' command to produce runnable application image: {ex}")

        if not could_build_image:
            raise CLIError("No supported builder could be used to build an image from the provided application source.")

        # Run 'docker push' to push the image to the container registry
        self._docker_push_to_container_registry(image_name, False)

    def build_container_from_source_with_acr_task(self, image_name, source):
        from azure.cli.command_modules.acr.task import acr_task_create, acr_task_run
        from azure.cli.command_modules.acr._client_factory import cf_acr_tasks, cf_acr_runs
        from azure.cli.core.profiles import ResourceType

        # Validate that the source provided is a directory, and not a file.
        if os.path.isfile(source):
            raise ValidationError(f"Impossible to build the artifact file {source} with ACR Task. Please make sure that you use --source and target a directory, or if you want to build your artifact locally, please make sure Docker is running on your machine.")

        task_name = "cli_build_containerapp"
        registry_name = (self.registry_server[: self.registry_server.rindex(ACR_IMAGE_SUFFIX)]).lower()
        if not self.target_port:
            self.target_port = DEFAULT_PORT
        task_content = ACR_TASK_TEMPLATE.replace("{{image_name}}", image_name).replace("{{target_port}}", str(self.target_port))
        task_client = cf_acr_tasks(self.cmd.cli_ctx)
        run_client = cf_acr_runs(self.cmd.cli_ctx)
        task_command_kwargs = {"resource_type": ResourceType.MGMT_CONTAINERREGISTRY, 'operation_group': 'webhooks'}
        old_command_kwargs = {}
        for key in task_command_kwargs:  # pylint: disable=consider-using-dict-items
            old_command_kwargs[key] = self.cmd.command_kwargs.get(key)
            self.cmd.command_kwargs[key] = task_command_kwargs[key]

        with NamedTemporaryFile(mode="w", delete=False) as task_file:
            try:
                task_file.write(task_content)
                task_file.flush()
                acr_task_create(self.cmd, task_client, task_name, registry_name, context_path="/dev/null", file=task_file.name)
                logger.warning("Created ACR task %s in registry %s", task_name, registry_name)
            finally:
                task_file.close()

            from time import sleep
            sleep(10)

            logger.warning("Running ACR build...")
            try:
                acr_task_run(self.cmd, run_client, task_name, registry_name, file=task_file.name, context_path=source)
            except CLIError as e:
                logger.error("Failed to automatically generate a docker container from your source. \n"
                             "See the ACR logs above for more error information. \nPlease check the supported languages for autogenerating docker containers (https://aka.ms/SourceToCloudSupportedVersions), "
                             "or consider using a Dockerfile for your app.")
                raise e
            finally:
                os.unlink(task_file.name)

        for k, v in old_command_kwargs.items():
            self.cmd.command_kwargs[k] = v

    def run_source_to_cloud_flow(self, source, dockerfile, build_env_vars, can_create_acr_if_needed, registry_server):
        image_name = self.image if self.image is not None else self.name
        from datetime import datetime

        # Creating a tag for the image using the current time to avoid overwriting customer's existing images
        now = datetime.now()
        tag_cli_prefix = "cli-containerapp"
        tag_now_suffix = str(now).replace(" ", "").replace("-", "").replace(".", "").replace(":", "")
        image_name_with_tag = image_name + ":{}-{}".format(tag_cli_prefix, tag_now_suffix)
        self.image = self.registry_server + "/" + image_name_with_tag

        if _has_dockerfile(source, dockerfile):
            logger.warning("Dockerfile detected. Running the build through ACR.")
            # ACR Task is the only way we have for now to build a Dockerfile using Docker.
            if can_create_acr_if_needed:
                self.create_acr_if_needed()
            elif not registry_server:
                raise RequiredArgumentMissingError("Usage error: --registry-server is required while using --source with a Dockerfile")
            elif ACR_IMAGE_SUFFIX not in registry_server:
                raise InvalidArgumentValueError("Usage error: --registry-server: expected an ACR registry (*.azurecr.io) for --source with a Dockerfile")
            self.image = self.registry_server + "/" + image_name_with_tag
            queue_acr_build(
                self.cmd,
                self.acr.resource_group.name,
                self.acr.name,
                image_name_with_tag,
                source,
                dockerfile,
                False
            )
            return False

        location = "eastus"
        if self.env.location:
            location = self.env.location
        if self.should_create_acr:
            # No container registry provided. Let's use the default container registry through Cloud Build.
            self.image = self.build_container_from_source_with_cloud_build_service(source, build_env_vars, location)
            return True

        if can_create_acr_if_needed:
            self.create_acr_if_needed()
        elif not registry_server:
            raise RequiredArgumentMissingError("Usage error: --registry-server is required while using --source or --artifact in this context")
        elif ACR_IMAGE_SUFFIX not in registry_server:
            raise InvalidArgumentValueError("Usage error: --registry-server: expected an ACR registry (*.azurecr.io) for --source or --artifact in this context")

        # At this point in the logic, we know that the customer doesn't have a Dockerfile but has a container registry.
        # Cloud Build is not an option anymore as we don't support BYO container registry yet.

        if is_docker_running():
            # Build the app with a constant 'build-cache' tag to leverage the local cache containing build layers
            # NOTE: this 'build-cache' tag will not be pushed to the user's registry, only maintained locally
            build_image_name_with_cache_tag = f"{image_name}:build-cache"
            self.build_container_from_source_with_buildpack(image_name_with_tag, source, build_image_name_with_cache_tag, build_env_vars)
            self.image = self.registry_server + "/" + image_name_with_tag
            return False

        # Fall back to ACR Task
        self.build_container_from_source_with_acr_task(image_name_with_tag, source)
        return False


class Extension:
    def __init__(
            self,
            cmd,
            name=None,
            exists: bool = None,
            namespace=None,
            logs_location=None,
            logs_rg=None,
            logs_customer_id=None,
            logs_share_key=None,
            connected_cluster_id=None
    ):
        self.cmd = cmd
        self.name = name
        self.exists = exists
        self.namespace = namespace
        self.logs_location = logs_location
        self.logs_rg = logs_rg
        self.logs_customer_id = logs_customer_id
        self.logs_share_key = logs_share_key
        self.connected_cluster_id = connected_cluster_id

    def create(self):
        extension = create_extension(cmd=self.cmd,
                                     extension_name=self.name,
                                     connected_cluster_id=self.connected_cluster_id,
                                     namespace=self.namespace,
                                     logs_customer_id=self.logs_customer_id,
                                     logs_share_key=self.logs_share_key,
                                     location=self.logs_location,
                                     logs_rg=self.logs_rg)
        self.exists = True
        return extension

    def create_if_needed(self):
        # if name is None, that means no need to create an extension
        if self.name is None:
            return
        if not self.check_exists():
            logger.warning(
                f"Creating {type(self).__name__} '{self.name}' in connected cluster {self.connected_cluster_id}"
            )
            self.create()
        else:
            logger.warning(
                f"Using {type(self).__name__} '{self.name}' in connected cluster {self.connected_cluster_id}"
            )  # TODO use .info()

    def check_exists(self):
        if self.name is None or self.connected_cluster_id is None:
            self.exists = False
        else:
            self.exists = self.get() is not None
        return self.exists

    def get(self):
        r = None
        try:
            r = self._get()
        except HttpResponseError as ex:  # pylint: disable=bare-except
            handle_non_404_status_code_exception(ex)
        return r

    def _get(self):
        return get_cluster_extension(self.cmd, self.get_rid())

    def get_rid(self):
        rid = self.name
        if not is_valid_resource_id(self.name):
            rid = "{}/providers/Microsoft.KubernetesConfiguration/extensions/{}".format(self.connected_cluster_id, self.name)
        return rid


class CustomLocation(Resource):
    def __init__(
        self,
        cmd,
        name: str,
        resource_group_name=None,
        exists: bool = None,
        location=None,
        namespace=None,
        cluster_extension_id=None,
        connected_cluster_id=None,
    ):
        resource_group = ResourceGroup(cmd, resource_group_name, location)
        super().__init__(cmd, name, resource_group, exists)
        self.resource_group_name = resource_group_name
        self.exists = exists
        self.location = location
        self.namespace = namespace
        self.cluster_extension_id = cluster_extension_id
        self.connected_cluster_id = connected_cluster_id

        if is_valid_resource_id(name):
            custom_location_dict = parse_resource_id(name)
            self.name = custom_location_dict["name"]
            self.exists = True
            if "resource_group" in custom_location_dict:
                self.resource_group_name = custom_location_dict["resource_group"]

    def create(self):
        register_provider_if_needed(self.cmd, EXTENDED_LOCATION_RP)
        custom_location = create_custom_location(
            cmd=self.cmd,
            custom_location_name=self.name,
            resource_group=self.resource_group_name,
            location=self.location,
            connected_cluster_id=self.connected_cluster_id,
            cluster_extension_id=self.cluster_extension_id,
            namespace=self.namespace
        )
        self.exists = True
        return custom_location

    def create_if_needed(self):
        if self.name is None:
            return
        if not self.exists:
            logger.warning(
                f"Creating {type(self).__name__} '{self.name}' in resource group {self.resource_group_name}"
            )
            self.create()
        else:
            logger.warning(
                f"Using {type(self).__name__} '{self.name}' in resource group {self.resource_group_name}"
            )  # TODO use .info()

    def _get(self):
        return get_custom_location(self.cmd, custom_location_id=self.get_rid())

    def set_name(self, name_or_rid):
        if is_valid_resource_id(name_or_rid):
            custom_location_dict = parse_resource_id(name_or_rid)
            self.name = custom_location_dict["name"]
            if "resource_group" in custom_location_dict:
                self.resource_group_name = custom_location_dict["resource_group"]
        else:
            self.name = name_or_rid

    def get_rid(self):
        rid = self.name
        if not is_valid_resource_id(self.name):
            rid = resource_id(
                subscription=get_subscription_id(self.cmd.cli_ctx),
                resource_group=self.resource_group_name,
                namespace=EXTENDED_LOCATION_RP,
                type=CUSTOM_LOCATION_RESOURCE_TYPE,
                name=self.name,
            )
        return rid


def _create_service_principal(cmd, resource_group_name, env_resource_group_name):
    logger.warning(
        "No valid service principal provided. Creating a new service principal..."
    )
    scopes = [
        f"/subscriptions/{get_subscription_id(cmd.cli_ctx)}/resourceGroups/{resource_group_name}"
    ]
    if (
        env_resource_group_name is not None
        and env_resource_group_name != resource_group_name
    ):
        scopes.append(
            f"/subscriptions/{get_subscription_id(cmd.cli_ctx)}/resourceGroups/{env_resource_group_name}"
        )
    sp = create_service_principal_for_github_action(cmd, scopes=scopes, role="contributor")

    logger.warning(f"Created service principal with ID {sp['appId']}")

    return sp["appId"], sp["password"], sp["tenant"]


def _get_or_create_sp(  # pylint: disable=inconsistent-return-statements
    cmd,
    resource_group_name,
    env_resource_group_name,
    name,
    service_principal_client_id,
    service_principal_client_secret,
    service_principal_tenant_id,
):
    if service_principal_client_id and service_principal_client_secret and service_principal_tenant_id:
        return (
            service_principal_client_id,
            service_principal_client_secret,
            service_principal_tenant_id,
        )
    try:
        GitHubActionClient.show(
            cmd=cmd, resource_group_name=resource_group_name, name=name
        )
        return (
            service_principal_client_id,
            service_principal_client_secret,
            service_principal_tenant_id,
        )
    except:  # pylint: disable=bare-except
        service_principal = None

        # TODO if possible, search for SPs with the right credentials
        # I haven't found a way to get SP creds + secrets yet from the API

        if not service_principal:
            return _create_service_principal(
                cmd, resource_group_name, env_resource_group_name
            )
        # return client_id, secret, tenant_id


def _get_dockerfile_content_from_repo(
    repo_url, branch, token, context_path, dockerfile
):
    from github import Github

    g = Github(token)
    context_path = context_path or "."
    repo = repo_url_to_name(repo_url)
    try:
        r = g.get_repo(repo)
        if not branch:
            branch = r.default_branch
    except Exception as e:
        raise ValidationError(f"Could not find repo {repo_url}") from e
    try:
        files = r.get_contents(context_path, ref=branch)
    except Exception as e:
        raise ValidationError(f"Could not find branch {branch}") from e
    for f in files:
        if f.path == dockerfile or f.path.endswith(f"/{dockerfile}"):
            resp = requests.get(f.download_url)
            if resp.ok and resp.content:
                return resp.content.decode("utf-8").split("\n")
    raise ValidationError("Could not find Dockerfile in Github repo/branch. Please ensure it is named 'Dockerfile'. "
                          "Set the path with --context-path if not in the root directory.")


def _get_ingress_and_target_port(ingress, target_port, dockerfile_content: "list[str]"):
    if not target_port and not ingress and dockerfile_content is not None:  # pylint: disable=too-many-nested-blocks
        for line in dockerfile_content:
            if line:
                line = (
                    line.upper()
                    .strip()
                    .replace("/TCP", "")
                    .replace("/UDP", "")
                    .replace("\n", "")
                )
                if line and line[0] != "#":
                    if "EXPOSE" in line:
                        parts = line.split(" ")
                        for i, p in enumerate(parts[:-1]):
                            if "EXPOSE" in p and is_int(parts[i + 1]):
                                target_port = parts[i + 1]
                                ingress = "external"
                                logger.warning(
                                    "Adding external ingress port {} based on dockerfile expose.".format(
                                        target_port
                                    )
                                )
    ingress = "external" if target_port and not ingress else ingress
    return ingress, target_port


def _validate_up_args(cmd, source, artifact, build_env_vars, image, repo, registry_server):
    disallowed_params = ["--only-show-errors", "--output", "-o"]
    command_args = cmd.cli_ctx.data.get("safe_params", [])
    for a in disallowed_params:
        if a in command_args:
            raise ValidationError(f"Argument {a} is not allowed for 'az containerapp up'")

    if not source and not artifact and not image and not repo:
        raise RequiredArgumentMissingError(
            "You must specify either --source, --artifact, --repo, or --image"
        )
    if source and repo:
        raise MutuallyExclusiveArgumentError(
            "Cannot use --source and --repo together. "
            "Can either deploy from a local directory or a Github repo"
        )
    if build_env_vars and not source and not artifact and not repo:
        raise RequiredArgumentMissingError(
            "--build_env_vars must be used with --source, --artifact, or --repo together"
        )
    _validate_source_artifact_args(source, artifact)
    if repo and registry_server and "azurecr.io" in registry_server:
        parsed = urlparse(registry_server)
        registry_name = (parsed.netloc if parsed.scheme else parsed.path).split(".")[0]
        if registry_name and len(registry_name) > MAXIMUM_SECRET_LENGTH:
            raise ValidationError(f"--registry-server ACR name must be less than {MAXIMUM_SECRET_LENGTH} "
                                  "characters when using --repo")


def _validate_custom_location_connected_cluster_args(cmd, env, resource_group_name, location, custom_location_id, connected_cluster_id):
    if custom_location_id or connected_cluster_id:
        register_provider_if_needed(cmd, EXTENDED_LOCATION_RP)
        register_provider_if_needed(cmd, KUBERNETES_CONFIGURATION_RP)
        if location:
            _ensure_location_allowed(cmd, location, CONTAINER_APPS_RP, CONNECTED_ENVIRONMENT_RESOURCE_TYPE)
        if custom_location_id:
            _validate_custom_loc_and_location(cmd, custom_location_id=custom_location_id, env=env, connected_cluster_id=connected_cluster_id, env_rg=resource_group_name)
        if connected_cluster_id:
            _validate_connected_k8s_exists(cmd, connected_cluster_id)


def _validate_source_artifact_args(source, artifact):
    if source and artifact:
        raise MutuallyExclusiveArgumentError(
            "Cannot use --source and --artifact together."
        )
    if source:
        if not os.path.exists(source):
            raise ValidationError(f"Impossible to find the source directory corresponding to {source}. Please make sure that this path exists.")
        if not os.path.isdir(source):
            raise ValidationError(f"The path corresponding to {source} is not a directory. Please make sure that the path given to --source is a directory.")
    if artifact:
        if not os.path.exists(artifact):
            raise ValidationError(f"Impossible to find the artifact file corresponding to {artifact}. Please make sure that this path exists.")
        if not os.path.isfile(artifact):
            raise ValidationError(f"The path corresponding to {artifact} is not a file. Please make sure that the path given to --artifact is a file.")


def _reformat_image(source, repo, image):
    if source and (image or repo):
        image = image.split("/")[-1]  # if link is given
        image = image.replace(":", "")
    return image


def _has_dockerfile(source, dockerfile):
    try:
        content = _get_dockerfile_content_local(source, dockerfile)
        return bool(content)
    except InvalidArgumentValueError:
        return False


def _get_dockerfile_content_local(source, dockerfile):
    lines = []
    if source:
        dockerfile_location = f"{source}/{dockerfile}"
        try:
            with open(dockerfile_location, "r") as fh:  # pylint: disable=unspecified-encoding
                lines = list(fh)
        except Exception as e:
            raise InvalidArgumentValueError(
                "Cannot open specified Dockerfile. Check dockerfile name, path, and permissions."
            ) from e
    return lines


def _get_dockerfile_content(repo, branch, token, source, context_path, dockerfile):
    if source:
        return _get_dockerfile_content_local(source, dockerfile)
    elif repo:
        return _get_dockerfile_content_from_repo(
            repo, branch, token, context_path, dockerfile
        )
    return []


def _get_app_env_and_group(
    cmd, name, resource_group: "ResourceGroup", env: "ContainerAppEnvironment", location, custom_location: "CustomLocation"
):
    matched_apps = []
    # If no resource group is provided, we need to search for the app in all resource groups
    if not resource_group.name and not resource_group.exists:
        matched_apps = [c for c in list_containerapp(cmd) if c["name"].lower() == name.lower()]

    # If a resource group is provided, we need to search for the app in that resource group
    if resource_group.name and resource_group.exists:
        matched_apps = [c for c in list_containerapp(cmd, resource_group_name=resource_group.name) if c["name"].lower() == name.lower()]

    # If env is provided, we need to search for the app in that env
    if env.name:
        matched_apps = [c for c in matched_apps if parse_resource_id(c["properties"]["environmentId"])["name"].lower() == env.name.lower()]

    # If location is provided, we need to search for the app in that location
    if location:
        matched_apps = [c for c in matched_apps if format_location(c["location"]) == format_location(location)]

    if env.custom_location_id:
        matched_apps = [c for c in matched_apps if (c.get("extendedLocation") and c["extendedLocation"]["name"].lower() == env.custom_location_id.lower())]
    elif env.resource_type:
        matched_apps = [c for c in matched_apps if parse_resource_id(c["properties"]["environmentId"])["resource_type"].lower() == env.resource_type.lower()]
    if custom_location.connected_cluster_id:
        matched_apps = _filter_containerapps_by_connected_cluster_id(cmd, matched_apps, custom_location.connected_cluster_id)

    # If there is only one app that matches the criteria, we can set the env name and resource group name
    if len(matched_apps) == 1:
        resource_group.name = parse_resource_id(matched_apps[0]["id"])[
            "resource_group"
        ]
        env.set_name(matched_apps[0]["properties"]["environmentId"])
    # If there are multiple apps that match the criteria, we need to ask the user to specify the env name and resource group name
    elif len(matched_apps) > 1:
        raise ValidationError(
            f"There are multiple containerapps with name {name} on the subscription. "
            "Please specify which resource group your Containerapp is in."
        )


def _filter_containerapps_by_connected_cluster_id(cmd, matched_apps, connected_cluster_id):
    result_apps = []
    for app in matched_apps:
        if app.get("extendedLocation"):
            custom_location_from_app = get_custom_location(cmd=cmd, custom_location_id=app["extendedLocation"]["name"])
            if custom_location_from_app and connected_cluster_id.lower() == custom_location_from_app.host_resource_id.lower():
                result_apps.append(app)
    return result_apps


# If the connected cluster already have a custom location (with ext namespace) bind to the container app ext, uses it.
def _prepare_custom_location_args(
        cmd,
        custom_location: "CustomLocation",
        extension: "Extension"
):
    if custom_location.name is None:
        if custom_location.connected_cluster_id is None:
            raise ValidationError("please specify one of --connected-cluster-id or --custom-location you want to create the Connected Environment or specify the existing Connected Environment with --environment.")

        connected_cluster = get_connected_k8s(cmd, custom_location.connected_cluster_id)
        custom_location.location = connected_cluster.location
        extension_list = list_cluster_extensions(cmd, connected_cluster_id=custom_location.connected_cluster_id)
        for e in extension_list:
            if e.extension_type.lower() == CONTAINER_APP_EXTENSION_TYPE:
                extension.exists = True
                extension.name = e.name
                extension.namespace = e.scope.cluster.release_namespace
                custom_location.cluster_extension_id = e.id
                custom_location.namespace = e.scope.cluster.release_namespace
                custom_location_list = list_custom_location(cmd,
                                                            connected_cluster_id=custom_location.connected_cluster_id)
                for c in custom_location_list:
                    if e.id in c.cluster_extension_ids and e.scope.cluster.release_namespace == c.namespace:
                        custom_location.set_name(c.id)
                        custom_location.exists = True
                        break
                break
    else:
        custom_location.location = get_custom_location(cmd, custom_location_id=custom_location.get_rid()).location


def _get_env_and_group_from_log_analytics(
    cmd,
    resource_group_name,
    env: "ContainerAppEnvironment",
    resource_group: "ResourceGroup",
    logs_customer_id,
    location,
):
    # For connected environment, the log customer id is bind in the configuration_protected_settings of connected cluster , which can not be read.
    if env.is_connected_environment():
        return
    # resource_group_name is the value the user passed in (if present)
    if not env.name:
        if (resource_group_name == resource_group.name and resource_group.exists) or (
            not resource_group_name
        ):
            env_list = list_managed_environments(
                cmd=cmd, resource_group_name=resource_group_name
            )
            if logs_customer_id:
                env_list = [
                    e
                    for e in env_list
                    if safe_get(
                        e,
                        "properties",
                        "appLogsConfiguration",
                        "logAnalyticsConfiguration",
                        "customerId",
                    )
                    == logs_customer_id
                ]
            if location:
                env_list = [e for e in env_list if format_location(e["location"]) == format_location(location)]
            if env_list:
                # TODO check how many CA in env
                env_details = parse_resource_id(env_list[0]["id"])
                env.set_name(env_details["name"])
                resource_group.name = env_details["resource_group"]


def _get_acr_from_image(cmd, app):
    if app.image is not None and "azurecr.io" in app.image:
        app.registry_server = app.image.split("/")[
            0
        ]  # TODO what if this conflicts with registry_server param?
        parsed = urlparse(app.image)
        registry_name = (parsed.netloc if parsed.scheme else parsed.path).split(".")[0]
        if app.registry_user is None or app.registry_pass is None:
            logger.info(
                "No credential was provided to access Azure Container Registry. Trying to look up..."
            )
            try:
                app.registry_user, app.registry_pass, registry_rg = _get_acr_cred(
                    cmd.cli_ctx, registry_name
                )
                app.acr = AzureContainerRegistry(
                    registry_name, ResourceGroup(cmd, registry_rg, None, None)
                )
            except Exception as ex:
                raise RequiredArgumentMissingError(
                    "Failed to retrieve credentials for container registry. Please provide the registry username and password"
                ) from ex
        else:
            acr_rg = _get_acr_rg(app)
            app.acr = AzureContainerRegistry(
                name=registry_name,
                resource_group=ResourceGroup(app.cmd, acr_rg, None, None),
            )


def _get_registry_from_app(app, source):
    containerapp_def = app.get()
    existing_registries = safe_get(containerapp_def, "properties", "configuration", "registries", default=[])
    if source:
        existing_registries = [r for r in existing_registries if ACR_IMAGE_SUFFIX in r["server"]]
    if containerapp_def:
        if len(existing_registries) == 1:
            app.registry_server = existing_registries[0]["server"]
        elif len(existing_registries) > 1:  # default to registry in image if possible, otherwise don't infer
            containers = safe_get(containerapp_def, "properties", "template", "containers", default=[])
            image_server = next(c["image"] for c in containers if c["name"].lower() == app.name.lower()).split('/')[0]
            if image_server in [r["server"] for r in existing_registries]:
                app.registry_server = image_server


def _get_acr_rg(app):
    registry_name = app.registry_server[: app.registry_server.rindex(ACR_IMAGE_SUFFIX)]
    client = get_mgmt_service_client(
        app.cmd.cli_ctx, ContainerRegistryManagementClient
    ).registries
    return parse_resource_id(acr_show(app.cmd, client, registry_name).id)[
        "resource_group"
    ]


def _get_default_registry_name(app):
    import hashlib

    h = hashlib.sha256()
    h.update(f"{get_subscription_id(app.cmd.cli_ctx)}/{app.env.resource_group.name}/{app.env.name}".encode("utf-8"))

    registry_name = f"{h.hexdigest()}"[:10]  # cap at 15 characters total
    return f"ca{registry_name}acr"  # ACR names must start + end in a letter


def _set_acr_creds(cmd, app: "ContainerApp", registry_name):
    logger.info("No credential was provided to access Azure Container Registry. Trying to look up...")
    try:
        app.registry_user, app.registry_pass, registry_rg = _get_acr_cred(
            cmd.cli_ctx, registry_name
        )
        return registry_rg
    except Exception as ex:
        raise RequiredArgumentMissingError(
            "Failed to retrieve credentials for container registry. Please provide the registry username and password"
        ) from ex


def _get_registry_details(cmd, app: "ContainerApp", source):
    registry_rg = None
    registry_name = None
    if app.registry_server:
        if "azurecr.io" not in app.registry_server and source:
            raise ValidationError(
                "Cannot supply non-Azure registry when using --source."
            )
        parsed = urlparse(app.registry_server)
        registry_name = (parsed.netloc if parsed.scheme else parsed.path).split(".")[0]
        if app.registry_user is None or app.registry_pass is None:
            registry_rg = _set_acr_creds(cmd, app, registry_name)
        else:
            registry_rg = _get_acr_rg(app)
    else:
        registry_name, registry_rg = find_existing_acr(cmd, app)
        if registry_name and registry_rg:
            _set_acr_creds(cmd, app, registry_name)
            app.registry_server = registry_name + ACR_IMAGE_SUFFIX
        else:
            registry_rg = app.resource_group.name
            registry_name = _get_default_registry_name(app)
            app.registry_server = registry_name + ACR_IMAGE_SUFFIX
            app.should_create_acr = True

    app.acr = AzureContainerRegistry(
        registry_name, ResourceGroup(cmd, registry_rg, None, None)
    )


# attempt to populate defaults for managed env, RG, ACR, etc
def _set_up_defaults(
    cmd,
    name,
    resource_group_name,
    logs_customer_id,
    location,
    resource_group: "ResourceGroup",
    env: "ContainerAppEnvironment",
    app: "ContainerApp",
    custom_location: "CustomLocation",
    extension: "Extension",
    is_registry_server_params_set=None
):
    # If no RG passed in and a singular app exists with the same name, get its env and rg
    _get_app_env_and_group(cmd, name, resource_group, env, location, custom_location)

    # If no env passed or set in the previous step (and not creating a new RG), then get env by location from log analytics ID
    _get_env_and_group_from_log_analytics(cmd, resource_group_name, env, resource_group, logs_customer_id, location)

    # try to set RG name by env name
    # Find managed env with env name, if found, use it.
    # Try to set RG name by env name
    # If the unique environment is found, use it.
    if not env.is_connected_environment() and env.name and not resource_group.name:
        if not location:
            env_list = [e for e in list_managed_environments(cmd=cmd) if e["name"] == env.name]
        else:
            env_list = [e for e in list_managed_environments(cmd=cmd) if e["name"] == env.name and format_location(e["location"]) == format_location(location)]
        if len(env_list) == 1:
            resource_group.name = parse_resource_id(env_list[0]["id"])["resource_group"]
            env.resource_type = MANAGED_ENVIRONMENT_RESOURCE_TYPE
        if len(env_list) > 1:
            raise ValidationError(
                f"There are multiple environments with name {env.name} on the subscription. "
                "Please specify which resource group your Containerapp environment is in."
            )    # get ACR details from --image, if possible

    _infer_existing_connected_env(cmd, location, resource_group, env, custom_location)

    _infer_existing_custom_location_or_extension(cmd, name, location, resource_group, env, custom_location, extension)

    if not is_registry_server_params_set:
        _get_acr_from_image(cmd, app)


# Try to get existed connected environment
# 'not env.resource_type' is for command: -n <app_name> --environment <env_name>:
# When the resource type cannot be parsed from input arguments, we find managed environments with env name first, if found, use it. We have done this in the previous parts.
# If manged env is not found, the env.resource_type is None, looks for a connected env with env name, uses it if found. If mutiple connected envs are found, thow a error.
# (env.is_connected_environment() and (not env.name or not resource_group.name or not env.custom_location_id)) is for commands:
# -n <app_name> --connected-cluster-id
# -n <app_name> --custom-location
def _infer_existing_connected_env(
        cmd,
        location,
        resource_group: "ResourceGroup",
        env: "ContainerAppEnvironment",
        custom_location: "CustomLocation",
):
    if not env.resource_type or (env.is_connected_environment() and (not env.name or not resource_group.name or not env.custom_location_id)):
        connected_env_list = list_connected_environments(cmd=cmd, resource_group_name=resource_group.name)
        env_list = []
        for e in connected_env_list:
            if env.name and env.name != e["name"]:
                continue
            if location and format_location(e["location"]) != location:
                continue
            if custom_location.name and e["extendedLocation"]["name"].lower() != custom_location.get_rid().lower():
                continue
            if custom_location.connected_cluster_id:
                custom_location_from_env = get_custom_location(cmd=cmd, custom_location_id=e["extendedLocation"]["name"])
                if custom_location_from_env is None or custom_location.connected_cluster_id.lower() != custom_location_from_env.host_resource_id.lower():
                    continue
            env_list.append(e)

        if len(env_list) == 1:
            if not resource_group.name:
                resource_group.name = parse_resource_id(env_list[0]["id"])["resource_group"]
            env.set_name(env_list[0]["id"])
            env.custom_location_id = env_list[0]["extendedLocation"]["name"]
        if len(env_list) > 1:
            if env.name:
                raise ValidationError(
                    f"There are multiple Connected Environments with name {env.name} on the subscription. "
                    "Please specify which resource group your Connected environment is in."
                )  # get ACR details from --image, if possible
            else:
                if not resource_group.name:
                    resource_group.name = parse_resource_id(env_list[0]["id"])["resource_group"]
                env.set_name(env_list[0]["id"])
                env.custom_location_id = env_list[0]["extendedLocation"]["name"]


def _infer_existing_custom_location_or_extension(
        cmd,
        name,
        location,
        resource_group: "ResourceGroup",
        env: "ContainerAppEnvironment",
        custom_location: "CustomLocation",
        extension: "Extension"
):
    # Try to get existed custom location and extension
    # Set up default values for not existed resources(env, custom location, extension)
    if env.is_connected_environment():
        if not env.check_exists():
            _prepare_custom_location_args(cmd, custom_location=custom_location, extension=extension)
            if location is None:
                env.location = custom_location.location
                resource_group.location = custom_location.location
            if custom_location.exists:
                env.custom_location_id = custom_location.get_rid()
            else:
                generated_resources_random_int = randint(0, 9999)
                resource_group.name = resource_group.name if resource_group.name else get_randomized_name(get_profile_username(), random_int=generated_resources_random_int)
                custom_location.name = custom_location.name if custom_location.name else get_randomized_name_with_dash(prefix=get_profile_username(), initial="env-location", random_int=generated_resources_random_int)
                custom_location.resource_group_name = resource_group.name
                env.custom_location_id = custom_location.get_rid()
                # If not existed extension, set up values for creating
                if not extension.exists:
                    extension.name = DEFAULT_CONNECTED_CLUSTER_EXTENSION_NAME
                    extension.namespace = DEFAULT_CONNECTED_CLUSTER_EXTENSION_NAMESPACE
                    extension.logs_rg = resource_group.name
                    extension.logs_location = resource_group.location
                    custom_location.namespace = DEFAULT_CONNECTED_CLUSTER_EXTENSION_NAMESPACE
                    custom_location.cluster_extension_id = extension.get_rid()


def _create_github_action(
    app: "ContainerApp",
    env: "ContainerAppEnvironment",
    service_principal_client_id,
    service_principal_client_secret,
    service_principal_tenant_id,
    branch,
    token,
    repo,
    context_path,
    build_env_vars,
):

    sp = _get_or_create_sp(
        app.cmd,
        app.resource_group.name,
        env.resource_group.name,
        app.name,
        service_principal_client_id,
        service_principal_client_secret,
        service_principal_tenant_id,
    )
    (
        service_principal_client_id,
        service_principal_client_secret,
        service_principal_tenant_id,
    ) = sp

    create_or_update_github_action(
        cmd=app.cmd,
        name=app.name,
        resource_group_name=app.resource_group.name,
        repo_url=repo,
        registry_url=app.registry_server,
        registry_username=app.registry_user,
        registry_password=app.registry_pass,
        branch=branch,
        token=token,
        login_with_github=False,
        service_principal_client_id=service_principal_client_id,
        service_principal_client_secret=service_principal_client_secret,
        service_principal_tenant_id=service_principal_tenant_id,
        image=app.image,
        context_path=context_path,
        build_env_vars=build_env_vars,
        trigger_existing_workflow=True,
    )


def up_output(app: 'ContainerApp', no_dockerfile):
    url = safe_get(
        ContainerAppPreviewClient.show(app.cmd, app.resource_group.name, app.name),
        "properties",
        "configuration",
        "ingress",
        "fqdn",
    )
    if url and not url.startswith("http"):
        url = f"http://{url}"

    logger.warning(
        f"\nYour container app {app.name} has been created and deployed! Congrats! \n"
    )
    if no_dockerfile and app.ingress:
        logger.warning(f"Your app is running image {app.image} and listening on port {app.target_port}")

    url and logger.warning(f"Browse to your container app at: {url} \n")
    logger.warning(
        f"Stream logs for your container with: az containerapp logs show -n {app.name} -g {app.resource_group.name} \n"
    )
    logger.warning(
        f"See full output using: az containerapp show -n {app.name} -g {app.resource_group.name} \n"
    )


def find_existing_acr(cmd, app: "ContainerApp"):
    from azure.cli.command_modules.acr._client_factory import cf_acr_registries
    client = cf_acr_registries(cmd.cli_ctx)

    acr = None
    try:
        acr = acr_show(cmd, client=client, registry_name=_get_default_registry_name(app))
    except Exception:
        pass

    if acr:
        app.should_create_acr = False
        return acr.name, parse_resource_id(acr.id)["resource_group"]
    return None, None


def check_env_name_on_rg(cmd, env, resource_group_name, location, custom_location_id=None, connected_cluster_id=None):
    env_name = env
    resource_type = None
    if is_valid_resource_id(env):
        env_dict = parse_resource_id(env)
        env_name = env_dict.get("name")
        resource_group_name = env_dict.get("resource_group")
        resource_type = env_dict.get("resource_type")
    if resource_type is None:
        if custom_location_id or connected_cluster_id:
            resource_type = CONNECTED_ENVIRONMENT_RESOURCE_TYPE
    if location:
        _ensure_location_allowed(cmd, location, CONTAINER_APPS_RP, resource_type if resource_type else "managedEnvironments")
    if env and resource_group_name:
        env_def = None
        try:
            if resource_type and CONNECTED_ENVIRONMENT_RESOURCE_TYPE.lower() == resource_type.lower():
                env_def = ConnectedEnvironmentClient.show(cmd, resource_group_name, env_name)
            else:
                env_def = ManagedEnvironmentPreviewClient.show(cmd, resource_group_name, env_name)
        except Exception as e:  # pylint: disable=bare-except
            handle_non_404_status_code_exception(e)
        if env_def:
            if location and format_location(location) != format_location(env_def["location"]):
                raise ValidationError("Environment {} already exists in resource group {} on location {}, cannot change location of existing environment to {}.".format(env_name, resource_group_name, env_def["location"], location))
            if resource_type and CONNECTED_ENVIRONMENT_RESOURCE_TYPE.lower() == resource_type.lower():
                if custom_location_id and env_def["extendedLocation"]["name"].lower() != custom_location_id.lower():
                    raise ValidationError("Environment {} already exists in resource group {} with custom location {}, cannot change custom location of existing environment to {}.".format(env_name, resource_group_name, env_def["extendedLocation"]["name"], custom_location_id))
                if connected_cluster_id:
                    custom_location_from_env = get_custom_location(cmd=cmd, custom_location_id=env_def["extendedLocation"]["name"])
                    if connected_cluster_id.lower() != custom_location_from_env.host_resource_id.lower():
                        raise ValidationError("Environment {} already exists in resource group {} on connected cluster {}, cannot change connected cluster of existing environment to {}.".format(env_name, custom_location_from_env.host_resource_id, env_def["location"], connected_cluster_id))


def get_token(cmd, repo, token):
    if not repo:
        return None
    if token:
        return token
    token = load_github_token_from_cache(cmd, repo)
    if not token:
        token = get_github_access_token(cmd, ["admin:repo_hook", "repo", "workflow"], token)
    return token
