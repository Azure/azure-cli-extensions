# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from json import JSONEncoder
from azext_ai_did_you_mean_this.cli_command import CliCommand


class SuggestionEncoder(JSONEncoder):
    # pylint: disable=method-hidden
    def default(self, o):
        if isinstance(o, CliCommand):
            param_delim: str = CliCommand.PARAMETER_DELIM
            arg_delim: str = CliCommand.ARGUMENT_DELIM
            return {
                'command': o.command,
                'parameters': param_delim.join(o.parameters),
                'placeholders': arg_delim.join(o.arguments)
            }

        return super().default(o)
