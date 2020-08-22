# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections.abc import Iterable

from azext_ai_did_you_mean_this._types import ArgumentsType

DEFAULT_DELIM = ','


class Arguments():
    def __init__(self, name: str, default: str = '', delim: str = DEFAULT_DELIM):
        super().__init__()
        self._default = default
        self.name = name
        self.delim = delim

        self.data = {}

    def __get__(self, instance: type, owner: object):
        return self.data.get(id(instance), self._default)

    def __set__(self, instance: type, value: ArgumentsType):
        is_string = isinstance(value, str)

        if not is_string:
            if isinstance(value, Iterable):
                value = [str(item) for item in value]
            else:
                raise TypeError(f'{self.name} must be of type str')
        else:
            # filter out empty entries from list of arguments.
            value = list(filter(None, value.split(self.delim)))

        self.data[id(instance)] = value
