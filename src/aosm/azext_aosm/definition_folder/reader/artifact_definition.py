# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from pathlib import Path
from typing import cast, Type

from knack.log import get_logger

from azext_aosm.common.artifact import ARTIFACT_TYPE_TO_CLASS, BaseArtifact
from azext_aosm.common.command_context import CommandContext
from azext_aosm.configuration_models.common_parameters_config import (
    BaseCommonParametersConfig,
)
from azext_aosm.definition_folder.reader.base_definition import BaseDefinitionElement

logger = get_logger(__name__)


class ArtifactDefinitionElement(BaseDefinitionElement):
    """Definition for Artifact"""  # TODO: Is this actually an artifact manifest?

    def __init__(self, path: Path, only_delete_on_clean: bool):
        super().__init__(path, only_delete_on_clean)
        logger.debug("ArtifactDefinitionElement path: %s", path)
        artifact_list = json.loads((path / "artifacts.json").read_text())
        self.artifacts = [
            self.create_artifact_object(artifact) for artifact in artifact_list
        ]

    @staticmethod
    def create_artifact_object(artifact: dict) -> BaseArtifact:
        """
        Use reflection (via the inspect module) to identify the artifact class's required fields
        and create an instance of the class using the supplied artifact dict.
        """
        if "type" not in artifact or artifact["type"] not in ARTIFACT_TYPE_TO_CLASS:
            raise ValueError(
                f"Artifact type is missing or invalid for artifact {artifact}"
            )

        # Give mypy a hint for the artifact type
        artifact_class = cast(
            Type[BaseArtifact], ARTIFACT_TYPE_TO_CLASS[artifact["type"]]
        )
        return artifact_class.from_dict(artifact)

    def deploy(
        self, config: BaseCommonParametersConfig, command_context: CommandContext
    ):
        """Deploy the element."""
        for artifact in self.artifacts:
            logger.info(
                "Deploying artifact %s of type %s",
                artifact.artifact_name,
                type(artifact),
            )
            artifact.upload(config=config, command_context=command_context)

    def delete(
        self, config: BaseCommonParametersConfig, command_context: CommandContext
    ):
        """Delete the element."""
        # TODO: Implement?
        raise NotImplementedError
