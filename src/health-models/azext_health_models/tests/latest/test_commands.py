# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import MagicMock

from azext_health_models.commands import load_command_table


class TestArrangeCommandRegistration(unittest.TestCase):

    def test_arrange_command_is_marked_experimental(self):
        loader = MagicMock()

        load_command_table(loader, None)

        command_group = loader.command_group.return_value.__enter__.return_value
        command_group.custom_command.assert_called_once_with(
            'arrange',
            'health_model_arrange',
            is_experimental=True,
        )


if __name__ == "__main__":
    unittest.main()
