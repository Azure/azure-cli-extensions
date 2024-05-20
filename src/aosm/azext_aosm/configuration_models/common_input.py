# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations

from dataclasses import dataclass, field

from azure.cli.core.azclierror import ValidationError


@dataclass
class ArmTemplatePropertiesConfig:
    """ARM template configuration."""

    artifact_name: str = field(
        default="",
        metadata={"comment": "Name of the artifact. Used as internal reference only."},
    )
    version: str = field(
        default="", metadata={"comment": "Version of the artifact in 1.1.1 format (three integers separated by dots)."}
    )
    file_path: str = field(
        default="",
        metadata={
            "comment": (
                "File path (absolute or relative to this configuration file) of the artifact you wish to upload from "
                "your local disk.\n"
                "Use Linux slash (/) file separator even if running on Windows."
            )
        },
    )

    def validate(self):
        """Validate the configuration."""
        if not self.artifact_name:
            raise ValidationError("Artifact name must be set")
        if not self.version:
            raise ValidationError("Artifact version must be set")
        if "." not in self.version or "-" in self.version:
            raise ValidationError(
                "Config validation error. ARM template artifact version should be in"
                " format 1.1.1"
            )
        if not self.file_path:
            raise ValidationError("Artifact file path must be set")
