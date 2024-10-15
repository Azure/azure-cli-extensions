# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import re
import shutil
import subprocess
from typing import List, Tuple, Dict, Union
from abc import abstractmethod
from knack.log import get_logger
from knack.util import CLIError
from azure.cli.core.azclierror import BadRequestError, ClientRequestError

from azext_aosm.common.utils import (
    call_subprocess_raise_output,
    clean_registry_name,
)

logger = get_logger(__name__)
ACR_REGISTRY_NAME_PATTERN = r"^([a-zA-Z0-9]+\.azurecr\.io)"


# pylint: disable=too-few-public-methods
class ContainerRegistry:
    """
    A class to represent a registry and handle all Registry operations.
    """

    def __init__(self, registry_name: str):
        """
        Initialise the Registry object.

        :param registry_name: The name of the registry
        """
        self.registry_name = registry_name
        self.registry_namespaces: List[str] = []

    def to_dict(self) -> Dict:
        """Convert an instance to a dict."""
        output_dict = {
            "type": REGISTRY_CLASS_TO_TYPE[type(self)],
            "registry_name": self.registry_name,
        }
        return output_dict

    @classmethod
    def from_dict(cls, registry_dict: Dict) -> "ContainerRegistry":
        """Create an instance from a dict."""
        try:
            registry_name = registry_dict["registry_name"]
            registry_class = REGISTRY_TYPE_TO_CLASS[registry_dict["type"]]
            return registry_class(registry_name)
        except KeyError as error:
            raise ValueError(
                f"Registry is missing required field {error}.\n"
                f"Registry is: {registry_dict}.\n"
                "This is unexpected and most likely comes from manual editing "
                "of the definition folder."
            ) from error

    @abstractmethod
    def find_image(
        self, image: str, version: str
    ) -> Union[Tuple["ContainerRegistry", str], Tuple[None, None]]:
        """
        Find whether the given image exists in this registry.

        :param image: The image to find in the registry
            (the image should be stripped of all namespace)
        :param version: The version of the image (also known as image tag)
        :return: The registry and namespace for the image
        """
        raise NotImplementedError

    def add_namespace(self, namespace: str) -> None:
        """
        Add a namespace to the registry.

        :param namespace: The namespace to add
        """
        if namespace not in self.registry_namespaces:
            self.registry_namespaces.append(namespace)

    def pull_image_to_local_registry(self, source_image: str) -> None:
        """
        Pull image to local registry using docker pull. Requires docker.

        :param: source_image: source docker image name e.g.
            uploadacr.azurecr.io/samples/nginx:stable
        """
        try:
            logger.info("Pulling source image %s", source_image)
            pull_source_image_cmd = [
                str(shutil.which("docker")),
                "pull",
                source_image,
            ]
            call_subprocess_raise_output(pull_source_image_cmd)
        except CLIError as error:
            logger.debug(error, exc_info=True)
            raise BadRequestError(
                f"Failed to pull {source_image}. Check if this image exists in the"
                f" source registry {self.registry_name} and that you have run docker"
                "login on this registry."
            ) from error


class UniversalRegistry(ContainerRegistry):
    """
    A class to represent all Container Registries other than Azure Container Registry
    and handle all Registry operations (primarily using docker CLI).
    """

    def find_image(
        self, image: str, version: str
    ) -> Union[Tuple[ContainerRegistry, str], Tuple[None, None]]:
        """
        Find whether the given image exists in this registry.

        :param image: The image to find in the registry
            (the image should be stripped of all namespace)
        :param version: The version of the image (also known as image tag)
        :return: The registry and namespace for the image
        """

        for namespace in self.registry_namespaces:
            image_path = f"{self.registry_name}/{namespace}{image}:{version}"

            logger.debug("Checking if %s exists.", image_path)

            try:
                manifest_inspect_cmd = [
                    str(shutil.which("docker")),
                    "manifest",
                    "inspect",
                    image_path,
                ]

                output = call_subprocess_raise_output(manifest_inspect_cmd)

                if output is not None:
                    return self, namespace

            except CLIError as error:
                if "manifest unknown" in str(error):
                    continue
                logger.warning(
                    (
                        "Failed to contact source registry %s. "
                        "Make sure you run docker login on this registry "
                        "before running the aosm command."
                    ),
                    self.registry_name,
                )
                logger.debug(error, exc_info=True)
                return None, None
        return None, None


class AzureContainerRegistry(ContainerRegistry):
    """
    A class to represent an Azure Container Registry and handle all ACR operations.
    """

    def _login(self) -> None:
        """
        Log in to the source registry using the Azure CLI.
        Uses the CLI user's context to log in to the source registry.
        """

        message = f"Logging into source registry {self.registry_name}"
        logger.info(message)

        try:
            acr_source_login_cmd = [
                str(shutil.which("az")),
                "acr",
                "login",
                "--name",
                self.registry_name,
            ]
            call_subprocess_raise_output(acr_source_login_cmd)
        except CLIError as error:
            logger.debug(error, exc_info=True)
            raise ClientRequestError(
                f"Failed to log into registry {self.registry_name}"
            ) from error

    def pull_image_to_local_registry(self, source_image: str) -> None:
        """
        Pull image to local registry using docker pull. Requires docker.

        :param: source_image: source docker image name e.g.
            uploadacr.azurecr.io/samples/nginx:stable
        """

        self._login()
        try:
            super().pull_image_to_local_registry(source_image)
        except BadRequestError as error:
            raise error
        finally:
            logger.info("Logging out of source registry %s", self.registry_name)

            # There is no az 'acr logout' command, so we use docker logout
            docker_logout_cmd = [
                str(shutil.which("docker")),
                "logout",
                self.registry_name,
            ]
            call_subprocess_raise_output(docker_logout_cmd)

    def copy_image_to_target_acr(
        self,
        source_image: str,
        image_name: str,
        image_version: str,
        target_acr: str,
    ) -> None:
        """
        Copy an image from this registry to a target ACR.

        :param source_image: The image to copy
            e.g. uploadacr.azurecr.io/samples/nginx:1.0.0
        :param image_name: The name of the image
            e.g. nginx
        :param image_version: The version of the artifact
            e.g. 1.0.0
        :param target_acr: The target ACR
        """

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
            # Dont use call_subprocess_raise_output here as we don't want to log the
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
            # TODO: we shouldn't be using "raise an issue" type language with users.
            # We should find out what we should use and change this
            logger.debug(get_token_err, exc_info=True)
            raise ClientRequestError(  # pylint: disable=raise-missing-from
                "Failed to import image: could not get an access token from your"
                " Azure account. Try logging in again with `az login` and then re-run"
                " the command. If it fails again, please raise an issue."
                " You can also try repeating the command using the --no-subscription-permissions"
                " flag to pull the image to your local machine and then"
                " push it to the Artifact Store using manifest credentials scoped"
                " only to the store. This requires Docker to be installed"
                " locally."
            )

        try:
            acr_import_image_cmd = [
                str(shutil.which("az")),
                "acr",
                "import",
                "--name",
                target_acr,
                "--source",
                source_image,
                "--image",
                f"{image_name}:{image_version}",
                "--password",
                access_token,
            ]
            call_subprocess_raise_output(acr_import_image_cmd)
        except CLIError as error:
            logger.debug(error, exc_info=True)
            if (" 401" in str(error)) or ("Unauthorized" in str(error)):
                # As we shell out the the subprocess, I think checking for these strings
                # is the best check we can do for permission failures.
                raise BadRequestError(
                    "Failed to import image.\nThe problem may be one or more of:\n"
                    " - the image_source in your config file does not exist;\n"
                    " - the image doesn't exist;\n"
                    " - you do not have permissions to import images.\n"
                    f"You need to have Reader/AcrPull from {self.registry_name}, "
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
                    "Failed to copy %s from %s to %s. If this failure is because it already "
                    "exists in the target registry we can continue. If the failure was for "
                    "another reason, for example it does not exist in the source registry, "
                    "this is likely fatal. Attempting to continue.\n"
                    "%s"
                ),
                source_image,
                self.registry_name,
                target_acr,
                error,
            )

    def find_image(
        self, image: str, version: str
    ) -> Union[Tuple["AzureContainerRegistry", str], Tuple[None, None]]:
        """
        Find whether the given image exists in this registry.

        :param image: The image to find in the registry
            (the image should be stripped of all namespace)
        :param version: The version of the image (also known as image tag)
        :return: The registry and namespace for the image
        """
        for namespace in self.registry_namespaces:
            image_with_namespace = f"{namespace}{image}:{version}"
            logger.debug("Checking if %s exists.", image_with_namespace)
            try:
                acr_source_get_images_cmd = [
                    str(shutil.which("az")),
                    "acr",
                    "repository",
                    "show",
                    "--name",
                    self.registry_name,
                    "--image",
                    image_with_namespace,
                ]

                call_subprocess_raise_output(acr_source_get_images_cmd)

                return (self, namespace)

            except CLIError as error:
                logger.debug(
                    ("Image %s, version %s not found in %s registry."),
                    image_with_namespace,
                    version,
                    self.registry_name,
                )
                logger.debug(error, exc_info=True)

        return None, None


class ContainerRegistryHandler:
    """
    A class to handle all the registries and their images.
    """

    def __init__(self, image_sources):
        self.image_sources = image_sources
        self.registry_list = self._create_registry_list()

    def _create_registry_list(self) -> List[ContainerRegistry]:
        """
        Create a list of registry objects from the registries provided by the user.

        :return: A list of registry objects
        """

        registry_object_list: List[ContainerRegistry] = []

        logger.debug("Creating registry list from the provided registries")

        for image_source in self.image_sources:
            image_source = clean_registry_name(image_source)

            parts = image_source.split("/", 1)
            registry_name = parts[0]
            registry_namespace = parts[1] if len(parts) > 1 else None

            if registry_namespace:
                # Make sure that the namespace ends with a slash
                if not registry_namespace.endswith("/"):
                    registry_namespace += "/"
            else:
                registry_namespace = ""

            # Get the registry_object with matching registry_name from the list,
            # or None if not found
            registry_object = None
            for registry in registry_object_list:
                if registry.registry_name == registry_name:
                    registry_object = registry
                    break

            if registry_object:
                # Object already exists, add namespace to it
                registry_object.add_namespace(registry_namespace)
            else:
                # Object does not exist, create a new one
                acr_match = re.match(ACR_REGISTRY_NAME_PATTERN, registry_name)

                if acr_match:
                    registry_object_list.append(AzureContainerRegistry(registry_name))
                else:
                    registry_object_list.append(UniversalRegistry(registry_name))

                registry_object_list[-1].add_namespace(registry_namespace)

        return registry_object_list

    def find_registry_for_image(
        self, image, version
    ) -> Union[Tuple["ContainerRegistry", str], Tuple[None, None]]:
        """
        Find the registry and namespace for a given image and version.

        :param image: The image to find the registry for
            This should be stripped of all namespace (e.g nginx, not samples/nginx)
        :param version: The version of the image
        :return: The registry and namespace for the image
        """
        # In the interest of speed, if we have just one registry and namespace, return it
        if (
            len(self.registry_list) == 1
            and len(self.registry_list[0].registry_namespaces) == 1
        ):
            return self.registry_list[0], self.registry_list[0].registry_namespaces[0]

        for registry in self.registry_list:

            image_registry, namespace = registry.find_image(image, version)
            if (image_registry is not None) and (namespace is not None):
                return image_registry, namespace
            continue

        logger.warning(
            (
                "Image: %s, version: %s was not found in any of the provided registries. "
                "This image will not be part of your Network Function. "
                "If you would like to include it, provide the registry containing this image "
                "in the 'image_sources' list in the input file and run the build command again."
            ),
            image,
            version,
        )
        return None, None


# Mapping of registry type names to their classes.
REGISTRY_CLASS_TO_TYPE = {
    UniversalRegistry: "UniversalRegistry",
    AzureContainerRegistry: "AzureContainerRegistry",
}

REGISTRY_TYPE_TO_CLASS = {value: key for key, value in REGISTRY_CLASS_TO_TYPE.items()}
