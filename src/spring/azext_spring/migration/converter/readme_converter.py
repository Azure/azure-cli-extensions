from .base_converter import ConverterTemplate

# Concrete Converter Subclass for Read Me
class ReadMeConverter(ConverterTemplate):

    def __init__(self, source):
        def extract_data():
            # TODO: Implement the extract_data method
            pass
        super().__init__(source, extract_data)

    def get_template_name(self):
        return "readme.md"