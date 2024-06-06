# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from pathlib import Path

from azext_aosm.definition_folder.builder.base_builder import (
    BaseDefinitionElementBuilder,
)


class BicepDefinitionElementBuilder(BaseDefinitionElementBuilder):
    """Bicep definition element builder."""

    bicep_content: str

    def __init__(
        self, path: Path, bicep_content: str, only_delete_on_clean: bool = False
    ):
        super().__init__(path, only_delete_on_clean)
        self.bicep_content = bicep_content

    def write(self):
        """Write the definition element to disk."""
        self.path.mkdir(exist_ok=True)
        (self.path / "deploy.bicep").write_text(self.bicep_content)

        self._write_supporting_files()
