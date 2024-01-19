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
        default="", metadata={"comment": "Name of the artifact."}
    )
    version: str = field(
        default="", metadata={"comment": "Version of the artifact in A.B.C format."}
    )
    file_path: str = field(
        default="",
        metadata={
            "comment": (
                "File path of the artifact you wish to upload from your local disk.\n"
                "Relative paths are relative to the configuration file. "
                "On Windows escape any backslash with another backslash."
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
                " format A.B.C"
            )
        if not self.file_path:
            raise ValidationError("Artifact file path must be set")
