from .base_converter import ConverterTemplate

class EurekaConverter(ConverterTemplate):

    def __init__(self, input):
        def extract_data():
            # TODO: Implement the extract_data method
            pass
        super().__init__(input, extract_data)

    def load_source(self, source):
        self.source = source

    def calculate_data(self):
        name = "eureka"
        configurations = []
        replicas = 1

        self.data = {
            "eurekaName": name,
            "configurations": configurations,
            "replicas": replicas
        }

    def get_template_name(self):
        return "eureka.bicep"
    

