# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from pathlib import Path


# pylint: disable=too-few-public-methods
class LocalFileBuilder:
    """Writes locally generated files to disk."""

    path: Path
    file_content: str

    def __init__(self, path: Path, file_content: str):
        """Initialize a new instance of the LocalFileBuilder class."""
        self.path = path
        self.file_content = file_content

    def write(self):
        """Write the file to disk."""
        self.path.write_text(self.file_content)
