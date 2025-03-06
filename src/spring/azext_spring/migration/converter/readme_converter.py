from .base_converter import ConverterTemplate

# Concrete Converter Subclass for Read Me
class ReadMeConverter(ConverterTemplate):

    def __init__(self, input):
        def extract_data():
            # TODO: Implement the extract_data method
            pass
        super().__init__(input, extract_data)

    def get_template_name(self):
        return "readme.md"