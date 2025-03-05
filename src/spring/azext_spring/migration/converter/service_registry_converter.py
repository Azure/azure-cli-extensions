from .base_converter import ConverterTemplate

class ServiceRegistryConverter(ConverterTemplate):

    def __init__(self, input):
        def extract_data():
            service_registry = self.wrapper_data.get_resources_by_type('Microsoft.AppPlatform/Spring/serviceRegistries')
            name = f"eureka"
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
    

