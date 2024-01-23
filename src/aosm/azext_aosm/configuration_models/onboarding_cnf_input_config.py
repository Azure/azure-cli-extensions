# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from azure.cli.core.azclierror import ValidationError

from azext_aosm.configuration_models.onboarding_nfd_base_input_config import (
    OnboardingNFDBaseInputConfig,
)


@dataclass
class ImageSourceConfig:
    """Object representing an image configuration"""

    source_registry: str = field(
        default="",
        metadata={
            "comment": (
                "Login server of the source acr registry from which to pull the image(s).\n"
                "For example sourceacr.azurecr.io. "
            )
        },
    )
    source_registry_namespace: str | None = field(
        default="",
        metadata={
            "comment": (
                "Optional. Namespace of the repository of the source acr registry from which to pull.\n"
                "For example if your repository is samples/prod/nginx then set this to samples/prod.\n"
                "Leave blank if the image is in the root namespace.\n"
                "See https://learn.microsoft.com/en-us/azure/container-registry/"
                "container-registry-best-practices#repository-namespaces for further details."
            )
        },
    )

    def validate(self):
        """Validate the image configuration."""
        if not self.source_registry:
            raise ValidationError("Source registry must be set")


@dataclass
class HelmPackageConfig:
    """Helm package configuration."""

    name: str = field(default="", metadata={"comment": "The name of the Helm package."})
    path_to_chart: str = field(
        default="",
        metadata={
            "comment": (
                "The file path of Helm Chart on the local disk. Accepts .tgz, .tar or .tar.gz.\n"
                "Use Linux slash (/) file separator even if running on Windows."
            )
        },
    )
    default_values: str | None = field(
        default="",
        metadata={
            "comment": (
                "The file path (absolute or relative to input.json) of YAML values file on the local disk which "
                "will be used instead of the values.yaml file present in the helm chart.\n"
                "Accepts .yaml or .yml. If left as a blank string, "
                "a value mappings file is generated with every value mapped to a deployment parameter.\n"
                "Use a blank string and --interactive on the build command to interactively choose which values to map."
            )
        },
    )
    depends_on: list = field(
        default_factory=lambda: [],
        metadata={
            "comment": (
                "Names of the Helm packages this package depends on.\n"
                "Leave as an empty array if there are no dependencies."
            )
        },
    )

    def validate(self):
        """Validate the helm package configuration."""
        if not self.name:
            raise ValidationError("nf_name must be set for your helm package")
        if not self.path_to_chart:
            raise ValidationError("path_to_chart must be set for your helm package")


@dataclass
class OnboardingCNFInputConfig(OnboardingNFDBaseInputConfig):
    """Input configuration for onboarding CNFs."""

    # TODO: Add better comment for images as not a list
    images: ImageSourceConfig = field(
        default_factory=ImageSourceConfig,
        metadata={"comment": "Source of images to be included in the CNF."},
    )
    helm_packages: List[HelmPackageConfig] = field(
        default_factory=lambda: [HelmPackageConfig()],
        metadata={"comment": "List of Helm packages to be included in the CNF."},
    )

    def validate(self):
        """Validate the CNFconfiguration."""
        super().validate()
        if not self.images:
            raise ValidationError("At least one image must be included.")
        if not self.helm_packages:
            raise ValidationError("At least one Helm package must be included.")
        self.images.validate()
        for helm_package in self.helm_packages:
            helm_package.validate()

    def __post_init__(self):
        if self.images and isinstance(self.images, dict):
            self.images = ImageSourceConfig(**self.images)

        helm_list = []
        for helm_package in self.helm_packages:
            if isinstance(helm_package, dict):
                helm_list.append(HelmPackageConfig(**helm_package))
            else:
                helm_list.append(helm_package)
        self.helm_packages = helm_list
