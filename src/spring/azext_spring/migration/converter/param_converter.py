from .base_converter import ConverterTemplate

# Concrete Converter Subclass for paramter
class ParamConverter(ConverterTemplate):
    def load_source(self, source):
        pass

    def calculate_data(self):
        pass

    def get_template_name(self):
        return "param.bicepparam"