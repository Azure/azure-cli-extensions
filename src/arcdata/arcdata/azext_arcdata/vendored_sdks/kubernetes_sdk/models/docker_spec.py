# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from azext_arcdata.vendored_sdks.kubernetes_sdk.models.dict_utils import SerializationUtils


class DockerSpec(SerializationUtils):
    """
    A Docker spec that models the controller docker spec for custom resources
    """

    def __init__(
        self,
        registry: str = None,
        repository: str = None,
        imageTag: str = None,
        imagePullPolicy: str = None,
    ):
        self._registry = registry
        self._repository = repository
        self._imageTag = imageTag
        self._imagePullPolicy = imagePullPolicy

    @property
    def registry(self) -> str:
        """
        The registry that holds the repository for the image
        """
        return self._registry

    @registry.setter
    def registry(self, r: str):
        self._registry = r

    @property
    def repository(self) -> str:
        """
        The repository that holds the docker image
        """
        return self._repository

    @repository.setter
    def repository(self, r: str):
        self._repository = r

    @property
    def imageTag(self) -> str:
        """
        The tag for the docker image
        """
        return self._imageTag

    @imageTag.setter
    def imageTag(self, it: str):
        self._imageTag = it

    @property
    def imagePullPolicy(self) -> str:
        """
        A k8s property that determines image pulling behavior
        """
        return self._imagePullPolicy

    @imagePullPolicy.setter
    def imagePullPolicy(self, ipp: str):
        self._imagePullPolicy = ipp

    def _to_dict(self) -> dict:
        return {
            "registry": getattr(self, "registry", None),
            "repository": getattr(self, "repository", None),
            "imageTag": getattr(self, "imageTag", None),
            "imagePullPolicy": getattr(self, "imagePullPolicy", None),
        }

    def _hydrate(self, d: dict):
        if "registry" in d:
            self.registry = d["registry"]

        if "repository" in d:
            self.repository = d["repository"]

        if "imageTag" in d:
            self.imageTag = d["imageTag"]

        if "imagePullPolicy" in d:
            self.imagePullPolicy = d["imagePullPolicy"]
