from .base_converter import ConverterTemplate

class EurekaConverter(ConverterTemplate):

    def __init__(self, input):
        def extract_data():
            name = "eureka"
            configurations = []
            replicas = 1

            return {
                "eurekaName": name,
                "configurations": configurations,
                "replicas": replicas
            }
        super().__init__(input, extract_data)

    def get_template_name(self):
        return "eureka.bicep"
    

