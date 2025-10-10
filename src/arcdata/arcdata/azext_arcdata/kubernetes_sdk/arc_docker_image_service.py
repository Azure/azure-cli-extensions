import base64
import json
import os
import re
import sys
from typing import Tuple
from azext_arcdata.core.constants import (
    DEFAULT_IMAGE_TAG,
    PUBLIC_DOCKER_REGISTRY,
)
from azext_arcdata.kubernetes_sdk.dc.constants import CONFIG_DIR

import pydash as _
import requests
from azext_arcdata.kubernetes_sdk.client import KubernetesClient
from knack.log import get_logger
from requests.structures import CaseInsensitiveDict

VERSION_REGEX = (
    "^v?(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)(\.("
    "?P<patch>0|[1-9]\d*))?(_(?P<label>.(.*)))?$"
)
"""
Regex defining the format of the version tag
"""

logger = get_logger(__name__)


class ArcDataImageService:
    @staticmethod
    def parse_image_uri(image_uri: str) -> Tuple[str, str, str, str]:
        """
        parses a k8s image uri returning a tuple: registry, repository,
        image_name, image_tag
        """
        return re.split("[/:]+", image_uri)

    @staticmethod
    def format_image_uri(
        registry: str, repository: str, image_name: str, image_tag: str
    ):
        """
        returns the image uri for the given parameters
        """
        return "{0}/{1}/{2}:{3}".format(
            registry, repository, image_name, image_tag
        )

    @staticmethod
    def get_latest_image_version(namespace, use_k8s=None):

        versions = ArcDataImageService.get_available_image_versions(
            namespace, use_k8s
        )
        return versions[0]

    @staticmethod
    def get_available_image_versions(namespace, use_k8s=None):

        header = []

        #  if use_k8s is true, attempt to connect to the local registry to
        # resolve available versions.  Otherwise, connect to mcr.microsoft.com
        (datacontroller, cr) = KubernetesClient.get_arc_datacontroller(
            namespace, use_k8s
        )
        docker_secret = ArcDataImageService.get_docker_secret(
            namespace, use_k8s
        )

        registry = datacontroller.spec.docker.registry
        repository = datacontroller.spec.docker.repository

        if (
            docker_secret is not None
            and registry.lower().strip() != PUBLIC_DOCKER_REGISTRY
        ):
            """
            resolve secret from the k8s store
            """
            username = _.get(docker_secret, ["auths", registry, "username"])
            password = _.get(docker_secret, ["auths", registry, "password"])
            header = ArcDataImageService.get_docker_registry_oauth_header(
                registry, repository, username, password
            )

        try:
            return (
                ArcDataImageService.get_available_image_versions_from_registry(
                    registry, repository, header
                )
            )
        except:
            return (
                ArcDataImageService.get_available_image_versions_from_registry(
                    PUBLIC_DOCKER_REGISTRY, "arcdata"
                )
            )

    @staticmethod
    def get_available_image_versions_from_registry(
        registry, repository, auth_header=[]
    ):
        response = requests.get(
            "https://{0}/v2/{1}/arc-controller/tags/list?n=10000".format(
                registry, repository
            ),
            headers=auth_header,
        )

        if response.status_code != 200:
            raise Exception(response.raw)

        tags = _.chain(json.loads(response.text)["tags"]).value()

        if len(tags) == 0:
            raise Exception(
                "Could not find any valid versions in {0}/{1}".format(
                    registry, repository
                )
            )
        return ArcDataImageService.resolve_valid_image_versions(tags)

    @staticmethod
    def resolve_valid_image_versions(tags: list) -> list:
        """
        Removes image tags that do not represent versions, sorts by latest
        version first
        """
        versions = (
            _.chain(tags).filter(ArcDataImageService.validate_image_tag).value()
        )
        return _.sort(
            versions,
            comparator=ArcDataImageService.compare_version_tag,
            reverse=True,
        )

    @staticmethod
    def compare_version_tag(left: str, right: str, ignore_label: bool = False):
        """
        returns a -1, 0, or 1 if the left tag is less than, equal to, or greater than the right tag
        """
        leftv = ArcDataImageService.parse_image_tag(left)
        rightv = ArcDataImageService.parse_image_tag(right)

        if ignore_label:
            leftv = leftv[:3]
            rightv = rightv[:3]

        if leftv < rightv:
            return -1
        if leftv > rightv:
            return 1
        if leftv == rightv:
            return 0

    @staticmethod
    def validate_image_tag(tag) -> bool:
        return re.match(VERSION_REGEX, tag) is not None

    @staticmethod
    def parse_image_tag(tag) -> Tuple[int, int, int, str]:
        """
        parses the image tag returning a tuple with the following layout:
        major, minor, patch, label
        image tag should be formatted using the following arcdata semantic
        format:
        v{major}.{minor}.{patch}_{label}
        """

        def int_or_empty(value):
            try:
                return int(value)
            except:
                return None

        try:
            version_groups = re.search(VERSION_REGEX, tag)
            return (
                int_or_empty(version_groups.group("major")),
                int_or_empty(version_groups.group("minor")),
                int_or_empty(version_groups.group("patch")),
                version_groups.group("label"),
            )
        except:
            raise ValueError(
                "Invalid version tag detected: {0} \n"
                "Version tags should have the format v<major>.<minor>.<patch>_label".format(
                    tag
                )
            )

    @staticmethod
    def format_image_tag(
        major: int, minor: int = None, patch: int = None, label: str = None
    ) -> str:
        def append_segment(segment, delimeter) -> str:
            if segment is not None:
                return "{0}{1}".format(delimeter, segment)

        v = "{0}".format(major)
        v = append_segment(minor, ".")
        v = append_segment(patch, ".")
        v = append_segment(label, "_")
        return v

    @staticmethod
    def get_docker_secret(namespace, use_k8s=True):
        try:
            client = KubernetesClient.resolve_k8s_client().CoreV1Api()
            secret = client.read_namespaced_secret(
                "arc-private-registry", namespace
            )
            docker_secret = json.loads(
                base64.b64decode(secret.data[".dockerconfigjson"])
            )
            return docker_secret
        except Exception:
            # secret not found
            pass

    @staticmethod
    def get_docker_registry_oauth_header(
        registry, repository, username, password
    ):
        token = ArcDataImageService.get_docker_registry_access_token(
            registry, repository, username, password
        )
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["Authorization"] = "Bearer {0}".format(token)
        return headers

    @staticmethod
    def get_docker_registry_access_token(
        registry, repository, username, password
    ):
        cred = str(
            base64.b64encode(
                "{0}:{1}".format(username, password).encode("utf-8")
            ),
            "utf-8",
        )
        header = {"Authorization": "Basic {0}".format(cred)}
        scope = "repository:{0}/arc-controller:metadata_read".format(repository)
        response = requests.get(
            "https://{0}/oauth2/token?service={0}&scope={1}".format(
                registry, scope
            ),
            headers=header,
        )
        if response.status_code != 200:
            logger.error(
                "Unable to retrieve oauth token for docker registry {0} for "
                "repository {1} scope.".format(registry, repository)
            )
            return ""

        token = ""

        try:
            token = json.loads(bytes.decode(response.content))["access_token"]
        except Exception:
            pass  # retrieved a 200 response from the registry, but it did not contain a valid token.  This may mean the registry does not require authentication.

        return token

    @staticmethod
    def get_config_image_tag():
        """
        Returns a tuple containing the major, minor, revision fields of
        the latest image tag supported by this version of the CLI.
        Since this will rev on each CLI release, it should be a safe indicator
        of the CLI version with parity to the image versions
        """
        tag = DEFAULT_IMAGE_TAG
        version = ArcDataImageService.parse_image_tag(tag)
        return version

    @staticmethod
    def is_image_version_supported_by_cli(image_tag):
        """
        Returns True if the provided image_tag is supported by this version of the CLI,
        otherwise returns False.  The CLI supports image tags up to the current
        major.minor version.
        """

        (
            d_major,
            d_minor,
            d_revision,
            d_tag,
        ) = ArcDataImageService.parse_image_tag(image_tag)
        # get image tag from config file
        (
            c_major,
            c_minor,
            c_revision,
            c_tag,
        ) = ArcDataImageService.get_config_image_tag()

        return d_major < c_major or (d_major == c_major and d_minor <= c_minor)
