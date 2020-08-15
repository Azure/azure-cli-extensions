# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pprint
from typing import Dict

from azext_ai_did_you_mean_this._cli_command import CliCommand
from azext_ai_did_you_mean_this._types import ArgumentsType


class SuggestionParseError(KeyError):
    pass


class Suggestion(CliCommand):
    # pylint: disable=useless-super-delegation
    def __init__(self, command: str, parameters: ArgumentsType = '', placeholders: ArgumentsType = ''):
        super().__init__(command, parameters, placeholders)

    def __str__(self):
        return f"az {super().__str__()}"

    def __repr__(self):
        return 'Suggestion(command={0}, parameters={1}, placeholders={2})'.format(
            pprint.pformat(self.command),
            pprint.pformat(self.parameters),
            pprint.pformat(self.arguments)
        )

    @classmethod
    def parse(cls, data: Dict[str, str]):
        try:
            command = data['command']
            parameters = data['parameters']
            placeholders = data['placeholders']
        except KeyError as e:
            raise SuggestionParseError(*e.args)

        return Suggestion(command, parameters, placeholders)
