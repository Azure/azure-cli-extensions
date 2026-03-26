# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from azext_aosm.definition_folder.builder.local_file_builder import LocalFileBuilder


class BaseDefinitionElementBuilder(ABC):
    """Base element definition builder."""

    path: Path
    supporting_files: List[LocalFileBuilder]
    only_delete_on_clean: bool

    def __init__(self, path: Path, only_delete_on_clean: bool = False):
        self.path = path
        self.supporting_files = []
        self.only_delete_on_clean = only_delete_on_clean

    def add_supporting_file(self, supporting_file: LocalFileBuilder):
        """Add a supporting file to the element."""
        self.supporting_files.append(supporting_file)

    def _write_supporting_files(self):
        """Write supporting files to disk."""
        for supporting_file in self.supporting_files:
            supporting_file.write()

    @abstractmethod
    def write(self):
        return NotImplementedError
