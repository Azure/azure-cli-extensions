# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=unidiomatic-typecheck
"""A module to handle interacting with artifacts."""
import json
import math
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any, Optional, Union

from knack.log import get_logger
from knack.util import CLIError
from oras.client import OrasClient

from azext_aosm._configuration import (
    ArtifactConfig,
    CNFImageConfig,
    HelmPackageConfig,
    VhdArtifactConfig,
)
from azext_aosm.vendored_sdks.azure_storagev2.blob.v2022_11_02 import (
    BlobClient, BlobType)

logger = get_logger(__name__)


@dataclass
class Artifact:
    """Artifact class."""

    artifact_name: str
    artifact_type: str
    artifact_version: str
    artifact_client: Union[BlobClient, OrasClient]
    manifest_credentials: Any

    def upload(
        self,
        artifact_config: Union[ArtifactConfig, HelmPackageConfig],
        use_manifest_permissions: bool = False,
    ) -> None:
        """
        Upload artifact.

        :param artifact_config: configuration for the artifact being uploaded
        """
        if isinstance(self.artifact_client, OrasClient):
            if isinstance(artifact_config, HelmPackageConfig):
                self._upload_helm_to_acr(artifact_config, use_manifest_permissions)
            elif isinstance(artifact_config, ArtifactConfig):
                self._upload_arm_to_acr(artifact_config)
            elif isinstance(artifact_config, CNFImageConfig):
                self._upload_or_copy_image_to_acr(
                    artifact_config, use_manifest_permissions
                )
            else:
                raise ValueError(f"Unsupported artifact type: {type(artifact_config)}.")
        else:
            assert isinstance(artifact_config, ArtifactConfig)
            self._upload_to_storage_account(artifact_config)

    def _upload_arm_to_acr(self, artifact_config: ArtifactConfig) -> None:
        """
        Upload ARM artifact to ACR.

        :param artifact_config: configuration for the artifact being uploaded
        """
        assert isinstance(self.artifact_client, OrasClient)

        if artifact_config.file_path:
            if not self.artifact_client.remote.hostname:
                raise ValueError(
                    "Cannot upload ARM template as OrasClient has no remote hostname."
                    " Please check your ACR config."
                )
            target = (
                f"{self.artifact_client.remote.hostname.replace('https://', '')}"
                f"/{self.artifact_name}:{self.artifact_version}"
            )
            logger.debug("Uploading %s to %s", artifact_config.file_path, target)
            self.artifact_client.push(files=[artifact_config.file_path], target=target)
        else:
            raise NotImplementedError(
                "Copying artifacts is not implemented for ACR artifacts stores."
            )

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
            logger.debug("Failed to run %s with %s", log_cmd, error)

            all_output: str = (
                f"Command: {'' ''.join(log_cmd)}\n"
                f"Output: {error.stdout}\n"
                f"Error output: {error.stderr}\n"
                f"Return code: {error.returncode}"
            )
            logger.debug("All the output %s", all_output)

            # Raise the error without the original exception, which may contain secrets.
            raise CLIError(all_output) from None

    def _upload_helm_to_acr(
        self, artifact_config: HelmPackageConfig, use_manifest_permissions: bool
    ) -> None:
        """
        Upload artifact to ACR. This does and az acr login and then a helm push.

        Requires helm to be installed.

        :param artifact_config: configuration for the artifact being uploaded
        :param use_manifest_permissions: whether to use the manifest credentials for the
            upload. If False, the CLI user credentials will be used, which does not
            require Docker to be installed. If True, the manifest creds will be used,
            which requires Docker.
        """
        self._check_tool_installed("helm")
        assert isinstance(self.artifact_client, OrasClient)
        chart_path = artifact_config.path_to_chart
        if not self.artifact_client.remote.hostname:
            raise ValueError(
                "Cannot upload artifact. Oras client has no remote hostname."
            )
        registry = self._get_acr()
        target_registry = f"oci://{registry}"
        registry_name = registry.replace(".azurecr.io", "")

        username = self.manifest_credentials["username"]
        password = self.manifest_credentials["acr_token"]

        if not use_manifest_permissions:
            # Note that this uses the user running the CLI's AZ login credentials, not
            # the manifest credentials retrieved from the ACR. This allows users with
            # enough permissions to avoid having to install docker. It logs in to the
            # registry by retrieving an access token, which allows use of this command
            # in environments without docker.
            # It is governed by the no-subscription-permissions CLI argument which
            # default to False.
            logger.debug("Using CLI user credentials to log into %s", registry_name)
            acr_login_with_token_cmd = [
                str(shutil.which("az")),
                "acr",
                "login",
                "--name",
                registry_name,
                "--expose-token",
                "--output",
                "tsv",
                "--query",
                "accessToken",
            ]
            username = "00000000-0000-0000-0000-000000000000"
            try:
                password = subprocess.check_output(
                    acr_login_with_token_cmd, encoding="utf-8", text=True
                ).strip()
            except subprocess.CalledProcessError as error:
                unauthorized = (
                    error.stderr
                    and (" 401" in error.stderr or "unauthorized" in error.stderr)
                ) or (
                    error.stdout
                    and (" 401" in error.stdout or "unauthorized" in error.stdout)
                )

                if unauthorized:
                    # As we shell out the the subprocess, I think checking for these
                    # strings is the best check we can do for permission failures.
                    raise CLIError(
                        " Failed to login to Artifact Store ACR.\n"
                        " It looks like you do not have permissions. You need to have"
                        " the AcrPush role over the"
                        " whole subscription in order to be able to upload to the new"
                        " Artifact store.\n\nIf you do not have them then you can"
                        " re-run the command using the --no-subscription-permissions"
                        " flag to use manifest credentials scoped"
                        " only to the store. This requires Docker to be installed"
                        " locally."
                    ) from error
        else:
            # This seems to prevent occasional helm login failures
            self._check_tool_installed("docker")
            acr_login_cmd = [
                str(shutil.which("az")),
                "acr",
                "login",
                "--name",
                registry_name,
                "--username",
                username,
                "--password",
                password,
            ]
            self._call_subprocess_raise_output(acr_login_cmd)
        try:
            logger.debug("Uploading %s to %s", chart_path, target_registry)
            helm_login_cmd = [
                str(shutil.which("helm")),
                "registry",
                "login",
                registry,
                "--username",
                username,
                "--password",
                password,
            ]
            self._call_subprocess_raise_output(helm_login_cmd)

            # helm push "$chart_path" "$target_registry"
            push_command = [
                str(shutil.which("helm")),
                "push",
                chart_path,
                target_registry,
            ]
            self._call_subprocess_raise_output(push_command)
        finally:
            helm_logout_cmd = [
                str(shutil.which("helm")),
                "registry",
                "logout",
                registry,
            ]
            self._call_subprocess_raise_output(helm_logout_cmd)

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

    def _vhd_upload_progress_callback(
        self, current_bytes: int, total_bytes: Optional[int]
    ) -> None:
        """Callback function for VHD upload progress."""
        current_readable = self._convert_to_readable_size(current_bytes)
        total_readable = self._convert_to_readable_size(total_bytes)
        message = f"Uploaded {current_readable} of {total_readable} bytes"
        logger.info(message)
        print(message)

    def _upload_to_storage_account(self, artifact_config: ArtifactConfig) -> None:
        """
        Upload artifact to storage account.

        :param artifact_config: configuration for the artifact being uploaded
        """
        assert isinstance(self.artifact_client, BlobClient)
        assert isinstance(artifact_config, ArtifactConfig)

        # If the file path is given, upload the artifact, else, copy it from an existing blob.
        if artifact_config.file_path:
            logger.info("Upload to blob store")
            with open(artifact_config.file_path, "rb") as artifact:
                self.artifact_client.upload_blob(
                    data=artifact,
                    overwrite=True,
                    blob_type=BlobType.PAGEBLOB,
                    progress_hook=self._vhd_upload_progress_callback,
                )
            logger.info(
                "Successfully uploaded %s to %s",
                artifact_config.file_path,
                self.artifact_client.account_name,
            )
        else:
            # Config Validation will raise error if not true
            assert isinstance(artifact_config, VhdArtifactConfig)
            assert artifact_config.blob_sas_url
            logger.info("Copy from SAS URL to blob store")
            source_blob = BlobClient.from_blob_url(artifact_config.blob_sas_url)

            if source_blob.exists():
                logger.debug(source_blob.url)
                self.artifact_client.start_copy_from_url(source_blob.url)
                logger.info(
                    "Successfully copied %s from %s to %s",
                    source_blob.blob_name,
                    source_blob.account_name,
                    self.artifact_client.account_name,
                )
            else:
                raise RuntimeError(
                    f"{source_blob.blob_name} does not exist in"
                    f" {source_blob.account_name}."
                )

    def _get_acr(self) -> str:
        """
        Get the name of the ACR.

        :return: The name of the ACR
        """
        assert hasattr(self.artifact_client, "remote")
        if not self.artifact_client.remote.hostname:
            raise ValueError(
                "Cannot upload artifact. Oras client has no remote hostname."
            )
        return self._clean_name(self.artifact_client.remote.hostname)

    def _get_acr_target_image(
        self,
        include_hostname: bool = True,
    ) -> str:
        """Format the acr url, artifact name and version into a target image string."""
        if include_hostname:
            return f"{self._get_acr()}/{self.artifact_name}:{self.artifact_version}"

        return f"{self.artifact_name}:{self.artifact_version}"

    @staticmethod
    def _check_tool_installed(tool_name: str) -> None:
        """
        Check whether a tool such as docker or helm is installed.

        :param tool_name: name of the tool to check, e.g. docker
        """
        if shutil.which(tool_name) is None:
            raise CLIError(f"You must install {tool_name} to use this command.")

    def _upload_or_copy_image_to_acr(
        self, artifact_config: CNFImageConfig, use_manifest_permissions: bool
    ) -> None:
        # Check whether the source registry has a namespace in the repository path
        source_registry_namespace: str = ""
        if artifact_config.source_registry_namespace:
            source_registry_namespace = f"{artifact_config.source_registry_namespace}/"

        if artifact_config.source_local_docker_image:
            # The user has provided a local docker image to use as the source
            # for the images in the artifact manifest
            self._check_tool_installed("docker")
            print(
                f"Using local docker image as source for image artifact upload for image artifact: {self.artifact_name}"
            )
            self._push_image_from_local_registry(
                local_docker_image=artifact_config.source_local_docker_image,
                target_username=self.manifest_credentials["username"],
                target_password=self.manifest_credentials["acr_token"],
            )
        elif use_manifest_permissions:
            self._check_tool_installed("docker")
            print(
                f"Using docker pull and push to copy image artifact: {self.artifact_name}"
            )
            image_name = (
                f"{self._clean_name(artifact_config.source_registry)}/"
                f"{source_registry_namespace}{self.artifact_name}"
                f":{self.artifact_version}"
            )
            self._pull_image_to_local_registry(
                source_registry_login_server=self._clean_name(
                    artifact_config.source_registry
                ),
                source_image=image_name,
            )
            self._push_image_from_local_registry(
                local_docker_image=image_name,
                target_username=self.manifest_credentials["username"],
                target_password=self.manifest_credentials["acr_token"],
            )
        else:
            print(f"Using az acr import to copy image artifact: {self.artifact_name}")
            self._copy_image(
                source_registry_login_server=artifact_config.source_registry,
                source_image=(
                    f"{source_registry_namespace}{self.artifact_name}"
                    f":{self.artifact_version}"
                ),
            )

    def _push_image_from_local_registry(
        self,
        local_docker_image: str,
        target_username: str,
        target_password: str,
    ):
        """
        Push image to target registry using docker push. Requires docker.

        :param local_docker_image: name and tag of the source image on local registry
            e.g. uploadacr.azurecr.io/samples/nginx:stable
        :type local_docker_image: str
        :param target_username: The username to use for the az acr login attempt
        :type target_username: str
        :param target_password: The password to use for the az acr login attempt
        :type target_password: str
        """
        assert hasattr(self.artifact_client, "remote")
        target_acr = self._get_acr()
        try:
            target = self._get_acr_target_image()
            print("Tagging source image")

            tag_image_cmd = [
                str(shutil.which("docker")),
                "tag",
                local_docker_image,
                target,
            ]
            self._call_subprocess_raise_output(tag_image_cmd)
            message = (
                "Logging into artifact store registry "
                f"{self.artifact_client.remote.hostname}"
            )

            print(message)
            logger.info(message)
            acr_target_login_cmd = [
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
            self._call_subprocess_raise_output(acr_target_login_cmd)

            print("Pushing target image using docker push")
            push_target_image_cmd = [
                str(shutil.which("docker")),
                "push",
                target,
            ]
            self._call_subprocess_raise_output(push_target_image_cmd)
        except CLIError as error:
            logger.error(
                ("Failed to tag and push %s to %s."),
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

    @staticmethod
    def _clean_name(registry_name: str) -> str:
        """Remove https:// from the registry name."""
        return registry_name.replace("https://", "")

    def _copy_image(
        self,
        source_registry_login_server: str,
        source_image: str,
    ):
        """
        Copy image from one ACR to another.

        Use az acr import to do the import image. Previously we used the python
        sdk ContainerRegistryManagementClient.registries.begin_import_image
        but this requires the source resource group name, which is more faff
        at configuration time.

        Neither az acr import or begin_import_image support using the username
        and acr_token retrieved from the manifest credentials, so this uses the
        CLI users context to access both the source registry and the target
        Artifact Store registry, which requires either Contributor role or a
        custom role that allows the importImage action over the whole subscription.

        :param source_registry: source registry login server e.g. https://uploadacr.azurecr.io
        :param source_image: source image including namespace and tags e.g.
                             samples/nginx:stable
        """
        target_acr = self._get_acr()
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
                self._get_acr_target_image(include_hostname=False),
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
                    " Failed to import image.\nIt looks like either the source_registry"
                    " in your config file does not exist or the image doesn't exist or"
                    " you do not have"
                    " permissions to import images. You need to have Reader/AcrPull"
                    f" from {source_registry_login_server}, and Contributor role +"
                    " AcrPush role, or a custom"
                    " role that allows the importImage action and AcrPush over the"
                    " whole subscription in order to be able to import to the new"
                    " Artifact store.\n\nIf you do not have the latter then you"
                    " can re-run the command using the --no-subscription-permissions"
                    " flag to pull the image to your local machine and then"
                    " push it to the Artifact Store using manifest credentials scoped"
                    " only to the store. This requires Docker to be installed"
                    " locally."
                ) from error

            # The most likely failure is that the image already exists in the artifact
            # store, so don't fail at this stage, log the error.
            logger.error(
                (
                    "Failed to import %s to %s. Check if this image exists in the"
                    " source registry or is already present in the target registry.\n"
                    "%s"
                ),
                source_image,
                target_acr,
                error,
            )
