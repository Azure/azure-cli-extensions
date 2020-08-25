# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from json import JSONEncoder
from azext_ai_did_you_mean_this._cli_command import CliCommand


class SuggestionEncoder(JSONEncoder):
    # pylint: disable=method-hidden
    def default(self, o):
        if isinstance(o, CliCommand):
            return {
                'command': o.command,
                'parameters': ','.join(o.parameters),
                'placeholders': '♠'.join(o.arguments)
            }

        return super().default(o)
