# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


class FaultDetails():
    FAULT_DESCRIPTION_PROPERTY = 'Reserved.DataModel.Fault.Description'
    FAULT_TYPE_PROPERTY = 'Context.Default.AzureCLI.FaultType'
    FAULT_CORRELATION_PROPERTY = 'Reserved.DataModel.Correlation.1'
    FAULT_MESSAGE_PROPERTY = 'Reserved.DataModel.Fault.Exception.Message'

    def __init__(self, details: dict):
        super().__init__()

        self._details = details
        self._type = details.get(self.FAULT_TYPE_PROPERTY, None)
        self._description = details.get(self.FAULT_DESCRIPTION_PROPERTY, None)
        self._correlation_id = details.get(self.FAULT_CORRELATION_PROPERTY, None)
        self._message = details.get(self.FAULT_MESSAGE_PROPERTY, None)

        if self._correlation_id:
            self._correlation_id = next(iter(self._correlation_id.split(',')), None)

    @property
    def fault_type(self):
        return self._type

    @property
    def description(self):
        return self._description

    @property
    def correlation_id(self):
        return self._correlation_id

    @property
    def message(self):
        return self._message


class Fault():
    def __init__(self, name: str, details: dict, exception: Exception, fault_type: str, summary: str):
        super().__init__()
        self._name = name
        self._details = FaultDetails(details) if details else details
        self._exception = exception
        self._type = fault_type
        self._summary = summary

    @property
    def name(self):
        return self._name

    @property
    def details(self):
        return self._details

    @property
    def exception(self):
        return self._exception

    @property
    def fault_type(self):
        return self._type

    @property
    def summary(self):
        return self._summary
