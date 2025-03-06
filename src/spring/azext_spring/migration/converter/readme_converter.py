from .base_converter import ConverterTemplate

# Concrete Converter Subclass for Read Me
class ReadMeConverter(ConverterTemplate):
    def load_source(self, source):
        pass

    def calculate_data(self):
        pass

    def get_template_name(self):
        return "README.md"