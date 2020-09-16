# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Union


class CommandNormalizationScenario():
    def __init__(self, command: str, normalized_command: Union[str, None] = None):
        super().__init__()
        self.is_command_normalized = normalized_command is None
        self.command = command
        self.normalized_command = normalized_command or command

    @property
    def normalizable(self):
        return not self.is_command_normalized

    @staticmethod
    def reduce(command: str, delim: str = ' '):
        last_delim_idx = command.rfind(delim)
        if last_delim_idx != -1:
            command = command[:last_delim_idx]
        return command
