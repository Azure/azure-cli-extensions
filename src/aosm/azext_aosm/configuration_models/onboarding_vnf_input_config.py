# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from azure.cli.core.azclierror import ValidationError

from azext_aosm.configuration_models.common_input import \
    ArmTemplatePropertiesConfig
from azext_aosm.configuration_models.onboarding_nfd_base_input_config import \
    OnboardingNFDBaseInputConfig


@dataclass
class VhdImageConfig:
    """Configuration for a VHD image."""

    artifact_name: str = field(
        default="", metadata={"comment": "Optional. Name of the artifact. Name will be generated if not supplied."}
    )
    version: str = field(
        default="", metadata={"comment": "Version of the artifact in A-B-C format. Note the '-' (dash) not '.' (dot)."}
    )
    file_path: str = field(
        default="",
        metadata={
            "comment": (
                "Supply either file_path or blob_sas_url, not both.\n"
                "File path (absolute or relative to this configuration file) of the artifact you wish to upload from your local disk.\n"
                "Leave as empty string if not required. Use Linux slash (/) file separator even if running on Windows."
            )
        },
    )
    blob_sas_url: str = field(
        default="",
        metadata={
            "comment": (
                "Supply either file_path or blob_sas_url, not both.\nSAS URL of the blob artifact you wish to copy to your Artifact Store.\n"
                "Leave as empty string if not required."
                "Use Linux slash (/) file separator even if running on Windows."
            )
        },
    )
    image_disk_size_GB: str | None = field(
        default="",
        metadata={
            "comment": (
                "Optional. Specifies the size of empty data disks in gigabytes.\n"
                "This value cannot be larger than 1023 GB. Delete if not required."
            )
        },
    )
    image_hyper_v_generation: str | None = field(
        default="",
        metadata={
            "comment": (
                "Optional. Specifies the HyperVGenerationType of the VirtualMachine created from the image.\n"
                "Valid values are V1 and V2. V1 is the default if not specified. Delete if not required."
            )
        },
    )
    image_api_version: str | None = field(
        default="",
        metadata={
            "comment": (
                "Optional. The ARM API version used to create the Microsoft.Compute/images resource.\n"
                "Delete if not required."
            )
        },
    )

    def validate(self):
        """Validate the configuration."""
        if not self.version:
            raise ValidationError("Artifact version must be set")
        if "-" not in self.version or "." in self.version:
            raise ValidationError(
                "Config validation error. VHD image artifact version should be in"
                " format A-B-C"
            )
        if self.blob_sas_url and self.file_path:
            raise ValidationError(
                "Only one of file_path or blob_sas_url may be set for vhd."
            )
        if not (self.blob_sas_url or self.file_path):
            raise ValidationError(
                "One of file_path or sas_blob_url must be set for vhd."
            )


@dataclass
class OnboardingVNFInputConfig(OnboardingNFDBaseInputConfig):
    """Input configuration for onboarding VNFs."""

    blob_artifact_store_name: str | None = field(
        default="",
        metadata={
            "comment": (
                "Optional. Name of the storage account Artifact Store resource. \n"
                "Will be created if it does not exist (with a default name if none is supplied)."
            )
        },
    )
    image_name_parameter: str = field(
        default="",
        metadata={
            "comment": (
                "The parameter name in the VM ARM template which "
                "specifies the name of the image to use for the VM."
            )
        },
    )

    # TODO: Add better comments
    arm_templates: List[ArmTemplatePropertiesConfig] = field(
        default_factory=lambda: [ArmTemplatePropertiesConfig()],
        metadata={"comment": "ARM template configuration. The ARM templates given here would deploy a VM if run. They will be used to generate the VNF."},
    )

    vhd: VhdImageConfig = field(
        default_factory=VhdImageConfig,
        metadata={"comment": "VHD image configuration."},
    )

    def __post_init__(self):
        arm_list = []
        for arm_template in self.arm_templates:
            if arm_template and isinstance(arm_template, dict):
                arm_list.append(ArmTemplatePropertiesConfig(**arm_template))
            else:
                arm_list.append(arm_template)
        self.arm_templates = arm_list

        if self.vhd and isinstance(self.vhd, dict):
            self.vhd = VhdImageConfig(**self.vhd)

    @property
    def sa_manifest_name(self) -> str:
        """Return the Storage account manifest name from the NFD name."""
        sanitized_nf_name = self.nf_name.lower().replace("_", "-")
        return f"{sanitized_nf_name}-sa-manifest-{self.version.replace('.', '-')}"

    def validate(self):
        """Validate the configuration."""
        super().validate()

        if not self.image_name_parameter:
            raise ValidationError("image_name_parameter must be set")
        if not self.arm_templates:
            raise ValidationError("arm_template must be set")
        if not self.vhd:
            raise ValidationError("vhd must be set")
        if not self.arm_templates:
            raise ValidationError("You must include at least one arm template")
        for arm_template in self.arm_templates:
            arm_template.validate()
        self.vhd.validate()