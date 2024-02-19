# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import math
import shutil
import subprocess
from abc import ABC, abstractmethod
from functools import lru_cache
from pathlib import Path
from time import sleep
from typing import Any, MutableMapping, Optional

from azext_aosm.configuration_models.common_parameters_config import (
    BaseCommonParametersConfig,
    NFDCommonParametersConfig,
)
from azext_aosm.vendored_sdks.azure_storagev2.blob.v2022_11_02 import (
    BlobClient,
    BlobType,
)
from azext_aosm.vendored_sdks.models import ArtifactType
from azext_aosm.vendored_sdks import HybridNetworkManagementClient
from azext_aosm.common.command_context import CommandContext
from azext_aosm.common.utils import convert_bicep_to_arm
from knack.util import CLIError
from knack.log import get_logger
from oras.client import OrasClient

logger = get_logger(__name__)


# TODO: Split these out into separate files, probably in a new artifacts module
class BaseArtifact(ABC):
    """Abstract base class for artifacts."""

    def __init__(self, artifact_name: str, artifact_type: str, artifact_version: str):
        self.artifact_name = artifact_name
        self.artifact_type = artifact_type
        self.artifact_version = artifact_version

    def to_dict(self) -> dict:
        """Convert an instance to a dict."""
        output_dict = {"type": ARTIFACT_CLASS_TO_TYPE[type(self)]}
        output_dict.update({k: vars(self)[k] for k in vars(self)})
        return output_dict

    @abstractmethod
    def upload(
        self, config: BaseCommonParametersConfig, command_context: CommandContext
    ):
        """Upload the artifact."""


class BaseACRArtifact(BaseArtifact):
    """Abstract base class for ACR artifacts."""

    @abstractmethod
    def upload(
        self, config: BaseCommonParametersConfig, command_context: CommandContext
    ):
        """Upload the artifact."""

    @staticmethod
    def _check_tool_installed(tool_name: str) -> None:
        """
        Check whether a tool such as docker or helm is installed.

        :param tool_name: name of the tool to check, e.g. docker
        """
        if shutil.which(tool_name) is None:
            raise CLIError(f"You must install {tool_name} to use this command.")

    @staticmethod
    def _clean_name(registry_name: str) -> str:
        """Remove https:// from the registry name."""
        return registry_name.replace("https://", "")

    @staticmethod
    def _call_subprocess_raise_output(cmd: list) -> None:
        """
        Call a subprocess and raise a CLIError with the output if it fails.

        :param cmd: command to run, in list format
        :raise CLIError: if the subprocess fails
        """
        log_cmd = cmd.copy()
        if "--password" in log_cmd:
            # Do not log out passwords.
            log_cmd[log_cmd.index("--password") + 1] = "[REDACTED]"

        try:
            called_process = subprocess.run(
                cmd, encoding="utf-8", capture_output=True, text=True, check=True
            )
            logger.debug(
                "Output from %s: %s. Error: %s",
                log_cmd,
                called_process.stdout,
                called_process.stderr,
            )
        except subprocess.CalledProcessError as error:
            all_output: str = (
                f"Command: {' '.join(log_cmd)}\n"
                f"stdout: {error.stdout}\n"
                f"stderr: {error.stderr}\n"
                f"Return code: {error.returncode}"
            )
            logger.debug("The following command failed to run:\n%s", all_output)
            # Raise the error without the original exception, which may contain secrets.
            raise CLIError(all_output) from None

    @staticmethod
    @lru_cache(maxsize=32)
    def _manifest_credentials(
        config: BaseCommonParametersConfig,
        aosm_client: HybridNetworkManagementClient,
    ) -> MutableMapping[str, Any]:
        """Gets the details for uploading the artifacts in the manifest."""
        return aosm_client.artifact_manifests.list_credential(
            resource_group_name=config.publisherResourceGroupName,
            publisher_name=config.publisherName,
            artifact_store_name=config.acrArtifactStoreName,
            artifact_manifest_name=config.acrManifestName,
        ).as_dict()

    @staticmethod
    def _get_oras_client(manifest_credentials: MutableMapping[str, Any]) -> OrasClient:
        client = OrasClient(hostname=manifest_credentials["acr_server_url"])
        client.login(
            username=manifest_credentials["username"],
            password=manifest_credentials["acr_token"],
        )
        return client

    @staticmethod
    def _get_acr(upload_client: OrasClient) -> str:
        """
        Get the name of the ACR.

        :return: The name of the ACR
        """
        assert hasattr(upload_client, "remote")
        if not upload_client.remote.hostname:
            raise ValueError(
                "Cannot upload artifact. Oras client has no remote hostname."
            )
        return BaseACRArtifact._clean_name(upload_client.remote.hostname)


class LocalFileACRArtifact(BaseACRArtifact):
    """Class for ACR artifacts from a local file."""

    def __init__(self, artifact_name, artifact_type, artifact_version, file_path: Path):
        super().__init__(artifact_name, artifact_type, artifact_version)
        self.file_path = file_path

    def upload(
        self, config: BaseCommonParametersConfig, command_context: CommandContext
    ):
        """Upload the artifact."""
        logger.debug("LocalFileACRArtifact config: %s", config)

        # TODO: remove, this is temporary until we fix in artifact reader
        self.file_path = Path(self.file_path)
        # For NSDs, we provide paths relative to the artifacts folder, resolve them to absolute paths
        if not self.file_path.is_absolute():
            output_folder_path = command_context.cli_options["definition_folder"]
            resolved_path = output_folder_path.resolve()
            absolute_file_path = resolved_path / self.file_path
            self.file_path = absolute_file_path

        if self.file_path.suffix == ".bicep":
            # Uploading the nf_template as part of the NSD will use this code path
            # This does mean we can never have a bicep file as an artifact, but that should be OK
            logger.debug("Converting self.file_path to ARM")
            arm_template = convert_bicep_to_arm(self.file_path)
            self.file_path = self.file_path.with_suffix(".json")
            json.dump(arm_template, self.file_path.open("w"))
            logger.debug("Converted bicep file to ARM as: %s", self.file_path)

        manifest_credentials = self._manifest_credentials(
            config=config, aosm_client=command_context.aosm_client
        )
        oras_client = self._get_oras_client(manifest_credentials=manifest_credentials)
        target_acr = self._get_acr(oras_client)
        target = f"{target_acr}/{self.artifact_name}:{self.artifact_version}"
        logger.debug("Uploading %s to %s", self.file_path, target)

        if self.artifact_type == ArtifactType.ARM_TEMPLATE.value:
            retries = 0
            while True:
                try:
                    oras_client.push(files=[self.file_path], target=target)
                    break
                except ValueError as error:
                    if retries < 20:
                        logger.info(
                            "Retrying pushing local artifact to ACR. Retries so far: %s",
                            retries,
                        )
                        retries += 1
                        sleep(3)
                        continue

                    logger.error(
                        "Failed to upload %s to %s. Check if this image exists in the"
                        " source registry %s.",
                        self.file_path,
                        target,
                        target_acr,
                    )
                    logger.debug(error, exc_info=True)
                    raise error

            logger.info("LocalFileACRArtifact uploaded %s to %s using oras push", self.file_path, target)

        elif self.artifact_type == ArtifactType.OCI_ARTIFACT.value:

            target_acr_name = target_acr.replace(".azurecr.io", "")
            target_acr_with_protocol = f"oci://{target_acr}"
            username = manifest_credentials["username"]
            password = manifest_credentials["acr_token"]

            # TODO: Maybe port over the "if not use_manifest_permissions" feature which means you don't need to
            #       install docker. Although not having to install docker feels like a marginal enhancement, as most
            #       people playing with containers will have docker, or won't mind installing it. Note that
            #       use_manifest_permissions is now in command_context.cli_options['no_subscription_permissions']

            self._check_tool_installed("docker")
            self._check_tool_installed("helm")

            # TODO: don't just dump this in /tmp
            if self.file_path.is_dir():
                helm_package_cmd = [
                    str(shutil.which("helm")),
                    "package",
                    self.file_path,
                    "--destination",
                    "/tmp",
                ]
                self._call_subprocess_raise_output(helm_package_cmd)

            # This seems to prevent occasional helm login failures
            acr_login_cmd = [
                str(shutil.which("az")),
                "acr",
                "login",
                "--name",
                target_acr_name,
                "--username",
                username,
                "--password",
                password,
            ]
            self._call_subprocess_raise_output(acr_login_cmd)

            try:
                helm_login_cmd = [
                    str(shutil.which("helm")),
                    "registry",
                    "login",
                    target_acr,
                    "--username",
                    username,
                    "--password",
                    password,
                ]
                self._call_subprocess_raise_output(helm_login_cmd)

                push_command = [
                    str(shutil.which("helm")),
                    "push",
                    f"/tmp/{self.artifact_name}-{self.artifact_version}.tgz",  # TODO: fix up helm package to use non-tmp path
                    target_acr_with_protocol,
                ]
                self._call_subprocess_raise_output(push_command)
            finally:
                helm_logout_cmd = [
                    str(shutil.which("helm")),
                    "registry",
                    "logout",
                    target_acr,
                ]
                self._call_subprocess_raise_output(helm_logout_cmd)

            logger.info("LocalFileACRArtifact uploaded %s to %s using helm push", self.file_path, target)

        else:  # TODO: Make this one of the allowed Azure CLI exceptions
            raise ValueError(f"Unexpected artifact type. Got {self.artifact_type}. Expected {ArtifactType.ARM_TEMPLATE.value} or {ArtifactType.OCI_ARTIFACT.value}")


class RemoteACRArtifact(BaseACRArtifact):
    """Class for ACR artifacts from a remote ACR image."""

    def __init__(
        self,
        artifact_name,
        artifact_type,
        artifact_version,
        source_registry: str,
        source_registry_namespace: str,
    ):
        super().__init__(artifact_name, artifact_type, artifact_version)
        self.source_registry = source_registry
        self.source_registry_namespace = source_registry_namespace
        self.namespace_with_slash = (
            f"{source_registry_namespace}/" if source_registry_namespace else ""
        )

    def _pull_image_to_local_registry(
        self,
        source_registry_login_server: str,
        source_image: str,
    ) -> None:
        """
        Pull image to local registry using docker pull. Requires docker.

        Uses the CLI user's context to log in to the source registry.

        :param: source_registry_login_server: e.g. uploadacr.azurecr.io
        :param: source_image: source docker image name e.g.
            uploadacr.azurecr.io/samples/nginx:stable
        """
        try:
            # Login to the source registry with the CLI user credentials. This requires
            # docker to be installed.
            message = f"Logging into source registry {source_registry_login_server}"
            print(message)
            logger.info(message)
            acr_source_login_cmd = [
                str(shutil.which("az")),
                "acr",
                "login",
                "--name",
                source_registry_login_server,
            ]
            self._call_subprocess_raise_output(acr_source_login_cmd)
            message = f"Pulling source image {source_image}"
            print(message)
            logger.info(message)
            pull_source_image_cmd = [
                str(shutil.which("docker")),
                "pull",
                source_image,
            ]
            self._call_subprocess_raise_output(pull_source_image_cmd)
        except CLIError as error:
            logger.error(
                (
                    "Failed to pull %s. Check if this image exists in the"
                    " source registry %s."
                ),
                source_image,
                source_registry_login_server,
            )
            logger.debug(error, exc_info=True)
            raise error
        finally:
            docker_logout_cmd = [
                str(shutil.which("docker")),
                "logout",
                source_registry_login_server,
            ]
            self._call_subprocess_raise_output(docker_logout_cmd)

    def _push_image_from_local_registry(
        self,
        config: BaseCommonParametersConfig,
        command_context: CommandContext,
        local_docker_image: str,
    ):
        """
        Push image to target registry using docker push. Requires docker.

        :param local_docker_image: name and tag of the source image on local registry
            e.g. uploadacr.azurecr.io/samples/nginx:stable
        :type local_docker_image: str
        :param target_password: The password to use for the az acr login attempt
        :type target_password: str
        """
        logger.debug("RemoteACRArtifact config: %s", config)
        manifest_credentials = self._manifest_credentials(
            config=config, aosm_client=command_context.aosm_client
        )
        # TODO (WIBNI): All oras_client is used for (I think) is to get the target_acr.
        #               Is there a simpler way to do this?
        oras_client = self._get_oras_client(manifest_credentials=manifest_credentials)
        target_acr = self._get_acr(oras_client)
        target_username = manifest_credentials["username"]
        target_password = manifest_credentials["acr_token"]
        target = f"{target_acr}/{self.artifact_name}:{self.artifact_version}"
        logger.debug("Target ACR: %s", target)

        print("Tagging source image")
        tag_image_cmd = [
            str(shutil.which("docker")),
            "tag",
            local_docker_image,
            target,
        ]
        self._call_subprocess_raise_output(tag_image_cmd)

        logger.info(
            "Logging into artifact store registry %s", oras_client.remote.hostname
        )
        # ACR login seems to work intermittently, so we retry on failure
        retries = 0
        while True:
            try:
                target_acr_login_cmd = [
                    str(shutil.which("az")),
                    "acr",
                    "login",
                    "--name",
                    target_acr,
                    "--username",
                    target_username,
                    "--password",
                    target_password,
                ]
                self._call_subprocess_raise_output(target_acr_login_cmd)
                logger.debug("Logged in to %s", oras_client.remote.hostname)
                break
            except CLIError as error:
                if retries < 20:
                    logger.info("Retrying ACR login. Retries so far: %s", retries)
                    retries += 1
                    sleep(3)
                    continue
                logger.error(
                    ("Failed to login to %s as %s."), target_acr, target_username
                )
                logger.debug(error, exc_info=True)
                raise error

        try:
            print("Pushing target image using docker push")
            push_target_image_cmd = [
                str(shutil.which("docker")),
                "push",
                target,
            ]
            self._call_subprocess_raise_output(push_target_image_cmd)
        except CLIError as error:
            logger.error(
                ("Failed to push %s to %s."),
                local_docker_image,
                target_acr,
            )
            logger.debug(error, exc_info=True)
            raise error
        finally:
            docker_logout_cmd = [
                str(shutil.which("docker")),
                "logout",
                target_acr,
            ]
            self._call_subprocess_raise_output(docker_logout_cmd)

    def _copy_image(
        self,
        config: BaseCommonParametersConfig,
        command_context: CommandContext,
        source_registry_login_server: str,
        source_image: str,
    ):
        """
        Copy image from one ACR to another.

        Use az acr import to do the import image. Previously we used the python
        sdk `ContainerRegistryManagementClient.registries.begin_import_image`
        but this requires the source resource group name, which is more faff
        at configuration time.

        Neither `az acr import` or `begin_import_image` support using the username
        and acr_token retrieved from the manifest credentials, so this uses the
        CLI users context to access both the source registry and the target
        Artifact Store registry. This requires either Contributor role or a
        custom role that allows the importImage action over the whole subscription.

        :param source_registry: source registry login server e.g. https://uploadacr.azurecr.io
        :param source_image: source image including namespace and tags e.g.
                             samples/nginx:stable
        """
        logger.debug("RemoteACRArtifact (copy_image) config: %s", config)
        manifest_credentials = self._manifest_credentials(
            config=config, aosm_client=command_context.aosm_client
        )
        # TODO (WIBNI): All oras_client is used for (I think) is to get the target_acr.
        #               Is there a simpler way to do this?
        oras_client = self._get_oras_client(manifest_credentials=manifest_credentials)
        target_acr = self._get_acr(oras_client)
        try:
            print("Copying artifact from source registry")
            # In order to use az acr import cross subscription, we need to use a token
            # to authenticate to the source registry. This is documented as the way to
            # us az acr import cross-tenant, not cross-sub, but it also works
            # cross-subscription, and meant we didn't have to make a breaking change to
            # the format of input.json. Our usage here won't work cross-tenant since
            # we're attempting to get the token (source) with the same context as that
            # in which we are creating the ACR (i.e. the target tenant)
            get_token_cmd = [str(shutil.which("az")), "account", "get-access-token"]
            # Dont use _call_subprocess_raise_output here as we don't want to log the
            # output
            called_process = subprocess.run(  # noqa: S603
                get_token_cmd,
                encoding="utf-8",
                capture_output=True,
                text=True,
                check=True,
            )
            access_token_json = json.loads(called_process.stdout)
            access_token = access_token_json["accessToken"]
        except subprocess.CalledProcessError as get_token_err:
            # This error is thrown from the az account get-access-token command
            # If it errored we can log the output as it doesn't contain the token
            logger.debug(get_token_err, exc_info=True)
            raise CLIError(  # pylint: disable=raise-missing-from
                "Failed to import image: could not get an access token from your"
                " Azure account. Try logging in again with `az login` and then re-run"
                " the command. If it fails again, please raise an issue and try"
                " repeating the command using the --no-subscription-permissions"
                " flag to pull the image to your local machine and then"
                " push it to the Artifact Store using manifest credentials scoped"
                " only to the store. This requires Docker to be installed"
                " locally."
            )

        try:
            source = f"{self._clean_name(source_registry_login_server)}/{source_image}"
            acr_import_image_cmd = [
                str(shutil.which("az")),
                "acr",
                "import",
                "--name",
                target_acr,
                "--source",
                source,
                "--image",
                f"{self.artifact_name}:{self.artifact_version}",
                "--password",
                access_token,
            ]
            self._call_subprocess_raise_output(acr_import_image_cmd)
        except CLIError as error:
            logger.debug(error, exc_info=True)
            if (" 401" in str(error)) or ("Unauthorized" in str(error)):
                # As we shell out the the subprocess, I think checking for these strings
                # is the best check we can do for permission failures.
                raise CLIError(
                    "Failed to import image.\nThe problem may be one or more of:\n"
                    " - the source_registry in your config file does not exist;\n"
                    " - the image doesn't exist;\n"
                    " - you do not have permissions to import images.\n"
                    f"You need to have Reader/AcrPull from {source_registry_login_server}, "
                    "and Contributor role + AcrPush role, or a custom "
                    "role that allows the importImage action and AcrPush over the "
                    "whole subscription in order to be able to import to the new "
                    "Artifact store. More information is available at "
                    "https://aka.ms/acr/authorization\n\n"
                    "If you do not have the latter then you can re-run the command using "
                    "the --no-subscription-permissions flag to pull the image to your "
                    "local machine and then push it to the Artifact Store using manifest "
                    "credentials scoped only to the store. This requires Docker to be "
                    "installed locally."
                ) from error

            # Otherwise, the most likely failure is that the image already exists in the artifact
            # store, so don't fail at this stage, log the error.
            logger.warning(
                (
                    "Failed to import %s to %s. If this failure is because it already exists in "
                    "the target registry we can continue. If the failure was for another reason, "
                    " for example it does not exist in the source registry, this is likely "
                    "fatal. Attempting to continue.\n"
                    "%s"
                ),
                source_image,
                target_acr,
                error,
            )

    def upload(
        self, config: BaseCommonParametersConfig, command_context: CommandContext
    ):
        """Upload the artifact."""

        if command_context.cli_options["no_subscription_permissions"]:
            print(
                f"Using docker pull and push to copy image artifact: {self.artifact_name}"
            )
            self._check_tool_installed("docker")
            image_name = (
                f"{self._clean_name(self.source_registry)}/"
                f"{self.namespace_with_slash}{self.artifact_name}"
                f":{self.artifact_version}"
            )
            self._pull_image_to_local_registry(
                source_registry_login_server=self._clean_name(self.source_registry),
                source_image=image_name,
            )
            self._push_image_from_local_registry(
                local_docker_image=image_name,
                config=config,
                command_context=command_context,
            )
        else:
            print(f"Using az acr import to copy image artifact: {self.artifact_name}")
            self._copy_image(
                source_registry_login_server=self.source_registry,
                config=config,
                command_context=command_context,
                source_image=(
                    f"{self.namespace_with_slash}{self.artifact_name}"
                    f":{self.artifact_version}"
                ),
            )


class BaseStorageAccountArtifact(BaseArtifact):
    """Abstract base class for storage account artifacts."""

    @abstractmethod
    def upload(
        self, config: BaseCommonParametersConfig, command_context: CommandContext
    ):
        """Upload the artifact."""

    def _get_blob_client(
        self, config: BaseCommonParametersConfig, command_context: CommandContext
    ) -> BlobClient:
        container_basename = self.artifact_name.replace("-", "")
        container_name = f"{container_basename}-{self.artifact_version}"
        # For AOSM to work VHD blobs must have the suffix .vhd
        if self.artifact_name.endswith("-vhd"):
            blob_name = f"{self.artifact_name[:-4].replace('-', '')}-{self.artifact_version}.vhd"
        else:
            blob_name = container_name

        logger.debug("container name: %s, blob name: %s", container_name, blob_name)

        manifest_credentials = (
            command_context.aosm_client.artifact_manifests.list_credential(
                resource_group_name=config.publisherResourceGroupName,
                publisher_name=config.publisherName,
                artifact_store_name=config.saArtifactStoreName,
                artifact_manifest_name=config.saManifestName,
            ).as_dict()
        )

        for container_credential in manifest_credentials["container_credentials"]:
            if container_credential["container_name"] == container_name:
                sas_uri = str(container_credential["container_sas_uri"])
                sas_uri_prefix, sas_uri_token = sas_uri.split("?", maxsplit=1)

                blob_url = f"{sas_uri_prefix}/{blob_name}?{sas_uri_token}"
                logger.debug("Blob URL: %s", blob_url)

        return BlobClient.from_blob_url(blob_url)


class LocalFileStorageAccountArtifact(BaseStorageAccountArtifact):
    """Class for storage account artifacts from a local file."""

    def __init__(self, artifact_name, artifact_type, artifact_version, file_path: Path):
        super().__init__(artifact_name, artifact_type, artifact_version)
        self.file_path = str(file_path)

    def upload(
        self, config: BaseCommonParametersConfig, command_context: CommandContext
    ):
        """Upload the artifact."""
        # Liskov substitution dictates we must accept BaseCommonParametersConfig, but we should
        # never be calling upload on this class unless we've got NFDCommonParametersConfig
        assert isinstance(config, NFDCommonParametersConfig)
        logger.debug("LocalFileStorageAccountArtifact config: %s", config)
        blob_client = self._get_blob_client(
            config=config, command_context=command_context
        )
        logger.info("Uploading local file '%s' to blob store", self.file_path)
        with open(self.file_path, "rb") as artifact:
            blob_client.upload_blob(
                data=artifact,
                overwrite=True,
                blob_type=BlobType.PAGEBLOB,
                progress_hook=self._vhd_upload_progress_callback,
            )

        logger.info(
            "Successfully uploaded %s to %s", self.file_path, blob_client.container_name
        )

    def _vhd_upload_progress_callback(
        self, current_bytes: int, total_bytes: Optional[int]
    ) -> None:
        """Callback function for VHD upload progress."""
        current_readable = self._convert_to_readable_size(current_bytes)
        total_readable = self._convert_to_readable_size(total_bytes)
        message = f"Uploaded {current_readable} of {total_readable} bytes"
        logger.info(message)
        print(message)

    @staticmethod
    def _convert_to_readable_size(size_in_bytes: Optional[int]) -> str:
        """Converts a size in bytes to a human readable size."""
        if size_in_bytes is None:
            return "Unknown bytes"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        index = int(math.floor(math.log(size_in_bytes, 1024)))
        power = math.pow(1024, index)
        readable_size = round(size_in_bytes / power, 2)
        return f"{readable_size} {size_name[index]}"


class BlobStorageAccountArtifact(BaseStorageAccountArtifact):
    # TODO (Rename): Rename class, e.g. RemoteBlobStorageAccountArtifact
    """Class for storage account artifacts from a remote blob."""

    def __init__(
        self, artifact_name, artifact_type, artifact_version, blob_sas_uri: str
    ):
        super().__init__(artifact_name, artifact_type, artifact_version)
        self.blob_sas_uri = blob_sas_uri

    def upload(
        self, config: BaseCommonParametersConfig, command_context: CommandContext
    ):
        """Upload the artifact."""
        # Liskov substitution dictates we must accept BaseCommonParametersConfig, but we should
        # never be calling upload on this class unless we've got NFDCommonParametersConfig
        assert isinstance(config, NFDCommonParametersConfig)
        logger.info("Copy from SAS URL to blob store")
        source_blob = BlobClient.from_blob_url(self.blob_sas_uri)

        if source_blob.exists():
            target_blob = self._get_blob_client(
                config=config, command_context=command_context
            )
            logger.debug(source_blob.url)
            target_blob.start_copy_from_url(source_blob.url)
            logger.info(
                "Successfully copied %s from %s to %s",
                source_blob.blob_name,
                source_blob.account_name,
                target_blob.account_name,
            )
        else:
            raise RuntimeError(
                f"{source_blob.blob_name} does not exist in"
                f" {source_blob.account_name}."
            )


# Mapping of artifact type names to their classes.
ARTIFACT_TYPE_TO_CLASS = {
    "ACRFromLocalFile": LocalFileACRArtifact,
    "ACRFromRemote": RemoteACRArtifact,
    "StorageAccountFromLocalFile": LocalFileStorageAccountArtifact,
    "StorageAccountFromBlob": BlobStorageAccountArtifact,
}

# Generated mapping of artifact classes to type names.
ARTIFACT_CLASS_TO_TYPE = {v: k for k, v in ARTIFACT_TYPE_TO_CLASS.items()}
