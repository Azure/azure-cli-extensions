# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from pathlib import Path
from typing import List

from azext_aosm.common.artifact import BaseArtifact
from knack.log import get_logger

from .base_builder import BaseDefinitionElementBuilder

logger = get_logger(__name__)


class ArtifactDefinitionElementBuilder(BaseDefinitionElementBuilder):
    """Artifact builder"""

    artifacts: List[BaseArtifact]

    def __init__(
        self,
        path: Path,
        artifacts: List[BaseArtifact],
        only_delete_on_clean: bool = False,
    ):
        super().__init__(path, only_delete_on_clean)
        self.artifacts = artifacts

    def write(self):
        """Write the definition element to disk."""
        self.path.mkdir(exist_ok=True)
        artifacts_list = []
        # TODO: handle converting path to string that doesn't couple this code to the artifact. Probably should be in to_dict method.
        for artifact in self.artifacts:
            logger.debug("Writing artifact %s as: %s", artifact.artifact_name, artifact.to_dict())
            if hasattr(artifact, "file_path") and artifact.file_path is not None:
                artifact.file_path = str(artifact.file_path)
            artifacts_list.append(artifact.to_dict())
        (self.path / "artifacts.json").write_text(json.dumps(artifacts_list, indent=4))
        self._write_supporting_files()
