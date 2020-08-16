# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from http import HTTPStatus
from typing import List, Union

from requests import RequestException

from azext_ai_did_you_mean_this._cli_command import CliCommand
from azext_ai_did_you_mean_this._suggestion import Suggestion
from azext_ai_did_you_mean_this.tests.latest.data.user_fault_type import UserFaultType


class RequestScenario():
    def __init__(self, status: HTTPStatus, exception: Union[RequestException, None] = None):
        super().__init__()

        if exception and not isinstance(exception, RequestException):
            raise TypeError('must specify exception of type RequestException')

        self.status = status.value
        self.exception = exception

    @property
    def exception_message(self):
        return next(iter(self.exception.args), None)

    def raise_exception(self):
        if self.raises:
            raise self.exception

    @property
    def raises(self):
        return isinstance(self.exception, Exception)


DEFAULT_REQUEST_SCENARIO = RequestScenario(HTTPStatus.OK)


class Scenario():
    def __init__(self,
                 cli_command: CliCommand,
                 suggestions: List[Suggestion] = None,
                 expected_user_fault_type: UserFaultType = UserFaultType.NOT_APPLICABLE,
                 extension: Union[str, None] = None,
                 request_scenario: RequestScenario = DEFAULT_REQUEST_SCENARIO):
        self._cli_command = cli_command
        self.suggestions = suggestions or []
        self.expected_user_fault_type = expected_user_fault_type
        self.extension = extension
        self.request_scenario = request_scenario

    @property
    def cli_command(self) -> str:
        return str(self._cli_command)

    @property
    def command(self) -> str:
        return self._cli_command.command

    @property
    def parameters(self) -> str:
        return ','.join(self._cli_command.parameters)
