# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections.abc import Iterable
from http import HTTPStatus
from typing import List, Tuple, Union

from requests import RequestException

from azext_ai_did_you_mean_this.cli_command import CliCommand
from azext_ai_did_you_mean_this.suggestion import Suggestion
from azext_ai_did_you_mean_this.tests.latest.data.user_fault_type import UserFaultType

RaiseExceptionType = Union[None, Tuple[RequestException, str]]


def _assert_raise_exc_is_of_correct_type(raise_exc: RaiseExceptionType):
    if raise_exc is None:
        return
    if not isinstance(raise_exc, Iterable):
        raise TypeError('raise_exc must be iterable')
    if len(raise_exc) != 2:
        raise ValueError('expected raise_exc to be of format (ex: RequestException, msg: str)')
    if not isinstance(raise_exc[0], RequestException):
        raise TypeError('exception must be from requests module')
    if not isinstance(raise_exc[1], str):
        raise TypeError('exception message should be of type str')


class RequestScenario():
    def __init__(self, status: HTTPStatus, raise_exc: RaiseExceptionType = None):
        super().__init__()
        _assert_raise_exc_is_of_correct_type(raise_exc)
        self._status = status.value
        self._exc_type = None
        self._exc_msg = ''

        if raise_exc:
            self._exc_type, self._exc_msg = raise_exc

    def raise_exception(self):
        if self._exc_type:
            raise self._exc_type(self._exc_msg)

    @property
    def raises(self):
        return isinstance(self._exc_type, Exception)

    @property
    def status(self) -> int:
        return self._status


DEFAULT_REQUEST_SCENARIO = RequestScenario(HTTPStatus.OK)


class Scenario():
    def __init__(self,
                 cli_command: CliCommand,
                 suggestions: List[Suggestion] = None,
                 expected_user_fault_type: UserFaultType = UserFaultType.NOT_APPLICABLE,
                 extension: Union[str, None] = None,
                 request_scenario: RequestScenario = DEFAULT_REQUEST_SCENARIO):
        self._cli_command = cli_command
        self._suggestions = suggestions or []
        self._expected_user_fault_type = expected_user_fault_type
        self._extension = extension
        self._request_scenario = request_scenario

    @property
    def cli_command(self) -> str:
        return str(self._cli_command)

    @property
    def command(self) -> str:
        return self._cli_command.command

    @property
    def parameters(self) -> str:
        return ','.join(self._cli_command.parameters)

    @property
    def extension(self):
        return self._extension

    @property
    def suggestions(self) -> List[Suggestion]:
        return self._suggestions

    @property
    def expected_user_fault_type(self):
        return self._expected_user_fault_type

    @property
    def request_scenario(self):
        return self._request_scenario
