# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import defaultdict
from typing import Iterator, List

from azext_ai_did_you_mean_this._logging import get_logger
from azext_ai_did_you_mean_this._types import (ParameterTableType, OptionListType)

logger = get_logger(__name__)

GLOBAL_PARAM_SHORTHAND_LOOKUP_TBL = {
    '-h': '--help',
    '-o': '--output',
}

GLOBAL_PARAM_LOOKUP_TBL = {
    **GLOBAL_PARAM_SHORTHAND_LOOKUP_TBL,
    '--only-show-errors': None,
    '--help': None,
    '--output': None,
    '--query': None,
    '--debug': None,
    '--verbose': None
}

GLOBAL_PARAM_BLOCKLIST = {
    '--only-show-errors',
    '--help',
    '--debug',
    '--verbose',
}

SUPPRESSED_STR = "==SUPPRESS=="


def has_len_op(value):
    return hasattr(value, '__len__') and callable(value.__len__)


class Parameter():

    DEFAULT_STATE = defaultdict(
        None,
        options_list=[],
        choices=[],
        required=False,
    )

    def __init__(self, alias: str, **kwargs):
        self._options = None

        self.state = defaultdict(None, Parameter.DEFAULT_STATE)
        self.state.update(**kwargs)
        self.alias = alias

        self.options = self.state.get('options_list', [])

        sorted_options = sorted(self.options, key=len, reverse=True)
        self.standard_form = next(iter(sorted_options), None)
        self.aliases = set(self.options) - set((self.standard_form,))

    @property
    def configurable(self) -> bool:
        return self.state['configured_default'] is not None

    @property
    def suppressed(self) -> bool:
        return self.state['help'] == SUPPRESSED_STR

    @property
    def options(self) -> List[str]:
        return self._options

    @options.setter
    def options(self, option_list: OptionListType):
        self._options = [option for option in option_list if has_len_op(option)]


def parameter_gen(parameter_table: ParameterTableType) -> Iterator[Parameter]:
    for alias, argument in parameter_table.items():
        parameter = Parameter(alias, **argument.type.settings)

        if not parameter.suppressed:
            yield parameter
        else:
            logger.debug('Discarding supressed parameter "%s"', alias)
