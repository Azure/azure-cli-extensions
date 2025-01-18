from .base_converter import ConverterTemplate

# Concrete Converter Subclass for Gateway
class GatewayConverter(ConverterTemplate):
    def __init__(self, client):
        self.client = client

    def load_source(self, source):
        # Call the client to get additional data
        pass

    def calculate_data(self):
        pass

    def get_template_name(self):
        return "gateway.bicep"