from .base_converter import ConverterTemplate

# Concrete Converter Subclass for Read Me
class ReadMeConverter(ConverterTemplate):

    def __init__(self, source):
        def transform_data():
            # TODO: Implement the transform_data method
            pass
        super().__init__(source, transform_data)

    def get_template_name(self):
        return "README.md"