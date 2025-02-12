from .base_converter import ConverterTemplate

class EurekaConverter(ConverterTemplate):

    def __init__(self):
        super().__init__()

    def load_source(self):
        pass

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
    

