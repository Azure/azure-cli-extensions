# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from functools import wraps
from typing import Dict, Any
from contextlib import contextmanager
from enum import Enum, auto
import azure.cli.core.telemetry as telemetry

from azext_ai_did_you_mean_this._const import (
    UNEXPECTED_ERROR_STR,
    EXTENSION_NAME
)

IS_TELEMETRY_ENABLED = telemetry.is_telemetry_enabled()


def _user_agrees_to_telemetry(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        if not IS_TELEMETRY_ENABLED:
            return None

        return func(*args, **kwargs)

    return _wrapper


class FaultType(Enum):
    RequestException = 'did-you-mean-request-exception'
    UnknownFaultType = 'unknown-fault-type'


class NoRecommendationReason(Enum):
    ServiceRequestFailure = 'service-request-failure'
    CommandFromExtension = 'command-from-extension'
    EmptyCommand = 'empty-command'


class TelemetryProperty(Enum):
    # azure-cli-core version
    CoreVersion = auto()
    # 'ai-did-you-mean-this' extension version.
    ExtensionVersion = auto()
    # The command passed to the extension.
    RawCommand = auto()
    # The possibly reduced command used in the service query.
    Command = auto()
    # The parameters passed to the extension.
    RawParameters = auto()
    # The normalized and sorted set of parameters as a list of comma-separated values.
    Parameters = auto()
    # The sorted set of unrecognized parameters
    UnrecognizedParameters = auto()
    # Time in milliseconds that it took to retrieve the user's subscription ID and correlation ID if applicable.
    TimeToRetrieveUserInfoMs = auto()
    # Time in milliseconds that it took to get recommendations from the Aladdin service.
    RoundTripRequestTimeMs = auto()
    # Time in milliseconds that it took to provide recommendations for the user's query (excludes display time).
    ExecutionTimeMs = auto()
    # True if the Aladdin service did not respond within the amount of time alotted, False otherwise.
    RequestTimedOut = auto()
    # Describes why recommendations weren't available for the specified query if applicable.
    NoRecommendationReason = auto()
    # A "pruned" list of recommendations which differs from that returned by the service. Only applicable when
    # one or more recommendations are invalid for the user's current CLI installation.
    PrunedSuggestions = auto()
    # The number of valid suggestions returned by the service.
    ValidSuggestionCount = auto()
    # The number of invalid suggestions returned by the service.
    InvalidSuggestionCount = auto()
    # The total number of suggestions received from the service.
    TotalSuggestionCount = auto()
    # Extension inferred by the azure-cli-core parser hook
    InferredExtension = auto()
    # True if "az find" was suggested, false otherwise.
    SuggestedAzFind = auto()
    # True if the correlation ID was missing, false otherwise.
    MissingCorrelationId = auto()
    # True if the Azure subscription ID was missing, false otherwise.
    MissingSubscriptionId = auto()


class ExtensionTelemetryManager():
    def __init__(self):
        super().__init__()
        self._props: Dict[str, str] = {}
        self._prefix: str = telemetry.AZURE_CLI_PREFIX

    def _get_property(self, name: str):
        prefix = self._prefix
        return name if name.startswith(prefix) else f'{prefix}{name}'

    def get_property_name(self, prop: TelemetryProperty):
        return self._get_property(prop.name)

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
                fault_type=FaultType.UnknownFaultType.value,
                summary=UNEXPECTED_ERROR_STR
            )

        add_extension_event(
            EXTENSION_NAME,
            _extension_telemetry_manager.properties.copy()
        )


@contextmanager
def extension_telemetry_session():
    with ExtensionTelemterySession():
        yield None
