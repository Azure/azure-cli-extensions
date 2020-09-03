# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from enum import Enum
from collections import namedtuple

UserFaultInfo = namedtuple('UserFaultInfo', ['keyword'])


class UserFaultType(Enum):
    MISSING_REQUIRED_SUBCOMMAND = UserFaultInfo(keyword='_subcommand')
    NOT_IN_A_COMMAND_GROUP = UserFaultInfo(keyword='command group')
    EXPECTED_AT_LEAST_ONE_ARGUMENT = UserFaultInfo(keyword='expected')
    UNRECOGNIZED_ARGUMENTS = UserFaultInfo(keyword='unrecognized')
    INVALID_JMESPATH_QUERY = UserFaultInfo(keyword='jmespath')
    NOT_APPLICABLE = UserFaultInfo(keyword='na')

    def __init__(self, keyword):
        super().__init__()
        self._keyword = keyword

    @property
    def keyword(self):
        return self._keyword
