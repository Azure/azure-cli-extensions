# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from pathlib import Path
from typing import List

from knack.log import get_logger

from azext_aosm.common.artifact import BaseArtifact

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
        for artifact in self.artifacts:
            artifact_dict = artifact.to_dict()
            logger.debug(
                "Writing artifact %s as: %s", artifact.artifact_name, artifact_dict
            )
            artifacts_list.append(artifact_dict)
        (self.path / "artifacts.json").write_text(json.dumps(artifacts_list, indent=4))
        self._write_supporting_files()
