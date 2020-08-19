# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from functools import wraps
from typing import Dict, Union, Any
from enum import Enum, auto
import azure.cli.core.telemetry as telemetry

from azext_ai_did_you_mean_this._const import (
    UNEXPECTED_ERROR_STR,
    EXTENSION_NAME
)

TELEMETRY_PROPERTY_PREFIX = 'Context.Default.Extension.Thoth'


def _user_agrees_to_telemetry(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        if not telemetry.is_telemetry_enabled():
            return None

        return func(*args, **kwargs)

    return _wrapper


class FaultType(Enum):
    RequestError = 'thoth-aladdin-request-error'
    SuggestionParseError = 'thoth-aladdin-response-parse-error'
    InvalidSuggestionError = 'thoth-aladdin-invalid-suggestion-in-response-error'
    UnexpectedError = 'thoth-unexpected-error'

    def __eq__(self, value: Union['FaultType', str]):
        if hasattr(value, 'value'):
            value = value.value
        # pylint: disable=comparison-with-callable
        return self.value == value

    def __hash__(self):
        return hash(self.value)


class NoRecommendationReason(Enum):
    ServiceRequestFailure = 'service-request-failure'
    CommandFromExtension = 'command-from-extension'
    EmptyCommand = 'empty-command'

    def __eq__(self, value: Union['NoRecommendationReason', str]):
        if hasattr(value, 'value'):
            value = value.value
        # pylint: disable=comparison-with-callable
        return self.value == value

    def __hash__(self):
        return hash(self.value)


class TelemetryProperty(Enum):
    # The "azure-cli-core" version.
    CoreVersion = auto()
    # The "ai-did-you-mean-this" extension version.
    ExtensionVersion = auto()
    # The command passed to the extension.
    RawCommand = auto()
    # The command used by the service query. May differ from the original command if an unrecognized token is removed.
    Command = auto()
    # The parameters passed to the extension.
    RawParams = auto()
    # The normalized and sorted set of parameters as a list of comma-separated values.
    Params = auto()
    # The sorted set of unrecognized parameters obtained by normalizing the passed parameters.
    UnrecognizedParams = auto()
    # Time in milliseconds that it took to retrieve the user's subscription ID and correlation ID if applicable.
    TimeToRetrieveUserInfoMs = auto()
    # Time in milliseconds that it took to send a request and receive a response from the Aladdin service.
    RoundTripRequestTimeMs = auto()
    # The total time in milliseconds that it took to retrieve recovery suggestions for specified failure.
    ExecutionTimeMs = auto()
    # True if the Aladdin service did not respond within the amount of time alotted, false otherwise.
    RequestTimedOut = auto()
    # Describes why suggestions weren't available where applicable.
    ResultSummary = auto()
    # JSON list of suggestions. Contains only the suggestions which passed client-side validation.
    Suggestions = auto()
    # The number of valid suggestions received from the service.
    NumberOfValidSuggestions = auto()
    # The number of suggestions received from the service.
    NumberOfSuggestions = auto()
    # The inferred name of the extension the command was sourced from if applicable.
    InferredExtension = auto()
    # True if "az find" was suggested to the user, alse otherwise.
    SuggestedAzFind = auto()
    # True if the correlation ID could not be retrieved, false otherwise.
    NoCorrelationId = auto()
    # True if the Azure subscription ID could not be retrieved, false otherwise.
    NoSubscriptionId = auto()

    def __init__(self, _: int):
        super().__init__()
        self._property_name = f'{TELEMETRY_PROPERTY_PREFIX}.{self.name}'

    @property
    def property_name(self) -> str:
        return self._property_name

    def __eq__(self, value: Union['TelemetryProperty', str]):
        if hasattr(value, 'property_name'):
            value = value.property_name
        return self.property_name == value

    def __hash__(self):
        return hash(self.property_name)


class ExtensionTelemetryManager():
    def __init__(self):
        super().__init__()
        self._props: Dict[str, str] = {}
        self._prefix: str = TELEMETRY_PROPERTY_PREFIX

    def _get_property(self, name: str):
        prefix = self._prefix
        return name if name.startswith(prefix) else f'{prefix}.{name}'

    def __setitem__(self, key: str, value: Any):
        self._props[self._get_property(key)] = str(value)

    def __getitem__(self, key: str) -> Any:
        return self._props[self._get_property(key)]

    @property
    def properties(self):
        return self._props

    def clear(self):
        self._props.clear()


_extension_telemetry_manager = ExtensionTelemetryManager()


def _assert_is_of_correct_type(arg: Any, expected_type: type, name: str):
    if not isinstance(arg, expected_type):
        raise TypeError(f'{name} must be a `{expected_type.__name__}`')


@_user_agrees_to_telemetry
def get_subscription_id():
    return telemetry._get_azure_subscription_id()  # pylint: disable=protected-access


@_user_agrees_to_telemetry
def get_correlation_id():
    return telemetry._session.correlation_id  # pylint: disable=protected-access


@_user_agrees_to_telemetry
def set_property(prop: TelemetryProperty, value: Any):
    _assert_is_of_correct_type(prop, TelemetryProperty, 'prop')
    _extension_telemetry_manager[prop.name] = value


@_user_agrees_to_telemetry
def set_properties(props: Dict[TelemetryProperty, Any]):
    for prop, value in props.items():
        _assert_is_of_correct_type(prop, TelemetryProperty, 'props')
        _extension_telemetry_manager[prop.name] = value


@_user_agrees_to_telemetry
def get_property(prop: TelemetryProperty):
    _assert_is_of_correct_type(prop, TelemetryProperty, 'prop')
    return _extension_telemetry_manager[prop.name]


@_user_agrees_to_telemetry
def set_exception(exception: Exception, fault_type: str, summary: str = None):
    telemetry.set_exception(
        exception=exception,
        fault_type=fault_type,
        summary=summary
    )


@_user_agrees_to_telemetry
def add_extension_event(extension_name: str, properties: dict):
    telemetry.add_extension_event(
        extension_name,
        properties
    )


class ExtensionTelemterySession():
    def __enter__(self):
        _extension_telemetry_manager.clear()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type and exc_val:
            set_exception(
                exception=exc_val,
                fault_type=FaultType.UnexpectedError.value,
                summary=UNEXPECTED_ERROR_STR
            )

        add_extension_event(
            EXTENSION_NAME,
            _extension_telemetry_manager.properties.copy()
        )
