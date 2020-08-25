# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from enum import Enum
from collections import namedtuple
from typing import Union

TelemetryPropertyInfo = namedtuple('TelemetryPropertyInfo', ['property_name'])


class CoreTelemetryProperty(Enum):
    EXTENSION_NAME = TelemetryPropertyInfo(property_name='Context.Default.AzureCLI.ExtensionName')
    CORRELATION_ID = TelemetryPropertyInfo(property_name='Reserved.DataModel.CorrelationId')

    def __init__(self, property_name: str):
        super().__init__()
        self._property_name = property_name

    @property
    def property_name(self) -> str:
        return self._property_name

    def __eq__(self, value: Union['CoreTelemetryProperty', str]):
        if hasattr(value, 'property_name'):
            value = value.property_name
        return self._property_name == value

    def __hash__(self):
        return hash(self._property_name)
