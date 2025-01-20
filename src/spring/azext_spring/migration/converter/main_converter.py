from .base_converter import ConverterTemplate

# Concrete Converter Subclass for Read Me
class MainConverter(ConverterTemplate):
    def load_source(self, source):
        pass

    def calculate_data(self):
        pass

    def get_template_name(self):
        return "main.bicep"