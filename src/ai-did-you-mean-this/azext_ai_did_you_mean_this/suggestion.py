# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def assert_has_split_method(field, value):
    if not getattr(value, 'split') or not callable(value.split):
        raise TypeError(f'value assigned to `{field}` must contain split method')


class Suggestion():
    COMNMAND_FIELD = 'command'
    PARAMETERS_FIELD = 'parameters'
    PLACEHOLDERS_FIELD = 'placeholders'

    def __init__(self, data):
        self._command = data[self.COMNMAND_FIELD]
        self._parameters = data[self.PARAMETERS_FIELD]
        self._placeholders = data[self.PLACEHOLDERS_FIELD]

        for attr in ('_parameters', '_placeholders'):
            value = getattr(self, attr)
            value = '' if value == '{}' else value
            setattr(self, attr, value)

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, value):
        self._command = value

    @property
    def parameters(self):
        return self._parameters.split(',')

    @parameters.setter
    def parameters(self, value):
        assert_has_split_method('parameters', value)
        self._parameters = value

    @property
    def placeholders(self):
        return self._placeholders.split(',')

    @placeholders.setter
    def placeholders(self, value):
        assert_has_split_method('placeholders', value)
        self._placeholders = value

    def __str__(self):
        parameter_and_argument_buffer = []

        for pair in zip(self.parameters, self.placeholders):
            parameter_and_argument_buffer.append(' '.join(pair))

        return f"az {self.command} {' '.join(parameter_and_argument_buffer)}"

    def __eq__(self, value):
        return (self.command == value.command and
                self.parameters == value.parameters and
                self.placeholders == value.placeholders)
