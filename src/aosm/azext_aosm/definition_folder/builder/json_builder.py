# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from pathlib import Path

from azext_aosm.common.constants import ALL_PARAMETERS_FILE_NAME
from azext_aosm.definition_folder.builder.base_builder import (
    BaseDefinitionElementBuilder,
)


class JSONDefinitionElementBuilder(BaseDefinitionElementBuilder):
    """JSON definition element builder."""

    json_content: str

    def __init__(
        self, path: Path, json_content: str, only_delete_on_clean: bool = False
    ):
        super().__init__(path, only_delete_on_clean)
        self.json_content = json_content

    def write(self):
        """Write the definition element to disk."""
        self.path.mkdir(exist_ok=True)
        (self.path / ALL_PARAMETERS_FILE_NAME).write_text(self.json_content)
