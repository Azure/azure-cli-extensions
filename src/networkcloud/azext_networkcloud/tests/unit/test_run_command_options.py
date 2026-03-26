# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from abc import ABC
from pathlib import Path
from unittest.mock import Mock, patch

from azure.cli.core.aaz._base import AAZUndefined
from azure.cli.core.azclierror import FileOperationError


class RunCommandOptionsTestClass(ABC):
    """
    This class provides a method that tests the pre_operations functions of
    commands inheriting the RunCommandOptions class.
    """

    def test_pre_operations(self):
        """Tests to ensure the RunCommandOptions.pre_operations function creates
        a directory within the directory provided to the output argument.
        """
        # Mock CLI args
        self.cmd.ctx = Mock()
        self.cmd.ctx.args = Mock()

        # Ensure mkdir not called when no output arg provided
        with patch.object(Path, "mkdir", return_value=None) as mock_mkdir:
            # Set output arg to undefined
            # NOTE(drewwalters): AAZ library uses AAZUndefined instead of None
            # to indicate an argument was not provided.
            self.cmd.ctx.args.output = AAZUndefined

            self.cmd.pre_operations()
            mock_mkdir.assert_not_called()

        # Ensure mkdir called when output arg provided
        with patch.object(Path, "mkdir", return_value=None) as mock_mkdir:
            # Set output arg to path
            self.cmd.ctx.args.output = "/path/to/test/output/dir"

            self.cmd.pre_operations()
            mock_mkdir.assert_called()

        # Ensure function raises FileOperationError for OSErrors
        with patch.object(Path, "mkdir", side_effect=OSError) as mock_mkdir:
            with self.assertRaises(FileOperationError):
                self.cmd.pre_operations()
