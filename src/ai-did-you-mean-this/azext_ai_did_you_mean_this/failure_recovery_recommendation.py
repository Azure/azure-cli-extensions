def assert_has_split_method(field, value):
    if not getattr(value, 'split') or not callable(value.split):
        raise TypeError(f'value assigned to `{field}` must contain split method')


class FailureRecoveryRecommendation():
    def __init__(self, data):
        data['SuccessCommand'] = data.get('SuccessCommand', '')
        data['SuccessCommand_Parameters'] = data.get('SuccessCommand_Parameters', '')
        data['SuccessCommand_ArgumentPlaceholders'] = data.get('SuccessCommand_ArgumentPlaceholders', '')
        data['NumberOfPairs'] = data.get('NumberOfPairs', 0)

        self._command = data['SuccessCommand']
        self._parameters = data['SuccessCommand_Parameters']
        self._placeholders = data['SuccessCommand_ArgumentPlaceholders']
        self._number_of_pairs = data['NumberOfPairs']

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

    @property
    def number_of_pairs(self):
        return self._number_of_pairs

    @number_of_pairs.setter
    def number_of_pairs(self, value):
        self._number_of_pairs = value

    def __str__(self):
        parameter_and_argument_buffer = []

        for pair in zip(self.parameters, self.placeholders):
            parameter_and_argument_buffer.append(' '.join(pair))

        return f"az {self.command} {' '.join(parameter_and_argument_buffer)}"
