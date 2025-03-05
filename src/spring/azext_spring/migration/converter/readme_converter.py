from .base_converter import ConverterTemplate

# Concrete Converter Subclass for Read Me
class ReadMeConverter(ConverterTemplate):

    def __init__(self, input):
        def extract_data(input):
            # TODO: Implement the extract_data method
            return input
        super().__init__(input, extract_data)

    def load_source(self, source):
        pass

    def calculate_data(self):
        pass

    def get_template_name(self):
        return "readme.md"