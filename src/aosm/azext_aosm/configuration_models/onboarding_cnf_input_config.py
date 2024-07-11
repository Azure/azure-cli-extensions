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
class HelmPackageConfig:
    """Helm package configuration."""

    name: str = field(default="", metadata={"comment": "The name of the Helm package."})
    path_to_chart: str = field(
        default="",
        metadata={
            "comment": (
                "The file path to the helm chart on the local disk, relative to the directory from which the "
                "command is run.\n"
                "Accepts .tgz, .tar or .tar.gz, or an unpacked directory. Use Linux slash (/) file separator "
                "even if running on Windows."
            )
        },
    )
    default_values: str | None = field(
        default="",
        metadata={
            "comment": (
                "The file path (absolute or relative to this configuration file) of YAML values file on the "
                "local disk which will be used instead of the values.yaml file present in the helm chart.\n"
                "Accepts .yaml or .yml. Use Linux slash (/) file separator even if running on Windows."
            )
        },
    )
    # # NOTE: there is a story to reimplement this, so not deleting
    # depends_on: list = field(
    #     default_factory=lambda: [],
    #     metadata={
    #         "comment": (
    #             "Names of the Helm packages this package depends on.\n"
    #             "Leave as an empty array if there are no dependencies."
    #         )
    #     },
    # )

    def validate(self):
        """Validate the helm package configuration."""
        if not self.name:
            raise ValidationError("nf_name must be set for your helm package")
        if not self.path_to_chart:
            raise ValidationError("path_to_chart must be set for your helm package")


@dataclass
class OnboardingCNFInputConfig(OnboardingNFDBaseInputConfig):
    """Input configuration for onboarding CNFs."""

    image_sources: list = field(
        default_factory=list,
        metadata={
            "comment": (
                "List of registries from which to pull the image(s).\n"
                'For example ["sourceacr.azurecr.io/test", "myacr2.azurecr.io", "ghcr.io/path"].\n'
                "For non Azure Container Registries, ensure you have run a docker login command before running build.\n"
            )
        },
    )

    helm_packages: List[HelmPackageConfig] = field(
        default_factory=lambda: [HelmPackageConfig()],
        metadata={"comment": "List of Helm packages to be included in the CNF."},
    )

    def validate(self):
        """Validate the CNFconfiguration."""
        super().validate()
        if not self.image_sources:
            raise ValidationError("At least one image source must be included.")
        if not self.helm_packages:
            raise ValidationError("At least one Helm package must be included.")
        for helm_package in self.helm_packages:
            helm_package.validate()

    def __post_init__(self):
        helm_list = []
        for helm_package in self.helm_packages:
            if isinstance(helm_package, dict):
                helm_list.append(HelmPackageConfig(**helm_package))
            else:
                helm_list.append(helm_package)
        self.helm_packages = helm_list
